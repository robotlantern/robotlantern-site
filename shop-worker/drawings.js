// The drawings API (docs/ORDERS.md, "Drawings API"): a customer's square photo in, a red-on-white stencil
// drawing out, from OpenAI's GPT Image, under decision 21's caps. Or the customer's own drawing, stored as
// it is (decision 28). Ready-made designs never come here (decision 30).
//
// KV: drawing:<id> is the record; file:drawing:<id>/photo.jpg and file:drawing:<id>/<n>.png are the files.
// All of it expires two days after the first try, unless an order is paid, which copies what it needs.
// The photo and the drawings are never logged; the logs carry IDs, try numbers and token counts.

import limits from './limits.json';
import stubDrawing from './stub-drawing.png';
import {
  DAY, ID, MAGIC, MiB, UNPAID_SECONDS, bodyLength, bump, count, drawingProduct, globalStore, hex, iso, json,
  newId, now, product, refuse, secondsToMidnight, store, switchedOff, thisMonth, today, tokenMode,
} from './lib.js';

const PHOTO_MAX = 4 * MiB;
const UPLOAD_MAX = 4 * MiB;
const OPENAI = 'https://api.openai.com/v1/images/edits';

// POST /api/drawings and POST /api/drawings/<id>/again
export async function drawings(request, env, mode, id, part) {
  if (request.method !== 'POST') refuse(405, 'Use POST.');
  if (!id) {
    const source = request.headers.get('x-source') || 'made';
    if (source === 'upload') return upload(request, env, mode);
    if (source !== 'made') refuse(400, `Drawings from ${source} aren't taken yet.`);
    return first(request, env, mode);
  }
  if (!ID.test(id) || part !== 'again') refuse(404, 'Not found');
  return again(request, env, mode, id);
}

async function first(request, env, mode) {
  const [slug, p] = drawingProduct(request, mode);
  const subject = madeSubject(p, request.headers.get('x-subject'));
  const kv = store(env, mode);
  if (await switchedOff(kv, 'drawings')) off();
  if (contentType(request) !== 'image/jpeg') refuse(415, 'Send the photo as image/jpeg.');
  bodyLength(request, PHOTO_MAX);
  const photo = new Uint8Array(await request.arrayBuffer());
  const edge = p.photo.edge || 1024;
  const size = jpegSize(photo);
  if (!size) refuse(415, "That isn't a JPEG.");
  if (size.width !== edge || size.height !== edge) {
    refuse(400, `The photo must be ${edge} × ${edge} pixels; this one is ${size.width} × ${size.height}.`);
  }
  const who = await visitor(request, env, mode, kv);
  await capsAllow(env, kv, who);

  const id = newId();
  const t = now();
  const expires = t + UNPAID_SECONDS;
  const made = await draw(env, p, subject, photo, who, { id, n: 1 });
  const rec = {
    id, mode, product: slug, subject: subject.id, source: 'made', tries: 1,
    created: iso(t), expires,
  };
  await Promise.all([
    kv.put(`file:drawing:${id}/photo.jpg`, photo, { expiration: expires, metadata: { size: photo.length, type: 'image/jpeg' } }),
    kv.put(`file:drawing:${id}/1.png`, made.png, { expiration: expires, metadata: { size: made.png.length, type: 'image/png' } }),
    kv.put(`drawing:${id}`, JSON.stringify(rec), { expiration: expires }),
    counted(env, kv, who, 'drawings'),
  ]);
  return json({
    id, n: 1, left: p.drawing.triesPerPhoto - 1, source: 'made', subject: subject.id,
    expires: iso(expires), image: made.b64,
  }, 201);
}

async function again(request, env, mode, id) {
  const kv = store(env, mode);
  const rec = await kv.get(`drawing:${id}`, 'json');
  if (!rec) refuse(404, 'That drawing has expired. Drawings are kept two days; please start again.');
  if (rec.source !== 'made') refuse(409, 'Your own drawing has no tries. Send another to change it.', { left: 0 });
  const p = product(rec.product, mode);
  const tries = p.drawing.triesPerPhoto;
  if (rec.tries >= tries) refuse(409, `That photo has had all ${tries} tries.`, { left: 0 });
  if (rec.expires - now() < 3600) refuse(410, 'That drawing is about to expire; please start again.');
  if (await switchedOff(kv, 'drawings')) off();
  const subject = madeSubject(p, rec.subject);
  const who = await visitor(request, env, mode, kv);
  await capsAllow(env, kv, who);

  const photo = await kv.get(`file:drawing:${id}/photo.jpg`, 'arrayBuffer');
  if (!photo) refuse(410, 'That photo has expired; please start again.');
  const n = rec.tries + 1;
  const made = await draw(env, p, subject, new Uint8Array(photo), who, { id, n });
  rec.tries = n;
  await Promise.all([
    kv.put(`file:drawing:${id}/${n}.png`, made.png, { expiration: rec.expires, metadata: { size: made.png.length, type: 'image/png' } }),
    kv.put(`drawing:${id}`, JSON.stringify(rec), { expiration: rec.expires }),
    counted(env, kv, who, 'drawings'),
  ]);
  return json({ id, n, left: tries - n, source: 'made', subject: subject.id, expires: iso(rec.expires), image: made.b64 }, 201);
}

// X-Source: upload. The page has already checked the drawing and squared it (docs/ORDERS.md, "Own drawings");
// the Worker reads only the PNG signature and IHDR.
async function upload(request, env, mode) {
  const [slug, p] = drawingProduct(request, mode);
  const named = request.headers.get('x-subject');
  const subject = named ? madeSubject(p, named) : null;
  const kv = store(env, mode);
  if (contentType(request) !== 'image/png') refuse(415, 'Send your drawing as image/png.');
  bodyLength(request, UPLOAD_MAX);
  const png = new Uint8Array(await request.arrayBuffer());
  const size = pngSize(png);
  if (!size) refuse(415, "That isn't a PNG.");
  const edge = p.photo.edge || 1024;
  if (size.width !== edge || size.height !== edge) {
    refuse(400, `Your drawing must be ${edge} × ${edge} pixels; this one is ${size.width} × ${size.height}.`);
  }
  const who = await visitor(request, env, mode, kv);
  const key = `count:${today()}:uploads:${who.hash}`;
  if ((await count(kv, key)) >= limits.uploadsPerVisitorPerDay) capped("You've sent as many drawings as we take in a day.");

  const id = newId();
  const t = now();
  const expires = t + UNPAID_SECONDS;
  const rec = {
    id, mode, product: slug, subject: subject?.id || null, source: 'upload', tries: 1,
    created: iso(t), expires,
  };
  await Promise.all([
    kv.put(`file:drawing:${id}/1.png`, png, { expiration: expires, metadata: { size: png.length, type: 'image/png' } }),
    kv.put(`drawing:${id}`, JSON.stringify(rec), { expiration: expires }),
    bump(kv, key, 1, 2 * DAY),
    bump(kv, `stats:uploads:${today()}`, 1, 40 * DAY),
  ]);
  console.log(JSON.stringify({ drawing: id, source: 'upload' }));
  return json({ id, n: 1, left: 0, source: 'upload', subject: rec.subject, expires: iso(expires) }, 201);
}

function madeSubject(p, id) {
  const made = p.drawing.subjects.filter((s) => s.source === 'made');
  const s = p.drawing.subjects.find((x) => x.id === id);
  if (!s) refuse(400, `Say what's in the photo with X-Subject: ${made.map((x) => x.id).join(' or ')}.`);
  if (s.source !== 'made') refuse(400, `${s.label} are ready-made: order one by name, with no drawing.`);
  return s;
}

function off() {
  refuse(503, "We're not making drawings just now. Please come back later.", { off: true });
}

function capped(message) {
  refuse(429, `${message} Please come back tomorrow.`, { retryAfter: secondsToMidnight() });
}

function contentType(request) {
  return (request.headers.get('content-type') || '').split(';')[0].trim().toLowerCase();
}

// ---- caps (docs/ORDERS.md, "Caps"; limits.json) ----------------------------------------------

// Who's asking, for the caps: a SHA-256 of the IP address and that day's salt, kept one day and never
// logged. A Signature-Agent header moves a request into the agents' shared pool (decision 28). In the
// sandbox only, a test run with the queue's token and X-Stub gets its own pool and a stub drawing.
async function visitor(request, env, mode, kv) {
  const stubbed = request.headers.get('x-stub');
  const stub = stubbed && mode === 'test' && (await tokenMode(request, env)) === 'test'
    ? `stub-${stubbed.replace(/[^a-z0-9-]/gi, '').slice(0, 24)}` : null;
  const agent = request.headers.has('signature-agent');
  const day = today();
  let salt = await kv.get(`salt:${day}`);
  if (!salt) {
    salt = hex(crypto.getRandomValues(new Uint8Array(16)));
    await kv.put(`salt:${day}`, salt, { expirationTtl: 2 * DAY });
  }
  const ip = request.headers.get('cf-connecting-ip') || '';
  const hash = hex(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(`${salt}:${ip}`))).slice(0, 32);
  return { stub, agent, hash: stub || hash, user: hash, day };
}

function poolKey(who) {
  return who.agent
    ? [`count:${who.day}:agents${who.stub ? `:${who.stub}` : ''}`, limits.agentDrawingsPerDay]
    : [`count:${who.day}:drawings:${who.hash}`, limits.perVisitorPerDay];
}

async function capsAllow(env, kv, who) {
  const [key, cap] = poolKey(who);
  if ((await count(kv, key)) >= cap) {
    capped(who.agent ? "AI assistants have made all the drawings we can make for them today."
      : "You've made all the drawings we can make for one person today.");
  }
  if (who.stub) return;
  const made = await count(globalStore(env), `stats:drawings:${who.day}`);
  if ((made + 1) * limits.costPerDrawing > limits.dollarsPerDay + 1e-9) {
    capped("We've made all the drawings we can today.");
  }
}

// After a drawing: the visitor's or agents' count, and (for a real one) the account's day and month.
async function counted(env, kv, who, what) {
  const [key] = poolKey(who);
  const jobs = [bump(kv, key, 1, 2 * DAY)];
  if (!who.stub) {
    const g = globalStore(env);
    jobs.push(bump(g, `stats:${what}:${who.day}`, 1, 40 * DAY), bump(g, `stats:${what}:${thisMonth()}`, 1, 400 * DAY));
  }
  await Promise.all(jobs);
}

// ---- the model -------------------------------------------------------------------------------

// One images edit: the product file's model, quality and size, the subject's brief, the photo, PNG out.
// A failed call uses no try and counts against no cap (docs/ORDERS.md, "Refusals").
async function draw(env, p, subject, photo, who, at) {
  if (who.stub) {
    const png = new Uint8Array(stubDrawing);
    return { png, b64: base64(png) };
  }
  if (!env.OPENAI_API_KEY) refuse(503, "We're not making drawings just now. Please come back later.", { off: true });
  const d = p.drawing;
  const body = new FormData();
  body.append('model', d.model);
  body.append('quality', d.quality);
  body.append('size', d.size);
  body.append('n', '1');
  body.append('prompt', subject.brief);
  body.append('user', who.user);
  body.append('image', new File([photo], 'photo.jpg', { type: 'image/jpeg' }));
  const t0 = Date.now();
  let res;
  let out;
  try {
    res = await fetch(OPENAI, { method: 'POST', headers: { Authorization: `Bearer ${env.OPENAI_API_KEY}` }, body });
    out = await res.json();
  } catch (err) {
    console.error(JSON.stringify({ drawing: at.id, n: at.n, error: String(err.message || err).slice(0, 200) }));
    refuse(502, "The drawing didn't come back. Please try again; that didn't use a try.");
  }
  const b64 = out?.data?.[0]?.b64_json;
  const log = {
    drawing: at.id, n: at.n, status: res.status, seconds: Math.round((Date.now() - t0) / 100) / 10,
    tokens: out?.usage ? { in: out.usage.input_tokens, out: out.usage.output_tokens } : null,
  };
  if (!res.ok || !b64) {
    // OpenAI's error type and code only: its message can quote the request.
    console.error(JSON.stringify({ ...log, error: out?.error?.type || null, code: out?.error?.code || null }));
    if (out?.error?.code === 'moderation_blocked') {
      refuse(422, "OpenAI wouldn't draw that photo. Please try a different one.", { moderation: true });
    }
    refuse(502, "The drawing didn't come back. Please try again; that didn't use a try.");
  }
  const png = unbase64(b64);
  if (!MAGIC.png.every((b, i) => png[i] === b)) {
    console.error(JSON.stringify({ ...log, error: 'not a PNG' }));
    refuse(502, "The drawing didn't come back. Please try again; that didn't use a try.");
  }
  console.log(JSON.stringify(log));
  return { png, b64 };
}

function base64(bytes) {
  let s = '';
  for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(s);
}

function unbase64(b64) {
  const s = atob(b64);
  const out = new Uint8Array(s.length);
  for (let i = 0; i < s.length; i++) out[i] = s.charCodeAt(i);
  return out;
}

// ---- image headers, without decoding ---------------------------------------------------------

export function jpegSize(b) {
  if (!(b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff)) return null;
  let i = 2;
  while (i + 9 < b.length) {
    if (b[i] !== 0xff) return null;
    const m = b[i + 1];
    if (m === 0xff) { i++; continue; }
    if (m === 0xd8 || (m >= 0xd0 && m <= 0xd7) || m === 0x01) { i += 2; continue; }
    const len = (b[i + 2] << 8) | b[i + 3];
    if (m >= 0xc0 && m <= 0xcf && m !== 0xc4 && m !== 0xc8 && m !== 0xcc) {
      return { height: (b[i + 5] << 8) | b[i + 6], width: (b[i + 7] << 8) | b[i + 8] };
    }
    if (m === 0xda || m === 0xd9) return null;
    i += 2 + len;
  }
  return null;
}

export function pngSize(b) {
  if (b.length < 24 || !MAGIC.png.every((x, i) => b[i] === x)) return null;
  if (String.fromCharCode(b[12], b[13], b[14], b[15]) !== 'IHDR') return null;
  const u32 = (o) => ((b[o] << 24) >>> 0) + (b[o + 1] << 16) + (b[o + 2] << 8) + b[o + 3];
  return { width: u32(16), height: u32(20) };
}

// For /api/stats.
export async function drawingStats(env, kv) {
  const g = globalStore(env);
  const day = today();
  const [d, m, uploads, agents] = await Promise.all([
    count(g, `stats:drawings:${day}`), count(g, `stats:drawings:${thisMonth()}`),
    count(kv, `stats:uploads:${day}`), count(kv, `count:${day}:agents`),
  ]);
  const usd = (n) => Math.round(n * limits.costPerDrawing * 100) / 100;
  return {
    drawings: { today: d, month: m, dollarsToday: usd(d), dollarsMonth: usd(m), agentsToday: agents, note: 'both modes; estimated at costPerDrawing' },
    uploads: { today: uploads },
    limits: Object.fromEntries(Object.entries(limits).filter(([k]) => !k.startsWith('_'))),
  };
}
