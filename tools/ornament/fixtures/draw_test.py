"""Draws fixtures/test-order/drawing.png: a made-up cat head, red #E01010 on white, as GPT Image is asked to.
It is a test drawing, not anyone's pet. One small pupil floats, so the builder has a bridge to make."""
from pathlib import Path
from PIL import Image, ImageDraw

R, W = (224, 16, 16), (255, 255, 255)
im = Image.new('RGB', (1024, 1024), W)
d = ImageDraw.Draw(im)
d.polygon([(180, 420), (250, 110), (430, 300)], fill=R)              # ears
d.polygon([(844, 420), (774, 110), (594, 300)], fill=R)
d.ellipse((140, 230, 884, 900), fill=R)                               # head
d.polygon([(245, 330), (270, 200), (360, 300)], fill=W)              # inner ears
d.polygon([(779, 330), (754, 200), (664, 300)], fill=W)
for x in (330, 600):                                                  # eyes, with pupils
    d.ellipse((x, 450, x + 110, 570), fill=W)
d.ellipse((352, 470, 418, 550), fill=R)                               # left pupil: floats, gets a bridge
d.rectangle((635, 450, 675, 540), fill=R)                             # right pupil: joined to the lid
d.polygon([(470, 640), (554, 640), (512, 690)], fill=W)              # nose
d.line([(512, 690), (512, 730), (460, 770)], fill=W, width=22)       # mouth
d.line([(512, 730), (564, 770)], fill=W, width=22)
for y in (650, 700):                                                  # whiskers, cut short of the outline
    d.line([(220, y - 20), (400, y)], fill=W, width=20)
    d.line([(804, y - 20), (624, y)], fill=W, width=20)
out = Path(__file__).parent / 'test-order/drawing.png'
im.save(out, optimize=True)
print(out)
