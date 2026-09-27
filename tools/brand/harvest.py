# Needs fontTools, Pillow and numpy (pip install fonttools pillow numpy).
# Run: python3 tools/brand/harvest.py && python3 tools/brand/sheet.py design/brand
"""Fetch the asterisk (U+002A) from every Google Fonts family, as outline paths.

Google Fonts serves a family subset to the characters in `text=`, so each request is ~1 KB.
Writes one JSON line per family to glyphs.jsonl; rerunning skips families already done.
"""
import io, json, os, re, sys, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, '..', '..', '.cache', 'asterisks', 'glyphs.jsonl')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'RobotLanternAsteriskSheet/1.0'}), timeout=30) as r:
        return r.read()

def families():
    raw = get('https://fonts.google.com/metadata/fonts').decode()
    raw = raw[raw.index('{'):]
    meta = json.loads(raw)
    for f in meta['familyMetadataList']:
        yield f['family'], f.get('category', ''), sorted(f.get('fonts', {}).keys())

def fetch(item):
    fam, cat, styles = item
    weight = '400' if '400' in styles else next((s for s in styles if s.isdigit()), None)
    q = urllib.parse.quote_plus(fam) + (f':wght@{weight}' if weight and weight != '400' else '')
    try:
        css = get(f'https://fonts.googleapis.com/css2?family={q}&text=%2A').decode()
        url = re.search(r'url\((https://[^)]+)\)', css).group(1)
        font = TTFont(io.BytesIO(get(url)))
        name = font.getBestCmap().get(0x2A)
        if not name:
            return {'family': fam, 'category': cat, 'error': 'no asterisk'}
        gs = font.getGlyphSet()
        pen = SVGPathPen(gs); gs[name].draw(pen)
        bp = BoundsPen(gs); gs[name].draw(bp)
        if not bp.bounds:
            return {'family': fam, 'category': cat, 'error': 'empty glyph'}
        return {'family': fam, 'category': cat, 'weight': weight, 'upm': font['head'].unitsPerEm,
                'bounds': bp.bounds, 'd': pen.getCommands()}
    except Exception as e:
        return {'family': fam, 'category': cat, 'error': f'{type(e).__name__}: {e}'[:200]}

def main():
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)['family'] for l in open(OUT)}
    todo = [f for f in families() if f[0] not in done]
    print(f'{len(done)} done, {len(todo)} to fetch', flush=True)
    with open(OUT, 'a') as out, ThreadPoolExecutor(10) as pool:
        for i, rec in enumerate(pool.map(fetch, todo)):
            out.write(json.dumps(rec) + '\n'); out.flush()
            if i % 200 == 0: print(i, rec['family'], rec.get('error', 'ok'), flush=True)

if __name__ == '__main__':
    main()
