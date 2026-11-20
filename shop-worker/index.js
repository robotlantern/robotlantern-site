// The shop's order Worker (docs/SHOP.md, docs/ORDERS.md, docs/PRODUCTION.md).
//
// POST /stripe: Stripe's webhook for completed Checkout Sessions. After checking Stripe's
// signature, it marks a photo order paid (markPaid, below), then reads the session's line items.
// Printed items (fulfillment "gelato") become one Gelato order with the Checkout Session ID as its
// orderReferenceId; it searches for that ID first, so Stripe's retries never place an order twice.
// Self-shipped and Slant items need nothing there.
//
// Gelato orders are always created as drafts. RJ confirms each one in the Gelato dashboard, which
// is when Gelato charges. Turning that off is a code change, on RJ's say-so (docs/CHARGES.md).
//
// /api/: photo products. A product made from a drawing (the stencil ornament) has drawings
// (drawings.js) and orders of several designs (designs.js); older photo products send photos with
// design.json (below). Files stream straight into Workers KV. The Worker prices each order from the
// product files bundled into it (catalog.json, built from products/*/shop.json by
// tools/orders/catalog.py) and opens a Stripe Checkout Session for it. Unpaid orders and drawings
// expire from KV after two days; paid ones stay until the purge (designs.js).
//
// The host sets the mode: robotlantern.com/api/ is live, shop.robotlantern.workers.dev/api/ is
// Stripe's sandbox with its own KV namespace. The queue's token sets it for the queue's endpoints.
// Logs carry IDs and notes, never what's in an order (the privacy page promises it).

import catalog from './catalog.json';
import { drawings } from './drawings.js';
import {
  addWrites, checkDesignFiles, contact, createDesigns, designFile, designLines, designSummary, paidDesigns,
  patchOrder, proof, proofLinks, purgeDesigns, purgeDue, putOut, putPreview, queueList, slantDraft, stats,
} from './designs.js';
import {
  ID, LIVE_HOSTS, MAGIC, MiB, Refusal, UNPAID_SECONDS, bodyLength, cents, checkOpen, counting, json, newId,
  nextMonday, product, putRecord, refuse, startsWith, store, stripe, stripeKey, switchedOff, tokenMode, week,
  weekOrders,
} from './lib.js';

const ORDER_TYPE = 'draft';
const TOLERANCE_SECONDS = 300;

const SITE = { test: 'https://site.robotlantern.workers.dev', live: 'https://robotlantern.com' };
// Pages allowed to call the sandbox API from another origin: the preview hosts and dev servers.
const ORIGINS = ['https://site.robotlantern.workers.dev', 'https://rl.rblt.io'];
const DEV_ORIGIN = /^http:\/\/(localhost|127\.0\.0\.1|[a-z0-9-]+\.lan)(:\d+)?$/;

const DESIGN_BYTES = 64 * 1024;
const KINDS = {
  photo: { ext: 'jpg', max: 12 * MiB },
  mask: { ext: 'png', max: 6 * MiB },
  preview: { ext: 'jpg', max: 3 * MiB },
};
const TYPES = { jpg: 'image/jpeg', png: 'image/png' };

export default {
  async fetch(request, rawEnv, ctx) {
    const io = { writes: 0 };
    const env = counting(rawEnv, io);
    const url = new URL(request.url);
    try {
      if (url.pathname === '/stripe' && request.method === 'POST') return await webhook(request, env);
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
    } finally {
      if (io.writes) ctx.waitUntil(addWrites(rawEnv, io.writes));
    }
  },

  // Daily: the purge that's due, in both modes (decision 6, as amended by 28).
  async scheduled(event, rawEnv, ctx) {
    const io = { writes: 0 };
    const env = counting(rawEnv, io);
    for (const mode of ['test', 'live']) {
      const kv = mode === 'live' ? env.ORDERS_LIVE : env.ORDERS_TEST;
      if (!kv) continue;
      const done = await purgeDue(kv, false);
      if (done.length) console.log(JSON.stringify({ cron: 'purge', mode, done }));
    }
    if (io.writes) ctx.waitUntil(addWrites(rawEnv, io.writes));
  },
};

// ---- routes ------------------------------------------------------------------------------------

async function api(request, env, url) {
  const [, area, id, part, ...rest] = url.pathname.split('/').filter(Boolean);
  const method = request.method;
  const mode = LIVE_HOSTS.includes(url.hostname) ? 'live' : 'test';

  if (area === 'products' && id && !part && method === 'GET') return capacity(request, env, mode, id);
  if (area === 'drawings' && !rest.length) return drawings(request, env, mode, id, part);
  if (area === 'proofs' && method === 'GET') return proof(env, url, [id, part, ...rest]);

  if (area === 'orders' && !id && method === 'POST') return create(request, env, mode);
  if (area === 'orders' && ID.test(id || '')) {
    if (part === 'checkout' && !rest.length && method === 'POST') return checkout(request, env, mode, id);
    if (method === 'PUT' && /^\d+$/.test(part || '') && rest.join('/') === 'preview.jpg') return putPreview(request, env, mode, id, part);
    if (method === 'PUT' && part && !rest.length) return upload(request, env, mode, id, part);
  } else if (area === 'orders' && id) {
    refuse(404, 'No such order');
  }

  // The queue's endpoints (tools/orders/, the routines): its token picks the mode.
  const queue = await tokenMode(request, env);
  if (!queue) refuse(401, 'Not allowed');
  const kv = store(env, queue);
  if (area === 'queue' && !id && method === 'GET') return queueList(kv);
  if (area === 'stats' && !id && method === 'GET') {
    return stats(env, queue, kv, Object.entries(catalog).filter(([, p]) => p.drawing && !(queue === 'live' && p.fixture)));
  }
  if (area === 'purge' && !id && method === 'POST') {
    return json({ mode: queue, dryRun: url.searchParams.has('dry'), due: await purgeDue(kv, url.searchParams.has('dry')) });
  }
  if (area !== 'orders' || !id) refuse(404, 'Not found');

  const rec = await kv.get(`order:${id}`, 'json');
  if (!rec) refuse(404, 'No such order');
  const designs = rec.kind === 'designs';
  if (!part && method === 'GET') return json(rec);
  if (!part && method === 'DELETE') {
    return designs ? purgeDesigns(kv, rec, url.searchParams.get('keep') === 'evidence') : purge(kv, id, rec);
  }
  if (!designs) {
    if (part && !rest.length && method === 'GET') return download(kv, rec, part);
    refuse(404, 'Not found');
  }
  if (!part && method === 'PATCH') return patchOrder(request, kv, rec);
  if (part === 'slant' && !rest.length && method === 'POST') return slantDraft(request, env, queue, kv, rec);
  if (part === 'contact' && !rest.length && method === 'GET') return contact(env, queue, rec);
  if (part === 'link' && rest.join('/') === 'proof.png' && method === 'GET') return proofLinks(env, queue, rec, url.origin);
  if (/^\d+$/.test(part || '') && rest.length) {
    const name = rest.join('/');
    if (method === 'GET') return designFile(kv, rec, part, name);
    if (method === 'PUT' && rest[0] === 'out' && rest.length === 2) return putOut(request, kv, rec, part, rest[1]);
  }
  refuse(404, 'Not found');
}

// GET /api/products/<slug>: whether the product takes orders this week, and what's switched off, for the
// product page. Products made from drawings also show their price tiers.
async function capacity(request, env, mode, slug) {
  const p = product(slug, mode);
  const kv = store(env, mode);
  const w = week();
  const [orders, drawingsOff, ordersOff] = await Promise.all([
    weekOrders(kv, slug, w), switchedOff(kv, 'drawings'), switchedOff(kv, 'orders'),
  ]);
  const open = orders.length < p.weeklyCap && !ordersOff;
  const body = { product: slug, mode, open, reopens: orders.length < p.weeklyCap ? null : nextMonday() };
  if (p.drawing) Object.assign(body, { pricing: p.pricing, drawings: !drawingsOff, orders: !ordersOff, shipping: p.shipping });
  else Object.assign(body, { price: p.price, shipping: p.shipping });
  if ((await tokenMode(request, env)) === mode) Object.assign(body, { week: w, count: orders.length, cap: p.weeklyCap });
  return json(body);
}

// POST /api/orders: an order of designs for a product made from drawings, or design.json for an older
// photo product. Either way the price comes from the product file.
async function create(request, env, mode) {
  if (!(request.headers.get('content-type') || '').startsWith('application/json')) {
    refuse(415, 'Send the order as application/json.');
  }
  bodyLength(request, DESIGN_BYTES);
  let design;
  try {
    design = JSON.parse(await request.text());
  } catch {
    refuse(400, "The order isn't JSON.");
  }
  if (!design || typeof design !== 'object' || Array.isArray(design)) refuse(400, 'The order must be an object.');
  const slug = design.product;
  const p = product(slug, mode);
  if (p.drawing) return createDesigns(env, mode, slug, p, design);

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

// PUT /api/orders/<id>/<file>: one file of an older photo product, its raw bytes streamed into KV.
async function upload(request, env, mode, id, name) {
  const kv = store(env, mode);
  const rec = await kv.get(`order:${id}`, 'json');
  if (!rec) refuse(404, 'No such order. Unpaid orders expire after two days.');
  if (!rec.files?.includes(name)) refuse(404, `This order doesn't take ${name}.`);
  if (rec.status !== 'open') refuse(409, 'This order has gone to checkout, so its files are fixed.');
  const kind = KINDS[name.split('-')[0].split('.')[0]];
  const type = TYPES[kind.ext];
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
  const designs = rec.kind === 'designs';
  if (designs && (await switchedOff(kv, 'orders'))) refuse(503, "We're not taking orders just now. Please come back later.", { off: true });
  const key = stripeKey(env, mode);
  if (rec.session) {
    // One open session per order, so it can't be paid twice. A new one replaces an expired one.
    const old = await stripe(key, `checkout/sessions/${rec.session}`);
    if (old.status === 'open') return json({ url: old.url });
    if (old.status === 'complete') refuse(409, 'This order is already paid.');
  }
  const p = product(rec.product, mode);
  await checkOpen(kv, rec.product, p);

  let missing = [];
  let wrong = [];
  if (designs) {
    ({ missing, wrong } = await checkDesignFiles(kv, rec));
  } else {
    for (const name of rec.files) {
      const { value } = await kv.getWithMetadata(`file:${id}/${name}`, { type: 'stream' });
      if (!value) missing.push(name);
      else if (!(await startsWith(value, MAGIC[name.split('.').pop()]))) wrong.push(name);
    }
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
  let lineItems;
  let summary;
  if (designs) {
    lineItems = designLines(p, rec, ids);
    summary = designSummary(p, rec);
  } else {
    rec.price = price(p, rec.options);
    rec.shipping = cents(p.shipping);
    summary = optionSummary(p, rec.options);
    lineItems = [{
      quantity: 1,
      price_data: { currency: 'usd', unit_amount: rec.price, tax_behavior: 'exclusive', product: ids.product },
    }];
  }
  const site = siteFor(request, mode);
  const count = designs ? rec.count : 1;
  const session = await stripe(key, 'checkout/sessions', {
    mode: 'payment',
    client_reference_id: id,
    metadata: { order: id, product: rec.product, ...(designs ? { designs: rec.designs.length, count } : { options: summary }) },
    line_items: lineItems,
    shipping_address_collection: { allowed_countries: ['US'] },
    shipping_options: [{ shipping_rate: ids.shippingRate }],
    automatic_tax: { enabled: true },
    expires_at: expires,
    success_url: `${site}/shop/thanks/?order=${id}`,
    cancel_url: `${site}/shop/${rec.product}/`,
    payment_intent_data: {
      description: designs ? `${p.name} × ${count}, order ${id}` : `${p.name}${summary ? ` (${summary})` : ''}, order ${id}`,
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

  if (rec.kind === 'designs') {
    await paidDesigns(kv, rec);
  } else {
    // KV can't change an expiry, so each file is written again without one.
    for (const name of rec.files) {
      const key = `file:${id}/${name}`;
      const { value, metadata } = await kv.getWithMetadata(key, { type: 'stream' });
      if (!value) throw new Error(`order ${id}: ${name} not found`);
      await kv.put(key, value, { metadata });
    }
  }
  const w = week();
  const orders = await weekOrders(kv, rec.product, w);
  if (!orders.includes(id)) {
    orders.push(id);
    await kv.put(`week:${rec.product}:${w}`, JSON.stringify(orders), { expirationTtl: 70 * 86400 });
  }
  const paid = new Date().toISOString();
  Object.assign(rec, {
    status: 'paid',
    session: session.id,
    paid,
    week: w,
    amountTotal: session.amount_total,
    expires: null,
  });
  if (rec.kind === 'designs') Object.assign(rec, { state: 'paid', history: [{ state: 'paid', when: paid, note: 'Stripe' }], dates: {} });
  await putRecord(kv, rec);
  return `order ${id} paid`;
}

// GET /api/orders/<id>/<file> (queue): one file of an older photo product, or design.json.
async function download(kv, rec, name) {
  const id = rec.id;
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

// DELETE /api/orders/<id> (queue), for an older photo product: the photos and everything else in KV,
// leaving a short-lived tombstone so a late webhook finds the order handled.
async function purge(kv, id, rec) {
  const names = rec?.files?.length
    ? rec.files
    : (await kv.list({ prefix: `file:${id}/` })).keys.map((k) => k.name.slice(`file:${id}/`.length));
  for (const name of names) await kv.delete(`file:${id}/${name}`);
  const tombstone = { id, status: 'purged', product: rec?.product, session: rec?.session, purged: new Date().toISOString() };
  await kv.put(`order:${id}`, JSON.stringify(tombstone), { expirationTtl: 90 * 86400, metadata: { product: rec?.product, status: 'purged' } });
  return json({ id, purged: names });
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

function corsHeaders(request, url) {
  const origin = request.headers.get('Origin');
  const allowed = origin && !LIVE_HOSTS.includes(url.hostname) && (ORIGINS.includes(origin) || DEV_ORIGIN.test(origin));
  if (!allowed) return { Vary: 'Origin' };
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-Subject, X-Source, X-Product',
    'Access-Control-Max-Age': '86400',
    Vary: 'Origin',
  };
}

function siteFor(request, mode) {
  if (mode === 'live') return SITE.live;
  const origin = request.headers.get('Origin');
  return origin && (ORIGINS.includes(origin) || DEV_ORIGIN.test(origin)) ? origin : SITE.test;
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

// Printed items go to Gelato as a draft. The Gelato key is needed only when there are some, so a photo
// order (Slant or self-shipped) never waits on one.
async function fulfil(session, livemode, env) {
  const stripeSecret = livemode ? env.STRIPE_SECRET_KEY_LIVE : env.STRIPE_SECRET_KEY_TEST;
  if (!stripeSecret) throw new Error(`no Stripe key for ${livemode ? 'live' : 'test'} mode`);

  const lines = await stripe(stripeSecret,
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
  const gelatoKey = livemode ? env.GELATO_API_KEY_LIVE : env.GELATO_API_KEY_TEST;
  if (!gelatoKey) throw new Error(`no Gelato key for ${livemode ? 'live' : 'test'} mode`);

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
