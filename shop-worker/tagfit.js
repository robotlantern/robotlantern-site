// nametag.tag_fit() without fonts (tools/ornament/nametag.py has the rule). tag-metrics.json holds each
// allowed character's advance and outline bounds, measured from the font files by tools/orders/tag_metrics.py.
// The text's box is the union of its glyphs' boxes, moved along by the advances plus 0.08 em of tracking.

import metrics from './tag-metrics.json';

export const FONTS = Object.keys(metrics.fonts);

export function tagFit(text, font, artW = metrics.rule.artW) {
  const r = metrics.rule;
  const f = metrics.fonts[font];
  if (!f) return { fits: false, textMm: 0, reason: `there's no font ${font}` };
  const gone = [...new Set([...text].filter((ch) => ch !== ' ' && !f.glyphs[ch]))];
  if (gone.length) return { fits: false, textMm: 0, reason: `the font has no ${gone.join(' ')}` };
  let x = 0;
  let box = null;
  for (const ch of text) {
    const [advance, b] = f.glyphs[ch];
    if (b) {
      const g = [x + b[0], b[1], x + b[2], b[3]];
      box = box ? [Math.min(box[0], g[0]), Math.min(box[1], g[1]), Math.max(box[2], g[2]), Math.max(box[3], g[3])] : g;
    }
    x += advance + r.track * f.upm;
  }
  if (!box) return { fits: false, textMm: 0, reason: 'there are no letters' };
  const tagW = Math.min(r.maxTagW, Math.max(r.minTagW, r.share * artW));
  const boxW = tagW - 2 * r.padX;
  const boxH = r.tagH - r.padBottom - r.padTop;
  const w = box[2] - box[0];
  const h = box[3] - box[1];
  const mm = Math.min(boxW / w, boxH / h, r.maxTextH / h) * h;
  const textMm = Math.round(mm * 100) / 100;
  if (mm < r.minTextH) return { fits: false, textMm, reason: `it's too long for the tag in this font` };
  return { fits: true, textMm };
}

export const CASES = metrics.cases;
