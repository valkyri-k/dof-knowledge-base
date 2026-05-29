#!/usr/bin/env node
// sync-job-list.js — refresh context/job-list.md from Airtable Master Job Log.
//
// Deterministic file op only (no judgment): fetches status=Current jobs via REST
// (env PAT, NOT cloud MCP), MERGES into the existing cache preserving manual
// aliases + "— (no channel by design)" annotations, rewrites the Active Jobs
// table, and prints a JSON diff summary on stdout. All coverage / allowlist
// judgment is left to Mugi reading that diff — see
// skills/producer/update-job-list.md.

const fs = require('fs');
const path = require('path');

const BASE_ID = 'appld5YU1iZm3Hx5F';
const TABLE_ID = 'tblaerjD8rDr0LjGK';
const CACHE_PATH = path.join(__dirname, '..', 'context', 'job-list.md');
const FIELDS = ['job_number', 'project_title', 'Aliases', 'brand', 'status', 'director', 'discord_channel_id', 'discord_channel_name'];

const PAT = process.env.AIRTABLE_PAT;
if (!PAT) {
  console.error('ERROR: AIRTABLE_PAT env var not set (Zeabur Variables). Aborting — do NOT fall back to cloud Airtable MCP.');
  process.exit(1);
}

function todayHK() {
  const fmt = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Hong_Kong', year: 'numeric', month: '2-digit', day: '2-digit' });
  return fmt.format(new Date()); // YYYY-MM-DD
}

function splitMulti(s) {
  if (!s) return [];
  return String(s).split(/[;,]/).map(x => x.trim()).filter(Boolean);
}

function unionAliases(cacheAliases, airtableAliases) {
  const out = [];
  const seen = new Set();
  for (const a of [...splitMulti(cacheAliases), ...splitMulti(airtableAliases)]) {
    const k = a.toLowerCase();
    if (!seen.has(k)) { seen.add(k); out.push(a); }
  }
  return out.join(';');
}

function isNoChannel(v) {
  return typeof v === 'string' && v.trim().startsWith('—');
}

async function fetchCurrentJobs() {
  const records = [];
  let offset;
  do {
    const params = new URLSearchParams();
    params.set('filterByFormula', '{status}="Current"');
    params.set('cellFormat', 'string');
    params.set('timeZone', 'Asia/Hong_Kong');
    params.set('userLocale', 'en');
    for (const f of FIELDS) params.append('fields[]', f);
    if (offset) params.set('offset', offset);
    const url = `https://api.airtable.com/v0/${BASE_ID}/${TABLE_ID}?${params.toString()}`;
    const res = await fetch(url, { headers: { Authorization: `Bearer ${PAT}` } });
    if (!res.ok) {
      const body = await res.text();
      throw new Error(`Airtable API ${res.status}: ${body}`);
    }
    const data = await res.json();
    records.push(...data.records);
    offset = data.offset;
  } while (offset);
  return records;
}

function parseCache(text) {
  const lines = text.split('\n');
  const map = {};
  let inTable = false;
  for (const line of lines) {
    if (line.startsWith('| Job No ')) { inTable = true; continue; }
    if (inTable) {
      if (!line.startsWith('|')) break;
      if (/^\|\s*-+/.test(line)) continue; // separator row
      const cells = line.split('|').slice(1, -1).map(c => c.trim());
      if (cells.length < 8) continue;
      const [jobNo, client, projectName, aliases, status, director, channelId, channelName] = cells;
      map[jobNo] = { jobNo, client, projectName, aliases, status, director, channelId, channelName };
    }
  }
  return map;
}

function buildRow(r) {
  return `| ${r.jobNo} | ${r.client} | ${r.projectName} | ${r.aliases} | ${r.status} | ${r.director} | ${r.channelId} | ${r.channelName} |`;
}

function rewriteCache(text, rows, syncDate) {
  const lines = text.split('\n');
  const out = [];
  let i = 0;
  // 1. Header block: replace the "> Last synced:" line.
  for (; i < lines.length; i++) {
    if (lines[i].startsWith('> Last synced:')) {
      out.push(`> Last synced: ${syncDate}（auto-sync via \`scripts/sync-job-list.js\`）`);
    } else if (lines[i].startsWith('| Job No ')) {
      break;
    } else {
      out.push(lines[i]);
    }
  }
  // 2. Table header + separator (keep as-is), then our generated data rows.
  out.push(lines[i]);     // | Job No | ... |
  out.push(lines[i + 1]); // |--------|...|
  i += 2;
  // skip old data rows
  while (i < lines.length && lines[i].startsWith('|')) i++;
  for (const r of rows) out.push(buildRow(r));
  // 3. Everything after the old table, verbatim.
  for (; i < lines.length; i++) out.push(lines[i]);
  return out.join('\n');
}

(async () => {
  const cacheText = fs.readFileSync(CACHE_PATH, 'utf8');
  const cache = parseCache(cacheText);
  const records = await fetchCurrentJobs();

  const rows = [];
  const diff = {
    syncDate: todayHK(),
    addedWithChannel: [],     // new Current job, has channel → /discord:access allowlist candidate
    addedNoChannel: [],       // new Current job, no channel → coverage decision needed (open? or no-channel-by-design?)
    removed: [],              // was in cache, no longer status=Current
    channelDrift: [],         // Airtable channel empty but cache had a real channel — investigate
    aliasMerged: [],          // cache-local manual aliases preserved into union
  };

  const seenJobNos = new Set();

  for (const rec of records) {
    const f = rec.fields;
    const jobNo = (f.job_number || '').trim();
    if (!jobNo) continue;
    seenJobNos.add(jobNo);
    const cached = cache[jobNo];

    const client = (f.brand || '').trim() || '—';
    const projectName = (f.project_title || '').trim();
    const director = splitMulti(f.director).join(';') || '—';
    const atAliases = (f.Aliases || '').trim();
    const atCid = (f.discord_channel_id || '').trim();
    const atCname = (f.discord_channel_name || '').trim();

    // Aliases: union Airtable + cache-local manual aliases.
    const aliases = cached ? unionAliases(cached.aliases, atAliases) : atAliases;
    if (cached && splitMulti(cached.aliases).some(a => !splitMulti(atAliases).map(x => x.toLowerCase()).includes(a.toLowerCase()))) {
      diff.aliasMerged.push({ jobNo, preserved: aliases });
    }

    // Channel resolution.
    let channelId, channelName;
    if (atCid) {
      channelId = atCid;
      channelName = atCname || (cached ? cached.channelName : '');
      if (!cached) diff.addedWithChannel.push({ jobNo, client, projectName, channelId, channelName });
    } else if (cached && isNoChannel(cached.channelId)) {
      channelId = cached.channelId;       // preserve "— (no channel by design)"
      channelName = cached.channelName;
    } else if (cached && cached.channelId && !isNoChannel(cached.channelId) && cached.channelId !== '—') {
      channelId = cached.channelId;       // Airtable empty, cache has real channel → preserve + flag
      channelName = cached.channelName;
      diff.channelDrift.push({ jobNo, cacheChannelId: cached.channelId });
    } else {
      channelId = '—';                    // brand-new job, no channel anywhere
      channelName = '—';
      if (!cached) diff.addedNoChannel.push({ jobNo, client, projectName });
    }

    rows.push({ jobNo, client, projectName, aliases, status: 'Current', director, channelId, channelName });
  }

  // Jobs in cache but no longer Current.
  for (const jobNo of Object.keys(cache)) {
    if (!seenJobNos.has(jobNo)) diff.removed.push({ jobNo, projectName: cache[jobNo].projectName });
  }

  rows.sort((a, b) => a.jobNo.localeCompare(b.jobNo));

  const newText = rewriteCache(cacheText, rows, diff.syncDate);
  fs.writeFileSync(CACHE_PATH, newText, 'utf8');

  console.log(JSON.stringify(diff, null, 2));
})().catch(err => {
  console.error('SYNC FAILED:', err.message);
  process.exit(1);
});
