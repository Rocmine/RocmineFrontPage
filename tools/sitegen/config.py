"""Shared constants."""
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SITE = "https://rocmine.net"
EMAIL = "amine.rochdi@rocmine.net"
esc = html.escape

SRC = ROOT / "src"
OUT = ROOT          # build.py points this at a temp dir for --check
WRITTEN = []
VERSION = {"css": "0", "js": "0"}   # content hashes for cache-busting, set by build.py        # relative paths written during a build


def load(name):
    """Read src/content/<name>.json."""
    import json
    return json.loads((SRC / "content" / f"{name}.json").read_text(encoding="utf8"))
