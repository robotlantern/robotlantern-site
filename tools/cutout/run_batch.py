"""Run mosaic.py over a batch of designs listed in a manifest, then lay out a contact sheet.

    PY=~/work/lab/lithophane-maker/.venv/bin/python
    $PY tools/cutout/run_batch.py .private/products/cutout-ornament/batches/2026-11-13/manifest.json [--stl] [--only <id>]

The manifest (kept in .private/: it names real pets and points at their photos) is a JSON list:

    [{"id": "spot-2020", "name": "Spot", "year": 2020, "design": "designs/08.png", "photo": "...",
      "plate_color": "gold", "year_note": "EXIF"}, ...]

Paths are relative to the manifest's folder. Each design is run with the house palette, black as the back,
three layers, a silhouette shape, 100 mm tall, and a name plate. Output goes to `out/<id>/` next to the
manifest, plus `sheet.jpg` (design above, ornament below).
"""
import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
HOUSE = 'black,white,tan,brown,gray,red,green,gold,orange,yellow'
ARGS = ['--palette', HOUSE, '--void', 'black', '--layers', '3', '--shape', 'outline', '--smooth', '1',
        '--min-area', '25', '--pitch', '3', '--pin', '1.5', '--size', '100']


def run(entry, root, stl):
    out = root / 'out' / entry['id']
    cmd = [sys.executable, str(HERE / 'mosaic.py'), str(root / entry['design']), str(out), *ARGS,
           '--name', entry['name'], '--year', str(entry['year']), '--plate-color', entry.get('plate_color', 'gold')]
    if stl:
        cmd.append('--stl')
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    try:
        rep = json.loads(r.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        return entry['id'], None, r.stderr[-400:]
    return entry['id'], rep, None


def sheet(entries, root):
    t = 300
    W = Image.new('RGB', (len(entries) * t, 2 * t + 24), 'white')
    d = ImageDraw.Draw(W)
    for i, e in enumerate(entries):
        d.text((i * t + 6, 4), f"{e['name']} {e['year']}", fill='black')
        for j, f in enumerate([root / e['design'], root / 'out' / e['id'] / 'preview.png']):
            if f.exists():
                im = Image.open(f).convert('RGB')
                im.thumbnail((t - 8, t - 8))
                W.paste(im, (i * t + 4, 24 + j * t + 4))
    W.save(root / 'sheet.jpg', quality=88)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('manifest')
    ap.add_argument('--stl', action='store_true')
    ap.add_argument('--only', nargs='*')
    ap.add_argument('--jobs', type=int, default=4)
    a = ap.parse_args()
    path = Path(a.manifest).resolve()
    root = path.parent
    entries = [e for e in json.loads(path.read_text()) if not a.only or e['id'] in a.only]
    with ThreadPoolExecutor(a.jobs) as ex:
        results = list(ex.map(lambda e: run(e, root, a.stl), entries))
    summary = {}
    for (eid, rep, err), e in zip(results, entries):
        if rep is None:
            print(f'{eid}: FAILED {err}')
            continue
        summary[eid] = {'pieces': rep['pieces'], 'colours': sorted(rep['colors']),
                        'smallest_mm2': rep['smallest_piece_mm2'], 'plate': rep.get('plate'),
                        'line_layer': rep.get('line_layer'), 'buy': [c for c, h in rep['on_shelf'].items() if not h]}
        print(f"{eid}: {rep['pieces']} pieces, {len(rep['colors'])} colours, smallest {rep['smallest_piece_mm2']} mm²")
    (root / 'summary.json').write_text(json.dumps(summary, indent=1))
    sheet(entries, root)


if __name__ == '__main__':
    main()
