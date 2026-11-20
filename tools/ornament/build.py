"""Two-part stencil ornament from a two-colour drawing.

base.stl     white backing: outline = art silhouette + rim, pocket for the stencil, hanging tab
stencil.stl  one connected sheet of the drawing's colour, press-fits into the pocket

Run: python build.py ART.png OUTDIR [--width 80 --height 85]   (requirements.txt; an order goes through make.py)
"""
import argparse, json
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw
from scipy import ndimage as nd
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.ops import unary_union
from shapely import affinity
import manifold3d as m3, trimesh

ap = argparse.ArgumentParser()
ap.add_argument('art'); ap.add_argument('out')
ap.add_argument('--width', type=float, default=80.0, help='art box width, mm: the art is scaled to fit the box')
ap.add_argument('--height', type=float, default=85.0, help='art box height, mm (added 2026-11-19; before, width only)')
ap.add_argument('--max-base-w', type=float, default=90.0, help='widest base that passes, mm')
ap.add_argument('--max-base-h', type=float, default=125.0, help='tallest base that passes, mm (ring and tag included)')
ap.add_argument('--min-white-kept', type=float, default=0.8, help='fail below this share of the drawing\'s cut-outs kept')
ap.add_argument('--min-line', type=float, default=1.0, help='thinnest red, mm')
ap.add_argument('--min-gap', type=float, default=1.0, help='thinnest white cut, mm')
ap.add_argument('--bridge', type=float, default=1.8, help='bridge width, mm (1.2 until 2026-11-19)')
ap.add_argument('--neck', type=float, default=1.8, help='widen connecting necks thinner than this, mm; 0 = off (added 2026-11-19)')
ap.add_argument('--speck', type=float, default=2.0, help='drop islands under this, mm2')
ap.add_argument('--stencil-t', type=float, default=1.2)
ap.add_argument('--base-t', type=float, default=3.2)
ap.add_argument('--pocket', type=float, default=1.0, help='pocket depth, mm')
ap.add_argument('--clear', type=float, default=0.10, help='pocket clearance per side, mm')
ap.add_argument('--ink', type=float, default=120, help='RGB distance from white that counts as ink')
ap.add_argument('--max-bridge', type=float, default=3.0, help='warn above this bridge length, mm')
ap.add_argument('--pegs', type=int, default=6)
ap.add_argument('--peg', type=float, default=2.2, help='diamond peg side, mm')
ap.add_argument('--peg-hole', type=float, default=3.0, help='round hole diameter, mm (< peg diagonal = press fit)')
ap.add_argument('--peg-h', type=float, default=1.4)
ap.add_argument('--base-col', default='#f6f4ee')
ap.add_argument('--stencil-col', default='#d61a1a')
ap.add_argument('--name', default='', help='text for the name tag; empty = no tag')
ap.add_argument('--font', default='allerta', help='stencil font key in nametag.STENCILS')
ap.add_argument('--tag-h', type=float, default=17.0, help='visible tag height, mm')
ap.add_argument('--tag-w', type=float, default=0.8, help='tag width as a share of the art width (clamped 64-72 mm, nametag.tag_width)')
ap.add_argument('--rim', type=float, default=2.0, help='white rim outside the stencil, mm')
a = ap.parse_args()
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

# 1-2. ink, scale to the box, cleanup, bridges, sheet and silhouette: drawing.py, shared with the upload check
import sys; sys.path.insert(0, str(Path(__file__).parent))
from drawing import prepare, unpinch, drop_small
rep, geo = prepare(a.art, width=a.width, height=a.height, min_line=a.min_line, min_gap=a.min_gap, neck=a.neck,
                   bridge=a.bridge, speck=a.speck, ink=a.ink, max_bridge=a.max_bridge, min_white_kept=a.min_white_kept)
s, sheet, sil = geo['s'], geo['sheet'], geo['sil']
log = {k: rep[k] for k in ('specks_dropped', 'thin_red_mm2', 'thin_gaps_filled_mm2', 'necks_widened_mm', 'bridges_mm')}
warn = list(rep['problems'])
if a.name:
    # name tag: base material hanging below the head; the stencil sheet covers it as a plate with the
    # name cut through, so the letters show the base colour. Stencil fonts keep the plate one piece.
    from nametag import fit, tag_width, PAD_X, PAD_BOTTOM, PAD_TOP, MIN_TEXT_H, MAX_TEXT_H
    from shapely.geometry import box
    x0, y0, x1, y1 = sil.bounds; cxs = (x0 + x1) / 2
    tw = tag_width(x1 - x0, a.tag_w)
    overlap = 5.0
    while True:
        tag = box(cxs - tw / 2, y0 - a.tag_h, cxs + tw / 2, y0 + overlap).buffer(-4).buffer(4)
        if unary_union([sil, tag]).geom_type == 'Polygon' or overlap > 30: break
        overlap += 2.0
    tbox = box(cxs - tw / 2 + PAD_X, y0 - a.tag_h + PAD_BOTTOM, cxs + tw / 2 - PAD_X, y0 - PAD_TOP)
    text, cap, tw_ = fit(a.name, a.font, tbox, max_h=MAX_TEXT_H, min_h=MIN_TEXT_H)
    text = text.buffer(-0.2)                      # thin the letters a hair so the font's bridges print
    sil = Polygon(unary_union([sil, tag]).exterior)
    sheet_notext = unary_union([sheet, tag])
    sheet = drop_small(sheet_notext.difference(text), 0.01)   # what ext() would skip anyway
    plate = sheet.intersection(tag)
    log['tag'] = dict(name=a.name, font=a.font, cap_mm=round(cap, 1), width_mm=round(tw, 1), overlap_mm=overlap,
                      thin_red_mm2=round(plate.difference(plate.buffer(-a.min_line / 2).buffer(a.min_line / 2)).area, 2),
                      pieces=1 if sheet.geom_type == 'Polygon' else len(sheet.geoms))
    if tw_: warn.append(tw_)
    if sheet.geom_type != 'Polygon': warn.append(f"tag text leaves {len(sheet.geoms) - 1} loose pieces (font not stencil-safe for this text)")
sheet, pinches = unpinch(sheet, a.min_line)
if pinches: log['pinches_widened'] = pinches
cx, cy = sil.centroid.x, sil.centroid.y
sheet = affinity.translate(sheet, -cx, -cy); sil = affinity.translate(sil, -cx, -cy)
if a.name:
    sheet_notext, tbox = (affinity.translate(g, -cx, -cy) for g in (sheet_notext, tbox))

def ext(g, h, z=0.0):
    gs = g.geoms if hasattr(g, 'geoms') else [g]
    body = None
    for p in gs:
        if p.area < 0.01: continue
        cs = m3.CrossSection([np.asarray(p.exterior.coords)[:-1].tolist()] +
                             [np.asarray(r.coords)[:-1].tolist() for r in p.interiors], m3.FillRule.EvenOdd)
        e = cs.extrude(h).translate([0, 0, z])
        body = e if body is None else body + e
    return body

def tm(man):
    mm = man.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts))

# 3. base: rim + pocket + hanging tab at the top centre of the outline
outline = sil.buffer(a.rim, join_style=1)
# hanging ring on the centre line (x=0 is the centroid, so it hangs level). Find the real top edge there,
# put the ring just above it and join them with a solid neck: the hull of the ring and a 14 mm wide band of
# the outline below it, then fillet the joins so it reads as one piece.
from shapely.geometry import LineString, box as _box
cut = LineString([(0, outline.bounds[1] - 1), (0, outline.bounds[3] + 1)]).intersection(outline)
top_y = max(c[1] for g in getattr(cut, 'geoms', [cut]) for c in g.coords)
RING_R, HOLE_R = 5.0, 2.0
ring = Point(0, top_y + 3.0).buffer(RING_R, 64)
band = outline.intersection(_box(-7, top_y - 8, 7, top_y + 0.01))
neck = unary_union([ring, band]).convex_hull
outline = unary_union([outline, neck]).buffer(1.5, join_style=1).buffer(-1.5, join_style=1)
outline = Polygon(outline.exterior) if outline.geom_type == 'Polygon' else Polygon(max(outline.geoms, key=lambda g: g.area).exterior)
outline = Polygon(outline.exterior).buffer(0.05, join_style=1).buffer(-0.05, join_style=1).simplify(0.02)   # clear pinch points
hole = Point(0, top_y + 3.0).buffer(HOLE_R, 32)
log['ring'] = dict(top_y=round(top_y, 1), wall_mm=RING_R - HOLE_R,
                   neck_min_mm=round(neck.intersection(_box(-20, top_y - 1, 20, top_y + 1)).bounds[2] * 2, 1))
# pegs: diamond (square turned 45 deg) pegs on the stencil's back, spread over its widest parts;
# round blind holes in the pocket floor. Diagonal > hole = press fit; the corners give.
diag = a.peg * 2 ** 0.5
inner = sheet.buffer(-(diag / 2 + 0.6))
xs_ = np.arange(*sheet.bounds[0::2], 0.5); ys_ = np.arange(*sheet.bounds[1::2], 0.5)
from shapely import prepared
pin = prepared.prep(inner)
cand = np.array([(x, y) for x in xs_ for y in ys_ if pin.contains(Point(x, y))])
sites = []
if len(cand):
    sites.append(cand[np.argmax(np.hypot(*cand.T))])
    while len(sites) < a.pegs:
        dmin = np.min([np.hypot(*(cand - q).T) for q in sites], axis=0)
        if dmin.max() < 10: break
        sites.append(cand[np.argmax(dmin)])
log['pegs'] = [[round(float(x), 1), round(float(y), 1)] for x, y in sites]
if len(sites) < 3: warn.append(f'only {len(sites)} peg sites')
floor = a.base_t - a.pocket
holes = None
for x, y in sites:
    h = m3.Manifold.cylinder(a.peg_h + 0.2 + 1, a.peg_hole / 2, a.peg_hole / 2, 40).translate([x, y, floor - a.peg_h - 0.2])
    holes = h if holes is None else holes + h
base = ext(outline.difference(hole), a.base_t) - ext(sil.buffer(a.clear, join_style=1), a.pocket + 1, floor)
if holes is not None: base = base - holes
# stencil in print orientation: face down on the bed (mirror y = the assembled part turned over), pegs up
stencil = ext(affinity.scale(sheet, 1, -1, origin=(0, 0)), a.stencil_t)
for x, y in sites:
    stencil = stencil + m3.Manifold.cube([a.peg, a.peg, a.peg_h], True).rotate([0, 0, 45]).translate([x, -y, a.stencil_t + a.peg_h / 2])
B, S = tm(base), tm(stencil)
B.export(out / 'base.stl'); S.export(out / 'stencil.stl')
log.update(base_mm=[round(v, 1) for v in B.extents], stencil_mm=[round(v, 1) for v in S.extents],
           base_watertight=B.is_watertight, stencil_watertight=S.is_watertight,
           stencil_bodies=len(S.split(only_watertight=False)), base_cm3=round(B.volume / 1000, 2),
           stencil_cm3=round(S.volume / 1000, 2))
if log['stencil_bodies'] != 1: warn.append('STENCIL IS NOT ONE PIECE')
if not (B.is_watertight and S.is_watertight): warn.append('MESH NOT WATERTIGHT')
if B.extents[0] > a.max_base_w + 1e-6 or B.extents[1] > a.max_base_h + 1e-6:
    warn.append(f'base {B.extents[0]:.1f} x {B.extents[1]:.1f} mm is over the {a.max_base_w:g} x {a.max_base_h:g} mm limit')
log.update(art_mm=rep['art_mm'], white_mm2=rep['white_mm2'], white_kept=rep['white_kept'], pieces=rep['pieces'])
log['warnings'] = warn

# 4. flat preview: white base, shadowed pocket wall, red sheet
k = 8; W = outline.bounds; img = Image.new('RGB', (int((W[2] - W[0]) * k) + 40, int((W[3] - W[1]) * k) + 40), (34, 60, 40))
d = ImageDraw.Draw(img)
P = lambda g, dx=0, dy=0: [((x - W[0]) * k + 20 + dx, (W[3] - y) * k + 20 + dy) for x, y in g.coords]
def fill(g, col, dx=0, dy=0, holes_col=None):
    for p in (g.geoms if hasattr(g, 'geoms') else [g]):
        d.polygon(P(p.exterior, dx, dy), fill=col)
        for r in p.interiors: d.polygon(P(r, dx, dy), fill=holes_col)
hx = lambda h: tuple(int(h.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
dim = lambda c, f: tuple(int(v * f) for v in c)
BC, SC = hx(a.base_col), hx(a.stencil_col)
fill(outline, (40, 40, 40), 6, 6, (34, 60, 40)); fill(outline, BC, holes_col=(34, 60, 40))
fill(sil, dim(BC, 0.88)); fill(sil.buffer(-0.6), BC)
fill(sheet, dim(SC, 0.6), 3, 3, None)
for p in (sheet.geoms if hasattr(sheet, 'geoms') else [sheet]):
    d.polygon(P(p.exterior), fill=SC)
    for r in p.interiors: d.polygon(P(r), fill=BC)
hc = P(hole.exterior); d.polygon(hc, fill=(34, 60, 40))
for x, y in sites:
    q = ((x - W[0]) * k + 20, (W[3] - y) * k + 20); r = diag / 2 * k
    d.polygon([(q[0], q[1] - r), (q[0] + r, q[1]), (q[0], q[1] + r), (q[0] - r, q[1])], outline=(255, 255, 0), width=2)
img.save(out / 'preview.png')
# design.svg for the colour picker: #base and #stencil groups, recoloured by the page
def svgpath(g):
    out_ = []
    for p in (g.geoms if hasattr(g, 'geoms') else [g]):
        for r in [p.exterior, *p.interiors]:
            out_.append('M' + ' L'.join(f'{x - W[0]:.2f},{W[3] - y:.2f}' for x, y in r.coords) + ' Z')
    return ' '.join(out_)
(out / 'design.svg').write_text(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W[2]-W[0]:.2f} {W[3]-W[1]:.2f}">'
    f'<g id="base"><path fill-rule="evenodd" fill="#ffffff" stroke="#00000033" stroke-width="0.3" d="{svgpath(outline.difference(hole))}"/></g>'
    f'<g id="stencil"><path fill-rule="evenodd" fill="#f91010" d="{svgpath(sheet)}"/></g></svg>')
if a.name:
    # design-tag.svg: the tag with no text cut, plus #textbox (the area the page fits the name into);
    # the page draws the name in the base colour on top. The real cut comes from build.py --name.
    bx0, by0, bx1, by1 = tbox.bounds
    (out / 'design-tag.svg').write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W[2]-W[0]:.2f} {W[3]-W[1]:.2f}">'
        f'<g id="base"><path fill-rule="evenodd" fill="#ffffff" stroke="#00000033" stroke-width="0.3" d="{svgpath(outline.difference(hole))}"/></g>'
        f'<g id="stencil"><path fill-rule="evenodd" fill="#f91010" d="{svgpath(sheet_notext)}"/></g>'
        f'<rect id="textbox" x="{bx0 - W[0]:.2f}" y="{W[3] - by1:.2f}" width="{bx1 - bx0:.2f}" height="{by1 - by0:.2f}" '
        f'fill="none" data-max-cap="11" data-min-cap="5"/></svg>')
(out / 'build.json').write_text(json.dumps(vars(a) | log, indent=1))
print(json.dumps(log, indent=1))
