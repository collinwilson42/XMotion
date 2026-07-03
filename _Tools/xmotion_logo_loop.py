"""XMotion Step 2 - seamless 10s animated logo loop.
Metallic specular sweep + soft exterior glow pulse (diamond/slate, white/blue).
All motion is integer-periodic in t -> frame 1 == frame N exactly.

Outputs to _Tools/_Overlays/:
  xmotion_logo_loop_10s.mov   ProRes 4444, straight alpha (compositing master)
  xmotion_logo_loop_10s.webm  VP9 yuva420p (web lane)
  xmotion_logo_loop_preview.mp4  on dark slate, for eyeball QA

wiz-6 | 2026-07-03
"""
import numpy as np, subprocess, sys
from PIL import Image
import imageio_ffmpeg

SRC   = r"C:\dev\XMotion\_Tools\_Overlays\xmotion_final_logo.png"
OUTD  = r"C:\dev\XMotion\_Tools\_Overlays"
SIZE  = 2048          # render size (master logo is 3268; downsample once)
FPS   = 30
DUR   = 10
N     = FPS * DUR     # 300 frames
SWEEPS_PER_LOOP = 2   # one shine event every 5 s
GLOW_CYCLES     = 2   # glow pulse locked to sweep rhythm

# ---- load + prep ----
im = Image.open(SRC).convert("RGBA").resize((SIZE, SIZE), Image.LANCZOS)
arr = np.asarray(im).astype(np.float32) / 255.0
rgb, a = arr[..., :3], arr[..., 3]

# margin so the exterior glow never clips at frame edge
PAD = SIZE // 8
F = SIZE + 2 * PAD
logo_rgb = np.zeros((F, F, 3), np.float32); logo_a = np.zeros((F, F), np.float32)
logo_rgb[PAD:PAD+SIZE, PAD:PAD+SIZE] = rgb; logo_a[PAD:PAD+SIZE, PAD:PAD+SIZE] = a

# ---- static glow shape (pulse is a scalar per frame) ----
def gauss_blur(x, sigma):
    # separable gaussian via repeated box approximation (pure numpy, fast enough once)
    from math import ceil
    r = max(1, int(sigma))
    k = np.ones(2*r+1, np.float32) / (2*r+1)
    for _ in range(3):
        x = np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 0, x)
        x = np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 1, x)
    return x

glow_shape = gauss_blur(logo_a.copy(), F * 0.012)
glow_shape = np.clip(glow_shape * 1.6, 0, 1) * (1 - logo_a)   # exterior only
GLOW_COL = np.array([0.72, 0.82, 1.00], np.float32)           # cool diamond blue-white

# ---- specular band geometry (diagonal, top-left -> bottom-right) ----
yy, xx = np.mgrid[0:F, 0:F].astype(np.float32)
ang = np.deg2rad(115.0)
proj = (xx * np.cos(ang) + yy * np.sin(ang))
proj = (proj - proj.min()) / (proj.max() - proj.min())        # 0..1 along sweep axis

CORE_W, SOFT_W = 0.020, 0.075
CORE_COL = np.array([1.00, 1.00, 1.00], np.float32)
SOFT_COL = np.array([0.67, 0.78, 1.00], np.float32)

def screen(base, light):
    return 1 - (1 - base) * (1 - light)

# ---- ffmpeg sinks ----
FF = imageio_ffmpeg.get_ffmpeg_exe()
common_in = ["-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{F}x{F}", "-r", str(FPS), "-i", "-"]
p_mov = subprocess.Popen([FF, "-y", *common_in, "-c:v", "prores_ks", "-profile:v", "4444",
    "-pix_fmt", "yuva444p10le", f"{OUTD}\\xmotion_logo_loop_10s.mov"], stdin=subprocess.PIPE)
p_webm = subprocess.Popen([FF, "-y", *common_in, "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
    "-b:v", "6M", "-auto-alt-ref", "0", f"{OUTD}\\xmotion_logo_loop_10s.webm"], stdin=subprocess.PIPE)
p_prev = subprocess.Popen([FF, "-y", *common_in, "-filter_complex",
    f"color=c=0x1A1D24:s={F}x{F}:r={FPS}[bg];[bg][0:v]overlay=shortest=1,format=yuv420p",
    "-c:v", "libx264", "-crf", "18", f"{OUTD}\\xmotion_logo_loop_preview.mp4"], stdin=subprocess.PIPE)

# ---- render ----
for i in range(N):
    t = i / N                                                  # phase in [0,1)
    # sweep: fully exits (-0.35 .. 1.35) so re-entry is invisible at wrap
    sp = (t * SWEEPS_PER_LOOP) % 1.0
    pos = -0.35 + sp * 1.70
    d = proj - pos
    band = np.exp(-(d / SOFT_W) ** 2)[..., None] * SOFT_COL + \
           np.exp(-(d / CORE_W) ** 2)[..., None] * CORE_COL
    band *= 0.85
    lit = screen(logo_rgb, band * logo_a[..., None])           # shine only inside the mark

    pulse = 0.35 + 0.40 * (0.5 - 0.5 * np.cos(2 * np.pi * GLOW_CYCLES * t))
    ga = glow_shape * pulse
    out_a = logo_a + ga * (1 - logo_a)
    out_rgb = (lit * logo_a[..., None] + GLOW_COL * ga[..., None] * (1 - logo_a[..., None])) \
              / np.maximum(out_a[..., None], 1e-4)
    frame = np.dstack([np.clip(out_rgb, 0, 1), np.clip(out_a, 0, 1)])
    buf = (frame * 255).astype(np.uint8).tobytes()
    for p in (p_mov, p_webm, p_prev):
        p.stdin.write(buf)
    if i % 30 == 0:
        print(f"frame {i}/{N}", flush=True)

for p in (p_mov, p_webm, p_prev):
    p.stdin.close(); p.wait()
print("DONE - 3 outputs in", OUTD)
