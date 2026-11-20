"""Bundle the photo products' shop files into the order Worker (docs/ORDERS.md).

Wrangler runs this before it builds shop-worker/ (the "build" command in its wrangler.jsonc), so the
Worker prices orders from the product files as they are when it's deployed. It writes
shop-worker/catalog.json (git-ignored) from every products/*/shop.json that has a "photo" section,
plus the sandbox-only fixtures in tools/orders/fixtures/, which the Worker refuses in live mode.
Only what the Worker needs goes in: names, prices, options, photo needs, weekly caps and Stripe IDs,
and for a product made from drawings (`"photo": {"via": "drawing"}`), its drawing settings, subjects with
their briefs' text, ready-made designs, pricing tiers and text rule. A ready-made design's SHA-256 is
checked against its file here, so a wrong one fails the deploy rather than an order.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ID = re.compile(r'^[a-z0-9][a-z0-9-]*$')


def entry(slug, p, folder, fixture):
    def bad(why):
        raise SystemExit(f'{slug}/shop.json: {why}')

    drawn = p['photo'].get('via') == 'drawing'
    photo = dict(p['photo']) if drawn else {'count': 1, **p['photo']}
    if not drawn and (not isinstance(photo['count'], int) or photo['count'] < 1):
        bad('photo.count must be a whole number from 1')
    if not drawn and (not isinstance(p.get('price'), (int, float)) or p['price'] <= 0):
        bad('price must be more than 0')
    if not isinstance(p.get('shipping'), (int, float)) or p['shipping'] < 0:
        bad('shipping must be 0 or more')
    if not isinstance(p.get('weeklyCap'), int) or p['weeklyCap'] < 0:
        bad('weeklyCap must be a whole number')
    options = []
    for o in p.get('options') or []:
        choices = []
        for c in o['choices']:
            choice = {'id': c['id'], 'label': c['label'], 'add': c.get('add', 0)}
            if c.get('slant'):
                choice['slant'] = c['slant']
            choices.append(choice)
        ids = [o['id']] + [c['id'] for c in choices]
        if not choices or not all(ID.match(i) for i in ids) or len(set(ids[1:])) < len(choices):
            bad(f'option {o["id"]}: needs choices with unique lowercase ids')
        if any(not isinstance(c['add'], (int, float)) or c['add'] < 0 for c in choices):
            bad(f'option {o["id"]}: add must be 0 or more')
        opt = {'id': o['id'], 'label': o['label'], 'choices': choices}
        if 'default' in o:
            if o['default'] not in ids[1:]:
                bad(f'option {o["id"]}: default {o["default"]!r} isn\'t one of its choices')
            opt['default'] = o['default']
        options.append(opt)
    if len({o['id'] for o in options}) < len(options):
        bad('option ids repeat')

    e = {
        'name': p['name'], 'shipping': p['shipping'], 'photo': photo,
        'options': options, 'weeklyCap': p['weeklyCap'], 'listed': bool(p.get('listed')),
        'stripe': {mode: {k: ids[k] for k in ('product', 'shippingRate') if k in ids}
                   for mode, ids in (p.get('stripe') or {}).items()},
    }
    if not drawn:
        e['price'] = p['price']
    else:
        e.update(drawn_entry(p, folder, {o['id']: o for o in options}, bad))
    if p.get('provisional'):
        e['provisional'] = p['provisional']
    if fixture:
        e['fixture'] = True
    return e


def drawn_entry(p, folder, options, bad):
    """The parts of a drawing product the Worker checks orders against (docs/ORDERS.md, "The product file")."""
    d = p.get('drawing') or bad('a drawing product needs "drawing"')
    for k in ('model', 'quality', 'size'):
        if not isinstance(d.get(k), str):
            bad(f'drawing.{k} is missing')
    if not isinstance(d.get('triesPerPhoto'), int) or d['triesPerPhoto'] < 1:
        bad('drawing.triesPerPhoto must be a whole number from 1')
    subjects = []
    for s in d.get('subjects') or []:
        if not ID.match(s.get('id', '')):
            bad(f'subject {s.get("id")!r}: needs a lowercase id')
        source = s.get('source', 'made')
        sub = {'id': s['id'], 'label': s['label'], 'source': source}
        if source == 'made':
            brief = folder / s['brief']
            if not brief.is_file():
                bad(f'subject {s["id"]}: no brief at {s["brief"]}')
            sub['brief'] = brief.read_text().strip()
        elif source == 'static':
            designs = []
            for x in s.get('designs') or []:
                f = folder / x['drawing']
                if not f.is_file():
                    bad(f'{s["id"]}/{x["id"]}: no drawing at {x["drawing"]}')
                if hashlib.sha256(f.read_bytes()).hexdigest() != x['sha256']:
                    bad(f'{s["id"]}/{x["id"]}: {x["drawing"]} doesn\'t match its sha256')
                designs.append({k: x[k] for k in ('id', 'label', 'sha256', 'text', 'font') if k in x})
            if not designs:
                bad(f'subject {s["id"]}: a ready-made subject needs designs')
            sub['designs'] = designs
        else:
            bad(f'subject {s["id"]}: source {source!r} is neither made nor static')
        subjects.append(sub)
    if not subjects or len({s['id'] for s in subjects}) < len(subjects):
        bad('drawing.subjects must be a list with unique ids')

    pricing = p.get('pricing') or bad('a drawing product needs "pricing"')
    tiers = pricing.get('tiers') or []
    froms = [t.get('from') for t in tiers]
    if not tiers or froms[0] != 1 or froms != sorted(set(froms)) or \
            any(not isinstance(t.get('each'), (int, float)) or t['each'] <= 0 for t in tiers):
        bad('pricing.tiers must start from 1, rise, and each price more than 0')
    for k in ('maxPerOrder', 'maxDesigns'):
        if not isinstance(pricing.get(k), int) or pricing[k] < 1:
            bad(f'pricing.{k} must be a whole number from 1')
    for m in pricing.get('modifiers') or []:
        if not isinstance(m.get('when'), dict) or not isinstance(m.get('add'), (int, float)):
            bad('each pricing modifier needs "when" (an object) and "add" (a number)')

    text = p.get('text')
    if text:
        try:
            re.compile(f"^[{text['allowed']}]+$")
        except (KeyError, re.error):
            bad('text.allowed must be a character class')
        for k, v in (text.get('when') or {}).items():
            if k not in options or v not in [c['id'] for c in options[k]['choices']]:
                bad(f'text.when: {k} = {v} isn\'t an option and choice')
        if text.get('font') and text['font'] not in options:
            bad(f'text.font: there\'s no option {text["font"]}')
    for pair in p.get('differ') or []:
        if any(k not in options for k in pair):
            bad(f'differ: {pair} names an option that isn\'t there')
    return {
        'drawing': {k: d[k] for k in ('model', 'quality', 'size', 'triesPerPhoto')} | {'subjects': subjects},
        'pricing': {'tiers': tiers, 'maxPerOrder': pricing['maxPerOrder'], 'maxDesigns': pricing['maxDesigns'],
                    'modifiers': pricing.get('modifiers') or []},
        'text': text, 'differ': p.get('differ') or [],
    }


def main():
    catalog = {}
    for pattern, fixture in (('products/*/shop.json', False), ('tools/orders/fixtures/*/shop.json', True)):
        for path in sorted(ROOT.glob(pattern)):
            p = json.loads(path.read_text())
            if 'photo' in p:
                catalog[path.parent.name] = entry(path.parent.name, p, path.parent, fixture)
    (ROOT / 'shop-worker/catalog.json').write_text(json.dumps(catalog, indent=1, ensure_ascii=False) + '\n')
    print('catalog.json:', ', '.join(catalog))


if __name__ == '__main__':
    main()
