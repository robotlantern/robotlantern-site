"""Switch the shop Worker's drawings or orders off and on (docs/PRODUCTION.md, "Caps and switches").

    python3 tools/orders/switch.py status [--live]
    python3 tools/orders/switch.py drawings off [--live]     # stops new OpenAI drawings at once
    python3 tools/orders/switch.py orders off [--live]       # stops new orders and checkouts
    python3 tools/orders/switch.py drawings on [--live]

It writes `switch:<what>` = `off` in the Worker's KV namespace through Cloudflare's API (or deletes it, for
on), with the agents' Cloudflare token from the secrets folder, so it runs on Sarcean. Without --live it's
the sandbox's namespace. Workers may read the old value for up to a minute after a change.

Agents switch drawings off on their own only if spending looks wrong, and tell RJ straight away. Switching
anything back on is RJ's call. Neither costs anything.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

SECRETS = Path(os.environ.get('RL_SECRETS', Path.home() / '.codex/secrets/robot-lantern'))
NAMESPACES = {'test': 'shop-orders-test', 'live': 'shop-orders-live'}
WHAT = ('drawings', 'orders')


def env_file(name):
    out = {}
    for line in (SECRETS / name).read_text().splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            out[k.strip()] = v.strip()
    return out


class KV:
    def __init__(self, mode):
        cf = env_file('cloudflare.env')
        self.auth = {'Authorization': f'Bearer {cf["CF_API_TOKEN"]}', 'User-Agent': 'robot-lantern-switch'}
        self.base = f'https://api.cloudflare.com/client/v4/accounts/{cf["CF_ACCT_ID"]}/storage/kv/namespaces'
        found = self.call('GET', '?per_page=100')[1]['result']
        hit = [n['id'] for n in found if n['title'] == NAMESPACES[mode]]
        if not hit:
            raise SystemExit(f'no KV namespace {NAMESPACES[mode]}')
        self.ns = hit[0]

    def call(self, method, path, body=None):
        req = urllib.request.Request(self.base + path, data=body, method=method, headers=self.auth)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
                return r.status, (json.loads(raw) if r.headers.get_content_type() == 'application/json' else raw)
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def get(self, key):
        status, raw = self.call('GET', f'/{self.ns}/values/{key}')
        return raw.decode() if status == 200 else None

    def set(self, key, value):
        status, raw = (self.call('PUT', f'/{self.ns}/values/{key}', value.encode()) if value is not None
                       else self.call('DELETE', f'/{self.ns}/values/{key}'))
        if status not in (200, 404):
            raise SystemExit(f'Cloudflare said {status}: {raw[:200]!r}')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('what', choices=WHAT + ('status',))
    ap.add_argument('state', nargs='?', choices=('on', 'off'))
    ap.add_argument('--live', action='store_true')
    a = ap.parse_args()
    mode = 'live' if a.live else 'test'
    kv = KV(mode)
    if a.what == 'status':
        for w in WHAT:
            print(f'{mode} {w}: {"off" if kv.get(f"switch:{w}") == "off" else "on"}')
        return
    if not a.state:
        ap.error('say on or off')
    kv.set(f'switch:{a.what}', 'off' if a.state == 'off' else None)
    print(f'{mode} {a.what}: {a.state} (the Worker sees it within a minute)')


if __name__ == '__main__':
    sys.exit(main())
