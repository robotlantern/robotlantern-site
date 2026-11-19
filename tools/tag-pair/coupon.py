"""Secret Santa tag pair: test piece (2026-11-19).

    PY=~/work/lab/lithophane-maker/.venv/bin/python
    $PY tools/tag-pair/coupon.py OUT_DIR

Two gift tags printed as one piece, one colour, stacked. The bottom tag's top face carries the secret
("TO: SALLY", raised), and the top tag's top face says who it's from. Between them is an air gap,
held by narrow pillars that taper to a small tip where they touch the top tag, so they snap off there.
An optional seam wall, one extrusion line thick, runs round the outline and the string hole. It
closes the gap so nobody can peek, and it tears open like an envelope.

Four pairs on one plate, each changing one thing:
    A  gap 0.6, tip 0.8, seam,    tags 1.2 mm
    B  gap 0.8, tip 0.8, seam,    tags 1.2 mm
    C  gap 1.0, tip 0.6, no seam, tags 1.2 mm
    D  gap 0.8, tip 0.8, seam,    tags 2.0 mm   (held to a lamp: does the name show through?)
v1 result: A, B and D sealed solid, and C (no seam) fell apart; nothing showed through against a lamp.
    E  (v2, printed alone) C, but the hidden name is raised one layer and has one layer of air above it,
       so the pillars are 0.4 mm tall. Pillars also go near the left and right edges.
"gap" is the air between the tops of the hidden letters and the top tag's underside.
    $PY tools/tag-pair/coupon.py OUT_DIR E      # only some variants
Writes pair-<X>.stl for each. Dimensions are multiples of 0.2 mm layers.
"""
from __future__ import annotations

import sys
from pathlib import Path

import manifold3d as m3
import numpy as np
import trimesh
from shapely import affinity
from shapely.geometry import Point, box
from shapely.geometry.polygon import orient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'qr-ornament'))
import snowflake as sf  # noqa: E402  (text_geom)

W, H, R = 50.0, 28.0, 4.0
HOLE = (6.0, H / 2, 2.25)
EMBOSS = 0.6
PILLAR_D, TIP_H = 1.6, 0.8
SEAM_W = 0.45
VARIANTS = {
    'A': dict(gap=0.6, tip=0.8, seam=True, t=1.2),
    'B': dict(gap=0.8, tip=0.8, seam=True, t=1.2),
    'C': dict(gap=1.0, tip=0.6, seam=False, t=1.2),
    'D': dict(gap=0.8, tip=0.8, seam=True, t=2.0),
    'E': dict(gap=0.2, tip=0.6, seam=False, t=1.2, emboss=0.2, tip_h=0.4,
              extra=[(1.8, H / 2), (W - 1.6, 8.0), (W - 1.6, H / 2), (W - 1.6, H - 8.0)]),
}


def extrude(poly, h, z=0.0):
    polys = [poly] if poly.geom_type == 'Polygon' else list(poly.geoms)
    acc = None
    for p in polys:
        p = orient(p, 1.0)
        cs = m3.CrossSection([np.asarray(p.exterior.coords)[:-1].tolist()] +
                             [np.asarray(r.coords)[:-1].tolist() for r in p.interiors])
        e = cs.extrude(h).translate([0, 0, z])
        acc = e if acc is None else acc + e
    return acc


def label(text, x0, x1, cap):
    """Text (y up) fitted into x0..x1, centred on the tag's middle line."""
    g = affinity.scale(sf.text_geom(text, cap), 1, -1, origin=(0, 0))
    w, h = g.bounds[2] - g.bounds[0], g.bounds[3] - g.bounds[1]
    s = min(1.0, (x1 - x0) / w)
    g = affinity.scale(g, s, s, origin=(0, 0))
    w, h = w * s, h * s
    minx, miny = g.bounds[0], g.bounds[1]
    return affinity.translate(g, x0 + (x1 - x0 - w) / 2 - minx, H / 2 - h / 2 - miny)


def pair(v):
    t, gap, tip = v['t'], v['gap'], v['tip']
    outline = box(0, 0, W, H).buffer(-R, join_style=2).buffer(R, 32)
    hole = Point(HOLE[0], HOLE[1]).buffer(HOLE[2], 48)
    tag = outline.difference(hole)
    emboss, tip_h = v.get('emboss', EMBOSS), v.get('tip_h', TIP_H)
    z0 = t + emboss + gap                      # underside of the top tag
    body = extrude(tag, t)                                                     # bottom tag
    body = body + extrude(label('TO: SALLY', 12, W - 3, 7.0), emboss + 0.02, t - 0.02)   # the secret
    body = body + extrude(tag, t, z0)                                          # top tag
    body = body + extrude(label(f'FROM: {v["name"]}', 12, W - 3, 7.0), EMBOSS + 0.02, z0 + t - 0.02)
    # pillars in the margins, tapering to the tip where they meet the top tag
    xs = [13.0, 21.5, 30.0, 38.5, 47.0]
    pts = [(x, 2.6) for x in xs] + [(x, H - 2.6) for x in xs] + [(2.8, 5.0), (2.8, H - 5.0)] + v.get('extra', [])
    for x, y in pts:
        stem_h = z0 - tip_h - t
        if stem_h > 0:
            body = body + m3.Manifold.cylinder(stem_h + 0.02, PILLAR_D / 2, PILLAR_D / 2, 32).translate([x, y, t - 0.02])
        cone = m3.Manifold.cylinder(tip_h + 0.05 + (0.02 if stem_h <= 0 else 0), PILLAR_D / 2, tip / 2, 32)
        body = body + cone.translate([x, y, z0 - tip_h - (0.02 if stem_h <= 0 else 0)])
    if v['seam']:
        seam = outline.difference(outline.buffer(-SEAM_W, join_style=2))
        seam = seam.union(hole.buffer(SEAM_W, 48).difference(hole))
        body = body + extrude(seam, z0 - t + 0.04, t - 0.02)
    mesh = body.to_mesh()
    tm = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))
    return tm, outline


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    report = {}
    pick = sys.argv[2:] or list(VARIANTS)
    for name, v in ((k, VARIANTS[k]) for k in pick):
        tm, _ = pair({**v, 'name': name})
        parts = [b for b in tm.split(only_watertight=False) if abs(b.volume) > 1.0]
        tm = trimesh.util.concatenate(parts)
        tm.export(out / f'pair-{name}.stl')
        report[name] = dict(v, watertight=bool(tm.is_watertight), bodies=len(parts),
                            height=round(float(tm.bounds[1][2]), 2), volume_cm3=round(tm.volume / 1000, 2))
        print(name, report[name])
    return report


if __name__ == '__main__':
    main()
