"""Create or update each product's Stripe objects from its shop.json (docs/SHOP.md).

    python3 tools/shop/sync.py                  # every products/*/shop.json, sandbox
    python3 tools/shop/sync.py tools/shop/fixtures/test-mug/shop.json
    python3 tools/shop/sync.py --live           # live mode: only at launch, with RJ's go-ahead

For each product it keeps a Stripe product, a price, a flat shipping rate and a Payment Link, and
writes their IDs and the link's URL back into the file under "stripe" -> "test" or "live".
Prices and shipping rates can't change in Stripe, so a new price or shipping amount makes new
ones and a new Payment Link (the old link is switched off). A new stock number updates the link
in place. Nothing here costs money; a Payment Link only charges when someone pays.

A photo product (one with "photo", docs/ORDERS.md) gets only the product and the shipping rate: the
order Worker prices each order from the file and opens its own Checkout Session, so there's no
fixed price and no Payment Link. Deploy the Worker after syncing one (tools/shop/worker-deploy.sh).
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECRETS = Path(os.environ.get('RL_SECRETS', Path.home() / '.codex/secrets/robot-lantern'))
SITE = {'test': 'https://site.robotlantern.workers.dev', 'live': 'https://robotlantern.com'}
SHIPPING_TAX_CODE = 'txcd_92010001'
GOODS_TAX_CODE = 'txcd_99999999'
THANKS = 'Thank you for your order. Your receipt is on its way by email.'
SOLD_OUT = 'Sold out. Thanks for looking.'


def secret(name):
    for line in (SECRETS / 'stripe.env').read_text().splitlines():
        if line.startswith(name + '='):
            return line.split('=', 1)[1].strip()
    raise SystemExit(f'{name} missing from stripe.env')


def form(data, prefix=''):
    """Stripe's nested form encoding: a[b][0][c]=v."""
    out = []
    items = data.items() if isinstance(data, dict) else enumerate(data)
    for k, v in items:
        key = f'{prefix}[{k}]' if prefix else str(k)
        if isinstance(v, (dict, list)):
            out += form(v, key)
        elif v is not None:
            out.append((key, 'true' if v is True else 'false' if v is False else str(v)))
    return out


class Stripe:
    def __init__(self, key):
        self.key = key

    def __call__(self, method, path, data=None):
        body = urllib.parse.urlencode(form(data or {})).encode() if method == 'POST' else None
        req = urllib.request.Request(f'https://api.stripe.com/v1/{path}', data=body, method=method)
        req.add_header('Authorization', f'Bearer {self.key}')
        try:
            with urllib.request.urlopen(req) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            raise SystemExit(f'Stripe {method} {path}: {json.load(e).get("error", {}).get("message")}')


def cents(dollars):
    return round(float(dollars) * 100)


def url(path, mode):
    return path if path.startswith('http') else SITE[mode] + path


def choice_key(label):
    key = re.sub(r'[^a-z0-9]', '', label.lower())
    if not key:
        raise SystemExit(f'option {label!r} needs letters or digits')
    return key


def metadata(slug, p, mode):
    """What the order Worker reads from the Stripe product to place the Gelato order."""
    md = {'slug': slug, 'fulfillment': p['fulfillment']}
    if p['fulfillment'] == 'gelato':
        g = p['gelato']
        for kind, path in g['files'].items():
            md[f'file_{kind}'] = url(path, mode)
        if 'options' in p:
            md['option'] = choice_key(p['options']['label'])
            for c in p['options']['choices']:
                md[f'uid_{choice_key(c["label"])}'] = c['productUid']
        else:
            md['uid'] = g['productUid']
    for k, v in md.items():
        if len(v) > 500:
            raise SystemExit(f'{slug}: metadata {k} is over 500 characters')
    return md


def shipping_rate(stripe, ids, p):
    """Keep a flat shipping rate for the file's shipping amount. True when it made a new one."""
    shipping = cents(p['shipping'])
    if ids.get('shippingRate') and \
            stripe('GET', f'shipping_rates/{ids["shippingRate"]}')['fixed_amount']['amount'] == shipping:
        return False
    old = ids.get('shippingRate')
    ids['shippingRate'] = stripe('POST', 'shipping_rates', {
        'display_name': 'Shipping', 'type': 'fixed_amount',
        'fixed_amount': {'amount': shipping, 'currency': 'usd'},
        'tax_behavior': 'exclusive', 'tax_code': SHIPPING_TAX_CODE})['id']
    if old:
        stripe('POST', f'shipping_rates/{old}', {'active': False})
    return True


def sync(path, stripe, mode):
    p = json.loads(path.read_text())
    slug = path.parent.name
    ids = p.setdefault('stripe', {}).setdefault(mode, {})
    md = metadata(slug, p, mode)
    product = {
        'name': p['name'],
        'description': p.get('description') or None,
        'tax_code': p.get('taxCode', GOODS_TAX_CODE),
        'images': [url(i, mode) for i in p.get('images', [])][:8],
    }

    if ids.get('product'):
        old = stripe('GET', f'products/{ids["product"]}')['metadata']
        stale = {k: '' for k in old if k not in md}  # '' removes a key
        stripe('POST', f'products/{ids["product"]}', {**product, 'metadata': {**stale, **md}})
    else:
        ids['product'] = stripe('POST', 'products', {**product, 'metadata': md})['id']

    if 'photo' in p:
        new_rate = shipping_rate(stripe, ids, p)
        path.write_text(json.dumps(p, indent=2, ensure_ascii=False) + '\n')
        print(f'{slug}: photo product {ids["product"]}' + (' (new shipping rate)' if new_rate else ''))
        return

    new_link = not ids.get('paymentLink')
    price = cents(p['price'])
    if not ids.get('price') or stripe('GET', f'prices/{ids["price"]}')['unit_amount'] != price:
        old = ids.get('price')
        ids['price'] = stripe('POST', 'prices', {
            'product': ids['product'], 'currency': 'usd', 'unit_amount': price,
            'tax_behavior': 'exclusive'})['id']
        stripe('POST', f'products/{ids["product"]}', {'default_price': ids['price']})
        if old:
            stripe('POST', f'prices/{old}', {'active': False})
        new_link = True

    if shipping_rate(stripe, ids, p):
        new_link = True

    choices = [c['label'] for c in p.get('options', {}).get('choices', [])]
    if choices != ids.get('choices', []):
        new_link = True
    ids['choices'] = choices

    stock = p.get('stock') if p['fulfillment'] == 'self' else None
    restrictions = {'completed_sessions': {'limit': stock}} if stock else None
    if new_link:
        link = {
            'line_items': [{'price': ids['price'], 'quantity': 1}],
            'shipping_address_collection': {'allowed_countries': ['US']},
            'shipping_options': [{'shipping_rate': ids['shippingRate']}],
            'automatic_tax': {'enabled': True},
            'after_completion': {'type': 'hosted_confirmation',
                                 'hosted_confirmation': {'custom_message': p.get('confirmation', THANKS)}},
            'inactive_message': SOLD_OUT,
            'metadata': {'slug': slug},
            'restrictions': restrictions,
        }
        if 'options' in p:
            link['custom_fields'] = [{
                'key': md['option'], 'type': 'dropdown',
                'label': {'type': 'custom', 'custom': p['options']['label']},
                'dropdown': {'options': [{'label': c, 'value': choice_key(c)} for c in choices]}}]
        old = ids.get('paymentLink')
        created = stripe('POST', 'payment_links', link)
        ids['paymentLink'], ids['url'] = created['id'], created['url']
        if old:
            stripe('POST', f'payment_links/{old}', {'active': False})
    elif stock:
        stripe('POST', f'payment_links/{ids["paymentLink"]}', {'restrictions': restrictions})

    path.write_text(json.dumps(p, indent=2, ensure_ascii=False) + '\n')
    print(f'{slug}: {ids["url"]}' + (' (new link)' if new_link else ''))


def main():
    args = [a for a in sys.argv[1:] if a != '--live']
    mode = 'live' if '--live' in sys.argv else 'test'
    key = secret('STRIPE_SECRET_KEY' if mode == 'live' else 'STRIPE_SECRET_KEY_TEST')
    if mode == 'test' and not key.startswith('sk_test_'):
        raise SystemExit('STRIPE_SECRET_KEY_TEST is not a test key')
    paths = [Path(a).resolve() for a in args] or sorted((ROOT / 'products').glob('*/shop.json'))
    for path in paths:
        sync(path, Stripe(key), mode)


if __name__ == '__main__':
    main()
