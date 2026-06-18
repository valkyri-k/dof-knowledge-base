#!/usr/bin/env node
// youtube-edit.js — read or change a dofofapple YouTube video's privacy /
// description / title, by video id.
//
// Companion to youtube-search.js (same OAuth creds). Used when a client asks us to
// pull a shared video back to private, or to fix a description/title. Authenticates
// to the dofofapple channel via OAuth refresh token (env YOUTUBE_CLIENT_ID /
// YOUTUBE_CLIENT_SECRET / YOUTUBE_REFRESH_TOKEN — needs the `youtube` manage scope,
// NOT cloud MCP), GETs the video's current snippet+status, and (only if change flags
// are given) PUTs videos.update. Prints before/after JSON on stdout.
//
// Usage:
//   node scripts/youtube-edit.js <videoId>                          # read-only: show current state
//   node scripts/youtube-edit.js <videoId> --privacy private
//   node scripts/youtube-edit.js <videoId> --description "new description text"
//   node scripts/youtube-edit.js <videoId> --title "New Title" --privacy unlisted

const CLIENT_ID = process.env.YOUTUBE_CLIENT_ID;
const CLIENT_SECRET = process.env.YOUTUBE_CLIENT_SECRET;
const REFRESH_TOKEN = process.env.YOUTUBE_REFRESH_TOKEN;

if (!CLIENT_ID || !CLIENT_SECRET || !REFRESH_TOKEN) {
  console.error(
    'ERROR: YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET / YOUTUBE_REFRESH_TOKEN env not all set (Zeabur Variables). Aborting — do NOT fall back to any cloud MCP or hand-written API call.'
  );
  process.exit(1);
}

// --- parse args ---
const argv = process.argv.slice(2);
const videoId = argv[0];
if (!videoId || videoId.startsWith('--')) {
  console.error(
    'ERROR: missing <videoId>. Usage: node scripts/youtube-edit.js <videoId> [--privacy public|unlisted|private] [--description "..."] [--title "..."]'
  );
  process.exit(1);
}

function flag(name) {
  const i = argv.indexOf(`--${name}`);
  return i >= 0 ? argv[i + 1] : undefined;
}

const newPrivacy = flag('privacy');
const newDescription = flag('description');
const newTitle = flag('title');

if (newPrivacy && !['public', 'unlisted', 'private'].includes(newPrivacy)) {
  console.error(`ERROR: --privacy must be public | unlisted | private (got "${newPrivacy}")`);
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

async function getVideo(token, id) {
  const url = `${API}/videos?${new URLSearchParams({ part: 'snippet,status', id }).toString()}`;
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error(`videos.list ${res.status}: ${await res.text()}`);
  const data = await res.json();
  const v = (data.items || [])[0];
  if (!v) throw new Error(`No video found for id "${id}" on this channel (is it owned by dofofapple?).`);
  return v;
}

async function updateVideo(token, body, part) {
  const url = `${API}/videos?${new URLSearchParams({ part }).toString()}`;
  const res = await fetch(url, {
    method: 'PUT',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`videos.update ${res.status}: ${await res.text()}`);
  return res.json();
}

(async () => {
  const token = await accessToken();
  const current = await getVideo(token, videoId);

  const before = {
    name: current.snippet.title,
    privacy: current.status.privacyStatus,
    description: current.snippet.description,
    link: `https://youtu.be/${videoId}`,
  };

  const wantsWrite =
    newPrivacy !== undefined || newDescription !== undefined || newTitle !== undefined;
  if (!wantsWrite) {
    // No change flags → read-only preview (use this to confirm with the user first).
    console.log(JSON.stringify({ id: videoId, mode: 'read', current: before }, null, 2));
    return;
  }

  // videos.update REPLACES each part it's given, so carry over existing writable
  // fields and override only what changed.
  const body = { id: videoId };
  const parts = [];

  if (newDescription !== undefined || newTitle !== undefined) {
    body.snippet = {
      title: newTitle !== undefined ? newTitle : current.snippet.title, // required by API
      categoryId: current.snippet.categoryId, // required by API
      description: newDescription !== undefined ? newDescription : current.snippet.description,
    };
    if (current.snippet.tags) body.snippet.tags = current.snippet.tags;
    if (current.snippet.defaultLanguage) body.snippet.defaultLanguage = current.snippet.defaultLanguage;
    parts.push('snippet');
  }

  if (newPrivacy !== undefined) {
    body.status = { privacyStatus: newPrivacy };
    for (const k of ['embeddable', 'license', 'publicStatsViewable', 'selfDeclaredMadeForKids']) {
      if (current.status[k] !== undefined) body.status[k] = current.status[k];
    }
    parts.push('status');
  }

  const updated = await updateVideo(token, body, parts.join(','));

  const after = {
    name: updated.snippet ? updated.snippet.title : before.name,
    privacy: updated.status ? updated.status.privacyStatus : before.privacy,
    description: updated.snippet ? updated.snippet.description : before.description,
    link: `https://youtu.be/${videoId}`,
  };

  const changes = {};
  if (before.name !== after.name) changes.title = { from: before.name, to: after.name };
  if (before.privacy !== after.privacy) changes.privacy = { from: before.privacy, to: after.privacy };
  if (before.description !== after.description)
    changes.description = { from: before.description, to: after.description };

  console.log(JSON.stringify({ id: videoId, mode: 'write', changes, before, after }, null, 2));
})().catch((err) => {
  console.error('YOUTUBE EDIT FAILED:', err.message);
  process.exit(1);
});
