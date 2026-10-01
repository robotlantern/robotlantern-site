"""Make the site's icons and social image from the brand (docs/BRAND.md).

    python3 tools/brand/make_icons.py

Needs rsvg-convert and ImageMagick (brew install librsvg imagemagick). Writes into public/:
favicon.svg, favicon.ico (16, 32, 48), apple-touch-icon.png (180, square: iOS rounds it) and
og.png (1200x630, the wordmark on the night sky, for link previews). The icons are RJ's tile
(docs/BRAND.md).
"""
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUB = ROOT / 'public'
brand = json.loads((ROOT / 'src/data/brand.json').read_text())


def tile(rounded):
    """RJ's tile (design/brand/favicon-options/e-night-on-cream.svg). The touch icon is square:
    iOS rounds it."""
    t = brand['tile']
    bg = f'<path d="{t["bg"]}" fill="#f4f1ea"/>' if rounded else '<rect width="100" height="100" fill="#f4f1ea"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">{bg}<path d="{t["r"]}" fill="#0a0e18"/>'
            f'<path d="{t["l"]}" fill="#0a0e18"/><path d="{t["dot"]}" fill="#f0a040"/></svg>\n')


def png(svg_text, size, out, tmp):
    src = Path(tmp) / 'in.svg'
    src.write_text(svg_text)
    subprocess.run(['rsvg-convert', '-w', str(size), '-h', str(size), '-o', str(out), str(src)], check=True)


def wordmark_svg():
    w = brand['twoLine']
    x0, y0, x1, y1 = w['periodBox']
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    letters = ''.join(f'<path d="{d}"/>' for d in w['letters'])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-40 -40 {w["width"] + 80} {w["height"] + 80}">'
            f'<defs><radialGradient id="l" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{w["width"] * .95}">'
            '<stop offset="0" stop-color="#ffd79a"/><stop offset=".25" stop-color="#f6dbb0"/><stop offset=".6" stop-color="#ddd5c4"/><stop offset="1" stop-color="#b3bccf"/></radialGradient>'
            '<radialGradient id="g"><stop offset="0" stop-color="#ffd68c" stop-opacity=".7"/><stop offset=".35" stop-color="#ffa050" stop-opacity=".18"/><stop offset="1" stop-color="#ff8c3c" stop-opacity="0"/></radialGradient></defs>'
            f'<circle cx="{cx}" cy="{cy}" r="{(x1 - x0) * 2.4}" fill="url(#g)"/><g fill="url(#l)">{letters}</g>'
            f'<path d="{w["period"]}" fill="#ffd28a"/></svg>\n')


def main():
    (PUB / 'favicon.svg').write_text(tile(True))
    with tempfile.TemporaryDirectory() as tmp:
        sizes = []
        for s in (16, 32, 48):
            p = Path(tmp) / f'f{s}.png'
            png(tile(True), s, p, tmp)
            sizes.append(str(p))
        subprocess.run(['magick', *sizes, str(PUB / 'favicon.ico')], check=True)
        png(tile(False), 180, PUB / 'apple-touch-icon.png', tmp)
        # Social image: the night photo, darkened, with the wordmark on the left.
        mark = Path(tmp) / 'mark.png'
        src = Path(tmp) / 'wm.svg'
        src.write_text(wordmark_svg())
        subprocess.run(['rsvg-convert', '-h', '380', '-o', str(mark), str(src)], check=True)
        subprocess.run(['magick', str(PUB / 'images/night.jpg'), '-resize', '1200x630^', '-gravity', 'center', '-extent', '1200x630',
                        '-fill', '#04060d', '-colorize', '35', str(mark), '-gravity', 'west', '-geometry', '+60+0', '-composite',
                        '-strip', '-quality', '88', str(PUB / 'og.png')], check=True)
    for f in ('favicon.svg', 'favicon.ico', 'apple-touch-icon.png', 'og.png'):
        print(f, (PUB / f).stat().st_size, 'bytes')


if __name__ == '__main__':
    main()
