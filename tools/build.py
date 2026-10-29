"""Builds rocmine.net from src/ and writes the site files at the repo root.

    python tools/build.py            build everything
    python tools/build.py --check    exit 1 if the committed output is stale
    python tools/build.py --serve    build, then serve http://localhost:8080
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sitegen import build  # noqa: E402

if __name__ == "__main__":
    build.main(sys.argv[1:])
