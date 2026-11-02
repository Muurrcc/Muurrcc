"""Local one-off: cutout cat photo -> animated ASCII SVG. Needs pillow, numpy, opencv-python-headless."""
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC, OUT = "assets/cat.webp", "assets/portrait.svg"
COLS, CW, LH, FS = 84, 5, 8, 8.4
RAMP = " .:-=+*#%@"

im = Image.open(SRC).convert("RGBA")
a = np.asarray(im)[..., 3]
if a.min() == 255:  # no transparency: treat near-white as background
    a = (np.asarray(im.convert("L")) < 245).astype(np.uint8) * 255
white = Image.new("RGBA", im.size, "white"); white.alpha_composite(im)
gray = np.asarray(white.convert("L"))
ys, xs = np.where(a > 128)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
y1 = y0 + int((y1 - y0) * 0.92)                    # drop the bottom of the chest
gray, a = gray[y0:y1, x0:x1], a[y0:y1, x0:x1]
gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4)).apply(gray)

rows = round(COLS * gray.shape[0] / gray.shape[1] * (CW / LH))
sm = lambda m: cv2.resize(m, (COLS, rows), interpolation=cv2.INTER_AREA).astype(float) / 255
g, f = sm(gray), sm(a)
ink = np.clip((1 - g - 0.22) / 0.6, 0, 1) ** 1.0   # dark = dense: eyes, nose, stripes, whiskers
v = np.where(f > 0.5, np.maximum(ink, 0.08), np.where(f > 0.12, 0.3, 0.0))  # light edge outlines the white chest

W, H = COLS * CW + 20, rows * LH + 20
lines = []
for r in range(rows):
    s = "".join(RAMP[int(x * (len(RAMP) - 1))] for x in v[r]).rstrip()
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    lines.append(f'<text class="r" x="10" y="{10 + (r + 1) * LH}" textLength="{COLS * CW}" lengthAdjust="spacing" '
                 f'style="animation-delay:{r * 0.05:.2f}s">{s}</text>')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
.r{{font:{FS}px ui-monospace,Menlo,monospace;fill:#8b949e;white-space:pre;clip-path:inset(0 100% 0 0);animation:w .9s ease-out forwards}}
@keyframes w{{to{{clip-path:inset(0 0 0 0)}}}}
@media (prefers-reduced-motion:reduce){{.r{{animation:none;clip-path:none}}}}
</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117"/>
{chr(10).join(lines)}
</svg>'''
open(OUT, "w").write(svg)

S = 2  # static PNG preview
pv = Image.new("RGB", (W * S, H * S), "#0d1117"); d = ImageDraw.Draw(pv)
font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", int(FS * S))
for r in range(rows):
    for i, ch in enumerate("".join(RAMP[int(x * (len(RAMP) - 1))] for x in v[r])):
        d.text(((10 + i * CW) * S, (10 + r * LH) * S), ch, fill="#8b949e", font=font)
pv.save("/tmp/claude-501/preview.png")
print(W, H, rows)
