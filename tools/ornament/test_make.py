#!/usr/bin/env python3
"""make.py on the test drawing: it passes, writes the four files, gives the same bytes twice, and refuses
a bad design. Run with the builder's Python: python tools/ornament/test_make.py"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / 'fixtures/test-order'


def run(folder: Path) -> int:
    return subprocess.run([sys.executable, str(HERE / 'make.py'), str(folder)], capture_output=True).returncode


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        a, b, bad = Path(tmp, 'a'), Path(tmp, 'b'), Path(tmp, 'bad')
        for d in (a, b, bad):
            shutil.copytree(FIXTURE, d)

        assert run(a) == 0, 'make.py failed on the test drawing'
        out = sorted(p.name for p in (a / 'out').iterdir())
        assert out == ['base.stl', 'build.json', 'proof.png', 'stencil.stl'], out
        rep = json.loads((a / 'out/build.json').read_text())
        assert rep['ok'] and all(rep['checks'].values()), rep['checks']
        assert rep['builder']['bridges_mm'], 'the floating pupil should have been bridged'

        assert run(b) == 0
        for f in out:
            assert (a / 'out' / f).read_bytes() == (b / 'out' / f).read_bytes(), f'{f} differs between runs'

        d = json.loads((bad / 'design.json').read_text())
        d['options']['stencil'] = d['options']['base']
        (bad / 'design.json').write_text(json.dumps(d))
        assert run(bad) == 2, 'same base and stencil colour should be refused'
    print('ok: make.py passes on the test drawing, is repeatable, and refuses a bad design')


if __name__ == '__main__':
    main()
