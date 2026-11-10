// The shop's order Worker (docs/SHOP.md, docs/ORDERS.md).
//
// POST /stripe: Stripe's webhook for completed Checkout Sessions. After checking Stripe's
// signature, it marks a photo order paid (markPaid, below), then reads the session's line items.
// Printed items (fulfillment "gelato") become one Gelato order with the Checkout Session ID as its
// orderReferenceId; it searches for that ID first, so Stripe's retries never place an order twice.
// Self-shipped items need nothing here: Stripe's payment email tells RJ.
//
// Gelato orders are always created as drafts. RJ confirms each one in the Gelato dashboard, which
// is when Gelato charges. Turning that off is a code change, on RJ's say-so (docs/CHARGES.md).
//
// /api/: photo orders (docs/ORDERS.md). The browser POSTs design.json, PUTs each file as a raw body
// that streams straight into Workers KV, then POSTs for checkout. On the free plan a request gets
// 10 ms of CPU, so nothing here parses a form or reads an image. The Worker prices each order from
// the product files bundled into it (catalog.json, built from products/*/shop.json by
// tools/orders/catalog.py) and opens a Stripe Checkout Session for it. Unpaid orders expire from KV
// after two days; the webhook keeps paid ones until tools/orders/queue.py purges them.
//
// The host sets the mode: robotlantern.com/api/ is live, shop.robotlantern.workers.dev/api/ is
// Stripe's sandbox with its own KV namespace. The queue's token sets it for the queue's endpoints.
// Logs carry IDs and notes, never what's in an order (the privacy page promises it).

import catalog from './catalog.json';

const ORDER_TYPE = 'draft';
const STRIPE_VERSION = '2026-08-26.dahlia';
const TOLERANCE_SECONDS = 300;

const LIVE_HOSTS = ['robotlantern.com', 'www.robotlantern.com'];
const SITE = { test: 'https://site.robotlantern.workers.dev', live: 'https://robotlantern.com' };
// Pages allowed to call the sandbox API from another origin: the preview hosts and dev servers.
const ORIGINS = ['https://site.robotlantern.workers.dev', 'https://rl.rblt.io'];
const DEV_ORIGIN = /^http:\/\/(localhost|127\.0\.0\.1|[a-z0-9-]+\.lan)(:\d+)?$/;

const UNPAID_SECONDS = 2 * 86400;
const DESIGN_BYTES = 32 * 1024;
const MiB = 2 ** 20;
const KINDS = {
  photo: { ext: 'jpg', max: 12 * MiB },
  mask: { ext: 'png', max: 6 * MiB },
  preview: { ext: 'jpg', max: 3 * MiB },
};
const TYPES = {
  jpg: { type: 'image/jpeg', magic: [0xff, 0xd8, 0xff] },
  png: { type: 'image/png', magic: [0x89, 0x50, 0x4e, 0x47] },
};
const ID_CHARS = '0123456789abcdefghjkmnpqrstvwxyz';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/stripe' && request.method === 'POST') return webhook(request, env);
    if (!url.pathname.startsWith('/api/')) return new Response('Not found', { status: 404 });

    const cors = corsHeaders(request, url);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    let res;
    try {
      res = await api(request, env, url);
    } catch (err) {
      if (err instanceof Refusal) {
        res = json({ error: err.message, ...err.extra }, err.status);
      } else {
        console.error(JSON.stringify({ path: url.pathname, error: String(err.message || err) }));
        res = json({ error: 'Something went wrong. Please try again.' }, 500);
      }
    }
    for (const [k, v] of Object.entries(cors)) res.headers.set(k, v);
    return res;
  },
};

// ---- Photo orders --------------------------------------------------------------------------

class Refusal extends Error {
  constructor(status, message, extra = {}) {
    super(message);
    this.status = status;
    this.extra = extra;
  }
}
function refuse(status, message, extra) {
  throw new Refusal(status, message, extra);
}

async function api(request, env, url) {
  const [, area, id, part, ...rest] = url.pathname.split('/').filter(Boolean);
  const method = request.method;
  const mode = LIVE_HOSTS.includes(url.hostname) ? 'live' : 'test';
  if (rest.length) refuse(404, 'Not found');

  if (area === 'products' && id && !part && method === 'GET') return capacity(request, env, mode, id);
  if (area !== 'orders') refuse(404, 'Not found');
  if (!id && method === 'POST') return create(request, env, mode);
  if (!/^[0-9a-z]{12}$/.test(id || '')) refuse(404, 'No such order');
  if (part === 'checkout' && method === 'POST') return checkout(request, env, mode, id);
  if (part && method === 'PUT') return upload(request, env, mode, id, part);

  // The queue's endpoints (tools/orders/queue.py): its token picks the mode.
  const queue = await tokenMode(request, env);
  if (!queue) refuse(401, 'Not allowed');
  const kv = store(env, queue);
  if (!part && method === 'GET') {
    const rec = await kv.get(`order:${id}`, 'json');
    return rec ? json(rec) : refuse(404, 'No such order');
  }
  if (!part && method === 'DELETE') return purge(kv, id);
  if (part && method === 'GET') return download(kv, id, part);
  refuse(404, 'Not found');
}

// GET /api/products/<slug>: whether the product takes orders this week, for the product page.
async function capacity(request, env, mode, slug) {
  const p = product(slug, mode);
  const kv = store(env, mode);
  const w = week();
  const orders = await weekOrders(kv, slug, w);
  const open = orders.length < p.weeklyCap;
  const body = { product: slug, mode, price: p.price, shipping: p.shipping, open, reopens: open ? null : nextMonday() };
  if ((await tokenMode(request, env)) === mode) Object.assign(body, { week: w, count: orders.length, cap: p.weeklyCap });
  return json(body);
}

// POST /api/orders, with design.json: checks the product and options, and starts an order.
async function create(request, env, mode) {
  if (!(request.headers.get('content-type') || '').startsWith('application/json')) {
    refuse(415, 'Send design.json as application/json.');
  }
  bodyLength(request, DESIGN_BYTES);
  let design;
  try {
    design = JSON.parse(await request.text());
  } catch {
    refuse(400, "design.json isn't JSON.");
  }
  if (!design || typeof design !== 'object' || Array.isArray(design)) refuse(400, 'design.json must be an object.');
  const slug = design.product;
  const p = product(slug, mode);
  const options = chosen(p, design.options);
  const kv = store(env, mode);
  await checkOpen(kv, slug, p);

  const now = Math.floor(Date.now() / 1000);
  const rec = {
    id: newId(),
    mode,
    product: slug,
    options,
    price: price(p, options),
    shipping: cents(p.shipping),
    // What the page showed, kept for the record. It never sets the price.
    shown: typeof design.price === 'number' ? cents(design.price) : null,
    files: expectedFiles(p),
    status: 'open',
    created: new Date(now * 1000).toISOString(),
    expires: now + UNPAID_SECONDS,
    design,
  };
  await putRecord(kv, rec);
  if (rec.shown !== null && rec.shown !== rec.price) console.log(JSON.stringify({ order: rec.id, note: 'shown price differs' }));
  return json({
    id: rec.id,
    mode,
    files: rec.files,
    price: rec.price / 100,
    shipping: rec.shipping / 100,
    expires: new Date(rec.expires * 1000).toISOString(),
  }, 201);
}

// PUT /api/orders/<id>/<file>: one file, its raw bytes streamed straight into KV.
async function upload(request, env, mode, id, name) {
  const kv = store(env, mode);
  const rec = await kv.get(`order:${id}`, 'json');
  if (!rec) refuse(404, 'No such order. Unpaid orders expire after two days.');
  if (!rec.files.includes(name)) refuse(404, `This order doesn't take ${name}.`);
  if (rec.status !== 'open') refuse(409, 'This order has gone to checkout, so its files are fixed.');
  const kind = KINDS[name.split('-')[0].split('.')[0]];
  const { type } = TYPES[kind.ext];
  if ((request.headers.get('content-type') || '').split(';')[0].trim() !== type) refuse(415, `Send ${name} as ${type}.`);
  const size = bodyLength(request, kind.max);
  if (rec.expires - Date.now() / 1000 < 3600) refuse(410, 'This order has nearly expired. Please start again.');
  await kv.put(`file:${id}/${name}`, request.body, { expiration: rec.expires, metadata: { size, type } });
  return json({ name, size }, 201);
}

// POST /api/orders/<id>/checkout: checks every file is there, and opens Stripe's checkout.
async function checkout(request, env, mode, id) {
  const kv = store(env, mode);
  const rec = await kv.get(`order:${id}`, 'json');
  if (!rec) refuse(404, 'No such order. Unpaid orders expire after two days.');
  if (rec.status !== 'open' && rec.status !== 'checkout') refuse(409, 'This order is already paid.');
  const key = stripeKey(env, mode);
  if (rec.session) {
    // One open session per order, so it can't be paid twice. A new one replaces an expired one.
    const old = await stripe(key, `checkout/sessions/${rec.session}`);
    if (old.status === 'open') return json({ url: old.url });
    if (old.status === 'complete') refuse(409, 'This order is already paid.');
  }
  const p = product(rec.product, mode);
  await checkOpen(kv, rec.product, p);

  const missing = [];
  const wrong = [];
  for (const name of rec.files) {
    const { value } = await kv.getWithMetadata(`file:${id}/${name}`, { type: 'stream' });
    if (!value) missing.push(name);
    else if (!(await startsWith(value, TYPES[name.split('.').pop()].magic))) wrong.push(name);
  }
  // KV caches a miss for up to a minute, so a file sent after a refusal here can take that long to
  // show. The page sends any missing file again and retries (docs/ORDERS.md).
  if (missing.length) refuse(409, `Still waiting for ${missing.join(', ')}. Try again in a minute.`, { missing });
  if (wrong.length) refuse(415, `Not a JPEG or PNG: ${wrong.join(', ')}.`, { wrong });

  const ids = p.stripe?.[mode] || {};
  if (!ids.product || !ids.shippingRate) refuse(503, `${p.name} isn't set up in Stripe yet.`);
  const now = Math.floor(Date.now() / 1000);
  const expires = Math.min(now + 86400 - 60, rec.expires - 15 * 60);
  if (expires < now + 31 * 60) refuse(410, 'This order has nearly expired. Please start again.');

  // The price comes from the product file bundled here, never from the browser.
  rec.price = price(p, rec.options);
  rec.shipping = cents(p.shipping);
  const summary = optionSummary(p, rec.options);
  const site = siteFor(request, mode);
  const session = await stripe(key, 'checkout/sessions', {
    mode: 'payment',
    client_reference_id: id,
    metadata: { order: id, product: rec.product, options: summary },
    line_items: [{
      quantity: 1,
      price_data: { currency: 'usd', unit_amount: rec.price, tax_behavior: 'exclusive', product: ids.product },
    }],
    shipping_address_collection: { allowed_countries: ['US'] },
    shipping_options: [{ shipping_rate: ids.shippingRate }],
    automatic_tax: { enabled: true },
    expires_at: expires,
    success_url: `${site}/shop/thanks/?order=${id}`,
    cancel_url: `${site}/shop/${rec.product}/`,
    payment_intent_data: {
      description: `${p.name}${summary ? ` (${summary})` : ''}, order ${id}`,
      metadata: { order: id },
    },
    custom_text: summary ? { submit: { message: summary } } : undefined,
  });
  Object.assign(rec, { status: 'checkout', session: session.id });
  await putRecord(kv, rec);
  return json({ url: session.url });
}

// The webhook's paid step: keep the files with no expiry, count the order in its week, mark it
// paid. A resent event finds it paid and changes nothing.
async function markPaid(session, livemode, env) {
  const mode = livemode ? 'live' : 'test';
  const kv = store(env, mode);
  const id = session.metadata.order;
  const rec = await kv.get(`order:${id}`, 'json');
  // Missing can mean KV hasn't reached this location yet: a 500 makes Stripe try again later.
  if (!rec) throw new Error(`order ${id} not found`);
  if (rec.status === 'paid' || rec.status === 'purged') return `order ${id} already ${rec.status}`;

  // KV can't change an expiry, so each file is written again without one.
  for (const name of rec.files) {
    const key = `file:${id}/${name}`;
    const { value, metadata } = await kv.getWithMetadata(key, { type: 'stream' });
    if (!value) throw new Error(`order ${id}: ${name} not found`);
    await kv.put(key, value, { metadata });
  }
  const w = week();
  const orders = await weekOrders(kv, rec.product, w);
  if (!orders.includes(id)) {
    orders.push(id);
    await kv.put(`week:${rec.product}:${w}`, JSON.stringify(orders), { expirationTtl: 70 * 86400 });
  }
  Object.assign(rec, {
    status: 'paid',
    session: session.id,
    paid: new Date().toISOString(),
    week: w,
    amountTotal: session.amount_total,
    expires: null,
  });
  await putRecord(kv, rec);
  return `order ${id} paid`;
}

// GET /api/orders/<id>/<file> (queue): one file, or design.json.
async function download(kv, id, name) {
  const rec = await kv.get(`order:${id}`, 'json');
  if (!rec) refuse(404, 'No such order');
  if (name === 'design.json') {
    if (!rec.design) refuse(410, 'Purged');
    return json(rec.design);
  }
  if (!(rec.files || []).includes(name)) refuse(404, `No ${name} in this order`);
  const { value, metadata } = await kv.getWithMetadata(`file:${id}/${name}`, { type: 'stream' });
  if (!value) refuse(404, `${name} is gone`);
  return new Response(value, {
    headers: { 'content-type': metadata?.type || 'application/octet-stream', 'x-file-size': String(metadata?.size ?? '') },
  });
}

// DELETE /api/orders/<id> (queue): the photos and everything else in KV, leaving a short-lived
// tombstone so a late webhook finds the order handled.
async function purge(kv, id) {
  const rec = await kv.get(`order:${id}`, 'json');
  const names = rec?.files?.length
    ? rec.files
    : (await kv.list({ prefix: `file:${id}/` })).keys.map((k) => k.name.slice(`file:${id}/`.length));
  for (const name of names) await kv.delete(`file:${id}/${name}`);
  const tombstone = { id, status: 'purged', product: rec?.product, session: rec?.session, purged: new Date().toISOString() };
  await kv.put(`order:${id}`, JSON.stringify(tombstone), { expirationTtl: 90 * 86400 });
  return json({ id, purged: names });
}

function product(slug, mode) {
  const p = typeof slug === 'string' && Object.hasOwn(catalog, slug) ? catalog[slug] : null;
  if (!p || (mode === 'live' && p.fixture)) refuse(404, 'No such product.');
  if (mode === 'live' && (!p.listed || p.provisional)) refuse(409, "This one isn't on sale yet.");
  return p;
}

function chosen(p, sent) {
  const given = sent && typeof sent === 'object' && !Array.isArray(sent) ? sent : {};
  const out = {};
  for (const o of p.options) {
    const c = o.choices.find((c) => c.id === given[o.id]);
    if (!c) refuse(400, `Choose a ${o.label.toLowerCase()}.`, { option: o.id });
    out[o.id] = c.id;
  }
  for (const k of Object.keys(given)) if (!Object.hasOwn(out, k)) refuse(400, `There's no option ${k}.`);
  return out;
}

function price(p, options) {
  const add = p.options.reduce((sum, o) => sum + o.choices.find((c) => c.id === options[o.id]).add, 0);
  return cents(p.price + add);
}

function optionSummary(p, options) {
  return p.options.map((o) => `${o.label}: ${o.choices.find((c) => c.id === options[o.id]).label}`).join(', ');
}

function expectedFiles(p) {
  const n = p.photo.count;
  const photos = Array.from({ length: n }, (_, i) => `photo-${i + 1}.jpg`);
  const masks = p.photo.subject ? Array.from({ length: n }, (_, i) => `mask-${i + 1}.png`) : [];
  return [...photos, ...masks, 'preview.jpg'];
}

async function checkOpen(kv, slug, p) {
  const orders = await weekOrders(kv, slug, week());
  if (orders.length >= p.weeklyCap) {
    const reopens = nextMonday();
    refuse(409, `This week's orders are full. Ordering reopens on ${reopens}.`, { full: true, reopens });
  }
}

async function weekOrders(kv, slug, w) {
  return (await kv.get(`week:${slug}:${w}`, 'json')) || [];
}

// ISO 8601 week, in UTC: weeks start on Monday.
function week(date = new Date()) {
  const d = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
  d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
  const year = d.getUTCFullYear();
  const n = Math.ceil(((d - Date.UTC(year, 0, 1)) / 86400000 + 1) / 7);
  return `${year}-W${String(n).padStart(2, '0')}`;
}

function nextMonday(date = new Date()) {
  const d = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
  d.setUTCDate(d.getUTCDate() + 8 - (d.getUTCDay() || 7));
  return d.toISOString().slice(0, 10);
}

function store(env, mode) {
  const kv = mode === 'live' ? env.ORDERS_LIVE : env.ORDERS_TEST;
  if (!kv) refuse(503, "Photo orders aren't open yet.");
  return kv;
}

function stripeKey(env, mode) {
  const key = mode === 'live' ? env.STRIPE_SECRET_KEY_LIVE : env.STRIPE_SECRET_KEY_TEST;
  // The sandbox must never reach a live key.
  if (!key || (mode === 'test' && !/^(sk|rk)_test_/.test(key))) refuse(503, "Checkout isn't open yet.");
  return key;
}

async function putRecord(kv, rec) {
  const opts = rec.expires ? { expiration: rec.expires } : {};
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

function bodyLength(request, max) {
  const n = Number(request.headers.get('content-length'));
  if (!request.headers.has('content-length') || !Number.isInteger(n)) refuse(411, 'Send a Content-Length.');
  if (n === 0) refuse(400, 'Nothing was sent.');
  if (n > max) refuse(413, `That's too big: at most ${max >= MiB ? `${max / MiB} MB` : `${max / 1024} KB`}.`);
  return n;
}

async function startsWith(stream, magic) {
  const reader = stream.getReader();
  let head = new Uint8Array(0);
  try {
    while (head.length < magic.length) {
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
  return magic.every((b, i) => head[i] === b);
}

async function tokenMode(request, env) {
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

function corsHeaders(request, url) {
  const origin = request.headers.get('Origin');
  const allowed = origin && !LIVE_HOSTS.includes(url.hostname) && (ORIGINS.includes(origin) || DEV_ORIGIN.test(origin));
  if (!allowed) return { Vary: 'Origin' };
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    Vary: 'Origin',
  };
}

function siteFor(request, mode) {
  if (mode === 'live') return SITE.live;
  const origin = request.headers.get('Origin');
  return origin && (ORIGINS.includes(origin) || DEV_ORIGIN.test(origin)) ? origin : SITE.test;
}

function newId() {
  return [...crypto.getRandomValues(new Uint8Array(12))].map((b) => ID_CHARS[b & 31]).join('');
}

function cents(dollars) {
  return Math.round(dollars * 100);
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });
}

// ---- Stripe's webhook ----------------------------------------------------------------------

async function webhook(request, env) {
  const body = await request.text();
  const secrets = [env.STRIPE_WEBHOOK_SECRET_TEST, env.STRIPE_WEBHOOK_SECRET_LIVE].filter(Boolean);
  if (!(await verified(body, request.headers.get('stripe-signature'), secrets))) {
    return new Response('Bad signature', { status: 400 });
  }
  const event = JSON.parse(body);
  const session = event.data.object;
  const done = (note) => {
    console.log(JSON.stringify({ event: event.id, session: session.id, livemode: event.livemode, note }));
    return new Response(note);
  };
  if (!['checkout.session.completed', 'checkout.session.async_payment_succeeded'].includes(event.type)) {
    return done(`ignored ${event.type}`);
  }
  if (session.payment_status !== 'paid') return done('not paid yet');

  try {
    const notes = [];
    if (session.metadata?.order) notes.push(await markPaid(session, event.livemode, env));
    notes.push(await fulfil(session, event.livemode, env));
    return done(notes.join('; '));
  } catch (err) {
    // A 500 makes Stripe retry, for up to three days, and shows the failure in its dashboard.
    const error = err instanceof Refusal ? err.message : String(err.message || err);
    console.error(JSON.stringify({ event: event.id, session: session.id, error }));
    return new Response('Order failed; Stripe will retry', { status: 500 });
  }
}

async function fulfil(session, livemode, env) {
  const stripeKey = livemode ? env.STRIPE_SECRET_KEY_LIVE : env.STRIPE_SECRET_KEY_TEST;
  const gelatoKey = livemode ? env.GELATO_API_KEY_LIVE : env.GELATO_API_KEY_TEST;
  if (!stripeKey || !gelatoKey) throw new Error(`no keys for ${livemode ? 'live' : 'test'} mode`);

  const lines = await stripe(stripeKey,
    `checkout/sessions/${session.id}/line_items?limit=100&expand[]=data.price.product`);
  const choices = Object.fromEntries((session.custom_fields || [])
    .map((f) => [f.key, f.dropdown?.value]));

  const items = [];
  for (const line of lines.data) {
    const md = line.price.product.metadata || {};
    if (md.fulfillment !== 'gelato') continue;
    const productUid = md.option ? md[`uid_${choices[md.option]}`] : md.uid;
    if (!productUid) throw new Error(`no Gelato product for ${md.slug} (${md.option}: ${choices[md.option]})`);
    const files = Object.entries(md)
      .filter(([k]) => k.startsWith('file_'))
      .map(([k, url]) => ({ type: k.slice(5), url }));
    items.push({ itemReferenceId: line.id, productUid, files, quantity: line.quantity });
  }
  if (!items.length) return 'nothing for Gelato';

  const found = await gelato(gelatoKey, 'orders:search', { orderReferenceId: session.id, limit: 1 });
  if (found.orders?.length) return `Gelato order exists: ${found.orders[0].id}`;

  const ship = session.collected_information?.shipping_details || session.shipping_details;
  if (!ship?.address) throw new Error('no shipping address on the session');
  const name = ship.name.trim();
  const cut = name.lastIndexOf(' ');
  const a = ship.address;
  const order = await gelato(gelatoKey, 'orders', {
    orderType: ORDER_TYPE,
    orderReferenceId: session.id,
    customerReferenceId: session.customer || session.customer_details.email,
    currency: 'USD',
    items,
    shippingAddress: {
      firstName: (cut > 0 ? name.slice(0, cut) : name).slice(0, 25),
      lastName: (cut > 0 ? name.slice(cut + 1) : '-').slice(0, 25),
      addressLine1: a.line1,
      addressLine2: a.line2 || undefined,
      city: a.city,
      postCode: a.postal_code,
      state: a.state,
      country: a.country,
      email: session.customer_details.email,
      phone: session.customer_details.phone || undefined,
    },
    metadata: [{ key: 'stripeMode', value: livemode ? 'live' : 'test' }],
  });
  return `Gelato ${ORDER_TYPE} ${order.id}`;
}

// GET without a body; POST with one, in Stripe's nested form encoding.
async function stripe(key, path, body) {
  const res = await fetch(`https://api.stripe.com/v1/${path}`, {
    method: body ? 'POST' : 'GET',
    headers: {
      Authorization: `Bearer ${key}`,
      'Stripe-Version': STRIPE_VERSION,
      ...(body && { 'Content-Type': 'application/x-www-form-urlencoded' }),
    },
    body: body ? new URLSearchParams(form(body)) : undefined,
  });
  const json = await res.json();
  if (!res.ok) throw new Error(`Stripe ${res.status}: ${json.error?.message}`);
  return json;
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

async function gelato(key, path, body) {
  const res = await fetch(`https://order.gelatoapis.com/v4/${path}`, {
    method: 'POST',
    headers: { 'X-API-KEY': key, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  if (!res.ok) throw new Error(`Gelato ${path} ${res.status}: ${text.slice(0, 500)}`);
  return JSON.parse(text);
}

// Stripe-Signature: t=<unix time>,v1=<hex HMAC-SHA256 of "<t>.<body>">[,v1=...]
async function verified(body, header, secrets) {
  if (!header) return false;
  const parts = header.split(',').map((p) => p.split('='));
  const t = parts.find(([k]) => k === 't')?.[1];
  const sigs = parts.filter(([k]) => k === 'v1').map(([, v]) => v);
  if (!t || !sigs.length || Math.abs(Date.now() / 1000 - Number(t)) > TOLERANCE_SECONDS) return false;
  const enc = new TextEncoder();
  for (const secret of secrets) {
    const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
    const mac = new Uint8Array(await crypto.subtle.sign('HMAC', key, enc.encode(`${t}.${body}`)));
    const hex = [...mac].map((b) => b.toString(16).padStart(2, '0')).join('');
    if (sigs.some((s) => s.length === hex.length && crypto.subtle.timingSafeEqual(enc.encode(s), enc.encode(hex)))) {
      return true;
    }
  }
  return false;
}
