"""Downloads the site fonts (latin subset, variable woff2) into assets/fonts/.

    python tools/fetch_fonts.py

Unbounded and JetBrains Mono are licensed under the SIL Open Font License 1.1.
The files are committed, so this only needs to run when the fonts change.
"""
import re
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "fonts"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
FAMILIES = {
    "Unbounded": "https://fonts.googleapis.com/css2?family=Unbounded:wght@400..900&display=swap",
    "JetBrainsMono": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400..700&display=swap",
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, css_url in FAMILIES.items():
        css = get(css_url).decode("utf8")
        # blocks look like:  /* latin */ @font-face { ... src: url(...) ... }
        for subset, block in re.findall(r"/\* ([\w-]+) \*/\s*(@font-face \{.*?\})", css, flags=re.S):
            if subset != "latin":
                continue
            url = re.search(r"url\((https://[^)]+\.woff2)\)", block).group(1)
            dest = OUT / f"{name}-latin.woff2"
            dest.write_bytes(get(url))
            print(f"{dest.name}: {dest.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
