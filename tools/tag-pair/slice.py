"""Slice the tag-pair test plate for Meltbot and keep the G-code (OrcaSlicer CLI).

    python3 tools/tag-pair/slice.py STL_DIR OUT_DIR [--nozzle 205] [--bed 60]

Uses 3d-modeling's tools/estimate.py presets: K1 SE 0.4, 0.20 mm Standard, Generic PLA, Textured PEI,
supports off, parts arranged on one plate. Reports time, grams and bridge moves; writes expected-settings.json
for 3d-modeling's validate_gcode.py.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

EST = Path.home() / 'work/3d-modeling/tools'
sys.path.insert(0, str(EST))
import estimate  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('stl_dir', type=Path)
ap.add_argument('out', type=Path)
ap.add_argument('--nozzle', type=int, default=205)
ap.add_argument('--bed', type=int, default=60)
a = ap.parse_args()
a.out.mkdir(parents=True, exist_ok=True)
cfg = estimate.presets('meltbot-0.4', 'PLA', {}, 'off')
fil = cfg['filament']
for k in ('nozzle_temperature', 'nozzle_temperature_initial_layer'):
    fil[k] = [str(a.nozzle)]
for k in ('textured_plate_temp', 'textured_plate_temp_initial_layer'):
    fil[k] = [str(a.bed)]
files = {}
for kind, data in cfg.items():
    files[kind] = a.out / f'{kind}.json'
    files[kind].write_text(json.dumps(data))
stls = sorted(str(p) for p in a.stl_dir.glob('*.stl'))
cmd = [estimate.ORCA, '--slice', '0', '--arrange', '1', '--orient', '0',
       '--load-settings', f"{files['machine']};{files['process']}", '--load-filaments', str(files['filament']),
       '--outputdir', str(a.out)] + stls
r = subprocess.run(['gtimeout', '300'] + cmd, capture_output=True, text=True)
g = sorted(a.out.glob('*.gcode'))
if not g:
    print(r.stdout[-2000:], r.stderr[-2000:])
    sys.exit('no G-code')
text = g[0].read_text(errors='ignore')
pick = lambda k: (re.search(rf'^; {re.escape(k)} = (.+)$', text, re.M) or [None, None])[1]
types = {}
for t in re.findall(r'^;TYPE:(.+)$', text, re.M):
    types[t] = types.get(t, 0) + 1
print('gcode', g[0])
print('time', pick('estimated printing time (normal mode)'), 'grams', pick('total filament used [g]') or pick('filament used [g]'))
print('types', {k: v for k, v in types.items() if re.search('ridge|upport|verhang', k)})
(a.out / 'expected-settings.json').write_text(json.dumps({
    'printer': 'Creality K1 SE 0.4 nozzle', 'bed_type': 'Textured PEI Plate', 'bed_c': a.bed,
    'nozzle_c': a.nozzle, 'filament_type': 'PLA'}, indent=2))
