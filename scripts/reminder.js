#!/usr/bin/env node
// reminder.js — ad-hoc reminder CRUD against the "DOF Reminders" Airtable queue.
//
// Deterministic Airtable op only (no judgment): set / list / cancel / edit rows
// in the standalone DOF Reminders base via REST (env PAT, NOT cloud MCP). The
// consumer side is n8n workflow d4VcGHDHLfeVKjgr (Reminder Poster, 5-min poll)
// which posts type=replay rows whose fire_at has passed, then flips status.
//
// All judgment — parsing the request, computing fire_at, resolving target
// channel + @-mentions, deciding WHICH row to edit/cancel from conversation
// context — lives in the Mugi skill, see skills/integration/reminder-set.md.
//
// Usage (container-side, AIRTABLE_PAT in env):
//   echo '{"label":"...","fire_at":"2026-06-18T22:30:00+08:00","target":"<channelId>","payload":"..."}' | node scripts/reminder.js set
//   node scripts/reminder.js list            # pending only (the actionable queue)
//   node scripts/reminder.js list --all      # every row regardless of status
//   echo '{"fire_at":"...","payload":"..."}'  | node scripts/reminder.js edit <recordId>
//   node scripts/reminder.js cancel <recordId>
//
// set/edit read their field object as JSON from stdin (robust against CJK,
// newlines, quotes in payload — prefer a quoted heredoc). Each command prints
// a JSON result on stdout for Mugi to read back; non-zero exit on failure.

const BASE_ID = 'appaAEiqHzUfLCGAU';
const TABLE_ID = 'tblw5MnnAesrKSV43'; // "Reminders"
const API = `https://api.airtable.com/v0/${BASE_ID}/${TABLE_ID}`;

const PAT = process.env.AIRTABLE_PAT;
if (!PAT) {
  console.error('ERROR: AIRTABLE_PAT env var not set (Zeabur Variables). Aborting — do NOT fall back to cloud Airtable MCP.');
  process.exit(1);
}

const AUTH = { Authorization: `Bearer ${PAT}` };
const JSON_HEADERS = { ...AUTH, 'Content-Type': 'application/json' };

function readStdin() {
  return new Promise((resolve, reject) => {
    let buf = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', d => (buf += d));
    process.stdin.on('end', () => resolve(buf));
    process.stdin.on('error', reject);
  });
}

async function readJsonStdin(cmd) {
  const raw = (await readStdin()).trim();
  if (!raw) throw new Error(`${cmd}: expected a JSON object on stdin (pipe it in, e.g. via a quoted heredoc).`);
  try {
    return JSON.parse(raw);
  } catch (e) {
    throw new Error(`${cmd}: stdin is not valid JSON — ${e.message}`);
  }
}

async function apiCall(method, urlSuffix, body) {
  const url = `${API}${urlSuffix || ''}`;
  const opts = { method, headers: body ? JSON_HEADERS : AUTH };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Airtable API ${res.status} (${method} ${urlSuffix || '/'}): ${text}`);
  }
  return res.json();
}

function slim(rec) {
  const f = rec.fields || {};
  return {
    id: rec.id,
    label: f.label || '',
    fire_at: f.fire_at || '',
    target: f.target || '',
    type: f.type || '',
    status: f.status || '',
    requested_by: f.requested_by || '',
    requested_by_id: f.requested_by_id || '',
    payload: f.payload || '',
  };
}

async function cmdSet() {
  const o = await readJsonStdin('set');
  for (const k of ['label', 'fire_at', 'target', 'payload']) {
    if (!o[k] || !String(o[k]).trim()) throw new Error(`set: missing required field "${k}".`);
  }
  const fields = {
    label: String(o.label).trim(),
    fire_at: String(o.fire_at).trim(),
    target: String(o.target).trim(),
    payload: String(o.payload),
    type: (o.type && String(o.type).trim()) || 'replay',
    status: 'pending',
  };
  // optional provenance: who issued the instruction (Discord envelope user / user_id)
  for (const k of ['requested_by', 'requested_by_id']) {
    if (o[k] && String(o[k]).trim()) fields[k] = String(o[k]).trim();
  }
  const data = await apiCall('POST', '', { records: [{ fields }], typecast: true });
  console.log(JSON.stringify(slim(data.records[0]), null, 2));
}

async function cmdList() {
  const all = process.argv.includes('--all');
  const params = new URLSearchParams();
  if (!all) params.set('filterByFormula', "{status}='pending'");
  params.set('cellFormat', 'string');
  params.set('timeZone', 'Asia/Hong_Kong');
  params.set('userLocale', 'en');
  params.append('sort[0][field]', 'fire_at');
  params.append('sort[0][direction]', 'asc');
  const records = [];
  let offset;
  do {
    if (offset) params.set('offset', offset);
    const data = await apiCall('GET', `?${params.toString()}`);
    records.push(...data.records);
    offset = data.offset;
  } while (offset);
  console.log(JSON.stringify(records.map(slim), null, 2));
}

async function cmdEdit() {
  const id = process.argv[3];
  if (!id) throw new Error('edit: missing <recordId> (arg 3).');
  const o = await readJsonStdin('edit');
  const fields = {};
  for (const k of ['label', 'fire_at', 'target', 'payload', 'type', 'requested_by', 'requested_by_id']) {
    if (o[k] !== undefined) fields[k] = k === 'payload' ? String(o[k]) : String(o[k]).trim();
  }
  if (Object.keys(fields).length === 0) throw new Error('edit: stdin JSON had no editable field (label/fire_at/target/payload/type/requested_by/requested_by_id).');
  const data = await apiCall('PATCH', '', { records: [{ id, fields }], typecast: true });
  console.log(JSON.stringify(slim(data.records[0]), null, 2));
}

async function cmdCancel() {
  const id = process.argv[3];
  if (!id) throw new Error('cancel: missing <recordId> (arg 3).');
  const data = await apiCall('DELETE', `/${id}`);
  console.log(JSON.stringify({ cancelled: data.id || id, deleted: data.deleted !== false }, null, 2));
}

const cmd = process.argv[2];
const handlers = { set: cmdSet, list: cmdList, edit: cmdEdit, cancel: cmdCancel };
const handler = handlers[cmd];
if (!handler) {
  console.error(`reminder.js: unknown command "${cmd || ''}". Use: set | list | cancel | edit`);
  process.exit(1);
}
handler().catch(err => {
  console.error('REMINDER FAILED:', err.message);
  process.exit(1);
});
