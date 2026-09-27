"""Lay out the harvested asterisks as black filled outlines (glyphs.jsonl -> two SVG sheets).

Every glyph is scaled to fit its cell (shape, not size, is what's being compared), with the
transform baked into the path so the file opens as plain outlines. Near-identical shapes are
grouped by rasterizing at 40x40 and comparing overlap; the distinct sheet shows one per group.
"""
import json, re, sys, os
import numpy as np
from PIL import Image, ImageDraw
from xml.sax.saxutils import escape

HERE = os.path.dirname(__file__)
recs = [json.loads(l) for l in open(os.path.join(HERE, '..', '..', '.cache', 'asterisks', 'glyphs.jsonl'))]
recs = [r for r in recs if 'd' in r]
recs.sort(key=lambda r: r['family'].lower())

TOK = re.compile(r'[MLHVQCZ]|-?[\d.]+(?:e-?\d+)?')
def contours(d):
    """Parse SVGPathPen output (absolute M L H V Q C Z, with implicit repeats) into contours
    of M/L/Q/C segments."""
    toks = TOK.findall(d); i = 0; out = []; cur = None; pos = [0, 0]; cmd = None
    size = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'Q': 4, 'C': 6, 'Z': 0}
    while i < len(toks):
        if toks[i] in size: cmd = toks[i]; i += 1
        elif cmd == 'M': cmd = 'L'   # numbers after an M's pair are line-tos
        n = size[cmd]
        args = [float(t) for t in toks[i:i + n]]; i += n
        if cmd == 'M': cur = [('M', args)]; out.append(cur); pos = args
        elif cmd == 'Z': cur.append(('Z', [])); cmd = None
        elif cmd == 'H': pos = [args[0], pos[1]]; cur.append(('L', pos))
        elif cmd == 'V': pos = [pos[0], args[0]]; cur.append(('L', pos))
        else: cur.append((cmd, args)); pos = args[-2:]
    return out

def flatten(cs, steps=8):
    polys = []
    for cont in cs:
        pts = []; p = None
        for c, a in cont:
            if c == 'M': p = a; pts.append(tuple(a))
            elif c == 'L': p = a; pts.append(tuple(a))
            elif c == 'Q':
                for t in np.linspace(0, 1, steps)[1:]:
                    pts.append(tuple((1-t)**2*np.array(p) + 2*(1-t)*t*np.array(a[:2]) + t*t*np.array(a[2:])))
                p = a[2:]
            elif c == 'C':
                for t in np.linspace(0, 1, steps)[1:]:
                    pts.append(tuple((1-t)**3*np.array(p) + 3*(1-t)**2*t*np.array(a[:2]) + 3*(1-t)*t*t*np.array(a[2:4]) + t**3*np.array(a[4:])))
                p = a[4:]
        if len(pts) > 2: polys.append(pts)
    return polys

def fit(r, size, pad):
    x0, y0, x1, y1 = r['bounds']; s = (size - 2 * pad) / max(x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return lambda x, y: (size / 2 + (x - cx) * s, size / 2 - (y - cy) * s)

def path_at(r, size, pad, ox, oy):
    f = fit(r, size, pad); out = []
    for cont in contours(r['d']):
        for c, a in cont:
            if c == 'Z': out.append('Z'); continue
            pts = [f(a[k], a[k + 1]) for k in range(0, len(a), 2)]
            out.append(c + ' '.join(f'{x + ox:.1f} {y + oy:.1f}' for x, y in pts))
    return ''.join(out)

def raster(r, n=40):
    f = fit(r, n, 2); img = Image.new('L', (n, n), 0); d = ImageDraw.Draw(img)
    for poly in flatten(contours(r['d'])):
        d.polygon([f(x, y) for x, y in poly], fill=255)
    return np.asarray(img) > 127

masks = [raster(r) for r in recs]
groups = []  # [rep index, members]
for i, m in enumerate(masks):
    for g in groups:
        rm = masks[g[0]]; iou = (m & rm).sum() / max(1, (m | rm).sum())
        if iou > .82: g[1].append(i); break
    else: groups.append([i, [i]])
print(f'{len(recs)} glyphs, {len(groups)} distinct groups')

def sheet(items, cols, cell, label, name, title):
    rows = (len(items) + cols - 1) // cols; lh = label * 2.6
    W, H = cols * cell, rows * (cell + lh) + 80
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           f'<rect width="{W}" height="{H}" fill="#fff"/>',
           f'<text x="20" y="48" font-family="Helvetica, Arial, sans-serif" font-size="28">{escape(title)}</text>']
    for k, (r, note) in enumerate(items):
        ox, oy = (k % cols) * cell, 80 + (k // cols) * (cell + lh)
        fid = re.sub(r'[^A-Za-z0-9]+', '-', r['family']).strip('-')
        out.append(f'<g id="{fid}"><path d="{path_at(r, cell, cell * .16, ox, oy)}" fill="#000"/>'
                   f'<text x="{ox + cell / 2:.1f}" y="{oy + cell + label * 1.1:.1f}" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="{label}" fill="#555">{escape(r["family"])}{escape(note)}</text></g>')
    out.append('</svg>')
    open(os.path.join(sys.argv[1], name), 'w').write('\n'.join(out) + '\n')

sheet([(r, '') for r in recs], 40, 64, 6, 'asterisks-all.svg', f'The asterisk (*) in every Google Fonts family: {len(recs)} families, each scaled to fit its cell')
reps = sorted(groups, key=lambda g: -len(g[1]))
sheet([(recs[g[0]], f' +{len(g[1]) - 1}' if len(g[1]) > 1 else '') for g in reps], 16, 120, 9, 'asterisks-distinct.svg',
      f'{len(groups)} distinct asterisks from {len(recs)} Google Fonts families (most common first; +N = look-alikes)')
json.dump([[recs[g[0]]['family'], [recs[i]['family'] for i in g[1]]] for g in reps], open(os.path.join(sys.argv[1], 'asterisks-groups.json'), 'w'), indent=0)
