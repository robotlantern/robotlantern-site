"""Print time and grams for mosaic.py's STLs, with the OrcaSlicer CLI on Meltbot's presets (estimate only).

    python3 tools/cutout/slice.py OUT_DIR        # slices every *.stl in OUT_DIR, prints a table

Flattens OrcaSlicer's installed system presets for a Creality K1 SE, 0.4 nozzle, 0.20 mm Standard and
Creality Generic PLA Matte. Adapted from 3d-modeling's tessa-pencil-cup/slice_orca.py. Nothing is uploaded.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ORCA = '/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer'
SYSTEM = Path.home() / 'Library/Application Support/OrcaSlicer/system'
PRESETS = {'machine': 'Creality K1 SE 0.4 nozzle',
           'process': '0.20mm Standard @Creality K1 SE 0.4',
           'filament': 'Creality Generic PLA Matte @K1-all'}


def resolve(kind, name):
    hits = [p for p in SYSTEM.rglob(f'{name}.json') if kind in p.parts]
    if not hits:
        raise FileNotFoundError(f'{kind}: {name}')
    data = json.loads(hits[0].read_text())
    merged = resolve(kind, data['inherits']) if data.get('inherits') else {}
    merged.update(data)
    merged.pop('inherits', None)
    return merged


def main():
    d = Path(sys.argv[1])
    cfg = d / 'orca'
    cfg.mkdir(exist_ok=True)
    files = {}
    for kind, name in PRESETS.items():
        data = resolve(kind, name)
        if kind == 'process':
            data['enable_support'] = '0'
        (cfg / f'{kind}.json').write_text(json.dumps(data, indent=1))
        files[kind] = cfg / f'{kind}.json'
    rows = []
    for stl in sorted(d.glob('*.stl')):
        out = cfg / stl.stem
        out.mkdir(exist_ok=True)
        r = subprocess.run(['gtimeout', '300', ORCA, '--slice', '0', '--arrange', '1', '--orient', '0',
                            '--load-settings', f"{files['machine']};{files['process']}",
                            '--load-filaments', str(files['filament']), '--outputdir', str(out), str(stl)],
                           capture_output=True, text=True)
        g = next(iter(sorted(out.glob('*.gcode'))), None)
        if not g:
            rows.append((stl.stem, 'failed', r.returncode, ''))
            continue
        t = g.read_text(errors='ignore')
        pick = lambda k: (re.search(rf'^; {re.escape(k)} = (.+)$', t, re.M) or [None, '?'])[1]
        rows.append((stl.stem, pick('estimated printing time (normal mode)'), pick('total filament used [g]'), ''))
    for row in rows:
        print('\t'.join(str(v) for v in row))


if __name__ == '__main__':
    main()
