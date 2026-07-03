"""XMotion - logo re-key v2 + glassmorphic card master.
Fixes: (1) enclosed O-counters -> transparent via component analysis,
       (2) white edge fringe -> alpha choke + full unmix.
Then renders the glass card per Chief's CSS spec at s=6 (240x360 -> 1440x2160).

Outputs to _Tools/_Overlays/:
  xmotion_final_logo.png        (overwritten, fixed alpha)
  xmotion_glass_card.png        (PNG-32 master, 1920x2640 canvas w/ shadow margin)
  _qa_logo_v2.jpg, _qa_card.jpg (small previews on slate, for QA eyeball)
wiz-6 | 2026-07-03
"""
import numpy as np, cv2
from PIL import Image

OV = r"C:\dev\XMotion\_Tools\_Overlays"
BG_COL = np.array([241.0, 242.0, 243.0], np.float32)

def log(*a): print(*a, flush=True)

# ================= PART 1: logo re-key v2 =================
arr = np.asarray(Image.open(OV + r"\xmotion_final_logo.png").convert("RGBA")).astype(np.float32)
rgb = arr[..., :3]
H, W = rgb.shape[:2]

# border-connected background (flood fill, as v1)
ff = rgb.astype(np.uint8).copy()
mask = np.zeros((H + 2, W + 2), np.uint8)
flags = 4 | cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE | (255 << 8)
for sx, sy in [(x, 0) for x in range(0, W, 16)] + [(x, H - 1) for x in range(0, W, 16)] + \
              [(0, y) for y in range(0, H, 16)] + [(W - 1, y) for y in range(0, H, 16)]:
    if rgb[sy, sx].mean() > 190 and not mask[sy + 1, sx + 1]:
        cv2.floodFill(ff, mask, (sx, sy), 0, (30,)*3, (30,)*3, flags)
border_bg = mask[1:-1, 1:-1] > 0

# enclosed background (letter counters): bg-colored, not border-connected,
# flat (low std), large enough to not be a metallic speckle
bg_like = (np.abs(rgb - BG_COL).max(2) < 14) & ~border_bg
n, lab, stats, _ = cv2.connectedComponentsWithStats(bg_like.astype(np.uint8), 8)
enclosed = np.zeros((H, W), bool)
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] < 200:
        continue
    sel = lab == i
    px = rgb[sel]
    if np.abs(px.mean(0) - BG_COL).max() < 8 and px.std(0).max() < 5:
        enclosed |= sel
        log("counter removed: area", int(stats[i, cv2.CC_STAT_AREA]))
full_bg = border_bg | enclosed

# alpha: choke 2px -> soften -> steepen  (kills white fringe)
alpha = (~full_bg).astype(np.float32)
alpha = cv2.erode(alpha, np.ones((5, 5), np.float32))
alpha = cv2.GaussianBlur(alpha, (0, 0), 1.4)
alpha = np.clip((alpha - 0.25) / 0.55, 0, 1)

# unmix bg color from every non-opaque pixel
a3 = alpha[..., None]
sub = alpha < 0.995
unmix = np.clip((rgb - (1 - a3) * BG_COL) / np.maximum(a3, 1e-3), 0, 255)
rgb_fixed = rgb.copy(); rgb_fixed[sub] = unmix[sub]

logo = np.dstack([rgb_fixed, alpha * 255]).astype(np.uint8)
Image.fromarray(logo, "RGBA").save(OV + r"\xmotion_final_logo.png", optimize=True)
log("logo v2 saved | opaque %.1f%% transparent %.1f%%" %
    ((alpha > .99).mean()*100, (alpha < .01).mean()*100))

# ================= PART 2: glass card =================
S = 6                                   # css px -> render px
CW, CH, R = 240*S, 360*S, 20*S          # 1440 x 2160, radius 120
PAD = 240
FW, FH = CW + 2*PAD, CH + 2*PAD         # 1920 x 2640 canvas

def rounded_mask(w, h, r, ss=4):
    m = Image.new("L", (w*ss, h*ss), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w*ss-1, h*ss-1], radius=r*ss, fill=255)
    return np.asarray(m.resize((w, h), Image.LANCZOS)).astype(np.float32) / 255.0

card = rounded_mask(CW, CH, R)
M = np.zeros((FH, FW), np.float32); M[PAD:PAD+CH, PAD:PAD+CW] = card

acc_rgb = np.zeros((FH, FW, 3), np.float32)   # premultiplied accumulate
acc_a   = np.zeros((FH, FW), np.float32)

def over(rgb_col, a_map):
    global acc_rgb, acc_a
    a = np.clip(a_map, 0, 1)[..., None]
    acc_rgb = rgb_col * a + acc_rgb * (1 - a)
    acc_a   = np.clip(a[..., 0] + acc_a * (1 - a[..., 0]), 0, 1)

WHITE = np.array([1., 1., 1.]); BLACK = np.array([0., 0., 0.])

# drop shadow: 0 8px 32px rgba(0,0,0,.1)  (css blur~2*sigma)
sh = np.roll(M, 8*S, axis=0)
sh = cv2.GaussianBlur(sh, (0, 0), 16*S)
over(BLACK, sh * 0.10)

# body fill: rgba(255,255,255,.07)
over(WHITE, M * 0.07)

# inset glow: inset 0 0 6px 3px rgba(255,255,255,.3)
inv = 1 - M
spread = cv2.dilate(inv, np.ones((2*3*S+1,)*2, np.float32))
glow_in = cv2.GaussianBlur(spread, (0, 0), 3*S) * M
over(WHITE, glow_in * 0.30)

# inset top 1px w.5 / bottom 1px w.1
top_band = np.clip(M - np.roll(M, 1*S, axis=0), 0, 1)
bot_band = np.clip(M - np.roll(M, -1*S, axis=0), 0, 1)
over(WHITE, top_band * 0.50)
over(WHITE, bot_band * 0.10)

# border: 1px solid rgba(255,255,255,.3)
ring = np.clip(M - cv2.erode(M, np.ones((S+1, S+1), np.float32)), 0, 1)
over(WHITE, ring * 0.30)

# ::before  top 1px line, horiz gradient transparent -> w.8 -> transparent
xs = np.linspace(0, 1, CW, dtype=np.float32)
hgrad = np.clip(1 - np.abs(xs - 0.5) * 2, 0, 1) ** 1.2 * 0.8
line = np.zeros((FH, FW), np.float32)
line[PAD:PAD+S, PAD:PAD+CW] = hgrad[None, :]
over(WHITE, line * M)

# ::after  left 1px line, vert gradient w.8 -> transparent -> w.3
ys = np.linspace(0, 1, CH, dtype=np.float32)
vgrad = np.where(ys < 0.5, 0.8 * (1 - ys*2), 0.3 * (ys*2 - 1)).astype(np.float32)
line2 = np.zeros((FH, FW), np.float32)
line2[PAD:PAD+CH, PAD:PAD+S] = vgrad[:, None]
over(WHITE, line2 * M)

# logo: crop to content, fit 78% card width, center
la = logo[..., 3]
ysx, xsx = np.where(la > 8)
crop = logo[ysx.min():ysx.max()+1, xsx.min():xsx.max()+1]
lw = int(CW * 0.78); lh = int(crop.shape[0] * lw / crop.shape[1])
lg = np.asarray(Image.fromarray(crop, "RGBA").resize((lw, lh), Image.LANCZOS)).astype(np.float32)/255
ly, lx = PAD + (CH - lh)//2, PAD + (CW - lw)//2
patch_a = np.zeros((FH, FW), np.float32); patch_a[ly:ly+lh, lx:lx+lw] = lg[..., 3]
patch_rgb = np.zeros((FH, FW, 3), np.float32); patch_rgb[ly:ly+lh, lx:lx+lw] = lg[..., :3]
acc_rgb = patch_rgb * patch_a[..., None] + acc_rgb * (1 - patch_a[..., None])
acc_a   = np.clip(patch_a + acc_a * (1 - patch_a), 0, 1)

# save straight-alpha PNG
out_rgb = np.where(acc_a[..., None] > 1e-4, acc_rgb / np.maximum(acc_a[..., None], 1e-4), 0)
final = np.dstack([np.clip(out_rgb, 0, 1), acc_a]) * 255
Image.fromarray(final.astype(np.uint8), "RGBA").save(OV + r"\xmotion_glass_card.png", optimize=True)
log("card saved 1920x2640")

# QA previews on slate (small jpgs I can actually view)
def qa(rgba_u8, path, wid):
    f = rgba_u8.astype(np.float32)/255
    slate = np.array([0.10, 0.11, 0.14])
    comp = f[..., :3]*f[..., 3:] + slate*(1-f[..., 3:])
    img = Image.fromarray((comp*255).astype(np.uint8))
    img.resize((wid, int(img.height*wid/img.width)), Image.LANCZOS).save(path, quality=88)
qa(logo, OV + r"\_qa_logo_v2.jpg", 900)
qa(final.astype(np.uint8), OV + r"\_qa_card.jpg", 640)
log("DONE")
