"""Body figure for the scan and heart cues: python3 analysis/body_outline.py path/to/figure.png   (needs numpy, scipy, Pillow)

The source is a 1024 x 1024 picture of a human outline in white on slate, with soft glow spots and a horizontal scan
light painted in at chest height. This keeps only the thin outline (what stands out above a local median), removes the
painted scan light and glow spots, and writes body_outline.png (white, alpha = line) and body_figure.json (size, the glow
points by name, and where the heart glow sits). The page draws the scan light and glow points itself.
"""
import sys, os, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, out = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else '.')
lum = np.asarray(Image.open(src).convert('RGB')).astype(float).mean(2)
line = np.clip((lum - ndi.median_filter(lum, size=11)) / 150.0, 0, 1)
# across the old scan line, the glow is smooth sideways, so a sideways-only median keeps the body's side outlines whole
r0, r1 = 286, 334
side = np.clip((lum[r0:r1] - ndi.median_filter(lum[r0:r1], size=(1, 25))) / 150.0, 0, 1)
keep = np.zeros(1024, bool)
for r in (line[r0 - 4], line[r1 + 4]):
    for x in np.nonzero(r > 0.3)[0]: keep[max(0, x - 9):x + 10] = True
band = np.zeros_like(side); band[:, keep] = side[:, keep]
band[(band < 0.25)] = 0                                          # the scan line's thin core is weaker than the outline
line[r0:r1] = band
line[line < 0.06] = 0
# where the old glow was brightest the side outlines still dip; restore each from the clean row just above, at its own position
for lo, hi in ((380, 420), (605, 650)):
    ref = line[296, lo:hi]; c = int(ref.argmax())
    for y in range(298, 320):
        row = line[y, lo:hi]; m = int(row.argmax())
        for dx in range(-5, 6):
            if 0 <= c + dx < len(ref) and 0 <= m + dx < len(row): row[m + dx] = max(row[m + dx], ref[c + dx])
pts = [('head', 511, 112), ('throat', 511, 250), ('chest', 511, 309), ('left elbow', 407, 401), ('right elbow', 616, 401),
       ('belly', 512, 443), ('left hand', 372, 541), ('right hand', 652, 541), ('left knee', 464, 719), ('right knee', 560, 719),
       ('left foot', 456, 930), ('right foot', 567, 930)]
yy, xx = np.mgrid[0:1024, 0:1024]
for _, x, y in pts:                                              # clear what is left of the old glow spots
    d = np.hypot(xx - x, yy - y); sp = d < 11
    if not (line[sp] > 0.5).sum() > 25: line[sp] = 0             # unless the outline itself runs through
lab, n = ndi.label(line > 0.05)
sizes = ndi.sum(np.ones_like(line), lab, range(1, n + 1))
for i, s in enumerate(sizes, 1):
    if s < 60: line[lab == i] = 0
x0, y0, x1, y1 = 325, 63, 699, 961
crop = line[y0:y1, x0:x1]
rgba = np.zeros(crop.shape + (4,), np.uint8); rgba[..., :3] = 255; rgba[..., 3] = (crop * 255).astype(np.uint8)
Image.fromarray(rgba).save(os.path.join(out, 'body_outline.png'), optimize=True)
# heart glow: at chest level, a little to the figure's own left (the viewer's right)
json.dump(dict(size=[x1 - x0, y1 - y0], points=[[n_, x - x0, y - y0] for n_, x, y in pts], heart=[200, 252]),
          open(os.path.join(out, 'body_figure.json'), 'w'))
print(os.path.getsize(os.path.join(out, 'body_outline.png')), 'bytes')
