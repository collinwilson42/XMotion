r"""
xmotion_overlay_batch.py  —  bulk A/B overlay generator for XMotion

Feed it ONE clean transparent logo PNG (export it from the Claude Design overlay
tool — it already keys the white background out perfectly). This script stamps
that logo into every A/B variant you want to test: size x position x opacity x
brand-tint x single-vs-diagonal x aspect ratio, each saved as a transparent PNG
ready to composite over a walkthrough video.

It is Pillow-only. No numpy, no browser.

  cd C:\dev\XMotion\_Tools
  py -m pip install pillow
  py xmotion_overlay_batch.py --logo assets/xmotion-logo.png

Options
  --logo PATH    transparent logo PNG (required)
  --mark PATH    optional compact "XM" monogram PNG for the diagonal marks;
                 defaults to the main logo scaled down
  --out  DIR     output folder (default: overlay_out)
  --ratios LIST  comma list from {9x16,16x9,1x1}  (default: 9x16,16x9)
  --key          rough white-removal if your logo still has a white background
                 (border flood-fill fallback — prefer the Design tool's export)

Edit the VARIANTS list below to change your A/B set. That's the whole knob board.
Signed — wiz-4.
"""

import argparse
import math
import os
from PIL import Image, ImageDraw, ImageOps

# ----------------------------------------------------------------------------- config
RATIOS = {"9x16": (1080, 1920), "16x9": (1920, 1080), "1x1": (1080, 1080)}

MARGIN_FRAC = 0.05          # edge margin for corner/edge placements (fraction of width)
HAIR_RGBA   = (242, 241, 234, 150)   # matte-white hairline colour + base alpha
BRAND_MINT  = "#99FF99"
BRAND_CADET = "#5F9EA0"

# Each dict is one output. mode "single" uses pos + width_frac; mode "diagonal"
# lays 7 nodes on an up-right diagonal (center = full logo, 6 flanking XM marks).
VARIANTS = [
    {"name": "A_center_bold",    "mode": "single",   "pos": "center",        "width_frac": 0.46, "opacity": 1.00, "tint": None},
    {"name": "B_center_subtle",  "mode": "single",   "pos": "center",        "width_frac": 0.34, "opacity": 0.75, "tint": None},
    {"name": "C_corner_mark",    "mode": "single",   "pos": "bottom-right",  "width_frac": 0.20, "opacity": 0.85, "tint": None},
    {"name": "D_center_mint",    "mode": "single",   "pos": "center",        "width_frac": 0.36, "opacity": 0.90, "tint": BRAND_MINT},
    {"name": "E_center_cadet",   "mode": "single",   "pos": "center",        "width_frac": 0.36, "opacity": 0.90, "tint": BRAND_CADET},
    {"name": "F_lower_third",    "mode": "single",   "pos": "bottom-center", "width_frac": 0.40, "opacity": 0.90, "tint": None},
    {"name": "G_diagonal6",      "mode": "diagonal", "width_frac": 0.30, "opacity": 0.85, "tint": None, "hairlines": True},
    {"name": "H_diagonal6_soft", "mode": "diagonal", "width_frac": 0.30, "opacity": 0.60, "tint": None, "hairlines": True},
]

# ----------------------------------------------------------------------------- helpers
def load_rgba(path):
    return Image.open(path).convert("RGBA")


def is_opaque(img):
    """True if the alpha channel is essentially all-on (no real transparency)."""
    a = img.split()[3]
    return a.getextrema()[0] >= 250


def corner_key(img, white=238):
    """Rough fallback: flood-fill near-white from the four corners to alpha 0.
    Enclosed letter counters (the holes in O/M) are left as-is. Prefer a proper
    transparent export from the Design tool over this."""
    rgb = img.convert("RGB")
    sentinel = (1, 254, 2)
    tol = 255 - white
    W, H = rgb.size
    for seed in [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1)]:
        ImageDraw.floodfill(rgb, seed, sentinel, thresh=tol)
    src = rgb.load()
    out = img.convert("RGBA")
    dst = out.load()
    for y in range(H):
        for x in range(W):
            if src[x, y] == sentinel:
                r, g, b, _ = dst[x, y]
                dst[x, y] = (r, g, b, 0)
    return out


def tint_logo(img, hexcolor):
    """Recolour the logo to a brand hue, preserving its luminance and alpha shape."""
    if not hexcolor:
        return img
    c = tuple(int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
    r, g, b, a = img.split()
    lum = Image.merge("RGB", (r, g, b)).convert("L")
    colored = ImageOps.colorize(lum, black=(0, 0, 0), white=c).convert("RGBA")
    colored.putalpha(a)
    return colored


def apply_opacity(layer, op):
    if op >= 0.999:
        return layer
    r, g, b, a = layer.split()
    a = a.point(lambda v: int(v * op))
    layer.putalpha(a)
    return layer


def resize_w(img, target_w):
    w, h = img.size
    s = target_w / w
    return img.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)


def place_single(canvas, logo, pos, margin):
    W, H = canvas.size
    lw, lh = logo.size
    cx, cy = (W - lw) // 2, (H - lh) // 2
    x, y = cx, cy
    if pos == "bottom-center": x, y = cx, H - lh - margin
    elif pos == "top-center":  x, y = cx, margin
    elif pos == "bottom-right": x, y = W - lw - margin, H - lh - margin
    elif pos == "bottom-left":  x, y = margin, H - lh - margin
    elif pos == "top-right":    x, y = W - lw - margin, margin
    elif pos == "top-left":     x, y = margin, margin
    canvas.alpha_composite(logo, (x, y))


def place_diagonal(canvas, logo, mark, width_frac, hairlines):
    W, H = canvas.size
    main_w = int(width_frac * W)
    full = resize_w(logo, main_w)
    small = resize_w(mark, int(main_w * 0.66))
    x0, y0 = 0.15 * W, 0.82 * H
    x1, y1 = 0.85 * W, 0.18 * H
    nodes = [(x0 + (x1 - x0) * t / 6.0, y0 + (y1 - y0) * t / 6.0) for t in range(7)]

    if hairlines:
        d = ImageDraw.Draw(canvas)
        gap = main_w * 0.34
        for i in range(6):
            ax, ay = nodes[i]
            bx, by = nodes[i + 1]
            dx, dy = bx - ax, by - ay
            L = math.hypot(dx, dy) or 1.0
            ux, uy = dx / L, dy / L
            d.line([(ax + ux * gap, ay + uy * gap), (bx - ux * gap, by - uy * gap)],
                   fill=HAIR_RGBA, width=2)

    for i, (nx, ny) in enumerate(nodes):
        g = full if i == 3 else small
        gw, gh = g.size
        canvas.alpha_composite(g, (int(nx - gw / 2), int(ny - gh / 2)))


def render_variant(v, logo, mark, W, H):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tinted = tint_logo(logo, v.get("tint"))
    if v["mode"] == "single":
        g = resize_w(tinted, int(v["width_frac"] * W))
        place_single(layer, g, v["pos"], int(MARGIN_FRAC * W))
    else:
        tmark = tint_logo(mark, v.get("tint"))
        place_diagonal(layer, tinted, tmark, v["width_frac"], v.get("hairlines", True))
    return apply_opacity(layer, v["opacity"])


def contact_sheet(layers, names, path, cols=4, cell=(270, 480)):
    """Dark montage so you can eyeball all variants at once (white overlays read)."""
    cw, ch = cell
    rows = (len(layers) + cols - 1) // cols
    pad, label = 16, 22
    sheet = Image.new("RGBA", (cols * cw + pad * (cols + 1),
                               rows * (ch + label) + pad * (rows + 1)), (14, 16, 19, 255))
    d = ImageDraw.Draw(sheet)
    for i, (lay, nm) in enumerate(zip(layers, names)):
        r, c = divmod(i, cols)
        x = pad + c * (cw + pad)
        y = pad + r * (ch + label + pad)
        thumb = lay.resize((cw, ch), Image.LANCZOS)
        sheet.alpha_composite(thumb, (x, y))
        d.text((x + 4, y + ch + 4), nm, fill=(210, 210, 205, 255))
    sheet.convert("RGBA").save(path)


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Bulk XMotion overlay A/B generator")
    ap.add_argument("--logo", required=True, help="transparent logo PNG")
    ap.add_argument("--mark", default=None, help="optional XM monogram PNG for diagonal marks")
    ap.add_argument("--out", default="overlay_out", help="output folder")
    ap.add_argument("--ratios", default="9x16,16x9", help="comma list: 9x16,16x9,1x1")
    ap.add_argument("--key", action="store_true", help="rough white-removal fallback")
    args = ap.parse_args()

    logo = load_rgba(args.logo)
    if args.key:
        logo = corner_key(logo)
    elif is_opaque(logo):
        print("!  Heads up: your logo has no transparency. Export a transparent PNG "
              "from the Design tool, or re-run with --key for a rough removal.")

    mark = load_rgba(args.mark) if args.mark else logo

    ratios = [r.strip() for r in args.ratios.split(",") if r.strip() in RATIOS]
    if not ratios:
        ratios = ["9x16"]

    os.makedirs(args.out, exist_ok=True)
    made = 0
    for rk in ratios:
        W, H = RATIOS[rk]
        layers, names = [], []
        for v in VARIANTS:
            layer = render_variant(v, logo, mark, W, H)
            fn = os.path.join(args.out, f"{v['name']}_{rk}.png")
            layer.save(fn)
            layers.append(layer)
            names.append(v["name"])
            made += 1
            print(f"  wrote {fn}")
        contact_sheet(layers, names, os.path.join(args.out, f"_contact_{rk}.png"))
        print(f"  wrote {os.path.join(args.out, f'_contact_{rk}.png')}")

    print(f"\nDone. {made} overlays + {len(ratios)} contact sheet(s) in '{args.out}'.")


if __name__ == "__main__":
    main()
