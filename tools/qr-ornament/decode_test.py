"""Can a phone read it? Simulated photos of each snowflake variant, run through real QR decoders.

    PY=~/work/lab/lithophane-maker/.venv/bin/python
    DYLD_LIBRARY_PATH=/opt/homebrew/lib $PY tools/qr-ornament/decode_test.py OUT_DIR [--module 2.0] [--text ...]

Each scenario renders the ornament's front from its thickness map, then degrades the picture over a grid
(module size in camera pixels x blur x tilt, plus sensor noise) and asks three decoders for the text:
zbar, OpenCV's QRCodeDetector and OpenCV's ArUco-based detector. A pass is the exact text from any of
them. Phone decoders (iOS Vision, Google ML Kit) are stronger than these, so a pass here is conservative;
the light model is not. How much light white PLA actually lets through, and how far it spreads inside
the plastic, are guesses bracketed by the k and spread values below until a print is measured.

Scenarios:
- control: a perfect black-on-white print of the same code and layout, no bridges
- stencil/<bg>: white plate (albedo 0.85) lying on a background of the given brightness, lit from the
  front; tilting the camera shows the hole walls (plate thickness x tan(tilt))
- relief/back k=<k> amb=<a>: held up to a light. Transmission exp(-k * thickness), blurred by the
  spread inside the plastic; amb is front room light relative to the backlight
- relief/front: no backlight, raking light from 45 degrees: only shadows of the raised modules
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import snowflake as sf  # noqa: E402

PPM = 10                       # render resolution, px per mm
MODULE_PX = [4, 6, 10]         # camera pixels per module
BLUR = [0.0, 1.0, 1.8]         # camera blur sigma, in camera pixels
TILT = [0, 25, 40]             # degrees off straight-on
RNG = np.random.default_rng(7)


def decoders():
    from pyzbar import pyzbar
    det, aru = cv2.QRCodeDetector(), cv2.QRCodeDetectorAruco()

    def zbar(img):
        return [r.data.decode('utf-8', 'replace') for r in pyzbar.decode(img, symbols=[pyzbar.ZBarSymbol.QRCODE])]

    def ocv(img):
        t, _, _ = det.detectAndDecode(img)
        return [t] if t else []

    def ocv_aruco(img):
        t, _, _ = aru.detectAndDecode(img)
        return [t] if t else []
    return {'zbar': zbar, 'opencv': ocv, 'aruco': ocv_aruco}


def mask(geom, bounds):
    return np.asarray(sf.raster(geom, bounds, PPM)) > 0


def shift_y(a, px):
    out = np.zeros_like(a)
    if px <= 0:
        return a.copy()
    out[px:] = a[:-px]
    return out


def gblur_mm(img, mm):
    s = mm * PPM
    return cv2.GaussianBlur(img, (0, 0), s) if s > 0 else img


def scene(kind, model, args, bounds, tilt, **kw):
    """Brightness image (0..1) at PPM, before the camera."""
    out = mask(model['outline'], bounds)
    if kind == 'control':
        img = np.where(out, 0.9, 0.35)
        img[mask(model['dark'], bounds)] = 0.05
        return img
    if kind == 'stencil':
        mat = mask(model['material'], bounds)
        bg = kw['bg']
        img = np.full(mat.shape, bg, float)
        img[mat] = 0.85
        wall = shift_y(mat, int(round(args.plate * np.tan(np.radians(tilt)) * PPM))) & ~mat
        img[wall] = 0.6                                      # the hole walls, half lit
        return img
    up = mask(model['raised'], bounds) & out
    t = out * args.backing + up * (args.relief - args.backing)
    if kind == 'relief_back':
        trans = np.where(out, np.exp(-kw['k'] * t), 1.0)
        trans = gblur_mm(trans.astype(np.float32), kw['spread'])
        img = trans + kw['amb'] * np.where(out, 0.85, 0.3)
        inside = img[out & ~up]
        return np.clip(img / np.percentile(inside, 90) * 0.9, 0, 1)   # auto-exposure on the glow
    if kind == 'relief_front':
        h = args.relief - args.backing
        shadow = shift_y(up, int(round(h / np.tan(np.radians(45)) * PPM))) & ~up & out
        img = np.where(out, 0.8, 0.35)
        img[shadow] = 0.35
        img[up] = 0.8
        return img
    raise ValueError(kind)


def camera(img, module_px, blur, tilt, module_mm):
    scale = module_px / (module_mm * PPM)
    h, w = img.shape
    small = cv2.resize(img.astype(np.float32), (max(1, int(w * scale)), max(1, int(h * scale))),
                       interpolation=cv2.INTER_AREA)
    if tilt:
        h, w = small.shape
        c = np.cos(np.radians(tilt))
        k = 0.12 * np.sin(np.radians(tilt))
        src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        dst = np.float32([[w * k, 0], [w * (1 - k), 0], [w, h * c], [0, h * c]])
        M = cv2.getPerspectiveTransform(src, dst)
        small = cv2.warpPerspective(small, M, (w, int(h * c) + 1), borderValue=float(small[0, 0]))
    pad = int(8 * module_px)
    small = cv2.copyMakeBorder(small, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=float(small[0, 0]))
    if blur:
        small = cv2.GaussianBlur(small, (0, 0), blur)
    small = small + RNG.normal(0, 0.02, small.shape)
    return (np.clip(small, 0, 1) * 255).astype(np.uint8)


def run(args):
    args.out.mkdir(parents=True, exist_ok=True)
    dark, version, ecc = sf.qr_matrix(args.text, 'm')
    ns = argparse.Namespace(**{**sf_defaults(), 'module': args.module, 'text': args.text, 'plate': args.plate})
    models = {}
    for v in ('stencil', 'relief'):
        ns.variant_now = v
        models[v] = sf.build(ns, dark)
    bounds = models['stencil']['outline'].buffer(6).bounds
    scenarios = [('control', 'control', 'stencil', {})]
    only = args.only
    for name, bg in [('black', 0.05), ('tree green', 0.15), ('wood/hand', 0.35), ('mid grey', 0.5)]:
        scenarios.append((f'stencil on {name} ({bg})', 'stencil', 'stencil', {'bg': bg}))
    for k, spread, amb in [(1.2, 0.3, 0.0), (1.2, 0.3, 0.3), (1.2, 0.3, 1.0), (0.8, 0.6, 0.3),
                           (0.8, 0.6, 1.0), (0.5, 1.0, 0.3), (0.5, 1.0, 1.0)]:
        scenarios.append((f'relief backlit k={k} spread={spread}mm amb={amb}', 'relief_back', 'relief',
                          {'k': k, 'spread': spread, 'amb': amb}))
    scenarios.append(('relief front-lit only (raking 45deg)', 'relief_front', 'relief', {}))
    scenarios = [s for s in scenarios if not only or s[1] in only.split(',')]
    dec = decoders()
    results = []
    samples = []
    for label, kind, var, kw in scenarios:
        model = models[var]
        cache = {}
        row = {'scenario': label, 'pass': 0, 'total': 0, 'by_decoder': {d: 0 for d in dec}, 'fails': []}
        for mpx, blur, tilt in itertools.product(MODULE_PX, BLUR, TILT):
            if tilt not in cache:
                cache[tilt] = scene(kind, model, ns, bounds, tilt, **kw)
            img = camera(cache[tilt], mpx, blur, tilt, args.module)
            ok = False
            for dn, fn in dec.items():
                if args.text in fn(img):
                    row['by_decoder'][dn] += 1
                    ok = True
            row['total'] += 1
            row['pass'] += ok
            if not ok:
                row['fails'].append(f'{mpx}px blur{blur} tilt{tilt}')
            if mpx == 6 and blur == 1.0 and tilt == 25:
                samples.append((label, img))
        results.append(row)
        print(f"{row['pass']:2d}/{row['total']}  {label}   {row['by_decoder']}", flush=True)
    rep = {'text': args.text, 'version': version, 'modules': int(dark.shape[0]), 'module_mm': args.module,
           'stencil_bridges': models['stencil']['bridges'], 'stencil_parts': models['stencil']['parts'],
           'size_mm': models['stencil']['size_mm'], 'results': results}
    (args.out / 'decode-report.json').write_text(json.dumps(rep, indent=2))
    contact_sheet(samples, args.out / 'decode-samples.jpg')
    return rep


def sf_defaults():
    return dict(rim=3.0, quiet=3, bridge=0.8, plate=2.0, backing=0.6, relief=3.0, deboss=0.6, text_h=6.0,
                name='Sam', year=2026, ecc='m')


def contact_sheet(samples, path):
    from PIL import ImageDraw
    tiles = []
    for label, img in samples:
        im = Image.fromarray(img).convert('RGB')
        im.thumbnail((360, 420))
        t = Image.new('RGB', (360, 450), 'white')
        t.paste(im, ((360 - im.width) // 2, 28))
        ImageDraw.Draw(t).text((6, 6), label[:58], fill='black')
        tiles.append(t)
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * 360, rows * 450), 'white')
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * 360, (i // cols) * 450))
    sheet.save(path, quality=88)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('out', type=Path)
    ap.add_argument('--module', type=float, default=2.0)
    ap.add_argument('--text', default='Your Secret Santa is Sally! Make it merry.')
    ap.add_argument('--plate', type=float, default=2.0, help='stencil thickness, mm')
    ap.add_argument('--only', default='', help='comma list of kinds: control,stencil,relief_back,relief_front')
    run(ap.parse_args())
