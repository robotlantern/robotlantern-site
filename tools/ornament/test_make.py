#!/usr/bin/env python3
"""make.py on the test drawing: it passes, writes the four files, gives the same bytes twice, and refuses
a bad design. Then the size box, "white kept", the tag fit, `kind` and `parts`, the upload check, and the two
builder fixes from agents-01, on drawings made here. Run with the builder's Python:
python tools/ornament/test_make.py"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw
from shapely.geometry import Polygon, MultiPolygon, box

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / 'fixtures/test-order'
sys.path.insert(0, str(HERE))
from drawing import check_drawing, drop_small, unpinch   # noqa: E402
from nametag import tag_fit, tag_width, STENCILS          # noqa: E402

R, W = (224, 16, 16), (255, 255, 255)


def run(folder: Path) -> int:
    return subprocess.run([sys.executable, str(HERE / 'make.py'), str(folder)], capture_output=True).returncode


def order(tmp: Path, name: str, drawing: Image.Image | None = None, **change) -> Path:
    """A copy of the test order, with another drawing or design fields if given."""
    d = Path(tmp, name)
    shutil.copytree(FIXTURE, d)
    if drawing is not None:
        drawing.save(d / 'drawing.png')
    if change:
        des = json.loads((d / 'design.json').read_text())
        for k, v in change.items():
            if v is None: des.pop(k, None)
            else: des[k] = v
        (d / 'design.json').write_text(json.dumps(des))
    return d


def tower() -> Image.Image:
    """A tall, narrow tower with windows: 3.6 times as tall as it is wide."""
    im = Image.new('RGB', (1024, 1024), W); d = ImageDraw.Draw(im)
    d.rectangle((412, 60, 612, 780), fill=R); d.polygon([(390, 780), (634, 780), (512, 960)], fill=R)
    for y in range(110, 720, 90):
        d.rectangle((452, y, 572, y + 50), fill=W)
    return im


def outlined() -> Image.Image:
    """A disc whose features are drawn as thin white outlines, which the 1 mm gap-fill closes."""
    im = Image.new('RGB', (1024, 1024), W); d = ImageDraw.Draw(im)
    d.ellipse((112, 112, 912, 912), fill=R)
    for r in (100, 180, 260):
        d.ellipse((512 - r, 512 - r, 512 + r, 512 + r), outline=W, width=5)
    d.ellipse((472, 472, 552, 552), fill=W)
    return im


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        a, b, bad = order(tmp, 'a'), order(tmp, 'b'), order(tmp, 'bad')

        assert run(a) == 0, 'make.py failed on the test drawing'
        out = sorted(p.name for p in (a / 'out').iterdir())
        assert out == ['base.stl', 'build.json', 'proof.png', 'stencil.stl'], out
        rep = json.loads((a / 'out/build.json').read_text())
        assert rep['ok'] and all(rep['checks'].values()), rep['checks']
        bl = rep['builder']
        assert bl['bridges_mm'], 'the floating pupil should have been bridged'
        # the fixture is 80 x 84.9 mm of art, so the 80 x 85 box leaves it as it was
        assert bl['art_mm'] == [80.0, 84.9], bl['art_mm']
        assert bl['base_mm'][:2] == [83.9, 106.0], bl['base_mm']
        assert 0.9 <= bl['white_kept'] <= 1.1, bl['white_kept']
        assert bl['tag']['width_mm'] == 64.0, bl['tag']
        assert rep['design']['kind'] == 'stencil'
        assert rep['parts'] == [{'part': 'base', 'file': 'base.stl', 'colour': 'white'},
                                {'part': 'stencil', 'file': 'stencil.stl', 'colour': 'red'}], rep['parts']

        assert run(b) == 0
        for f in out:
            assert (a / 'out' / f).read_bytes() == (b / 'out' / f).read_bytes(), f'{f} differs between runs'

        d = json.loads((bad / 'design.json').read_text())
        d['options']['stencil'] = d['options']['base']
        (bad / 'design.json').write_text(json.dumps(d))
        assert run(bad) == 2, 'same base and stencil colour should be refused'
        assert run(order(tmp, 'inlay', kind='inlay')) == 2, 'an unknown kind should be refused'

        # tag text: , ! ? are allowed; text that is too long for the tag fails the build
        assert run(order(tmp, 'punct', text='Hi, Cat! Why?')) == 0, '", ! ?" should be allowed'
        long = order(tmp, 'long', text='Fairmont General')
        assert run(long) == 1
        assert not json.loads((long / 'out/build.json').read_text())['checks']['tag_fits']

        # size box: a tall drawing fits 85 mm tall, not 80 mm wide (that would be 80 x 290 mm of art)
        tall = order(tmp, 'tall', tower(), text='Tower')
        assert run(tall) == 0, 'the tall tower should pass'
        tb = json.loads((tall / 'out/build.json').read_text())['builder']
        assert tb['art_mm'][1] == 85.0 and tb['art_mm'][0] < 30, tb['art_mm']
        assert tb['base_mm'][1] <= 125 and tb['tag']['width_mm'] == 64.0, (tb['base_mm'], tb['tag'])
        # and a base over the limit fails (build.py's --max-base-h; make.py's size_ok check)
        r = subprocess.run([sys.executable, str(HERE / 'build.py'), str(tall / 'drawing.png'), str(Path(tmp, 'small')),
                            '--max-base-h', '80'], capture_output=True, text=True)
        assert any('over the 90 x 80 mm limit' in w for w in json.loads(r.stdout)['warnings']), r.stdout[-500:]

    # the upload check: the builder's cleanup and bridges, no meshes
    c = check_drawing(FIXTURE / 'drawing.png')
    assert c['ok'] and c['pieces'] == 2 and len(c['bridges_mm']) == 1 and c['max_bridge_mm'] <= 3, c
    c = check_drawing(outlined())
    assert not c['ok'] and c['white_kept'] < 0.8 and 'features' in c['problems'][0], c

    # tag fit: the page's test (docs/ORDERS.md, "Text"); figures from buildings-01 and objects-01
    assert tag_width(30) == tag_width(80) == 64.0 and tag_width(110) == 72.0
    assert not tag_fit('Fairmont General', 'allerta')['fits']
    assert [f for f in STENCILS if tag_fit('Thanksgiving 2026', f)['fits']] == ['allerta', 'saira', 'big-shoulders']
    assert tag_fit('Oh, snap! Why?', 'allerta')['fits']
    assert not tag_fit('Tab\there', 'allerta')['fits']

    # agents-01's two builder bugs, in miniature
    sliver = MultiPolygon([box(0, 0, 10, 10), box(20, 20, 20.05, 20.05)])
    assert drop_small(sliver, 2.0).geom_type == 'Polygon', 'a fleck from vectorising is not a loose piece'
    pinched = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)], [[(2, 2), (5, 5), (2, 5)], [(5, 5), (8, 5), (8, 8)]])
    fixed, pts = unpinch(pinched, 1.0)
    assert pts == [[5.0, 5.0]] and fixed.geom_type == 'Polygon', (pts, fixed.geom_type)
    assert not fixed.interiors[0].intersects(fixed.interiors[1]), 'the two cut-outs should no longer touch'
    print('ok: make.py passes on the test drawing, is repeatable and refuses a bad design; size box, white kept,'
          ' tag fit, kind and parts, the upload check and the two agents-01 fixes all hold')


if __name__ == '__main__':
    main()
