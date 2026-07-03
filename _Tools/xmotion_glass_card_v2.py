"""XMotion glass card v2 - uniform logo margin.
Card width fixed at 240*S; height DERIVED: logo_h + 2 * side_margin,
so the logo-to-edge distance is identical on x and y.
Reads mastered xmotion_final_logo.png (v2). Outputs xmotion_glass_card.png (overwrite).
wiz-6 | 2026-07-03
"""
import numpy as np, cv2
from PIL import Image, ImageDraw

OV = r"C:\dev\XMotion\_Tools\_Overlays"
S = 6
CW, R = 240*S, 20*S
LOGO_FRAC = 0.78
PAD = 240

def log(*a): print(*a, flush=True)

# logo crop + placement math first (drives card height)
logo = np.asarray(Image.open(OV + r"\xmotion_final_logo.png").convert("RGBA"))
la = logo[..., 3]
ys, xs = np.where(la > 8)
crop = logo[ys.min():ys.max()+1, xs.min():xs.max()+1]
lw = int(CW * LOGO_FRAC)
lh = int(round(crop.shape[0] * lw / crop.shape[1]))
margin = (CW - lw) // 2
CH = lh + 2 * margin
log(f"logo {lw}x{lh} | margin {margin} | card {CW}x{CH}")

FW, FH = CW + 2*PAD, CH + 2*PAD

m = Image.new("L", (CW*4, CH*4), 0)
ImageDraw.Draw(m).rounded_rectangle([0, 0, CW*4-1, CH*4-1], radius=R*4, fill=255)
card = np.asarray(m.resize((CW, CH), Image.LANCZOS)).astype(np.float32) / 255.0
M = np.zeros((FH, FW), np.float32); M[PAD:PAD+CH, PAD:PAD+CW] = card

acc_rgb = np.zeros((FH, FW, 3), np.float32); acc_a = np.zeros((FH, FW), np.float32)
def over(col, amap):
    global acc_rgb, acc_a
    a = np.clip(amap, 0, 1)[..., None]
    acc_rgb = col * a + acc_rgb * (1 - a)
    acc_a = np.clip(a[..., 0] + acc_a * (1 - a[..., 0]), 0, 1)
WHITE = np.array([1., 1., 1.]); BLACK = np.array([0., 0., 0.])

sh = np.roll(M, 8*S, axis=0); sh = cv2.GaussianBlur(sh, (0, 0), 16*S)
over(BLACK, sh * 0.10)                                   # drop shadow
over(WHITE, M * 0.07)                                    # body
inv = 1 - M
spread = cv2.dilate(inv, np.ones((2*3*S+1,)*2, np.float32))
over(WHITE, cv2.GaussianBlur(spread, (0, 0), 3*S) * M * 0.30)   # inset glow
over(WHITE, np.clip(M - np.roll(M,  1*S, axis=0), 0, 1) * 0.50) # inset top
over(WHITE, np.clip(M - np.roll(M, -1*S, axis=0), 0, 1) * 0.10) # inset bottom
over(WHITE, np.clip(M - cv2.erode(M, np.ones((S+1,)*2, np.float32)), 0, 1) * 0.30)  # border

xsg = np.linspace(0, 1, CW, dtype=np.float32)
hgrad = np.clip(1 - np.abs(xsg - 0.5) * 2, 0, 1) ** 1.2 * 0.8
line = np.zeros((FH, FW), np.float32); line[PAD:PAD+S, PAD:PAD+CW] = hgrad[None, :]
over(WHITE, line * M)                                    # ::before
ysg = np.linspace(0, 1, CH, dtype=np.float32)
vgrad = np.where(ysg < 0.5, 0.8 * (1 - ysg*2), 0.3 * (ysg*2 - 1)).astype(np.float32)
line2 = np.zeros((FH, FW), np.float32); line2[PAD:PAD+CH, PAD:PAD+S] = vgrad[:, None]
over(WHITE, line2 * M)                                   # ::after

lg = np.asarray(Image.fromarray(crop, "RGBA").resize((lw, lh), Image.LANCZOS)).astype(np.float32)/255
ly, lx = PAD + margin, PAD + margin
pa = np.zeros((FH, FW), np.float32); pa[ly:ly+lh, lx:lx+lw] = lg[..., 3]
pr = np.zeros((FH, FW, 3), np.float32); pr[ly:ly+lh, lx:lx+lw] = lg[..., :3]
acc_rgb = pr * pa[..., None] + acc_rgb * (1 - pa[..., None])
acc_a = np.clip(pa + acc_a * (1 - pa), 0, 1)

out = np.where(acc_a[..., None] > 1e-4, acc_rgb / np.maximum(acc_a[..., None], 1e-4), 0)
final = (np.dstack([np.clip(out, 0, 1), acc_a]) * 255).astype(np.uint8)
Image.fromarray(final, "RGBA").save(OV + r"\xmotion_glass_card.png", optimize=True)
log(f"card saved {FW}x{FH}")

f = final.astype(np.float32)/255
slate = np.array([0.10, 0.11, 0.14])
comp = f[..., :3]*f[..., 3:] + slate*(1-f[..., 3:])
img = Image.fromarray((comp*255).astype(np.uint8))
img.resize((820, int(img.height*820/img.width)), Image.LANCZOS).save(OV + r"\_qa_card.jpg", quality=88)
log("DONE")
