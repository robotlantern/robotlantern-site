"""Secret Santa snowflake: a one-colour QR code ornament (feasibility prototype, 2026-11-19).

    PY=~/work/lab/lithophane-maker/.venv/bin/python   # shapely, manifold3d, trimesh, cv2, segno, pyzbar
    $PY tools/qr-ornament/snowflake.py OUT_DIR --text "Your Secret Santa is Sally!" --name Sam --year 2026 \
        [--variant stencil|relief|both] [--module 2.0] [--stl]

The QR code is turned 45 degrees into a diamond, with pixel-art arms on its four sides, a hanging loop on
the top tip and a tag on the bottom tip. The giver's name and the year are debossed into the back of the
tag, mirrored so they read correctly from behind. Two single-colour variants:

- stencil: a light plate with a hole for every dark module, scanned lying on a dark surface. A QR code
  always has light regions boxed in by dark ones (the ring in each finder pattern, the alignment
  pattern, scattered data modules), and those would fall out. Every light region is tied back to the
  frame: a small disc wherever two light modules meet only at a corner, then the fewest thin bridges
  across dark modules (union-find, cheapest first). Straight bridges run along an edge of the dark
  module rather than through its centre, where scanners sample, and bridges that would cross a finder
  pattern's centre lines are avoided.
- relief: a thin backing under everything, with the dark modules standing up from it, scanned held up
  to a light (the lithophane effect). One piece with no islands and no bridges.

Outputs: plan-<variant>.png (the front, light = material/thin), report.json, and with --stl
<variant>.stl, printed face-up as modelled (the back with the debossed tag is on the bed).
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import segno
from PIL import Image, ImageDraw, ImageFont
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

FONT = Path.home() / 'work/lab/lithophane-maker/fonts/ArchivoBlack-Regular.ttf'   # SIL OFL

# A pixel-art arm, pointing up from the code's edge (row 0 is the tip). '#' is material.
ARM = ['...##...',
       '...##...',
       '##.##.##',
       '.######.',
       '...##...',
       '##.##.##',
       '.######.',
       '...##...',
       '...##...']


def qr_matrix(text, ecc='m'):
    qr = segno.make(text, error=ecc, micro=False, boost_error=False)
    m = np.array([list(r) for r in qr.matrix], dtype=bool)   # True = dark
    return m, qr.version, qr.error


# --- islands and bridges (in module units, y down, cell (r, c) spans [c, c+1] x [r, r+1]) ------------

class UF:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, a):
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        self.p[b] = a
        return True


def plan_bridges(dark, quiet, bw):
    """Light material for the stencil: returns (joints, bridges) as shapely geometry in module units of
    the padded grid, and counts. bw is the bridge width in modules."""
    n = dark.shape[0]
    N = n + 2 * quiet
    g = np.zeros((N, N), bool)
    g[quiet:quiet + n, quiet:quiet + n] = dark
    light = ~g
    idx = lambda r, c: r * N + c
    uf = UF(N * N + 1)
    FRAME = N * N
    for r in range(N):
        for c in range(N):
            if not light[r, c]:
                continue
            if r in (0, N - 1) or c in (0, N - 1):
                uf.union(FRAME, idx(r, c))
            if r + 1 < N and light[r + 1, c]:
                uf.union(idx(r, c), idx(r + 1, c))
            if c + 1 < N and light[r, c + 1]:
                uf.union(idx(r, c), idx(r, c + 1))
    # corner joints: light cells meeting only at a corner get a disc, for strength and to avoid a
    # zero-width neck; always added
    joints = []
    for r in range(N - 1):
        for c in range(N - 1):
            a, b, cc, d = light[r, c], light[r, c + 1], light[r + 1, c], light[r + 1, c + 1]
            if (a and d and not b and not cc) or (b and cc and not a and not d):
                joints.append(Point(c + 1, r + 1).buffer(bw * 0.6, 16))
                if a and d:
                    uf.union(idx(r, c), idx(r + 1, c + 1))
                else:
                    uf.union(idx(r, c + 1), idx(r + 1, c))
    # finder centre lines (padded coords): bridges there break the 1:1:3:1:1 stripe pattern
    f_lines = set()
    for (r0, c0) in [(quiet, quiet), (quiet, quiet + n - 7), (quiet + n - 7, quiet)]:
        for k in range(7):
            f_lines.add(('row', r0 + 3, c0 + k))
            f_lines.add(('col', r0 + k, c0 + 3))
    in_finder = lambda r, c: any(r0 - 1 <= r <= r0 + 7 and c0 - 1 <= c <= c0 + 7 for (r0, c0) in
                                 [(quiet, quiet), (quiet, quiet + n - 7), (quiet + n - 7, quiet)])
    cands = []
    for r in range(1, N - 1):
        for c in range(1, N - 1):
            if light[r, c]:
                continue
            on_centre = ('row', r, c) in f_lines or ('col', r, c) in f_lines
            pen = 10 if on_centre else 0
            # horizontal: across a dark cell between light left and right, along its top or bottom edge
            if light[r, c - 1] and light[r, c + 1]:
                y0 = r if light[r - 1, c] or not light[r + 1, c] else r + 1 - bw
                cands.append((1 + pen, idx(r, c - 1), idx(r, c + 1), box(c - 0.05, y0, c + 1.05, y0 + bw)))
            if light[r - 1, c] and light[r + 1, c]:
                x0 = c if light[r, c - 1] or not light[r, c + 1] else c + 1 - bw
                cands.append((1 + pen, idx(r - 1, c), idx(r + 1, c), box(x0, r - 0.05, x0 + bw, r + 1.05)))
            # diagonal through the dark cell (used for the finder rings' corners)
            for (dr, dc) in [(1, 1), (1, -1)]:
                if light[r - dr, c - dc] and light[r + dr, c + dc]:
                    p0 = (c + (0 if dc > 0 else 1), r)
                    p1 = (c + (1 if dc > 0 else 0), r + 1)
                    strip = Polygon([p0, p1, (p1[0], p1[1] + 0.001), (p0[0], p0[1] + 0.001)])
                    from shapely.geometry import LineString
                    strip = LineString([p0, p1]).buffer(bw / 2, cap_style=2)
                    cost = (2 if in_finder(r, c) else 3) + pen
                    cands.append((cost, idx(r - dr, c - dc), idx(r + dr, c + dc), strip))
    # two dark cells in a row (rarely needed)
    for r in range(1, N - 1):
        for c in range(1, N - 2):
            if not light[r, c] and not light[r, c + 1] and light[r, c - 1] and light[r, c + 2]:
                y0 = r if light[r - 1, c] else r + 1 - bw
                cands.append((4, idx(r, c - 1), idx(r, c + 2), box(c - 0.05, y0, c + 2.05, y0 + bw)))
    for r in range(1, N - 2):
        for c in range(1, N - 1):
            if not light[r, c] and not light[r + 1, c] and light[r - 1, c] and light[r + 2, c]:
                x0 = c if light[r, c - 1] else c + 1 - bw
                cands.append((4, idx(r - 1, c), idx(r + 2, c), box(x0, r - 0.05, x0 + bw, r + 2.05)))
    cands.sort(key=lambda t: t[0])
    bridges = []
    for cost, a, b, geom in cands:
        if uf.union(a, b):
            bridges.append((cost, geom))
    # anything still loose?
    roots = {uf.find(idx(r, c)) for r in range(N) for c in range(N) if light[r, c]}
    loose = len(roots - {uf.find(FRAME)})
    return joints, [g for _, g in bridges], {'joints': len(joints), 'bridges': len(bridges),
                                             'bridges_on_finder_centre': sum(c >= 10 for c, _ in bridges),
                                             'loose_islands': loose}


# --- outline ---------------------------------------------------------------------------------------

def arm_geom(px, flip_scale=1.0):
    """The ARM bitmap as geometry, pointing up (-y), base at y=0, centred on x=0, pixel size px."""
    rows, cols = len(ARM), len(ARM[0])
    cells = [box((c - cols / 2) * px, -(rows - r) * px, (c - cols / 2 + 1) * px, -(rows - r - 1) * px)
             for r, row in enumerate(ARM) for c, ch in enumerate(row) if ch == '#']
    return unary_union(cells).buffer(0.01 * px, join_style=2)


def text_geom(text, height_mm):
    """Text as shapely polygons (mm, y down, origin at top-left), traced from a high-res render."""
    import cv2
    S = 40   # px per mm
    font = ImageFont.truetype(str(FONT), int(height_mm * S * 1.35))
    l, t, r, b = font.getbbox(text)
    img = Image.new('L', (r - l + 20, b - t + 20), 0)
    ImageDraw.Draw(img).text((10 - l, 10 - t), text, font=font, fill=255)
    a = np.asarray(img)
    cs, hier = cv2.findContours((a > 127).astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    polys = []
    for i, c in enumerate(cs):
        if hier[0][i][3] != -1 or len(c) < 3:
            continue
        holes = [cs[j][:, 0, :] / S for j in range(len(cs)) if hier[0][j][3] == i and len(cs[j]) >= 3]
        polys.append(Polygon(c[:, 0, :] / S, holes).buffer(0))
    g = unary_union(polys).simplify(0.03)
    minx, miny, maxx, maxy = g.bounds
    return affinity.translate(g, -minx, -miny)


def build(args, dark):
    m = args.module
    n = dark.shape[0]
    q = args.quiet
    N = n + 2 * q
    side = N * m
    c0 = side / 2
    square = box(0, 0, side, side)
    rim = args.rim if args.variant_now == 'relief' else 0.0   # relief: a thick frame outside the thin quiet zone
    frame = box(-rim, -rim, side + rim, side + rim)
    # arms on the four sides (before rotation; after the 45 degree turn they point diagonally)
    arm = arm_geom(m)
    arms = []
    for ang in (0, 90, 180, 270):
        a = affinity.translate(arm, c0, -rim + 0.2 * m)          # base slightly inside the edge
        arms.append(affinity.rotate(a, ang, origin=(c0, c0)))
    outline = unary_union([frame] + arms)
    rot = lambda g: affinity.rotate(g, 45, origin=(c0, c0))
    outline = rot(outline)
    minx, miny, maxx, maxy = outline.bounds
    half_diag = (side / 2 + rim) * math.sqrt(2)
    top = (c0, c0 - half_diag)
    bot = (c0, c0 + half_diag)
    # hanging loop on the top tip
    loop_r, hole_r = 4.5, 2.2
    loop = Point(top[0], top[1] - loop_r + 1.5).buffer(loop_r, 48)
    hole = Point(top[0], top[1] - loop_r + 1.5).buffer(hole_r, 48)
    # tag on the bottom tip for the name and year
    txt = text_geom(args.name, args.text_h)
    yr = text_geom(str(args.year), args.text_h * 0.8)
    tw = max(txt.bounds[2], yr.bounds[2]) + 6
    ty0 = bot[1] + 1.5                                    # lettering starts just below the tip
    tag = box(c0 - tw / 2, bot[1] - 6, c0 + tw / 2, ty0 + txt.bounds[3] + 2 + yr.bounds[3] + 2.5)   # 6 mm into the tip
    tag = tag.buffer(2.0, join_style=1).buffer(-1.0)
    lettering = unary_union([
        affinity.translate(txt, c0 - txt.bounds[2] / 2, ty0),
        affinity.translate(yr, c0 - yr.bounds[2] / 2, ty0 + txt.bounds[3] + 2)])
    lettering = affinity.scale(lettering, -1, 1, origin=(c0, 0))   # mirrored: read from the back
    outline = unary_union([outline, loop, tag]).difference(hole)

    cell = lambda r, c: box((c + q) * m, (r + q) * m, (c + q + 1) * m, (r + q + 1) * m)
    dark_u = unary_union([cell(r, c) for r in range(n) for c in range(n) if dark[r, c]])
    qr_area = rot(box(q * m, q * m, (q + n) * m, (q + n) * m))
    quiet_area = rot(square)
    out = {'outline': outline, 'lettering': lettering, 'dark': rot(dark_u), 'quiet_area': quiet_area, 'qr_area': qr_area,
           'size_mm': [round(outline.bounds[2] - outline.bounds[0], 1),
                       round(outline.bounds[3] - outline.bounds[1], 1)]}
    if args.variant_now == 'stencil':
        joints, bridges, rep = plan_bridges(dark, q, args.bridge / m)
        adds = unary_union(joints + bridges)
        adds = affinity.scale(adds, m, m, origin=(0, 0))
        material = outline.difference(rot(dark_u)).union(rot(adds).intersection(quiet_area))
        out['material'] = material
        out['parts'] = 1 if material.geom_type == 'Polygon' else len(material.geoms)
        out['bridges'] = rep
    else:
        raised = rot(dark_u.buffer(0.02, join_style=2))
        rim = outline.difference(quiet_area)
        out['raised'] = unary_union([raised, rim])
    return out


# --- raster plan and meshes ------------------------------------------------------------------------

def raster(geom, bounds, ppm, value=255, img=None):
    minx, miny, maxx, maxy = bounds
    W, H = int((maxx - minx) * ppm) + 1, int((maxy - miny) * ppm) + 1
    if img is None:
        img = Image.new('L', (W, H), 0)
    polys = [geom] if geom.geom_type == 'Polygon' else list(getattr(geom, 'geoms', []))
    tr = lambda cs: [((x - minx) * ppm, (y - miny) * ppm) for x, y in cs]
    # each polygon on its own layer, so one polygon's hole can't erase another polygon sitting inside it
    for p in polys:
        if p.geom_type != 'Polygon' or p.is_empty:
            continue
        layer = Image.new('L', img.size, 0)
        d = ImageDraw.Draw(layer)
        d.polygon(tr(p.exterior.coords), fill=value)
        for h in p.interiors:
            d.polygon(tr(h.coords), fill=0)
        img.paste(value, mask=layer)
    return img


def thickness_map(model, args, ppm, bounds):
    """mm of material per pixel, front view."""
    if args.variant_now == 'stencil':
        mat = np.asarray(raster(model['material'], bounds, ppm)) > 0
        return mat * args.plate
    out = np.asarray(raster(model['outline'], bounds, ppm)) > 0
    up = np.asarray(raster(model['raised'], bounds, ppm)) > 0
    return out * args.backing + (up & out) * (args.relief - args.backing)


def write_stl(model, args, path):
    import manifold3d as m3
    import trimesh

    def polys(g):
        return [g] if g.geom_type == 'Polygon' else [p for p in g.geoms if p.geom_type == 'Polygon']

    def extrude(g, h, z=0.0):
        acc = None
        for p in polys(g):
            p = orient(affinity.scale(p, 1, -1, origin=(0, 0)), 1.0)   # y up for the slicer; CCW
            cs = m3.CrossSection([np.asarray(p.exterior.coords)[:-1].tolist()] +
                                 [np.asarray(r.coords)[:-1].tolist() for r in p.interiors])
            e = cs.extrude(h).translate([0, 0, z])
            acc = e if acc is None else acc + e
        return acc

    if args.variant_now == 'stencil':
        body = extrude(model['material'], args.plate)
        top_t = args.plate
    else:
        body = extrude(model['outline'], args.backing) + extrude(model['raised'], args.relief - args.backing + 0.05,
                                                                args.backing - 0.05)
        top_t = args.relief
    body = body - extrude(model['lettering'], args.deboss + 0.01, -0.01)
    mesh = body.to_mesh()
    tm = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))
    parts = [b for b in tm.split(only_watertight=False) if abs(b.volume) > 1.0]   # drop zero-volume slivers
    tm = trimesh.util.concatenate(parts)
    tm.export(path)
    return {'watertight': bool(tm.is_watertight), 'volume_cm3': round(tm.volume / 1000, 2),
            'bodies': len(tm.split(only_watertight=False)), 'height_mm': top_t}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('out', type=Path)
    ap.add_argument('--text', default='Your Secret Santa is Sally! Make it merry.')
    ap.add_argument('--name', default='Sam')
    ap.add_argument('--year', default=2026)
    ap.add_argument('--ecc', default='m')
    ap.add_argument('--variant', default='both', choices=['stencil', 'relief', 'both'])
    ap.add_argument('--module', type=float, default=2.0, help='mm per QR module')
    ap.add_argument('--quiet', type=int, default=3, help='quiet zone, modules')
    ap.add_argument('--bridge', type=float, default=0.8, help='stencil bridge width, mm')
    ap.add_argument('--plate', type=float, default=2.0, help='stencil thickness, mm')
    ap.add_argument('--backing', type=float, default=0.6, help='relief backing, mm')
    ap.add_argument('--relief', type=float, default=3.0, help='relief total height, mm')
    ap.add_argument('--rim', type=float, default=3.0, help='relief frame outside the quiet zone, mm')
    ap.add_argument('--deboss', type=float, default=0.6)
    ap.add_argument('--text-h', type=float, default=6.0, help='name cap height, mm')
    ap.add_argument('--stl', action='store_true')
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    dark, version, ecc = qr_matrix(args.text, args.ecc)
    report = {'text': args.text, 'chars': len(args.text), 'version': version, 'ecc': ecc,
              'modules': int(dark.shape[0]), 'module_mm': args.module, 'variants': {}}
    models = {}
    for v in (['stencil', 'relief'] if args.variant == 'both' else [args.variant]):
        args.variant_now = v
        model = build(args, dark)
        r = {'size_mm': model['size_mm']}
        if v == 'stencil':
            r.update(parts=model['parts'], **model['bridges'])
        b = model['outline'].bounds
        t = thickness_map(model, args, 10, b)
        Image.fromarray((255 * (t > 0) - (t > args.backing + 0.01) * 0).astype(np.uint8) if v == 'stencil'
                        else (np.where(t == 0, 0, np.where(t > args.backing + 0.01, 90, 255))).astype(np.uint8)
                        ).save(args.out / f'plan-{v}.png')
        if args.stl:
            r['stl'] = write_stl(model, args, args.out / f'{v}.stl')
        report['variants'][v] = r
        models[v] = model
    (args.out / 'report.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return report, models, dark


if __name__ == '__main__':
    main()
