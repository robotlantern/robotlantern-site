// The stencil ornament's preview (docs/ORDERS.md, "The page"): the ornament drawn in the browser from a
// drawing, copying the builder's geometry (tools/ornament/build.py) so the page and the print agree.
//
//   the stencil   the drawing's ink after the builder's cleanup and bridges (stencil-drawing.js), scaled to
//                 fit 80 x 85 mm
//   the tag       17 mm tall, 0.8 of the art's width held between 64 and 72 mm, rounded 4 mm, overlapping
//                 the art until the two join; a plate of stencil with the text cut through in the base colour
//   the base      the silhouette (ink with its holes filled, tag included) grown by the 2 mm rim
//   the ring      10 mm across with a 4 mm hole, on the silhouette's centre line just above the outline,
//                 joined to it by the hull of the ring and a 14 mm band of the outline
//
// The text is fitted as nametag.tag_fit() does it, from shop-worker/tag-metrics.json (the same numbers the
// Worker checks with): advances plus 0.08 em, the outline box scaled into the tag's text box, at most 11 mm.

import metrics from '../../../shop-worker/tag-metrics.json';
import { dilate, erode, edt, fillHoles } from './stencil-drawing.js';

const R = metrics.rule;
const RIM = 2, RING_R = 5, HOLE_R = 2, RING_UP = 3, TAG_ROUND = 4;

// The CSS families the page declares for the five stencil fonts (public/shop/fonts/).
export const FONTS = {
  allerta: { family: 'RL Allerta Stencil', weight: 400 },
  saira: { family: 'RL Saira Stencil One', weight: 400 },
  'big-shoulders': { family: 'RL Big Shoulders Stencil', weight: 800 },
  emblema: { family: 'RL Emblema One', weight: 400 },
  wallpoet: { family: 'RL Wallpoet', weight: 400 },
};

// The tag's width for art artW mm wide (nametag.tag_width).
export const tagWidth = (artW) => Math.min(R.maxTagW, Math.max(R.minTagW, R.share * artW));

// The text laid out as tag_fit() measures it: { box (font units), xs (each glyph's origin), mm (cap height
// of the box), scale (mm per font unit) } or null when there's nothing to draw.
export function textLayout(text, font, artW) {
  const f = metrics.fonts[font];
  if (!f) return null;
  let x = 0, box = null;
  const xs = [];
  for (const ch of text) {
    const g = f.glyphs[ch];
    xs.push(x);
    if (!g) { x += (f.glyphs[' ']?.[0] ?? f.upm / 4) + R.track * f.upm; continue; }
    const [adv, b] = g;
    if (b) {
      const gb = [x + b[0], b[1], x + b[2], b[3]];
      box = box ? [Math.min(box[0], gb[0]), Math.min(box[1], gb[1]), Math.max(box[2], gb[2]), Math.max(box[3], gb[3])] : gb;
    }
    x += adv + R.track * f.upm;
  }
  if (!box) return null;
  const tw = tagWidth(artW);
  const bw = tw - 2 * R.padX, bh = R.tagH - R.padBottom - R.padTop;
  const w = box[2] - box[0], h = box[3] - box[1];
  const scale = Math.min(bw / w, bh / h, R.maxTextH / h);
  return { box, xs, mm: scale * h, scale, upm: f.upm };
}

// Grid classes, painted in this order (later wins).
const BG = 0, BASE_SHADOW = 1, BASE = 2, WALL = 3, SHEET_SHADOW = 4, SHEET = 5, POCKET = 6;

// The ornament's geometry from a checked drawing: { cls (class per grid pixel), W, H, s, tag, artW }.
// `tag` is the text box in grid pixels when the tag is on.
export function layout(check, withTag) {
  const s = check.s, p = 1 / s;                       // mm per px, px per mm
  const artW = check.art_mm[0];
  const half = Math.max(tagWidth(artW) / 2, artW / 2) + RIM + 2;
  // A grid round the drawing's own: room for the tag below, the ring above and the rim at the sides.
  const midX = check.W / 2;
  const left = Math.ceil(Math.max(0, half * p - midX) + RIM * p);
  const top = Math.ceil((RING_UP + RING_R + RIM + 2) * p);
  const bottom = Math.ceil((withTag ? R.tagH + 2 : 0) * p + (RIM + 2) * p);
  const W = check.W + 2 * left, H = check.H + top + bottom;
  const sheet = new Uint8Array(W * H);
  for (let y = 0; y < check.H; y++) sheet.set(check.mask.subarray(y * check.W, (y + 1) * check.W), (y + top) * W + left);

  let sil = fillHoles(sheet, W, H);
  let tag = null;
  if (withTag) {
    let x0 = W, x1 = -1, yb = -1;
    for (let i = 0; i < sil.length; i++) if (sil[i]) { const x = i % W, y = (i / W) | 0; if (x < x0) x0 = x; if (x > x1) x1 = x; if (y > yb) yb = y; }
    const cx = (x0 + x1 + 1) / 2;
    const tw = tagWidth((x1 - x0 + 1) * s);
    const bottomY = yb + 1;                           // the silhouette's lowest edge, in px from the top
    let rect = null;
    for (let overlap = 5; ; overlap += 2) {
      rect = roundRect(W, H, cx - (tw / 2) * p, bottomY - overlap * p, cx + (tw / 2) * p, bottomY + R.tagH * p, TAG_ROUND * p);
      let meets = false;
      for (let i = 0; i < rect.length && !meets; i++) meets = !!(rect[i] && sil[i]);
      if (meets || overlap > 30) break;
    }
    for (let i = 0; i < sheet.length; i++) if (rect[i]) sheet[i] = 1;
    sil = fillHoles(sheet, W, H);
    tag = {
      x0: cx - (tw / 2 - R.padX) * p, x1: cx + (tw / 2 - R.padX) * p,
      y0: bottomY + R.padTop * p, y1: bottomY + (R.tagH - R.padBottom) * p, p,
    };
  }

  // The ring's centre line: the silhouette's centroid.
  let sx = 0, n = 0;
  for (let i = 0; i < sil.length; i++) if (sil[i]) { sx += i % W; n++; }
  const cx = sx / n + 0.5;
  let outline = dilate(sil, W, H, RIM * p);
  const col = Math.round(cx - 0.5);
  let topY = 0;
  while (topY < H && !outline[topY * W + col]) topY++;
  const ringY = topY - RING_UP * p;
  // The neck: the hull of the ring and the outline's 14 mm band below it.
  const pts = [];
  for (let k = 0; k < 64; k++) { const a = (k / 64) * 2 * Math.PI; pts.push([cx + RING_R * p * Math.cos(a), ringY + RING_R * p * Math.sin(a)]); }
  for (let y = topY; y <= Math.min(H - 1, topY + 8 * p); y++) {
    let a = -1, b = -1;
    for (let x = Math.max(0, Math.floor(cx - 7 * p)); x <= Math.min(W - 1, Math.ceil(cx + 7 * p)); x++) {
      if (outline[y * W + x]) { if (a < 0) a = x; b = x + 1; }
    }
    if (a >= 0) pts.push([a, y], [b, y], [a, y + 1], [b, y + 1]);
  }
  fillHull(outline, W, H, hull(pts));
  // Fillet the joins (buffer 1.5 mm out and back), then the outline's outer edge only.
  outline = fillHoles(erode(dilate(outline, W, H, 1.5 * p), W, H, 1.5 * p), W, H);
  const wall = erode(sil, W, H, Math.max(1, 0.6 * p));
  const shadowB = shift(outline, W, H, Math.round(0.75 * p), Math.round(0.75 * p));
  const shadowS = shift(sheet, W, H, Math.round(0.375 * p), Math.round(0.375 * p));

  const cls = new Uint8Array(W * H);
  const hr2 = (HOLE_R * p) ** 2;
  for (let i = 0; i < cls.length; i++) {
    let c = BG;
    if (shadowB[i]) c = BASE_SHADOW;
    if (outline[i]) c = BASE;
    if (sil[i]) c = WALL;
    if (wall[i]) c = BASE;
    if (shadowS[i] && sil[i]) c = SHEET_SHADOW;
    if (sheet[i]) c = SHEET;
    const x = i % W, y = (i / W) | 0;
    if ((x + 0.5 - cx) ** 2 + (y + 0.5 - ringY) ** 2 <= hr2) c = BG;
    cls[i] = c;
  }
  // The pocket's holes (cut-outs in the sheet) show the base: they're already BASE or WALL.
  return { cls, W, H, s, tag, artW, ring: { x: cx, y: ringY } };
}

function roundRect(W, H, x0, y0, x1, y1, r) {
  const m = new Uint8Array(W * H);
  for (let y = Math.max(0, Math.floor(y0)); y < Math.min(H, Math.ceil(y1)); y++) {
    for (let x = Math.max(0, Math.floor(x0)); x < Math.min(W, Math.ceil(x1)); x++) {
      const px = x + 0.5, py = y + 0.5;
      const dx = Math.max(x0 + r - px, 0, px - (x1 - r)), dy = Math.max(y0 + r - py, 0, py - (y1 - r));
      if (dx * dx + dy * dy <= r * r) m[y * W + x] = 1;
    }
  }
  return m;
}

function shift(m, W, H, dx, dy) {
  const out = new Uint8Array(W * H);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const sx = x - dx, sy = y - dy;
    if (sx >= 0 && sy >= 0 && sx < W && sy < H) out[y * W + x] = m[sy * W + sx];
  }
  return out;
}

function hull(pts) {
  pts = pts.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const cross = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lo = [], hi = [];
  for (const q of pts) { while (lo.length >= 2 && cross(lo.at(-2), lo.at(-1), q) <= 0) lo.pop(); lo.push(q); }
  for (const q of pts.reverse()) { while (hi.length >= 2 && cross(hi.at(-2), hi.at(-1), q) <= 0) hi.pop(); hi.push(q); }
  return lo.slice(0, -1).concat(hi.slice(0, -1));
}

function fillHull(m, W, H, poly) {
  const xs = poly.map((q) => q[0]), ys = poly.map((q) => q[1]);
  for (let y = Math.max(0, Math.floor(Math.min(...ys))); y <= Math.min(H - 1, Math.ceil(Math.max(...ys))); y++) {
    for (let x = Math.max(0, Math.floor(Math.min(...xs))); x <= Math.min(W - 1, Math.ceil(Math.max(...xs))); x++) {
      let inside = true;
      for (let k = 0; k < poly.length && inside; k++) {
        const a = poly[k], b = poly[(k + 1) % poly.length];
        inside = (b[0] - a[0]) * (y + 0.5 - a[1]) - (b[1] - a[1]) * (x + 0.5 - a[0]) >= 0;
      }
      if (inside) m[y * W + x] = 1;
    }
  }
}

const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
const dim = (c, f) => c.map((v) => Math.round(v * f));

// The ornament in colour on a canvas of the grid's size, with the tag's text. Returns that canvas.
export function paint(geo, { base, stencil, text, font }) {
  const B = rgb(base), S = rgb(stencil);
  const lut = [null, [0, 0, 0, 90], [...B, 255], [...dim(B, 0.86), 255], [...dim(S, 0.6), 255], [...S, 255]];
  const c = document.createElement('canvas');
  c.width = geo.W; c.height = geo.H;
  const g = c.getContext('2d');
  const im = g.createImageData(geo.W, geo.H);
  const d = im.data;
  for (let i = 0, q = 0; i < geo.cls.length; i++, q += 4) {
    const v = lut[geo.cls[i]];
    if (!v) continue;
    d[q] = v[0]; d[q + 1] = v[1]; d[q + 2] = v[2]; d[q + 3] = v[3];
  }
  g.putImageData(im, 0, 0);
  if (geo.tag && text) {
    const L = textLayout(text, font, geo.artW);
    const F = FONTS[font];
    if (L && F) {
      const k = L.scale * geo.tag.p;                   // px per font unit
      const cx = (geo.tag.x0 + geo.tag.x1) / 2, cy = (geo.tag.y0 + geo.tag.y1) / 2;
      const x0 = cx - ((L.box[0] + L.box[2]) / 2) * k;
      const baseline = cy + ((L.box[1] + L.box[3]) / 2) * k;
      g.fillStyle = base;
      g.textBaseline = 'alphabetic';
      g.textAlign = 'left';
      g.font = `${F.weight} ${L.upm * k}px "${F.family}"`;
      [...text].forEach((ch, i) => g.fillText(ch, x0 + L.xs[i] * k, baseline));
    }
  }
  return c;
}

// The painted ornament fitted into a square canvas of `size` px on `backdrop`, as the page shows it and as
// preview.jpg sends it.
export function compose(target, painted, backdrop, size = target.width) {
  target.width = target.height = size;
  const g = target.getContext('2d');
  g.fillStyle = backdrop;
  g.fillRect(0, 0, size, size);
  const k = (size * 0.9) / Math.max(painted.width, painted.height);
  const w = painted.width * k, h = painted.height * k;
  g.imageSmoothingEnabled = true;
  g.imageSmoothingQuality = 'high';
  g.drawImage(painted, (size - w) / 2, (size - h) / 2, w, h);
  return target;
}

export { edt };
