"""Secret Santa snowflake, round and dotted (prototype, 2026-11-19). Successor to snowflake.py's diamond.

    PY=~/work/lab/lithophane-maker/.venv/bin/python
    $PY tools/qr-ornament/dotflake.py OUT_DIR --text "Your Secret Santa is Sally!" --name SAM --year 2026 \
        [--variant stencil|relief|both] [--module 2.0] [--stl]

A disc carrying a QR code drawn as dots, with six arms grown from a seed (the giver's name and the year,
unless --seed is given), so no two ornaments share arms. The loop is on the tip of the top arm. On the
back, the giver's name runs along the bottom of the disc and the year along the top, debossed and
mirrored so they read from behind.

The code: each dark module is a round dot; the three finder patterns are rounded "eyes" (a scanner finds
them by the stripes through their centre, so they stay solid). Space between the code's corners and the
disc's edge is left plain at top and bottom (the lettering is behind it) and dotted at random at left and
right, so the code reads as a round pattern rather than a square.

- stencil: a light plate with a hole per dot. Dots are separate holes, so the plate stays in one piece
  with no bridges except two diagonal ties into each eye's light ring. Dots shrink as needed to keep at
  least --web of plastic between neighbours.
- relief: a thin backing with raised dots and eyes, a thick rim, thick top and bottom caps (for the
  lettering) and thick arms; scanned held up to a light.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

import snowflake as sf   # qr_matrix, text_geom, raster, write_stl


def rounded(b, r):
    return b.buffer(-r, join_style=2).buffer(r, 32) if r > 0 else b


def defaults():
    return dict(module=2.0, quiet=2, margin=1.5, dot=0.85, web=0.7, plate=1.6, backing=0.6, relief=3.0,
                rim=2.0, deboss=0.6, text_h=4.5, fill=0.45, arm=1.0, name='SAM', year=2026, seed=None,
                ecc='m', bridge=0.8, eye_r=0.5)


# --- arms -------------------------------------------------------------------------------------------

def make_arm(rng, scale=1.0):
    """One arm in local coordinates: base at the origin, pointing up (+y). Mirror-symmetric, as real
    snowflake arms are. Returns (geometry, tip y)."""
    L = rng.uniform(14, 20) * scale
    w = 3.0
    parts = [LineString([(0, -2), (0, L)]).buffer(w / 2, cap_style=1)]
    nb = rng.choice([2, 2, 3])
    ts = sorted(rng.uniform(0.28, 0.85) for _ in range(nb))
    for i, t in enumerate(ts):
        y = t * L
        bl = rng.uniform(0.28, 0.5) * L * (1.05 - 0.45 * t)
        bw = rng.uniform(2.2, 2.6)
        ang = math.radians(rng.choice([60, 60, 55, 65]))
        for s in (1, -1):
            end = (s * bl * math.sin(ang), y + bl * math.cos(ang))
            parts.append(LineString([(0, y), end]).buffer(bw / 2, cap_style=1))
            if bl > 6 and rng.random() < 0.45:               # a twig off the branch, parallel to the spine
                mx, my = s * bl * 0.55 * math.sin(ang), y + bl * 0.55 * math.cos(ang)
                parts.append(LineString([(mx, my), (mx, my + bl * 0.4)]).buffer(1.1, cap_style=1))
        if rng.random() < 0.25:                              # a small plate at the node
            parts.append(hexagon(0, y, rng.uniform(2.2, 3.0)))
    tip = rng.choice(['point', 'hex', 'fork'])
    if tip == 'hex':
        parts.append(hexagon(0, L, rng.uniform(2.6, 3.6)))
    elif tip == 'fork':
        fl = rng.uniform(3, 5)
        for s in (1, -1):
            parts.append(LineString([(0, L - 1), (s * fl * 0.6, L - 1 + fl * 0.8)]).buffer(1.1, cap_style=1))
    if rng.random() < 0.35:                                  # a hexagon where the arm leaves the disc
        parts.append(hexagon(0, 2.5, rng.uniform(3.0, 4.0)))
    return unary_union(parts), L


def hexagon(x, y, r):
    return Polygon([(x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a)))
                    for a in range(90, 450, 60)])


# --- lettering along an arc (built as seen from the back, y up) -------------------------------------

def arc_text(text, r_base, h, bottom, max_deg):
    """Characters along a circle of radius r_base (their baseline), centred on the bottom or top."""
    glyphs = []
    for ch in text:
        if ch == ' ':
            glyphs.append((None, h * 0.35))
            continue
        g = sf.text_geom(ch, h)
        g = affinity.scale(g, 1, -1, origin=(0, 0))
        w, gh = g.bounds[2] - g.bounds[0], g.bounds[3] - g.bounds[1]
        g = affinity.translate(g, -g.bounds[0] - w / 2, -g.bounds[1])   # baseline centre at the origin
        glyphs.append((g, w))
    track = h * 0.12
    total = sum(w for _, w in glyphs) + track * (len(glyphs) - 1)
    r_mid = r_base - h / 2 if bottom else r_base + h / 2
    span = math.degrees(total / r_mid)
    if span > 2 * max_deg:
        return None
    out, s = [], -total / 2
    for g, w in glyphs:
        phi = (s + w / 2) / r_mid
        s += w + track
        if g is None:
            continue
        if bottom:
            p = (r_base * math.sin(phi), -r_base * math.cos(phi))
            out.append(affinity.translate(affinity.rotate(g, phi, origin=(0, 0), use_radians=True), *p))
        else:
            p = (r_base * math.sin(phi), r_base * math.cos(phi))
            out.append(affinity.translate(affinity.rotate(g, -phi, origin=(0, 0), use_radians=True), *p))
    return unary_union(out)


def fit_arc_text(text, r_base, h, bottom, max_deg):
    while h > 2.5:
        g = arc_text(text, r_base, h, bottom, max_deg)
        if g is not None:
            return g, h
        h -= 0.25
    raise SystemExit(f'"{text}" does not fit on the arc')


# --- the ornament (built y up, centred on the origin; flipped to y down at the end) ------------------

def build(args, dark):
    m, n, q = args.module, dark.shape[0], args.quiet
    h = n * m / 2
    R = h * math.sqrt(2) + args.margin * m
    hq = h + q * m                                      # half-side of the quiet square
    disc = Point(0, 0).buffer(R, 128)
    cx = lambda c: (c - n / 2 + 0.5) * m                 # module centre, y up
    cy = lambda r: (n / 2 - r - 0.5) * m
    stencil = args.variant_now == 'stencil'
    d = min(args.dot * m, m - args.web) if stencil else args.dot * m
    finders = [(0, 0), (0, n - 7), (n - 7, 0)]
    in_finder = lambda r, c: any(r0 <= r < r0 + 7 and c0 <= c < c0 + 7 for r0, c0 in finders)
    dots = [Point(cx(c), cy(r)).buffer(d / 2, 24) for r in range(n) for c in range(n)
            if dark[r, c] and not in_finder(r, c)]
    rings, centres, ties = [], [], []
    for r0, c0 in finders:
        fx, fy = cx(c0 + 3), cy(r0 + 3)
        ro = args.eye_r * m                          # eye corner radius; 0 = square
        ri, rc = ro * 0.7, ro * 0.5
        outer = rounded(box(fx - 3.5 * m, fy - 3.5 * m, fx + 3.5 * m, fy + 3.5 * m), ro)
        inner = rounded(box(fx - 2.5 * m, fy - 2.5 * m, fx + 2.5 * m, fy + 2.5 * m), ri)
        rings.append(outer.difference(inner))
        centres.append(rounded(box(fx - 1.5 * m, fy - 1.5 * m, fx + 1.5 * m, fy + 1.5 * m), rc))
        di = (2.5 * m - ri) * math.sqrt(2) + ri
        do = (3.5 * m - ro) * math.sqrt(2) + ro
        for sx, sy in [(1, 1), (-1, -1)]:
            u = (sx / math.sqrt(2), sy / math.sqrt(2))
            a, b = di - 0.4 * m, do + 0.4 * m
            ties.append(LineString([(fx + u[0] * a, fy + u[1] * a), (fx + u[0] * b, fy + u[1] * b)])
                        .buffer(args.bridge / 2, cap_style=2))
    # random dots in the left and right caps, on the module grid
    seed = args.seed if args.seed is not None else f'{args.name}|{args.year}'
    rng = random.Random(int(hashlib.sha256(f'{seed}|dots'.encode()).hexdigest()[:12], 16))
    arm_rng = random.Random(int(hashlib.sha256(f'{seed}|arms'.encode()).hexdigest()[:12], 16))
    deco = []
    k = int(R / m) + 2
    for r in range(-k, n + k):
        for c in range(-k, n + k):
            x, y = cx(c), cy(r)
            if abs(x) <= hq or abs(y) > hq + 0.5 * m:
                continue
            if math.hypot(x, y) + d / 2 > R - args.rim - 0.6 * m:
                continue
            if rng.random() < args.fill:
                deco.append(Point(x, y).buffer(d / 2, 24))
    dark_shapes = unary_union(dots + rings + centres + deco)
    # arms
    arm, L = make_arm(arm_rng, args.arm)
    arms = []
    for ang in (90, 30, -30, -90, -150, 150):
        a = affinity.translate(arm, 0, R - 1.5)
        arms.append(affinity.rotate(a, ang - 90, origin=(0, 0)))
    top_tip = R - 1.5 + L
    loop_r, hole_r = 4.5, 2.2
    loop = Point(0, top_tip + loop_r - 1.0).buffer(loop_r, 48)
    hole = Point(0, top_tip + loop_r - 1.0).buffer(hole_r, 48)
    outline = unary_union([disc, loop] + arms).difference(hole)
    # lettering in the top and bottom caps, as seen from the back, then mirrored to the front
    cap_deg = math.degrees(math.acos(min(1, (hq + 0.8 * m) / (R - args.rim - 0.6))))
    name, nh = fit_arc_text(str(args.name).upper(), R - args.rim - 0.6, args.text_h, True, cap_deg * 0.92)
    year, yh = fit_arc_text(str(args.year), R - args.rim - 0.6 - args.text_h, args.text_h, False, cap_deg * 0.92)
    lettering = affinity.scale(unary_union([name, year]), -1, 1, origin=(0, 0))
    caps = disc.difference(box(-R, -hq - 0.5 * m, R, hq + 0.5 * m))
    out = {'outline': outline, 'lettering': lettering, 'dark': dark_shapes, 'R': R,
           'arm_len': round(L, 1), 'name_h': nh, 'dot_mm': round(d, 2)}
    if stencil:
        material = outline.difference(dark_shapes).union(unary_union(ties).intersection(disc))
        out['material'] = material
        out['parts'] = 1 if material.geom_type == 'Polygon' else len(material.geoms)
    else:
        rim = disc.difference(Point(0, 0).buffer(R - args.rim, 128))
        out['raised'] = unary_union([dark_shapes.buffer(0.02), rim, caps,
                                     outline.difference(disc)])
    # y down, origin at the top-left, as snowflake.py's raster and write_stl expect
    for key in ('outline', 'lettering', 'dark', 'material', 'raised'):
        if key in out:
            out[key] = affinity.scale(out[key], 1, -1, origin=(0, 0))
    b = out['outline'].bounds
    out['size_mm'] = [round(b[2] - b[0], 1), round(b[3] - b[1], 1)]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('out', type=Path)
    ap.add_argument('--text', default='Your Secret Santa is Sally! Make it merry.')
    ap.add_argument('--variant', default='both', choices=['stencil', 'relief', 'both'])
    for k, v in defaults().items():
        if k in ('name', 'year', 'seed', 'ecc'):
            ap.add_argument(f'--{k}', default=v)
        else:
            ap.add_argument(f'--{k}', type=float, default=v)
    ap.add_argument('--stl', action='store_true')
    args = ap.parse_args(argv)
    args.quiet = int(args.quiet)
    args.out.mkdir(parents=True, exist_ok=True)
    dark, version, ecc = sf.qr_matrix(args.text, args.ecc)
    report = {'text': args.text, 'version': version, 'modules': int(dark.shape[0]), 'module_mm': args.module,
              'name': args.name, 'year': args.year, 'variants': {}}
    for v in (['stencil', 'relief'] if args.variant == 'both' else [args.variant]):
        args.variant_now = v
        model = build(args, dark)
        r = {k: model[k] for k in ('size_mm', 'arm_len', 'name_h', 'dot_mm') }
        if v == 'stencil':
            r['parts'] = model['parts']
        bnd = model['outline'].buffer(2).bounds
        img = sf.raster(model['outline'], bnd, 10, 235)
        if v == 'stencil':
            img = sf.raster(model['material'], bnd, 10, 235, Image.new('L', img.size, 30))
        else:
            img = sf.raster(model['raised'].intersection(model['outline']), bnd, 10, 90, img)
        img.save(args.out / f'plan-{v}.png')
        if args.stl:
            r['stl'] = sf.write_stl(model, args, args.out / f'{v}.stl')
        report['variants'][v] = r
    (args.out / 'report.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
