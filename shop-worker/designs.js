// Orders of designs (docs/ORDERS.md, "Orders"): a product made from drawings, where one order holds several
// designs, each with a quantity (decision 26). A design points to a made or uploaded drawing, or names a
// ready-made one (decision 30). Options, the text rule and prices all come from the product file, and no
// option is named in code (decision 29).
//
// Also the routine's queue endpoints for these orders, signed proof links, Slant drafts (which only ever
// dry-run in the sandbox), /api/stats and the purge on schedule (decision 6, as amended by 28).
//
// KV: order:<id> is the record (never the address or email: those stay in Stripe). Design k's files are
// file:<id>/<k>/preview.jpg (from the page), then, once paid, design.json, photo.jpg, drawing.png, and the
// routine's out/ files.

import limits from './limits.json';
import { drawingStats } from './drawings.js';
import { tagFit } from './tagfit.js';
import {
  DAY, ID, MAGIC, MiB, UNPAID_SECONDS, bodyLength, checkOpen, cents, globalStore, count, hmacHex, iso,
  json, listOrders, newId, now, product, putRecord, refuse, safeEqual, startsWith, store, stripe, stripeKey,
  switchedOff, today, week, weekOrders,
} from './lib.js';

const KINDS = ['stencil'];            // design.json "kind"; "inlay" after launch (decision 29)
const PREVIEW_MAX = 3 * MiB;
const STL_MAX = 25 * MiB;
const OUT = {
  'proof.png': { max: 5 * MiB, type: 'image/png', magic: MAGIC.png },
  'build.json': { max: MiB, type: 'application/json' },
};
const PART_FILE = /^[a-z0-9][a-z0-9-]{0,40}\.stl$/;
const DESIGN_FILES = { 'design.json': 'application/json', 'photo.jpg': 'image/jpeg', 'drawing.png': 'image/png', 'preview.jpg': 'image/jpeg' };
// PATCH may move an order only along these arrows. "drafted" comes only from the Slant endpoint, and
// "purged" only from a purge.
const ARROWS = {
  paid: ['built', 'needs-rj', 'cancelled'],
  built: ['needs-rj', 'cancelled'],
  drafted: ['processed', 'needs-rj', 'cancelled'],
  processed: ['shipped', 'cancelled'],
  'needs-rj': ['built', 'cancelled'],
};
const OPEN_STATES = ['shipped', 'cancelled', 'purged'];
const KEEP_PHOTOS_DAYS = 60;
const KEEP_EVIDENCE_DAYS = 180;
const KEEP_RECORD_DAYS = 7 * 365;
const PROOF_LINK_SECONDS = 7 * DAY;
const SLANT_API = 'https://slant3dapi.com/v2/api';
const ORDERS_EMAIL = 'orders@robotlantern.com';

// ---- placing an order ----------------------------------------------------------------------

// POST /api/orders, for a product with "drawing". `body` is already parsed.
export async function createDesigns(env, mode, slug, p, body) {
  const kv = store(env, mode);
  if (await switchedOff(kv, 'orders')) refuse(503, "We're not taking orders just now. Please come back later.", { off: true });
  await checkOpen(kv, slug, p);
  const list = body.designs;
  const { maxDesigns, maxPerOrder } = p.pricing;
  if (!Array.isArray(list) || !list.length) refuse(400, 'Send the designs: a list of at least one.');
  if (list.length > maxDesigns) refuse(400, `An order takes at most ${maxDesigns} designs.`);
  const designs = [];
  for (const [i, x] of list.entries()) designs.push(await checkDesign(kv, slug, p, x, i + 1));
  const total = designs.reduce((n, d) => n + d.quantity, 0);
  if (total > maxPerOrder) refuse(400, `An order takes at most ${maxPerOrder} ornaments.`);

  const priced = priceOrder(p, designs);
  if (typeof body.price !== 'number') refuse(400, 'Send the price the page showed, as price.');
  if (cents(body.price) !== priced.total) {
    refuse(409, `The price is $${(priced.total / 100).toFixed(2)}, not $${body.price.toFixed(2)}.`, {
      price: priced.total / 100, each: designs.map((d) => d.each / 100),
    });
  }
  const t = now();
  const drawingExpiry = Math.min(...designs.map((d) => d.expires || Infinity));
  const expires = Math.min(t + UNPAID_SECONDS, drawingExpiry);
  if (expires - t < 2 * 3600) refuse(410, 'A drawing in this order is about to expire. Please make it again.');
  for (const d of designs) delete d.expires;
  const rec = {
    id: newId(), mode, product: slug, kind: 'designs', designs, count: total, price: priced.total,
    shown: cents(body.price), version: typeof body.version === 'string' ? body.version.slice(0, 80) : null,
    status: 'open', created: iso(t), expires,
  };
  await putRecord(kv, rec);
  return json({
    id: rec.id, mode, count: total, price: rec.price / 100, expires: iso(expires),
    designs: designs.map((d) => ({ k: d.k, each: d.each / 100, quantity: d.quantity })),
    files: designs.map((d) => `${d.k}/preview.jpg`),
  }, 201);
}

async function checkDesign(kv, slug, p, x, k) {
  if (!x || typeof x !== 'object' || Array.isArray(x)) refuse(400, `Design ${k} must be an object.`);
  const at = (msg, extra) => refuse(400, `Design ${k}: ${msg}`, { design: k, ...extra });
  const kind = x.kind ?? 'stencil';
  if (!KINDS.includes(kind)) at(`we don't make ${kind} designs yet.`);
  const quantity = x.quantity;
  if (!Number.isInteger(quantity) || quantity < 1) at('the quantity must be a whole number from 1.');

  let d;
  let suggested;
  const ref = x.drawing;
  if (ref && typeof ref.static === 'string') {
    const [sid, did, extra] = ref.static.split('/');
    const subject = p.drawing.subjects.find((s) => s.id === sid && s.source === 'static');
    const design = subject?.designs.find((s) => s.id === did);
    if (!design || extra !== undefined) at(`there's no ready-made design ${ref.static}.`);
    d = { k, kind, source: 'static', subject: sid, drawing: { static: `${sid}/${did}` }, sha256: design.sha256 };
    suggested = design.text;
  } else if (ref && typeof ref.id === 'string') {
    if (!ID.test(ref.id) || !Number.isInteger(ref.n)) at('drawing must be {"id", "n"} or {"static"}.');
    const rec = await kv.get(`drawing:${ref.id}`, 'json');
    if (!rec || rec.product !== slug) at('that drawing has expired or was never made. Drawings are kept two days.');
    if (ref.n < 1 || ref.n > rec.tries) at(`drawing ${ref.id} has no try ${ref.n}.`);
    d = { k, kind, source: rec.source, subject: rec.subject, drawing: { id: ref.id, n: ref.n }, expires: rec.expires };
  } else {
    at('drawing must be {"id", "n"} or {"static"}.');
  }

  d.options = chosen(p, x.options, at);
  for (const pair of p.differ) {
    if (new Set(pair.map((o) => d.options[o])).size < pair.length) {
      at(`${listOf(pair.map((o) => p.options.find((x) => x.id === o).label))} can't be the same colour.`, { options: pair });
    }
  }
  const rule = p.text;
  const needed = rule && Object.entries(rule.when || {}).every(([o, v]) => d.options[o] === v);
  if (needed) {
    const text = x.text ?? suggested;
    if (typeof text !== 'string' || !text.trim()) at('the tag needs text.', { text: true });
    if (text.length > rule.max) at(`the tag takes at most ${rule.max} characters.`, { text: true });
    if (!new RegExp(`^[${rule.allowed}]+$`).test(text)) at(`the tag takes only letters, numbers, spaces and ' & . , ! ? -`, { text: true });
    const font = rule.font ? d.options[rule.font] : null;
    if (font) {
      const fit = tagFit(text, font);
      if (!fit.fits) at(`"${text}" doesn't fit the tag in this font: ${fit.reason}.`, { text: true, fit });
    }
    d.text = text;
  }
  d.quantity = quantity;
  return d;
}

// Each option in the product file, from what was sent or the option's default. No option is named here.
function chosen(p, sent, at) {
  const given = sent && typeof sent === 'object' && !Array.isArray(sent) ? sent : {};
  const out = {};
  for (const o of p.options) {
    const id = Object.hasOwn(given, o.id) ? given[o.id] : o.default;
    const c = o.choices.find((c) => c.id === id);
    if (!c) at(id === undefined ? `choose a ${o.label.toLowerCase()}.` : `there's no ${o.label.toLowerCase()} ${id}.`, { option: o.id });
    out[o.id] = c.id;
  }
  for (const key of Object.keys(given)) if (!Object.hasOwn(out, key)) at(`there's no option ${key}.`, { option: key });
  return out;
}

function listOf(words) {
  return words.length < 3 ? words.join(' and ') : `${words.slice(0, -1).join(', ')} and ${words.at(-1)}`;
}

// price(design): the tier its order's count falls in, plus the modifiers that apply to it (decision 29).
// Options' own "add" amounts count too, as for any photo product.
export function priceOrder(p, designs) {
  const n = designs.reduce((s, d) => s + d.quantity, 0);
  const tier = p.pricing.tiers.filter((t) => t.from <= n).at(-1);
  let total = 0;
  for (const d of designs) {
    const attrs = { kind: d.kind, source: d.source, subject: d.subject, ...d.options };
    const mods = p.pricing.modifiers.filter((m) => Object.entries(m.when).every(([k, v]) => attrs[k] === v));
    const adds = p.options.reduce((s, o) => s + (o.choices.find((c) => c.id === d.options[o.id])?.add || 0), 0);
    d.each = cents(tier.each + mods.reduce((s, m) => s + m.add, 0) + adds);
    total += d.each * d.quantity;
  }
  return { tier, count: n, total };
}

// PUT /api/orders/<id>/<k>/preview.jpg, from the page: the picture the customer approved.
export async function putPreview(request, env, mode, id, k) {
  const kv = store(env, mode);
  const rec = await kv.get(`order:${id}`, 'json');
  if (!rec || rec.kind !== 'designs') refuse(404, 'No such order. Unpaid orders expire after two days.');
  if (!rec.designs.some((d) => String(d.k) === k)) refuse(404, `This order has no design ${k}.`);
  if (rec.status !== 'open') refuse(409, 'This order has gone to checkout, so its files are fixed.');
  if ((request.headers.get('content-type') || '').split(';')[0].trim() !== 'image/jpeg') refuse(415, 'Send preview.jpg as image/jpeg.');
  const size = bodyLength(request, PREVIEW_MAX);
  if (rec.expires - now() < 3600) refuse(410, 'This order has nearly expired. Please start again.');
  await kv.put(`file:${id}/${k}/preview.jpg`, request.body, { expiration: rec.expires, metadata: { size, type: 'image/jpeg' } });
  return json({ name: `${k}/preview.jpg`, size }, 201);
}

// For checkout: every preview is there and a JPEG, and every drawing is still there.
export async function checkDesignFiles(kv, rec) {
  const missing = [];
  const wrong = [];
  for (const d of rec.designs) {
    const name = `${d.k}/preview.jpg`;
    const { value } = await kv.getWithMetadata(`file:${rec.id}/${name}`, { type: 'stream' });
    if (!value) missing.push(name);
    else if (!(await startsWith(value, MAGIC.jpg))) wrong.push(name);
    if (d.drawing?.id && !(await kv.get(`drawing:${d.drawing.id}`))) {
      refuse(410, `The drawing for design ${d.k} has expired. Please make it again.`, { design: d.k });
    }
  }
  return { missing, wrong };
}

// One Checkout line per design, with its quantity (docs/ORDERS.md, "Orders").
export function designLines(p, rec, ids) {
  const fresh = priceOrder(p, rec.designs);
  rec.price = fresh.total;
  return rec.designs.map((d) => ({
    quantity: d.quantity,
    price_data: { currency: 'usd', unit_amount: d.each, tax_behavior: 'exclusive', product: ids.product },
  }));
}

export function designSummary(p, rec) {
  const label = (o, id) => p.options.find((x) => x.id === o)?.choices.find((c) => c.id === id)?.label || id;
  const lines = rec.designs.map((d) => {
    const opts = p.options.map((o) => `${o.label} ${label(o.id, d.options[o.id])}`);
    return `${d.k}: ${d.quantity} × ${opts.join(', ')}${d.text ? `, tag "${d.text}"` : ''}`;
  });
  return `${rec.count} ornament${rec.count === 1 ? '' : 's'}. ${lines.join('. ')}.`.slice(0, 1000);
}

// The webhook's paid step for an order of designs: design.json, the photo and the chosen drawing copied
// into the order's folder, and the preview, all written again with no expiry (KV can't change one).
export async function paidDesigns(kv, rec) {
  for (const d of rec.designs) {
    const dir = `file:${rec.id}/${d.k}`;
    const design = JSON.stringify({
      product: rec.product, order: rec.id, k: d.k, kind: d.kind, source: d.source, subject: d.subject,
      drawing: d.drawing, ...(d.sha256 && { sha256: d.sha256 }), options: d.options,
      ...(d.text !== undefined && { text: d.text }), quantity: d.quantity, price: d.each / 100,
    }, null, 1);
    await kv.put(`${dir}/design.json`, design, { metadata: { size: design.length, type: 'application/json' } });
    const copies = [[`${dir}/preview.jpg`, `${dir}/preview.jpg`]];
    if (d.drawing.id) {
      copies.push([`file:drawing:${d.drawing.id}/${d.drawing.n}.png`, `${dir}/drawing.png`]);
      if (d.source === 'made') copies.push([`file:drawing:${d.drawing.id}/photo.jpg`, `${dir}/photo.jpg`]);
    }
    for (const [from, to] of copies) {
      const { value, metadata } = await kv.getWithMetadata(from, { type: 'stream' });
      // Missing can mean KV hasn't reached this location yet: the error makes Stripe try again later.
      if (!value) throw new Error(`order ${rec.id}: ${from.split('/').slice(-1)[0]} for design ${d.k} not found`);
      await kv.put(to, value, { metadata });
    }
  }
}

// ---- the queue's endpoints (the queue's token sets the mode) ------------------------------

export async function queueList(kv) {
  const rows = await listOrders(kv);
  const queue = rows
    .filter((r) => r.status === 'paid' && !OPEN_STATES.includes(r.state || 'paid'))
    .map((r) => ({ id: r.id, product: r.product, state: r.state || 'paid', paid: r.paid }))
    .sort((a, b) => String(a.paid).localeCompare(String(b.paid)));
  return json({ queue });
}

export async function designFile(kv, rec, k, name) {
  const d = rec.designs.find((x) => String(x.k) === k);
  if (!d) refuse(404, `This order has no design ${k}.`);
  if (!name.startsWith('out/') && !Object.hasOwn(DESIGN_FILES, name)) refuse(404, `There's no ${name}.`);
  const { value, metadata } = await kv.getWithMetadata(`file:${rec.id}/${k}/${name}`, { type: 'stream' });
  if (!value) refuse(404, `${k}/${name} isn't there${rec.purged ? ' (purged)' : ''}.`);
  return new Response(value, {
    headers: { 'content-type': metadata?.type || 'application/octet-stream', 'x-file-size': String(metadata?.size ?? '') },
  });
}

// PUT /api/orders/<id>/<k>/out/<name>: the routine's build of design k.
export async function putOut(request, kv, rec, k, name) {
  if (!rec.designs.some((x) => String(x.k) === k)) refuse(404, `This order has no design ${k}.`);
  if (rec.status !== 'paid' || !['paid', 'built', 'needs-rj'].includes(rec.state)) {
    refuse(409, `The order is ${rec.state || rec.status}, so its build is fixed.`);
  }
  const type = (request.headers.get('content-type') || '').split(';')[0].trim();
  let spec = OUT[name];
  if (!spec) {
    const build = await kv.get(`file:${rec.id}/${k}/out/build.json`, 'json');
    if (!build) refuse(409, 'Send build.json first: its parts list names the STLs.');
    if (!PART_FILE.test(name) || !build.parts.some((x) => x.file === name)) refuse(400, `build.json's parts don't list ${name}.`);
    spec = { max: STL_MAX, type: 'model/stl' };
  }
  if (type !== spec.type) refuse(415, `Send ${name} as ${spec.type}.`);
  const size = bodyLength(request, spec.max);
  let body = request.body;
  if (name === 'build.json') {
    const text = await request.text();
    let build;
    try {
      build = JSON.parse(text);
    } catch {
      refuse(400, "build.json isn't JSON.");
    }
    const parts = build?.parts;
    if (!Array.isArray(parts) || !parts.length || parts.some((x) => !x?.part || !PART_FILE.test(x.file || '') || !x.colour)) {
      refuse(400, 'build.json needs parts: [{"part", "file", "colour"}, …], each file a .stl.');
    }
    body = text;
  } else if (spec.magic) {
    body = new Uint8Array(await request.arrayBuffer());
    if (!spec.magic.every((x, i) => body[i] === x)) refuse(415, `${name} isn't a PNG.`);
  }
  await kv.put(`file:${rec.id}/${k}/out/${name}`, body, { metadata: { size, type: spec.type } });
  return json({ name: `${k}/out/${name}`, size }, 201);
}

// PATCH /api/orders/<id>: {"state", "note"} along the arrows, plus "tracking" when shipped.
export async function patchOrder(request, kv, rec) {
  let body;
  try {
    body = JSON.parse(await request.text());
  } catch {
    refuse(400, 'Send {"state", "note"} as JSON.');
  }
  const from = rec.state;
  const to = body?.state;
  if (rec.status !== 'paid' || !ARROWS[from]?.includes(to)) {
    refuse(409, `An order can't go from ${from || rec.status} to ${to}.`, { state: from, allowed: ARROWS[from] || [] });
  }
  if (to === 'built') {
    for (const d of rec.designs) {
      for (const f of ['build.json', 'proof.png']) {
        const v = await kv.get(`file:${rec.id}/${d.k}/out/${f}`, 'stream');
        if (!v) refuse(409, `Design ${d.k} has no out/${f} yet.`);
        await v.cancel();
      }
    }
  }
  const note = typeof body.note === 'string' ? body.note.slice(0, 500) : null;
  move(rec, to, note);
  if (to === 'shipped' && typeof body.tracking === 'string') rec.tracking = body.tracking.slice(0, 200);
  await putRecord(kv, rec);
  return json(rec);
}

function move(rec, state, note) {
  rec.state = state;
  rec.history = [...(rec.history || []), { state, when: iso(), note: note || null }];
  rec.dates = rec.dates || {};
  if (state === 'shipped' || state === 'cancelled') rec.dates[state] = iso();
}

// GET /api/orders/<id>/contact: the customer's name and email, from Stripe, only for the shipping email.
export async function contact(env, mode, rec) {
  if (rec.state !== 'shipped') refuse(409, 'Only a shipped order has a shipping email to write.');
  const s = await stripe(stripeKey(env, mode), `checkout/sessions/${rec.session}`);
  const ship = s.collected_information?.shipping_details || s.shipping_details;
  return json({ id: rec.id, name: s.customer_details?.name || ship?.name || null, email: s.customer_details?.email || null });
}

// ---- proof links ------------------------------------------------------------------------------

// GET /api/orders/<id>/link/proof.png (queue): a link to each design's proof that lasts seven days.
export async function proofLinks(env, mode, rec, origin) {
  if (!env.PROOF_LINK_SECRET) refuse(503, 'Proof links aren\'t set up.');
  const e = now() + PROOF_LINK_SECONDS;
  const base = mode === 'live' ? 'https://robotlantern.com' : origin;
  const links = [];
  for (const d of rec.designs) {
    const path = `${mode}/${rec.id}/${d.k}/proof.png`;
    const s = await hmacHex(env.PROOF_LINK_SECRET, `${path}:${e}`);
    links.push({ design: d.k, url: `${base}/api/proofs/${path}?e=${e}&s=${s}` });
  }
  return json({ id: rec.id, expires: iso(e), links });
}

// GET /api/proofs/<mode>/<id>/<k>/proof.png?e=&s=: the proof itself, for whoever has the link.
export async function proof(env, url, [mode, id, k, name]) {
  const e = Number(url.searchParams.get('e'));
  const s = url.searchParams.get('s') || '';
  if (!['test', 'live'].includes(mode) || !ID.test(id || '') || !/^\d+$/.test(k || '') || name !== 'proof.png') refuse(404, 'Not found');
  if (!env.PROOF_LINK_SECRET || !Number.isInteger(e)) refuse(403, 'This link is broken.');
  const want = await hmacHex(env.PROOF_LINK_SECRET, `${mode}/${id}/${k}/proof.png:${e}`);
  if (!safeEqual(s, want)) refuse(403, 'This link is broken.');
  if (e < now()) refuse(410, 'This link has expired.');
  const { value } = await store(env, mode).getWithMetadata(`file:${id}/${k}/out/proof.png`, { type: 'stream' });
  if (!value) refuse(404, 'This proof is gone.');
  return new Response(value, { headers: { 'content-type': 'image/png', 'cache-control': 'private, max-age=3600' } });
}

// ---- Slant drafts --------------------------------------------------------------------------

// POST /api/orders/<id>/slant (docs/ORDERS.md, "Slant drafts"). In the sandbox it never calls Slant: it
// returns what it would have sent, with the address left out, because the routine never sees it.
export async function slantDraft(request, env, mode, kv, rec) {
  if (rec.slant) return json({ id: rec.id, state: rec.state, recorded: true, slant: rec.slant });
  if (rec.state !== 'built') refuse(409, `The order is ${rec.state || rec.status}; it must be built.`);
  let body;
  try {
    body = JSON.parse(await request.text());
  } catch {
    refuse(400, 'Send {"items": […]} as JSON.');
  }
  const p = product(rec.product, mode);
  const items = await checkItems(kv, p, rec, body?.items);

  rec.slant = { state: 'drafting', started: iso() };
  await putRecord(kv, rec);
  const s = await stripe(stripeKey(env, mode), `checkout/sessions/${rec.session}`);
  const ship = s.collected_information?.shipping_details || s.shipping_details;
  if (!ship?.address) {
    delete rec.slant;
    await putRecord(kv, rec);
    refuse(409, 'The Checkout Session has no shipping address.');
  }
  const a = ship.address;
  const address = { name: ship.name, line1: a.line1, line2: a.line2 || undefined, city: a.city, state: a.state, zip: a.postal_code, country: a.country };
  const order = {
    platformId: env.SLANT_PLATFORM_ID,
    customer: { details: { email: ORDERS_EMAIL, address } },
    items: items.map((i) => ({ type: 'PRINT', publicFileServiceId: i.fileId, filamentId: i.filamentId, quantity: i.quantity })),
  };

  if (mode !== 'live') {
    // Slant can't cancel or delete a draft (docs/CHARGES.md), so the sandbox never makes one.
    rec.slant = { state: 'dry-run', dryRun: true, orderId: null, printingCost: null, deliveryCost: null, drafted: iso() };
    move(rec, 'drafted', 'dry run: no Slant call in the sandbox');
    await putRecord(kv, rec);
    const shown = {
      ...order,
      platformId: env.SLANT_PLATFORM_ID ? '(SLANT_PLATFORM_ID)' : '(not set)',
      customer: { details: { email: ORDERS_EMAIL, address: Object.fromEntries(Object.entries(address).filter(([, v]) => v).map(([k]) => [k, '(from Stripe)'])) } },
    };
    return json({ id: rec.id, state: rec.state, dryRun: true, request: shown, slant: rec.slant });
  }

  if (!env.SLANT_API_KEY || !env.SLANT_PLATFORM_ID) {
    delete rec.slant;
    await putRecord(kv, rec);
    refuse(503, "Slant isn't set up in the Worker.");
  }
  let res;
  let out;
  try {
    res = await fetch(`${SLANT_API}/orders`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${env.SLANT_API_KEY}`, 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(order),
    });
    out = await res.json().catch(() => null);
  } catch (err) {
    out = { message: String(err.message || err) };
  }
  const data = out?.data || out;
  if (res?.ok && data?.publicId) {
    rec.slant = { state: 'drafted', orderId: data.publicId, printingCost: Number(data.printingCost), deliveryCost: Number(data.deliveryCost), drafted: iso() };
    move(rec, 'drafted', `Slant ${data.publicId}`);
  } else {
    // Whether Slant made a draft is unknown, so this never retries by itself: RJ looks in Slant first.
    const why = `Slant ${res?.status || 'unreachable'}: ${String(out?.message || out?.error || '').slice(0, 200)}`;
    rec.slant = { state: 'failed', error: why, at: iso() };
    move(rec, 'needs-rj', `${why}. Check Slant's dashboard for a draft before trying again.`);
  }
  await putRecord(kv, rec);
  console.log(JSON.stringify({ order: rec.id, slant: rec.slant.state }));
  return json({ id: rec.id, state: rec.state, slant: rec.slant }, rec.slant.state === 'drafted' ? 200 : 502);
}

// One item per part in each design's build.json "parts", list for list, with that design's quantity and
// the Slant filament of the part's colour (decision 29).
async function checkItems(kv, p, rec, items) {
  if (!Array.isArray(items) || !items.length) refuse(400, 'Send items: one per part of each design.');
  const want = [];
  for (const d of rec.designs) {
    const build = await kv.get(`file:${rec.id}/${d.k}/out/build.json`, 'json');
    if (!build?.parts) refuse(409, `Design ${d.k} has no build.json.`);
    for (const part of build.parts) {
      const filament = p.options.flatMap((o) => o.choices).find((c) => c.id === part.colour && c.slant)?.slant;
      if (!filament) refuse(409, `Design ${d.k}: there's no Slant filament for ${part.colour}.`);
      want.push({ design: d.k, part: part.part, quantity: d.quantity, filamentId: filament });
    }
  }
  if (items.length !== want.length) refuse(400, `Expected ${want.length} items, one per part, not ${items.length}.`, { expected: want });
  return items.map((it, i) => {
    const w = want[i];
    const where = `Item ${i + 1}`;
    if (it?.design !== w.design || it?.part !== w.part) refuse(400, `${where} should be design ${w.design}'s ${w.part}.`, { expected: want });
    if (it.quantity !== w.quantity) refuse(400, `${where}: design ${w.design} is ${w.quantity}, not ${it.quantity}.`);
    if (it.filamentId !== w.filamentId) refuse(400, `${where}: the ${w.part}'s colour is Slant filament ${w.filamentId}.`);
    if (typeof it.fileId !== 'string' || !/^[A-Za-z0-9_-]{1,100}$/.test(it.fileId)) refuse(400, `${where} needs Slant's fileId.`);
    return { ...w, fileId: it.fileId };
  });
}

// ---- stats ---------------------------------------------------------------------------------

export async function stats(env, mode, kv, catalogProducts) {
  const day = today();
  const w = week();
  const [d, writes, sd, so] = await Promise.all([
    drawingStats(env, kv), count(globalStore(env), `stats:writes:${day}`),
    switchedOff(kv, 'drawings'), switchedOff(kv, 'orders'),
  ]);
  const orders = {};
  for (const [slug, p] of catalogProducts) orders[slug] = { week: w, count: (await weekOrders(kv, slug, w)).length, cap: p.weeklyCap };
  return json({
    mode, day, ...d, orders,
    kvWrites: { today: writes, warnAbove: limits.kvWritesWarn, note: 'both modes; counted by the Worker' },
    switches: { drawings: sd ? 'off' : 'on', orders: so ? 'off' : 'on' },
  });
}

export async function addWrites(env, n) {
  const g = globalStore(env);
  if (!g || !n) return;
  const key = `stats:writes:${today()}`;
  try {
    await g.put(key, String((await count(g, key)) + n + 1), { expirationTtl: 40 * DAY });
  } catch {
    // A busy second: the count is approximate anyway.
  }
}

// ---- purge (decision 6, as amended by 28) ----------------------------------------------------

// DELETE /api/orders/<id> purges now: the photo, the drawing, the build and the drawing's own files.
// With ?keep=evidence, preview.jpg and out/build.json stay, as after 60 days. An unpaid order is
// deleted outright and leaves a tombstone. The record of a paid one stays, without drawing references,
// for seven years.
export async function purgeDesigns(kv, rec, keepEvidence) {
  const keep = (name) => keepEvidence && /^\d+\/(preview\.jpg|out\/build\.json)$/.test(name);
  const deleted = [];
  for (const key of await keys(kv, `file:${rec.id}/`)) {
    const name = key.slice(`file:${rec.id}/`.length);
    if (keep(name)) continue;
    await kv.delete(key);
    deleted.push(name);
  }
  for (const d of rec.designs) {
    if (!d.drawing?.id) continue;
    for (const key of await keys(kv, `file:drawing:${d.drawing.id}/`)) await kv.delete(key);
    await kv.delete(`drawing:${d.drawing.id}`);
  }
  if (rec.status !== 'paid') {
    const tombstone = { id: rec.id, kind: 'designs', status: 'purged', product: rec.product, session: rec.session, purged: { all: iso() } };
    await kv.put(`order:${rec.id}`, JSON.stringify(tombstone), { expirationTtl: 90 * DAY, metadata: { product: rec.product, status: 'purged', state: 'purged', purged: tombstone.purged } });
    return json({ id: rec.id, purged: deleted });
  }
  for (const d of rec.designs) if (d.drawing?.id) d.drawing = { purged: true };
  const when = iso();
  rec.purged = { ...(rec.purged || {}), photos: rec.purged?.photos || when, ...(keepEvidence ? {} : { evidence: when }) };
  const since = Date.parse(rec.dates?.shipped || rec.dates?.cancelled || when) / 1000;
  rec.keepUntil = Math.floor(since + KEEP_RECORD_DAYS * DAY);
  if (rec.state !== 'purged') move(rec, 'purged', keepEvidence ? 'photos and drawings deleted; preview and build.json kept' : 'everything deleted');
  else rec.history.push({ state: 'purged', when, note: keepEvidence ? 'photos and drawings deleted' : 'preview and build.json deleted' });
  await putRecord(kv, rec);
  return json({ id: rec.id, purged: deleted, kept: keepEvidence ? 'preview.jpg and build.json' : null });
}

async function keys(kv, prefix) {
  const out = [];
  let cursor;
  do {
    const page = await kv.list({ prefix, cursor });
    out.push(...page.keys.map((k) => k.name));
    cursor = page.list_complete ? null : page.cursor;
  } while (cursor);
  return out;
}

// What's due: 60 days after shipping or cancelling, the photos and drawings; 180 days after, the preview
// and build.json too. The Worker's daily cron runs this; POST /api/purge runs it now (?dry=1 to look).
export async function purgeDue(kv, dry) {
  const t = now();
  const done = [];
  for (const r of await listOrders(kv)) {
    if (r.status !== 'paid') continue;
    const since = r.shipped || r.cancelled;
    if (!since) continue;
    const days = (t - Date.parse(since) / 1000) / DAY;
    const stage = days >= KEEP_EVIDENCE_DAYS && !r.purged?.evidence ? 'evidence'
      : days >= KEEP_PHOTOS_DAYS && !r.purged?.photos ? 'photos' : null;
    if (!stage) continue;
    done.push({ id: r.id, stage });
    if (dry) continue;
    const rec = await kv.get(`order:${r.id}`, 'json');
    if (rec?.kind === 'designs') await purgeDesigns(kv, rec, stage === 'photos');
  }
  return done;
}
