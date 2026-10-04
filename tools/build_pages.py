# -*- coding: utf-8 -*-
"""Generates the static pages of rocmine.net (output is plain HTML, committed to the repo).

Usage (from the repo root):  python tools/build_pages.py
Preview:                      python -m http.server 8080
"""
import html, json, os, sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parent.parent)
SITE = "https://rocmine.net"
EMAIL = "amine.rochdi@rocmine.net"
esc = html.escape


# ─── SVG helpers (all shapes carry pathLength=1 so one CSS rule draws them) ──
class Svg:
    def __init__(self, w, h, title, desc):
        self.w, self.h, self.title, self.desc = w, h, title, desc
        self.p = []

    def box(self, x, y, w, h, label, sub=None, cls="", d=0.0):
        self.p.append(
            f'<rect class="node {cls} draw" x="{x}" y="{y}" width="{w}" height="{h}" '
            f'pathLength="1" style="--d:{d}s"/>')
        cx = x + w / 2
        if not label:
            return
        if sub:
            self.text(cx, y + h / 2 - 3, label, "", d + 0.5, "middle")
            self.text(cx, y + h / 2 + 14, sub, "sub", d + 0.6, "middle")
        else:
            self.text(cx, y + h / 2 + 4, label, "", d + 0.5, "middle")

    def encl(self, x, y, w, h, d=0.0):
        self.p.append(
            f'<rect class="encl draw" x="{x}" y="{y}" width="{w}" height="{h}" '
            f'pathLength="1" style="--d:{d}s"/>')

    def wire(self, path, cls="", d=0.0):
        self.p.append(
            f'<path class="wire {cls} draw" d="{path}" pathLength="1" style="--d:{d}s"/>')

    def line(self, x1, y1, x2, y2, cls="node", d=0.0):
        self.p.append(
            f'<path class="{cls} draw" d="M{x1} {y1} L{x2} {y2}" fill="none" '
            f'pathLength="1" style="--d:{d}s"/>')

    def text(self, x, y, s, cls="", d=0.4, anchor="start"):
        c = ("fade " + cls).strip()
        self.p.append(
            f'<text class="{c}" x="{x}" y="{y}" text-anchor="{anchor}" '
            f'style="--d:{d}s">{esc(s)}</text>')

    def render(self, uid, extra=""):
        cls = ("diagram " + extra).strip()
        return (
            f'<svg class="{cls}" viewBox="0 0 {self.w} {self.h}" role="img" '
            f'aria-labelledby="{uid}-t {uid}-d" xmlns="http://www.w3.org/2000/svg">'
            f'<title id="{uid}-t">{esc(self.title)}</title>'
            f'<desc id="{uid}-d">{esc(self.desc)}</desc>' + "".join(self.p) + "</svg>")


def diagram_quake():
    s = Svg(960, 300, "Morocco Earthquake Tracker architecture",
            "Visitors reach Cloudflare, then an Nginx reverse proxy that load-balances two Express.js API "
            "instances backed by a MySQL or MariaDB database, all hosted on the RocmineLabs Proxmox homelab.")
    s.encl(350, 24, 600, 252, 0.2)
    s.text(366, 46, "Hosted on RocmineLabs · Proxmox VE", "cap", 0.9)
    s.box(10, 110, 130, 80, "Visitors", "10M+ visits", "", 0.0)
    s.box(190, 110, 130, 80, "Cloudflare", "protection", "core", 0.3)
    s.box(380, 110, 150, 80, "Nginx", "reverse proxy · LB", "core", 0.6)
    s.box(600, 62, 150, 64, "Express.js API", "instance", "", 0.9)
    s.box(600, 174, 150, 64, "Express.js API", "instance", "", 1.0)
    s.box(800, 110, 140, 80, "MySQL / MariaDB", None, "hot", 1.2)
    s.wire("M140 150 H190", "", 0.2)
    s.wire("M320 150 H380", "", 0.5)
    s.wire("M530 150 H565 V94 H600", "", 0.8)
    s.wire("M530 150 H565 V206 H600", "", 0.85)
    s.wire("M750 94 H775 V150 H800", "hot", 1.1)
    s.wire("M750 206 H775 V150", "hot", 1.15)
    return s.render("dq")


def diagram_dc():
    s = Svg(960, 430, "3-Tier versus hyperconverged architecture",
            "Left: a 3-Tier mock-up with VMware ESXi compute, an iSCSI and NFS storage network and TrueNAS Core "
            "storage on a ZFS RAID-Z1 pool. Right: a Nutanix Community Edition hyperconverged cluster with "
            "Prism Element, virtual machines and AOS storage. Both are protected by Veeam Backup & Replication.")
    s.text(60, 24, "3-Tier", "head", 0.1)
    s.text(570, 24, "Hyperconverged (HCI)", "head", 0.1)
    # 3-tier
    s.box(60, 44, 330, 72, "Compute", "VMware ESXi 8.0 · vSphere", "core", 0.1)
    s.box(60, 160, 330, 60, "SAN / NAS network", "iSCSI LUNs · NFS", "", 0.4)
    s.box(60, 264, 330, 72, "Storage", "TrueNAS Core · ZFS pool RAID-Z1", "core", 0.7)
    s.wire("M225 116 V160", "", 0.3)
    s.wire("M225 220 V264", "", 0.6)
    # hci
    s.box(570, 44, 330, 292, "", None, "core", 0.2)
    s.text(586, 66, "Nutanix Community Edition cluster", "cap", 0.7)
    s.box(596, 84, 278, 56, "Prism Element", "cluster management", "", 0.5)
    s.box(596, 164, 278, 56, "Virtual machines", None, "", 0.7)
    s.box(596, 244, 278, 70, "AOS storage", "native snapshots", "hot", 0.9)
    s.wire("M735 140 V164", "", 0.7)
    s.wire("M735 220 V244", "", 0.9)
    # backup bar
    s.box(60, 376, 840, 44, "Veeam Backup & Replication  ·  full + incremental backups  ·  restore tests", None, "hot", 1.3)
    s.wire("M225 336 V376", "hot", 1.2)
    s.wire("M735 336 V376", "hot", 1.25)
    return s.render("dd")


def diagram_lab():
    s = Svg(960, 340, "RocmineLabs topology",
            "Internet traffic passes through Cloudflare to an Nginx reverse proxy and load balancer, then to "
            "a multi-node Proxmox VE environment running web services, monitoring, game servers, local LLMs "
            "with MCP agents, and the Morocco Earthquake Tracker.")
    s.encl(560, 16, 400, 308, 0.2)
    s.text(576, 38, "Proxmox VE · multi-node", "cap", 0.9)
    s.box(0, 130, 110, 76, "Internet", None, "", 0.0)
    s.box(160, 130, 130, 76, "Cloudflare", "protection", "core", 0.3)
    s.box(340, 130, 160, 76, "Nginx", "reverse proxy · LB", "core", 0.6)
    s.box(580, 56, 170, 64, "Web services", None, "", 0.9)
    s.box(580, 140, 170, 64, "Monitoring", None, "", 1.0)
    s.box(580, 224, 170, 64, "Earthquake Tracker", "10M+ visits", "hot", 1.1)
    s.box(770, 56, 170, 64, "Game servers", "Minecraft · CS2 · FiveM", "", 1.2)
    s.box(770, 140, 170, 64, "Local LLMs + agents", "Ollama · MCP", "hot", 1.3)
    s.wire("M110 168 H160", "", 0.2)
    s.wire("M290 168 H340", "", 0.5)
    s.wire("M500 168 H560", "", 0.8)
    return s.render("dl")


def hw_r630():
    s = Svg(640, 96, "Dell PowerEdge R630, front view (illustration)",
            "A 1U rack server with a row of drive bays, a power button and ventilation slots.")
    s.box(4, 14, 632, 68, "", None, "core", 0.0)
    s.line(36, 14, 36, 82, "node", 0.2)
    s.line(604, 14, 604, 82, "node", 0.2)
    for i in range(8):
        s.box(56 + i * 56, 26, 48, 44, "", None, "", 0.2 + i * 0.05)
    s.p.append('<circle class="node hot draw" cx="620" cy="30" r="5" pathLength="1" style="--d:0.9s"/>')
    for i in range(3):
        s.line(612, 48 + i * 7, 628, 48 + i * 7, "node", 0.9)
    return s.render("hr", "hw")


def hw_t5820():
    s = Svg(220, 330, "Dell Precision T5820, front view (illustration)",
            "A tower workstation with a front vent grille, an optical bay, a power button and ports.")
    s.box(6, 6, 208, 318, "", None, "core", 0.0)
    s.box(26, 26, 168, 24, "", None, "", 0.2)
    s.p.append('<circle class="node hot draw" cx="110" cy="86" r="9" pathLength="1" style="--d:0.5s"/>')
    for i in range(14):
        s.line(30, 124 + i * 11, 190, 124 + i * 11, "node", 0.4 + i * 0.04)
    s.box(26, 290, 60, 16, "", None, "", 0.9)
    s.box(96, 290, 24, 16, "", None, "", 0.95)
    s.box(130, 290, 24, 16, "", None, "", 1.0)
    return s.render("ht", "hw")


# ─── Static thumbnails for the work list (baked colours, used via <img>) ────
def write_thumbs():
    def wrap(inner):
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 110" fill="none" '
                'stroke-width="1.2"><style>text{font-family:monospace;font-size:10px;fill:#8e8e99;stroke:none}'
                '.n{stroke:#56566a}.c{stroke:#3b6dff}.h{stroke:#ee1681}.w{stroke:#3b6dff}</style>' + inner + '</svg>')

    def r(x, y, w, h, c="n"):
        return f'<rect class="{c}" x="{x}" y="{y}" width="{w}" height="{h}"/>'

    quake = (r(4, 36, 60, 38) + r(92, 36, 60, 38, "c") + r(180, 36, 70, 38, "c") + r(290, 14, 70, 32) +
             r(290, 64, 70, 32) + r(400, 36, 76, 38, "h") +
             '<path class="w" d="M64 55H92M152 55H180M250 55H272V30H290M250 55H272V80H290M360 30H380V55H400M360 80H380V55"/>'
             '<text x="12" y="58">visitors</text><text x="100" y="58">cf</text><text x="196" y="58">nginx</text>'
             '<text x="304" y="34">api</text><text x="304" y="84">api</text><text x="420" y="58">db</text>')
    dc = (r(8, 8, 180, 26, "c") + r(8, 42, 180, 22) + r(8, 72, 180, 26, "c") +
          r(280, 8, 190, 90, "c") + r(292, 20, 166, 20) + r(292, 48, 166, 20) + r(292, 76, 166, 14, "h") +
          '<path class="w" d="M98 34V42M98 64V72"/>'
          '<text x="212" y="58">vs</text>')
    lab = (r(8, 8, 464, 22, "c") + r(8, 38, 464, 22) + r(8, 68, 464, 22) +
           ''.join(f'<rect class="n" x="{20 + i * 40}" y="12" width="30" height="14"/>' for i in range(10)) +
           '<circle class="h" cx="452" cy="49" r="4"/><circle class="c" cx="452" cy="79" r="4"/>')
    for name, body in (("thumb-earthquake-tracker", quake), ("thumb-datacenter-hci", dc), ("thumb-rocminelabs", lab)):
        with open(os.path.join(ROOT, "assets", "img", "work", name + ".svg"), "w", encoding="utf8") as f:
            f.write(wrap(body))


# ─── Shared chrome ──────────────────────────────────────────────────────────
# Runs before first paint. Animation is ON unless the visitor used the footer switch;
# the OS "reduce motion" setting is intentionally not consulted.
MOTION_SCRIPT = ("<script>(function(d){d.classList.add('js');try{d.dataset.motion="
                 "localStorage.getItem('rocmine-motion')==='off'?'reduced':'full'}"
                 "catch(e){d.dataset.motion='full'}})(document.documentElement)</script>")

NAV = [("work", "~/work"), ("lab", "~/lab"), ("about", "~/about")]


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
    og = f"{SITE}/assets/img/brand/share-card.jpg"
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
  <meta name="twitter:card" content="summary_large_image" />

  <link rel="icon" href="/assets/img/brand/favicon-32.png" type="image/png" sizes="32x32" />
  <link rel="apple-touch-icon" href="/assets/img/brand/apple-touch-icon.png" />

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;700;900&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/assets/css/main.css" />
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

<script src="/assets/js/main.js"></script>
</body>
</html>
'''


def write(rel, content):
    full = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf8", newline="\n") as f:
        f.write(content)


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


def crumb_trail(*parts):
    out = '<span class="role-prompt">~/</span>'
    segs = []
    for href, label in parts:
        segs.append(f'<a href="{href}">{esc(label)}</a>' if href else esc(label))
    return out + " / ".join(segs)


# ═══════════════════════════════════════════════════════════════════════════
#  HOME
# ═══════════════════════════════════════════════════════════════════════════
TICKER = ["LINUX", "PROXMOX", "VMWARE ESXI", "NUTANIX", "DOCKER", "KUBERNETES", "TERRAFORM", "ANSIBLE",
          "NGINX", "CLOUDFLARE", "GCP", "AWS", "AZURE", "PYTHON", "FASTAPI", "OLLAMA", "MCP", "RAG"]


def home():
    sep = " &nbsp;·&nbsp; "
    ticker = sep.join(TICKER)
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Rochdi Mohamed Amine",
        "alternateName": ["Mohamed Amine Rochdi", "ROCMINE"],
        "jobTitle": "AI, Cloud & Infrastructure Engineer",
        "url": SITE + "/",
        "email": "mailto:" + EMAIL,
        "image": SITE + "/assets/img/brand/share-card.jpg",
        "address": {"@type": "PostalAddress", "addressCountry": "MA", "addressLocality": "Rabat"},
        "alumniOf": "École Marocaine des Sciences d'Ingénieur",
        "knowsAbout": ["Generative AI", "Cloud computing", "DevOps", "Datacenter infrastructure", "Virtualisation"],
        "sameAs": ["https://github.com/Rocmine", "https://linkedin.com/in/rocmine"],
    }, ensure_ascii=False, indent=2)
    body = f'''  <main id="main" class="main-home">

    <div id="portrait-bg" aria-hidden="true"></div>

    <h1 class="sr-only">Rochdi Mohamed Amine, AI, cloud and infrastructure engineer</h1>

    <div class="left-col">

      <p class="role-line reveal d-1" aria-label="Role: AI, cloud and infrastructure engineer">
        <span class="role-prompt">~/</span><span class="role-text"> ai · cloud · infrastructure engineer</span><span class="cursor" aria-hidden="true"></span>
      </p>

      <div class="name-block rail" translate="no">
        <span class="name-line reveal d-2" aria-hidden="true">ROCHDI</span>
        <span class="name-line reveal d-3" aria-hidden="true">MOHAMED</span>
        <span class="name-line reveal d-4" aria-hidden="true">AMINE</span>
        <p class="name-tagline reveal d-5">I build LLM applications, and the cloud and infrastructure that carries them to production.</p>
      </div>

      <ol class="specialties reveal d-6" aria-label="Areas of expertise">
        <li><a href="/about/#skills-ai"><span class="spec-num">01</span>AI</a></li>
        <li><a href="/about/#skills-cloud"><span class="spec-num">02</span>Cloud</a></li>
        <li><a href="/about/#skills-datacenter"><span class="spec-num">03</span>Infrastructure</a></li>
        <li><a href="/about/#skills-cloud"><span class="spec-num">04</span>DevOps</a></li>
      </ol>

      <div class="name-stats reveal d-8">
        <span class="stat"><span class="stat-key">Based in</span><span class="stat-val">Rabat, Morocco</span></span>
        <span class="stat-sep" aria-hidden="true">·</span>
        <span class="stat"><span class="stat-key">Degree</span><span class="stat-val">State Engineer · EMSI 2026</span></span>
        <span class="stat-sep" aria-hidden="true">·</span>
        <span class="stat"><span class="stat-key">Peak traffic</span><span class="stat-val">10M+ visits</span></span>
        <span class="stat-sep" aria-hidden="true">·</span>
        <span class="stat"><span class="stat-key">Homelab</span><span class="stat-val">2 enterprise servers</span></span>
      </div>

    </div>

    <span id="edge-label" aria-hidden="true">ROCMINE.NET · PORTFOLIO · 2026</span>

    <p class="stack-ticker reveal d-7" aria-label="Tech stack: {', '.join(t.title() for t in TICKER)}">
      <span class="ticker-label">STACK</span>
      <span class="ticker-rule">──</span>
      <span class="ticker-body">
        <span class="ticker-run">
          <span class="ticker-items">{ticker}</span>
          <span class="ticker-items" aria-hidden="true">{ticker}</span>
        </span>
      </span>
    </p>

  </main>'''
    extra = '\n  <script type="application/ld+json">\n' + jsonld + '\n  </script>'
    return page("/", "ROCMINE — Rochdi Mohamed Amine · AI, cloud & infrastructure engineer",
                "Rochdi Mohamed Amine (ROCMINE): State Engineer in computer science and networks. Generative-AI applications, cloud & DevOps, and datacenter infrastructure. Based in Rabat, Morocco.",
                body, home=True, extra_head=extra, body_class="page-home")


# ═══════════════════════════════════════════════════════════════════════════
#  WORK
# ═══════════════════════════════════════════════════════════════════════════
def work_row(num, title, stack, meta, href=None, thumb=None):
    thumb_html = ""
    if thumb:
        thumb_html = f'\n          <span class="w-thumb" aria-hidden="true"><span><img src="/assets/img/work/{thumb}" alt="" width="480" height="110" loading="lazy" /></span></span>'
    inner = f'''          <span class="w-num">{num}</span>
          <span class="w-main"><span class="w-title">{esc(title)}</span><span class="w-stack">{esc(stack)}</span></span>
          <span class="w-meta">{esc(meta)}</span>
          <span class="w-arrow" aria-hidden="true">{"→" if href else ""}</span>{thumb_html}'''
    if href:
        el = f'        <a class="work-link" href="{href}">\n{inner}\n        </a>'
    else:
        el = f'        <div class="work-link">\n{inner}\n        </div>'
    return f'      <li class="work-row">\n{el}\n      </li>'


def work():
    rows = "\n".join([
        work_row("01", "Morocco Earthquake Tracker", "Express.js · Nginx load balancing · Cloudflare · MariaDB", "10M+ visits", "/work/earthquake-tracker/", "thumb-earthquake-tracker.svg"),
        work_row("02", "Datacenter: 3-Tier vs HCI", "VMware ESXi · TrueNAS · Nutanix · Veeam", "Final-year project", "/work/datacenter-hci/", "thumb-datacenter-hci.svg"),
        work_row("03", "RocmineLabs", "Proxmox VE · Nginx · Cloudflare · Ollama · MCP", "Homelab", "/lab/", "thumb-rocminelabs.svg"),
        work_row("04", "Safar AI", "React · Tailwind CSS · Flask · PostgreSQL", "Team project"),
        work_row("05", "Metascope", "Python · FastAPI · Docker", "Personal project"),
    ])
    others = [
        ("RocAtlas CS2", None), ("netboot-lan", None), ("SYNFPS stream package", None), ("Chediid stream overlays", None),
        ("7wayej.ma", None), ("FoodAdmin", None), ("TarikhAlHuroob", None),
        ("yalahbadi", "https://github.com/Rocmine/yalahbadi"),
        ("Oh My Posh theme", "https://github.com/Rocmine/Rocmine_omp_theme"),
        ("Vencord theme", "https://github.com/Rocmine/DiscordVencordThemeRCMParameter"),
        ("Fresh-install scripts", "https://github.com/Rocmine/RocmineFreshInstallPrograms"),
    ]
    other_html = "\n".join(
        f'          <li><a href="{u}" target="_blank" rel="noopener noreferrer">{esc(n)}</a></li>' if u
        else f"          <li>{esc(n)}</li>" for n, u in others)
    body = f'''  <main id="main" class="page">

{head_block(crumb_trail((None, "work")), "Work", "Infrastructure, AI and web projects, from a datacenter study to a site that passed 10 million visits.")}

    <ol class="work-list">
{rows}
    </ol>

{sec("Other projects", f'        <ul class="other-list">{chr(10)}{other_html}{chr(10)}        </ul>')}

  </main>'''
    return page("/work/", "Work — ROCMINE",
                "Selected projects by Rochdi Mohamed Amine: the Morocco Earthquake Tracker, a 3-Tier vs HCI datacenter study at CBI.MA, the RocmineLabs homelab, Safar AI and Metascope.",
                body, active="work")


def case_nav(label, href, name):
    return f'''    <a class="next-link" href="{href}">
      <span class="nl-key">{esc(label)}</span>
      <span class="nl-val">{esc(name)}</span>
    </a>'''


def quake():
    body = f'''  <main id="main" class="page">

{head_block(crumb_trail(("/work/", "work"), (None, "earthquake-tracker")), "Morocco Earthquake Tracker",
            "A public earthquake tracker for Morocco, built and hosted by me. It passed 10 million visits without an interruption.",
            long=True, meta=[("Type", "Personal project"), ("Role", "Design, build, hosting"), ("Reach", "10M+ visits")])}

{sec("Architecture", '''        <div class="diagram-wrap">
        ''' + diagram_quake() + '''
        </div>
        <p class="diagram-note">Simplified request path. Two API instances are drawn to show the load-balancing layer.</p>''', wide=True)}

{sec("What I built", points([
        "An <b>Express.js</b> back end exposing a REST API, backed by <b>MySQL / MariaDB</b>.",
        "<b>Nginx</b> as reverse proxy, load-balancing traffic across the application instances.",
        "<b>Cloudflare</b> in front of the origin for protection against abusive traffic.",
        "Self-hosting on <a href=\"/lab/\">RocmineLabs</a>, my homelab: Dell enterprise servers running Proxmox VE.",
    ]))}

{sec("Stack", chips(["Express.js", "REST API", "Nginx", "Load balancing", "Cloudflare", "MySQL", "MariaDB", "Proxmox VE", "Linux"]))}

{sec("Outcome", '        <p class="lead-p">More than 10 million visits, served from a home datacenter with no interruption.</p>')}

{case_nav("Next project", "/work/datacenter-hci/", "Datacenter: 3-Tier vs HCI")}

  </main>'''
    return page("/work/earthquake-tracker/", "Morocco Earthquake Tracker — ROCMINE",
                "Case study: a public earthquake tracker for Morocco on Express.js, Nginx load balancing and Cloudflare, self-hosted on a Proxmox homelab, with more than 10 million visits.",
                body, active="work", og_type="article")


def datacenter():
    body = f'''  <main id="main" class="page">

{head_block(crumb_trail(("/work/", "work"), (None, "datacenter-hci")), "Datacenter: 3-Tier vs HCI",
            "My final-year project at CBI.MA: two ways to build a datacenter, compared on a working mock-up with data protection on top.",
            long=True, meta=[("Where", "CBI.MA"), ("When", "2025 – 2026"), ("School", "EMSI, Rabat")])}

{sec("Context", '''        <div class="prose">
          <p>CBI.MA is an integrator specialised in datacenter, cloud and cybersecurity infrastructure: 55 years in business, 300+ people, 13 African countries.</p>
          <p>The question: should a customer build on the classic 3-Tier architecture (separate compute, network and storage) or on hyperconverged infrastructure (HCI), where the same nodes provide both? I built both and measured them.</p>
        </div>''')}

{sec("Architecture", '''        <div class="diagram-wrap">
        ''' + diagram_dc() + '''
        </div>
        <p class="diagram-note">Simplified view of the two mock-ups and the shared backup layer.</p>''', wide=True)}

{sec("What I built", points([
        "A <b>3-Tier mock-up</b>: VMware ESXi 8.0 hypervisor, with SAN/NAS storage on TrueNAS Core (ZFS pool in RAID-Z1, iSCSI and NFS LUNs).",
        "A <b>hyperconverged architecture</b> on Nutanix Community Edition, managed through a Prism Element cluster.",
        "<b>Data protection</b> with Veeam Backup &amp; Replication: full and incremental backups, restores, and native Nutanix AOS snapshots.",
        "<b>Benchmarks</b> of I/O performance and of backup and restore times, run on both architectures.",
        "A <b>5-year TCO analysis</b>, and architecture recommendations presented to the CBI.MA teams.",
    ]))}

{sec("Stack", chips(["VMware ESXi 8.0", "vSphere", "TrueNAS Core", "ZFS RAID-Z1", "iSCSI", "NFS", "Nutanix CE", "Prism Element", "Nutanix AOS", "Veeam Backup & Replication"]))}

{sec("Outcome", '        <p class="lead-p">Recommendations delivered to CBI.MA, backed by benchmark results and a 5-year cost comparison.</p>')}

{case_nav("Next", "/lab/", "RocmineLabs")}

  </main>'''
    return page("/work/datacenter-hci/", "Datacenter: 3-Tier vs HCI — ROCMINE",
                "Case study: final-year project at CBI.MA comparing 3-Tier (VMware ESXi, TrueNAS) and hyperconverged (Nutanix) datacenter architectures with Veeam data protection, benchmarks and 5-year TCO.",
                body, active="work", og_type="article")


# ═══════════════════════════════════════════════════════════════════════════
#  LAB
# ═══════════════════════════════════════════════════════════════════════════
def lab():
    hw = f'''        <div class="hw-grid">
          <figure class="hw-item">
            <div class="diagram-wrap">
            {hw_r630()}
            </div>
            <figcaption><b>Dell PowerEdge R630</b> · 1U rack server</figcaption>
          </figure>
          <figure class="hw-item">
            <div class="hw-tower">
            {hw_t5820()}
            </div>
            <figcaption><b>Dell Precision T5820</b> · tower</figcaption>
          </figure>
        </div>
        <p class="diagram-note">Front panels are illustrations, not photos.</p>'''
    body = f'''  <main id="main" class="page">

{head_block(crumb_trail((None, "lab")), "RocmineLabs",
            "My home datacenter: two enterprise-class servers running multi-node virtualisation, close enough to production to practise on real operations.")}

{sec("Hardware", hw, wide=True)}

{sec("Topology", '''        <div class="diagram-wrap">
        ''' + diagram_lab() + '''
        </div>''', wide=True)}

{sec("What runs here", points([
        "Multi-node virtualisation with <b>Proxmox VE</b>: web services, monitoring tools and game servers (Minecraft, CS2, FiveM).",
        "<b>Local LLMs</b> with Ollama, and experiments with AI agents connected to tools through <b>MCP</b>.",
        "An <b>Nginx</b> reverse proxy with load balancing, behind <b>Cloudflare</b> protection.",
        "Full <b>Linux</b> administration: network configuration, access management, backups, and hardening of exposed services.",
        'It hosted the <a href="/work/earthquake-tracker/">Morocco Earthquake Tracker</a> through more than 10 million visits, without interruption.',
    ]))}

{case_nav("Next", "/about/", "About me")}

  </main>'''
    return page("/lab/", "RocmineLabs — ROCMINE",
                "RocmineLabs: a home datacenter with Dell PowerEdge R630 and Precision T5820 servers running Proxmox VE, Nginx, Cloudflare, local LLMs with Ollama and MCP agents.",
                body, active="lab")


# ═══════════════════════════════════════════════════════════════════════════
#  ABOUT
# ═══════════════════════════════════════════════════════════════════════════
def tl(num, date, role, org, bullets=None, link=None):
    b = ""
    if bullets:
        b = '\n            <div class="tl-body">' + points(bullets).replace("        <ul", "<ul") + "</div>"
    if link:
        b += f'\n            <p class="tl-body"><a class="link-btn" href="{link[0]}">{esc(link[1])}</a></p>'
    return f'''          <li>
            <span class="tl-num">{num}</span>
            <span class="tl-date">{date}</span>
            <div class="tl-main">
              <p class="tl-role">{role}</p>
              <p class="tl-org">{org}</p>{b}
            </div>
          </li>'''


def skill_group(sid, name, items):
    return f'''        <div class="skill-group" id="{sid}">
          <h3>{esc(name)}</h3>
{chips(items)}
        </div>'''


def about():
    timeline = '        <ol class="timeline">\n' + "\n".join([
        tl("01", "2025 – 2026", "Final-year project intern: datacenter architectures (3-Tier vs HCI) and data protection", "CBI.MA",
           ["Final-year project at CBI.MA, an integrator specialised in datacenter, cloud and cybersecurity infrastructure.",
            "Designed and deployed a 3-Tier mock-up: VMware ESXi 8.0, TrueNAS Core storage (ZFS RAID-Z1, iSCSI/NFS LUNs).",
            "Deployed a hyperconverged architecture on Nutanix Community Edition (Prism Element cluster).",
            "Set up data protection with Veeam Backup &amp; Replication, including native Nutanix AOS snapshots.",
            "Benchmarked I/O and backup/restore, analysed 5-year TCO and presented recommendations to the CBI.MA teams."],
           ("/work/datacenter-hci/", "Read the case study")),
        tl("02", "2025", "Intern: audit management application (IMANOR)", "CEDAMUS IT",
           ["Built an audit management application (agent checklist): database modelling, back-end API and user interface, in Java and MySQL."]),
        tl("03", "2024", "Intern: AI application", "Trésorerie Générale du Royaume",
           ["Built an AI application that predicts a company's upcoming financial direct debits.",
            "Set up the server environment and deployed the application."]),
        tl("04", "2024", "Developer helper", "Eghata.ma",
           ["Collected and structured geographic data for the Google Maps mapping of the Al Haouz earthquake."]),
    ]) + "\n        </ol>"

    skills = '        <div class="skill-groups">\n' + "\n".join([
        skill_group("skills-ai", "Generative AI & agents",
                    ["LLM APIs: OpenAI, Claude, Mistral", "Prompt engineering", "RAG", "LangChain", "LlamaIndex",
                     "Vector databases (Chroma)", "Local LLMs (Ollama)", "AI agents & MCP", "AI coding assistants"]),
        skill_group("skills-cloud", "Cloud & DevOps",
                    ["GCP", "AWS", "Azure", "Docker", "Kubernetes", "Terraform", "Ansible", "GitHub Actions",
                     "GitLab CI", "Git / GitHub", "Automation scripting"]),
        skill_group("skills-datacenter", "Virtualisation & datacenter",
                    ["VMware ESXi (vSphere)", "Nutanix (HCI, Prism Element)", "Proxmox VE", "Infrastructure sizing & mock-ups"]),
        skill_group("skills-storage", "Storage & backup",
                    ["SAN / NAS", "iSCSI", "NFS", "TrueNAS Core (ZFS, RAID-Z)", "Veeam Backup & Replication",
                     "Snapshots", "Disaster recovery planning"]),
        skill_group("skills-systems", "Systems, networks & security",
                    ["Linux (Debian / Ubuntu)", "Windows Server", "IP addressing", "VLAN",
                     "Nginx (reverse proxy, load balancing)", "Cloudflare", "Server hardening",
                     "Ethical-hacking basics", "Monitoring", "High availability"]),
        skill_group("skills-dev", "Development",
                    ["Python (FastAPI, Flask)", "C", "C++", "C#", "Java", "JavaScript / React", ".NET",
                     "SQL (MySQL, PostgreSQL)", "MongoDB"]),
    ]) + "\n        </div>"

    certs = '''        <ul class="dl-simple">
          <li>Meta <span>React Basics / Native</span></li>
          <li>Google <span>Introduction to Git and GitHub</span></li>
          <li>University of Pennsylvania (Coursera) <span>Introduction to Java and Object-Oriented Programming</span></li>
          <li>HKUST (Coursera) <span>Software Engineering: Software Design and Project Management</span></li>
          <li>University of Michigan (Coursera) <span>Programming for Everybody (Python); HTML, CSS, and JavaScript for Web Developers</span></li>
        </ul>'''
    edu = '''        <ul class="dl-simple">
          <li>State Engineer in Computer Science &amp; Networks, MIAGE option <span>École Marocaine des Sciences d'Ingénieur, Rabat · 2021 – 2026</span></li>
          <li>Baccalauréat, Mathematical Sciences A <span>Établissement Scolaire Al Jaouzia, Temara · 2020 – 2021</span></li>
        </ul>'''
    beyond = '''        <ul class="dl-simple">
          <li>GDSC (Google Developer Student Club) <span>Media, design &amp; production lead · 2023 – 2024</span></li>
          <li>Hult Prize <span>Social media coordinator · 2023</span></li>
          <li>Nexus AI Club, EMSI <span>Member · 2024</span></li>
          <li>Innovation Club <span>Member · 2026</span></li>
        </ul>'''
    contact = f'''        <p class="lead-p">Open to opportunities in AI, cloud and infrastructure. My CV is available on request.</p>
        <p><a class="btn" href="mailto:{EMAIL}?subject=CV%20request">Ask for my CV</a></p>
        <dl class="kv">
          <dt>Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd>
          <dt>GitHub</dt><dd><a href="https://github.com/Rocmine" target="_blank" rel="noopener noreferrer">github.com/Rocmine</a></dd>
          <dt>LinkedIn</dt><dd><a href="https://linkedin.com/in/rocmine" target="_blank" rel="noopener noreferrer">linkedin.com/in/rocmine</a></dd>
        </dl>'''
    profile = '''        <div class="prose">
          <p>I'm a State Engineer in Computer Science and Networks (MIAGE option), graduated from the École Marocaine des Sciences d'Ingénieur in Rabat, with a hybrid profile across generative AI, cloud and infrastructure.</p>
          <p>I design LLM-based applications (OpenAI, Claude and Mistral APIs, RAG, AI agents and MCP), and I'm comfortable with the chain that takes them to production: public cloud (GCP, AWS, Azure), containers and orchestration, Infrastructure as Code and CI/CD.</p>
          <p>My final-year project at CBI.MA compared 3-Tier and hyperconverged datacenter architectures. Alongside it, my homelab runs local LLMs, web services, and a site that passed 10 million visits.</p>
        </div>'''
    body = f'''  <main id="main" class="page">

{head_block(crumb_trail((None, "about")), "About", "State Engineer in Computer Science and Networks, EMSI Rabat, class of 2026.")}

{sec("Profile", profile)}

{sec("Experience", timeline)}

{sec("Skills", skills, sid="skills")}

{sec("Education", edu)}

{sec("Certifications", certs)}

{sec("Languages", '        <p class="lead-p">Arabic B2 · French B2 · English B2</p>')}

{sec("Beyond the code", beyond + '''
        <p class="lead-p muted">Interests: homelab and self-hosting, generative AI and local LLMs, gaming and streaming (CS2, Valorant), video editing and animation.</p>''')}

{sec("Contact", contact)}

  </main>'''
    return page("/about/", "About — ROCMINE",
                "Rochdi Mohamed Amine: State Engineer in computer science and networks (EMSI Rabat, 2026). Experience at CBI.MA, CEDAMUS IT and the Trésorerie Générale du Royaume; skills in generative AI, cloud, DevOps and datacenter infrastructure.",
                body, active="about")


# ═══════════════════════════════════════════════════════════════════════════
#  404
# ═══════════════════════════════════════════════════════════════════════════
def notfound():
    body = '''  <main id="main" class="page">
    <div class="nf rail">
      <p class="crumb reveal d-1"><span class="role-prompt">~/</span>route not found<span class="cursor" aria-hidden="true"></span></p>
      <h1 class="nf-code reveal d-2">404</h1>
      <p class="page-lede reveal d-3">Nothing lives at this address. It may have moved, or the link is wrong.</p>
      <p class="nf-links reveal d-4">
        <a class="link-btn" href="/">home</a>
        <a class="link-btn" href="/work/">work</a>
        <a class="link-btn" href="/about/">about</a>
      </p>
    </div>
  </main>'''
    return page("/404.html", "404 — ROCMINE", "Page not found.", body, noindex=True)


# ═══════════════════════════════════════════════════════════════════════════
def main():
    write_thumbs()
    write("index.html", home())
    write("work/index.html", work())
    write("work/earthquake-tracker/index.html", quake())
    write("work/datacenter-hci/index.html", datacenter())
    write("lab/index.html", lab())
    write("about/index.html", about())
    write("404.html", notfound())
    urls = ["/", "/work/", "/work/earthquake-tracker/", "/work/datacenter-hci/", "/lab/", "/about/"]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"  <url><loc>{SITE}{u}</loc><lastmod>2026-10-04</lastmod></url>\n" for u in urls) + "</urlset>\n"
    write("sitemap.xml", sm)
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    print("built", len(urls) + 1, "pages")


if __name__ == "__main__":
    main()
