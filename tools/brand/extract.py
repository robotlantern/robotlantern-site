"""Turn RJ's brand SVGs (design/brand/) into the data the site draws from (src/data/brand.json).

The SVG files are the source; rerun this after editing them in Affinity:

    python3 tools/brand/extract.py

Each wordmark is 15 paths: 14 letters and the period (the ovaloid). The "t" of "Lantern" is
two paths (its hook and its base); with the ovaloid beside it, it's the monogram. Paths are
identified by position, so a re-export that keeps the shapes keeps working.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'design' / 'brand'
NUM = re.compile(r'-?\d*\.?\d+(?:e-?\d+)?')


def svg(name):
    s = (SRC / name).read_text()
    w = float(re.search(r'width="([\d.]+)px"', s).group(1))
    h = float(re.search(r'height="([\d.]+)px"', s).group(1))
    if 'transform=' in s:
        sys.exit(f'{name}: has transforms; export with "flatten transforms" on')
    paths = re.findall(r'<path d="([^"]+)"', s)
    return w, h, paths


def box(d):
    """Bounding box of an absolute path's coordinates (control points included: close enough
    to tell the pieces apart)."""
    xs, ys = [], []
    for cmd in re.finditer(r'([MLCQZ])([^MLCQZ]*)', d):
        nums = [float(n) for n in NUM.findall(cmd.group(2))]
        xs += nums[0::2]
        ys += nums[1::2]
    return [min(xs), min(ys), max(xs), max(ys)]


def wordmark(name):
    w, h, paths = svg(name)
    boxes = [box(d) for d in paths]
    # The period is the last glyph: the rightmost box's path.
    period = max(range(len(paths)), key=lambda i: boxes[i][2])
    letters = [d for i, d in enumerate(paths) if i != period]
    # The t of "Lantern": the two narrow pieces (hook above base) sharing an x range, lowest
    # on the page among such pairs and furthest right.
    pieces = sorted(((b, i) for i, b in enumerate(boxes) if i != period and b[2] - b[0] < 40), key=lambda t: (t[0][0], t[0][1]))
    pairs = [(a, b) for a in pieces for b in pieces if a[1] != b[1] and abs(a[0][0] - b[0][0]) < 2 and b[0][1] > a[0][3]]
    hook, base = max(pairs, key=lambda p: (p[0][0][1], p[0][0][0]))
    return {
        'width': w, 'height': h, 'letters': letters, 'period': paths[period], 'periodBox': boxes[period],
        't': {'hook': paths[hook[1]], 'base': paths[base[1]], 'hookBox': hook[0], 'baseBox': base[0]},
    }


def main():
    ow, oh, [ovaloid] = svg('skewed-ovaloid.svg')
    mw, mh, mono = svg('monogram-logo-bw.svg')
    mboxes = [box(d) for d in mono]
    dot = max(range(3), key=lambda i: mboxes[i][2])
    rest = sorted((i for i in range(3) if i != dot), key=lambda i: mboxes[i][1])
    out = {
        'source': 'design/brand/*.svg, via tools/brand/extract.py',
        'ovaloid': {'width': ow, 'height': oh, 'd': ovaloid, 'box': box(ovaloid)},
        'monogram': {'width': mw, 'height': mh, 'hook': mono[rest[0]], 'base': mono[rest[1]], 'dot': mono[dot],
                     'hookBox': mboxes[rest[0]], 'baseBox': mboxes[rest[1]], 'dotBox': mboxes[dot]},
        'twoLine': wordmark('wordmark-two-lines.svg'),
        'landscape': wordmark('wordmark-landscape.svg'),
    }
    (ROOT / 'src' / 'data' / 'brand.json').write_text(json.dumps(out, indent=1) + '\n')
    for k in ('twoLine', 'landscape'):
        print(k, 'period', [round(v, 1) for v in out[k]['periodBox']], 't hook', [round(v, 1) for v in out[k]['t']['hookBox']])
    print('monogram dot', [round(v, 1) for v in out['monogram']['dotBox']])


if __name__ == '__main__':
    main()
