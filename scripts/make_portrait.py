"""Local one-off: turn the cat photo into an animated ASCII SVG (needs pillow, numpy)."""
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageChops

SRC, OUT = "assets/cat-wow.gif", "assets/portrait.svg"
COLS, CW, LH, FS = 70, 5, 8, 8
RAMP = " .:-=+*#%@"

im = Image.open(SRC); im.seek(0)
im = im.convert("RGB").crop((140, 470, 580, 1110))          # tight on the cat
g = ImageOps.autocontrast(im.convert("L"), cutoff=2)
g = ImageOps.invert(g).filter(ImageFilter.GaussianBlur(0.8))
# soft silhouette mask (crop coords) to drop the busy background around the cat
mask = Image.new("L", g.size, 0)
poly = [(175, 120), (190, 60), (260, 20), (345, 10), (420, 40), (470, 110), (400, 260), (410, 400), (420, 640), (10, 640), (35, 300), (60, 150)]
ImageDraw.Draw(mask).polygon([(x - 0, y) for x, y in poly], fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(10))
g = ImageChops.multiply(g, mask)
rows = round(COLS * g.height / g.width * (CW / LH) * 1.0 * (0.6 * FS / CW))
a = np.asarray(g.resize((COLS, rows), Image.LANCZOS), dtype=float) / 255
a = np.clip((a - 0.25) / 0.75, 0, 1) ** 1.3

W, H = COLS * CW + 20, rows * LH + 20
lines = []
for r in range(rows):
    s = "".join(RAMP[int(v * (len(RAMP) - 1))] for v in a[r]).rstrip()
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
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
print(W, H, rows)
