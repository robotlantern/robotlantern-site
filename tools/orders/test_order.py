"""Place a photo order end to end in Stripe's sandbox, then pull it (docs/ORDERS.md, "Testing").

    python3 tools/orders/test_order.py                               # the test-photo fixture
    python3 tools/orders/test_order.py --product lithophane-ornament
    python3 tools/orders/test_order.py --keep                        # leave it in the queue

It draws a test picture (shapes on a gradient, never anyone's photo), sends design.json with a
made-up price, uploads the files and checks the unpaid ones expire in two days. Then it opens
checkout, pays with Stripe's test card token, shipping to the West Virginia State Capitol (so tax
shows), waits for the webhook, and checks the files no longer expire and the week's count went up.
It resends the webhook and checks nothing changed, sends a bad signature, pulls the order with
queue.py and lists the queue. Last, it purges the order, in KV and on disk, unless --keep.

Sandbox only: it refuses a live key. Each run costs about 20 of KV's 1,000 free writes a day, and
counts against the product's weekly cap in the sandbox's namespace. It needs macOS's sips for JPEGs.
Like tools/shop/test_order.py, it pays through the endpoints the Stripe CLI uses, which aren't in
Stripe's public reference.
"""
import argparse
import hashlib
import hmac
import json
import re
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'shop'))
import sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
WORKER = 'https://shop.robotlantern.workers.dev'
QUEUE = [sys.executable, str(ROOT / 'tools/orders/queue.py')]
NAMESPACE = 'shop-orders-test'
ORIGIN = 'https://site.robotlantern.workers.dev'
ADDRESS = {'line1': '1900 Kanawha Blvd E', 'city': 'Charleston', 'state': 'WV',
           'postal_code': '25305', 'country': 'US'}
BUYER = {'name': 'Test Buyer', 'email': 'test@example.com'}


def check(ok, what):
    print(f'  {"ok  " if ok else "FAIL"} {what}')
    if not ok:
        raise SystemExit(f'failed: {what}')


def env_file(name):
    out = {}
    for line in (sync.SECRETS / name).read_text().splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            out[k.strip()] = v.strip()
    return out


def http(method, url, body=None, headers=None):
    req = urllib.request.Request(url, data=body, method=method, headers={'User-Agent': 'robot-lantern-test', **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def api(method, path, body=None, ctype=None, token=None):
    headers = {'Origin': ORIGIN}
    if ctype:
        headers['Content-Type'] = ctype
    if token:
        headers['Authorization'] = f'Bearer {token}'
    data = json.dumps(body).encode() if isinstance(body, dict) else body
    status, raw = http(method, f'{WORKER}/api/{path}', data, headers)
    try:
        return status, json.loads(raw)
    except ValueError:
        return status, raw


class KV:
    """The sandbox namespace, read through Cloudflare's API: what KV itself says about expiry."""

    def __init__(self):
        cf = env_file('cloudflare.env')
        self.auth = {'Authorization': f'Bearer {cf["CF_API_TOKEN"]}'}
        self.base = f'https://api.cloudflare.com/client/v4/accounts/{cf["CF_ACCT_ID"]}/storage/kv/namespaces'
        found = json.loads(http('GET', self.base + '?per_page=100', headers=self.auth)[1])['result']
        self.ns = next(n['id'] for n in found if n['title'] == NAMESPACE)

    def keys(self, prefix):
        q = urllib.parse.urlencode({'prefix': prefix})
        res = json.loads(http('GET', f'{self.base}/{self.ns}/keys?{q}', headers=self.auth)[1])
        return {k['name']: k.get('expiration') for k in res['result']}

    def wait(self, prefix, want, test, seconds=90):
        """Poll until the keys under prefix are exactly `want` and test(expirations) holds."""
        deadline = time.time() + seconds
        while True:
            got = self.keys(prefix)
            if set(got) == set(want) and test(got):
                return got
            if time.time() > deadline:
                return got
            time.sleep(3)


# ---- a test picture, with the standard library and sips --------------------------------------

def png(width, height, rows, grey=False):
    raw = b''.join(b'\x00' + row for row in rows)

    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    header = struct.pack('>IIBBBBB', width, height, 8, 0 if grey else 2, 0, 0, 0)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b'')


def picture(n, width=1600, height=1200):
    """Photo n: a sky gradient with a lantern-coloured disc (the 'subject') and its mask."""
    cx, cy, r = width * (0.42 + 0.12 * n), height * 0.48, height * 0.28
    disc = bytes((240, 150 - 20 * n, 60 + 40 * n))
    rows, mask = [], []
    for y in range(height):
        t = y / height
        sky = bytes((int(20 + 200 * t), int(30 + 90 * t), int(90 - 40 * t)))
        dy = abs(y - cy)
        if dy < r:
            half = int((r * r - dy * dy) ** 0.5)
            a, b = int(cx) - half, int(cx) + half
            rows.append(sky * a + disc * (b - a) + sky * (width - b))
            mask.append(b'\x00' * a + b'\xff' * (b - a) + b'\x00' * (width - b))
        else:
            rows.append(sky * width)
            mask.append(b'\x00' * width)
    return png(width, height, rows), png(width, height, mask, grey=True)


def jpeg(png_bytes, folder, name, size=None):
    src, out = folder / f'{name}.png', folder / f'{name}.jpg'
    src.write_bytes(png_bytes)
    cmd = ['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '85'] + (['-Z', str(size)] if size else [])
    subprocess.run(cmd + [str(src), '--out', str(out)], check=True, capture_output=True)
    return out.read_bytes()


# ---- the run ----------------------------------------------------------------------------------

def product_file(slug):
    for path in (ROOT / 'products' / slug / 'shop.json', ROOT / 'tools/orders/fixtures' / slug / 'shop.json'):
        if path.exists():
            return json.loads(path.read_text())
    raise SystemExit(f'no product {slug}')


def signed(body, secret, t=None):
    t = t or int(time.time())
    return f't={t},v1={hmac.new(secret.encode(), f"{t}.{body}".encode(), hashlib.sha256).hexdigest()}'


def queue(*args):
    done = subprocess.run(QUEUE + list(args), capture_output=True, text=True, cwd=ROOT)
    print('\n'.join(f'    | {line}' for line in (done.stdout + done.stderr).strip().splitlines()))
    return done


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--product', default='test-photo')
    ap.add_argument('--keep', action='store_true', help='leave the order in the queue')
    args = ap.parse_args()

    slug = args.product
    p = product_file(slug)
    key = sync.secret('STRIPE_SECRET_KEY_TEST')
    if not key.startswith('sk_test_'):
        raise SystemExit('not a test key')
    stripe = sync.Stripe(key)
    hook_secret = sync.secret('STRIPE_WEBHOOK_SECRET_TEST')
    token = env_file('orders.env')['ORDERS_QUEUE_TOKEN_TEST']
    kv = KV()
    ids = p['stripe']['test']
    options = {o['id']: o['choices'][-1]['id'] for o in p.get('options', [])}
    want = round(100 * (p['price'] + sum(next(c for c in o['choices'] if c['id'] == options[o['id']]).get('add', 0)
                                           for o in p.get('options', []))))

    print(f'{slug}: the week before')
    status, cap0 = api('GET', f'products/{slug}', token=token)
    check(status == 200 and cap0['open'], f'open this week ({cap0.get("count")} of {cap0.get("cap")})')

    print('Order: design.json with a made-up price of $0.01')
    count = p['photo'].get('count', 1)
    design = {
        'product': slug, 'options': options, 'price': 0.01,
        'crop': [{'photo': i + 1, 'x': 0, 'y': 0, 'w': 1, 'h': 1, 'rotate': 0} for i in range(count)],
        'subject': [{'photo': i + 1, 'taps': [[0.5, 0.45, 1]]} for i in range(count)] if p['photo']['subject'] else [],
        'version': 'tools/orders/test_order.py',
    }
    status, made = api('POST', 'orders', design, 'application/json')
    check(status == 201, f'created {made.get("id") if isinstance(made, dict) else made}')
    oid = made['id']
    check(round(made['price'] * 100) == want, f'priced from the product file: ${want / 100:.2f}, not $0.01')

    # On a second order: reading a file before it's written makes KV cache the miss for a minute.
    status, other = api('POST', 'orders', design, 'application/json')
    status, early = api('POST', f'orders/{other["id"]}/checkout')
    check(status == 409 and len(early.get('missing', [])) == len(made['files']), 'checkout refused without the files')

    print(f'Upload: {", ".join(made["files"])}')
    sent = {}
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        pictures = [picture(i) for i in range(count)]
        for name in made['files']:
            kind, _, rest = name.partition('-')
            i = int(rest.split('.')[0]) - 1 if rest else 0
            if kind == 'photo':
                sent[name] = jpeg(pictures[i][0], tmp, name)
            elif kind == 'mask':
                sent[name] = pictures[i][1]
            else:
                sent[name] = jpeg(pictures[0][0], tmp, 'preview', size=640)
    for name, data in sent.items():
        ctype = 'image/png' if name.endswith('.png') else 'image/jpeg'
        status, res = api('PUT', f'orders/{oid}/{name}', data, ctype)
        check(status == 201 and res['size'] == len(data), f'{name}: {len(data):,} bytes')

    print('Unpaid: everything expires in two days')
    expires = int(datetime.fromisoformat(made['expires'].replace('Z', '+00:00')).timestamp())
    files = {f'file:{oid}/{n}' for n in made['files']}
    got = kv.wait(f'file:{oid}/', files, lambda e: all(e.values()))
    check(set(got) == files and all(v == expires for v in got.values()),
          f'{len(got)} files expire at {made["expires"]} ({(expires - time.time()) / 3600:.1f} h from now)')
    rec_key = kv.wait(f'order:{oid}', {f'order:{oid}'}, lambda e: True)
    check(rec_key.get(f'order:{oid}') == expires, 'the order record expires with them')

    print('Checkout')
    status, co = api('POST', f'orders/{oid}/checkout')
    check(status == 200 and co['url'].startswith('https://checkout.stripe.com/'), 'checkout page opened')
    status, again = api('POST', f'orders/{oid}/checkout')
    check(status == 200 and again['url'] == co['url'], 'asking again gives the same session')
    status, late = api('PUT', f'orders/{oid}/{made["files"][0]}', sent[made['files'][0]], 'image/jpeg')
    check(status == 409, 'files are fixed once checkout opens')
    # The record read here may be KV's cached copy from before checkout, so take the ID from the URL.
    cs = stripe('GET', 'checkout/sessions/' + re.search(r'cs_test_[A-Za-z0-9]+', co['url']).group(0))
    check(cs['amount_subtotal'] == want, f'session subtotal ${cs["amount_subtotal"] / 100:.2f}')
    check(cs['client_reference_id'] == oid and cs['metadata']['order'] == oid, 'order ID in client_reference_id and metadata')
    check(cs['shipping_address_collection']['allowed_countries'] == ['US'], 'US addresses only')
    check(cs['automatic_tax']['enabled'], 'Stripe Tax on')
    check(cs['shipping_options'][0]['shipping_rate'] == ids['shippingRate'], 'the product\'s flat shipping rate')

    print('Pay with the test card')
    page = stripe('POST', f'payment_pages/{cs["id"]}', {'tax_region': ADDRESS})
    card = stripe('POST', 'payment_methods', {
        'type': 'card', 'card': {'token': 'tok_visa'}, 'billing_details': BUYER})
    stripe('POST', f'payment_pages/{cs["id"]}/confirm', {
        'payment_method': card['id'], 'expected_amount': page['total_summary']['due'],
        'shipping': {'name': BUYER['name'], 'address': ADDRESS}})
    paid = stripe('GET', f'checkout/sessions/{cs["id"]}')
    check(paid['payment_status'] == 'paid', f'paid ${paid["amount_total"] / 100:.2f} '
          f'(tax ${paid["total_details"]["amount_tax"] / 100:.2f}, shipping ${paid["total_details"]["amount_shipping"] / 100:.2f})')

    print('Webhook')
    deadline = time.time() + 120
    while (rec := api('GET', f'orders/{oid}', token=token)[1]).get('status') != 'paid' and time.time() < deadline:
        time.sleep(3)
    check(rec.get('status') == 'paid', f'marked paid at {rec.get("paid")}')
    got = kv.wait(f'file:{oid}/', files, lambda e: not any(e.values()))
    check(set(got) == files and not any(got.values()), 'the files no longer expire')
    check(kv.wait(f'order:{oid}', {f'order:{oid}'}, lambda e: not any(e.values())).get(f'order:{oid}') is None,
          'nor does the record')
    deadline = time.time() + 90  # this location may hold the old count for up to a minute
    while (cap1 := api('GET', f'products/{slug}', token=token)[1])['count'] == cap0['count'] and time.time() < deadline:
        time.sleep(5)
    check(cap1['count'] == cap0['count'] + 1, f'counted in {cap1["week"]}: {cap1["count"]} of {cap1["cap"]}')

    print('Resend the webhook')
    event = None
    for _ in range(20):
        events = stripe('GET', 'events?type=checkout.session.completed&limit=20')['data']
        event = next((e for e in events if e['data']['object']['id'] == cs['id']), None)
        if event:
            break
        time.sleep(3)
    check(event is not None, f'found {event["id"] if event else "no event"}')
    body = json.dumps(event)
    status, note = http('POST', f'{WORKER}/stripe', body.encode(),
                        {'Content-Type': 'application/json', 'Stripe-Signature': signed(body, hook_secret)})
    check(status == 200 and b'already paid' in note, f'the Worker answered: {note.decode()}')
    after = api('GET', f'orders/{oid}', token=token)[1]
    cap2 = api('GET', f'products/{slug}', token=token)[1]
    check(after == rec, 'the order record is unchanged')
    check(cap2['count'] == cap1['count'], 'the week\'s count is unchanged')
    check(not any(kv.keys(f'file:{oid}/').values()), 'the files still don\'t expire')
    bad = re.sub(r'v1=[0-9a-f]+', 'v1=' + '0' * 64, signed(body, hook_secret))
    status, _ = http('POST', f'{WORKER}/stripe', body.encode(), {'Content-Type': 'application/json', 'Stripe-Signature': bad})
    check(status == 400, 'a bad signature gets a 400')
    status, _ = http('POST', f'{WORKER}/stripe', body.encode(), {'Content-Type': 'application/json'})
    check(status == 400, 'no signature gets a 400')

    print('Queue')
    queue('pull')
    folder = next(ROOT.glob(f'.private/orders/*-{oid}'), None)
    check(folder is not None, f'pulled into {folder.relative_to(ROOT) if folder else "nothing"}')
    for name, data in sent.items():
        check((folder / name).read_bytes() == data, f'{name} on disk, byte for byte')
    order = json.loads((folder / 'order.json').read_text())
    record = (folder / 'order.json').read_text() + (folder / 'design.json').read_text()
    check(all(s not in record for s in (ADDRESS['line1'], ADDRESS['postal_code'], BUYER['name'], BUYER['email'])),
          'no name, email or address on disk')
    check(round(order['amount']['subtotal'] * 100) == want and order['status'] == 'paid', 'order.json: paid, at the file\'s price')
    listed = queue('list')
    check(oid in listed.stdout, 'queue.py list shows it')

    if args.keep:
        print(f'Kept: {oid} stays in the queue. Remove it with: python3 tools/orders/queue.py purge {oid}')
        return
    print('Purge')
    queue('purge', oid)
    check(api('GET', f'orders/{oid}', token=token)[1].get('status') == 'purged', 'the Worker keeps only a tombstone')
    check(not kv.wait(f'file:{oid}/', set(), lambda e: True), 'no files left in KV')
    left = sorted(p.name for p in folder.iterdir())
    check(left == ['design.json', 'order.json'], f'on disk only {", ".join(left)}')
    print(f'Done: {oid}')


if __name__ == '__main__':
    main()
