"""Local one-off: cutout cat photo -> animated ASCII SVG. Needs pillow, numpy, opencv-python-headless."""
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC, OUT = "assets/cat.webp", "assets/portrait.svg"
COLS, CW, LH, FS = 76, 6, 9, 9.6
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
gray = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8)).apply(gray)

rows = round(COLS * gray.shape[0] / gray.shape[1] * (CW / LH))
sm = lambda m: cv2.resize(m, (COLS, rows), interpolation=cv2.INTER_AREA).astype(float) / 255
g, f = sm(gray), sm(a)
# bright = dense, like the photo seen on a dark page; pure white fur stays readable via a floor
lo, hi = np.percentile(g[f > 0.5], [3, 97])
lum = np.clip((g - lo) / (hi - lo), 0, 1) ** 0.85
e = sm(cv2.Canny(cv2.resize(gray, (COLS * 4, rows * 4)).astype(np.uint8), 60, 160) if False else cv2.resize(cv2.Canny(gray, 60, 160), (COLS, rows), interpolation=cv2.INTER_AREA))
lum = np.clip((lum - 0.45) * 1.7 + 0.5 - e * 0.8, 0, 1)  # edges (eyes, nose, mouth, ear rims) cut dark lines into the fur
v = np.where(f > 0.5, np.maximum(lum, 0.12), np.where(f > 0.12, 0.2, 0.0))

W, H = COLS * CW + 20, rows * LH + 20
lines = []
for r in range(rows):
    chars = [(i, RAMP[int(x * (len(RAMP) - 1))]) for i, x in enumerate(v[r])]
    chars = [(i, ch) for i, ch in chars if ch != " "]
    if not chars:
        continue
    # one explicit x per glyph: layout can't drift whatever monospace font the viewer falls back to
    xs = " ".join(f"{10 + i * CW}" for i, _ in chars)
    t = "".join(ch for _, ch in chars).replace("&", "&amp;").replace("<", "&lt;")
    lines.append(f'<text class="r" x="{xs}" y="{10 + (r + 1) * LH}" style="animation-delay:{r * 0.05:.2f}s">{t}</text>')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
.r{{font:{FS}px ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace;fill:#8b949e;clip-path:inset(0 100% 0 0);animation:w .9s ease-out forwards}}
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
