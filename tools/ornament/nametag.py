"""Text as shapely polygons from a font file, fitted into a box. Used by build.py for the name tag."""
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


def _font(name):
    f, axes = STENCILS[name]
    font = TTFont(FONTS / f)
    if axes:
        from fontTools.varLib import instancer
        font = instancer.instantiateVariableFont(font, axes)
    return font


def text_poly(text, font_name, track=0.08):
    """Text outline in font units, baseline at y=0, even-odd fill."""
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


def fit(text, font_name, box, max_h, min_h):
    """Fit text into box (shapely polygon, mm); cap height between min_h and max_h. Returns (poly, cap_mm, warn)."""
    t = text_poly(text, font_name)
    if t.is_empty: return t, 0, 'no glyphs'
    bx0, by0, bx1, by1 = box.bounds
    tx0, ty0, tx1, ty1 = t.bounds
    s = min((bx1 - bx0) / (tx1 - tx0), (by1 - by0) / (ty1 - ty0), max_h / (ty1 - ty0))
    cap = s * (ty1 - ty0); warn = None
    if cap < min_h: warn = f'text {cap:.1f} mm tall, under {min_h} mm: too long'
    t = affinity.scale(t, s, s, origin=(0, 0))
    tx0, ty0, tx1, ty1 = t.bounds
    t = affinity.translate(t, (bx0 + bx1) / 2 - (tx0 + tx1) / 2, (by0 + by1) / 2 - (ty0 + ty1) / 2)
    return t, cap, warn
