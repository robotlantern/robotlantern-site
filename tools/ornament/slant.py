#!/usr/bin/env python3
"""Slant 3D: upload an STL and quote it. Both are free. Stdlib only.

    slant.py upload part.stl                       upload, wait for Slant's analysis, print the file record
    slant.py quote part.stl --filament <id|name>   upload, then price it (or pass a Slant file id instead of an STL)
    slant.py filaments                             Slant's filament list (id, name, colour, stock)

There is no draft or process command, on purpose: Slant can't cancel or delete a draft, and processing an
order is when Slant charges. Only the Worker drafts (docs/ORDERS.md), and only RJ processes.

Environment:
  SLANT_API_KEY      sent as a Bearer token. Leave it unset in the cloud: rl-production's proxy adds it for
                     slant3dapi.com, so no Authorization header is sent then (docs/PRODUCTION.md).
  SLANT_PLATFORM_ID  the Slant platform the upload belongs to (needed by upload and quote).

Slant v2 API: https://slant3dapi.com/v2/api (spec at /v2/api/openapi.json). Adapted from printdb's client,
without its printdb cache.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = 'https://slant3dapi.com/v2/api'


class SlantError(Exception):
    pass


class Slant:
    def __init__(self, key: str | None = None, platform_id: str | None = None):
        self.key = key if key is not None else os.environ.get('SLANT_API_KEY')
        self.platform_id = platform_id or os.environ.get('SLANT_PLATFORM_ID')

    def request(self, method: str, path: str, body=None, params=None, retries: int = 2):
        url = API + path + ('?' + urllib.parse.urlencode(params, doseq=True) if params else '')
        data = json.dumps(body).encode() if body is not None else None
        hdrs = {'Accept': 'application/json'}
        if self.key:
            hdrs['Authorization'] = f'Bearer {self.key}'
        if data is not None:
            hdrs['Content-Type'] = 'application/json'
        for attempt in range(retries + 1):
            req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    payload = json.loads(r.read() or b'null')
                break
            except urllib.error.HTTPError as e:
                text = e.read().decode('utf-8', 'replace')
                if e.code == 429 and attempt < retries:   # rate limited: the block lasts a minute
                    time.sleep(65)
                    continue
                if e.code >= 500 and attempt < retries:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise SlantError(f'{method} {path}: HTTP {e.code}: {text[:500]}') from None
        if isinstance(payload, dict) and payload.get('success') is False:
            raise SlantError(f"{method} {path}: {payload.get('message') or payload.get('error')}")
        return payload.get('data') if isinstance(payload, dict) and 'data' in payload else payload

    def filaments(self) -> list[dict]:
        return self.request('GET', '/filaments')

    def filament_id(self, spec: str) -> str:
        """A Slant filament id from an id or an exact name ('PLA RED')."""
        rows = self.filaments()
        hit = [r for r in rows if spec in (r.get('publicId'), r.get('id')) or (r.get('name') or '').lower() == spec.lower()]
        if len(hit) != 1:
            raise SlantError(f'filament {spec!r} matches {len(hit)} of Slant\'s filaments')
        return hit[0].get('publicId') or hit[0]['id']

    def upload(self, path: Path) -> dict:
        """Upload an STL (presigned PUT, then confirm) and wait for Slant's analysis. Returns the file record."""
        if not self.platform_id:
            raise SlantError('no SLANT_PLATFORM_ID: an upload needs a Slant platform')
        d = self.request('POST', '/files/direct-upload', {'name': path.name, 'platformId': self.platform_id,
                                                         'ownerId': 'robot-lantern'})
        put_url, placeholder = d['presignedUrl'], d['filePlaceholder']
        signed = urllib.parse.parse_qs(urllib.parse.urlparse(put_url).query).get('X-Amz-SignedHeaders', [''])[0]
        hdrs = {'Content-Type': 'application/octet-stream'} if 'content-type' in signed else {}
        # no Authorization here: the URL carries its own signature
        req = urllib.request.Request(put_url, data=path.read_bytes(), method='PUT', headers=hdrs)
        try:
            urllib.request.urlopen(req, timeout=300).close()
        except urllib.error.HTTPError as e:
            raise SlantError(f'upload PUT: HTTP {e.code}: {e.read()[:300]!r}') from None
        rec = self.request('POST', '/files/confirm-upload', {'filePlaceholder': placeholder})
        fid = rec.get('publicFileServiceId') or placeholder['publicFileServiceId']
        for _ in range(30):   # analysis can lag the confirm
            if (rec.get('metrics') or {}).get('weight') is not None:
                break
            time.sleep(4)
            rec = self.request('GET', f'/files/{fid}')
        rec['_uploadHost'] = urllib.parse.urlparse(put_url).hostname
        return rec

    def estimate(self, file_id: str, filament_id: str | None, quantity: int = 1) -> dict:
        options = {'quantity': quantity}
        if filament_id:
            options['filamentId'] = filament_id
        return self.request('POST', f'/files/{file_id}/estimate', {'options': options})


def _file_id(rec: dict) -> str:
    return rec.get('publicFileServiceId') or rec.get('id')


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    u = sub.add_parser('upload')
    u.add_argument('stl', type=Path)
    q = sub.add_parser('quote')
    q.add_argument('stl', help='an STL to upload, or a Slant file id already uploaded')
    q.add_argument('--filament', help="Slant filament id or exact name; default is Slant's (PLA Black)")
    q.add_argument('--quantity', type=int, default=1)
    sub.add_parser('filaments')
    a = ap.parse_args(argv)
    s = Slant()
    try:
        if a.cmd == 'filaments':
            out = [{k: f.get(k) for k in ('publicId', 'name', 'color', 'hexColor', 'profile', 'available')}
                   for f in s.filaments()]
        elif a.cmd == 'upload':
            rec = s.upload(a.stl)
            out = {'fileId': _file_id(rec), 'name': a.stl.name, 'metrics': rec.get('metrics'),
                   'uploadHost': rec['_uploadHost']}
        else:
            p = Path(a.stl)
            if p.suffix.lower() == '.stl':
                rec = s.upload(p)
                fid, metrics, host = _file_id(rec), rec.get('metrics'), rec['_uploadHost']
            else:
                fid, metrics, host = a.stl, None, None
            fil = s.filament_id(a.filament) if a.filament else None
            e = s.estimate(fid, fil, a.quantity)
            out = {'fileId': fid, 'filamentId': fil, 'quantity': a.quantity, 'total': e.get('total'),
                   'pricePerUnit': e.get('pricePerUnit'), 'metrics': metrics, 'estimate': e}
            if host:
                out['uploadHost'] = host
    except SlantError as e:
        print(f'slant.py: {e}', file=sys.stderr)
        return 1
    print(json.dumps(out, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
