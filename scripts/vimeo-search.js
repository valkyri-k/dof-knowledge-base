#!/usr/bin/env node
// vimeo-search.js — search the DOF Vimeo account by title text.
//
// Read-only lookup (Layer 1, no Airtable / no Job# join): takes a query term,
// hits Vimeo's native title search via REST (env VIMEO_TOKEN, NOT cloud MCP),
// paginates, and prints a JSON array of matched videos (name + link + privacy)
// on stdout. Job# ↔ video join is Layer 2 and lives elsewhere — see
// skills/integration/vimeo-search.md.
//
// Usage: node scripts/vimeo-search.js <query terms...>
//   e.g. node scripts/vimeo-search.js EMSD Dems Briefing

const TOKEN = process.env.VIMEO_TOKEN;
if (!TOKEN) {
  console.error('ERROR: VIMEO_TOKEN env var not set (Zeabur Variables). Aborting — do NOT fall back to any cloud MCP or hand-written API call.');
  process.exit(1);
}

const query = process.argv.slice(2).join(' ').trim();
if (!query) {
  console.error('ERROR: no query term. Usage: node scripts/vimeo-search.js <query terms...>');
  process.exit(1);
}

const PER_PAGE = 100;
const FIELDS = 'uri,name,link,privacy.view,created_time,duration';

function idFromUri(uri) {
  // uri is like "/videos/1103377505" → stable video ID key
  return (uri || '').split('/').pop();
}

async function search(term) {
  const out = [];
  let page = 1;
  for (;;) {
    const params = new URLSearchParams();
    params.set('query', term);
    params.set('per_page', String(PER_PAGE));
    params.set('page', String(page));
    params.set('fields', FIELDS);
    const url = `https://api.vimeo.com/me/videos?${params.toString()}`;
    const res = await fetch(url, {
      headers: {
        Authorization: `Bearer ${TOKEN}`,
        Accept: 'application/vnd.vimeo.*+json;version=3.4',
      },
    });
    if (!res.ok) {
      const body = await res.text();
      throw new Error(`Vimeo API ${res.status}: ${body}`);
    }
    const data = await res.json();
    for (const v of data.data || []) {
      out.push({
        id: idFromUri(v.uri),
        name: v.name,
        link: v.link,
        privacy: v.privacy && v.privacy.view,
        created: v.created_time,
        duration: v.duration,
      });
    }
    if (!data.paging || !data.paging.next) break;
    page += 1;
  }
  return out;
}

(async () => {
  const results = await search(query);
  console.log(JSON.stringify({ query, count: results.length, results }, null, 2));
})().catch(err => {
  console.error('VIMEO SEARCH FAILED:', err.message);
  process.exit(1);
});
