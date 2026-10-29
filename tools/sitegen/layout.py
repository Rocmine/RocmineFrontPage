"""Page chrome: <head>, header, footer and small HTML building blocks."""
import os

from . import config
from .config import SITE, EMAIL, esc
import json


# ─── Shared chrome ──────────────────────────────────────────────────────────
# Runs before first paint. Animation is ON unless the visitor used the footer switch;
# the OS "reduce motion" setting is intentionally not consulted.
MOTION_SCRIPT = ("<script>(function(d){d.classList.add('js');try{d.dataset.motion="
                 "localStorage.getItem('rocmine-motion')==='off'?'reduced':'full'}"
                 "catch(e){d.dataset.motion='full'}})(document.documentElement)</script>")

NAV = [("work", "~/work"), ("lab", "~/lab"), ("stack", "~/stack"), ("about", "~/about")]


def header(active, home=False):
    r0 = ' reveal d-0' if home else ''
    r1 = ' reveal d-1' if home else ''
    links = "".join(
        f'<a href="/{k}/"' + (' aria-current="page"' if active == k else '') + f'>{esc(label)}</a>'
        for k, label in NAV)
    return f'''  <header id="header">
    <a class="header-left{r0}" href="/" aria-label="ROCMINE, home">
      <video class="avatar" id="logo-video" autoplay muted loop playsinline preload="auto" poster="/assets/img/brand/logo-poster.png" aria-hidden="true">
        <source src="/assets/video/logo-spin.webm" type="video/webm" />
        <source src="/assets/video/logo-spin.mp4" type="video/mp4" />
      </video>
      <span class="logotype" translate="no">ROCMINE</span>
    </a>
    <nav class="site-nav{r1}" aria-label="Primary">{links}</nav>
    <span class="status-badge{r1}" aria-label="Status: available"><span class="status-dot" aria-hidden="true"></span>Available</span>
  </header>'''


def footer(home=False):
    r = ' reveal d-7' if home else ''
    return f'''  <footer id="footer">
    <nav class="footer-links{r}" aria-label="Contact and social links">
      <button class="link-btn" id="btn-email" data-email="{EMAIL}" aria-label="Copy email address">email</button>
      <span class="link-sep" aria-hidden="true">·</span>
      <a class="link-btn" href="https://github.com/Rocmine" id="btn-github" target="_blank" rel="noopener noreferrer">github</a>
      <span class="link-sep" aria-hidden="true">·</span>
      <a class="link-btn" href="https://linkedin.com/in/rocmine" id="btn-linkedin" target="_blank" rel="noopener noreferrer">linkedin</a>
    </nav>
    <div class="footer-right{r}">
      <button class="link-btn" id="btn-motion" type="button">motion: on</button>
      <a href="/" class="site-link">rocmine.net</a>
      <span class="footer-copy">© <span id="year">2026</span></span>
    </div>
  </footer>'''


def page(path, title, desc, body, active=None, home=False, extra_head="", body_class="", og_type="website", noindex=False):
    url = SITE + path
    slug = "home" if path in ("/", "/404.html") else path.strip("/").split("/")[-1]
    og = f"{SITE}/assets/img/cards/{slug}.jpg"
    og_alt = f"{title}"
    v = config.VERSION
    robots = '\n  <meta name="robots" content="noindex" />' if noindex else ""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />{robots}
  <meta name="theme-color" content="#06060f" />
  <meta name="color-scheme" content="dark" />
  <link rel="canonical" href="{url}" />

  <meta property="og:type" content="{og_type}" />
  <meta property="og:site_name" content="ROCMINE" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{og}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="{esc(og_alt)}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(desc)}" />
  <meta name="twitter:image" content="{og}" />

  <link rel="icon" href="/favicon.ico" sizes="48x48" />
  <link rel="icon" href="/assets/img/brand/favicon-32.png" type="image/png" sizes="32x32" />
  <link rel="apple-touch-icon" href="/assets/img/brand/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />

  <link rel="preload" href="/assets/fonts/Unbounded-latin.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/assets/fonts/JetBrainsMono-latin.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="stylesheet" href="/assets/css/main.css?v={v['css']}" />
  {MOTION_SCRIPT}{extra_head}
</head>
<body class="{body_class}">

<a class="skip" href="#main">Skip to content</a>
<div id="grain" aria-hidden="true"></div>

<div id="grid">

{header(active, home)}

{body}

{footer(home)}

</div>

<div id="toast" role="status" aria-live="polite" aria-atomic="true"></div>

<script src="/assets/js/main.js?v={v['js']}" defer></script>
</body>
</html>
'''


def write(rel, content):
    full = os.path.join(config.OUT, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf8", newline="\n") as f:
        f.write(content)
    config.WRITTEN.append(rel)


def head_block(crumb, title, lede=None, long=False, meta=None):
    lede_html = f'\n      <p class="page-lede reveal d-3">{lede}</p>' if lede else ""
    meta_html = ""
    if meta:
        meta_html = '\n      <p class="case-meta reveal d-3">' + "".join(
            f"<span>{esc(k)} <b>{esc(v)}</b></span>" for k, v in meta) + "</p>"
    cls = "page-title long" if long else "page-title"
    return f'''    <div class="page-head rail">
      <p class="crumb reveal d-1">{crumb}</p>
      <h1 class="{cls} reveal d-2">{esc(title)}</h1>{lede_html}{meta_html}
    </div>'''


def sec(label, inner, wide=False, sid=None):
    idattr = f' id="{sid}"' if sid else ""
    cls = "sec sec-wide" if wide else "sec"
    return f'''    <section class="{cls}"{idattr}>
      <h2 class="sec-label">{esc(label)}</h2>
      <div class="sec-body">
{inner}
      </div>
    </section>'''


def points(items):
    return '        <ul class="points">\n' + "\n".join(f"          <li>{i}</li>" for i in items) + "\n        </ul>"


def chips(items):
    return '        <ul class="chips">\n' + "\n".join(f"          <li>{esc(i)}</li>" for i in items) + "\n        </ul>"


def chips_links(pairs):
    """Chips that link to a skills group on the About page: [(label, href), ...]."""
    return '        <ul class="chips chips-links">\n' + "\n".join(
        f'          <li><a href="{href}">{esc(label)}</a></li>' for label, href in pairs) + "\n        </ul>"


def crumb_trail(*parts):
    out = '<span class="role-prompt">~/</span>'
    segs = []
    for href, label in parts:
        segs.append(f'<a href="{href}">{esc(label)}</a>' if href else esc(label))
    return out + " / ".join(segs)


# ─── structured data (schema.org JSON-LD) ───────────────────────────────────
PERSON_ID = SITE + "/#person"


def ld_script(obj):
    return '\n  <script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=2) + '\n  </script>'


def breadcrumb_ld(*items):
    """items: (name, path) pairs after Home, e.g. ("Work", "/work/")."""
    trail = [("Home", "/")] + list(items)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p} for i, (n, p) in enumerate(trail)]}


def article_ld(title, desc, path):
    return {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc,
            "url": SITE + path, "author": {"@id": PERSON_ID}, "inLanguage": "en",
            "image": SITE + "/assets/img/cards/" + path.strip("/").split("/")[-1] + ".jpg",
            "mainEntityOfPage": SITE + path}


