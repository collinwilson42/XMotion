#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMotion - Clipboard Capture Parser
========================================
Captures full-resolution images from the Windows clipboard the moment they
are copied, grouped into ADJUSTABLE TIME-BLOCK folders (default 5 minutes)
named in Eastern time, e.g.  PM_3-42_3-47.

Each block also gets a thumbnail subfolder  TN_<blockname>  (e.g.
TN_PM_3-42_3-47) holding small JPEG previews. Those TN_ thumbnails are the
AI-readable layer: a Claude account "scouts" a block by reading the TN_
folder, because the full-resolution PNGs exceed the media read size limit.

WORKFLOW FOR VAs
----------------
1. (one time)  pip install pillow
2. Run:        python "C:\\dev\\XMotion\\Tools\\legacy_capture.py"
   Adjust window:  ... legacy_capture.py --window 7     (or just  --7)
3. Open the listing. For each photo, either:
      - right-click the image > "Copy image"          (browser bitmap), or
      - select the image file(s) in Explorer > Ctrl+C (true originals - best)
   Every copy is saved into the current time block, plus a TN_ thumbnail.
4. Keys while running:
      n  = close the current block now (next copy opens a fresh one)
      q  = quit

OUTPUT LAYOUT
-------------
    C:\\dev\\XMotion\\Captures\\
        2026-06-27\\                   <- daily folder (Eastern date)
            PM_3-42_3-47\\             <- 5-min block, anchored to first copy (EST)
                001.png  002.png ...  <- full-resolution captures
                _manifest.md          <- index + WxH + LOW-RES flag per image
                TN_PM_3-42_3-47\\     <- AI-readable thumbnails (scout reads here)
                    001.jpg  002.jpg ...
                CS_PM_3-42_3-47\\     <- 3x3 contact sheets (bulk scout: 9 frames/read)
                    CS_PM_3-42_3-47_01.jpg ...

Contact sheets rebuild automatically whenever a block closes ([n], [q], or
window expiry). To (re)generate sheets for ALL existing blocks:

    py XCopy.py --backfill

Low-resolution images are FLAGGED but still saved. The flag is a coarse
picture-quality signal; the Shot Quality gate scores Noise/Ambiguity properly.
"""

import os
import sys
import time
import hashlib
import shutil
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
CAPTURE_ROOT          = r"C:\dev\XMotion\Captures"
DEFAULT_WINDOW_MIN    = 5       # block length in minutes (override via CLI)
POLL_SECONDS          = 0.4     # clipboard check interval
MIN_GOOD_EDGE_PX      = 720     # shortest edge below this -> flagged LOW-RES
                                # (720 = can't fill a 720p video frame)
THUMB_MAX_PX          = 768     # thumbnail longest edge
THUMB_QUALITY         = 72      # thumbnail JPEG quality
SHEET_COLS            = 3       # contact sheet grid columns
SHEET_ROWS            = 3       # contact sheet grid rows (9 frames/sheet)
SHEET_CELL_W          = 480     # contact sheet cell width  (px)
SHEET_CELL_H          = 330     # contact sheet cell height (px)
SHEET_FONT_PX         = 44      # frame-number label size (white, center-cell)
IMAGE_EXTS            = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff")
# ---------------------------------------------------------------------------

try:
    from PIL import Image, ImageGrab
except ImportError:
    print("Pillow is required.  Run:  pip install pillow")
    sys.exit(1)

# Eastern time for block naming, independent of the VPS timezone.
try:
    from zoneinfo import ZoneInfo
    EAST = ZoneInfo("America/New_York")
    def now_east():
        return datetime.now(EAST)
except Exception:
    EAST = None
    def now_east():
        return datetime.now()   # fallback: machine local time

# Windows single-keypress reader (no extra dependency)
try:
    import msvcrt
    def poll_key():
        if msvcrt.kbhit():
            try:
                return msvcrt.getch().decode("utf-8", "ignore").lower()
            except Exception:
                return ""
        return ""
except ImportError:
    def poll_key():
        return ""


def parse_window_arg(argv):
    """Accept  --window N | --mins N | -w N | --N | -N .  Default 5."""
    for i, a in enumerate(argv):
        if a in ("--window", "--mins", "-w") and i + 1 < len(argv):
            try:
                return max(1, int(argv[i + 1]))
            except ValueError:
                pass
        s = a.lstrip("-")
        if s.isdigit():
            return max(1, int(s))
    return DEFAULT_WINDOW_MIN


def hm(dt):
    h = dt.hour % 12 or 12
    return f"{h}-{dt.minute:02d}"


def block_folder_name(start_dt, window_min):
    end_dt = start_dt + timedelta(minutes=window_min)
    ampm = "AM" if start_dt.hour < 12 else "PM"
    return f"{ampm}_{hm(start_dt)}_{hm(end_dt)}"


def sha1_image(img):
    return "img:" + hashlib.sha1(img.tobytes()).hexdigest()


def sha1_files(paths):
    return "files:" + hashlib.sha1("|".join(sorted(paths)).encode()).hexdigest()


def content_hash_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class Block:
    """One time-window folder, with its TN_ thumbnail subfolder."""
    def __init__(self, start_dt, window_min):
        self.name = block_folder_name(start_dt, window_min)
        self.start = start_dt
        self.end = start_dt + timedelta(minutes=window_min)
        self.dir = os.path.join(CAPTURE_ROOT, start_dt.strftime("%Y-%m-%d"), self.name)
        self.thumb_dir = os.path.join(self.dir, "TN_" + self.name)
        os.makedirs(self.thumb_dir, exist_ok=True)   # also creates self.dir
        self.manifest = os.path.join(self.dir, "_manifest.md")
        self.seen = set()                              # per-block content dedup
        existing = [f for f in os.listdir(self.dir)
                    if f.lower().endswith(IMAGE_EXTS)]
        self.count = len(existing)                     # resume numbering if reused
        if not os.path.exists(self.manifest):
            self._init_manifest(window_min)

    def _init_manifest(self, window_min):
        with open(self.manifest, "w", encoding="utf-8") as f:
            f.write("# XMotion - Capture Manifest\n\n")
            f.write(f"Folder: `{self.dir}`  \n")
            f.write(f"Thumbnails: `TN_{self.name}/`  \n")
            f.write(f"Block: {self.start:%Y-%m-%d %I:%M %p} -> "
                    f"{self.end:%I:%M %p} ({window_min} min, Eastern)\n\n")
            f.write("| # | File | Resolution | Shortest Edge | Flag | Source |\n")
            f.write("|---|------|-----------|---------------|------|--------|\n")

    def expired(self, now_dt):
        return now_dt >= self.end

    def _make_thumb(self, src, out_name):
        """src may be a PIL.Image or a file path. Best-effort; never fatal."""
        try:
            im = src if isinstance(src, Image.Image) else Image.open(src)
            im = im.convert("RGB")
            im.thumbnail((THUMB_MAX_PX, THUMB_MAX_PX))
            im.save(os.path.join(self.thumb_dir, out_name), "JPEG", quality=THUMB_QUALITY)
        except Exception:
            pass

    def add_row(self, filename, w, h, source):
        self.count += 1
        short = min(w, h) if (w and h) else 0
        flag = "OK" if short >= MIN_GOOD_EDGE_PX else "LOW-RES"
        with open(self.manifest, "a", encoding="utf-8") as f:
            f.write(f"| {self.count:03d} | {filename} | {w}x{h} | {short} | "
                    f"{flag} | {source} |\n")
        return flag

    def save_bitmap(self, img):
        seq = self.count + 1
        name = f"{seq:03d}.png"
        save_img = img if img.mode in ("RGB", "RGBA", "L") else img.convert("RGBA")
        save_img.save(os.path.join(self.dir, name), "PNG")   # lossless full-res
        self._make_thumb(img, f"{seq:03d}.jpg")
        flag = self.add_row(name, img.size[0], img.size[1], "clipboard")
        return name, img.size, flag

    def save_original(self, src):
        seq = self.count + 1
        ext = os.path.splitext(src)[1].lower()
        name = f"{seq:03d}{ext}"
        out = os.path.join(self.dir, name)
        shutil.copy2(src, out)                               # exact original bytes
        try:
            with Image.open(out) as im:
                size = im.size
        except Exception:
            size = (0, 0)
        self._make_thumb(out, f"{seq:03d}.jpg")
        flag = self.add_row(name, size[0], size[1], os.path.basename(src))
        return name, size, flag


def _sheet_font(size=SHEET_FONT_PX):
    """Bold system font if available; PIL default as last resort."""
    try:
        from PIL import ImageFont
        for name in ("arialbd.ttf", "arial.ttf", "segoeui.ttf"):
            try:
                return ImageFont.truetype(name, size)
            except Exception:
                continue
        return ImageFont.load_default()
    except Exception:
        return None


def build_contact_sheets(block_dir, block_name):
    """Stitch TN_ thumbnails into 3x3 CS_ grid sheets.

    Each cell shows one thumbnail with its frame number overlaid in the
    center as white text (black stroke for legibility on any background).
    Sheets land in  CS_<block>\\CS_<block>_NN.jpg  -> 55 frames = 7 reads.
    Idempotent: stale sheets are cleared and rebuilt on every call.
    """
    from PIL import ImageDraw
    tn_dir = os.path.join(block_dir, "TN_" + block_name)
    if not os.path.isdir(tn_dir):
        return 0
    thumbs = sorted(f for f in os.listdir(tn_dir) if f.lower().endswith(".jpg"))
    if not thumbs:
        return 0
    cs_dir = os.path.join(block_dir, "CS_" + block_name)
    os.makedirs(cs_dir, exist_ok=True)
    for old in os.listdir(cs_dir):                 # rebuild-clean on re-run
        if old.lower().endswith(".jpg"):
            try:
                os.remove(os.path.join(cs_dir, old))
            except Exception:
                pass
    per = SHEET_COLS * SHEET_ROWS
    font = _sheet_font()
    sheets = 0
    for s in range(0, len(thumbs), per):
        batch = thumbs[s:s + per]
        rows = (len(batch) + SHEET_COLS - 1) // SHEET_COLS
        sheet = Image.new("RGB", (SHEET_COLS * SHEET_CELL_W, rows * SHEET_CELL_H),
                          (24, 24, 24))
        draw = ImageDraw.Draw(sheet)
        for i, fn in enumerate(batch):
            r, c = divmod(i, SHEET_COLS)
            x0, y0 = c * SHEET_CELL_W, r * SHEET_CELL_H
            try:
                with Image.open(os.path.join(tn_dir, fn)) as im:
                    im = im.convert("RGB")
                    im.thumbnail((SHEET_CELL_W - 8, SHEET_CELL_H - 8))
                    sheet.paste(im, (x0 + (SHEET_CELL_W - im.width) // 2,
                                     y0 + (SHEET_CELL_H - im.height) // 2))
            except Exception:
                pass
            label = os.path.splitext(fn)[0]        # '001'
            cx = x0 + SHEET_CELL_W // 2
            cy = y0 + SHEET_CELL_H // 2
            try:
                draw.text((cx, cy), label, fill="white", font=font,
                          anchor="mm", stroke_width=3, stroke_fill="black")
            except TypeError:                      # very old Pillow: no anchor/stroke
                draw.text((cx - 30, cy - 20), label, fill="white", font=font)
        sheets += 1
        sheet.save(os.path.join(cs_dir, f"CS_{block_name}_{sheets:02d}.jpg"),
                   "JPEG", quality=82)
    return sheets


def finalize_block_assets(block_dir, block_name):
    n = build_contact_sheets(block_dir, block_name)
    if n:
        print(f"  [sheets] {n} contact sheet(s) -> CS_{block_name}\\")
    return n


def backfill(root=CAPTURE_ROOT):
    """Regenerate CS_ contact sheets for every existing capture block."""
    made = blocks = 0
    if not os.path.isdir(root):
        print(f"no capture root at {root}")
        return
    for day in sorted(os.listdir(root)):
        day_dir = os.path.join(root, day)
        if not os.path.isdir(day_dir):
            continue
        for blk in sorted(os.listdir(day_dir)):
            blk_dir = os.path.join(day_dir, blk)
            if not os.path.isdir(os.path.join(blk_dir, "TN_" + blk)):
                continue
            n = build_contact_sheets(blk_dir, blk)
            print(f"[backfill] {day}\\{blk}: {n} sheet(s)")
            made += n
            blocks += 1
    print(f"backfill complete: {blocks} block(s), {made} sheet(s)")


def get_clipboard():
    """Returns ('image', PIL.Image) | ('files', [paths]) | None."""
    try:
        data = ImageGrab.grabclipboard()
    except Exception:
        return None
    if data is None:
        return None
    if isinstance(data, list):
        imgs = [p for p in data if isinstance(p, str)
                and p.lower().endswith(IMAGE_EXTS) and os.path.isfile(p)]
        return ("files", imgs) if imgs else None
    return ("image", data)


def main():
    if "--backfill" in sys.argv[1:]:
        backfill()
        return

    window_min = parse_window_arg(sys.argv[1:])
    os.makedirs(CAPTURE_ROOT, exist_ok=True)

    bar = "=" * 60
    print(bar)
    print("  LEGACY MOTION  -  CLIPBOARD CAPTURE")
    print(bar)
    print(f"  root   : {CAPTURE_ROOT}")
    print(f"  window : {window_min} min blocks  (folder = AMPM_start_end, Eastern)")
    print(f"  thumbs : TN_<block>/  ({THUMB_MAX_PX}px JPEG, AI scout layer)")
    print(f"  sheets : CS_<block>/  (3x3 grids, frame # centered — built at block close)")
    print(f"  rule   : shortest edge < {MIN_GOOD_EDGE_PX}px  ->  flagged LOW-RES")
    print(f"  keys   : [n] close block   [q] quit      (--backfill rebuilds all sheets)")
    print(bar)
    print("Waiting for the first copy...")

    block = None
    last_sig = None     # persists ACROSS blocks -> a lingering clipboard
                        # image is saved once and never re-spawns a folder

    try:
        while True:
            key = poll_key()
            if key == "q":
                break
            if key == "n" and block is not None:
                finalize_block_assets(block.dir, block.name)
                print("--- block closed; next copy opens a fresh one ---")
                block = None

            clip = get_clipboard()
            if clip:
                kind, payload = clip
                sig = sha1_image(payload) if kind == "image" else sha1_files(payload)

                if sig != last_sig:
                    last_sig = sig
                    now = now_east()

                    if block is None or block.expired(now):
                        if block is not None:
                            finalize_block_assets(block.dir, block.name)
                        block = Block(now, window_min)
                        print(f"\n[block] {block.dir}")

                    if kind == "image":
                        h = hashlib.sha1(payload.tobytes()).hexdigest()
                        if h not in block.seen:
                            block.seen.add(h)
                            name, (w, hh), flag = block.save_bitmap(payload)
                            mark = "OK " if flag == "OK" else "!! "
                            print(f"  {mark}{name}  {w}x{hh}  ({flag})   [{block.count} in block]")
                    else:  # files
                        for p in payload:
                            ch = content_hash_file(p)
                            if ch in block.seen:
                                continue
                            block.seen.add(ch)
                            name, (w, hh), flag = block.save_original(p)
                            mark = "OK " if flag == "OK" else "!! "
                            print(f"  {mark}{name}  {w}x{hh}  ({flag})  <- {os.path.basename(p)}"
                                  f"   [{block.count} in block]")

            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        pass

    if block is not None:
        finalize_block_assets(block.dir, block.name)
        print(f"\nDone. Last block: {block.dir}  ({block.count} images)")
    else:
        print("\nDone. No images captured.")


if __name__ == "__main__":
    main()
