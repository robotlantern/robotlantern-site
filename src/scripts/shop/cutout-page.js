// The product page for a drawing product (docs/ORDERS.md, "The flow" and "The page"). It reads the product
// file the page embeds (#product-data), so subjects, colours, fonts and prices are data, and talks to the order
// Worker: drawings, orders of designs, previews and checkout. Nothing is kept in the browser's storage; a
// reload starts again.

import { tagFit } from '../../../shop-worker/tagfit.js';
import { checkDrawing, explain, checkFile, checkPixels, normalise } from './stencil-drawing.js';
import { layout, paint, compose, FONTS } from './stencil-ornament.js';

const LIVE_HOSTS = ['robotlantern.com', 'www.robotlantern.com'];
// robotlantern.com routes /api/ to the Worker; everywhere else (previews, dev) uses the sandbox's.
const API = LIVE_HOSTS.includes(location.hostname) ? '' : 'https://shop.robotlantern.workers.dev';
const BACKDROP = '#b8bdc7';
const PREVIEW_PX = 1024;

let P, SLUG, OPT, $;
const designs = [];
let cur = 0;
let capacity = { open: true, drawings: true, orders: true };
let busy = false;

// ---- small helpers ---------------------------------------------------------------------------------------

const money = (n) => `$${n % 1 ? n.toFixed(2) : n}`;
const subjectOf = (id) => P.subjects.find((s) => s.id === id);
const choice = (opt, id) => OPT[opt].choices.find((c) => c.id === id);
const frame = () => new Promise((r) => requestAnimationFrame(() => setTimeout(r, 0)));
const plural = (n, one, many = `${one}s`) => `${n} ${n === 1 ? one : many}`;

function say(el, text, bad = false) {
  el.textContent = text;
  el.classList.toggle('bad', bad);
}

async function api(path, init = {}) {
  let res;
  try {
    res = await fetch(`${API}/api/${path}`, init);
  } catch {
    return { ok: false, status: 0, body: { error: "Couldn't reach the shop. Check your connection and try again." } };
  }
  let body = {};
  try { body = await res.json(); } catch { /* not JSON */ }
  return { ok: res.ok, status: res.status, body };
}

async function imageData(source, w, h, fillWhite = false) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  const g = c.getContext('2d', { willReadFrequently: true });
  if (fillWhite) { g.fillStyle = '#fff'; g.fillRect(0, 0, w, h); }
  g.drawImage(source, 0, 0, w, h);
  return g.getImageData(0, 0, w, h);
}

// ---- colour distance, for the close-colours note (CIEDE2000, from the picker) ----------------------------

function lab(hex) {
  const v = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255).map((c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  const f = (t) => (t > 216 / 24389 ? Math.cbrt(t) : (24389 / 27 * t + 16) / 116);
  const x = f((v[0] * 0.4124 + v[1] * 0.3576 + v[2] * 0.1805) / 0.95047);
  const y = f(v[0] * 0.2126 + v[1] * 0.7152 + v[2] * 0.0722);
  const z = f((v[0] * 0.0193 + v[1] * 0.1192 + v[2] * 0.9505) / 1.08883);
  return [116 * y - 16, 500 * (x - y), 200 * (y - z)];
}
function deltaE(h1, h2) {
  const [L1, a1, b1] = lab(h1), [L2, a2, b2] = lab(h2);
  const rad = Math.PI / 180, deg = 180 / Math.PI;
  const C1 = Math.hypot(a1, b1), C2 = Math.hypot(a2, b2), Cb = (C1 + C2) / 2;
  const G = 0.5 * (1 - Math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)));
  const a1p = a1 * (1 + G), a2p = a2 * (1 + G);
  const C1p = Math.hypot(a1p, b1), C2p = Math.hypot(a2p, b2);
  const hp = (b, a) => { if (!b && !a) return 0; const h = Math.atan2(b, a) * deg; return h < 0 ? h + 360 : h; };
  const h1p = hp(b1, a1p), h2p = hp(b2, a2p);
  const dL = L2 - L1, dC = C2p - C1p;
  let dh = 0;
  if (C1p * C2p) { dh = h2p - h1p; if (dh > 180) dh -= 360; else if (dh < -180) dh += 360; }
  const dH = 2 * Math.sqrt(C1p * C2p) * Math.sin((dh / 2) * rad);
  const Lb = (L1 + L2) / 2, Cbp = (C1p + C2p) / 2;
  let hb = h1p + h2p;
  if (C1p * C2p) { if (Math.abs(h1p - h2p) > 180) hb += h1p + h2p < 360 ? 360 : -360; hb /= 2; }
  const T = 1 - 0.17 * Math.cos((hb - 30) * rad) + 0.24 * Math.cos(2 * hb * rad) + 0.32 * Math.cos((3 * hb + 6) * rad) - 0.2 * Math.cos((4 * hb - 63) * rad);
  const dTh = 30 * Math.exp(-(((hb - 275) / 25) ** 2));
  const Rc = 2 * Math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7));
  const Sl = 1 + (0.015 * (Lb - 50) ** 2) / Math.sqrt(20 + (Lb - 50) ** 2);
  const Sc = 1 + 0.045 * Cbp, Sh = 1 + 0.015 * Cbp * T;
  const Rt = -Math.sin(2 * dTh * rad) * Rc;
  return Math.sqrt((dL / Sl) ** 2 + (dC / Sc) ** 2 + (dH / Sh) ** 2 + Rt * (dC / Sc) * (dH / Sh));
}

// ---- designs ---------------------------------------------------------------------------------------------

function defaults() {
  const o = {};
  for (const opt of P.options) o[opt.id] = opt.default ?? opt.choices[0].id;
  const pair = P.pairs.find((p) => choice('base', p.base) && choice('stencil', p.stencil));
  if (pair) Object.assign(o, { base: pair.base, stencil: pair.stencil });
  if (OPT.tag) o.tag = OPT.tag.choices.some((c) => c.id === 'yes') ? 'yes' : o.tag;
  return o;
}

function newDesign(subject) {
  return {
    subject, kind: null, tries: [], pick: null, drawingId: null, left: null, staticId: null,
    photo: null, crop: { x: 0.5, y: 0.5, zoom: 1 }, options: defaults(), text: '', quantity: 1,
    madeOnce: false,
  };
}

const design = () => designs[cur];
const pickedTry = (d = design()) => d.tries.find((t) => t.n === d.pick) || null;
const tagOn = (d) => d.options.tag === 'yes';
const textRule = () => P.text;
const allowedRe = () => new RegExp(`^[${textRule().allowed}]*$`);

// Is the tag's text acceptable, and in which fonts does it fit? { ok, message, fits: {font: bool} }
function tagState(d) {
  const t = d.text;
  const artW = pickedTry(d)?.check.art_mm[0] ?? 80;
  const fits = {};
  for (const c of OPT.font.choices) fits[c.id] = t.trim() ? tagFit(t, c.id, artW).fits : false;
  if (!tagOn(d)) return { ok: true, message: '', fits };
  if (!t.trim()) return { ok: false, message: 'Type what the tag says, or turn the tag off.', fits };
  if ([...t].length > textRule().max) return { ok: false, message: `The tag takes at most ${textRule().max} characters.`, fits };
  if (!allowedRe().test(t)) return { ok: false, message: "The tag takes letters, numbers, spaces and ' & . , ! ? - only.", fits };
  const any = Object.values(fits).some(Boolean);
  if (!any) return { ok: false, message: "That's too long for the tag in every font. Try something shorter.", fits };
  const fit = tagFit(t, d.options.font, artW);
  if (!fit.fits) return { ok: false, message: `That doesn't fit the tag in ${choice('font', d.options.font).label}.`, fits };
  return { ok: true, message: `It fits: letters ${fit.textMm.toFixed(1)} mm tall in ${choice('font', d.options.font).label}.`, fits };
}

// What's still missing before a design can be ordered, or '' when it's ready.
function missing(d) {
  const t = pickedTry(d);
  if (!t) return subjectOf(d.subject).source === 'static' ? 'pick a design' : 'make or add a drawing';
  if (!t.check.ok) return 'choose a drawing that passes the check';
  const ts = tagState(d);
  if (!ts.ok) return ts.message.replace(/\.$/, '').replace(/^./, (c) => c.toLowerCase());
  if (!Number.isInteger(d.quantity) || d.quantity < 1) return 'set how many';
  return '';
}

// price(design), as the Worker has it (shop-worker/designs.js, priceOrder): the tier for the order's total
// count, plus each design's modifiers and option amounts.
function priceOrder() {
  const n = designs.reduce((s, d) => s + (d.quantity || 0), 0);
  const tiers = P.pricing.tiers;
  const tier = tiers.filter((t) => t.from <= Math.max(n, 1)).at(-1);
  let total = 0;
  const each = designs.map((d) => {
    const source = d.kind === 'static' ? 'static' : d.kind === 'upload' ? 'upload' : 'made';
    const attrs = { kind: 'stencil', source, subject: d.subject, ...d.options };
    const mods = (P.pricing.modifiers || []).filter((m) => Object.entries(m.when).every(([k, v]) => attrs[k] === v));
    const adds = P.options.reduce((s, o) => s + (o.choices.find((c) => c.id === d.options[o.id])?.add || 0), 0);
    const e = Math.round((tier.each + mods.reduce((s, m) => s + m.add, 0) + adds) * 100);
    total += e * (d.quantity || 0);
    return e / 100;
  });
  const next = tiers.find((t) => t.from > n);
  return { n, tier, each, total: total / 100, next };
}

// ---- drawings: check and geometry ------------------------------------------------------------------------

async function addTry(d, n, blob) {
  const bmp = await createImageBitmap(blob);
  const im = await imageData(bmp, bmp.width, bmp.height, true);
  await frame();
  const check = checkDrawing(im.data, im.width, im.height);
  const url = URL.createObjectURL(blob);
  const t = { n, url, check, geo: {} };
  d.tries = d.tries.filter((x) => x.n !== n).concat(t).sort((a, b) => a.n - b.n);
  return t;
}

function geometry(t, withTag) {
  const k = withTag ? 'tag' : 'plain';
  if (!t.geo[k]) t.geo[k] = layout(t.check, withTag);
  return t.geo[k];
}

async function fontReady(font) {
  const f = FONTS[font];
  if (!f) return;
  try { await document.fonts.load(`${f.weight} 40px "${f.family}"`); } catch { /* falls back */ }
}

// The design painted at full size, for the stage, the thumbnails and preview.jpg.
async function painted(d) {
  const t = pickedTry(d);
  if (!t || !t.check.ok) return null;
  const on = tagOn(d);
  if (on) await fontReady(d.options.font);
  const ts = on ? tagState(d) : null;
  return paint(geometry(t, on), {
    base: choice('base', d.options.base).hex,
    stencil: choice('stencil', d.options.stencil).hex,
    text: on && ts.ok ? d.text : '',
    font: d.options.font,
  });
}

// ---- rendering --------------------------------------------------------------------------------------------

let renderSeq = 0;
async function render() {
  const seq = ++renderSeq;
  const d = design();
  const canvas = $('preview');
  const pic = await painted(d);
  if (seq !== renderSeq) return;
  const size = Math.round(Math.min(1024, canvas.clientWidth * (window.devicePixelRatio || 1)) || 720);
  if (pic) {
    compose(canvas, pic, BACKDROP, size);
    $('stage-empty').hidden = true;
  } else {
    canvas.width = canvas.height = size;
    canvas.getContext('2d').clearRect(0, 0, size, size);
    $('stage-empty').hidden = false;
  }
  const base = choice('base', d.options.base).label, sten = choice('stencil', d.options.stencil).label;
  const tag = tagOn(d) && d.text.trim() ? `, tag reads “${d.text.trim()}”` : tagOn(d) ? ', name tag' : ', no tag';
  const words = `${base} base, ${sten} stencil${tag}`;
  canvas.setAttribute('aria-label', pic ? `Your ornament: ${words}` : 'Your ornament shows here once there is a drawing');
  $('chosen').textContent = pic ? words : '';
  thumb(cur, pic);
}

const thumbs = new Map();
function thumb(k, pic) {
  const c = document.createElement('canvas');
  if (pic) compose(c, pic, BACKDROP, 168);
  else { c.width = c.height = 168; }
  thumbs.set(designs[k], c);
  renderOrder();
}

function renderSubject() {
  const d = design();
  const s = subjectOf(d.subject);
  for (const r of document.querySelectorAll('input[name="subject"]')) r.checked = r.value === d.subject;
  const made = s.source !== 'static';
  $('made').hidden = !made;
  $('gallery').hidden = made;
  if (made) {
    $('crop-hint').textContent = s.crop || '';
    $('made-h').textContent = s.label;
    renderCrop();
    renderTries();
  } else {
    renderGallery();
  }
}

function renderTries() {
  const d = design();
  const row = $('tries-row');
  row.replaceChildren();
  const made = d.kind === 'made' || d.kind === 'upload';
  $('tries').hidden = !made || !d.tries.length;
  for (const t of made ? d.tries : []) {
    const lab = document.createElement('label');
    lab.className = 'pick';
    const r = Object.assign(document.createElement('input'), { type: 'radio', name: 'try', value: String(t.n), checked: t.n === d.pick, disabled: !t.check.ok });
    r.addEventListener('change', () => { d.pick = t.n; changed({ tries: true }); });
    const img = Object.assign(document.createElement('img'), { src: t.url, alt: '' });
    const span = document.createElement('span');
    span.textContent = d.kind === 'upload' ? (t.check.ok ? 'Your drawing' : 'Your drawing: won’t print') : t.check.ok ? `Try ${t.n}` : `Try ${t.n}: won’t print`;
    lab.append(r, img, span);
    row.append(lab);
  }
  const again = $('again');
  again.hidden = d.kind !== 'made' || !d.tries.length;
  again.disabled = busy || !d.left || !capacity.drawings;
  again.textContent = d.left ? `Try again (${plural(d.left, 'try', 'tries')} left)` : 'No tries left for this photo';
  $('draw').disabled = busy || !d.photo || !capacity.drawings;
}

const galleryCache = new Map();
function renderGallery() {
  const d = design();
  const s = subjectOf(d.subject);
  $('gallery').querySelector('legend').textContent = s.label;
  const row = $('gallery-row');
  row.replaceChildren();
  for (const x of s.designs) {
    const id = `${s.id}/${x.id}`;
    const lab = document.createElement('label');
    lab.className = 'pick';
    const r = Object.assign(document.createElement('input'), { type: 'radio', name: 'ready', value: id, checked: d.staticId === id });
    r.addEventListener('change', () => pickStatic(x, id));
    const img = Object.assign(document.createElement('img'), { src: x.url, alt: x.alt, loading: 'lazy' });
    const span = document.createElement('span');
    span.textContent = x.label;
    lab.append(r, img, span);
    row.append(lab);
  }
}

async function pickStatic(x, id) {
  const d = design();
  d.kind = 'static';
  d.staticId = id;
  d.text = x.text;
  d.options.font = x.font;
  if (OPT.tag) d.options.tag = 'yes';
  d.tries = [];
  d.pick = null;
  renderControls();
  let t = galleryCache.get(id);
  if (!t) {
    const blob = await (await fetch(x.url)).blob();
    const holder = { tries: [] };
    t = await addTry(holder, 1, blob);
    galleryCache.set(id, t);
  }
  if (design() !== d || d.staticId !== id) return;
  d.tries = [t];
  d.pick = 1;
  changed({});
}

function renderSwatches() {
  const d = design();
  for (const part of ['base', 'stencil']) {
    const other = part === 'base' ? 'stencil' : 'base';
    const differ = P.differ.some((pair) => pair.includes(part) && pair.includes(other));
    for (const r of $(part).querySelectorAll('input')) {
      r.checked = r.value === d.options[part];
      r.disabled = differ && r.value === d.options[other];
    }
    $(`${part}-val`).textContent = choice(part, d.options[part]).label;
  }
  for (const b of $('pairs').querySelectorAll('button')) {
    b.setAttribute('aria-pressed', String(b.dataset.base === d.options.base && b.dataset.stencil === d.options.stencil));
  }
  const de = deltaE(choice('base', d.options.base).hex, choice('stencil', d.options.stencil).hex);
  $('close-note').hidden = de >= 20;
}

function renderTag() {
  const d = design();
  $('tag').checked = tagOn(d);
  $('tag-body').hidden = !tagOn(d);
  if ($('tag-text').value !== d.text) $('tag-text').value = d.text;
  const ts = tagState(d);
  const anyText = !!d.text.trim();
  for (const o of $('font').options) {
    const fits = !anyText || ts.fits[o.value];
    o.disabled = !fits;
    o.textContent = choice('font', o.value).label + (fits ? '' : ' (too long)');
  }
  $('font').value = d.options.font;
  say($('tag-status'), ts.message, !ts.ok && anyText);
}

function renderControls() {
  renderSubject();
  renderSwatches();
  renderTag();
  $('quantity').value = String(design().quantity);
  const e = $('editing');
  e.hidden = designs.length < 2;
  e.textContent = `Editing design ${cur + 1} of ${designs.length}.`;
}

function renderOrder() {
  const list = $('designs');
  list.replaceChildren();
  designs.forEach((d, k) => {
    const li = document.createElement('li');
    if (k === cur) li.setAttribute('aria-current', 'true');
    const pic = thumbs.get(d) || Object.assign(document.createElement('div'), { className: 'blank' });
    const what = document.createElement('div');
    what.className = 'what';
    const s = subjectOf(d.subject);
    const ready = s.source === 'static' && d.staticId ? s.designs.find((x) => `${s.id}/${x.id}` === d.staticId)?.label : null;
    const name = `Design ${k + 1}: ${ready || s.label}`;
    const tag = tagOn(d) && d.text.trim() ? `, “${d.text.trim()}”` : '';
    what.textContent = name;
    const em = document.createElement('em');
    const need = missing(d);
    em.textContent = need ? `Still to do: ${need}.` : `${choice('base', d.options.base).label} and ${choice('stencil', d.options.stencil).label}${tag}`;
    what.append(em);
    const row = document.createElement('div');
    row.className = 'row';
    const ql = document.createElement('label');
    ql.textContent = 'How many';
    const q = Object.assign(document.createElement('input'), { type: 'number', min: '1', max: String(P.pricing.maxPerOrder), step: '1', value: String(d.quantity), inputMode: 'numeric' });
    q.setAttribute('aria-label', `How many of design ${k + 1}`);
    q.addEventListener('change', () => { setQuantity(d, q.value); });
    ql.append(q);
    row.append(ql);
    if (k !== cur) {
      const edit = Object.assign(document.createElement('button'), { type: 'button', className: 'act act--quiet', textContent: 'Edit' });
      edit.setAttribute('aria-label', `Edit design ${k + 1}`);
      edit.addEventListener('click', () => { cur = k; changed({ all: true }); $('maker').scrollIntoView({ behavior: 'smooth' }); });
      row.append(edit);
    }
    if (designs.length > 1) {
      const rm = Object.assign(document.createElement('button'), { type: 'button', className: 'act act--quiet', textContent: 'Remove' });
      rm.setAttribute('aria-label', `Remove design ${k + 1}`);
      rm.addEventListener('click', () => removeDesign(k));
      row.append(rm);
    }
    li.append(pic, what, row);
    list.append(li);
  });
  $('add').disabled = designs.length >= P.pricing.maxDesigns;
  $('add').textContent = designs.length >= P.pricing.maxDesigns ? `An order takes up to ${P.pricing.maxDesigns} designs` : 'Add another design';
  renderTotal();
}

function renderTotal() {
  const pr = priceOrder();
  const t = $('total');
  t.replaceChildren(`${money(pr.total)} for ${plural(pr.n, 'ornament')}`);
  const small = document.createElement('small');
  const same = pr.each.every((e) => e === pr.each[0]);
  small.textContent = `${same ? `${money(pr.each[0] ?? pr.tier.each)} each` : 'Priced by design'}, with US shipping included.`;
  if (pr.next) small.textContent += ` From ${pr.next.from} ornaments, ${money(pr.next.each)} each: ${plural(pr.next.from - pr.n, 'more')} saves ${money((pr.tier.each - pr.next.each) * pr.next.from)}.`;
  if (pr.n > P.pricing.maxPerOrder) small.textContent += ` An order takes at most ${P.pricing.maxPerOrder}.`;
  t.append(small);
  const needs = designs.map((d, k) => [k, missing(d)]).filter(([, m]) => m);
  const closed = !capacity.open || !capacity.orders;
  $('order').disabled = busy || closed || !!needs.length || pr.n > P.pricing.maxPerOrder;
  if (!busy) {
    say($('order-status'), needs.length ? needs.map(([k, m]) => `Design ${k + 1}: ${m}.`).join(' ') : '');
  }
}

function changed({ all = false, tries = false } = {}) {
  if (all) renderControls();
  else {
    renderSwatches();
    renderTag();
    if (tries) renderTries();
  }
  render();
}

function setQuantity(d, v) {
  const n = Math.max(1, Math.min(P.pricing.maxPerOrder, Math.round(Number(v)) || 1));
  d.quantity = n;
  if (d === design()) $('quantity').value = String(n);
  renderOrder();
}

function removeDesign(k) {
  const [gone] = designs.splice(k, 1);
  thumbs.delete(gone);
  if (cur >= designs.length) cur = designs.length - 1;
  else if (k < cur) cur--;
  changed({ all: true });
}

// ---- photo and crop ---------------------------------------------------------------------------------------

function cropScale(d, side) {
  const { w, h } = d.photo;
  const mode = subjectOf(d.subject).cropMode;
  return (mode === 'fit' ? side / Math.max(w, h) : side / Math.min(w, h)) * d.crop.zoom;
}

function clampCrop(d) {
  const { w, h } = d.photo;
  const mode = subjectOf(d.subject).cropMode;
  const half = 0.5 / cropScale(d, 1);                // half the square's side, in photo px
  const c = d.crop;
  let x = c.x * w, y = c.y * h;
  if (mode === 'fit') {
    x = Math.min(Math.max(x, 0), w); y = Math.min(Math.max(y, 0), h);
  } else {
    x = Math.min(Math.max(x, half), w - half); y = Math.min(Math.max(y, half), h - half);
  }
  c.x = x / w; c.y = y / h;
}

function drawCrop(target, d, side) {
  const g = target.getContext('2d');
  g.fillStyle = '#fff';
  g.fillRect(0, 0, side, side);
  const k = cropScale(d, side);
  const { w, h, bmp } = d.photo;
  g.imageSmoothingQuality = 'high';
  g.drawImage(bmp, side / 2 - d.crop.x * w * k, side / 2 - d.crop.y * h * k, w * k, h * k);
}

function renderCrop() {
  const d = design();
  $('crop').hidden = !d.photo;
  if (!d.photo) return;
  const c = $('crop-canvas');
  const side = Math.round((c.clientWidth || 320) * (window.devicePixelRatio || 1));
  c.width = c.height = side;
  $('zoom').value = String(d.crop.zoom);
  drawCrop(c, d, side);
}

async function photoChosen(file) {
  const d = design();
  say($('draw-status'), '');
  if (!file) return;
  let bmp;
  try {
    bmp = await createImageBitmap(file, { imageOrientation: 'from-image' });
  } catch {
    say($('draw-status'), "Couldn't read that photo. Try a JPEG or PNG.", true);
    return;
  }
  d.photo = { bmp, w: bmp.width, h: bmp.height };
  d.crop = { x: 0.5, y: 0.5, zoom: 1 };
  clampCrop(d);
  renderCrop();
  renderTries();
  say($('draw-status'), 'Move and zoom the photo to fit the square, then press Make my drawing.');
}

function cropGestures() {
  const box = $('crop-box');
  const pts = new Map();
  let start = null;
  const snapshot = () => {
    const d = design();
    const [a, b] = [...pts.values()];
    return { crop: { ...d.crop }, a: { ...a }, dist: b ? Math.hypot(a.x - b.x, a.y - b.y) : 0, mid: b ? { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 } : { ...a } };
  };
  box.addEventListener('pointerdown', (e) => {
    if (!design().photo) return;
    box.setPointerCapture(e.pointerId);
    pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
    start = snapshot();
  });
  box.addEventListener('pointermove', (e) => {
    if (!pts.has(e.pointerId) || !start) return;
    pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
    const d = design();
    const side = box.clientWidth;
    const [a, b] = [...pts.values()];
    const mid = b ? { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 } : a;
    if (b && start.dist) d.crop.zoom = Math.min(4, Math.max(1, start.crop.zoom * (Math.hypot(a.x - b.x, a.y - b.y) / start.dist)));
    const k = cropScale(d, side);
    d.crop.x = start.crop.x - (mid.x - start.mid.x) / k / d.photo.w;
    d.crop.y = start.crop.y - (mid.y - start.mid.y) / k / d.photo.h;
    clampCrop(d);
    renderCrop();
  });
  const end = (e) => { pts.delete(e.pointerId); start = pts.size ? snapshot() : null; };
  box.addEventListener('pointerup', end);
  box.addEventListener('pointercancel', end);
  box.addEventListener('wheel', (e) => {
    const d = design();
    if (!d.photo) return;
    e.preventDefault();
    d.crop.zoom = Math.min(4, Math.max(1, d.crop.zoom * Math.exp(-e.deltaY / 400)));
    clampCrop(d);
    renderCrop();
  }, { passive: false });
  $('zoom').addEventListener('input', () => {
    const d = design();
    if (!d.photo) return;
    d.crop.zoom = Number($('zoom').value);
    clampCrop(d);
    renderCrop();
  });
}

// The crop as the Worker takes it: a 1024 x 1024 JPEG, re-encoded, so the camera's details (GPS included)
// stay behind.
function cropJpeg(d) {
  const c = document.createElement('canvas');
  c.width = c.height = P.edge;
  drawCrop(c, d, P.edge);
  return new Promise((r) => c.toBlob(r, 'image/jpeg', 0.9));
}

// ---- the Worker: drawings ---------------------------------------------------------------------------------

function refusal(res, what = 'drawing') {
  const b = res.body || {};
  if (res.status === 429) {
    const h = b.retryAfter ? Math.ceil(b.retryAfter / 3600) : null;
    return `${b.error || 'That’s all for today.'}${h ? ` Try again in about ${plural(h, 'hour')}.` : ''} You can still use your own drawing or a ready-made design.`;
  }
  if (res.status === 503) return b.error || `We're not taking ${what}s just now. Please come back later.`;
  if (res.status === 422 || b.moderation) return "The drawing service wouldn't draw this photo. Try a different one. It didn't use up a try.";
  if (res.status === 502) return "The drawing didn't come through. Please try again; it didn't use up a try.";
  return b.error || 'Something went wrong. Please try again.';
}

function waiting(el, text) {
  const t0 = Date.now();
  say(el, text);
  const id = setInterval(() => say(el, `${text} ${Math.round((Date.now() - t0) / 1000)} s`), 1000);
  return () => clearInterval(id);
}

async function received(d, body) {
  const blob = await (await fetch(`data:image/png;base64,${body.image}`)).blob();
  const t = await addTry(d, body.n, blob);
  d.left = body.left;
  if (t.check.ok) d.pick = t.n;
  else if (!pickedTry(d)?.check.ok) d.pick = null;
  const left = body.left ? ` ${plural(body.left, 'try', 'tries')} left.` : ' That was the last try for this photo.';
  const msg = t.check.ok ? `Drawing ${t.n} is ready.${left}` : `Drawing ${t.n} won't print well: ${explain(t.check)}${body.left ? ' Try again for another.' : ''}${left}`;
  return { ok: t.check.ok, msg };
}

async function makeDrawing() {
  const d = design();
  if (!d.photo || busy) return;
  busy = true;
  renderTries(); renderTotal();
  const stop = waiting($('draw-status'), 'Making your drawing. This takes about half a minute to a minute.');
  try {
    const jpeg = await cropJpeg(d);
    const res = await api('drawings', { method: 'POST', headers: { 'Content-Type': 'image/jpeg', 'X-Subject': d.subject, 'X-Product': SLUG }, body: jpeg });
    stop();
    if (!res.ok) { say($('draw-status'), refusal(res), true); if (res.status === 503) capacity.drawings = false; return; }
    Object.assign(d, { kind: 'made', drawingId: res.body.id, tries: [], pick: null, madeOnce: true });
    const r = await received(d, res.body);
    say($('draw-status'), r.msg, !r.ok);
  } finally {
    stop();
    busy = false;
    changed({ tries: true });
  }
}

async function tryAgain() {
  const d = design();
  if (d.kind !== 'made' || !d.left || busy) return;
  busy = true;
  renderTries(); renderTotal();
  const stop = waiting($('draw-status'), 'Making another drawing.');
  try {
    const res = await api(`drawings/${d.drawingId}/again`, { method: 'POST', headers: { 'X-Product': SLUG } });
    stop();
    if (!res.ok) {
      if (res.status === 409) d.left = 0;
      say($('draw-status'), refusal(res), true);
      return;
    }
    const r = await received(d, res.body);
    say($('draw-status'), r.msg, !r.ok);
  } finally {
    stop();
    busy = false;
    changed({ tries: true });
  }
}

// ---- own drawings (decision 28) ------------------------------------------------------------------------------

async function ownDrawing(file) {
  const d = design();
  const out = $('own-status');
  if (!file || busy) return;
  const fileRefusals = checkFile(file);
  if (fileRefusals.length) { say(out, `We can't use it. ${fileRefusals.join(' ')}`, true); return; }
  busy = true;
  say(out, 'Checking your drawing…');
  try {
    let bmp;
    try { bmp = await createImageBitmap(file, { imageOrientation: 'from-image' }); } catch { say(out, "We can't read that image. Send a PNG, JPEG or WebP.", true); return; }
    await frame();
    const raw = await imageData(bmp, bmp.width, bmp.height);
    const { refuse, warn } = checkPixels(raw.data, raw.width, raw.height);
    if (refuse.length) { say(out, `We can't use it. ${refuse.join(' ')}`, true); return; }
    const norm = normalise(bmp, bmp.width, bmp.height, P.edge);
    const blob = await new Promise((r) => norm.toBlob(r, 'image/png'));
    const holder = { tries: [] };
    const t = await addTry(holder, 1, blob);
    if (!t.check.ok) { say(out, `We can't use it. ${explain(t.check)} Ask for a new image rather than editing this one.`, true); return; }
    say(out, 'It passes. Sending it…');
    const subject = subjectOf(d.subject).source === 'static' ? null : d.subject;
    const res = await api('drawings', {
      method: 'POST',
      headers: { 'Content-Type': 'image/png', 'X-Source': 'upload', 'X-Product': SLUG, ...(subject && { 'X-Subject': subject }) },
      body: blob,
    });
    if (!res.ok) { say(out, refusal(res, 'upload'), true); return; }
    Object.assign(d, { kind: 'upload', drawingId: res.body.id, tries: [t], pick: 1, left: 0, photo: null });
    say(out, `Your drawing is in.${warn.length ? ` ${warn.join(' ')}` : ''}`);
  } finally {
    busy = false;
    $('own').value = '';
    changed({ all: true });
  }
}

// ---- the order ----------------------------------------------------------------------------------------------

async function previewJpeg(d) {
  const pic = await painted(d);
  const c = compose(document.createElement('canvas'), pic, BACKDROP, PREVIEW_PX);
  return new Promise((r) => c.toBlob(r, 'image/jpeg', 0.9));
}

function orderBody() {
  const pr = priceOrder();
  return {
    product: SLUG,
    designs: designs.map((d) => ({
      drawing: d.kind === 'static' ? { static: d.staticId } : { id: d.drawingId, n: d.pick },
      options: { ...d.options },
      ...(tagOn(d) && { text: d.text }),
      quantity: d.quantity,
    })),
    price: pr.total,
    version: P.version,
  };
}

async function placeOrder() {
  if (busy) return;
  const out = $('order-status');
  busy = true;
  $('order').disabled = true;
  try {
    say(out, 'Sending your order…');
    const res = await api('orders', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(orderBody()) });
    if (!res.ok) {
      const b = res.body || {};
      if (res.status === 409 && typeof b.price === 'number') {
        say(out, `The price has changed: it's ${money(b.price)} now. Reload the page to see the current prices.`, true);
      } else if (b.design) {
        cur = b.design - 1;
        changed({ all: true });
        say(out, b.error, true);
      } else {
        say(out, b.error || 'Something went wrong. Please try again.', true);
      }
      return;
    }
    const order = res.body;
    say(out, 'Sending the previews you approved…');
    const sendPreview = async (k) => {
      const blob = await previewJpeg(designs[k - 1]);
      return api(`orders/${order.id}/${k}/preview.jpg`, { method: 'PUT', headers: { 'Content-Type': 'image/jpeg' }, body: blob });
    };
    for (const x of order.designs) {
      const r = await sendPreview(x.k);
      if (!r.ok) { say(out, r.body.error || 'A preview didn’t upload. Please try again.', true); return; }
    }
    say(out, 'Opening checkout…');
    for (let attempt = 0; ; attempt++) {
      const c = await api(`orders/${order.id}/checkout`, { method: 'POST' });
      if (c.ok && c.body.url) { location.href = c.body.url; return; }
      if (c.status === 409 && c.body.missing && attempt < 4) {
        // KV can take up to a minute to show a file sent just before (docs/ORDERS.md): send it again and wait.
        for (const name of c.body.missing) await sendPreview(Number(name.split('/')[0]));
        say(out, 'Still getting your previews to the shop. Trying checkout again in a moment…');
        await new Promise((r) => setTimeout(r, 15000));
        continue;
      }
      say(out, c.body.error || 'Checkout didn’t open. Please try again.', true);
      return;
    }
  } finally {
    busy = false;
    renderTotal();
  }
}

// ---- controls ----------------------------------------------------------------------------------------------

function buildSwatches(part) {
  const row = $(part).querySelector('.swatches__row');
  for (const c of OPT[part].choices) {
    const lab = document.createElement('label');
    lab.className = 'sw';
    lab.title = c.label;
    const r = Object.assign(document.createElement('input'), { type: 'radio', name: part, value: c.id });
    r.setAttribute('aria-label', c.label);
    r.addEventListener('change', () => { design().options[part] = c.id; changed(); });
    const i = document.createElement('i');
    i.style.background = c.hex;
    lab.append(r, i);
    const finish = /matte|marble/i.exec(c.label);
    if (finish) { const b = document.createElement('b'); b.textContent = finish[0].toUpperCase(); lab.append(b); }
    row.append(lab);
  }
}

function buildPairs() {
  for (const p of P.pairs) {
    const b = choice('base', p.base), s = choice('stencil', p.stencil);
    if (!b || !s) continue;
    const btn = Object.assign(document.createElement('button'), { type: 'button', className: 'pair' });
    btn.dataset.base = p.base; btn.dataset.stencil = p.stencil;
    btn.setAttribute('aria-label', `${p.label}: ${b.label} base, ${s.label} stencil`);
    const dot = document.createElement('span');
    dot.className = 'dot';
    dot.style.background = b.hex;
    const i = document.createElement('i');
    i.style.background = s.hex;
    dot.append(i);
    btn.append(dot, p.label);
    btn.addEventListener('click', () => { Object.assign(design().options, { base: p.base, stencil: p.stencil }); changed(); });
    $('pairs').append(btn);
  }
}

async function loadCapacity() {
  const res = await api(`products/${SLUG}`);
  if (!res.ok) return;
  capacity = { open: res.body.open !== false, drawings: res.body.drawings !== false, orders: res.body.orders !== false };
  const closed = $('closed');
  if (!capacity.open) {
    const when = res.body.reopens ? new Date(res.body.reopens).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' }) : null;
    closed.textContent = `We've taken all the orders we can make this week.${when ? ` Orders open again ${when}.` : ''}`;
  } else if (!capacity.orders) {
    closed.textContent = "We're not taking orders just now. Please come back later.";
  }
  closed.hidden = capacity.open && capacity.orders;
  if (!capacity.drawings) say($('draw-status'), "We're not making drawings just now. You can still use your own drawing or a ready-made design.", true);
  renderTries();
  renderTotal();
}

export function start() {
  P = JSON.parse(document.getElementById('product-data').textContent);
  SLUG = P.slug;
  OPT = Object.fromEntries(P.options.map((o) => [o.id, o]));
  const ids = {};
  $ = (id) => (ids[id] ||= document.getElementById(id));

  designs.push(newDesign(P.subjects[0].id));
  buildSwatches('base');
  buildSwatches('stencil');
  buildPairs();
  cropGestures();

  for (const r of document.querySelectorAll('input[name="subject"]')) {
    r.addEventListener('change', () => {
      const d = design();
      if (d.subject === r.value) return;
      // A new subject starts this design again, keeping its colours and quantity.
      const fresh = newDesign(r.value);
      Object.assign(fresh, { options: { ...d.options }, quantity: d.quantity });
      designs[cur] = fresh;
      thumbs.delete(d);
      say($('draw-status'), ''); say($('own-status'), '');
      changed({ all: true });
    });
  }
  $('photo').addEventListener('change', (e) => photoChosen(e.target.files[0]));
  $('own').addEventListener('change', (e) => ownDrawing(e.target.files[0]));
  $('draw').addEventListener('click', makeDrawing);
  $('again').addEventListener('click', tryAgain);
  $('swap').addEventListener('click', () => {
    const o = design().options;
    [o.base, o.stencil] = [o.stencil, o.base];
    changed();
  });
  $('tag').addEventListener('change', (e) => { design().options.tag = e.target.checked ? 'yes' : 'no'; changed(); });
  $('tag-text').addEventListener('input', (e) => {
    const d = design();
    d.text = e.target.value;
    const ts = tagState(d);
    // Offer only the fonts the text fits: move off one it no longer fits.
    if (d.text.trim() && !ts.fits[d.options.font]) {
      const first = OPT.font.choices.find((c) => ts.fits[c.id]);
      if (first) d.options.font = first.id;
    }
    changed();
  });
  $('font').addEventListener('change', (e) => { design().options.font = e.target.value; changed(); });
  $('quantity').addEventListener('change', (e) => setQuantity(design(), e.target.value));
  $('add').addEventListener('click', () => {
    if (designs.length >= P.pricing.maxDesigns) return;
    const last = design();
    const d = newDesign(last.subject);
    d.options = { ...last.options };
    designs.push(d);
    cur = designs.length - 1;
    say($('draw-status'), ''); say($('own-status'), '');
    changed({ all: true });
    $('maker').scrollIntoView({ behavior: 'smooth' });
  });
  $('order').addEventListener('click', placeOrder);
  let resize;
  addEventListener('resize', () => { clearTimeout(resize); resize = setTimeout(() => { render(); renderCrop(); }, 150); });

  changed({ all: true });
  loadCapacity();
  document.fonts.ready.then(() => render());
}
