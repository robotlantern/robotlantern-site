"""The builder's first steps on a drawing, with no meshes: ink, scale, cleanup, bridges and "white kept".

build.py runs these to make the stencil sheet. The upload check (the page mirrors it, and the routine can
call it) runs the same code through check_drawing():

    from drawing import check_drawing
    check_drawing('drawing.png')  # -> {'ok', 'problems', 'art_mm', 'pieces', 'bridges_mm', 'max_bridge_mm',
                                  #     'white_kept', 'white_mm2', ...}

The rules, in order (docs/ORDERS.md, "The recipe" and "Own drawings"):
  ink        any pixel more than 120 (RGB distance) from white
  scale      the ink's bounding box fits a box, 80 mm wide x 85 mm tall by default
  cleanup    drop ink islands under 2 mm2; fatten ink thinner than 1 mm; fill white gaps thinner than 1 mm;
             widen connecting necks thinner than 1.8 mm
  bridges    join every island to the main piece by its shortest path, 1.8 mm wide; over 3 mm fails
  white kept cut-out area in the proof / cut-out area in the drawing (white enclosed by ink, the tag left
             out); under 0.8 fails, because the cleanup has filled in features the customer saw
"""
from __future__ import annotations

import numpy as np, cv2
from PIL import Image
from scipy import ndimage as nd
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity

DEFAULTS = dict(width=80.0, height=85.0, min_line=1.0, min_gap=1.0, neck=1.8, bridge=1.8, speck=2.0,
                ink=120, max_bridge=3.0, min_white_kept=0.8)
PAD = 40   # px of white kept round the ink after cropping


def ink_mask(png, ink=DEFAULTS['ink']):
    """Ink as a bool array, cropped to the ink with PAD px of white round it. png is a path or a PIL image."""
    im = np.asarray((png if isinstance(png, Image.Image) else Image.open(png)).convert('RGB')).astype(int)
    red = np.pad(np.linalg.norm(im - 255, axis=2) > ink, 60)
    ys, xs = np.nonzero(red)
    if not len(xs):
        raise ValueError('no ink in the drawing')
    return red[ys.min() - PAD:ys.max() + PAD, xs.min() - PAD:xs.max() + PAD]


def scale(red, width=DEFAULTS['width'], height=DEFAULTS['height']):
    """mm per px, so the ink's bounding box fits width x height mm."""
    ys, xs = np.nonzero(red)
    return min(width / (xs.max() - xs.min() + 1), height / (ys.max() - ys.min() + 1))


def _disk(mm, s):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * max(1, round(mm / 2 / s)) + 1,) * 2)


def cleanup(red, s, min_line, min_gap, neck, speck):
    """Step 1: drop specks, fatten thin ink, fill thin white cuts, widen necks. Returns (red, log)."""
    log = {}
    lab, n = nd.label(red, np.ones((3, 3)))
    area = nd.sum(red, lab, range(1, n + 1)) * s * s
    red = np.isin(lab, [i + 1 for i in range(n) if area[i] >= speck])
    log['specks_dropped'] = int(sum(area < speck))
    r8 = red.astype(np.uint8)
    thin = red & ~cv2.morphologyEx(r8, cv2.MORPH_OPEN, _disk(min_line, s)).astype(bool)
    red = red | cv2.dilate(thin.astype(np.uint8), _disk(min_line * 0.6, s)).astype(bool)
    log['thin_red_mm2'] = round(float(thin.sum() * s * s), 1)
    before = red.sum()
    red = cv2.morphologyEx(red.astype(np.uint8), cv2.MORPH_CLOSE, _disk(min_gap, s)).astype(bool)
    log['thin_gaps_filled_mm2'] = round(float((red.sum() - before) * s * s), 1)

    # 1b. thicken necks: a strip narrower than `neck` that is the only thing holding two wide parts together
    # (a 1 mm one nearly broke on the first print). Dead-end tips touch one part only and are left as drawn.
    necks = []
    if neck > 0:
        wide = cv2.morphologyEx(red.astype(np.uint8), cv2.MORPH_OPEN, _disk(neck, s)).astype(bool)
        wlab, _ = nd.label(wide, np.ones((3, 3)))
        clab, cn = nd.label(red & ~wide, np.ones((3, 3)))
        edt = nd.distance_transform_edt(red)
        grow = np.zeros_like(red)
        for i in range(1, cn + 1):
            c = clab == i
            touch = np.unique(wlab[cv2.dilate(c.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)])
            if len(touch[touch > 0]) < 2: continue
            w = 2 * edt[c].max() * s                      # neck width, mm
            r = max(1, round((neck - w) / 2 / s) + 1)
            grow |= cv2.dilate(c.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1,) * 2)).astype(bool)
            necks.append(round(float(w), 2))
        red = red | grow
    log['necks_widened_mm'] = necks
    return red, log


def bridge(red, s, width):
    """Step 2: bridge every island to the main sheet by its shortest path. Returns (red, pieces, bridges_mm)."""
    bridges, pieces = [], None
    while True:
        lab, n = nd.label(red, np.ones((3, 3)))
        if pieces is None: pieces = int(n)
        if n <= 1: break
        sizes = nd.sum(red, lab, range(1, n + 1)); main = np.argmax(sizes) + 1
        dist, (iy, ix) = nd.distance_transform_edt(lab != main, return_indices=True)
        best = None
        for i in range(1, n + 1):
            if i == main: continue
            d = np.where(lab == i, dist, np.inf); p = np.unravel_index(np.argmin(d), d.shape)
            if best is None or d[p] < best[0]: best = (d[p], p, (iy[p], ix[p]))
        _, (y0, x0), (y1, x1) = best
        m = red.astype(np.uint8)
        cv2.line(m, (int(x0), int(y0)), (int(x1), int(y1)), 1, max(2, round(width / s)))
        red = m.astype(bool); bridges.append(round(float(best[0] * s), 2))
    return red, pieces, bridges


def polys(mask, s, blur=1.2):
    """A pixel mask as shapely polygons in mm, y up."""
    m = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), blur) > 0.5
    cs, hier = cv2.findContours(m.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    ps = []
    for j, c in enumerate(cs):
        if hier[0][j][3] != -1 or len(c) < 4: continue
        holes = [cs[h][:, 0] for h in range(len(cs)) if hier[0][h][3] == j and len(cs[h]) >= 4]
        ps.append(Polygon(c[:, 0], holes).buffer(0))
    g = unary_union(ps).simplify(0.6)
    return affinity.scale(g, s, -s, origin=(0, 0))   # mm, y up


def drop_small(g, area):
    """g without the polygons smaller than `area` mm2. Vectorising a bridged sheet can leave a few-pixel
    fleck inside a hole (agents-01 v2 and v4: 0.003 mm2), which read as a loose piece of the tag."""
    if g.geom_type == 'Polygon':
        return g
    keep = [p for p in g.geoms if p.area >= area]
    if len(keep) == len(g.geoms):
        return g
    return keep[0] if len(keep) == 1 else unary_union(keep)


def unpinch(g, width):
    """g with ink added where two of its rings touch at a point: there the ink between two cut-outs (or a
    cut-out and the outside) has narrowed to nothing after vectorising. Shapely calls that valid, but the
    extruded mesh is not one watertight body (agents-01 v5 h1: "STENCIL IS NOT ONE PIECE" and "MESH NOT
    WATERTIGHT"). Adds a `width` mm disk at each touch point, inside the outline. Returns (g, points)."""
    from shapely import STRtree
    from shapely.geometry import Point
    pts = []
    parts = list(getattr(g, 'geoms', [g]))
    for p in parts:
        rings = [p.exterior, *p.interiors]
        tree = STRtree(rings)
        for i, r in enumerate(rings):
            for j in tree.query(r):
                if j <= i: continue
                x = r.intersection(rings[j])
                if not x.is_empty:
                    pts += [q.representative_point() for q in getattr(x, 'geoms', [x])]
    if not pts:
        return g, []
    fill = unary_union([Polygon(p.exterior) for p in parts])
    g = unary_union([g, *[Point(q.x, q.y).buffer(width / 2, 16) for q in pts]]).intersection(fill)
    return g, [[round(q.x, 1), round(q.y, 1)] for q in pts]


def sheet_and_silhouette(red, s, speck):
    """The stencil sheet (ink with its cut-outs) and the silhouette (its outline, holes filled), in mm."""
    sheet = drop_small(polys(red, s), speck)
    sil = Polygon(max(sheet.geoms, key=lambda g: g.area).exterior) if sheet.geom_type == 'MultiPolygon' else Polygon(sheet.exterior)
    return sheet.intersection(sil), sil


def white_kept(red0, s, sheet, sil, k=8):
    """(drawing cut-outs mm2, proof cut-outs mm2, ratio). A cut-out is white enclosed by ink. The drawing's are
    counted on its own pixels; the sheet's are counted as the proof draws them (k px per mm, holes painted
    over the ink), which is what the 0.8 limit was set on (buildings-01). The ratio is None when the drawing
    has no cut-outs, since there is nothing to lose."""
    from PIL import ImageDraw
    drawn = float((nd.binary_fill_holes(red0) & ~red0).sum() * s * s)
    x0, y0, x1, y1 = sil.bounds
    im = Image.new('L', (int((x1 - x0) * k) + 4, int((y1 - y0) * k) + 4), 0)
    d = ImageDraw.Draw(im)
    P = lambda r: [((x - x0) * k + 2, (y1 - y) * k + 2) for x, y in r.coords]
    d.polygon(P(sil.exterior), fill=1)
    for p in getattr(sheet, 'geoms', [sheet]):
        d.polygon(P(p.exterior), fill=2)
        for r in p.interiors: d.polygon(P(r), fill=1)
    kept = float((np.asarray(im) == 1).sum() / k / k)
    return round(drawn, 1), round(kept, 1), (round(kept / drawn, 2) if drawn >= 1.0 else None)


def prepare(png, **kw):
    """Everything check_drawing measures, plus the geometry build.py goes on with."""
    p = DEFAULTS | kw
    red0 = ink_mask(png, p['ink'])
    s = scale(red0, p['width'], p['height'])
    ys, xs = np.nonzero(red0)
    red, log = cleanup(red0, s, p['min_line'], p['min_gap'], p['neck'], p['speck'])
    red, pieces, bridges = bridge(red, s, p['bridge'])
    sheet, sil = sheet_and_silhouette(red, s, p['speck'])
    drawn, kept, ratio = white_kept(red0, s, sheet, sil)
    rep = dict(art_mm=[round(float((xs.max() - xs.min() + 1) * s), 1), round(float((ys.max() - ys.min() + 1) * s), 1)],
               mm_per_px=round(float(s), 5), pieces=pieces, **log, bridges_mm=bridges,
               max_bridge_mm=max(bridges, default=0.0), white_mm2=dict(drawing=drawn, kept=kept), white_kept=ratio)
    problems = [f'bridge {b} mm > {p["max_bridge"]}' for b in bridges if b > p['max_bridge']]
    if ratio is not None and ratio < p['min_white_kept']:
        problems.append(f'white kept {ratio} < {p["min_white_kept"]}: the cleanup filled in cut-outs, so features '
                        f'in the drawing are lost (thin white lines or outline-drawn shapes)')
    rep['problems'] = problems
    rep['ok'] = not problems
    return rep, dict(s=s, red=red, sheet=sheet, sil=sil)


def check_drawing(png, **kw) -> dict:
    """The builder's cleanup and bridge measurement on one drawing, with no meshes. Keyword arguments
    override DEFAULTS. `problems` lists, in words, what would fail the build: a bridge over max_bridge, or
    white kept under min_white_kept. `pieces` is the count after cleanup, before bridging."""
    return prepare(png, **kw)[0]


if __name__ == '__main__':
    import json, sys
    for f in sys.argv[1:]:
        print(json.dumps({'file': f} | check_drawing(f)))
