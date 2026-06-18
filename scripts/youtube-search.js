#!/usr/bin/env node
// youtube-search.js — search the DOF (dofofapple) YouTube channel by title text.
//
// Read-only lookup (no Airtable / no Job# join): takes a query term and finds
// matching videos on the dofofapple channel, INCLUDING unlisted + private, via the
// channel-owner OAuth refresh token (env YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET /
// YOUTUBE_REFRESH_TOKEN, NOT cloud MCP). Prints JSON (name + youtu.be link +
// privacy) on stdout.
//
// Matching is exact case-insensitive SUBSTRING (every query word must appear in the
// title) — DOF titles smush tokens (e.g. "CCSD2026", date suffix "20260617"), which
// YouTube's word-based search.list can't match, so we filter titles locally.
//
// Efficiency: instead of re-paging the whole ~10k-video channel every search, the
// id+title list is cached on disk and topped up INCREMENTALLY. The uploads playlist
// is newest-first, so each run pages from the top only until it hits a video already
// cached, then stops (usually 1 page). New uploads are picked up immediately; the
// full ~200-page scan happens only on first run / empty cache / --rebuild.
// Privacy + duration are always fetched live (privacy changes), never cached.
//
// Cache file: $YOUTUBE_CACHE_PATH, else ~/.cache/dof-youtube-titles.json.
//
// Usage:
//   node scripts/youtube-search.js EMSD CCSD2026
//   node scripts/youtube-search.js --rebuild EMSD CCSD2026   # force full re-scan

const fs = require('fs');
const os = require('os');
const path = require('path');

const CLIENT_ID = process.env.YOUTUBE_CLIENT_ID;
const CLIENT_SECRET = process.env.YOUTUBE_CLIENT_SECRET;
const REFRESH_TOKEN = process.env.YOUTUBE_REFRESH_TOKEN;

if (!CLIENT_ID || !CLIENT_SECRET || !REFRESH_TOKEN) {
  console.error(
    'ERROR: YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET / YOUTUBE_REFRESH_TOKEN env not all set (Zeabur Variables). Aborting — do NOT fall back to any cloud MCP or hand-written API call.'
  );
  process.exit(1);
}

const argv = process.argv.slice(2);
const rebuild = argv.includes('--rebuild') || argv.includes('--full');
const query = argv.filter((a) => a !== '--rebuild' && a !== '--full').join(' ').trim();
if (!query) {
  console.error('ERROR: no query term. Usage: node scripts/youtube-search.js [--rebuild] <query terms...>');
  process.exit(1);
}

const TOKEN_URI = 'https://oauth2.googleapis.com/token';
const API = 'https://www.googleapis.com/youtube/v3';
const CACHE_PATH = process.env.YOUTUBE_CACHE_PATH || path.join(os.homedir(), '.cache', 'dof-youtube-titles.json');

async function accessToken() {
  const params = new URLSearchParams({
    client_id: CLIENT_ID,
    client_secret: CLIENT_SECRET,
    refresh_token: REFRESH_TOKEN,
    grant_type: 'refresh_token',
  });
  const res = await fetch(TOKEN_URI, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString(),
  });
  if (!res.ok) throw new Error(`OAuth token refresh ${res.status}: ${await res.text()}`);
  return (await res.json()).access_token;
}

async function api(token, path_, params) {
  const url = `${API}/${path_}?${new URLSearchParams(params).toString()}`;
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error(`YouTube API ${path_} ${res.status}: ${await res.text()}`);
  return res.json();
}

async function uploadsPlaylistId(token) {
  const data = await api(token, 'channels', { part: 'contentDetails', mine: 'true' });
  const ch = (data.items || [])[0];
  if (!ch) throw new Error('No channel found for this account (is the refresh token for dofofapple?).');
  return ch.contentDetails.relatedPlaylists.uploads;
}

function pageItems(data) {
  return (data.items || []).map((it) => ({
    id: it.contentDetails.videoId,
    name: it.snippet.title,
    published: it.contentDetails.videoPublishedAt,
  }));
}

// Page the uploads playlist (newest first). If `knownIds` given, stop as soon as a
// cached id is seen (incremental top-up). Returns NEW items, newest-first.
async function pageUploads(token, playlistId, knownIds) {
  const out = [];
  let pageToken;
  for (;;) {
    const params = { part: 'snippet,contentDetails', playlistId, maxResults: '50' };
    if (pageToken) params.pageToken = pageToken;
    const data = await api(token, 'playlistItems', params);
    for (const v of pageItems(data)) {
      if (knownIds && knownIds.has(v.id)) return out; // hit cache boundary → done
      out.push(v);
    }
    if (!data.nextPageToken) break;
    pageToken = data.nextPageToken;
  }
  return out;
}

function loadCache() {
  try {
    const j = JSON.parse(fs.readFileSync(CACHE_PATH, 'utf8'));
    if (Array.isArray(j.videos)) return j.videos;
  } catch (_) {
    /* missing / corrupt → rebuild */
  }
  return null;
}

function saveCache(videos) {
  try {
    fs.mkdirSync(path.dirname(CACHE_PATH), { recursive: true });
    fs.writeFileSync(CACHE_PATH, JSON.stringify({ updatedAt: new Date().toISOString(), videos }));
  } catch (_) {
    // Non-fatal: a read-only fs just means no caching speedup, search still works.
  }
}

// videos.list batch — resolve privacyStatus + duration live (never cached)
async function enrich(token, ids) {
  const map = {};
  for (let i = 0; i < ids.length; i += 50) {
    const batch = ids.slice(i, i + 50);
    if (!batch.length) break;
    const data = await api(token, 'videos', { part: 'status,contentDetails', id: batch.join(',') });
    for (const v of data.items || []) {
      map[v.id] = {
        privacy: v.status && v.status.privacyStatus,
        duration: v.contentDetails && v.contentDetails.duration,
      };
    }
  }
  return map;
}

(async () => {
  const token = await accessToken();
  const uploads = await uploadsPlaylistId(token);

  const cached = rebuild ? null : loadCache();
  let videos;
  let mode;
  if (!cached) {
    mode = rebuild ? 'rebuild' : 'full-build';
    videos = await pageUploads(token, uploads); // full scan
  } else {
    mode = 'cache';
    const knownIds = new Set(cached.map((v) => v.id));
    const fresh = await pageUploads(token, uploads, knownIds); // newest-first, stops at boundary
    videos = fresh.concat(cached); // newest first
  }
  saveCache(videos);

  // Exact case-insensitive substring: every query word must appear in the title.
  const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
  const matched = videos.filter((v) => {
    const n = (v.name || '').toLowerCase();
    return terms.every((t) => n.includes(t));
  });

  const meta = await enrich(token, matched.map((v) => v.id));
  // Drop entries that no longer resolve (e.g. deleted video lingering in cache).
  const results = matched
    .filter((v) => meta[v.id])
    .map((v) => ({
      id: v.id,
      name: v.name,
      link: `https://youtu.be/${v.id}`,
      privacy: meta[v.id].privacy,
      published: v.published,
      duration: meta[v.id].duration,
    }));

  console.log(JSON.stringify({ query, mode, scanned: videos.length, count: results.length, results }, null, 2));
})().catch((err) => {
  console.error('YOUTUBE SEARCH FAILED:', err.message);
  process.exit(1);
});
