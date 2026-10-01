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

/** How the wordmark becomes the logo (the collapse, run by SiteMenu.astro), as JSON for the
 * wordmark's data-collapse: its viewBox, then each piece that flies into the tile, with its path
 * and box (wordmark units), the box it ends in (tile units, 0-100), how far it turns, and its
 * color there. The t's lower half turns 90 degrees clockwise to become the r; its upper half
 * drops to become the L; the period becomes the dot. Everything else turns into the tile. */
export const collapseFor = (w: typeof brand.twoLine, pad = 4) => {
  const t = brand.tile;
  const r2 = (b: number[]) => b.map((n) => +n.toFixed(2));
  return JSON.stringify({
    vb: [-pad, -pad, w.width + pad * 2, w.height + pad * 2],
    parts: [
      [w.t.base, r2(w.t.baseBox), r2(t.rBox), 90, '#0a0e18'],
      [w.t.hook, r2(w.t.hookBox), r2(t.lBox), 0, '#0a0e18'],
      [w.period, r2(w.periodBox), r2(t.dotBox), 0, '#f0a040'],
    ],
  });
};
