"""The photo-order queue (docs/ORDERS.md): paid orders from Stripe and the shop Worker into
.private/orders/ on Sarcean, then making, shipping and, 60 days later, deleting the photos.

    python3 tools/orders/queue.py pull [--live]      # paid orders and their files
    python3 tools/orders/queue.py list [--all]       # the queue; --all includes purged orders
    python3 tools/orders/queue.py make <id>          # run the product's recipe (lithophane-maker)
    python3 tools/orders/queue.py ship <id> [--yes] [--tracking T] [--date YYYY-MM-DD]
    python3 tools/orders/queue.py purge [--dry-run] [<id> ...]

`pull` reads completed Checkout Sessions with the agents' Stripe key (the sandbox's unless --live),
and fetches each order's files from the Worker with the queue's token (orders.env in the secrets
folder). An order folder, `.private/orders/<date>-<id>/`, holds order.json, design.json and the
files; a recipe writes `out/`. Nothing on disk holds the customer's name, email or address: `ship`
reads the address from Stripe and only prints it, for the label.

An order goes paid -> made -> shipped -> purged. A fully refunded one becomes cancelled when `pull`
next sees it. `purge` deletes its photos and everything made from them, in KV and on disk, 60 days
after it shipped or was cancelled (NOW.md decision 6); with IDs, it purges those orders now.
order.json and design.json stay, as the order's record.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'shop'))
import sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ORDERS = ROOT / '.private/orders'
WORKER = os.environ.get('RL_SHOP_WORKER', 'https://shop.robotlantern.workers.dev')
MAKER = Path(os.environ.get('LITHO_MAKER', Path.home() / 'work/lab/lithophane-maker'))
KEEP_DAYS = 60
LOOKBACK_DAYS = 180
MAGIC = {'.jpg': b'\xff\xd8\xff', '.png': b'\x89PNG'}
RECORD = ('order.json', 'design.json')


def now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def iso(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def stripe_for(mode):
    key = sync.secret('STRIPE_SECRET_KEY' if mode == 'live' else 'STRIPE_SECRET_KEY_TEST')
    if not key.startswith(('sk_live_', 'rk_live_') if mode == 'live' else ('sk_test_', 'rk_test_')):
        raise SystemExit(f'the Stripe key for {mode} mode is the wrong kind')
    return sync.Stripe(key)


def token(mode):
    name = f'ORDERS_QUEUE_TOKEN_{mode.upper()}'
    for line in (sync.SECRETS / 'orders.env').read_text().splitlines():
        if line.startswith(name + '=') and line.split('=', 1)[1].strip():
            return line.split('=', 1)[1].strip()
    raise SystemExit(f'{name} missing from orders.env')


def worker(mode, method, path):
    """The Worker's queue endpoints. Returns (status, body bytes, headers)."""
    req = urllib.request.Request(f'{WORKER}/api/orders/{path}', method=method)
    req.add_header('Authorization', f'Bearer {token(mode)}')
    req.add_header('User-Agent', 'robot-lantern-queue')
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read(), r.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read(), e.headers


def folders():
    return sorted(p for p in ORDERS.glob('*-*') if (p / 'order.json').exists()) if ORDERS.exists() else []


def find(oid):
    hits = [p for p in folders() if p.name.endswith('-' + oid)]
    return hits[0] if hits else None


def load(folder):
    return json.loads((folder / 'order.json').read_text())


def save(folder, order):
    tmp = folder / 'order.json.tmp'
    tmp.write_text(json.dumps(order, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(folder / 'order.json')


def need(oid):
    folder = find(oid)
    if not folder:
        raise SystemExit(f'no order {oid} in {ORDERS.relative_to(ROOT)} (run pull first)')
    return folder, load(folder)


def shop_file(slug):
    for path in (ROOT / 'products' / slug / 'shop.json', ROOT / 'tools/orders/fixtures' / slug / 'shop.json'):
        if path.exists():
            return json.loads(path.read_text())
    return {}


def summary(p, options):
    labels = []
    for o in p.get('options') or []:
        c = next((c for c in o['choices'] if c['id'] == options.get(o['id'])), None)
        labels.append(f'{o["label"]}: {c["label"] if c else options.get(o["id"])}')
    return ', '.join(labels)


# ---- pull ---------------------------------------------------------------------------------

def paid_sessions(stripe):
    since = int((datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)).timestamp())
    after = None
    while True:
        page = stripe('GET', 'checkout/sessions?status=complete&limit=100&created[gte]=' + str(since)
                      + '&expand[]=data.payment_intent.latest_charge' + (f'&starting_after={after}' if after else ''))
        for s in page['data']:
            if (s.get('metadata') or {}).get('order') and s['payment_status'] == 'paid':
                yield s
        if not page['has_more']:
            return
        after = page['data'][-1]['id']


def refunded_on(stripe, s):
    """The date of the refund when the order's payment was refunded in full, else None."""
    pi = s.get('payment_intent')
    charge = pi.get('latest_charge') if isinstance(pi, dict) else None
    if not isinstance(charge, dict) or not charge.get('refunded'):
        return None
    refunds = stripe('GET', f'refunds?payment_intent={pi["id"]}&limit=1')['data']
    return iso(refunds[0]['created']) if refunds else now()


def fetch_files(mode, oid, folder, order, names):
    """Download what's missing. Returns the names still missing."""
    missing = []
    for name in names:
        if (folder / name).exists() and (name == 'design.json' or name in order['files']):
            continue
        status, body, headers = worker(mode, 'GET', f'{oid}/{name}')
        if status != 200:
            print(f'  {name}: the Worker said {status}')
            missing.append(name)
            continue
        size = headers.get('x-file-size')
        if name != 'design.json':
            if size and int(size) != len(body):
                print(f'  {name}: got {len(body)} bytes of {size}')
                missing.append(name)
                continue
            if not body.startswith(MAGIC[Path(name).suffix]):
                print(f'  {name}: not a {Path(name).suffix[1:].upper()} file. Kept, but look before using it.')
        tmp = folder / (name + '.part')
        tmp.write_bytes(body)
        tmp.replace(folder / name)
        if name != 'design.json':
            order['files'][name] = {'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()}
    return missing


def pull(mode):
    stripe = stripe_for(mode)
    ORDERS.mkdir(parents=True, exist_ok=True)
    seen = 0
    for s in paid_sessions(stripe):
        seen += 1
        oid = s['metadata']['order']
        folder = find(oid)
        order = load(folder) if folder else None
        if order and order['status'] in ('shipped', 'purged', 'cancelled'):
            continue
        cancelled = refunded_on(stripe, s)

        status, body, _ = worker(mode, 'GET', oid)
        rec = json.loads(body) if status == 200 else None
        if status not in (200, 404):
            print(f'{oid}: the Worker said {status}; try again later')
            continue
        if not order:
            slug = s['metadata'].get('product') or (rec or {}).get('product')
            p = shop_file(slug)
            options = (rec or {}).get('options') or {}
            created = datetime.fromtimestamp(s['created']).strftime('%Y-%m-%d')
            folder = ORDERS / f'{created}-{oid}'
            folder.mkdir(parents=True, exist_ok=True)
            total = s['total_details'] or {}
            order = {
                'id': oid, 'mode': mode, 'session': s['id'],
                'paymentIntent': s['payment_intent']['id'] if isinstance(s['payment_intent'], dict) else s['payment_intent'],
                'product': slug, 'name': p.get('name', slug), 'recipe': p.get('recipe'),
                'options': options, 'summary': summary(p, options),
                'amount': {'subtotal': s['amount_subtotal'] / 100, 'shipping': total.get('amount_shipping', 0) / 100,
                           'tax': total.get('amount_tax', 0) / 100, 'total': s['amount_total'] / 100},
                'status': 'paid', 'files': {}, 'tracking': None,
                'dates': {'ordered': iso(s['created']), 'paid': (rec or {}).get('paid'), 'pulled': None,
                          'made': None, 'shipped': None, 'cancelled': None, 'purged': None},
            }
            save(folder, order)

        if cancelled:
            order['status'] = 'cancelled'
            order['dates']['cancelled'] = cancelled
            save(folder, order)
            print(f'{oid}: refunded, so cancelled; its photos go on '
                  f'{(datetime.fromisoformat(cancelled[:10]) + timedelta(days=KEEP_DAYS)).date()}')
            continue
        if not rec or rec.get('status') == 'purged':
            print(f'{oid}: its files are no longer in the Worker ({"purged" if rec else "not found"})')
            continue
        if rec.get('status') != 'paid':
            print(f'{oid}: paid in Stripe, but the webhook hasn\'t marked it paid yet. Pulling its files anyway.')
        missing = fetch_files(mode, oid, folder, order, ['design.json'] + rec['files'])
        order['dates']['paid'] = order['dates']['paid'] or rec.get('paid')
        if not missing and not order['dates']['pulled']:
            order['dates']['pulled'] = now()
            print(f'{oid}: pulled to {folder.relative_to(ROOT)} ({order["name"]}; {order["summary"] or "no options"})')
        elif missing:
            print(f'{oid}: still missing {", ".join(missing)}; pull again')
        save(folder, order)
    print(f'{seen} paid photo order(s) in Stripe ({mode}).')


# ---- list, make, ship, purge ----------------------------------------------------------------

def due(order):
    """When the order's photos are due to be deleted, or None."""
    for status in ('shipped', 'cancelled'):
        if order['status'] == status and order['dates'].get(status):
            return date.fromisoformat(order['dates'][status][:10]) + timedelta(days=KEEP_DAYS)
    return None


def list_orders(show_all):
    rows = [load(f) | {'_folder': f} for f in folders()]
    rows = [o for o in rows if show_all or o['status'] != 'purged']
    if not rows:
        print('No orders.' if show_all else 'No orders waiting. (--all shows purged ones too.)')
        return
    for o in rows:
        f = o['_folder']
        files = [n for n in o['files'] if (f / n).exists()]
        note = f'{len(files)} file(s)'
        if (f / 'out').is_dir():
            note += ', out/ made'
        if d := due(o):
            note += f', photos go {d}'
        print(f'{f.name[:10]}  {o["id"]}  {o["mode"]:<4}  {o["status"]:<9}  {o["name"]}'
              f'{" (" + o["summary"] + ")" if o.get("summary") else ""}  {note}')


def make(oid):
    folder, order = need(oid)
    if order['status'] not in ('paid', 'made'):
        raise SystemExit(f'{oid} is {order["status"]}')
    missing = [n for n in order['files'] if not (folder / n).exists()]
    if missing or not order['files']:
        raise SystemExit(f'{oid}: files missing ({", ".join(missing) or "none pulled"}); run pull')
    recipe = order.get('recipe')
    script = MAKER / 'products' / f'{recipe}.py'
    if not recipe or not script.exists():
        print(f'{oid}: there\'s no recipe for {order["name"]} yet ({script} isn\'t there). '
              f'Make it by hand from {folder.relative_to(ROOT)}, or wait for the recipe.')
        return
    python = MAKER / '.venv/bin/python'
    print(f'{oid}: running {script.relative_to(MAKER)} on {folder.relative_to(ROOT)}')
    done = subprocess.run([str(python if python.exists() else sys.executable), str(script), str(folder)], cwd=MAKER)
    if done.returncode:
        raise SystemExit(f'{oid}: the {recipe} recipe failed (exit {done.returncode}); the order is unchanged')
    order['status'] = 'made'
    order['dates']['made'] = now()
    save(folder, order)
    made = sorted(p.name for p in (folder / 'out').glob('*')) if (folder / 'out').is_dir() else []
    print(f'{oid}: made. out/: {", ".join(made) or "(empty)"}. Compare proof.png with preview.jpg.')


def ship(oid, yes, tracking, when):
    folder, order = need(oid)
    if order['status'] not in ('paid', 'made'):
        raise SystemExit(f'{oid} is {order["status"]}')
    s = stripe_for(order['mode'])('GET', f'checkout/sessions/{order["session"]}')
    ship_to = (s.get('collected_information') or {}).get('shipping_details') or s.get('shipping_details') or {}
    a = ship_to.get('address') or {}
    # Shown for the label, never saved.
    print(f'{order["name"]}{" (" + order["summary"] + ")" if order.get("summary") else ""}, order {oid}\n')
    print('\n'.join(x for x in [ship_to.get('name'), a.get('line1'), a.get('line2'),
                                f'{a.get("city")}, {a.get("state")} {a.get("postal_code")}', a.get('country')] if x))
    print()
    if not yes:
        if not sys.stdin.isatty():
            print('Not marked shipped (add --yes to mark it).')
            return
        if input('Mark it shipped? [y/N] ').strip().lower() != 'y':
            return
    order['status'] = 'shipped'
    order['dates']['shipped'] = when or date.today().isoformat()
    order['tracking'] = tracking
    save(folder, order)
    print(f'{oid}: shipped {order["dates"]["shipped"]}; its photos go {due(order)}.')


def purge(ids, dry_run):
    today = date.today()
    picked = []
    for f in folders():
        o = load(f)
        if o['status'] == 'purged':
            continue
        if ids:
            if o['id'] in ids:
                picked.append((f, o))
        elif (d := due(o)) and d <= today:
            picked.append((f, o))
    unknown = set(ids) - {o['id'] for _, o in picked}
    if unknown:
        print(f'not in the queue, or purged already: {", ".join(sorted(unknown))}')
    for f, o in picked:
        local = [p for p in f.iterdir() if p.name not in RECORD]
        print(f'{o["id"]}: {"would delete" if dry_run else "deleting"} its photos in KV and '
              f'{", ".join(sorted(p.name for p in local)) or "nothing"} on disk')
        if dry_run:
            continue
        status, body, _ = worker(o['mode'], 'DELETE', o['id'])
        if status != 200:
            print(f'  the Worker said {status}: {body[:200]!r}. Nothing deleted; try again.')
            continue
        for p in local:
            shutil.rmtree(p) if p.is_dir() else p.unlink()
        o['status'] = 'purged'
        o['dates']['purged'] = now()
        save(f, o)
    if not picked:
        print('Nothing to purge.')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('pull')
    p.add_argument('--live', action='store_true')
    sub.add_parser('list').add_argument('--all', action='store_true')
    sub.add_parser('make').add_argument('id')
    p = sub.add_parser('ship')
    p.add_argument('id')
    p.add_argument('--yes', action='store_true', help='mark it shipped without asking')
    p.add_argument('--tracking')
    p.add_argument('--date', help='the day it shipped, if not today (YYYY-MM-DD)')
    p = sub.add_parser('purge')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('ids', nargs='*')
    a = ap.parse_args()
    if a.cmd == 'pull':
        pull('live' if a.live else 'test')
    elif a.cmd == 'list':
        list_orders(a.all)
    elif a.cmd == 'make':
        make(a.id)
    elif a.cmd == 'ship':
        if a.date:
            date.fromisoformat(a.date)
        ship(a.id, a.yes, a.tracking, a.date)
    elif a.cmd == 'purge':
        purge(a.ids, a.dry_run)


if __name__ == '__main__':
    main()
