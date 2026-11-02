"""Local one-off: cat photo -> animated ASCII SVG. Needs pillow, numpy, opencv-python-headless."""
import cv2, numpy as np
from PIL import Image

SRC, OUT = "assets/cat-wow.gif", "assets/portrait.svg"
COLS, CW, LH, FS = 80, 5, 8, 8.4
RAMP = " .:-=+*#%@"

im = Image.open(SRC); im.seek(0)
img = cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2BGR)
X0, Y0, X1, Y1 = 100, 440, 620, 1280
c = img[Y0:Y1, X0:X1].copy()

# cut the cat out of the background
m = np.zeros(c.shape[:2], np.uint8)
cv2.grabCut(c, m, (60, 40, 400, 790), np.zeros((1, 65)), np.zeros((1, 65)), 8, cv2.GC_INIT_WITH_RECT)
fg = ((m == 1) | (m == 3)).astype(np.uint8) * 255
fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(fg)
fg = ((lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])) * 255).astype(np.uint8)  # keep the cat only
fg = cv2.erode(fg, np.ones((9, 9), np.uint8))

# head + chest only, tight crop
cx0, cy0, cx1, cy1 = 60, 50, 450, 500
gray = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY)
gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4)).apply(gray)
gray = gray[cy0:cy1, cx0:cx1]; fg = fg[cy0:cy1, cx0:cx1]

rows = round(COLS * gray.shape[0] / gray.shape[1] * (CW / LH))
sm = lambda a: cv2.resize(a, (COLS, rows), interpolation=cv2.INTER_AREA).astype(float) / 255
g, f = sm(gray), sm(fg)
# dark = dense (like ink on paper): eyes, nose, mouth and stripes read clearly
ink = np.clip((1 - g - 0.28) / 0.55, 0, 1) ** 1.1
contour = sm(cv2.dilate(cv2.Canny(fg, 50, 150), np.ones((7, 7), np.uint8)))
v = np.where(f > 0.5, np.maximum(ink, 0.1), 0.0)

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

# static PNG preview for checking the result without a browser
from PIL import ImageDraw, ImageFont
S = 3
pv = Image.new("RGB", (W * S, H * S), "#0d1117"); d = ImageDraw.Draw(pv)
font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", int(FS * S))
for r in range(rows):
    s = "".join(RAMP[int(x * (len(RAMP) - 1))] for x in v[r])
    for i, ch in enumerate(s):
        d.text(((10 + i * CW) * S, (10 + r * LH) * S), ch, fill="#8b949e", font=font)
pv.save("/tmp/claude-501/preview.png")
print(W, H, rows)
