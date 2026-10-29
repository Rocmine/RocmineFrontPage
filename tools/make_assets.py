r"""Re-creates the derived site assets from the masters in originals/.

Usage (from the repo root):
    python tools/make_assets.py              # everything
    python tools/make_assets.py cards icons  # only some steps: logo icons cards portrait

Needs Pillow and ffmpeg (set FFMPEG=C:\path\to\ffmpeg.exe if it is not on PATH).
Card text comes from src/content/cards.json.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "originals"
OUT = ROOT / "assets"
FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
BG = "0x090912"          # page colour at the header corner: --bg (#06060f) + ~2.5 levels from the grain overlay

BLUE, VIOLET, MAGENTA = (59, 109, 255), (138, 77, 255), (238, 22, 129)
FG, MUTED = (236, 236, 242), (160, 160, 175)


def ff(*args):
    subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", *map(str, args)], check=True)


def logo_video():
    """Square logo with a transparent background -> opaque clips matching the page colour behind it.

    The source stores alpha in the WebM side channel, so it must be decoded with
    libvpx-vp9 (ffmpeg's native VP9 decoder drops alpha and turns the glow white).
    """
    (OUT / "video").mkdir(parents=True, exist_ok=True)
    (OUT / "img" / "brand").mkdir(parents=True, exist_ok=True)
    src = SRC / "logo-spin-1080-alpha.webm"
    comp = ("[1][0]overlay=shortest=1:format=auto,"
            "crop=720:720:180:190,scale=112:112:flags=lanczos,fps=30,format=yuv420p")
    base = ["-c:v", "libvpx-vp9", "-i", src, "-f", "lavfi", "-i", f"color=c={BG}:s=1080x1080:r=60",
            "-filter_complex", comp, "-an"]
    ff(*base, "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "34", OUT / "video" / "logo-spin.webm")
    ff(*base, "-c:v", "libx264", "-crf", "22", "-movflags", "+faststart", OUT / "video" / "logo-spin.mp4")
    ff(*base, "-ss", "4.2", "-frames:v", "1", OUT / "img" / "brand" / "logo-poster.png")  # front-facing frame


def logo_mark():
    im = Image.open(SRC / "logo-render-1080p.jpg").convert("RGB")
    return im.crop((685, 265, 1245, 825))


def icons():
    brand = OUT / "img" / "brand"
    brand.mkdir(parents=True, exist_ok=True)
    mark = logo_mark()
    for size, name in ((180, "apple-touch-icon.png"), (192, "icon-192.png"), (512, "icon-512.png"), (32, "favicon-32.png")):
        mark.resize((size, size), Image.LANCZOS).save(brand / name, optimize=True)
    mark.resize((48, 48), Image.LANCZOS).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])


def portrait():
    """The portrait is used exactly as shot: a plain copy, no grading or masks."""
    (OUT / "img" / "portrait").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SRC / "portrait-original-400.png", OUT / "img" / "portrait" / "portrait.png")


# ── share cards (1200x630) ────────────────────────────────────────────────────
def font(name, size, weight):
    f = ImageFont.truetype(str(SRC / "fonts" / name), size)
    f.set_variation_by_axes([weight])
    return f


def wrap_title(draw, text, max_w, max_lines=3):
    """Largest Unbounded 900 size whose wrapped text fits max_w within max_lines."""
    for size in range(96, 40, -4):
        f = font("Unbounded-VF.ttf", size, 900)
        lines, cur = [], ""
        for word in text.split():
            trial = f"{cur} {word}".strip()
            if draw.textlength(trial, font=f) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
        if len(lines) <= max_lines and all(draw.textlength(l, font=f) <= max_w for l in lines):
            return f, lines
    return f, lines


def card(slug, title, line, path):
    W, H = 1200, 630
    bg = ImageOps.fit(Image.open(SRC / "wallpaper-navy-2k.png").convert("RGB"), (W, H), Image.LANCZOS)
    bg = Image.blend(bg, Image.new("RGB", (W, H), (6, 6, 15)), 0.35)
    # logo mark, faded into the background with a radial mask
    size = 400
    mark = logo_mark().resize((size, size), Image.LANCZOS)
    mask = ImageOps.invert(Image.radial_gradient("L")).resize((size, size))
    mask = mask.point(lambda v: min(255, int(v * 1.6)))
    bg.paste(mark, (W - size - 40, (H - size) // 2), mask)

    d = ImageDraw.Draw(bg)
    x, max_w = 84, 640
    d.text((x, 72), path, font=font("JetBrainsMono-VF.ttf", 26, 600), fill=BLUE)
    f, lines = wrap_title(d, title.upper(), max_w)
    y = 150
    lh = int(f.size * 1.08)
    top = y
    for l in lines:
        d.text((x, y), l, font=f, fill=FG)
        y += lh
    # rail (blue -> violet -> magenta), like the site's name block
    bottom = y - int(f.size * 0.1)
    for i in range(top, bottom):
        t = (i - top) / max(1, bottom - top - 1)
        c = tuple(int(BLUE[k] + (VIOLET[k] - BLUE[k]) * t / 0.62) if t < 0.62
                  else int(VIOLET[k] + (MAGENTA[k] - VIOLET[k]) * (t - 0.62) / 0.38) for k in range(3))
        d.line([(x - 26, i), (x - 22, i)], fill=c, width=1)
    d.text((x, y + 28), line, font=font("JetBrainsMono-VF.ttf", 28, 400), fill=MUTED)
    d.text((x, H - 76), "rocmine.net", font=font("JetBrainsMono-VF.ttf", 26, 600), fill=FG)
    out = OUT / "img" / "cards"
    out.mkdir(parents=True, exist_ok=True)
    bg.save(out / f"{slug}.jpg", quality=86, optimize=True)


def cards():
    data = json.loads((ROOT / "src" / "content" / "cards.json").read_text(encoding="utf8"))
    for c in data["cards"]:
        card(c["slug"], c["title"], c["line"], c["path"])
        print("  card", c["slug"])


if __name__ == "__main__":
    steps = {"logo": logo_video, "icons": icons, "portrait": portrait, "cards": cards}
    for name in (sys.argv[1:] or steps):
        print("making", name)
        steps[name]()
