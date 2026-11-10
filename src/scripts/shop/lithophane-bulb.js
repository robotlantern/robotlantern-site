// The lithophane ornament's preview: the customer's photo as the printed bulb will look, lit by one tree
// light and unlit. It's a port of lithophane-maker's ornament recipe (products/ornament.py there):
// the same tone steps (autocontrast, CLAHE, sharpen), the optical tone curve through the white filament,
// the model of the bulb's light inside the ball, and the same front view the recipe draws as proof.png.
// What the customer sees here is what the recipe makes.
//
// The sizes in PARAMS come from `products/ornament.py --params <light>`. Rerun it and paste the numbers
// whenever the recipe changes. Nothing here leaves the browser.
//
// Use (the configurator, NOW.md step 10):
//
//   import { createOrnamentPreview } from '../scripts/shop/lithophane-bulb.js';
//   const preview = createOrnamentPreview(canvas, { light: 'mini', cap: 'gold' });
//   await preview.setPhoto(file);              // a File, Blob, ImageBitmap, <img> or <canvas>, upright
//   preview.setCrop({ x, y, w, h });           // the circle's square, fractions of width and height
//   preview.set({ light: 'c9', lit: false });  // and redraws
//   preview.check();                           // { dark, flat, ... } for the photo warning
//   const jpeg = await preview.toBlob();       // preview.jpg for the order bundle
//
// The pure functions (tone, solvePlate, renderFront) take plain arrays, so they also run in Node.

const LUMA = [0.2126, 0.7152, 0.0722];

// Shared by every light (ornament.py: T_MIN, T_MAX, T_PLAIN_MIN, PLATE_T, CHAMFER, SLIT_W, LED, WHITE).
export const COMMON = {
  tMin: 0.6, tMax: 2.8, tPlainMin: 1.2, plateT: 1.6, chamfer: 0.8, slitW: 1.0, pitch: 0.2,
  led: [1.0, 0.86, 0.66],
  absorb: [0.95, 1.05, 1.3], // shelf-matte-white, basis "heuristic" until the wedge is fitted
  tone: { autocontrast: 0.5, clahe: 0.35, sharpen: 0.6 },
};

// From `products/ornament.py --params <light>` (2026-11-10). Sizes in mm, in the ornament's frame:
// y up, the photo facing the viewer, the ball's centre at 0.
export const PARAMS = {
  mini: {
    label: 'Mini LED lights', diameter: 72, R: 34, shoulderDeg: 45, tShoulder: 2.8, rCollar: 9.8,
    yOut: 42.243, yRim: 49.243, lightY: 26.243, alphaDeg: 44, tiltDeg: -8, rimDeg: 2.5, glow: 0.22,
    comp: 0.5, beam: { floor: 0.35, k: 1 }, socketD: 10, cap: { rSkirtOut: 11.6, skirtH: 6.7, fingers: 9 },
  },
  c7: {
    label: 'C7 LED bulbs', diameter: 76, R: 36, shoulderDeg: 45, tShoulder: 2.8, rCollar: 14.7,
    yOut: 40.171, yRim: 47.171, lightY: 3.771, alphaDeg: 44, tiltDeg: -8, rimDeg: 2.5, glow: 0.22,
    comp: 0.5, beam: { floor: 0.6, k: 1 }, socketD: 18, cap: { rSkirtOut: 16.5, skirtH: 6.7, fingers: 13 },
  },
  c9: {
    label: 'C9 LED bulbs', diameter: 84, R: 40, shoulderDeg: 45, tShoulder: 2.8, rCollar: 17.9,
    yOut: 42.628, yRim: 49.628, lightY: -8.172, alphaDeg: 44, tiltDeg: -8, rimDeg: 2.5, glow: 0.22,
    comp: 0.5, beam: { floor: 0.6, k: 1 }, socketD: 23, cap: { rSkirtOut: 19.7, skirtH: 6.7, fingers: 15 },
  },
};

export const CAP_COLOURS = { gold: '#d9a441', silver: '#c9ccd1' };

const rad = (d) => (d * Math.PI) / 180;
const clamp = (v, lo, hi) => (v < lo ? lo : v > hi ? hi : v);
export const srgbToLinear = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
export const linearToSrgb = (c) => {
  c = c < 0 ? 0 : c;
  return c <= 0.0031308 ? c * 12.92 : 1.055 * c ** (1 / 2.4) - 0.055;
};
const hexToLinear = (h) => [1, 3, 5].map((i) => srgbToLinear(parseInt(h.slice(i, i + 2), 16) / 255));

/** numpy's default ("linear") percentile of a numeric array. */
function percentile(values, p) {
  if (!values.length) return 0;
  const v = Float64Array.from(values).sort();
  const pos = (p / 100) * (v.length - 1);
  const i = Math.floor(pos);
  return i + 1 < v.length ? v[i] + (v[i + 1] - v[i]) * (pos - i) : v[i];
}

// ---------------------------------------------------------------------------------------------------
// Tone: litho/imageprep.py `tone()` with the defaults, for a mono lithophane

const M_RGB2XYZ = [0.412453, 0.35758, 0.180423, 0.212671, 0.71516, 0.072169, 0.019334, 0.119193, 0.950227];
const M_XYZ2RGB = [3.240479, -1.53715, -0.498535, -0.969256, 1.875991, 0.041556, 0.055648, -0.204043, 1.057311];
const XN = 0.950456, ZN = 1.088754;
const labF = (t) => (t > 0.008856 ? Math.cbrt(t) : 7.787 * t + 16 / 116);

/** OpenCV's CLAHE on an 8-bit image (createCLAHE(clipLimit, (tiles, tiles)).apply). */
export function clahe(src, w, h, tiles, clipLimit = 2) {
  let pw = w, ph = h, img = src;
  if (w % tiles || h % tiles) {
    // OpenCV pads right and bottom by `tiles - size % tiles`, mirrored (BORDER_REFLECT_101)
    pw = w + tiles - (w % tiles);
    ph = h + tiles - (h % tiles);
    img = new Uint8Array(pw * ph);
    const refl = (i, n) => (i < n ? i : 2 * n - 2 - i);
    for (let y = 0; y < ph; y++) for (let x = 0; x < pw; x++) img[y * pw + x] = src[refl(y, h) * w + refl(x, w)];
  }
  const tw = pw / tiles, th = ph / tiles, area = tw * th;
  const lutScale = 255 / area;
  const limit = Math.max(Math.trunc((clipLimit * area) / 256), 1);
  const luts = [];
  for (let ty = 0; ty < tiles; ty++) {
    for (let tx = 0; tx < tiles; tx++) {
      const hist = new Int32Array(256);
      for (let y = ty * th; y < (ty + 1) * th; y++) for (let x = tx * tw; x < (tx + 1) * tw; x++) hist[img[y * pw + x]]++;
      let clipped = 0;
      for (let i = 0; i < 256; i++) if (hist[i] > limit) { clipped += hist[i] - limit; hist[i] = limit; }
      const batch = Math.trunc(clipped / 256);
      let residual = clipped - batch * 256;
      for (let i = 0; i < 256; i++) hist[i] += batch;
      if (residual) {
        const step = Math.max(Math.trunc(256 / residual), 1);
        for (let i = 0; i < 256 && residual > 0; i += step, residual--) hist[i]++;
      }
      const lut = new Uint8Array(256);
      let sum = 0;
      for (let i = 0; i < 256; i++) { sum += hist[i]; lut[i] = clamp(Math.round(sum * lutScale), 0, 255); }
      luts.push(lut);
    }
  }
  const out = new Uint8Array(w * h);
  for (let y = 0; y < h; y++) {
    const tyf = y / th - 0.5;
    let ty1 = Math.floor(tyf), ty2 = ty1 + 1;
    const ya = tyf - ty1;
    ty1 = Math.max(ty1, 0); ty2 = Math.min(ty2, tiles - 1);
    for (let x = 0; x < w; x++) {
      const txf = x / tw - 0.5;
      let tx1 = Math.floor(txf), tx2 = tx1 + 1;
      const xa = txf - tx1;
      tx1 = Math.max(tx1, 0); tx2 = Math.min(tx2, tiles - 1);
      const v = src[y * w + x];
      const r = (luts[ty1 * tiles + tx1][v] * (1 - xa) + luts[ty1 * tiles + tx2][v] * xa) * (1 - ya)
        + (luts[ty2 * tiles + tx1][v] * (1 - xa) + luts[ty2 * tiles + tx2][v] * xa) * ya;
      out[y * w + x] = clamp(Math.round(r), 0, 255);
    }
  }
  return out;
}

/** Separable Gaussian blur of one float channel, as cv2.GaussianBlur(img, (0, 0), sigma) on float32. */
export function gaussianBlur(src, w, h, sigma) {
  const size = Math.round(sigma * 8 + 1) | 1;
  const r = size >> 1;
  const k = new Float64Array(size);
  let s = 0;
  for (let i = 0; i < size; i++) { k[i] = Math.exp(-((i - r) ** 2) / (2 * sigma * sigma)); s += k[i]; }
  for (let i = 0; i < size; i++) k[i] /= s;
  const refl = (i, n) => (n === 1 ? 0 : i < 0 ? -i : i >= n ? 2 * n - 2 - i : i);
  const tmp = new Float32Array(w * h), out = new Float32Array(w * h);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      let a = 0;
      for (let i = 0; i < size; i++) a += k[i] * src[y * w + refl(x + i - r, w)];
      tmp[y * w + x] = a;
    }
  }
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      let a = 0;
      for (let i = 0; i < size; i++) a += k[i] * tmp[refl(y + i - r, h) * w + x];
      out[y * w + x] = a;
    }
  }
  return out;
}

/**
 * The photo's lightness as the lithophane will carry it.
 * rgb: Float32Array of n*n*3 sRGB values 0..1 (row 0 = top); keep: Float32Array n*n, 1 inside the circle.
 * Returns Float32Array n*n of display-referred lightness 0..1 (imageprep's `Prepared.luma`).
 */
export function tone(rgb, keep, n, opts = COMMON.tone) {
  const N = n * n;
  const c = Float32Array.from(rgb);
  if (opts.autocontrast > 0) {
    const ys = [];
    for (let i = 0; i < N; i++) if (keep[i] > 0.5) ys.push(c[3 * i] * LUMA[0] + c[3 * i + 1] * LUMA[1] + c[3 * i + 2] * LUMA[2]);
    const lo = percentile(ys, opts.autocontrast), hi = percentile(ys, 100 - opts.autocontrast);
    if (hi - lo > 1e-3) for (let i = 0; i < 3 * N; i++) c[i] = (c[i] - lo) / (hi - lo);
  }
  for (let i = 0; i < 3 * N; i++) c[i] = clamp(c[i], 0, 1);
  if (opts.clahe > 0) {
    // Lab as OpenCV computes it for float RGB (sRGB, D65); CLAHE on L in 8 bits; L blended back
    const L = new Float32Array(N), A = new Float32Array(N), B = new Float32Array(N), L8 = new Uint8Array(N);
    for (let i = 0; i < N; i++) {
      const r = srgbToLinear(c[3 * i]), g = srgbToLinear(c[3 * i + 1]), b = srgbToLinear(c[3 * i + 2]);
      const X = (M_RGB2XYZ[0] * r + M_RGB2XYZ[1] * g + M_RGB2XYZ[2] * b) / XN;
      const Y = M_RGB2XYZ[3] * r + M_RGB2XYZ[4] * g + M_RGB2XYZ[5] * b;
      const Z = (M_RGB2XYZ[6] * r + M_RGB2XYZ[7] * g + M_RGB2XYZ[8] * b) / ZN;
      const fy = labF(Y);
      L[i] = Y > 0.008856 ? 116 * fy - 16 : 903.3 * Y;
      A[i] = 500 * (labF(X) - fy);
      B[i] = 200 * (fy - labF(Z));
      L8[i] = Math.trunc(clamp(L[i] * 2.55, 0, 255));
    }
    const tiles = Math.max(2, Math.round(n / 96));
    const eq = clahe(L8, n, n, tiles, 2);
    for (let i = 0; i < N; i++) {
      const l = (1 - opts.clahe) * L[i] + (opts.clahe * eq[i]) / 2.55;
      const fy = (l + 16) / 116;
      const Y = l <= 8 ? l / 903.3 : fy ** 3;
      const fyY = l <= 8 ? 7.787 * Y + 16 / 116 : fy;
      const fx = fyY + A[i] / 500, fz = fyY - B[i] / 200;
      const X = (fx ** 3 > 0.008856 ? fx ** 3 : (fx - 16 / 116) / 7.787) * XN;
      const Z = (fz ** 3 > 0.008856 ? fz ** 3 : (fz - 16 / 116) / 7.787) * ZN;
      for (let k = 0; k < 3; k++) {
        const lin = M_XYZ2RGB[3 * k] * X + M_XYZ2RGB[3 * k + 1] * Y + M_XYZ2RGB[3 * k + 2] * Z;
        c[3 * i + k] = clamp(linearToSrgb(clamp(lin, 0, 1)), 0, 1);
      }
    }
  }
  if (opts.sharpen > 0) {
    const ch = new Float32Array(N);
    for (let k = 0; k < 3; k++) {
      for (let i = 0; i < N; i++) ch[i] = c[3 * i + k];
      const bl = gaussianBlur(ch, n, n, 1.2);
      for (let i = 0; i < N; i++) c[3 * i + k] = clamp(ch[i] + opts.sharpen * (ch[i] - bl[i]), 0, 1);
    }
  }
  const luma = new Float32Array(N);
  for (let i = 0; i < N; i++) {
    luma[i] = linearToSrgb(srgbToLinear(c[3 * i]) * LUMA[0] + srgbToLinear(c[3 * i + 1]) * LUMA[1] + srgbToLinear(c[3 * i + 2]) * LUMA[2]);
  }
  return luma;
}

// ---------------------------------------------------------------------------------------------------
// Optics and light: litho/filaments.py, litho/lighting.py, separate.solve_mono, ornament.py

/** Transmitted luminance through t mm of the white (Beer-Lambert per RGB band). */
export const luminance = (t, a = COMMON.absorb) => LUMA[0] * Math.exp(-a[0] * t) + LUMA[1] * Math.exp(-a[1] * t) + LUMA[2] * Math.exp(-a[2] * t);

/** The curve solve_mono interpolates on: 512 thicknesses from tMin to tMax and their luminance. */
function curve() {
  const ts = new Float64Array(512), y = new Float64Array(512);
  for (let i = 0; i < 512; i++) { ts[i] = COMMON.tMin + ((COMMON.tMax - COMMON.tMin) * i) / 511; y[i] = luminance(ts[i]); }
  return { ts, y };
}
const CURVE = curve();

/** Thickness that passes `want` luminance (np.interp on the falling curve, clamped at its ends). */
function thicknessFor(want) {
  const { ts, y } = CURVE;
  if (want >= y[0]) return ts[0];
  if (want <= y[511]) return ts[511];
  let lo = 0, hi = 511; // y falls with index
  while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (y[mid] >= want) lo = mid; else hi = mid; }
  return ts[lo] + ((ts[hi] - ts[lo]) * (y[lo] - want)) / (y[lo] - y[hi]);
}

function axes(p) {
  const tl = rad(p.tiltDeg);
  return { c: [0, Math.sin(tl), Math.cos(tl)], ex: [1, 0, 0], ey: [0, Math.cos(tl), -Math.sin(tl)] };
}

/** lighting.irradiance for the bulb on the ornament's axis, pointing down. */
function irradiance(p, qx, qy, qz, nx, ny, nz) {
  const vx = qx, vy = qy - p.lightY, vz = qz;
  const d2 = Math.max(vx * vx + vy * vy + vz * vz, 1e-9), d = Math.sqrt(d2);
  const cosT = clamp(-vy / d, 0, 1);
  const I = p.beam.floor + (1 - p.beam.floor) * cosT ** p.beam.k;
  const cosB = clamp((vx * nx + vy * ny + vz * nz) / d, 0, 1);
  return (I * cosB) / d2;
}

function refIrradiance(p) {
  const { c } = axes(p);
  return irradiance(p, p.R * c[0], p.R * c[1], p.R * c[2], c[0], c[1], c[2]);
}

/** The plain wall by latitude (ornament.py fill_profile): an even glow, thicker into the shoulder. */
export function fillProfile(p) {
  const n = 721, lat = new Float64Array(n), t = new Float64Array(n);
  const ref = refIrradiance(p), y0 = CURVE.y[0];
  for (let i = 0; i < n; i++) {
    const la = rad(-90 + ((p.shoulderDeg + 90) * i) / (n - 1));
    const dy = Math.sin(la), dz = Math.cos(la);
    const g = irradiance(p, 0, p.R * dy, p.R * dz, 0, dy, dz) / ref;
    let v = clamp(thicknessFor((p.glow * y0) / Math.max(g, 1e-6)), COMMON.tPlainMin, COMMON.tMax);
    let w = clamp((-90 + ((p.shoulderDeg + 90) * i) / (n - 1) - (p.shoulderDeg - 12)) / 12, 0, 1);
    w = w * w * (3 - 2 * w);
    lat[i] = la;
    t[i] = v + (p.tShoulder - v) * w;
  }
  return (la) => {
    if (la <= lat[0]) return t[0];
    if (la >= lat[n - 1]) return t[n - 1];
    const f = ((la - lat[0]) / (lat[n - 1] - lat[0])) * (n - 1), i = Math.floor(f);
    return t[i] + (t[i + 1] - t[i]) * (f - i);
  };
}

/** The photo's circle as wall thickness: solve_mono's optical curve, with half the light's falloff evened out. */
export function solvePlate(luma, n, p) {
  const { c, ex, ey } = axes(p);
  const k = Math.sin(rad(p.alphaDeg)), ref = refIrradiance(p);
  const yMin = CURVE.y[511], yMax = CURVE.y[0];
  const t = new Float32Array(n * n);
  for (let row = 0; row < n; row++) {
    const yp = -(-k + (2 * k * row) / (n - 1));
    for (let col = 0; col < n; col++) {
      const xp = -k + (2 * k * col) / (n - 1);
      const zp = Math.sqrt(clamp(1 - xp * xp - yp * yp, 0, 1));
      const dx = xp * ex[0] + yp * ey[0] + zp * c[0];
      const dy = xp * ex[1] + yp * ey[1] + zp * c[1];
      const dz = xp * ex[2] + yp * ey[2] + zp * c[2];
      const g = irradiance(p, p.R * dx, p.R * dy, p.R * dz, dx, dy, dz) / ref;
      const v = clamp(luma[row * n + col], 0, 1);
      let want = yMin + (yMax - yMin) * srgbToLinear(v);
      want = clamp(want / Math.max(g ** p.comp, 1e-6), yMin, yMax);
      t[row * n + col] = thicknessFor(want);
    }
  }
  return t;
}

function wallThickness(p, plate, n, fill, dx, dy, dz) {
  const { c, ex, ey } = axes(p);
  const a = rad(p.alphaDeg), k = Math.sin(a);
  const cg = dx * c[0] + dy * c[1] + dz * c[2];
  if (cg >= Math.cos(a)) {
    const mx = clamp((((dx * ex[0] + dy * ex[1] + dz * ex[2]) / k) * 0.5 + 0.5) * (n - 1), 0, n - 1);
    const my = clamp((0.5 - ((dx * ey[0] + dy * ey[1] + dz * ey[2]) / k) * 0.5) * (n - 1), 0, n - 1);
    const x0 = Math.min(Math.floor(mx), n - 2), y0 = Math.min(Math.floor(my), n - 2);
    const fx = mx - x0, fy = my - y0, i = y0 * n + x0;
    return (plate[i] * (1 - fx) + plate[i + 1] * fx) * (1 - fy) + (plate[i + n] * (1 - fx) + plate[i + n + 1] * fx) * fy;
  }
  if (cg >= Math.cos(a + rad(p.rimDeg))) return COMMON.tMax;
  return fill(Math.asin(clamp(dy, -1, 1)));
}

// ---------------------------------------------------------------------------------------------------
// The front view: ornament.py render_front, with the cap and the light's wire

/** The view's extent in mm: the ornament with its cap and a margin. */
export function extentFor(p) {
  const half = p.R + 8;
  return { x0: -half, x1: half, y0: -p.R - 8, y1: p.yRim + COMMON.plateT + 9 };
}

/**
 * Draw the ornament seen from the front. Returns { rgb: Float32Array w*h*3 (sRGB 0..1), w, h, exposure }.
 * plate: solvePlate's output (n*n), or null for a plain ball. opts: { lit, pxPerMm, cap, exposure }.
 */
export function renderFront(p, plate, n, opts = {}) {
  const { lit = true, pxPerMm = 8, cap = 'gold' } = opts;
  const ext = opts.extent || extentFor(p);
  const w = Math.round((ext.x1 - ext.x0) * pxPerMm), h = Math.round((ext.y1 - ext.y0) * pxPerMm);
  const fill = fillProfile(p);
  const a = rad(p.shoulderDeg), ta = Math.tan(a);
  const yt = (p.R + p.tShoulder) * Math.sin(a), rt = (p.R + p.tShoulder) * Math.cos(a);
  const ref = refIrradiance(p), yWhite = luminance(COMMON.tMin);
  const { c } = axes(p);
  const cosAlpha = Math.cos(rad(p.alphaDeg));
  const N = w * h;
  const inside = new Uint8Array(N), onBall = new Uint8Array(N), pic = new Uint8Array(N);
  const tMap = new Float32Array(N), lin = new Float32Array(3 * N), nrm = new Float32Array(3 * N);
  for (let j = 0; j < h; j++) {
    const Y = ext.y1 - (j + 0.5) / pxPerMm;
    let r;
    if (Y > p.yRim) r = 0;
    else if (Y > yt) r = Math.max(rt - (Y - yt) * ta, p.rCollar);
    else {
      const Ro = p.R + fill(Math.asin(clamp(Y / (p.R + 2), -1, 1)));
      r = Math.sqrt(Math.max(Ro * Ro - Y * Y, 0));
    }
    for (let i = 0; i < w; i++) {
      const X = ext.x0 + (i + 0.5) / pxPerMm, q = j * w + i;
      if (!(Math.abs(X) < r)) continue;
      inside[q] = 1;
      const Z = Math.sqrt(Math.max(r * r - X * X, 0));
      let nx, ny, nz, t;
      if (Y <= yt) {
        const len = Math.hypot(X, Y, Z) || 1;
        nx = X / len; ny = Y / len; nz = Z / len;
        t = wallThickness(p, plate, n, fill, nx, ny, nz);
        onBall[q] = 1;
        if (nx * c[0] + ny * c[1] + nz * c[2] >= cosAlpha) pic[q] = 1;
      } else {
        const rr = Math.max(r, 1e-6);
        nx = (Math.cos(a) * X) / rr; ny = Math.sin(a); nz = (Math.cos(a) * Z) / rr;
        t = p.tShoulder;
      }
      tMap[q] = t;
      nrm[3 * q] = nx; nrm[3 * q + 1] = ny; nrm[3 * q + 2] = nz;
      const g = irradiance(p, X - nx * t, Y - ny * t, Z - nz * t, nx, ny, nz) / ref;
      for (let k = 0; k < 3; k++) lin[3 * q + k] = ((g * Math.exp(-t * COMMON.absorb[k])) / yWhite) * COMMON.led[k];
    }
  }
  const rgb = new Float32Array(3 * N);
  let exposure = opts.exposure;
  if (lit) {
    if (exposure == null) {
      const vals = [];
      for (let q = 0; q < N; q++) if (pic[q]) vals.push(Math.max(lin[3 * q], lin[3 * q + 1], lin[3 * q + 2]));
      exposure = 0.95 / Math.max(percentile(vals, 99.5), 1e-6);
    }
    for (let q = 0; q < N; q++) {
      for (let k = 0; k < 3; k++) rgb[3 * q + k] = inside[q] ? lin[3 * q + k] * exposure : [0.012, 0.014, 0.03][k];
    }
  } else {
    // room light from the upper left; the relief, softened, tilts the normal
    const src = new Float32Array(N);
    for (let q = 0; q < N; q++) src[q] = onBall[q] ? tMap[q] : p.tShoulder;
    const bl = gaussianBlur(src, w, h, 0.25 * pxPerMm);
    let sx = -0.45, sy = 0.55, sz = 0.7;
    const sl = Math.hypot(sx, sy, sz); sx /= sl; sy /= sl; sz /= sl;
    for (let j = 0; j < h; j++) {
      for (let i = 0; i < w; i++) {
        const q = j * w + i;
        if (!inside[q]) { rgb[3 * q] = 0.3; rgb[3 * q + 1] = 0.3; rgb[3 * q + 2] = 0.31; continue; }
        const gx = (i === 0 ? bl[q + 1] - bl[q] : i === w - 1 ? bl[q] - bl[q - 1] : (bl[q + 1] - bl[q - 1]) / 2) * pxPerMm;
        const gy = (j === 0 ? bl[q + w] - bl[q] : j === h - 1 ? bl[q] - bl[q - w] : (bl[q + w] - bl[q - w]) / 2) * pxPerMm;
        let nx = nrm[3 * q] - gx * 0.35, ny = nrm[3 * q + 1] + gy * 0.35, nz = nrm[3 * q + 2];
        const nl = Math.hypot(nx, ny, nz) || 1;
        const shade = 0.22 + 0.78 * clamp((nx * sx + ny * sy + nz * sz) / nl, 0, 1);
        rgb[3 * q] = 0.8 * shade; rgb[3 * q + 1] = 0.79 * shade; rgb[3 * q + 2] = 0.77 * shade;
      }
    }
  }
  if (cap) drawCap(p, rgb, w, h, ext, pxPerMm, lit, CAP_COLOURS[cap] || cap);
  for (let i = 0; i < 3 * N; i++) rgb[i] = clamp(linearToSrgb(rgb[i]), 0, 1);
  return { rgb, w, h, exposure };
}

function drawCap(p, rgb, w, h, ext, pxPerMm, lit, hex) {
  const gold = hexToLinear(hex);
  const { rSkirtOut: rso, skirtH, fingers } = p.cap;
  const yLo = p.yRim - skirtH, yHi = p.yRim + COMMON.plateT, yCh = yHi - COMMON.chamfer;
  let sx = -0.45, sy = 0.35, sz = 0.82;
  const sl = Math.hypot(sx, sy, sz); sx /= sl; sy /= sl; sz /= sl;
  let hx = sx, hy = sy, hz = sz + 1;
  const hl = Math.hypot(hx, hy, hz); hx /= hl; hy /= hl; hz /= hl;
  const k = lit ? 0.1 : 1;
  const slits = [];
  for (let f = 0; f < fingers; f++) {
    const th = rad((360 * (f + 0.5)) / fingers) - Math.PI / 2;
    if (Math.cos(th) > 0.05) slits.push([Math.asin(Math.sin(th)), Math.cos(th)]);
  }
  const wire = [0.01, 0.035, 0.015].map((v) => v * (lit ? 1 : 3));
  for (let j = 0; j < h; j++) {
    const Y = ext.y1 - (j + 0.5) / pxPerMm;
    for (let i = 0; i < w; i++) {
      const X = ext.x0 + (i + 0.5) / pxPerMm, q = 3 * (j * w + i);
      const taper = Y > yCh ? rso - (Y - yCh) : rso;
      if (Math.abs(X) <= taper && Y >= yLo && Y <= yHi) {
        const u = clamp(X / rso, -1, 1), nz = Math.sqrt(1 - u * u);
        const diff = clamp(u * sx + nz * sz, 0, 1);
        const spec = clamp(u * hx + nz * hz, 0, 1) ** 40;
        let dark = 1;
        if (Y < p.yRim) {
          const ang = Math.asin(u);
          for (const [a0, cw] of slits) if (Math.abs(ang - a0) * rso * cw < COMMON.slitW / 2) { dark = 0.25; break; }
        }
        for (let c = 0; c < 3; c++) rgb[q + c] = (gold[c] * (0.18 + 0.82 * diff) * k + spec * 0.9 * k) * dark;
        continue;
      }
      const above = Y - yHi - 4;
      if ((Math.abs(X) <= p.socketD / 2 && Y > yHi && Y <= yHi + 4)
        || (above > 0 && Math.abs(X - (0.8 * above ** 1.3) / 6) <= 1.1)) {
        for (let c = 0; c < 3; c++) rgb[q + c] = wire[c];
      }
    }
  }
}

// ---------------------------------------------------------------------------------------------------
// In the browser

const PLATE_PX = (p) => Math.round((2 * p.R * Math.sin(rad(p.alphaDeg))) / COMMON.pitch) + 1;

/** Lightness statistics of the toned photo inside its circle, for the configurator's warning. */
export function checkLuma(luma, n) {
  const ys = [];
  const r = (n - 1) / 2;
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) if ((x - r) ** 2 + (y - r) ** 2 <= r * r) ys.push(luma[y * n + x]);
  const mean = ys.reduce((s, v) => s + v, 0) / ys.length;
  const spread = percentile(ys, 90) - percentile(ys, 10);
  const shadows = ys.filter((v) => v < 0.12).length / ys.length;
  return { mean, spread, shadows, dark: mean < 0.3 || shadows > 0.35, flat: spread < 0.35 };
}

async function toSource(photo) {
  if (photo instanceof Blob) return createImageBitmap(photo);
  if (photo instanceof HTMLImageElement && !photo.complete) await photo.decode();
  return photo;
}

/**
 * A live preview on `canvas`. Options: light ('mini' | 'c7' | 'c9'), cap ('gold' | 'silver'), lit (true).
 * The canvas is drawn at its CSS width times the device pixel ratio (at most 2), so it stays sharp on phones.
 */
export function createOrnamentPreview(canvas, options = {}) {
  const state = { light: 'mini', cap: 'gold', lit: true, ...options };
  let source = null, crop = null, luma = null, plate = null, n = 0, plateFor = '';

  function cropBox() {
    const W = source.width, H = source.height;
    if (crop) return [crop.x * W, crop.y * H, crop.w * W, crop.h * H];
    const s = Math.min(W, H);
    return [(W - s) / 2, (H - s) / 2, s, s];
  }

  function prepare() {
    const p = PARAMS[state.light];
    n = PLATE_PX(p);
    const off = document.createElement('canvas');
    off.width = off.height = n;
    const ctx = off.getContext('2d', { willReadFrequently: true });
    ctx.imageSmoothingQuality = 'high';
    const [sx, sy, sw, sh] = cropBox();
    ctx.drawImage(source, sx, sy, sw, sh, 0, 0, n, n);
    const px = ctx.getImageData(0, 0, n, n).data;
    const rgb = new Float32Array(n * n * 3), keep = new Float32Array(n * n);
    const r = (n - 1) / 2;
    for (let i = 0; i < n * n; i++) {
      rgb[3 * i] = px[4 * i] / 255; rgb[3 * i + 1] = px[4 * i + 1] / 255; rgb[3 * i + 2] = px[4 * i + 2] / 255;
      const x = i % n, y = (i / n) | 0;
      keep[i] = (x - r) ** 2 + (y - r) ** 2 <= r * r ? 1 : 0;
    }
    luma = tone(rgb, keep, n);
    plate = solvePlate(luma, n, p);
    plateFor = state.light;
  }

  // { draft: true } draws at half resolution, for while a finger is moving the photo.
  function render(how = {}) {
    if (!source) return;
    if (!plate || plateFor !== state.light) prepare();
    const p = PARAMS[state.light];
    const ext = extentFor(p);
    const css = canvas.clientWidth || canvas.width;
    const dpr = Math.min(window.devicePixelRatio || 1, 2) * (how.draft ? 0.5 : 1);
    const pxPerMm = (css * dpr) / (ext.x1 - ext.x0);
    const out = renderFront(p, plate, n, { lit: state.lit, cap: state.cap, pxPerMm, extent: ext });
    canvas.width = out.w;
    canvas.height = out.h;
    const ctx = canvas.getContext('2d');
    const img = ctx.createImageData(out.w, out.h);
    for (let i = 0; i < out.w * out.h; i++) {
      img.data[4 * i] = Math.round(out.rgb[3 * i] * 255);
      img.data[4 * i + 1] = Math.round(out.rgb[3 * i + 1] * 255);
      img.data[4 * i + 2] = Math.round(out.rgb[3 * i + 2] * 255);
      img.data[4 * i + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
  }

  return {
    async setPhoto(photo) { source = await toSource(photo); crop = null; plate = null; render(); },
    setCrop(c, how) { crop = c; plate = null; render(how); },
    set(changes, how) {
      Object.assign(state, changes);
      render(how);
    },
    get state() { return { ...state, crop }; },
    /** The photo's size in pixels, once set. */
    get photoSize() { return source ? { width: source.width, height: source.height } : null; },
    /** Where the photo's circle sits on the canvas, as fractions of its width: { cx, cy, d }. */
    get circle() {
      const p = PARAMS[state.light], e = extentFor(p), wmm = e.x1 - e.x0;
      const tl = rad(p.tiltDeg);
      return { cx: -e.x0 / wmm, cy: (e.y1 - p.R * Math.sin(tl)) / wmm, d: (2 * p.R * Math.sin(rad(p.alphaDeg))) / wmm };
    },
    check() { if (!luma) return null; return checkLuma(luma, n); },
    toBlob(type = 'image/jpeg', quality = 0.9) { return new Promise((res) => canvas.toBlob(res, type, quality)); },
    render,
  };
}
