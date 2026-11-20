"""Write shop-worker/tag-metrics.json: what the order Worker needs to run nametag.tag_fit() without fonts.

    python3 tools/orders/tag_metrics.py        # needs tools/ornament's requirements (fontTools, shapely)

tag_fit() lays the text out glyph by glyph and measures the outlines' bounding box (tools/ornament/nametag.py).
The box of a line of glyphs is the union of each glyph's own box, moved along by the advances, so the Worker
only needs, per font, each allowed character's advance and outline bounds. They're measured here with
nametag's own outline code, so the two agree. Run it again when a font or the text rule changes, and commit
the result: the deploy machine needn't have fontTools.

It also writes `cases`: tag_fit()'s answers for a set of texts, which `node shop-worker/tagfit.test.mjs`
checks the Worker's version against.
"""
import json
import string
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/ornament'))
import nametag  # noqa: E402

CHARS = string.ascii_letters + string.digits + " '&.,!?-"
CASES = ['Tucker', 'Test Cat', 'Never Forget', 'Fairmont General', 'Thanksgiving 2026', 'Turkey Day 2026',
         "Mamaw's Bucket", 'WV Coal Miner', 'Max', 'I', 'W', 'Mr. & Mrs. Smith', 'Merry Xmas!!', 'Who? Me?',
         'WWWWWWWWWWWWWWWW', 'iiiiiiiiiiiiiiii', 'Princess Buttons', 'Sir Barks-a-Lot', 'Pepperoni Roll',
         'Born to Pick', '2026 So Far', 'Debug Duck', 'Naughty List', 'Moonshine', 'a, b, c']


def main():
    fonts = {}
    for key in nametag.STENCILS:
        font = nametag._font(key)
        upm = font['head'].unitsPerEm
        glyphs = {}
        for ch in CHARS:
            g = font.getBestCmap().get(ord(ch))
            if g is None:
                continue
            poly = nametag.text_poly(ch, key, track=0)
            glyphs[ch] = [font['hmtx'][g][0], None if poly.is_empty else [round(v, 4) for v in poly.bounds]]
        fonts[key] = {'upm': upm, 'glyphs': glyphs}
    cases = []
    for key in nametag.STENCILS:
        for text in CASES:
            r = nametag.tag_fit(text, key)
            cases.append({'text': text, 'font': key, 'fits': r['fits'], 'text_mm': r['text_mm']})
    out = {
        '_source': 'tools/orders/tag_metrics.py, from tools/ornament/nametag.py and public/shop/fonts/',
        'rule': {'track': nametag.TRACK, 'tagH': nametag.TAG_H, 'share': nametag.TAG_SHARE,
                 'minTagW': nametag.MIN_TAG_W, 'maxTagW': nametag.MAX_TAG_W, 'padX': nametag.PAD_X,
                 'padBottom': nametag.PAD_BOTTOM, 'padTop': nametag.PAD_TOP, 'minTextH': nametag.MIN_TEXT_H,
                 'maxTextH': nametag.MAX_TEXT_H, 'artW': 80.0},
        'fonts': fonts,
        'cases': cases,
    }
    path = ROOT / 'shop-worker/tag-metrics.json'
    path.write_text(json.dumps(out, separators=(',', ':'), ensure_ascii=False) + '\n')
    print(f'{path.relative_to(ROOT)}: {len(fonts)} fonts, {len(cases)} cases, {path.stat().st_size:,} bytes')


if __name__ == '__main__':
    main()
