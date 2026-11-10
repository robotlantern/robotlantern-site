"""Bundle the photo products' shop files into the order Worker (docs/ORDERS.md).

Wrangler runs this before it builds shop-worker/ (the "build" command in its wrangler.jsonc), so the
Worker prices orders from the product files as they are when it's deployed. It writes
shop-worker/catalog.json (git-ignored) from every products/*/shop.json that has a "photo" section,
plus the sandbox-only fixtures in tools/orders/fixtures/, which the Worker refuses in live mode.
Only what the Worker needs goes in: names, prices, options, photo needs, weekly caps and Stripe IDs.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ID = re.compile(r'^[a-z0-9][a-z0-9-]*$')


def entry(slug, p, fixture):
    def bad(why):
        raise SystemExit(f'{slug}/shop.json: {why}')

    photo = {'count': 1, **p['photo']}
    if not isinstance(photo['count'], int) or photo['count'] < 1:
        bad('photo.count must be a whole number from 1')
    if not isinstance(p.get('price'), (int, float)) or p['price'] <= 0:
        bad('price must be more than 0')
    if not isinstance(p.get('shipping'), (int, float)) or p['shipping'] < 0:
        bad('shipping must be 0 or more')
    if not isinstance(p.get('weeklyCap'), int) or p['weeklyCap'] < 0:
        bad('weeklyCap must be a whole number')
    options = []
    for o in p.get('options') or []:
        choices = [{'id': c['id'], 'label': c['label'], 'add': c.get('add', 0)} for c in o['choices']]
        ids = [o['id']] + [c['id'] for c in choices]
        if not choices or not all(ID.match(i) for i in ids) or len(set(ids[1:])) < len(choices):
            bad(f'option {o["id"]}: needs choices with unique lowercase ids')
        if any(not isinstance(c['add'], (int, float)) or c['add'] < 0 for c in choices):
            bad(f'option {o["id"]}: add must be 0 or more')
        options.append({'id': o['id'], 'label': o['label'], 'choices': choices})
    if len({o['id'] for o in options}) < len(options):
        bad('option ids repeat')

    e = {
        'name': p['name'], 'price': p['price'], 'shipping': p['shipping'], 'photo': photo,
        'options': options, 'weeklyCap': p['weeklyCap'], 'listed': bool(p.get('listed')),
        'stripe': {mode: {k: ids[k] for k in ('product', 'shippingRate') if k in ids}
                   for mode, ids in (p.get('stripe') or {}).items()},
    }
    if p.get('provisional'):
        e['provisional'] = p['provisional']
    if fixture:
        e['fixture'] = True
    return e


def main():
    catalog = {}
    for pattern, fixture in (('products/*/shop.json', False), ('tools/orders/fixtures/*/shop.json', True)):
        for path in sorted(ROOT.glob(pattern)):
            p = json.loads(path.read_text())
            if 'photo' in p:
                catalog[path.parent.name] = entry(path.parent.name, p, fixture)
    (ROOT / 'shop-worker/catalog.json').write_text(json.dumps(catalog, indent=1, ensure_ascii=False) + '\n')
    print('catalog.json:', ', '.join(catalog))


if __name__ == '__main__':
    main()
