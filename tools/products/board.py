"""Print the product pipeline by stage (docs/PRODUCTS.md).

    python3 tools/products/board.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGES = ['idea', 'sketch', 'feasibility', 'design', 'sample', 'listing', 'live', 'parked', 'dropped']


def front(path):
    m = re.match(r'---\n(.*?)\n---\n', path.read_text(), re.S)
    if not m:
        raise SystemExit(f'{path}: no frontmatter')
    out = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(':')
        out[k.strip()] = v.split('#')[0].strip()
    return out


products = []
for f in sorted((ROOT / 'products').glob('*/product.md')):
    p = front(f)
    if p.get('stage') not in STAGES:
        raise SystemExit(f'{f}: unknown stage {p.get("stage")!r}')
    products.append((f.parent.name, p))

for stage in STAGES:
    rows = [(slug, p) for slug, p in products if p['stage'] == stage]
    if not rows:
        continue
    print(f'\n{stage.upper()}')
    for slug, p in rows:
        who = 'RJ' if p.get('waiting_on') == 'rj' else 'agent'
        print(f'  {p["name"]}  ({slug}, {p.get("updated", "?")})\n    next ({who}): {p.get("next", "?")}')
waiting = [p['name'] for _, p in products if p.get('waiting_on') == 'rj' and p['stage'] not in ('parked', 'dropped', 'live')]
print(f'\nWaiting on RJ: {", ".join(waiting) or "nothing"}')
