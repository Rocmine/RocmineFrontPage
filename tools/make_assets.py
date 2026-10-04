"""Re-creates the derived site assets from the originals in source/.

Usage (from the repo root):
    python tools/make_assets.py

Needs Pillow + numpy, and ffmpeg (set FFMPEG=path\to\ffmpeg.exe if it is not on PATH).
"""
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source"
OUT = ROOT / "assets"
FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
BG = "0x090912"          # page colour at the header corner: --bg (#06060f) + ~2.5 levels from the grain overlay


def ff(*args):
    subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", *map(str, args)], check=True)


def logo_video():
    """Square logo with a transparent background -> opaque clips matching the page colour behind it.

    The source stores alpha in the WebM side channel, so it must be decoded with
    libvpx-vp9 (ffmpeg's native VP9 decoder drops alpha and turns the glow white).
    """
    (OUT / "video").mkdir(parents=True, exist_ok=True)
    src = SRC / "logo-spin-1080-alpha.webm"
    comp = (f"[1][0]overlay=shortest=1:format=auto,"
            f"crop=720:720:180:190,scale=112:112:flags=lanczos,fps=30,format=yuv420p")
    base = ["-c:v", "libvpx-vp9", "-i", src, "-f", "lavfi", "-i", f"color=c={BG}:s=1080x1080:r=60",
            "-filter_complex", comp, "-an"]
    ff(*base, "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "34", OUT / "video" / "logo-spin.webm")
    ff(*base, "-c:v", "libx264", "-crf", "22", "-movflags", "+faststart", OUT / "video" / "logo-spin.mp4")
    # poster: a front-facing frame
    ff(*base, "-ss", "4.2", "-frames:v", "1", OUT / "img" / "brand" / "logo-poster.png")


def icons():
    brand = OUT / "img" / "brand"
    brand.mkdir(parents=True, exist_ok=True)
    im = Image.open(SRC / "logo-render-1080p.jpg").convert("RGB")
    mark = im.crop((685, 265, 1245, 825))
    mark.resize((180, 180), Image.LANCZOS).save(brand / "apple-touch-icon.png", optimize=True)
    mark.resize((192, 192), Image.LANCZOS).save(brand / "icon-192.png", optimize=True)
    mark.resize((32, 32), Image.LANCZOS).save(brand / "favicon-32.png", optimize=True)
    w, h = im.size
    card = im.resize((1200, int(h * 1200 / w)), Image.LANCZOS)
    top = (card.height - 630) // 2
    card.crop((0, top, 1200, top + 630)).save(brand / "share-card.jpg", quality=84, optimize=True)


# portrait tuning (the original is very dark: mean ~19/255)
GAMMA = 0.62       # <1 lifts shadows
KEEP_BG = 0.04     # how much of the lift survives outside the subject (0 = untouched dark background)
CENTER = (0.50, 0.60)
RADII = (0.40, 0.46)
BLACK = 0.16       # black point applied after the lift, keeps the backdrop dark


def portrait():
    (OUT / "img" / "portrait").mkdir(parents=True, exist_ok=True)
    im = Image.open(SRC / "portrait-original-400.png").convert("RGB").resize((800, 800), Image.LANCZOS)
    a = np.asarray(im).astype("float32") / 255
    hi = np.percentile(a.mean(axis=2), 99.7)
    lifted = np.clip((np.clip(a / hi, 0, 1) ** GAMMA - BLACK) / (1 - BLACK), 0, 1)
    y, x = np.mgrid[0:800, 0:800] / 800
    d = np.sqrt(((x - CENTER[0]) / RADII[0]) ** 2 + ((y - CENTER[1]) / RADII[1]) ** 2)
    subject = np.clip(1.15 - d, 0, 1) ** 0.8                      # 1 on the subject, falling to 0 outside
    mix = KEEP_BG + (1 - KEEP_BG) * subject
    base = a * 1.0                                                 # original (dark) background
    out = base + (lifted - base) * mix[..., None]
    Image.fromarray((np.clip(out, 0, 1) * 255).astype("uint8")).save(
        OUT / "img" / "portrait" / "portrait-lit.webp", quality=88, method=6)


if __name__ == "__main__":
    steps = {"logo": logo_video, "icons": icons, "portrait": portrait}
    for name in (sys.argv[1:] or steps):
        print("making", name)
        steps[name]()
