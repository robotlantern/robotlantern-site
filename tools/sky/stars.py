"""Find the stars in RJ's night photo, for the sky map (docs/HOME.md).

Subtracts the sky background, finds local peaks, and ranks them by brightness. Positions are
fractions of the photo's width and height, so they survive resizing.

    python3 tools/sky/stars.py public/images/night.jpg src/data/night-stars.json [--preview out.png]
"""
import json
import sys

import numpy as np
from PIL import Image, ImageDraw


def box_blur(a, r):
    """Mean over a (2r+1)-square window, via summed-area tables."""
    p = np.pad(a, r + 1, mode='edge').cumsum(0).cumsum(1)
    n = 2 * r + 1
    s = p[n:, n:] - p[:-n, n:] - p[n:, :-n] + p[:-n, :-n]
    return s[: a.shape[0], : a.shape[1]] / (n * n)


def find_stars(path, keep=400):
    img = Image.open(path).convert('RGB')
    rgb = np.asarray(img, dtype=np.float32)
    gray = rgb.mean(axis=2)
    signal = gray - box_blur(gray, 20)
    h, w = gray.shape
    # A peak is the maximum of its 9x9 neighborhood and clearly above the background.
    peak = np.full_like(signal, -1e9)
    padded = np.pad(signal, 4, mode='constant', constant_values=-1e9)
    for dy in range(9):
        for dx in range(9):
            np.maximum(peak, padded[dy : dy + h, dx : dx + w], out=peak)
    threshold = np.percentile(signal, 99.5)
    ys, xs = np.nonzero((signal == peak) & (signal > threshold))
    flux = box_blur(np.clip(signal, 0, None), 2)[ys, xs] * 25
    order = np.argsort(-flux)
    stars, taken = [], []
    for i in order:
        x, y = int(xs[i]), int(ys[i])
        if any((x - a) ** 2 + (y - b) ** 2 < 64 for a, b in taken):
            continue
        taken.append((x, y))
        r, g, b = rgb[max(0, y - 1) : y + 2, max(0, x - 1) : x + 2].reshape(-1, 3).mean(0)
        stars.append({'x': round(x / w, 4), 'y': round(y / h, 4), 'flux': round(float(flux[i]), 1),
                      'color': '#%02x%02x%02x' % (int(r), int(g), int(b))})
        if len(stars) == keep:
            break
    top = stars[0]['flux']
    for s in stars:
        s['mag'] = round(-2.5 * np.log10(s['flux'] / top), 2)  # relative, 0 = brightest
    return img, stars


def main():
    src, out = sys.argv[1], sys.argv[2]
    img, stars = find_stars(src)
    for i, s in enumerate(stars):
        s['id'] = i
    json.dump({'source': src.split('/')[-1], 'width': img.width, 'height': img.height, 'stars': stars},
              open(out, 'w'), indent=1)
    print(f'{len(stars)} stars -> {out}')
    if '--preview' in sys.argv:
        prev = img.copy()
        d = ImageDraw.Draw(prev)
        for s in stars[:150]:
            x, y = s['x'] * img.width, s['y'] * img.height
            r = 14 if s['id'] < 40 else 9
            d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 170, 60) if s['id'] < 40 else (90, 160, 255), width=2)
            if s['id'] < 60:
                d.text((x + r + 2, y - 6), str(s['id']), fill=(255, 220, 150))
        prev.save(sys.argv[sys.argv.index('--preview') + 1])


if __name__ == '__main__':
    main()
