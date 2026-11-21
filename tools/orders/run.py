"""The orders run for drawing products (docs/PRODUCTION.md, "The orders run"; docs/ORDERS.md, "Contracts").

    python3 tools/orders/run.py status [--live]            # the queue: what's paid, built, drafted, flagged
    python3 tools/orders/run.py build <id> [--live]        # each design: fetch, make.py, store out/, built or needs-rj
    python3 tools/orders/run.py flag <id> "<what's wrong>" [--live]   # to needs-rj, with the note
    python3 tools/orders/run.py slant <id> [--live]        # upload and quote every part, then the Worker's draft
    python3 tools/orders/run.py email <id> [--live]        # the "Ready for Slant" email to RJ, printed

The sandbox (shop.robotlantern.workers.dev) unless --live (robotlantern.com). In the sandbox the Worker's Slant
draft is always a dry run. Nothing here processes, cancels or edits a Slant order, refunds, or emails anyone:
`email` only prints the message for whoever sends it.

`build` works in a folder per order, `.private/orders/<id>/<k>/` in a checkout that has `.private/` (Sarcean), or
the system's temp folder otherwise (the cloud). Each design folder ends up with design.json, drawing.png,
preview.jpg and out/, so the proof can be compared with the preview. It never fetches photo.jpg: the build
doesn't need it. Run it with the Python that has tools/ornament/requirements.txt (/opt/rl/bin/python in the
cloud), because it runs make.py with the same interpreter.

Keys: ORDERS_QUEUE_TOKEN_TEST / _LIVE, SLANT_API_KEY and SLANT_PLATFORM_ID come from the environment, or from
the secrets folder when it exists. In the cloud the tokens are network secrets the proxy adds, so with no key
set, no Authorization header is sent (docs/PRODUCTION.md, "Secrets").
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/ornament'))
import slant as slantapi  # noqa: E402

SECRETS = Path(os.environ.get('RL_SECRETS', Path.home() / '.codex/secrets/robot-lantern'))
WORKER = {'test': 'https://shop.robotlantern.workers.dev', 'live': 'https://robotlantern.com'}
TODO = ('paid', 'built', 'needs-rj')


def secret(name, file):
    if os.environ.get(name):
        return os.environ[name]
    path = SECRETS / file
    if path.exists():
        for line in path.read_text().splitlines():
            if line.startswith(name + '='):
                return line.split('=', 1)[1].strip()
    return None


class Worker:
    def __init__(self, mode):
        self.base = WORKER[mode] + '/api/'
        self.token = secret(f'ORDERS_QUEUE_TOKEN_{mode.upper()}', 'orders.env')

    def call(self, method, path, body=None, ctype=None, raw=False):
        headers = {'User-Agent': 'robot-lantern-orders-run'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        if isinstance(body, (dict, list)):
            body, ctype = json.dumps(body).encode(), 'application/json'
        if ctype:
            headers['Content-Type'] = ctype
        req = urllib.request.Request(self.base + path, data=body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                status, data = r.status, r.read()
        except urllib.error.HTTPError as e:
            status, data = e.code, e.read()
        if raw:
            return status, data
        try:
            return status, json.loads(data)
        except ValueError:
            return status, {'error': data[:200].decode('utf-8', 'replace')}

    def need(self, method, path, body=None, ctype=None, raw=False):
        status, data = self.call(method, path, body, ctype, raw)
        if status >= 300:
            raise SystemExit(f'{method} /api/{path}: {status} {data if not raw else data[:200]!r}')
        return data


def product_file(slug):
    return json.loads((ROOT / 'products' / slug / 'shop.json').read_text())


def folder_for(oid):
    base = ROOT / '.private/orders' if (ROOT / '.private').is_dir() else Path(tempfile.gettempdir()) / 'rl-orders'
    return base / oid


def flag(w, oid, note):
    status, res = w.call('PATCH', f'orders/{oid}', {'state': 'needs-rj', 'note': note})
    print(f'{oid}: needs-rj ({note})' if status == 200 else f'{oid}: could not flag: {status} {res}')
    return 1


def status(w, args):
    q = w.need('GET', 'queue')['queue']
    todo = [o for o in q if o['state'] in TODO]
    for o in q:
        print(f'{o["id"]}  {o["product"]}  {o["state"]:<9}  paid {o.get("paid") or "-"}')
    if not todo:
        print('Nothing to do.')
    return 0


def build(w, args):
    oid = args.id
    rec = w.need('GET', f'orders/{oid}')
    # needs-rj too, so an order can be built again once RJ has fixed what stopped it.
    if rec.get('state') not in ('paid', 'needs-rj'):
        raise SystemExit(f'{oid} is {rec.get("state") or rec.get("status")}; build takes a paid or needs-rj order')
    # A Python without the builder's packages would fail every design and flag a good order.
    try:
        import cv2, numpy, trimesh  # noqa: F401
    except ImportError as e:
        raise SystemExit(f'{e}: run this with the builder\'s Python (tools/ornament/requirements.txt); nothing changed')
    p = product_file(rec['product'])
    statics = {f'{s["id"]}/{d["id"]}': d for s in p['drawing']['subjects'] for d in s.get('designs', [])}
    top = folder_for(oid)
    failed = []
    for d in rec['designs']:
        k = d['k']
        f = top / str(k)
        (f / 'out').mkdir(parents=True, exist_ok=True)
        design = w.need('GET', f'orders/{oid}/{k}/design.json')
        (f / 'design.json').write_text(json.dumps(design, indent=1) + '\n')
        (f / 'preview.jpg').write_bytes(w.need('GET', f'orders/{oid}/{k}/preview.jpg', raw=True))
        if design.get('source') == 'static':
            ref = design['drawing']['static']
            if ref not in statics:
                failed.append(f'design {k}: no ready-made design {ref} in the product file')
                continue
            png = (ROOT / 'products' / rec['product'] / statics[ref]['drawing']).read_bytes()
            if hashlib.sha256(png).hexdigest() != design.get('sha256'):
                failed.append(f'design {k}: {ref} does not match its SHA-256')
                continue
        else:
            png = w.need('GET', f'orders/{oid}/{k}/drawing.png', raw=True)
        (f / 'drawing.png').write_bytes(png)
        r = subprocess.run([sys.executable, str(ROOT / 'tools/ornament/make.py'), str(f)], capture_output=True, text=True)
        print(f'design {k}: make.py exit {r.returncode}')
        print('\n'.join('  ' + line for line in (r.stdout or r.stderr).strip().splitlines()[-25:]))
        if r.returncode == 2 or not (f / 'out/build.json').exists():
            failed.append(f'design {k}: invalid ({(r.stderr or "").strip().splitlines()[-1:]})')
            continue
        rep = json.loads((f / 'out/build.json').read_text())
        if not rep['ok']:
            failed.append(f'design {k}: failed {", ".join(c for c, ok in rep["checks"].items() if not ok)}')
        # Stored either way, so RJ can see the proof of a failed build.
        w.need('PUT', f'orders/{oid}/{k}/out/build.json', (f / 'out/build.json').read_bytes(), 'application/json')
        w.need('PUT', f'orders/{oid}/{k}/out/proof.png', (f / 'out/proof.png').read_bytes(), 'image/png')
        for part in rep['parts']:
            w.need('PUT', f'orders/{oid}/{k}/out/{part["file"]}', (f / 'out' / part['file']).read_bytes(), 'model/stl')
    print(f'files in {top}')
    if failed:
        return flag(w, oid, '; '.join(failed))
    w.need('PATCH', f'orders/{oid}', {'state': 'built', 'note': 'built by tools/orders/run.py'})
    print(f'{oid}: built. Compare each proof.png with its preview.jpg before `run.py slant {oid}`.')
    return 0


def slant(w, args):
    oid = args.id
    rec = w.need('GET', f'orders/{oid}')
    if rec.get('state') != 'built':
        raise SystemExit(f'{oid} is {rec.get("state")}; slant takes a built order')
    p = product_file(rec['product'])
    filament = {c['id']: c.get('slant') for o in p['options'] for c in o['choices']}
    s = slantapi.Slant(secret('SLANT_API_KEY', 'slant.env'), secret('SLANT_PLATFORM_ID', 'slant.env'))
    available = {f.get('publicId') or f.get('id'): f.get('available', True) for f in s.filaments()}
    items, quotes = [], []
    with tempfile.TemporaryDirectory() as tmp:
        for d in rec['designs']:
            k, qty = d['k'], d['quantity']
            rep = w.need('GET', f'orders/{oid}/{k}/out/build.json')
            for part in rep['parts']:
                fid = filament.get(part['colour'])
                if not fid or not available.get(fid):
                    return flag(w, oid, f'design {k}: Slant has no {part["colour"]} filament available now')
                stl = Path(tmp) / f'{oid}-{k}-{part["part"]}.stl'
                stl.write_bytes(w.need('GET', f'orders/{oid}/{k}/out/{part["file"]}', raw=True))
                up = s.upload(stl)
                file_id = up.get('publicFileServiceId') or up.get('id')
                est = s.estimate(file_id, fid, qty)
                quotes.append({'design': k, 'part': part['part'], 'colour': part['colour'], 'quantity': qty,
                               'grams': (up.get('metrics') or {}).get('weight'), 'total': est.get('total')})
                items.append({'design': k, 'part': part['part'], 'fileId': file_id, 'filamentId': fid, 'quantity': qty})
                print(f'design {k} {part["part"]:<8} {part["colour"]:<16} x{qty}  ${float(est.get("total") or 0):.2f}')
    printing = sum(float(q['total'] or 0) for q in quotes)
    print(f'Slant quote for the parts: ${printing:.2f} (shipping shows only on the draft)')
    status_, res = w.call('POST', f'orders/{oid}/slant', {'items': items})
    print(json.dumps(res, indent=1))
    folder = folder_for(oid)
    if folder.is_dir():
        (folder / 'slant.json').write_text(json.dumps({'quotes': quotes, 'printing': round(printing, 2), 'draft': res}, indent=1) + '\n')
    return 0 if status_ == 200 else 1


def email(w, args):
    oid = args.id
    rec = w.need('GET', f'orders/{oid}')
    sl = rec.get('slant') or {}
    links = w.need('GET', f'orders/{oid}/link/proof.png')
    quoted = folder_for(oid) / 'slant.json'
    printing = sl.get('printingCost')
    if printing is None and quoted.exists():
        printing = json.loads(quoted.read_text())['printing']
    money = lambda v: '?' if v is None else f'{float(v):.2f}'  # noqa: E731
    subject = f'Ready for Slant: order {oid} (${money(printing)} + ${money(sl.get("deliveryCost"))})'
    lines = [f'Order {oid} ({rec["product"]}, {rec["count"]} ornament{"s" if rec["count"] != 1 else ""} in '
             f'{len(rec["designs"])} design{"s" if len(rec["designs"]) != 1 else ""}) is built, checked and drafted at Slant.', '']
    if sl.get('dryRun'):
        lines += ['SANDBOX: this was a dry run. No Slant draft exists, and the shipping cost is unknown.', '']
    else:
        lines += [f'Slant draft: {sl.get("orderId")}. Process it in Slant\'s dashboard; that is when Slant charges.', '']
    lines.append(f'Proofs (signed links, until {links["expires"]}):')
    lines += [f'  Design {x["design"]}: {x["url"]}' for x in links['links']]
    lines += ['', f'Paid {rec.get("paid")}, ${rec.get("amountTotal", 0) / 100:.2f} with tax and any discount.',
              '', 'Sent by the orders run (docs/PRODUCTION.md).']
    print(f'To: RJ\nSubject: {subject}\n\n' + '\n'.join(lines))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--live', action='store_true')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('status')
    for name in ('build', 'slant', 'email'):
        sub.add_parser(name).add_argument('id')
    f = sub.add_parser('flag')
    f.add_argument('id')
    f.add_argument('note')
    args, rest = ap.parse_known_args()
    if '--live' in rest:
        args.live = True
    w = Worker('live' if args.live else 'test')
    if args.cmd == 'flag':
        return flag(w, args.id, args.note)
    return {'status': status, 'build': build, 'slant': slant, 'email': email}[args.cmd](w, args)


if __name__ == '__main__':
    sys.exit(main())
