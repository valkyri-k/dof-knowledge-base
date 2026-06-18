#!/usr/bin/env node
// youtube-search.js — search the DOF (dofofapple) YouTube channel by title text.
//
// Mirror of vimeo-search.js. Read-only lookup (no Airtable / no Job# join): takes
// a query term, authenticates to the dofofapple channel via OAuth refresh token
// (env YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET / YOUTUBE_REFRESH_TOKEN, NOT cloud
// MCP), lists the channel's uploads playlist (which, as the channel owner, includes
// unlisted videos), local-filters by title, and prints a JSON array of matched
// videos (name + youtu.be link + privacy) on stdout.
//
// Usage: node scripts/youtube-search.js <query terms...>
//   e.g. node scripts/youtube-search.js EMSD Dems Briefing

const CLIENT_ID = process.env.YOUTUBE_CLIENT_ID;
const CLIENT_SECRET = process.env.YOUTUBE_CLIENT_SECRET;
const REFRESH_TOKEN = process.env.YOUTUBE_REFRESH_TOKEN;

if (!CLIENT_ID || !CLIENT_SECRET || !REFRESH_TOKEN) {
  console.error(
    'ERROR: YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET / YOUTUBE_REFRESH_TOKEN env not all set (Zeabur Variables). Aborting — do NOT fall back to any cloud MCP or hand-written API call.'
  );
  process.exit(1);
}

const query = process.argv.slice(2).join(' ').trim();
if (!query) {
  console.error('ERROR: no query term. Usage: node scripts/youtube-search.js <query terms...>');
  process.exit(1);
}

const TOKEN_URI = 'https://oauth2.googleapis.com/token';
const API = 'https://www.googleapis.com/youtube/v3';

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

async function api(token, path, params) {
  const url = `${API}/${path}?${new URLSearchParams(params).toString()}`;
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error(`YouTube API ${path} ${res.status}: ${await res.text()}`);
  return res.json();
}

async function uploadsPlaylistId(token) {
  const data = await api(token, 'channels', { part: 'contentDetails', mine: 'true' });
  const ch = (data.items || [])[0];
  if (!ch) throw new Error('No channel found for this account (is the refresh token for dofofapple?).');
  return ch.contentDetails.relatedPlaylists.uploads;
}

async function allUploads(token, playlistId) {
  const out = [];
  let pageToken;
  for (;;) {
    const params = { part: 'snippet,contentDetails', playlistId, maxResults: '50' };
    if (pageToken) params.pageToken = pageToken;
    const data = await api(token, 'playlistItems', params);
    for (const it of data.items || []) {
      out.push({
        id: it.contentDetails.videoId,
        name: it.snippet.title,
        published: it.contentDetails.videoPublishedAt,
      });
    }
    if (!data.nextPageToken) break;
    pageToken = data.nextPageToken;
  }
  return out;
}

// videos.list batch — resolve privacyStatus + duration (playlistItems doesn't carry privacy)
async function enrich(token, ids) {
  const map = {};
  for (let i = 0; i < ids.length; i += 50) {
    const batch = ids.slice(i, i + 50);
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
  const vids = await allUploads(token, uploads);

  // Broad local title filter: every query word must appear (case-insensitive).
  const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
  const matched = vids.filter((v) => {
    const n = (v.name || '').toLowerCase();
    return terms.every((t) => n.includes(t));
  });

  const meta = await enrich(token, matched.map((v) => v.id));
  const results = matched.map((v) => ({
    id: v.id,
    name: v.name,
    link: `https://youtu.be/${v.id}`,
    privacy: meta[v.id] && meta[v.id].privacy,
    published: v.published,
    duration: meta[v.id] && meta[v.id].duration,
  }));

  console.log(JSON.stringify({ query, count: results.length, results }, null, 2));
})().catch((err) => {
  console.error('YOUTUBE SEARCH FAILED:', err.message);
  process.exit(1);
});
