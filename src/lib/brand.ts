// The brand's shapes (src/data/brand.json, extracted from RJ's design/brand/*.svg) and the
// ovaloid rule: one shape, the wordmark's rotated "o", serves as the period, the flying lantern,
// the stars on cards and in the nav, and the monogram's dot. It's never shown twice at the same
// angle: each use takes a rotation derived from its name, so it looks scattered but never changes
// between visits (docs/BRAND.md).
import brand from '../data/brand.json';

export { brand };

const [ox0, oy0, ox1, oy1] = brand.ovaloid.box;
const O = { cx: (ox0 + ox1) / 2, cy: (oy0 + oy1) / 2, size: Math.max(ox1 - ox0, oy1 - oy0) };
export const OVALOID = brand.ovaloid.d;

/** A transform that draws the ovaloid centered at (x, y), `size` across, turned `deg` degrees. */
export const ovaloidAt = (x: number, y: number, size: number, deg: number) => {
  const r = (n: number) => Math.round(n * 1000) / 1000;
  return `translate(${r(x)} ${r(y)}) rotate(${r(deg)}) scale(${r(size / O.size)}) translate(${r(-O.cx)} ${r(-O.cy)})`;
};

/** A stable, scattered-looking angle for a name (FNV-1a hash onto 0-360). */
export const turnFor = (name: string) => {
  let h = 2166136261;
  for (const c of name) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
  return ((h >>> 0) % 3600) / 10;
};

/** How the "t" halves and the period move (wordmark units) to become the monogram, which sits at
 * the wordmark's top-left corner: the collapse behind the menu button (SiteMenu.astro). In RJ's
 * monogram the t's upper half is flipped top to bottom (it reads as an r), so the hook turns over
 * about its center as it slides. Returns the hook's move, the base's move, the period's move,
 * then the hook's center. */
export const collapseFor = (w: typeof brand.twoLine) => {
  const m = brand.monogram;
  const d = (a: number[], b: number[]) => [+(b[0] - a[0]).toFixed(2), +(b[1] - a[1]).toFixed(2)];
  const [x0, y0, x1, y1] = w.t.hookBox;
  return [...d(w.t.hookBox, m.hookBox), ...d(w.t.baseBox, m.baseBox), ...d(w.periodBox, m.dotBox), +((x0 + x1) / 2).toFixed(2), +((y0 + y1) / 2).toFixed(2)].join(' ');
};

/** Where the monogram's center sits in the wordmark's drawn box (with its 4-unit padding), as
 * fractions: the menu button is centered there. */
export const monogramCenter = (w: typeof brand.twoLine, pad = 4) => {
  const m = brand.monogram;
  const x = (Math.min(m.hookBox[0], m.baseBox[0]) + m.dotBox[2]) / 2;
  const y = (m.hookBox[1] + m.baseBox[3]) / 2;
  return [(x + pad) / (w.width + pad * 2), (y + pad) / (w.height + pad * 2)];
};
