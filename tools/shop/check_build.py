"""Check a built site (dist/) after `npm run build`: every internal link and image resolves, and the agent
files agree with the product files (NOW.md step 11; docs/ORDERS.md, "Agents").

    python3 tools/shop/check_build.py            # exits 1 with a list of problems

- Every href/src on robotlantern.com, or relative, in dist/**/*.html points at a file in dist/.
- product.json's tiers, limits and order-by date are shop.json's; it holds no Stripe IDs, Slant filament ids or caps.
- llms.txt names every tier price, the order-by date and every ready-made design.
"""
import html.parser
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / 'dist'
SITE = 'https://robotlantern.com'
problems = []


class Links(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.found = []

    def handle_starttag(self, tag, attrs):
        if tag == 'link' and dict(attrs).get('rel') == 'canonical':
            return  # the 404 page's canonical names /404/, which no host serves; not a link
        for k, v in attrs:
            if k in ('href', 'src') and v and tag in ('a', 'img', 'link', 'script'):
                self.found.append(v)


def exists(path):
    p = DIST / path.lstrip('/')
    return p.is_file() or (p / 'index.html').is_file()


for page in DIST.rglob('*.html'):
    rel = '/' + str(page.relative_to(DIST)).replace('index.html', '')
    parser = Links()
    parser.feed(page.read_text())
    for link in parser.found:
        if link.startswith(('mailto:', 'data:', '#', 'javascript:')):
            continue
        url = urlparse(urljoin(SITE + rel, link))
        if url.netloc != 'robotlantern.com' or url.path.startswith('/api/'):
            continue
        if not exists(url.path):
            problems.append(f'{rel}: {link} -> {url.path} is not in dist/')

money = lambda n: f'${n:.2f}' if n % 1 else f'${n:g}'
for shop in ROOT.glob('products/*/shop.json'):
    p = json.loads(shop.read_text())
    if 'drawing' not in p:
        continue
    slug = shop.parent.name
    pj_file = DIST / 'shop' / slug / 'product.json'
    if not pj_file.is_file():
        problems.append(f'{slug}: no product.json')
        continue
    raw = pj_file.read_text()
    pj = json.loads(raw)
    tiers = [{'fromCount': t['from'], 'each': t['each']} for t in p['pricing']['tiers']]
    if pj['pricing']['perOrnament'] != tiers:
        problems.append(f'{slug}: product.json tiers differ from shop.json')
    for k in ('maxPerOrder', 'maxDesigns'):
        if pj['pricing'][k] != p['pricing'][k]:
            problems.append(f'{slug}: product.json {k} differs')
    if (pj['orderBy'] or {}).get('date') != p.get('orderBy'):
        problems.append(f'{slug}: product.json orderBy differs')
    leaks = [s for s in ('prod_', 'shr_', 'weeklyCap', '"slant"', 'brief', p['drawing']['model'])
             if s in raw]
    leaks += [c['slant'] for o in p['options'] for c in o['choices'] if c.get('slant') and c['slant'] in raw]
    if leaks:
        problems.append(f'{slug}: product.json carries {leaks}')
    ready = {f"{s['id']}/{d['id']}" for s in p['drawing']['subjects'] for d in s.get('designs', [])}
    listed = {d['order']['static'] for s in pj['subjects'] for d in s.get('designs', [])}
    if ready != listed:
        problems.append(f'{slug}: product.json ready-made designs {sorted(listed)} != {sorted(ready)}')
    llms = (DIST / 'llms.txt').read_text()
    for t in p['pricing']['tiers']:
        if f"{money(t['each'])} each for {t['from']}" not in llms:
            problems.append(f"llms.txt: no {money(t['each'])} each for {t['from']}")
    if p.get('orderBy'):
        from datetime import date
        d = date.fromisoformat(p['orderBy'])
        if f'Order by {d:%B} {d.day}' not in llms:
            problems.append('llms.txt: no order-by date')
    for s in p['drawing']['subjects']:
        for d in s.get('designs', []):
            if d['label'].lower() not in llms:
                problems.append(f"llms.txt: no {d['label']}")
    promo = p.get('promotion', {}).get('code')
    if promo and (re.search(rf'\b{promo}\b', llms) or promo in raw):
        problems.append(f'{slug}: the promotion code is in the agent files; it is only for people who have bought')

print('\n'.join(problems) or 'ok: links resolve, agent files match the product files')
sys.exit(1 if problems else 0)
