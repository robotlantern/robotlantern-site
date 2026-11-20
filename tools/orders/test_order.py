"""Place a photo order end to end in Stripe's sandbox, then pull it (docs/ORDERS.md, "Testing").

    python3 tools/orders/test_order.py                               # the test-photo fixture
    python3 tools/orders/test_order.py --product lithophane-ornament
    python3 tools/orders/test_order.py --keep                        # leave it in the queue
    python3 tools/orders/test_order.py --product cutout-ornament     # drawings and an order of designs
    python3 tools/orders/test_order.py --product cutout-ornament --real-drawing   # plus one real drawing

It draws a test picture (shapes on a gradient, never anyone's photo), sends design.json with a
made-up price, uploads the files and checks the unpaid ones expire in two days. Then it opens
checkout, pays with Stripe's test card token, shipping to the West Virginia State Capitol (so tax
shows), waits for the webhook, and checks the files no longer expire and the week's count went up.
It resends the webhook and checks nothing changed, sends a bad signature, pulls the order with
queue.py and lists the queue. Last, it purges the order, in KV and on disk, unless --keep.

A product made from drawings (the stencil ornament) runs its own test instead: drawings with OpenAI
stubbed (the sandbox Worker returns shop-worker/stub-drawing.png to a request with the queue's token and
X-Stub), the caps, the switches, an own drawing, an order of three designs (made, own and ready-made) with
its refusals, checkout, the paid step, the queue's files, made-up build files, a proof link, the Slant draft's
dry run, shipping, stats and the purge. --real-drawing adds one real GPT Image call with a drawn cat, which
costs about $0.06 and counts against the caps; the drawing is saved in .private/test-drawings/.

Sandbox only: it refuses a live key. Each run costs about 20 of KV's 1,000 free writes a day, and
counts against the product's weekly cap in the sandbox's namespace. It needs macOS's sips for JPEGs.
Like tools/shop/test_order.py, it pays through the endpoints the Stripe CLI uses, which aren't in
Stripe's public reference.
"""
import argparse
import base64
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


def api(method, path, body=None, ctype=None, token=None, headers=None):
    headers = {'Origin': ORIGIN, **(headers or {})}
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


def cat_picture(edge=1024):
    """A drawn cartoon cat (never anyone's pet): an orange head with ears, eyes and a muzzle on a sky."""
    cx, cy, r = edge * 0.5, edge * 0.55, edge * 0.3
    ears = [((cx - r * 0.95, cy - r * 0.35), (cx - r * 0.55, cy - r * 1.35), (cx - r * 0.1, cy - r * 0.8)),
            ((cx + r * 0.95, cy - r * 0.35), (cx + r * 0.55, cy - r * 1.35), (cx + r * 0.1, cy - r * 0.8))]

    def inside(px, py, tri):
        (x1, y1), (x2, y2), (x3, y3) = tri
        d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        a = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / d
        b = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / d
        return a >= 0 and b >= 0 and a + b <= 1

    rows = []
    for y in range(edge):
        t = y / edge
        sky = (int(120 + 90 * t), int(170 + 50 * t), int(220 - 30 * t))
        row = bytearray()
        for x in range(edge):
            c = sky
            dx, dy = (x - cx) / r, (y - cy) / r
            if dx * dx + dy * dy < 1 or any(inside(x, y, e) for e in ears):
                shade = int(30 * (dy + 1))
                c = (235 - shade, 140 - shade, 40)
                if (dx * 1.6) ** 2 + ((dy - 0.45) * 2.2) ** 2 < 1:
                    c = (250, 240, 225)                                   # muzzle
                for ex in (-0.38, 0.38):
                    if ((dx - ex) * 5) ** 2 + ((dy + 0.12) * 3.6) ** 2 < 1:
                        c = (40, 110, 40) if ((dx - ex) * 12) ** 2 + ((dy + 0.12) * 5) ** 2 > 1 else (10, 10, 10)
                if ((dx) * 9) ** 2 + ((dy - 0.28) * 12) ** 2 < 1:
                    c = (230, 120, 140)                                   # nose
            row += bytes(c)
        rows.append(bytes(row))
    return png(edge, edge, rows)


def two_colour(edge, cut=0.2):
    """An own drawing: a red disc with white cut-outs on white, exactly two colours."""
    red, white = b'\xe0\x10\x10', b'\xff\xff\xff'
    rows = []
    for y in range(edge):
        row = bytearray()
        for x in range(edge):
            dx, dy = (x - edge / 2) / (edge * 0.4), (y - edge / 2) / (edge * 0.4)
            ink = dx * dx + dy * dy < 1 and not (abs(dx) < 0.5 and abs(dy + 0.2) < cut) and not (dx * dx + (dy - 0.5) ** 2 < 0.03)
            row += red if ink else white
        rows.append(bytes(row))
    return png(edge, edge, rows)


def tier_price(p, designs):
    """The product file's price for these designs (docs/ORDERS.md, "pricing"), as the Worker works it out."""
    n = sum(d['quantity'] for d in designs)
    tier = [t for t in p['pricing']['tiers'] if t['from'] <= n][-1]
    return round(100 * tier['each']) * n


def ornament(args, p, slug):
    """The stencil ornament: drawings (stubbed unless --real-drawing), an order of three designs, the paid
    step, the queue, the build files, a proof link, the Slant dry run, shipping and the purge."""
    key = sync.secret('STRIPE_SECRET_KEY_TEST')
    if not key.startswith('sk_test_'):
        raise SystemExit('not a test key')
    stripe = sync.Stripe(key)
    token = env_file('orders.env')['ORDERS_QUEUE_TOKEN_TEST']
    kv = KV()
    pool = f'run{int(time.time())}'
    stub = {'X-Stub': pool, 'X-Subject': 'pet'}
    stub_png = (ROOT / 'shop-worker/stub-drawing.png').read_bytes()

    def draw(body, headers, ctype='image/jpeg', path='drawings', tok=token):
        return api('POST', path, body, ctype, tok, headers)

    print(f'{slug}: the product')
    status, cap = api('GET', f'products/{slug}', token=token)
    check(status == 200 and cap['open'] and cap['drawings'] and cap['orders'], f'open, drawings and orders on ({cap.get("count")} of {cap.get("cap")} this week)')
    check(cap['pricing']['tiers'] == p['pricing']['tiers'], 'price tiers from the product file')

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        cat = cat_picture()
        photo = jpeg(cat, tmp, 'photo')
        small = jpeg(cat, tmp, 'small', size=800)
        preview = jpeg(cat, tmp, 'preview', size=640)
    own = two_colour(1024)

    print('Drawings, with OpenAI stubbed')
    status, d1 = draw(photo, stub)
    check(status == 201 and d1['n'] == 1 and d1['left'] == 2 and d1['source'] == 'made', f'made {d1.get("id")}: try 1, 2 left')
    check(base64.b64decode(d1['image']) == stub_png, 'the image is the drawing, as base64 PNG')
    did = d1['id']
    status, d2 = draw(b'', stub, path=f'drawings/{did}/again', ctype=None)
    check(status == 201 and d2['n'] == 2 and d2['left'] == 1, 'again: try 2, 1 left')
    status, d3 = draw(b'', stub, path=f'drawings/{did}/again', ctype=None)
    check(status == 201 and d3['n'] == 3 and d3['left'] == 0, 'again: try 3, none left')
    status, d4 = draw(b'', stub, path=f'drawings/{did}/again', ctype=None)
    check(status == 409 and d4.get('left') == 0, f'a fourth try is refused: {d4.get("error")}')
    for headers, body, ctype, want, what in (
            ({**stub, 'X-Subject': 'dragon'}, photo, 'image/jpeg', 400, 'a subject the product file lacks'),
            ({**stub, 'X-Subject': 'gag'}, photo, 'image/jpeg', 400, 'a ready-made subject'),
            (stub, own, 'image/png', 415, 'a PNG for a photo'),
            (stub, small, 'image/jpeg', 400, 'an 800 px photo'),
            (stub, b'not a jpeg at all', 'image/jpeg', 415, 'bytes that aren\'t a JPEG')):
        status, res = draw(body, headers, ctype)
        check(status == want, f'{what}: {status} {res.get("error") if isinstance(res, dict) else res}')
    files = {f'file:drawing:{did}/{n}' for n in ('photo.jpg', '1.png', '2.png', '3.png')}
    expires = int(datetime.fromisoformat(d1['expires'].replace('Z', '+00:00')).timestamp())
    got = kv.wait(f'file:drawing:{did}/', files, lambda e: all(e.values()))
    check(set(got) == files and all(v == expires for v in got.values()), f'photo and 3 tries in KV, expiring {d1["expires"]}')
    check(kv.wait(f'drawing:{did}', {f'drawing:{did}'}, lambda e: True).get(f'drawing:{did}') == expires, 'the record expires with them')

    print('Caps')
    for i in range(3):
        status, res = draw(photo, stub)
        check(status == 201, f'drawing {4 + i} of {6} for this visitor')
    status, res = draw(photo, stub)
    check(status == 429 and res.get('retryAfter', 0) > 0, f'the 7th is refused until tomorrow: {res.get("error")}')
    status, res = draw(photo, {**stub, 'Signature-Agent': '"https://agent.example"'})
    check(status == 201, 'an agent (Signature-Agent) counts in its own pool')

    print('Switches (the sandbox\'s, back on within a couple of minutes)')
    probe = lambda: draw(b'x', {'X-Subject': 'pet'}, 'text/plain', tok=None)  # noqa: E731
    order_probe = lambda: api('POST', 'orders', {'product': slug, 'designs': [{'drawing': {'static': 'gag/toilet'}, 'options': {'base': 'white', 'stencil': 'red', 'tag': 'no'}, 'quantity': 1}], 'price': 0.01}, 'application/json')  # noqa: E731
    check(probe()[0] == 415 and order_probe()[0] == 409, 'on: requests get as far as their own checks')
    try:
        switch('drawings', 'off')
        switch('orders', 'off')
        check(until(lambda: probe()[0] == 503) and until(lambda: order_probe()[0] == 503), 'off: drawings and orders get 503')
        status, res = draw(own, {'X-Source': 'upload', 'X-Stub': pool}, 'image/png')
        check(status == 201, 'own drawings still go in with drawings off')
    finally:
        switch('drawings', 'on')
        switch('orders', 'on')
    check(until(lambda: probe()[0] == 415) and until(lambda: order_probe()[0] == 409), 'on again')

    print('Own drawing (X-Source: upload)')
    up_headers = {'X-Source': 'upload', 'X-Stub': pool}
    status, up = draw(own, up_headers, 'image/png')
    check(status == 201 and up['left'] == 0 and up['source'] == 'upload' and 'image' not in up, f'stored {up.get("id")}: no tries, nothing echoed')
    uid = up['id']
    status, res = draw(b'', stub, path=f'drawings/{uid}/again', ctype=None)
    check(status == 409, 'again is refused for an own drawing')
    for body, ctype, want, what in ((two_colour(800), 'image/png', 400, 'an 800 px PNG'), (photo, 'image/png', 415, 'a JPEG sent as PNG'),
                                    (photo, 'image/jpeg', 415, 'a JPEG')):
        status, res = draw(body, up_headers, ctype)
        check(status == want, f'{what}: {status} {res.get("error")}')
    got = kv.wait(f'file:drawing:{uid}/', {f'file:drawing:{uid}/1.png'}, lambda e: all(e.values()))
    check(set(got) == {f'file:drawing:{uid}/1.png'}, 'stored as try 1, with no photo')

    print('Order: three designs, made, own and ready-made')
    toilet = next(x for s in p['drawing']['subjects'] if s['id'] == 'gag' for x in s['designs'] if x['id'] == 'toilet')
    designs = [
        {'drawing': {'id': did, 'n': 2}, 'options': {'base': 'white', 'stencil': 'red', 'tag': 'yes', 'font': 'allerta'},
         'text': 'Test Cat', 'quantity': 1},
        {'drawing': {'id': uid, 'n': 1}, 'options': {'base': 'black', 'stencil': 'gold', 'tag': 'no'}, 'quantity': 2},
        {'drawing': {'static': 'gag/toilet'}, 'options': {'base': 'white', 'stencil': 'green', 'tag': 'yes', 'font': 'allerta'},
         'quantity': 1},
    ]
    want = tier_price(p, designs)
    order = {'product': slug, 'designs': designs, 'price': want / 100, 'version': 'tools/orders/test_order.py'}

    def variant(i, **change):
        ds = json.loads(json.dumps(designs))
        for k, v in change.items():
            if k == 'options':
                ds[i]['options'].update(v)
            else:
                ds[i][k] = v
        return {**order, 'designs': ds, 'price': tier_price(p, ds) / 100}

    refusals = [
        ({**order, 'price': 0.01}, 409, 'a made-up price of $0.01'),
        ({k: v for k, v in order.items() if k != 'price'}, 400, 'no price'),
        (variant(0, options={'stencil': 'white'}), 400, 'base and stencil the same colour'),
        (variant(0, options={'glitter': 'yes'}), 400, 'an option the product file lacks'),
        (variant(0, options={'stencil': 'clear'}), 400, 'a colour that isn\'t offered'),
        (variant(0, text='Fairmont General'), 400, '"Fairmont General", which doesn\'t fit in Allerta'),
        (variant(0, text='Thanksgiving 2026'), 400, '17 characters'),
        (variant(0, text='Tucker <3'), 400, 'a character the tag doesn\'t take'),
        (variant(0, text='   '), 400, 'a blank tag'),
        (variant(0, drawing={'id': did, 'n': 4}), 400, 'a try that wasn\'t made'),
        (variant(0, drawing={'id': 'zzzzzzzzzzzz', 'n': 1}), 400, 'a drawing that doesn\'t exist'),
        (variant(2, drawing={'static': 'gag/unicorn'}), 400, 'a ready-made design that doesn\'t exist'),
        (variant(1, quantity=0), 400, 'a quantity of 0'),
        (variant(1, quantity=p['pricing']['maxPerOrder']), 400, f'more than {p["pricing"]["maxPerOrder"]} ornaments'),
        (variant(0, kind='inlay'), 400, 'a kind not made yet'),
        ({**order, 'designs': designs * 5, 'price': tier_price(p, designs * 5) / 100}, 400, f'more than {p["pricing"]["maxDesigns"]} designs'),
    ]
    for body, code, what in refusals:
        status, res = api('POST', 'orders', body, 'application/json')
        check(status == code, f'refused, {what}: {res.get("error")}')
        if what.startswith('a made-up'):
            check(round(res.get('price', 0) * 100) == want, f'the refusal gives the price, ${want / 100:.2f}')
    status, alt = api('POST', 'orders', variant(0, text='Thanksgiving'), 'application/json')
    check(status == 201, 'tag text that fits in Allerta is taken')
    status, res = api('POST', 'orders', variant(0, text='Fairmont General', options={'font': 'big-shoulders'}), 'application/json')
    check(status == (201 if tag_fits('Fairmont General', 'big-shoulders') else 400), f'the fit follows the font ({status})')
    if status == 201:
        api('DELETE', f'orders/{res["id"]}', token=token)
    status, made = api('POST', 'orders', order, 'application/json')
    check(status == 201 and round(made.get('price', 0) * 100) == want, f'created {made.get("id") or made}:${want / 100:.2f} for {made.get("count")} ornaments')
    oid = made['id']
    check(made['files'] == ['1/preview.jpg', '2/preview.jpg', '3/preview.jpg'], 'it asks for a preview of each design')

    status, early = api('POST', f'orders/{alt["id"]}/checkout')
    check(status == 409 and len(early.get('missing', [])) == 3, 'checkout refused without the previews')

    print('Previews and checkout')
    for k in (1, 2, 3):
        status, res = api('PUT', f'orders/{oid}/{k}/preview.jpg', preview, 'image/jpeg')
        check(status == 201 and res['size'] == len(preview), f'{k}/preview.jpg: {len(preview):,} bytes')
    status, _ = api('PUT', f'orders/{oid}/4/preview.jpg', preview, 'image/jpeg')
    check(status == 404, 'there\'s no design 4')
    status, _ = api('PUT', f'orders/{oid}/1/preview.jpg', own, 'image/png')
    check(status == 415, 'a preview must be a JPEG')
    status, co = api('POST', f'orders/{oid}/checkout')
    check(status == 200 and co['url'].startswith('https://checkout.stripe.com/'), 'checkout page opened')
    status, _ = api('PUT', f'orders/{oid}/1/preview.jpg', preview, 'image/jpeg')
    check(status == 409, 'previews are fixed once checkout opens')
    cs = stripe('GET', 'checkout/sessions/' + re.search(r'cs_test_[A-Za-z0-9]+', co['url']).group(0))
    lines = stripe('GET', f'checkout/sessions/{cs["id"]}/line_items?limit=20')['data']
    check([li['quantity'] for li in lines] == [1, 2, 1], 'one line per design, with its quantity')
    check(cs['amount_subtotal'] == want, f'session subtotal ${cs["amount_subtotal"] / 100:.2f}')

    print('Pay with the test card')
    page = stripe('POST', f'payment_pages/{cs["id"]}', {'tax_region': ADDRESS})
    card = stripe('POST', 'payment_methods', {'type': 'card', 'card': {'token': 'tok_visa'}, 'billing_details': BUYER})
    stripe('POST', f'payment_pages/{cs["id"]}/confirm', {
        'payment_method': card['id'], 'expected_amount': page['total_summary']['due'],
        'shipping': {'name': BUYER['name'], 'address': ADDRESS}})
    paid = stripe('GET', f'checkout/sessions/{cs["id"]}')
    check(paid['payment_status'] == 'paid', f'paid ${paid["amount_total"] / 100:.2f} (tax ${paid["total_details"]["amount_tax"] / 100:.2f})')

    print('Webhook')
    deadline = time.time() + 120
    while (rec := api('GET', f'orders/{oid}', token=token)[1]).get('status') != 'paid' and time.time() < deadline:
        time.sleep(3)
    check(rec.get('status') == 'paid' and rec.get('state') == 'paid', f'paid at {rec.get("paid")}, state paid')
    want_files = {f'file:{oid}/{n}' for n in ('1/design.json', '1/photo.jpg', '1/drawing.png', '1/preview.jpg',
                                              '2/design.json', '2/drawing.png', '2/preview.jpg', '3/design.json', '3/preview.jpg')}
    got = kv.wait(f'file:{oid}/', want_files, lambda e: not any(e.values()))
    check(set(got) == want_files and not any(got.values()), 'each design\'s folder, with no expiry (no photo or drawing for the ready-made one)')
    check(not any(s in json.dumps(rec) for s in (ADDRESS['line1'], BUYER['email'])), 'no address or email in the record')

    print('Queue')
    status, q = api('GET', 'queue', token=token)
    check(status == 200 and any(r['id'] == oid and r['state'] == 'paid' for r in q['queue']), 'GET /api/queue lists it')
    status, dj1 = api('GET', f'orders/{oid}/1/design.json', token=token)
    check(dj1.get('source') == 'made' and dj1.get('text') == 'Test Cat' and dj1.get('drawing') == {'id': did, 'n': 2}, 'design 1: made, try 2, "Test Cat"')
    status, dj2 = api('GET', f'orders/{oid}/2/design.json', token=token)
    check(dj2.get('source') == 'upload' and 'text' not in dj2 and dj2['options']['font'] == 'allerta', 'design 2: upload, no text, the default font')
    status, dj3 = api('GET', f'orders/{oid}/3/design.json', token=token)
    check(dj3.get('source') == 'static' and dj3.get('sha256') == toilet['sha256'] and dj3.get('text') == toilet['text'],
          f'design 3: ready-made, its sha256 and "{toilet["text"]}"')
    check(api('GET', f'orders/{oid}/1/drawing.png', token=token)[1] == stub_png, 'design 1\'s drawing.png is try 2')
    check(api('GET', f'orders/{oid}/2/drawing.png', token=token)[1] == own, 'design 2\'s is the own drawing, byte for byte')
    check(api('GET', f'orders/{oid}/1/photo.jpg', token=token)[1] == photo, 'design 1\'s photo.jpg, byte for byte')
    check(api('GET', f'orders/{oid}/3/drawing.png', token=token)[0] == 404, 'design 3 has no drawing.png')
    check(api('GET', f'orders/{oid}/1/design.json')[0] == 401, 'no token, no files')

    print('Build files')
    patch = lambda state, **kw: api('PATCH', f'orders/{oid}', {'state': state, **kw}, 'application/json', token)  # noqa: E731
    check(patch('shipped')[0] == 409, 'paid can\'t go straight to shipped')
    check(patch('built')[0] == 409, 'built needs each design\'s build.json and proof')
    stl = b'solid test\nendsolid test\n'
    status, _ = api('PUT', f'orders/{oid}/1/out/base.stl', stl, 'model/stl', token)
    check(status == 409, 'an STL before build.json is refused')
    parts = {}
    for d, k in zip(designs, (1, 2, 3)):
        o = d['options']
        parts[k] = [{'part': 'base', 'file': 'base.stl', 'colour': o['base']},
                    {'part': 'stencil', 'file': 'stencil.stl', 'colour': o['stencil']}]
        build = json.dumps({'ok': True, 'parts': parts[k]}).encode()
        check(api('PUT', f'orders/{oid}/{k}/out/build.json', build, 'application/json', token)[0] == 201, f'{k}/out/build.json')
        check(api('PUT', f'orders/{oid}/{k}/out/proof.png', stub_png, 'image/png', token)[0] == 201, f'{k}/out/proof.png')
        for part in parts[k]:
            check(api('PUT', f'orders/{oid}/{k}/out/{part["file"]}', stl, 'model/stl', token)[0] == 201, f'{k}/out/{part["file"]}')
    check(api('PUT', f'orders/{oid}/1/out/extra.stl', stl, 'model/stl', token)[0] == 400, 'an STL its parts don\'t list is refused')
    check(api('PUT', f'orders/{oid}/1/out/proof.png', preview, 'image/png', token)[0] == 415, 'a proof that isn\'t a PNG is refused')
    status, res = patch('built', note='test build')
    check(status == 200 and res['state'] == 'built', 'built')

    print('Proof link')
    status, links = api('GET', f'orders/{oid}/link/proof.png', token=token)
    check(status == 200 and [x['design'] for x in links['links']] == [1, 2, 3], f'three links, until {links.get("expires")}')
    status, body = http('GET', links['links'][0]['url'])
    check(status == 200 and body == stub_png, 'the link serves the proof with no token')
    status, _ = http('GET', re.sub(r's=[0-9a-f]{4}', 's=0000', links['links'][0]['url']))
    check(status == 403, 'a tampered link gets a 403')
    status, _ = http('GET', links['links'][0]['url'].replace(f'/{oid}/1/', f'/{oid}/2/'))
    check(status == 403, 'a link opens only its own design')

    print('Slant draft (a dry run: the sandbox never calls Slant)')
    fil = {c['id']: c['slant'] for o in p['options'] for c in o['choices'] if c.get('slant')}
    items = [{'design': k, 'part': part['part'], 'fileId': f'test-{k}-{part["part"]}', 'filamentId': fil[part['colour']],
              'quantity': designs[k - 1]['quantity']} for k in (1, 2, 3) for part in parts[k]]
    slant = lambda its: api('POST', f'orders/{oid}/slant', {'items': its}, 'application/json', token)  # noqa: E731
    check(slant(items[:-1])[0] == 400, 'a missing part is refused')
    check(slant([{**items[0], 'quantity': 5}] + items[1:])[0] == 400, 'a wrong quantity is refused')
    check(slant([{**items[0], 'filamentId': fil['blue']}] + items[1:])[0] == 400, 'the wrong colour is refused')
    status, dry = slant(items)
    check(status == 200 and dry.get('dryRun') and dry['state'] == 'drafted', 'drafted, as a dry run')
    sent = json.dumps(dry)
    check(len(dry['request']['items']) == 6 and dry['request']['customer']['details']['email'] == 'orders@robotlantern.com',
          'six print items, one box, orders@ as the email')
    check(not any(s in sent for s in (ADDRESS['line1'], ADDRESS['postal_code'], BUYER['name'], BUYER['email'])),
          'the address and name stay out of the answer')
    status, again = slant(items)
    check(status == 200 and again.get('recorded') and again['slant'] == dry['slant'], 'asking again returns what\'s recorded')

    print('Shipping')
    check(api('GET', f'orders/{oid}/contact', token=token)[0] == 409, 'no contact details before it ships')
    check(patch('processed')[0] == 200, 'processed')
    status, res = patch('shipped', tracking='TEST-TRACKING')
    check(status == 200 and res['tracking'] == 'TEST-TRACKING', 'shipped, with tracking')
    status, who = api('GET', f'orders/{oid}/contact', token=token)
    check(status == 200 and who['email'] == BUYER['email'], 'the contact endpoint gives the email, once shipped')
    check(patch('built')[0] == 409, 'shipped can\'t go back')

    print('Stats')
    status, st = api('GET', 'stats', token=token)
    check(status == 200 and st['switches'] == {'drawings': 'on', 'orders': 'on'}, 'switches on')
    check(st['kvWrites']['today'] > 0 and st['uploads']['today'] >= 1, f'{st["kvWrites"]["today"]} KV writes and {st["uploads"]["today"]} uploads today')
    check(st['orders'][slug]['count'] >= 1, f'{st["orders"][slug]["count"]} order(s) this week; drawings today ${st["drawings"]["dollarsToday"]:.2f} (stubs aren\'t counted)')

    if args.real_drawing:
        real_drawing(photo, token, st)

    if args.keep:
        print(f'Kept: {oid} stays in the queue, shipped. Purge it with: DELETE /api/orders/{oid}')
        return
    print('Purge')
    status, due = api('POST', 'purge?dry=1', token=token)
    check(status == 200 and oid not in [d['id'] for d in due['due']], 'not due yet: it shipped today')
    status, res = api('DELETE', f'orders/{oid}?keep=evidence', token=token)
    check(status == 200, f'purged now, keeping the evidence: {len(res["purged"])} files')
    kept = {f'file:{oid}/{k}/{n}' for k in (1, 2, 3) for n in ('preview.jpg', 'out/build.json')}
    check(set(kv.wait(f'file:{oid}/', kept, lambda e: True)) == kept, 'only each preview.jpg and build.json left')
    check(not kv.wait(f'file:drawing:{did}/', set(), lambda e: True) and not kv.wait(f'drawing:{did}', set(), lambda e: True),
          'the drawing\'s own files and record are gone')
    rec = api('GET', f'orders/{oid}', token=token)[1]
    check(rec['state'] == 'purged' and rec['designs'][0]['drawing'] == {'purged': True} and rec['designs'][2]['drawing'] == {'static': 'gag/toilet'},
          'the record stays, without drawing references')
    status, res = api('DELETE', f'orders/{oid}', token=token)
    check(status == 200 and not kv.wait(f'file:{oid}/', set(), lambda e: True), 'then everything')
    api('DELETE', f'orders/{alt["id"]}', token=token)
    print(f'Done: {oid}')


def real_drawing(photo, token, before):
    """One real GPT Image call (about $0.06, counted against the caps): the drawn cat, no stub."""
    print('A real drawing (OpenAI, about $0.06)')
    t0 = time.time()
    status, d = api('POST', 'drawings', photo, 'image/jpeg', headers={'X-Subject': 'pet'})
    check(status == 201 and d.get('n') == 1, f'drawn in {time.time() - t0:.0f} s: {d.get("id") if status == 201 else d}')
    out = ROOT / '.private/test-drawings'
    out.mkdir(parents=True, exist_ok=True)
    png_bytes = base64.b64decode(d['image'])
    (out / f'{d["id"]}.png').write_bytes(png_bytes)
    check(png_bytes.startswith(b'\x89PNG') and struct.unpack('>II', png_bytes[16:24]) == (1024, 1024),
          f'a 1024 x 1024 PNG, saved as {(out / (d["id"] + ".png")).relative_to(ROOT)}')
    deadline = time.time() + 90
    while (st := api('GET', 'stats', token=token)[1])['drawings']['today'] <= before['drawings']['today'] and time.time() < deadline:
        time.sleep(5)
    check(st['drawings']['today'] == before['drawings']['today'] + 1,
          f'counted: {st["drawings"]["today"]} today, ${st["drawings"]["dollarsToday"]:.2f} estimated')


def switch(what, state):
    subprocess.run([sys.executable, str(ROOT / 'tools/orders/switch.py'), what, state], check=True, capture_output=True)


def until(test, seconds=150):
    deadline = time.time() + seconds
    while not test():
        if time.time() > deadline:
            return False
        time.sleep(5)
    return True


def tag_fits(text, font):
    m = json.loads((ROOT / 'shop-worker/tag-metrics.json').read_text())
    return next((c['fits'] for c in m['cases'] if c['text'] == text and c['font'] == font), None)


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
    ap.add_argument('--real-drawing', action='store_true', help='also make one real drawing (about $0.06)')
    args = ap.parse_args()

    slug = args.product
    p = product_file(slug)
    if 'drawing' in p:
        return ornament(args, p, slug)
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
