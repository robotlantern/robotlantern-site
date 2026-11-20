// What the shop Worker's modules share: refusals, KV access, IDs, dates, tokens and the catalog.

import catalog from './catalog.json';

export const MiB = 2 ** 20;
export const DAY = 86400;
export const UNPAID_SECONDS = 2 * DAY;
const ID_CHARS = '0123456789abcdefghjkmnpqrstvwxyz';
export const ID = /^[0-9a-z]{12}$/;
export const LIVE_HOSTS = ['robotlantern.com', 'www.robotlantern.com'];

export class Refusal extends Error {
  constructor(status, message, extra = {}) {
    super(message);
    this.status = status;
    this.extra = extra;
  }
}
export function refuse(status, message, extra) {
  throw new Refusal(status, message, extra);
}

export function json(body, status = 200, headers = {}) {
  return new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', ...headers } });
}

export function cents(dollars) {
  return Math.round(dollars * 100);
}

export function newId() {
  return [...crypto.getRandomValues(new Uint8Array(12))].map((b) => ID_CHARS[b & 31]).join('');
}

export function now() {
  return Math.floor(Date.now() / 1000);
}

export function iso(seconds = now()) {
  return new Date(seconds * 1000).toISOString();
}

// UTC day and month, the caps' and counters' periods.
export function today(date = new Date()) {
  return date.toISOString().slice(0, 10);
}
export function thisMonth(date = new Date()) {
  return date.toISOString().slice(0, 7);
}
export function secondsToMidnight(date = new Date()) {
  const next = Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate() + 1);
  return Math.ceil((next - date.getTime()) / 1000);
}

// ISO 8601 week, in UTC: weeks start on Monday.
export function week(date = new Date()) {
  const d = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
  d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
  const year = d.getUTCFullYear();
  const n = Math.ceil(((d - Date.UTC(year, 0, 1)) / 86400000 + 1) / 7);
  return `${year}-W${String(n).padStart(2, '0')}`;
}

export function nextMonday(date = new Date()) {
  const d = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
  d.setUTCDate(d.getUTCDate() + 8 - (d.getUTCDay() || 7));
  return d.toISOString().slice(0, 10);
}

// ---- KV ------------------------------------------------------------------------------------

// Each request gets its own view of the bindings that counts KV writes, for /api/stats (docs/ORDERS.md,
// "Caps"). The count is added to the day's total once the response has gone.
export function counting(env, io) {
  const wrap = (kv) => kv && {
    get: (...a) => kv.get(...a),
    getWithMetadata: (...a) => kv.getWithMetadata(...a),
    list: (...a) => kv.list(...a),
    put: (...a) => { io.writes++; return kv.put(...a); },
    delete: (...a) => { io.writes++; return kv.delete(...a); },
  };
  return { ...env, ORDERS_TEST: wrap(env.ORDERS_TEST), ORDERS_LIVE: wrap(env.ORDERS_LIVE) };
}

export function store(env, mode) {
  const kv = mode === 'live' ? env.ORDERS_LIVE : env.ORDERS_TEST;
  if (!kv) refuse(503, "Photo orders aren't open yet.");
  return kv;
}

// Counters that cover the whole account, whichever mode spent it: OpenAI drawings (one key, one
// balance) and KV writes (an account's limit). They live in the live namespace when it's bound.
export function globalStore(env) {
  return env.ORDERS_LIVE || env.ORDERS_TEST;
}

export async function count(kv, key) {
  return Number(await kv.get(key)) || 0;
}

// KV counters are read-then-write, so a burst can overshoot by a few (docs/ORDERS.md, "Caps").
export async function bump(kv, key, by = 1, ttl = 3 * DAY) {
  const n = (await count(kv, key)) + by;
  await kv.put(key, String(n), { expirationTtl: ttl });
  return n;
}

export async function putRecord(kv, rec) {
  const opts = { metadata: listing(rec) };
  if (rec.expires) opts.expiration = rec.expires;
  else if (rec.keepUntil) opts.expiration = rec.keepUntil;
  for (let attempt = 0; ; attempt++) {
    try {
      return await kv.put(`order:${rec.id}`, JSON.stringify(rec), opts);
    } catch (err) {
      // KV takes one write a second per key.
      if (attempt || !/429|too many/i.test(String(err))) throw err;
      await new Promise((r) => setTimeout(r, 1100));
    }
  }
}

// What a listing of order: keys shows without reading each record (the queue and the purge).
function listing(rec) {
  return {
    product: rec.product,
    status: rec.status,
    state: rec.state || null,
    paid: rec.paid || null,
    shipped: rec.dates?.shipped || null,
    cancelled: rec.dates?.cancelled || null,
    purged: rec.purged || null,
  };
}

export async function listOrders(kv) {
  const out = [];
  let cursor;
  do {
    const page = await kv.list({ prefix: 'order:', cursor });
    for (const k of page.keys) out.push({ id: k.name.slice(6), ...(k.metadata || {}) });
    cursor = page.list_complete ? null : page.cursor;
  } while (cursor);
  return out;
}

export async function headOf(stream, n) {
  const reader = stream.getReader();
  let head = new Uint8Array(0);
  try {
    while (head.length < n) {
      const { value, done } = await reader.read();
      if (done) break;
      const next = new Uint8Array(head.length + value.length);
      next.set(head);
      next.set(value, head.length);
      head = next;
    }
  } finally {
    await reader.cancel().catch(() => {});
  }
  return head;
}

export async function startsWith(stream, magic) {
  const head = await headOf(stream, magic.length);
  return magic.every((b, i) => head[i] === b);
}

export const MAGIC = {
  jpg: [0xff, 0xd8, 0xff],
  png: [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a],
};

export function bodyLength(request, max) {
  const n = Number(request.headers.get('content-length'));
  if (!request.headers.has('content-length') || !Number.isInteger(n)) refuse(411, 'Send a Content-Length.');
  if (n === 0) refuse(400, 'Nothing was sent.');
  if (n > max) refuse(413, `That's too big: at most ${max >= MiB ? `${max / MiB} MB` : `${max / 1024} KB`}.`);
  return n;
}

// ---- tokens and signatures -----------------------------------------------------------------

// The queue's token sets the mode for the queue's endpoints.
export async function tokenMode(request, env) {
  const auth = request.headers.get('authorization') || '';
  if (!auth.startsWith('Bearer ')) return null;
  for (const [mode, token] of [['test', env.QUEUE_TOKEN_TEST], ['live', env.QUEUE_TOKEN_LIVE]]) {
    if (token && (await same(auth.slice(7), token))) return mode;
  }
  return null;
}

async function same(a, b) {
  const enc = new TextEncoder();
  const [x, y] = await Promise.all([a, b].map((s) => crypto.subtle.digest('SHA-256', enc.encode(s))));
  return crypto.subtle.timingSafeEqual(x, y);
}

export async function hmacHex(secret, message) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return hex(await crypto.subtle.sign('HMAC', key, enc.encode(message)));
}

export function hex(buf) {
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

export function safeEqual(a, b) {
  const enc = new TextEncoder();
  const x = enc.encode(a);
  const y = enc.encode(b);
  return x.length === y.length && crypto.subtle.timingSafeEqual(x, y);
}

// ---- the catalog ---------------------------------------------------------------------------

export function product(slug, mode) {
  const p = typeof slug === 'string' && Object.hasOwn(catalog, slug) ? catalog[slug] : null;
  if (!p || (mode === 'live' && p.fixture)) refuse(404, 'No such product.');
  if (mode === 'live' && (!p.listed || p.provisional)) refuse(409, "This one isn't on sale yet.");
  return p;
}

// The product a drawing is for: X-Product, or the one product that makes drawings.
export function drawingProduct(request, mode) {
  const named = request.headers.get('x-product');
  if (named) {
    const p = product(named, mode);
    if (!p.drawing) refuse(400, `${p.name} isn't made from a drawing.`);
    return [named, p];
  }
  const slugs = Object.keys(catalog).filter((s) => catalog[s].drawing && !catalog[s].fixture);
  if (slugs.length !== 1) refuse(400, 'Say which product with X-Product.');
  return [slugs[0], product(slugs[0], mode)];
}

export async function switchedOff(kv, what) {
  return (await kv.get(`switch:${what}`)) === 'off';
}

export async function weekOrders(kv, slug, w) {
  return (await kv.get(`week:${slug}:${w}`, 'json')) || [];
}

export async function checkOpen(kv, slug, p) {
  const orders = await weekOrders(kv, slug, week());
  if (orders.length >= p.weeklyCap) {
    const reopens = nextMonday();
    refuse(409, `This week's orders are full. Ordering reopens on ${reopens}.`, { full: true, reopens });
  }
}

export function stripeKey(env, mode) {
  const key = mode === 'live' ? env.STRIPE_SECRET_KEY_LIVE : env.STRIPE_SECRET_KEY_TEST;
  // The sandbox must never reach a live key.
  if (!key || (mode === 'test' && !/^(sk|rk)_test_/.test(key))) refuse(503, "Checkout isn't open yet.");
  return key;
}

const STRIPE_VERSION = '2026-08-26.dahlia';

// GET without a body; POST with one, in Stripe's nested form encoding.
export async function stripe(key, path, body) {
  const res = await fetch(`https://api.stripe.com/v1/${path}`, {
    method: body ? 'POST' : 'GET',
    headers: {
      Authorization: `Bearer ${key}`,
      'Stripe-Version': STRIPE_VERSION,
      ...(body && { 'Content-Type': 'application/x-www-form-urlencoded' }),
    },
    body: body ? new URLSearchParams(form(body)) : undefined,
  });
  const out = await res.json();
  if (!res.ok) throw new Error(`Stripe ${res.status}: ${out.error?.message}`);
  return out;
}

function form(data, prefix = '', out = []) {
  for (const [k, v] of Object.entries(data)) {
    const key = prefix ? `${prefix}[${k}]` : k;
    if (v === undefined || v === null) continue;
    if (typeof v === 'object') form(v, key, out);
    else out.push([key, String(v)]);
  }
  return out;
}
