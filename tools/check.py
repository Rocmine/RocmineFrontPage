"""Static checks for the built site. No dependencies.

    python tools/check.py

Fails (exit 1) on: broken internal links or #anchors, missing assets, duplicate ids,
images without alt, pages without title/description/canonical/one h1, invalid JSON-LD,
pages missing from sitemap.xml, unexpected third-party requests, and a blown size budget.
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://rocmine.net"
SKIP_DIRS = {"src", "tools", "docs", "originals", "node_modules", ".git", ".github", ".claude"}
# external hosts that pages may link to (outbound links only, never loaded as resources)
OUTBOUND = ("https://github.com/", "https://linkedin.com/", "https://rocmine.net")
HOME_BUDGET_KB = 450         # html + css + js + fonts + portrait + logo clip for the home page

errors = []


def err(page, msg):
    errors.append(f"{page}: {msg}")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.refs, self.imgs, self.metas, self.h1 = [], [], [], {}, 0
        self.title, self._in_title, self._in_ld, self.ld, self.canonical, self.lang = "", False, False, [], None, None
        self.resources = []   # things the browser loads (src, stylesheet, preload...)

    def handle_starttag(self, tag, a):
        a = dict(a)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "meta" and (a.get("name") or a.get("property")):
            self.metas[a.get("name") or a.get("property")] = a.get("content", "")
        elif tag == "link":
            if a.get("rel") == "canonical":
                self.canonical = a.get("href")
            if a.get("href"):
                (self.refs if a.get("rel") in ("canonical",) else self.resources).append(a["href"])
        elif tag == "script":
            if a.get("type") == "application/ld+json":
                self._in_ld = True
                self.ld.append("")
            if a.get("src"):
                self.resources.append(a["src"])
        elif tag == "a" and a.get("href"):
            self.refs.append(a["href"])
        elif tag in ("img", "source", "video") and (a.get("src") or a.get("poster")):
            self.resources.append(a.get("src") or a.get("poster"))
            if tag == "img":
                self.imgs.append(a)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "script":
            self._in_ld = False

    def handle_data(self, d):
        if self._in_title:
            self.title += d
        if self._in_ld:
            self.ld[-1] += d


def target_file(path):
    """/work/ -> work/index.html, /x.css -> x.css"""
    p = path.lstrip("/")
    f = ROOT / p
    if p == "" or p.endswith("/"):
        f = ROOT / p / "index.html"
    return f


def main():
    pages = {}
    for f in sorted(ROOT.rglob("*.html")):
        if SKIP_DIRS & set(f.relative_to(ROOT).parts):
            continue
        pages[f] = Page()
        pages[f].feed(f.read_text(encoding="utf8"))
    if not pages:
        print("no pages found (run: python tools/build.py)")
        return 1

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf8")
    in_sitemap = set(re.findall(r"<loc>(.*?)</loc>", sitemap))
    ids_by_url = {}
    for f, p in pages.items():
        url = "/" + f.relative_to(ROOT).as_posix()
        url = url[: -len("index.html")] if url.endswith("/index.html") else url
        ids_by_url[url] = set(p.ids)

    for f, p in pages.items():
        rel = f.relative_to(ROOT).as_posix()
        url = "/" + rel[: -len("index.html")] if rel.endswith("index.html") else "/" + rel
        noindex = p.metas.get("robots") == "noindex"
        # basics
        if not p.title.strip():
            err(rel, "missing <title>")
        if not p.metas.get("description"):
            err(rel, "missing meta description")
        if p.lang != "en":
            err(rel, f"html lang is {p.lang!r}")
        if p.h1 != 1:
            err(rel, f"{p.h1} <h1> elements (expected 1)")
        if not p.canonical:
            err(rel, "missing canonical link")
        for k in ("og:title", "og:description", "og:image", "twitter:card"):
            if not p.metas.get(k):
                err(rel, f"missing {k}")
        og = p.metas.get("og:image", "")
        if og.startswith(SITE) and not (ROOT / og[len(SITE):].lstrip("/")).exists():
            err(rel, f"og:image file missing: {og}")
        dupes = {i for i in p.ids if p.ids.count(i) > 1}
        if dupes:
            err(rel, f"duplicate ids: {sorted(dupes)}")
        for img in p.imgs:
            if "alt" not in img:
                err(rel, f"<img> without alt: {img.get('src')}")
        # structured data
        for block in p.ld:
            try:
                json.loads(block)
            except ValueError as e:
                err(rel, f"invalid JSON-LD: {e}")
        # sitemap parity
        if not noindex and (SITE + url) not in in_sitemap:
            err(rel, f"not in sitemap.xml ({SITE + url})")
        # resources must exist locally and be first-party
        for r in p.resources:
            if r.startswith(("http://", "https://", "//")):
                err(rel, f"third-party/absolute resource: {r}")
                continue
            if r.startswith("data:"):
                continue
            if not target_file(r.split("?")[0].split("#")[0]).exists():
                err(rel, f"missing resource: {r}")
        # links
        for href in p.refs:
            if href.startswith(("mailto:", "tel:")):
                continue
            if href.startswith(("http://", "https://")):
                if not href.startswith(OUTBOUND):
                    err(rel, f"unexpected outbound link: {href}")
                continue
            path, _, frag = href.partition("#")
            path = path.split("?")[0] or url
            tf = target_file(path)
            if not tf.exists():
                err(rel, f"broken link: {href}")
            elif frag:
                tid = ids_by_url.get(path if path.endswith("/") or path.endswith(".html") else path, None)
                if tid is None or frag not in tid:
                    err(rel, f"broken anchor: {href}")

    # urls in the sitemap must exist
    for loc in in_sitemap:
        if not target_file(loc[len(SITE):]).exists():
            err("sitemap.xml", f"points to a missing page: {loc}")

    # css: url() targets
    css = (ROOT / "assets" / "css" / "main.css").read_text(encoding="utf8")
    for u in set(re.findall(r"url\(['\"]?(/[^)'\"]+)['\"]?\)", css)):
        if not target_file(u.split("?")[0]).exists():
            err("assets/css/main.css", f"missing asset: {u}")

    # size budget for the home page
    home = [ROOT / "index.html", ROOT / "assets/css/main.css", ROOT / "assets/js/main.js",
            ROOT / "assets/fonts/Unbounded-latin.woff2", ROOT / "assets/fonts/JetBrainsMono-latin.woff2",
            ROOT / "assets/img/portrait/portrait.png", ROOT / "assets/video/logo-spin.webm"]
    kb = sum(p.stat().st_size for p in home if p.exists()) / 1024
    if kb > HOME_BUDGET_KB:
        err("budget", f"home page weighs {kb:.0f} KB (budget {HOME_BUDGET_KB} KB)")

    print(f"checked {len(pages)} pages, home weight {kb:.0f} KB")
    if errors:
        print(f"\n{len(errors)} problem(s):")
        for e in errors:
            print("  -", e)
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
