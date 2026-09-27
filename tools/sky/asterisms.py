"""Fit each section's icon to real stars in the night photo (docs/HOME.md, "Asterism icons").

Each icon is a template: a few points plus the lines between them. For every placement of a
template (position within the section's region of the sky, size, a small rotation), each
point snaps to its nearest star. The placement whose stars sit closest to the shape, with a
small preference for bright stars, wins. The result lists the chosen stars and the lines.

    python3 tools/sky/asterisms.py src/data/night-stars.json src/data/asterisms.json [--preview in.jpg out.png]
"""
import json
import math
import sys

import numpy as np

# Points in a unit box centered on 0 (y down), and lines as index pairs.
def loop(a, b):
    return [(i, i + 1) for i in range(a, b)] + [(b, a)]

TEMPLATES = {
    'thoughts': {  # a cloud with two trailing dots
        'points': [(-.40, .05), (-.42, -.2), (-.2, -.38), (.05, -.42), (.3, -.33), (.42, -.1), (.3, .12), (0, .15),
                   (-.3, .3), (-.42, .45)],
        'lines': loop(0, 7),
    },
    'chats': {  # a speech bubble with a tail, and a second one behind it
        'points': [(-.5, -.4), (.1, -.4), (.1, .05), (-.28, .05), (-.42, .22), (-.5, .05),
                   (.25, -.15), (.5, -.15), (.5, .3), (.38, .3), (.42, .45)],
        'lines': loop(0, 5) + [(6, 7), (7, 8), (8, 9), (9, 10)],
    },
    'builds': {  # a block on top of two
        'points': [(-.22, -.5), (.22, -.5), (.22, -.05), (-.22, -.05),
                   (-.5, .05), (.5, .05), (.5, .5), (-.5, .5), (0, .05), (0, .5)],
        'lines': loop(0, 3) + loop(4, 7) + [(8, 9)],
    },
    'shop': {  # a bag with a handle
        'points': [(-.4, -.15), (.4, -.15), (.32, .5), (-.32, .5), (-.18, -.15), (-.15, -.42), (.15, -.42), (.18, -.15)],
        'lines': loop(0, 3) + [(4, 5), (5, 6), (6, 7)],
    },
}

# Where each section may sit, as fractions of the photo (x0, y0, x1, y1). Chats take the
# Pleiades' neighborhood.
REGIONS = {
    'thoughts': (.05, .05, .5, .42),
    'shop': (.6, .06, .9, .2),
    'chats': (.5, .4, .75, .6),
    'builds': (.1, .6, .9, .9),
}


def fit(name, stars_px, mags, W, H, used):
    t = np.array(TEMPLATES[name]['points'])
    x0, y0, x1, y1 = REGIONS[name]
    best = None
    free = np.array([k not in used for k in range(len(stars_px))])
    for s in np.linspace(.12 * W, (.3 if name == 'builds' else .22) * W, 7):
        for deg in range(-25, 26, 5):
            a = math.radians(deg)
            rot = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
            shape = t @ rot.T * s
            cx = np.arange(x0 * W, x1 * W, 18)
            cy = np.arange(y0 * H, y1 * H, 18)
            centers = np.stack(np.meshgrid(cx, cy), -1).reshape(-1, 2)
            pts = centers[:, None, :] + shape[None, :, :]                  # C x n x 2
            d = np.linalg.norm(pts[:, :, None, :] - stars_px[None, None], axis=-1)  # C x n x K
            d[:, :, ~free] = 1e9  # a star belongs to one asterism
            near = d.argmin(-1)
            nd = d.min(-1)
            rms = np.sqrt((nd ** 2).mean(-1)) / s
            dup = np.array([len(r) - len(set(r)) for r in near])
            cost = rms + .5 * dup + .01 * mags[near].mean(-1)
            i = cost.argmin()
            if best is None or cost[i] < best[0]:
                best = (float(cost[i]), pts[i], float(rms[i]))
    cost, pts, rms = best
    # Final assignment: each point takes its nearest star not already taken.
    d = np.linalg.norm(pts[:, None, :] - stars_px[None], axis=-1)
    chosen = []
    for i in np.argsort(d.min(1)):
        for k in np.argsort(d[i]):
            if k not in chosen and k not in used:
                chosen.append(int(k)); break
    order = [None] * len(pts)
    for i, k in zip(np.argsort(d.min(1)), chosen):
        order[int(i)] = k
    return order, rms


def main():
    data = json.load(open(sys.argv[1]))
    W, H = data['width'], data['height']
    stars = data['stars'][:260]
    px = np.array([[s['x'] * W, s['y'] * H] for s in stars])
    mags = np.array([s['mag'] for s in stars])
    out = {'source': data['source'], 'width': W, 'height': H, 'asterisms': {}}
    used = set()
    for name in TEMPLATES:
        order, rms = fit(name, px, mags, W, H, used)
        used.update(order)
        out['asterisms'][name] = {
            'stars': [{k: stars[i][k] for k in ('id', 'x', 'y', 'mag')} for i in order],
            'lines': TEMPLATES[name]['lines'],
            'fit': round(rms, 3),
        }
        print(f'{name}: fit {rms:.3f}, stars {[stars[i]["id"] for i in order]}')
    json.dump(out, open(sys.argv[2], 'w'), indent=1)
    if '--preview' in sys.argv:
        from PIL import Image, ImageDraw
        i = sys.argv.index('--preview')
        img = Image.open(sys.argv[i + 1]).convert('RGB')
        dr = ImageDraw.Draw(img)
        for name, a in out['asterisms'].items():
            p = [(s['x'] * W, s['y'] * H) for s in a['stars']]
            for u, v in a['lines']:
                dr.line([p[u], p[v]], fill=(255, 200, 120), width=3)
            for x, y in p:
                dr.ellipse([x - 9, y - 9, x + 9, y + 9], outline=(120, 190, 255), width=3)
            dr.text((p[0][0], p[0][1] - 40), name, fill=(255, 230, 180))
        img.save(sys.argv[i + 2])


if __name__ == '__main__':
    main()
