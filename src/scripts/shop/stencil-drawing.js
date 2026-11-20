// The builder's first steps on a drawing, in the browser: a port of tools/ornament/drawing.py (check_drawing),
// so the page never offers a try the routine would refuse (docs/ORDERS.md, "The page"), and of the upload
// check for own drawings ("Own drawings"). Masks are Uint8Arrays (1 = ink), one byte per pixel.
//
// The rules, in order, as drawing.py has them:
//   ink        any pixel more than 120 (RGB distance) from white
//   scale      the ink's bounding box fits a box, 80 mm wide x 85 mm tall
//   cleanup    drop ink islands under 2 mm2; fatten ink thinner than 1 mm; fill white gaps thinner than 1 mm;
//              widen connecting necks thinner than 1.8 mm
//   bridges    join every island to the main piece by its shortest path, 1.8 mm wide; over 3 mm fails
//   white kept cut-out area after all that / cut-out area in the drawing; under 0.77 fails here (0.8 in the builder, which reads ~0.04 higher)
//
// OpenCV's elliptical kernels are disks here, measured with an exact distance transform, and "white kept" is
// counted on pixels rather than on the builder's vector outline, so a figure can differ from build.json's
// in the second decimal. The routine's own check is the one that counts.

export const DEFAULTS = {
  width: 80, height: 85, minLine: 1.0, minGap: 1.0, neck: 1.8, bridge: 1.8, speck: 2.0,
  ink: 120, maxBridge: 3.0, minWhiteKept: 0.77, // the builder's 0.8, less this port's ~0.04 lower reading (steps 10, 14)
};
const PAD = 40;
// More islands than this after cleanup isn't a drawing the builder should bridge one by one.
const MAX_PIECES = 60;

// ---- distance transform (Felzenszwalb & Huttenlocher), with the nearest feature pixel --------------------

const BIG = 1e20;

function dt1(f, n, d, arg, v, z) {
  let k = 0;
  v[0] = 0; z[0] = -Infinity; z[1] = Infinity;
  for (let q = 1; q < n; q++) {
    let s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k]);
    while (s <= z[k]) { k--; s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k]); }
    k++; v[k] = q; z[k] = s; z[k + 1] = Infinity;
  }
  k = 0;
  for (let q = 0; q < n; q++) {
    while (z[k + 1] < q) k++;
    const dq = q - v[k];
    d[q] = dq * dq + f[v[k]];
    arg[q] = v[k];
  }
}

// Squared distance from each pixel to the nearest pixel where feature is set; with `nearest`, also that
// pixel's index. Pixels outside the image are never features.
export function edt(feature, W, H, nearest = false) {
  const n = Math.max(W, H);
  const f = new Float64Array(n), d = new Float64Array(n), v = new Int32Array(n), z = new Float64Array(n + 1);
  const arg = new Int32Array(n);
  const col = new Float64Array(W * H);
  const rowOf = nearest ? new Int32Array(W * H) : null;
  for (let x = 0; x < W; x++) {
    for (let y = 0; y < H; y++) f[y] = feature[y * W + x] ? 0 : BIG;
    dt1(f, H, d, arg, v, z);
    for (let y = 0; y < H; y++) { col[y * W + x] = d[y]; if (rowOf) rowOf[y * W + x] = arg[y]; }
  }
  const out = new Float32Array(W * H);
  const idx = nearest ? new Int32Array(W * H) : null;
  for (let y = 0; y < H; y++) {
    const o = y * W;
    for (let x = 0; x < W; x++) f[x] = col[o + x];
    dt1(f, W, d, arg, v, z);
    for (let x = 0; x < W; x++) {
      out[o + x] = d[x] >= BIG / 2 ? Infinity : d[x];
      if (idx) idx[o + x] = rowOf[o + arg[x]] * W + arg[x];
    }
  }
  return nearest ? { d2: out, idx } : out;
}

// OpenCV's ellipse of size 2r+1, as a squared-distance limit: it takes in a little more than r.
const reach = (r) => r * r + 0.6 * r;
const radius = (mm, s) => Math.max(1, Math.round(mm / 2 / s));

export function dilate(m, W, H, r) {
  const d2 = edt(m, W, H), t = reach(r), out = new Uint8Array(W * H);
  for (let i = 0; i < out.length; i++) out[i] = d2[i] <= t ? 1 : 0;
  return out;
}

export function erode(m, W, H, r) {
  const inv = new Uint8Array(W * H);
  for (let i = 0; i < inv.length; i++) inv[i] = m[i] ? 0 : 1;
  const d2 = edt(inv, W, H), t = reach(r), out = new Uint8Array(W * H);
  for (let i = 0; i < out.length; i++) out[i] = d2[i] > t ? 1 : 0;
  return out;
}

const open = (m, W, H, r) => dilate(erode(m, W, H, r), W, H, r);
const close = (m, W, H, r) => erode(dilate(m, W, H, r), W, H, r);

// ---- labels and holes ---------------------------------------------------------------------------------------

// 8-connected components. Returns { lab (0 = none), n, sizes (sizes[i] for label i) }.
export function label(m, W, H) {
  const lab = new Int32Array(W * H);
  const parent = [0];
  const find = (a) => { while (parent[a] !== a) { parent[a] = parent[parent[a]]; a = parent[a]; } return a; };
  const join = (a, b) => { a = find(a); b = find(b); if (a !== b) parent[Math.max(a, b)] = Math.min(a, b); };
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const i = y * W + x;
      if (!m[i]) continue;
      let l = 0;
      const look = (j) => { const k = lab[j]; if (k) { if (!l) l = k; else if (k !== l) join(l, k); } };
      if (x > 0) look(i - 1);
      if (y > 0) {
        if (x > 0) look(i - W - 1);
        look(i - W);
        if (x < W - 1) look(i - W + 1);
      }
      if (!l) { l = parent.length; parent.push(l); }
      lab[i] = l;
    }
  }
  const map = new Int32Array(parent.length);
  let n = 0;
  for (let a = 1; a < parent.length; a++) { const r = find(a); if (!map[r]) map[r] = ++n; map[a] = map[r]; }
  const sizes = new Int32Array(n + 1);
  for (let i = 0; i < lab.length; i++) if (lab[i]) { lab[i] = map[lab[i]]; sizes[lab[i]]++; }
  return { lab, n, sizes };
}

// The mask with its holes filled: white not reachable from the border (4-connected), as scipy's
// binary_fill_holes does it.
export function fillHoles(m, W, H) {
  const out = new Uint8Array(W * H).fill(1);
  const stack = [];
  const push = (i) => { if (!m[i] && out[i]) { out[i] = 0; stack.push(i); } };
  for (let x = 0; x < W; x++) { push(x); push((H - 1) * W + x); }
  for (let y = 0; y < H; y++) { push(y * W); push(y * W + W - 1); }
  while (stack.length) {
    const i = stack.pop(), x = i % W;
    if (x > 0) push(i - 1);
    if (x < W - 1) push(i + 1);
    if (i >= W) push(i - W);
    if (i < W * (H - 1)) push(i + W);
  }
  return out;
}

const count = (m) => { let c = 0; for (let i = 0; i < m.length; i++) c += m[i]; return c; };
const holesArea = (m, W, H) => { const f = fillHoles(m, W, H); let c = 0; for (let i = 0; i < m.length; i++) c += f[i] & (1 - m[i]); return c; };

// ---- the steps --------------------------------------------------------------------------------------------

// Ink from RGBA pixels, cropped to the ink with PAD px of white round it. Returns { red, W, H } or null.
export function inkMask(rgba, w, h, ink = DEFAULTS.ink) {
  const t = ink * ink;
  let x0 = w, y0 = h, x1 = -1, y1 = -1;
  const full = new Uint8Array(w * h);
  for (let i = 0, p = 0; i < full.length; i++, p += 4) {
    const r = 255 - rgba[p], g = 255 - rgba[p + 1], b = 255 - rgba[p + 2];
    if (r * r + g * g + b * b > t) {
      full[i] = 1;
      const x = i % w, y = (i / w) | 0;
      if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y;
    }
  }
  if (x1 < 0) return null;
  const W = x1 - x0 + 1 + 2 * PAD, H = y1 - y0 + 1 + 2 * PAD;
  const red = new Uint8Array(W * H);
  for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) red[(y - y0 + PAD) * W + (x - x0 + PAD)] = full[y * w + x];
  return { red, W, H, box: [x0, y0, x1, y1] };
}

function cleanup(red, W, H, s, p) {
  const log = {};
  // drop specks
  let { lab, n, sizes } = label(red, W, H);
  let dropped = 0;
  const keep = new Uint8Array(n + 1);
  for (let i = 1; i <= n; i++) { if (sizes[i] * s * s >= p.speck) keep[i] = 1; else dropped++; }
  red = red.map((_, i) => keep[lab[i]]);
  log.specks_dropped = dropped;
  // fatten thin ink
  const opened = open(red, W, H, radius(p.minLine, s));
  const thin = red.map((v, i) => v & (1 - opened[i]));
  const fat = dilate(thin, W, H, radius(p.minLine * 0.6, s));
  red = red.map((v, i) => v | fat[i]);
  log.thin_red_mm2 = +(count(thin) * s * s).toFixed(1);
  // fill thin white cuts
  const before = count(red);
  red = close(red, W, H, radius(p.minGap, s));
  log.thin_gaps_filled_mm2 = +((count(red) - before) * s * s).toFixed(1);
  // widen necks: a strip narrower than `neck` that is the only thing joining two wide parts
  const necks = [];
  if (p.neck > 0) {
    const wide = open(red, W, H, radius(p.neck, s));
    const wl = label(wide, W, H).lab;
    const narrow = red.map((v, i) => v & (1 - wide[i]));
    const cl = label(narrow, W, H);
    const inside = new Uint8Array(W * H);
    for (let i = 0; i < inside.length; i++) inside[i] = red[i] ? 0 : 1;
    const toWhite = edt(inside, W, H);
    const first = new Int32Array(cl.n + 1), second = new Uint8Array(cl.n + 1), deepest = new Float32Array(cl.n + 1);
    for (let i = 0; i < cl.lab.length; i++) {
      const c = cl.lab[i];
      if (!c) continue;
      if (toWhite[i] > deepest[c]) deepest[c] = toWhite[i];
      if (second[c]) continue;
      const x = i % W, y = (i / W) | 0;
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
        const xx = x + dx, yy = y + dy;
        if (xx < 0 || yy < 0 || xx >= W || yy >= H) continue;
        const w = wl[yy * W + xx];
        if (!w) continue;
        if (!first[c]) first[c] = w; else if (first[c] !== w) second[c] = 1;
      }
    }
    const byR = new Map();
    for (let c = 1; c <= cl.n; c++) {
      if (!second[c]) continue;
      const w = 2 * Math.sqrt(deepest[c]) * s;
      const r = Math.max(1, Math.round((p.neck - w) / 2 / s) + 1);
      if (!byR.has(r)) byR.set(r, new Uint8Array(cl.n + 1));
      byR.get(r)[c] = 1;
      necks.push(+w.toFixed(2));
    }
    for (const [r, which] of byR) {
      const grow = dilate(cl.lab.map((c) => which[c]), W, H, r);
      red = red.map((v, i) => v | grow[i]);
    }
  }
  log.necks_widened_mm = necks;
  return { red, log };
}

function bridge(red, W, H, s, width) {
  const bridges = [];
  let pieces = null;
  const t = Math.max(2, Math.round(width / s)) / 2;
  for (;;) {
    const { lab, n, sizes } = label(red, W, H);
    if (pieces === null) pieces = n;
    if (n <= 1) break;
    if (n > MAX_PIECES) return { red, pieces, bridges, tooMany: true };
    let main = 1;
    for (let i = 2; i <= n; i++) if (sizes[i] > sizes[main]) main = i;
    const { d2, idx } = edt(lab.map((l) => (l === main ? 1 : 0)), W, H, true);
    let best = -1;
    for (let i = 0; i < lab.length; i++) if (lab[i] && lab[i] !== main && (best < 0 || d2[i] < d2[best])) best = i;
    const to = idx[best];
    capsule(red, W, H, best % W, (best / W) | 0, to % W, (to / W) | 0, t);
    bridges.push(+(Math.sqrt(d2[best]) * s).toFixed(2));
  }
  return { red, pieces, bridges };
}

// A thick line with round ends, as cv2.line draws one.
function capsule(m, W, H, x0, y0, x1, y1, r) {
  const dx = x1 - x0, dy = y1 - y0, L2 = dx * dx + dy * dy || 1;
  const xa = Math.max(0, Math.floor(Math.min(x0, x1) - r)), xb = Math.min(W - 1, Math.ceil(Math.max(x0, x1) + r));
  const ya = Math.max(0, Math.floor(Math.min(y0, y1) - r)), yb = Math.min(H - 1, Math.ceil(Math.max(y0, y1) + r));
  for (let y = ya; y <= yb; y++) for (let x = xa; x <= xb; x++) {
    const u = Math.max(0, Math.min(1, ((x - x0) * dx + (y - y0) * dy) / L2));
    const ex = x - (x0 + u * dx), ey = y - (y0 + u * dy);
    if (ex * ex + ey * ey <= r * r) m[y * W + x] = 1;
  }
}

// check_drawing(): the builder's cleanup and bridge measurement on one drawing (RGBA pixels), with no meshes.
// Returns drawing.py's report, plus the cleaned, bridged mask the preview draws (`mask`, W x H, `s` mm/px).
export function checkDrawing(rgba, w, h, opts = {}) {
  const p = { ...DEFAULTS, ...opts };
  const m = inkMask(rgba, w, h, p.ink);
  if (!m) return { ok: false, problems: ['there is no drawing in the image: no red at all'] };
  const { W, H } = m;
  const red0 = m.red;
  const iw = m.box[2] - m.box[0] + 1, ih = m.box[3] - m.box[1] + 1;
  const s = Math.min(p.width / iw, p.height / ih);
  const { red: cleaned, log } = cleanup(red0, W, H, s, p);
  const b = bridge(cleaned, W, H, s, p.bridge);
  const drawn = holesArea(red0, W, H) * s * s;
  const kept = holesArea(b.red, W, H) * s * s;
  const ratio = drawn >= 1 ? +(kept / drawn).toFixed(2) : null;
  const rep = {
    art_mm: [+(iw * s).toFixed(1), +(ih * s).toFixed(1)], mm_per_px: +s.toFixed(5), pieces: b.pieces, ...log,
    bridges_mm: b.bridges, max_bridge_mm: Math.max(0, ...b.bridges),
    white_mm2: { drawing: +drawn.toFixed(1), kept: +kept.toFixed(1) }, white_kept: ratio,
  };
  const problems = b.bridges.filter((x) => x > p.maxBridge).map((x) => `bridge ${x} mm > ${p.maxBridge}`);
  if (b.tooMany) problems.push(`more than ${MAX_PIECES} loose pieces`);
  if (ratio !== null && ratio < p.minWhiteKept) {
    problems.push(`white kept ${ratio} < ${p.minWhiteKept}: the cleanup filled in cut-outs, so features in the drawing are lost`);
  }
  return { ...rep, problems, ok: !problems.length, mask: b.red, W, H, s };
}

// What a failed check means, in words for the customer.
export function explain(rep) {
  if (rep.ok) return '';
  if (!rep.mask) return "There's no drawing in this image.";
  const far = rep.problems.some((x) => x.startsWith('bridge') || x.startsWith('more than'));
  const lost = rep.white_kept !== null && rep.white_kept < DEFAULTS.minWhiteKept;
  if (far && lost) return 'Part of this drawing floats too far from the rest to join on, and some thin white details would fill in when printed.';
  if (far) return 'Part of this drawing floats too far from the rest to join on, so the stencil would come out in pieces.';
  return 'Some thin white details in this drawing would fill in when printed, so it would lose features you can see here.';
}

// ---- own drawings (docs/ORDERS.md, "Own drawings") ----------------------------------------------------------

export const UPLOAD = { types: ['image/png', 'image/jpeg', 'image/webp'], minPx: 1024, maxPx: 4096, maxBytes: 4 * 1024 * 1024, ink: '#E01010' };

// The checks on the file itself, before it's decoded.
export function checkFile(file) {
  const refuse = [];
  if (!UPLOAD.types.includes(file.type)) refuse.push("It isn't a PNG, JPEG or WebP image.");
  if (file.size > UPLOAD.maxBytes) refuse.push('It is over 4 MB.');
  return refuse;
}

// The checks on its pixels (RGBA at the file's own size). Returns { refuse: [], warn: [] } in words.
export function checkPixels(rgba, w, h) {
  const refuse = [], warn = [];
  if (Math.abs(w - h) > 0.02 * Math.max(w, h)) refuse.push(`It is ${w} × ${h} pixels; it needs to be square.`);
  else if (Math.min(w, h) < UPLOAD.minPx || Math.max(w, h) > UPLOAD.maxPx) refuse.push(`It is ${w} × ${h} pixels; it needs to be from ${UPLOAD.minPx} to ${UPLOAD.maxPx} pixels square.`);
  let clear = 0;
  for (let p = 3; p < rgba.length; p += 4) if (rgba[p] < 250) clear++;
  if (clear / (w * h) > 0.001) refuse.push('It has transparent parts; it needs a white background.');

  // In-between pixels: neither near white nor near the drawing's own ink colour.
  const n = w * h;
  const dw = new Float32Array(n);
  let sr = [], sg = [], sb = [];
  for (let i = 0, p = 0; i < n; i++, p += 4) {
    const r = 255 - rgba[p], g = 255 - rgba[p + 1], b = 255 - rgba[p + 2];
    dw[i] = Math.sqrt(r * r + g * g + b * b);
    if (dw[i] > 200 && (i % 7 === 0)) { sr.push(rgba[p]); sg.push(rgba[p + 1]); sb.push(rgba[p + 2]); }
  }
  if (!sr.length) for (let i = 0, p = 0; i < n; i++, p += 4) if (dw[i] > 120 && i % 7 === 0) { sr.push(rgba[p]); sg.push(rgba[p + 1]); sb.push(rgba[p + 2]); }
  if (!sr.length) { refuse.push("There's no drawing in it: no red at all."); return { refuse, warn }; }
  const med = (a) => { a.sort((x, y) => x - y); return a[a.length >> 1]; };
  const inkCol = [med(sr), med(sg), med(sb)];
  let between = 0;
  for (let i = 0, p = 0; i < n; i++, p += 4) {
    const r = rgba[p] - inkCol[0], g = rgba[p + 1] - inkCol[1], b = rgba[p + 2] - inkCol[2];
    if (dw[i] > 40 && Math.sqrt(r * r + g * g + b * b) > 60) between++;
  }
  const betweenPct = (100 * between) / n;
  if (betweenPct > 6) refuse.push(`It looks like a photo or shaded art (${betweenPct.toFixed(1)}% of it is in-between colours); it needs exactly two flat colours.`);
  else if (betweenPct > 1.5) warn.push('It has soft edges or shading. It will be made exactly two colours.');
  if (inkCol[0] - Math.max(inkCol[1], inkCol[2]) < 80) warn.push("The drawing isn't red. That's fine: any colour on white works, and you choose the colours below.");

  // Shape: the ink over the whole image, as the page will make it (1024 square, then two colours).
  const ink = new Uint8Array(n);
  let x0 = w, y0 = h, x1 = -1, y1 = -1;
  for (let i = 0; i < n; i++) if (dw[i] > DEFAULTS.ink) {
    ink[i] = 1;
    const x = i % w, y = (i / w) | 0;
    if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y;
  }
  const edges = (x0 === 0) + (y0 === 0) + (x1 === w - 1) + (y1 === h - 1);
  const sil = fillHoles(ink, w, h);
  const silN = count(sil), inkN = count(ink);
  const silPct = (100 * silN) / n, cutPct = (100 * (silN - inkN)) / Math.max(silN, 1);
  const full = x1 - x0 > 0.96 * w && y1 - y0 > 0.96 * h;
  if (full) refuse.push('The art fills the whole image. It needs a white margin all round: no frame, no background box, and nothing cut off at the edges.');
  else if (edges >= 3 || silPct > 80) refuse.push('There is no white background round the art: one shape covers most of the image.');
  else if (edges) warn.push('The art touches the edge of the image. Is something cut off?');
  if (cutPct < 3 && !full) refuse.push('It has no features: the shape is almost solid, with nothing cut out of it.');
  if ((x1 - x0 + 1) / w < 0.5) warn.push('The art is less than half the width of the image. It will be scaled up, so it may print rougher.');
  return { refuse, warn };
}

// The drawing as the Worker takes it: 1024 x 1024, every pixel more than 120 from white made #E01010 and the
// rest white. `source` is anything drawImage takes; returns a canvas.
export function normalise(source, sw, sh, edge = 1024) {
  const c = document.createElement('canvas');
  c.width = c.height = edge;
  const g = c.getContext('2d', { willReadFrequently: true });
  g.fillStyle = '#fff';
  g.fillRect(0, 0, edge, edge);
  g.imageSmoothingQuality = 'high';
  const side = Math.min(sw, sh);
  g.drawImage(source, (sw - side) / 2, (sh - side) / 2, side, side, 0, 0, edge, edge);
  const im = g.getImageData(0, 0, edge, edge);
  const d = im.data, t = DEFAULTS.ink * DEFAULTS.ink;
  for (let p = 0; p < d.length; p += 4) {
    const r = 255 - d[p], gg = 255 - d[p + 1], b = 255 - d[p + 2];
    const on = r * r + gg * gg + b * b > t;
    d[p] = on ? 0xe0 : 255; d[p + 1] = on ? 0x10 : 255; d[p + 2] = on ? 0x10 : 255; d[p + 3] = 255;
  }
  g.putImageData(im, 0, 0);
  return c;
}
