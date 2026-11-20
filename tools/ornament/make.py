#!/usr/bin/env python3
"""The stencil ornament's recipe: one order folder in, the files Slant prints out (docs/ORDERS.md, "The recipe").

    python3 tools/ornament/make.py <order folder>

Reads `design.json` and `drawing.png` from the folder and writes `out/`:
  base.stl, stencil.stl   posed for printing (base face up; stencil face down, pegs up)
  proof.png               the builder's preview in the order's colours, with the tag
  build.json              the design, the builder's report and the checks

Exits 1 if a check fails (the files are still written, so the proof can be looked at), 2 if the design
itself is invalid. The same folder always gives the same files. Run it with the Python that has
requirements.txt installed (/opt/rl/bin/python in the cloud).
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SHOP = ROOT / 'products/cutout-ornament/shop.json'
FONTS = ('allerta', 'saira', 'big-shoulders', 'emblema', 'wallpoet')   # nametag.STENCILS
TEXT = {'max': 16, 'allowed': "A-Za-z0-9 '&.,!?-"}                        # shop.json "text", until it exists
MAX_BRIDGE = 3.0


class Invalid(Exception):
    pass


def colour(key: str, shop: dict, option: str) -> dict:
    """{'hex', 'slant'} for a colour choice: the product file's choice first, then colours.json."""
    table = json.loads((HERE / 'colours.json').read_text())['colours']
    opt = next((o for o in shop.get('options', []) if o.get('id') == option), None)
    if opt is not None:
        ids = [c['id'] for c in opt['choices'] if isinstance(c, dict)]
        if ids and key not in ids:
            raise Invalid(f'{option} colour {key!r} is not offered')
        choice = next((c for c in opt['choices'] if isinstance(c, dict) and c['id'] == key), {})
    else:
        choice = {}
    base = table.get(key)
    if base is None and 'hex' not in choice:
        raise Invalid(f'unknown {option} colour {key!r}')
    if base is not None and not base['offered'] and not choice:
        raise Invalid(f'{option} colour {key!r} is not offered')
    return {'hex': choice.get('hex') or base['hex'], 'slant': choice.get('slant') or (base or {}).get('slant')}


def read_design(folder: Path) -> tuple[dict, list[str]]:
    d = json.loads((folder / 'design.json').read_text())
    if d.get('product') != 'cutout-ornament':
        raise Invalid(f"product {d.get('product')!r} is not cutout-ornament")
    shop = json.loads(SHOP.read_text()) if SHOP.exists() else {}
    o = d.get('options') or {}
    for k in ('base', 'stencil', 'tag'):
        if k not in o:
            raise Invalid(f'options.{k} is missing')
    if o['base'] == o['stencil']:
        raise Invalid('base and stencil are the same colour')
    base, sten = colour(o['base'], shop, 'base'), colour(o['stencil'], shop, 'stencil')
    args = ['--base-col', base['hex'], '--stencil-col', sten['hex']]
    if o['tag'] == 'yes':
        rule = shop.get('text', TEXT)
        text = d.get('text') or ''
        if not text.strip():
            raise Invalid('the tag needs text')
        if len(text) > rule['max'] or not re.fullmatch(f"[{rule['allowed']}]+", text):
            raise Invalid(f"tag text {text!r} breaks the rule ({rule['max']} of {rule['allowed']})")
        font = o.get('font', 'allerta')
        if font not in FONTS:
            raise Invalid(f'unknown font {font!r}')
        args += ['--name', text, '--font', font]
    elif o['tag'] != 'no':
        raise Invalid(f"options.tag is {o['tag']!r}, not yes or no")
    d['_colours'] = {'base': base, 'stencil': sten}
    return d, args


def checks(rep: dict, tag: bool) -> dict:
    c = {
        'stencil_one_piece': rep['stencil_bodies'] == 1,
        'watertight': bool(rep['base_watertight'] and rep['stencil_watertight']),
        'bridges_ok': all(b <= MAX_BRIDGE for b in rep['bridges_mm']),
        'size_ok': rep['base_mm'][0] <= rep['max_base_w'] and rep['base_mm'][1] <= rep['max_base_h'],
        'white_kept': rep['white_kept'] is None or rep['white_kept'] >= rep['min_white_kept'],
        'no_warnings': not rep['warnings'],
    }
    if tag:
        t = rep.get('tag') or {}
        c['tag_fits'] = t.get('pieces') == 1 and not any('too long' in w or 'no glyph' in w for w in rep['warnings'])
    return c


def make(folder: Path) -> int:
    folder = folder.resolve()
    for f in ('design.json', 'drawing.png'):
        if not (folder / f).is_file():
            print(f'make.py: {folder / f} is missing', file=sys.stderr)
            return 2
    try:
        design, args = read_design(folder)
    except (Invalid, json.JSONDecodeError) as e:
        print(f'make.py: invalid design: {e}', file=sys.stderr)
        return 2
    out = folder / 'out'
    with tempfile.TemporaryDirectory(dir=folder, prefix='.build-') as tmp:
        # relative paths, so build.json is the same wherever the folder is
        r = subprocess.run([sys.executable, str(HERE / 'build.py'), 'drawing.png', Path(tmp).name, *args],
                           cwd=folder, capture_output=True, text=True)
        if r.returncode:
            print(r.stderr[-2000:], file=sys.stderr)
            print('make.py: the builder failed', file=sys.stderr)
            return 1
        rep = json.loads((Path(tmp) / 'build.json').read_text())
        if out.exists():
            shutil.rmtree(out)
        out.mkdir()
        for src, dst in (('base.stl', 'base.stl'), ('stencil.stl', 'stencil.stl'), ('preview.png', 'proof.png')):
            shutil.move(Path(tmp) / src, out / dst)
    for k in ('art', 'out'):
        rep.pop(k, None)
    c = checks(rep, design['options']['tag'] == 'yes')
    ok = all(c.values())
    kept = {k: design.get(k) for k in ('product', 'drawing', 'options')}
    if design['options']['tag'] == 'yes':
        kept['text'] = design['text']
    report = {'ok': ok, 'checks': c, 'design': kept, 'colours': design['_colours'], 'builder': rep}
    (out / 'build.json').write_text(json.dumps(report, indent=1) + '\n')
    print(json.dumps({'ok': ok, 'checks': c, 'warnings': rep['warnings']}, indent=1))
    return 0 if ok else 1


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(make(Path(sys.argv[1])))
