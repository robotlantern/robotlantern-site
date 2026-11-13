"""Feasibility prototype: a photo becomes a snap-together mosaic ornament (products/cutout-ornament/).

    PY=~/work/lab/lithophane-maker/.venv/bin/python   # cv2, shapely, manifold3d, trimesh, onnxruntime
    $PY tools/cutout/mosaic.py photo.jpg out/ --colors 4 [--crop x0,y0,x1,y1] [--size 80] [--stl]

Every pixel of the round face is assigned to one filament colour, so the face is a mosaic of flat pieces
(two colours is the black-and-white "stencil" case). The pieces sit on a common round back, a stock part
with a grid of square sockets, and each piece carries square pins wherever its interior covers a grid
point. The back is black, and the pieces are inset from each other, so a thin black line shows between
neighbours, like the leading in stained glass. That line also hides fit tolerance.

The printability rules are applied to the picture itself, so whatever comes out can be printed:
- every piece holds at least one pin (so it can't fall off, and a square pin stops it turning);
- no part of a piece is narrower than `min_width`;
- a small region that stands out (an eye, a nose) is grown until it holds a pin, the way a cartoonist
  exaggerates features; a small region that doesn't stand out is merged into its neighbour.

Outputs: preview.png, layers.svg (one group per colour), report.json, and with --stl one STL per colour
plate plus back.stl. Customer photos never go in Git; write outputs outside the repo or in .private/.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

LITHO = Path.home() / 'work/lab/lithophane-maker'
sys.path.insert(0, str(LITHO))

# Filament colours. "have" = on the shelf in printdb on 2026-11-13; the rest are common matte PLA colours
# that would have to be bought. Hex values are display guesses, not measured.
FILAMENTS = {
    'white':      ('#f2f0ea', True),
    'black':      ('#1d1d1f', True),
    'navy':       ('#1f2f5c', True),
    'ruby red':   ('#9b1b2a', True),
    'olive':      ('#6b7232', True),
    'orange':     ('#e8762d', True),
    'gold silk':  ('#c9a64a', True),
    'silver silk': ('#a9adb3', True),
    'cream':      ('#e9dcc0', False),
    'tan':        ('#c49a6c', False),
    'brown':      ('#7a4b2a', False),
    'dark brown': ('#3e2a1e', False),
    'grey':       ('#8a8d91', False),
    'light grey': ('#c6c8ca', False),
    'pink':       ('#e3a3a6', False),
}
BACKGROUNDS = ['ruby red', 'olive', 'navy']   # festive field colours for the area around the subject


def hex_rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.uint8)


def to_lab(rgb_u8):
    return cv2.cvtColor(rgb_u8.reshape(-1, 1, 3), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)


def disk(r):
    r = max(int(round(r)), 1)
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


class Spec:
    def __init__(self, a):
        self.size = a.size            # face diameter, mm
        self.mmpx = 0.1               # working resolution, mm per pixel
        self.gap = 0.6                # black line between pieces, mm
        self.min_width = 1.2          # narrowest printable part of a piece, mm (3 lines of a 0.4 nozzle)
        self.pitch = a.pitch          # socket grid pitch, mm
        self.pin = 2.0                # square pin side, mm
        self.pin_margin = 0.6         # piece material left around a pin, mm
        self.piece_t = 1.6            # piece thickness, mm
        self.pin_h = 1.2
        self.back_t = 2.4
        self.socket = 2.2             # socket side, mm (0.1 mm clearance a side; set by a test print)
        self.socket_d = 1.4
        self.rim = 2.0                # back's border outside the face, mm
        self.min_area = a.min_area    # non-salient regions smaller than this merge away, mm²
        self.salient = 30             # Lab distance that makes a small region a feature worth keeping
        self.smooth = a.smooth        # boundary smoothing, px
        self.n = int(round(self.size / self.mmpx))

    @property
    def pin_erode_px(self):
        # A grid point is a pin site when the whole pin, plus margin, plus half the gap, is inside the region.
        return (self.pin / 2 * 2 ** 0.5 + self.pin_margin + self.gap / 2) / self.mmpx


def load(path, crop):
    im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    if crop:
        im = im.crop(crop)
    w, h = im.size                    # centre square crop
    s = min(w, h)
    return im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))


def subject_mask(im, n):
    from litho import matting
    a = matting.alpha_model(im)
    a = cv2.resize(a, (n, n))
    m = (a > 0.5).astype(np.uint8)
    k = cv2.connectedComponentsWithStats(m)   # keep the largest blob
    if k[0] > 1:
        big = 1 + int(np.argmax(k[2][1:, cv2.CC_STAT_AREA]))
        m = (k[1] == big).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(15))
    # fill enclosed holes: a white muzzle on a white background is still the subject
    ff = np.pad(1 - m, 1, constant_values=1).astype(np.uint8)
    cv2.floodFill(ff, None, (0, 0), 2)
    m[ff[1:-1, 1:-1] == 1] = 1
    return m.astype(bool)


def quantize(im, n, subj, k, face):
    """k colour clusters over the subject, after flattening fur and texture."""
    rgb = np.asarray(im.resize((n, n), Image.LANCZOS))
    flat = cv2.pyrMeanShiftFiltering(rgb, sp=14, sr=28)
    flat = cv2.bilateralFilter(flat, 9, 40, 9)
    lab = cv2.cvtColor(flat, cv2.COLOR_RGB2LAB).astype(np.float32)
    pts = lab[subj & face]
    # weight lightness more: value structure matters more than hue for likeness
    w = np.array([1.6, 1.0, 1.0], np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.2)
    _, lab_i, centres = cv2.kmeans(pts * w, k, None, crit, 6, cv2.KMEANS_PP_CENTERS)
    centres = centres / w
    labels = np.full((n, n), -1, np.int32)
    d = ((lab[..., None, :] - centres[None, None]) ** 2 * w ** 2).sum(-1)
    labels[subj & face] = d.argmin(-1)[subj & face]
    return labels, centres, rgb


def assign_filaments(centres, k, stock_only):
    """Map clusters to distinct filaments (nearest in Lab, best total by brute force over small k)."""
    import itertools
    names = [f for f, (_, have) in FILAMENTS.items() if (have or not stock_only) and f not in BACKGROUNDS]
    flab = to_lab(np.array([hex_rgb(FILAMENTS[f][0]) for f in names]))
    cost = ((centres[:, None] - flab[None]) ** 2 * np.array([1.6, 1, 1]) ** 2).sum(-1)
    best = min(itertools.permutations(range(len(names)), k), key=lambda p: sum(cost[i, j] for i, j in enumerate(p)))
    return [names[j] for j in best]


def cleanup(labels, face, spec, contrast, max_pass=60):
    """Make every connected region printable: wide enough, and holding at least one pin."""
    n = spec.n
    ys, xs = np.mgrid[0:n, 0:n]
    step = spec.pitch / spec.mmpx
    off = (n / 2) % step
    grid = np.zeros((n, n), bool)
    gy = np.arange(off, n, step).round().astype(int)
    grid[np.ix_(gy, gy)] = True
    grid &= face
    er = disk(spec.pin_erode_px)
    open_k = disk(spec.min_width / 2 / spec.mmpx)
    L = labels.copy()
    grown = 0
    seeds = []                          # (label, y, x) of grown features: never merged afterwards
    for _ in range(max_pass):
        changed = False
        # 1. smooth boundaries: blur each label's indicator, take the argmax (consistent shared edges)
        ids = [i for i in np.unique(L[face]) if i >= 0]
        stack = np.stack([cv2.GaussianBlur((L == i).astype(np.float32), (0, 0), spec.smooth) for i in ids])
        L2 = np.where(face, np.array(ids)[stack.argmax(0)], -1)
        # 2. thin necks: open each label, hand the removed pixels to their neighbours
        keep = np.zeros_like(face)
        for i in ids:
            keep |= cv2.morphologyEx((L2 == i).astype(np.uint8), cv2.MORPH_OPEN, open_k).astype(bool)
        L2 = fill_from_neighbours(L2, face & ~keep)
        if (L2 != L).any():
            changed = True
        L = L2
        # 3. regions without a pin site: grow if salient, else merge
        comps = []
        for i in np.unique(L[face]):
            cnt, cc = cv2.connectedComponents((L == i).astype(np.uint8))
            for c in range(1, cnt):
                m = cc == c
                inner = cv2.erode(m.astype(np.uint8), er).astype(bool)
                comps.append((int(m.sum()), i, m, int((inner & grid).sum())))
        comps.sort(key=lambda t: t[0])
        for area, i, m, sites in comps:
            if sites and area * spec.mmpx ** 2 >= spec.min_area:
                continue
            if sites and any(lab == i and m[y, x] for lab, y, x in seeds):
                continue
            ring0 = cv2.dilate(m.astype(np.uint8), disk(3)).astype(bool) & ~m & face
            nb0 = L[ring0]
            nb0 = nb0[nb0 >= 0]
            if sites and nb0.size and contrast[i][np.bincount(nb0).argmax()] > spec.salient:
                continue                # small but salient and already pinned: keep it
            if not (L[m] == i).all():
                continue                # changed earlier in this pass
            changed = True
            ring = cv2.dilate(m.astype(np.uint8), disk(3)).astype(bool) & ~m & face
            nb = L[ring]
            nb = nb[nb >= 0]
            if nb.size == 0:
                continue
            host = np.bincount(nb).argmax()
            hcc = cv2.connectedComponents((L == host).astype(np.uint8))[1]
            host_area = (hcc == np.bincount(hcc[ring & (L == host)]).argmax()).sum() * spec.mmpx ** 2
            # a mark on a small feature (a catchlight in an eye) merges; a mark on a big area is a feature
            cy0, cx0 = [v.mean() for v in np.nonzero(m)]
            regrow = any(lab == i and np.hypot(y - cy0, x - cx0) < 40 for lab, y, x in seeds)
            if (not sites and not regrow and contrast[i][host] > spec.salient and area * spec.mmpx ** 2 > 0.8
                    and host_area > 150):
                # salient (an eye, a nose): grow it about its centre until it holds a pin
                cy, cx = [int(v.mean()) for v in np.nonzero(m)]
                d = np.hypot(*(np.stack(np.nonzero(grid & face)) - np.array([[cy], [cx]])))
                gyx = np.stack(np.nonzero(grid & face))[:, d.argmin()]
                r = spec.pin_erode_px + 2
                blob = np.hypot(ys - (cy + gyx[0]) / 2, xs - (cx + gyx[1]) / 2) <= r + d.min() / 2
                L[(blob | m) & face & ((L == host) | m)] = i
                seeds.append((i, int(gyx[0]), int(gyx[1])))
                grown += 1
            else:
                L[m] = host
        if not changed:
            break
    return L, grid, grown


def fill_from_neighbours(L, hole):
    L = L.copy()
    L[hole] = -2
    for _ in range(60):
        todo = L == -2
        if not todo.any():
            break
        best = np.full(L.shape, -2)
        bestc = np.zeros(L.shape)
        for i in np.unique(L[L >= 0]):
            c = cv2.blur((L == i).astype(np.float32), (5, 5))
            upd = todo & (c > bestc)
            best[upd], bestc[upd] = i, c[upd]
        L[todo & (best >= 0)] = best[todo & (best >= 0)]
    return L


def pieces(L, face, grid, spec, names):
    """Vector pieces: one polygon per connected region, inset by half the gap, with its pin sites."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    out = []
    er = disk(spec.pin_erode_px)
    for i in np.unique(L[face]):
        cnt, cc = cv2.connectedComponents((L == i).astype(np.uint8))
        for c in range(1, cnt):
            m = (cc == c).astype(np.uint8)
            cs, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
            polys = []
            for j, cnt_ in enumerate(cs):
                if hier[0][j][3] != -1 or len(cnt_) < 4:
                    continue
                holes = [cs[h][:, 0] for h in range(len(cs)) if hier[0][h][3] == j and len(cs[h]) >= 4]
                polys.append(Polygon(cnt_[:, 0], holes))
            g = unary_union(polys).buffer(0)
            g = g.simplify(0.6).buffer(-spec.gap / 2 / spec.mmpx, join_style=1)
            if g.is_empty:
                continue
            if g.geom_type == 'MultiPolygon':
                g = max(g.geoms, key=lambda p: p.area)
            sites = np.stack(np.nonzero(cv2.erode(m, er).astype(bool) & grid), 1)
            out.append({'color': names[i], 'poly': g, 'pins': sites.tolist(),
                        'area_mm2': g.area * spec.mmpx ** 2})
    return out


def back_outline(face, spec):
    """The back's outline in px: the face grown by the rim, as one polygon."""
    from shapely.geometry import Polygon
    pad = int(spec.rim / spec.mmpx) + 2
    m = cv2.copyMakeBorder(face.astype(np.uint8), pad, pad, pad, pad, cv2.BORDER_CONSTANT, 0)
    m = cv2.dilate(m, disk(spec.rim / spec.mmpx))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)[:, 0].astype(float) - pad
    return Polygon(c).simplify(0.6)


def render(ps, spec, path, outline):
    n = spec.n
    img = np.zeros((n + 80, n + 80, 3), np.uint8) + 235
    cv2.fillPoly(img, [np.asarray(outline.exterior.coords, np.int32) + 40], (31, 29, 29), cv2.LINE_AA)
    for p in ps:
        col = tuple(int(v) for v in hex_rgb(FILAMENTS[p['color']][0]))
        mask = np.zeros(img.shape[:2], np.uint8)
        cv2.fillPoly(mask, [np.asarray(p['poly'].exterior.coords, np.int32) + 40], 255, cv2.LINE_AA)
        for h in p['poly'].interiors:
            cv2.fillPoly(mask, [np.asarray(h.coords, np.int32) + 40], 0, cv2.LINE_AA)
        a = mask[..., None] / 255.0
        img[:] = (img * (1 - a) + np.array(col) * a).astype(np.uint8)
    Image.fromarray(img).save(path)


def write_svg(ps, spec, path, outline):
    s = spec.mmpx
    groups = {}
    back = 'M' + 'L'.join(f'{x * s:.2f},{y * s:.2f}' for x, y in outline.exterior.coords) + 'Z'
    for p in ps:
        g = p['poly']
        d = 'M' + 'L'.join(f'{x * s:.2f},{y * s:.2f}' for x, y in g.exterior.coords) + 'Z'
        for h in g.interiors:
            d += 'M' + 'L'.join(f'{x * s:.2f},{y * s:.2f}' for x, y in h.coords) + 'Z'
        groups.setdefault(p['color'], []).append(d)
    body = ''.join(
        f'<g id="{c}" fill="{FILAMENTS[c][0]}" fill-rule="evenodd">' + ''.join(f'<path d="{d}"/>' for d in ds) + '</g>'
        for c, ds in groups.items())
    Path(path).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{spec.size}mm" height="{spec.size}mm" '
                          f'viewBox="{-spec.rim} {-spec.rim} {spec.size + 2 * spec.rim} {spec.size + 2 * spec.rim}">'
                          f'<path id="back" d="{back}" fill="#1d1d1f"/>{body}</svg>')


def write_stl(ps, spec, out, outline, face):
    """One STL per colour plate (pieces face-down, pins up) and the stock back. Plates are laid out by
    the slicer's arrange step."""
    import manifold3d as m3
    import trimesh
    from shapely import affinity

    def extrude(poly, h):
        cs = m3.CrossSection([np.asarray(poly.exterior.coords)[:-1].tolist()] +
                             [np.asarray(r.coords)[:-1][::-1].tolist() for r in poly.interiors])
        return cs.extrude(h)

    def to_tm(man):
        mesh = man.to_mesh()
        return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))

    s = spec.mmpx
    plates = {}
    for p in ps:
        poly = affinity.scale(p['poly'], s, -s, origin=(0, 0))   # mirror: printed face-down
        body = extrude(poly, spec.piece_t)
        for y, x in p['pins']:
            pin = m3.Manifold.cube([spec.pin, spec.pin, spec.pin_h], center=False).translate(
                [x * s - spec.pin / 2, -y * s - spec.pin / 2, spec.piece_t])
            body = body + pin
        plates.setdefault(p['color'], []).append(to_tm(body))
    for c, ms in plates.items():
        trimesh.util.concatenate(ms).export(out / f'plate-{c.replace(" ", "-")}.stl')
    # the back: the outline (a disc for the round ornament, a stock part), a socket at every grid point
    # under the face, and a hanging tab at the top
    o = affinity.scale(outline, s, -s, origin=(0, 0))
    back = extrude(o, spec.back_t)
    top = max(o.exterior.coords, key=lambda c: c[1])
    cx = (o.bounds[0] + o.bounds[2]) / 2
    ty = max(c[1] for c in o.exterior.coords if abs(c[0] - cx) < 3) if any(abs(c[0] - cx) < 3 for c in o.exterior.coords) else top[1]
    back = back + m3.Manifold.cylinder(spec.back_t, 4.5, 4.5, 48).translate([cx, ty + 1.5, 0])
    back = back - m3.Manifold.cylinder(spec.back_t + 2, 2.0, 2.0, 32).translate([cx, ty + 1.5, -1])
    inner = cv2.erode(face.astype(np.uint8), disk(1.5 / s)).astype(bool)
    step = spec.pitch / s
    off = (spec.n / 2) % step
    for gy in np.arange(off, spec.n, step).round().astype(int):
        for gx in np.arange(off, spec.n, step).round().astype(int):
            if inner[gy, gx]:
                back = back - m3.Manifold.cube([spec.socket, spec.socket, spec.socket_d + 1]).translate(
                    [gx * s - spec.socket / 2, -gy * s - spec.socket / 2, spec.back_t - spec.socket_d])
    to_tm(back).export(out / 'back.stl')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('photo')
    ap.add_argument('out')
    ap.add_argument('--colors', type=int, default=4, help='colours in the subject (2 = black and white)')
    ap.add_argument('--crop', type=lambda s: tuple(int(v) for v in s.split(',')))
    ap.add_argument('--size', type=float, default=80)
    ap.add_argument('--pitch', type=float, default=4.0)
    ap.add_argument('--bg', default='ruby red')
    ap.add_argument('--min-area', type=float, default=30, help='mm²; smaller plain regions merge')
    ap.add_argument('--smooth', type=float, default=4.0)
    ap.add_argument('--features', type=float, default=25, help='black-hat threshold for dark features; 0 = off')
    ap.add_argument('--stock-only', action='store_true', help='only filaments already on the shelf')
    ap.add_argument('--stl', action='store_true')
    ap.add_argument('--shape', choices=['circle', 'outline'], default='circle')
    ap.add_argument('--no-fit', dest='fit', action='store_false')
    a = ap.parse_args()
    spec = Spec(a)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    n = spec.n
    im = load(a.photo, a.crop)
    subj = subject_mask(im, n)
    if a.fit:                           # crop to the subject, with a margin, so the head fills the face
        ys_, xs_ = np.nonzero(subj)
        k = im.size[0] / n
        cy, cx = (ys_.min() + ys_.max()) / 2 * k, (xs_.min() + xs_.max()) / 2 * k
        half = max(ys_.max() - ys_.min(), xs_.max() - xs_.min()) / 2 * k * (1.06 if a.shape == 'outline' else 1.12)
        pad = int(half)
        edge = tuple(int(v) for v in np.median(np.concatenate([np.asarray(im)[0], np.asarray(im)[-1]]), 0))
        im = ImageOps.expand(im, pad, fill=edge).crop(
            (int(cx - half) + pad, int(cy - half) + pad, int(cx + half) + pad, int(cy + half) + pad))
        subj = subject_mask(im, n)
    yy, xx = np.mgrid[0:n, 0:n]
    if a.shape == 'outline':            # the ornament is the subject's silhouette, simplified
        subj = cv2.morphologyEx(subj.astype(np.uint8), cv2.MORPH_CLOSE, disk(4 / spec.mmpx))
        subj = cv2.morphologyEx(subj, cv2.MORPH_OPEN, disk(3 / spec.mmpx)).astype(bool)
        face = subj.copy()
    else:
        face = np.hypot(yy - n / 2 + .5, xx - n / 2 + .5) <= n / 2
    if a.colors == 2:
        names = ['black', 'white']
        g = cv2.cvtColor(np.asarray(im.resize((n, n), Image.LANCZOS)), cv2.COLOR_RGB2GRAY)
        g = cv2.createCLAHE(2.0, (8, 8)).apply(cv2.bilateralFilter(g, 9, 30, 9))
        t, _ = cv2.threshold(g[subj & face], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        labels = np.where(subj & face, (g > t).astype(np.int32), -1)
        centres = to_lab(np.array([hex_rgb(FILAMENTS[c][0]) for c in names]))
    else:
        labels, centres, _ = quantize(im, n, subj, a.colors, face)
        names = assign_filaments(centres, a.colors, a.stock_only)
    if a.features and a.colors > 2:
        # eyes, nose, mouth: locally dark spots inside the subject become the darkest filament
        g = cv2.cvtColor(np.asarray(im.resize((n, n), Image.LANCZOS)), cv2.COLOR_RGB2GRAY)
        g = cv2.bilateralFilter(g, 9, 30, 9)
        bh = cv2.morphologyEx(g, cv2.MORPH_BLACKHAT, disk(4.0 / spec.mmpx))
        feat = (bh > a.features) & (g < 110) & cv2.erode(subj.astype(np.uint8), disk(10)).astype(bool)
        feat = cv2.morphologyEx(feat.astype(np.uint8), cv2.MORPH_OPEN, disk(4)).astype(bool)
        if 'black' in names:
            labels[feat] = names.index('black')
        else:
            names.append('black')
            centres = np.vstack([centres, to_lab(hex_rgb(FILAMENTS['black'][0])[None])])
            labels[feat] = len(names) - 1
    labels = fill_from_neighbours(labels, face & (labels < 0)) if a.shape == 'outline' else labels
    if a.shape == 'circle':
        bg_i = len(names)
        bg = a.bg if a.colors > 2 else 'white'
        names = names + [bg]            # its own label even when it shares a colour: the line traces the outline
        labels[(~subj) & face] = bg_i
        centres = np.vstack([centres, to_lab(hex_rgb(FILAMENTS[bg][0])[None])])
    contrast = np.sqrt(((centres[:, None] - centres[None]) ** 2).sum(-1))
    Image.fromarray(np.asarray(im.resize((n, n)))).save(out / 'input.png')
    L, grid, grown = cleanup(labels, face, spec, contrast)
    ps = pieces(L, face, grid, spec, names)
    outline = back_outline(face, spec)
    render(ps, spec, out / 'preview.png', outline)
    write_svg(ps, spec, out / 'layers.svg', outline)
    by = {}
    for p in ps:
        b = by.setdefault(p['color'], {'pieces': 0, 'area_mm2': 0.0, 'pins': 0})
        b['pieces'] += 1
        b['area_mm2'] += round(p['area_mm2'], 1)
        b['pins'] += len(p['pins'])
    rep = {'size_mm': spec.size, 'colors': by, 'pieces': len(ps), 'grown_features': grown,
           'smallest_piece_mm2': round(min(p['area_mm2'] for p in ps), 1),
           'on_shelf': {c: FILAMENTS[c][1] for c in by}}
    (out / 'report.json').write_text(json.dumps(rep, indent=1))
    if a.stl:
        write_stl(ps, spec, out, outline, face)
    print(json.dumps(rep))


if __name__ == '__main__':
    main()
