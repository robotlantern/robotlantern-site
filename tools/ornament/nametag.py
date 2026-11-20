"""Text as shapely polygons from a font file, fitted into a box: build.py's name tag, and tag_fit(), the test
the page and the routine run on tag text before checkout."""
from functools import lru_cache
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity

# The five Google Fonts stencil faces (OFL), shared with the product page: public/shop/fonts/ (docs/ORDERS.md, "Modules")
FONTS = Path(__file__).resolve().parents[2] / 'public/shop/fonts'
# key -> (file, variable-font axes)
STENCILS = {
    'allerta':        ('allerta-stencil.ttf', None),
    'saira':          ('saira-stencil-one.ttf', None),
    'big-shoulders':  ('big-shoulders-stencil.ttf', {'wght': 800, 'opsz': 72}),
    'emblema':        ('emblema-one.ttf', None),
    'wallpoet':       ('wallpoet.ttf', None),
}


class _Flat(BasePen):
    def __init__(self, gs, steps=8):
        super().__init__(gs); self.rings, self.cur, self.n = [], [], steps
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, self.n + 1):
            t = i / self.n; u = 1 - t
            self.cur.append(tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d
                                  for a, b, c, d in zip(p0, p1, p2, p3)))
    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for i in range(1, self.n + 1):
            t = i / self.n; u = 1 - t
            self.cur.append(tuple(u * u * a + 2 * u * t * b + t * t * c for a, b, c in zip(p0, p1, p2)))
    def _closePath(self):
        if len(self.cur) > 2: self.rings.append(self.cur)
        self.cur = []
    _endPath = _closePath


@lru_cache(maxsize=None)
def _font(name):
    f, axes = STENCILS[name]
    font = TTFont(FONTS / f)
    if axes:
        from fontTools.varLib import instancer
        font = instancer.instantiateVariableFont(font, axes)
    return font


def text_poly(text, font_name, track=None):
    """Text outline in font units, baseline at y=0, even-odd fill."""
    track = TRACK if track is None else track
    font = _font(font_name)
    cmap, gs, hmtx = font.getBestCmap(), font.getGlyphSet(), font['hmtx']
    x, shapes = 0, []
    for ch in text:
        g = cmap.get(ord(ch))
        if g is None: continue
        pen = _Flat(gs); gs[g].draw(pen)
        rings = [Polygon([(px + x, py) for px, py in r]).buffer(0) for r in pen.rings]
        glyph = Polygon()
        for r in sorted(rings, key=lambda p: -p.area):     # even-odd: xor the rings
            glyph = glyph.symmetric_difference(r)
        shapes.append(glyph)
        x += hmtx[g][0] + track * font['head'].unitsPerEm
    return unary_union(shapes)


# The tag (docs/ORDERS.md, "The product file", "text"). build.py draws it with these; tag_fit() is the test the
# page and the routine run before checkout. All lengths in mm.
TAG_H = 17.0                    # visible tag height below the art
TAG_SHARE = 0.8                 # tag width as a share of the art's width...
MIN_TAG_W, MAX_TAG_W = 64.0, 72.0   # ...clamped to this, however narrow or wide the art
PAD_X, PAD_BOTTOM, PAD_TOP = 3.5, 3.0, 1.5   # text box inside the tag
MIN_TEXT_H, MAX_TEXT_H = 5.0, 11.0
TRACK = 0.08                    # letter spacing added to each advance, in em


def tag_width(art_w, share=TAG_SHARE):
    """Tag width for art art_w mm wide. With the default 80 mm art box it is always 64."""
    return min(MAX_TAG_W, max(MIN_TAG_W, share * art_w))


def text_box(tag_w, tag_h=TAG_H):
    """(width, height) of the box the text is fitted into."""
    return tag_w - 2 * PAD_X, tag_h - PAD_BOTTOM - PAD_TOP


def _size(bounds, box_w, box_h, max_h):
    """Scale for text with outline bounds (font units) into box_w x box_h, no taller than max_h."""
    tx0, ty0, tx1, ty1 = bounds
    return min(box_w / (tx1 - tx0), box_h / (ty1 - ty0), max_h / (ty1 - ty0))


def missing(text, font_name):
    """Characters of text that font_name has no glyph for (spaces aside)."""
    cmap = _font(font_name).getBestCmap()
    return sorted({ch for ch in text if ch != ' ' and ord(ch) not in cmap})


def tag_fit(text, font_name, art_w=80.0, tag_h=TAG_H, share=TAG_SHARE):
    """Does text fit the name tag in this font? Returns {'fits', 'text_mm', 'tag_w', 'reason'}.

    The rule, which the page mirrors with the same font files:
      1. Lay the text out with the font's glyph outlines, each glyph advanced by its advance width plus
         TRACK (0.08) em. Take the bounding box of the outlines (w x h, font units), descenders included.
      2. The tag is tag_width(art_w) wide: 0.8 x the art's width, clamped to 64-72 mm (64 for any art
         up to 80 mm wide). The text box is that width less 2 x 3.5 mm, by 17 - 3 - 1.5 = 12.5 mm.
      3. Scale the text uniformly to the largest size that fits the box and is at most 11 mm tall.
      4. It fits if the scaled text is at least 5 mm tall (text_mm >= MIN_TEXT_H) and the font has every
         character. Empty text doesn't fit.
    """
    tag_w = tag_width(art_w, share)
    r = dict(fits=False, text_mm=0.0, tag_w=round(tag_w, 1), reason=None)
    gone = missing(text, font_name)
    if gone:
        r['reason'] = f"no glyph for {' '.join(gone)} in {font_name}"
        return r
    t = text_poly(text, font_name)
    if t.is_empty:
        r['reason'] = 'no glyphs'
        return r
    bw, bh = text_box(tag_w, tag_h)
    b = t.bounds
    h = _size(b, bw, bh, MAX_TEXT_H) * (b[3] - b[1])
    r['text_mm'] = round(h, 2)
    if h < MIN_TEXT_H:
        r['reason'] = f'text {h:.1f} mm tall, under {MIN_TEXT_H} mm: too long'
    else:
        r['fits'] = True
    return r


def fit(text, font_name, box, max_h, min_h):
    """Fit text into box (shapely polygon, mm); cap height between min_h and max_h. Returns (poly, cap_mm, warn).
    The same sizing as tag_fit(), which is the test to call before building."""
    gone = missing(text, font_name)
    t = text_poly(text, font_name)
    if t.is_empty: return t, 0, 'no glyphs'
    bx0, by0, bx1, by1 = box.bounds
    tx0, ty0, tx1, ty1 = t.bounds
    s = _size(t.bounds, bx1 - bx0, by1 - by0, max_h)
    cap = s * (ty1 - ty0); warn = None
    if cap < min_h: warn = f'text {cap:.1f} mm tall, under {min_h} mm: too long'
    if gone: warn = f"no glyph for {' '.join(gone)} in {font_name}"
    t = affinity.scale(t, s, s, origin=(0, 0))
    tx0, ty0, tx1, ty1 = t.bounds
    t = affinity.translate(t, (bx0 + bx1) / 2 - (tx0 + tx1) / 2, (by0 + by1) / 2 - (ty0 + ty1) / 2)
    return t, cap, warn
