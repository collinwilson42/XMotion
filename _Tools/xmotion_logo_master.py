"""XMotion Step 1 — logo master: EDSR x4 super-res + flood-fill alpha key.
Output: _Tools/_Overlays/xmotion_final_logo.png (PNG-32, transparent bg, 3268px)
wiz-6 | 2026-07-03
"""
import numpy as np, cv2
from cv2 import dnn_superres
from PIL import Image

RAW = r"C:\dev\XMotion\_Tools\_Overlays\xmotion_raw_logo.png"
OUT = r"C:\dev\XMotion\_Tools\_Overlays\xmotion_final_logo.png"
MODEL = r"C:\dev\XMotion\_Tools\_models\EDSR_x4.pb"

# ---- 1. Super-resolution (RGB detail pass) ----
bgr = cv2.imread(RAW, cv2.IMREAD_COLOR)
sr = dnn_superres.DnnSuperResImpl_create()
sr.readModel(MODEL); sr.setModel("edsr", 4)
up = sr.upsample(bgr)                       # 817 -> 3268
H, W = up.shape[:2]
print("SR done:", W, "x", H)

# ---- 2. Background mask via border flood fill (protects enclosed highlights) ----
rgb = cv2.cvtColor(up, cv2.COLOR_BGR2RGB)
ff = rgb.copy()
mask = np.zeros((H + 2, W + 2), np.uint8)
flags = 4 | cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE | (255 << 8)
tol = (30, 30, 30)
step = 16                                    # seed densely along all four borders
seeds = [(x, 0) for x in range(0, W, step)] + [(x, H - 1) for x in range(0, W, step)] \
      + [(0, y) for y in range(0, H, step)] + [(W - 1, y) for y in range(0, H, step)]
for sx, sy in seeds:
    px = rgb[sy, sx]
    if px.mean() > 190 and not mask[sy + 1, sx + 1]:   # only seed on background-bright pixels
        cv2.floodFill(ff, mask, (sx, sy), 0, tol, tol, flags)
bg = mask[1:-1, 1:-1] > 0
print("bg coverage: %.1f%%" % (bg.mean() * 100))

# ---- 3. Alpha: soft AA edge + defringe (unmix bg color from edge pixels) ----
alpha = (~bg).astype(np.float32)
alpha = cv2.GaussianBlur(alpha, (0, 0), 1.2)           # ~1px AA at 3268px
alpha = np.clip((alpha - 0.15) / 0.7, 0, 1)            # re-steepen, keep soft edge

bg_col = np.array([241.0, 242.0, 243.0])               # measured border mean
f = rgb.astype(np.float32)
a3 = alpha[..., None]
edge = (alpha > 0.01) & (alpha < 0.99)
unmix = np.clip((f - (1 - a3) * bg_col) / np.maximum(a3, 1e-3), 0, 255)
f[edge] = unmix[edge]

out = np.dstack([f, alpha * 255]).astype(np.uint8)
Image.fromarray(out, "RGBA").save(OUT, optimize=True)
print("saved:", OUT)

# ---- 4. QA report ----
op = (alpha > 0.99).mean(); tr = (alpha < 0.01).mean()
print("opaque %.1f%% | transparent %.1f%% | edge %.1f%%" % (op*100, tr*100, (1-op-tr)*100))
