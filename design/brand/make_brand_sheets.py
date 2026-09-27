"""Spark concepts and wordmark lockups for the brand work (NOW.md, "Brand mark").

    python3 design/brand/make_brand_sheets.py

Writes sparks.svg (six spark concepts, large and at favicon sizes) and wordmark-lockups.svg
(one line, stacked left, centered and right; each with the period and with a spark). Every
shape is a black filled outline with its geometry baked in, ready to edit in Affinity.
"""
import math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

def arc(cx, cy, r, a0, a1, n=14):
    return [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in [a0 + (a1 - a0) * k / n for k in range(n + 1)]]

def capsule(a, length, w, base=0.0):
    """An arm from the center along angle a (degrees, y down), rounded at the tip."""
    t = math.radians(a); ux, uy = math.cos(t), math.sin(t); px, py = -uy, ux; r = w / 2
    tip = (ux * length, uy * length)
    pts = [(ux * base + px * r, uy * base + py * r)]
    pts += arc(tip[0], tip[1], r, t + math.pi / 2, t - math.pi / 2)
    pts += [(ux * base - px * r, uy * base - py * r)]
    pts += arc(ux * base, uy * base, r, t - math.pi / 2, t - 3 * math.pi / 2)
    return pts

def taper(a, length, w0, w1):
    """A wedge from the center (width w0) to a rounded tip (width w1)."""
    t = math.radians(a); ux, uy = math.cos(t), math.sin(t); px, py = -uy, ux
    tip = (ux * length, uy * length)
    pts = [(px * w0 / 2, py * w0 / 2)] + arc(tip[0], tip[1], w1 / 2, t + math.pi / 2, t - math.pi / 2) + [(-px * w0 / 2, -py * w0 / 2)]
    pts += arc(0, 0, w0 / 2, t - math.pi / 2, t - 3 * math.pi / 2)
    return pts

def petal(a, length, w):
    """A teardrop: point at the center, round at the far end."""
    t = math.radians(a); ux, uy = math.cos(t), math.sin(t); r = w / 2
    c = (ux * (length - r), uy * (length - r))
    return [(0, 0)] + arc(c[0], c[1], r, t - math.pi / 2 - .5, t + math.pi / 2 + .5, 20)

def circle(cx, cy, r):
    return arc(cx, cy, r, 0, 2 * math.pi, 40)[:-1]

def sparkle(lengths, pinch=.13, skew=0):
    """A four-point sparkle with concave sides; lengths for up, right, down, left."""
    tips = [(0, -lengths[0]), (lengths[1], 0), (0, lengths[2]), (-lengths[3], 0)]
    pts = []
    for k in range(4):
        p, q = tips[k], tips[(k + 1) % 4]
        ctrl = ((p[0] + q[0]) * pinch, (p[1] + q[1]) * pinch)
        for s in [i / 16 for i in range(16)]:
            pts.append(((1 - s) ** 2 * p[0] + 2 * (1 - s) * s * ctrl[0] + s * s * q[0], (1 - s) ** 2 * p[1] + 2 * (1 - s) * s * ctrl[1] + s * s * q[1]))
    return [pts]

def shear(shapes, deg):
    k = math.tan(math.radians(deg))
    return [[(x - y * k, y) for x, y in s] for s in shapes]

# The concepts, in a unit box around the center (y down). Names say what each is after.
SPARKS = [
    ('skewed-six', 'Skewed six: RJ\'s nav asterisk, grown uneven and leaning forward',
     shear([capsule(a, l, .3) for a, l in [(-90, 1.0), (-30, .78), (30, .66), (90, .7), (150, .8), (-150, .6)]], 12)),
    ('comet-five', 'Comet five: one long arm trailing down-left, like the period\'s flight',
     [taper(a, l, .42, .16) for a, l in [(135, 1.25), (-160, .72), (-95, .82), (-25, .78), (45, .66)]]),
    ('sparkle', 'Sparkle: a four-point glint, tall and leaning',
     shear(sparkle([1.05, .6, .8, .48]), 10)),
    ('robot-five', 'Robot five: chunky rounded arms from the wordmark\'s own strokes, unevenly set',
     [capsule(a, l, .38) for a, l in [(-90, .92), (-14, .84), (58, .8), (122, .9), (196, .78)]]),
    ('ember', 'Ember: three petals and two sparks flying off',
     [petal(a, l, w) for a, l, w in [(-100, 1.0, .52), (20, .78, .46), (140, .86, .48)]] + [circle(.72, -.72, .11), circle(.98, -.4, .07)]),
    ('lit-period', 'Lit period: the lantern dot, throwing three short rays',
     [circle(-.18, .22, .42)] + [[(x - .18, y + .22) for x, y in capsule(a, l, .16, .6)] for a, l in [(-78, 1.12), (-38, 1.05), (2, .92)]]),
]

def d_of(shapes, s, ox, oy):
    return ''.join('M' + 'L'.join(f'{ox + x * s:.2f} {oy + y * s:.2f}' for x, y in sh) + 'Z' for sh in shapes)

def sparks_sheet():
    W, cell = 1800, 250
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{140 + len(SPARKS) * cell}" viewBox="0 0 {W} {140 + len(SPARKS) * cell}">',
           f'<rect width="{W}" height="{140 + len(SPARKS) * cell}" fill="#fff"/>',
           '<text x="40" y="60" font-family="Helvetica, Arial, sans-serif" font-size="30">Spark concepts: large, then at 64, 32 and 16 px, on light and dark</text>']
    for k, (sid, note, shapes) in enumerate(SPARKS):
        y = 140 + k * cell + cell / 2
        out.append(f'<g id="{sid}"><path d="{d_of(shapes, 95, 150, y)}" fill="#000"/>')
        x = 330
        for px in (64, 32, 16):
            for bg, fg in (('#fff', '#000'), ('#0c1730', '#ffd28a')):
                out.append(f'<rect x="{x - px * .62:.1f}" y="{y - px * .62:.1f}" width="{px * 1.24:.1f}" height="{px * 1.24:.1f}" fill="{bg}" stroke="#ddd" stroke-width=".5"/>')
                out.append(f'<path d="{d_of(shapes, px * .5, x, y)}" fill="{fg}"/>')
                x += px * 1.24 + 22
            x += 20
        out.append(f'<text x="{x + 20}" y="{y + 8}" font-family="Helvetica, Arial, sans-serif" font-size="20" fill="#333">{note.replace("&", "&amp;")}</text></g>')
    out.append('</svg>')
    open(os.path.join(HERE, 'sparks.svg'), 'w').write('\n'.join(out) + '\n')

def lockups_sheet():
    src = open(os.path.join(ROOT, 'src/components/Wordmark.astro')).read()
    paths = re.findall(r'<path d="([^"]+)"', src)
    robot, lantern = paths[:6], paths[6:14]
    tf = 'translate(-0.027169,316) scale(0.1,-0.1)'
    word = lambda ps, dx, dy: f'<g transform="translate({dx} {dy})"><g transform="{tf}">' + ''.join(f'<path d="{p}"/>' for p in ps) + '</g></g>'
    # Measured in the wordmark's own units: Robot spans x 96-618 on baseline 153, Lantern x 0-704
    # on baseline 315, cap height 150. The period is at (729.4, 299.2), r 17.2.
    layouts = [('one-line', 'One line', [(robot, -96, 0), (lantern, 522 + 48, -162)], 522 + 48 + 704, 153),
               ('stacked-left', 'Stacked, left', [(robot, -96, 0), (lantern, 0, 0)], 704, 315),
               ('stacked-centered', 'Stacked, centered (the current wordmark)', [(robot, 0, 0), (lantern, 0, 0)], 704, 315),
               ('stacked-right', 'Stacked, right', [(robot, 86, 0), (lantern, 0, 0)], 704, 315)]
    spark = shear([capsule(a, l, .5) for a, l in [(-90, 1.0), (-30, .78), (30, .66), (90, .7), (150, .8), (-150, .6)]], 12)
    rows = []
    y = 120
    for lid, label, words, end, base in layouts:
        h = 170 if lid == 'one-line' else 330
        for variant in ('period', 'spark'):
            x0 = 60 if variant == 'period' else 1500 + 60 - (0 if lid != 'one-line' else 0)
            g = [f'<g id="{lid}-{variant}" transform="translate({x0} {y})">' + ''.join(word(p, dx, dy) for p, dx, dy in words)]
            if variant == 'period':
                g.append(f'<circle cx="{end + 25.4:.1f}" cy="{base - 15.8:.1f}" r="17.2"/>')
            else:
                g.append(f'<path d="{d_of(spark, 54, end + 66, base - 100)}"/>')
            g.append('</g>')
            rows.append(''.join(g))
        rows.append(f'<text x="60" y="{y - 24}" font-family="Helvetica, Arial, sans-serif" font-size="24" fill="#555">{label}: with the period, then with the skewed-six spark, weighted to match the letters</text>')
        y += h + 110
    W = 1500 * 2 if False else 3000
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{y}" viewBox="0 0 {W} {y}">', f'<rect width="{W}" height="{y}" fill="#fff"/>']
    out += rows + ['</svg>']
    open(os.path.join(HERE, 'wordmark-lockups.svg'), 'w').write('\n'.join(out) + '\n')

sparks_sheet()
lockups_sheet()
print('wrote sparks.svg and wordmark-lockups.svg')
