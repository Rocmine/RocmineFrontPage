"""Page bodies."""
import json

from .config import SITE, EMAIL, esc, load
from .svg import diagram_quake, diagram_dc, diagram_lab, hw_r630, hw_t5820
from .icons import svg as icon_svg, group_icon
from .layout import (page, head_block, sec, points, chips, chips_links, crumb_trail, ld_script, breadcrumb_ld,
                     article_ld, PERSON_ID)


# ═══════════════════════════════════════════════════════════════════════════
#  HOME
# ═══════════════════════════════════════════════════════════════════════════
SITE_DATA = load("site")
TICKER = SITE_DATA["ticker"]


def letters(word, start):
    """One span per letter (index --i drives the staggered title animation)."""
    return "".join(f'<span class="ch" style="--i:{start + i}">{c}</span>' for i, c in enumerate(word))


def home():
    sep = " &nbsp;·&nbsp; "
    # one copy = every item plus a trailing separator, so the rhythm is identical at the loop point
    copy = sep.join(TICKER) + sep
    TICKER_COPIES = 6
    ticker_copies = "".join(
        f'          <span class="ticker-items"' + ("" if i == 0 else ' aria-hidden="true"') + f'>{copy}</span>{chr(10)}'
        for i in range(TICKER_COPIES)).rstrip()
    specialties = "\n".join(
        f'        <li><a href="{x["href"]}"><span class="spec-num">{x["num"]}</span>{esc(x["label"])}</a></li>'
        for x in SITE_DATA["specialties"])
    stats = '\n        <span class="stat-sep" aria-hidden="true">·</span>\n'.join(
        f'        <span class="stat"><span class="stat-key">{esc(x["key"])}</span><span class="stat-val">{esc(x["val"])}</span></span>'
        for x in SITE_DATA["stats"])
    person = {
        "@type": "Person",
        "@id": PERSON_ID,
        "name": "Rochdi Mohamed Amine",
        "alternateName": ["Mohamed Amine Rochdi", "ROCMINE"],
        "jobTitle": "Linux & Infrastructure Engineer",
        "url": SITE + "/",
        "email": "mailto:" + EMAIL,
        "image": SITE + "/assets/img/cards/home.jpg",
        "address": {"@type": "PostalAddress", "addressCountry": "MA", "addressLocality": "Rabat"},
        "alumniOf": "École Marocaine des Sciences d'Ingénieur",
        "knowsAbout": ["Linux", "Docker", "Linux servers", "Datacenter infrastructure", "Virtualisation", "NVIDIA CUDA", "Local LLMs"],
        "sameAs": ["https://github.com/Rocmine", "https://linkedin.com/in/rocmine"],
    }
    website = {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "ROCMINE",
               "inLanguage": "en", "publisher": {"@id": PERSON_ID}}
    graph = {"@context": "https://schema.org", "@graph": [person, website]}
    body = f'''  <main id="main" class="main-home">

    <div id="portrait-bg" aria-hidden="true"></div>

    <h1 class="sr-only">Rochdi Mohamed Amine, Linux, Docker and infrastructure engineer</h1>

    <div class="left-col">

      <p class="role-line reveal d-1" aria-label="Role: Linux, Docker and infrastructure engineer">
        <span class="role-prompt">~/</span><span class="role-text"> {SITE_DATA["role"]}</span><span class="cursor" aria-hidden="true"></span>
      </p>

      <div class="name-block rail" translate="no">
        <span class="name-line" aria-hidden="true">{letters("ROCHDI", 0)}</span>
        <span class="name-line" aria-hidden="true">{letters("MOHAMED", 6)}</span>
        <span class="name-line" aria-hidden="true">{letters("AMINE", 13)}</span>
        <p class="name-tagline reveal d-5">{SITE_DATA["tagline"]}</p>
      </div>

      <p class="hero-cta reveal d-6">
        <a class="btn" href="/work/">See my work</a>
        <a class="btn btn-ghost" id="cta-email" href="mailto:{EMAIL}" data-email="{EMAIL}">Email me</a>
      </p>

      <ol class="specialties reveal d-7" aria-label="Areas of expertise">
{specialties}
      </ol>

      <div class="name-stats reveal d-8">
{stats}
      </div>

    </div>

    <span id="edge-label" aria-hidden="true">ROCMINE.NET · PORTFOLIO · 2026</span>

    <p class="stack-ticker reveal d-7" aria-label="Tech stack: {', '.join(t.title() for t in TICKER)}">
      <span class="ticker-label">STACK</span>
      <span class="ticker-rule">──</span>
      <span class="ticker-body">
        <span class="ticker-run" style="--n:{TICKER_COPIES}">
{ticker_copies}
        </span>
      </span>
    </p>

  </main>'''
    extra = ld_script(graph)
    return page("/", "ROCMINE — Rochdi Mohamed Amine · Linux, Docker & infrastructure engineer",
                "Rochdi Mohamed Amine (ROCMINE): State Engineer in computer science and networks. Linux servers, Docker, datacenter infrastructure and local LLMs on GPUs. Based in Rabat, Morocco.",
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
    projects = load("projects")
    rows = "\n".join(
        work_row(p["num"], p["title"], p["stack"], p["meta"], p.get("href"), p.get("thumb"))
        for p in projects["selected"])
    others = [(o["name"], o.get("url")) for o in projects["other"]]
    other_html = "\n".join(
        f'          <li><a href="{u}" target="_blank" rel="noopener noreferrer">{esc(n)}</a></li>' if u
        else f"          <li>{esc(n)}</li>" for n, u in others)
    body = f'''  <main id="main" class="page">

{head_block(crumb_trail((None, "work")), "Work", "Linux, Docker and infrastructure projects, from a datacenter study to a site that passed 10 million visits.")}

    <ol class="work-list">
{rows}
    </ol>

{sec("Other projects", f'        <ul class="other-list">{chr(10)}{other_html}{chr(10)}        </ul>')}

  </main>'''
    return page("/work/", "Work — ROCMINE",
                "Selected projects by Rochdi Mohamed Amine: the Morocco Earthquake Tracker, a 3-Tier vs HCI datacenter study at CBI.MA, the RocmineLabs homelab, Safar AI and Metascope.",
                body, active="work", extra_head=ld_script(breadcrumb_ld(("Work", "/work/"))))


SK_DEV, SK_SYS, SK_DC, SK_ST = ("/about/#skills-dev", "/about/#skills-systems", "/about/#skills-datacenter", "/about/#skills-storage")


def case_ld(title, desc, path, name):
    return ld_script(article_ld(title, desc, path)) + ld_script(breadcrumb_ld(("Work", "/work/"), (name, path)))


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

{sec("Approach", points([
        "An <b>Express.js</b> back end exposing a REST API, backed by <b>MySQL / MariaDB</b>.",
        "<b>Nginx</b> as reverse proxy, load-balancing traffic across the application instances.",
        "<b>Cloudflare</b> in front of the origin for protection against abusive traffic.",
        "Self-hosting on <a href=\"/lab/\">RocmineLabs</a>, my homelab: Dell enterprise servers running Proxmox VE.",
    ]))}

{sec("Skills used", chips_links([("Express.js", SK_DEV), ("REST API", SK_DEV), ("Nginx", SK_SYS), ("Load balancing", SK_SYS), ("Cloudflare", SK_SYS), ("MySQL", SK_DEV), ("MariaDB", SK_DEV), ("Proxmox VE", SK_DC), ("Linux", SK_SYS)]))}

{sec("Result", '        <p class="lead-p">More than 10 million visits, served from a home datacenter with no interruption.</p>')}

{case_nav("Next project", "/work/datacenter-hci/", "Datacenter: 3-Tier vs HCI")}

  </main>'''
    return page("/work/earthquake-tracker/", "Morocco Earthquake Tracker — ROCMINE",
                "Case study: a public earthquake tracker for Morocco on Express.js, Nginx load balancing and Cloudflare, self-hosted on a Proxmox homelab, with more than 10 million visits.",
                body, active="work", og_type="article",
                extra_head=case_ld("Morocco Earthquake Tracker", "Case study: a public earthquake tracker for Morocco, self-hosted with Nginx load balancing and Cloudflare, with more than 10 million visits.", "/work/earthquake-tracker/", "Morocco Earthquake Tracker"))


def datacenter():
    body = f'''  <main id="main" class="page">

{head_block(crumb_trail(("/work/", "work"), (None, "datacenter-hci")), "Datacenter: 3-Tier vs HCI",
            "My final-year project at CBI.MA: two ways to build a datacenter, compared on a working mock-up with data protection on top.",
            long=True, meta=[("Where", "CBI.MA"), ("When", "2025 – 2026"), ("School", "EMSI, Rabat")])}

{sec("Problem", '''        <div class="prose">
          <p>CBI.MA is an integrator specialised in datacenter, cloud and cybersecurity infrastructure: 55 years in business, 300+ people, 13 African countries.</p>
          <p>The question: should a customer build on the classic 3-Tier architecture (separate compute, network and storage) or on hyperconverged infrastructure (HCI), where the same nodes provide both? I built both and measured them.</p>
        </div>''')}

{sec("Architecture", '''        <div class="diagram-wrap">
        ''' + diagram_dc() + '''
        </div>
        <p class="diagram-note">Simplified view of the two mock-ups and the shared backup layer.</p>''', wide=True)}

{sec("Approach", points([
        "A <b>3-Tier mock-up</b>: VMware ESXi 8.0 hypervisor, with SAN/NAS storage on TrueNAS Core (ZFS pool in RAID-Z1, iSCSI and NFS LUNs).",
        "A <b>hyperconverged architecture</b> on Nutanix Community Edition, managed through a Prism Element cluster.",
        "<b>Data protection</b> with Veeam Backup &amp; Replication: full and incremental backups, restores, and native Nutanix AOS snapshots.",
        "<b>Benchmarks</b> of I/O performance and of backup and restore times, run on both architectures.",
        "A <b>5-year TCO analysis</b>, and architecture recommendations presented to the CBI.MA teams.",
    ]))}

{sec("Skills used", chips_links([("VMware ESXi 8.0", SK_DC), ("vSphere", SK_DC), ("TrueNAS Core", SK_ST), ("ZFS RAID-Z1", SK_ST), ("iSCSI", SK_ST), ("NFS", SK_ST), ("Nutanix CE", SK_DC), ("Prism Element", SK_DC), ("Nutanix AOS", SK_DC), ("Veeam Backup & Replication", SK_ST)]))}

{sec("Result", '        <p class="lead-p">Recommendations delivered to CBI.MA, backed by benchmark results and a 5-year cost comparison.</p>')}

{case_nav("Next", "/lab/", "RocmineLabs")}

  </main>'''
    return page("/work/datacenter-hci/", "Datacenter: 3-Tier vs HCI — ROCMINE",
                "Case study: final-year project at CBI.MA comparing 3-Tier (VMware ESXi, TrueNAS) and hyperconverged (Nutanix) datacenter architectures with Veeam data protection, benchmarks and 5-year TCO.",
                body, active="work", og_type="article",
                extra_head=case_ld("Datacenter: 3-Tier vs HCI", "Final-year project at CBI.MA comparing 3-Tier and hyperconverged datacenter architectures.", "/work/datacenter-hci/", "Datacenter: 3-Tier vs HCI"))


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
        "<b>Local LLMs</b> on NVIDIA GPUs, run in <b>Docker</b> (CUDA, Ollama), and experiments with agents connected to tools through <b>MCP</b>.",
        "An <b>Nginx</b> reverse proxy with load balancing, behind <b>Cloudflare</b> protection.",
        "Full <b>Linux</b> administration: network configuration, access management, backups, and hardening of exposed services.",
        'It hosted the <a href="/work/earthquake-tracker/">Morocco Earthquake Tracker</a> through more than 10 million visits, without interruption.',
    ]))}

{case_nav("Next", "/about/", "About me")}

  </main>'''
    return page("/lab/", "RocmineLabs — ROCMINE",
                "RocmineLabs: a home datacenter with Dell PowerEdge R630 and Precision T5820 servers running Proxmox VE, Docker, Nginx, Cloudflare and local LLMs on NVIDIA GPUs.",
                body, active="lab", extra_head=ld_script(breadcrumb_ld(("Lab", "/lab/"))))


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


def skill_group(sid, name, items, used_in=None):
    used = ""
    if used_in:
        links = " · ".join(f'<a href="{u["href"]}">{esc(u["label"])}</a>' for u in used_in)
        used = f'\n          <p class="used-in">Used in: {links}</p>'
    return f'''        <div class="skill-group" id="{sid}">
          <h3>{icon_svg(group_icon(sid))}{esc(name)}</h3>
{chips(items, sid)}{used}
        </div>'''


def about():
    timeline = '        <ol class="timeline">\n' + "\n".join(
        tl(x["num"], x["date"], x["role"], x["org"], x.get("bullets"),
           (x["link"]["href"], x["link"]["label"]) if x.get("link") else None)
        for x in load("experience")["items"]) + "\n        </ol>"

    skills = '        <div class="skill-groups">\n' + "\n".join(
        skill_group(g["id"], g["name"], g["items"], g.get("used_in")) for g in load("skills")["groups"]) + "\n        </div>"

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
    contact = f'''        <p class="lead-p">Open to opportunities in Linux, Docker and infrastructure. My CV is available on request.</p>
        <p><a class="btn" href="mailto:{EMAIL}?subject=CV%20request">Ask for my CV</a></p>
        <dl class="kv">
          <dt>Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd>
          <dt>GitHub</dt><dd><a href="https://github.com/Rocmine" target="_blank" rel="noopener noreferrer">github.com/Rocmine</a></dd>
          <dt>LinkedIn</dt><dd><a href="https://linkedin.com/in/rocmine" target="_blank" rel="noopener noreferrer">linkedin.com/in/rocmine</a></dd>
        </dl>'''
    profile = '''        <div class="prose">
          <p>I'm a State Engineer in Computer Science and Networks (MIAGE option), graduated from the École Marocaine des Sciences d'Ingénieur in Rabat. I work mostly with Linux servers and Docker.</p>
          <p>I build, host and look after services from my own home datacenter: Proxmox, Nginx behind Cloudflare, backups and hardening. It hosted a site that passed 10 million visits without interruption.</p>
          <p>I also run local LLMs on NVIDIA GPUs in Docker (CUDA, Ollama), and I like taking hardware and firmware apart: router firmware, a phone's OS, custom Windows installs.</p>
          <p>My final-year project at CBI.MA compared 3-Tier and hyperconverged datacenter architectures (VMware ESXi, TrueNAS, Nutanix, Veeam).</p>
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
        <p class="lead-p muted">Interests: homelab and self-hosting, local LLMs and GPUs, DIY and modding, gaming and streaming (CS2, Valorant), video editing and animation.</p>''')}

{sec("Contact", contact)}

  </main>'''
    return page("/about/", "About — ROCMINE",
                "Rochdi Mohamed Amine: State Engineer in computer science and networks (EMSI Rabat, 2026). Experience at CBI.MA, CEDAMUS IT and the Trésorerie Générale du Royaume; skills in Linux servers, Docker, datacenter infrastructure, NVIDIA GPUs and local LLMs.",
                body, active="about", extra_head=ld_script({
                    "@context": "https://schema.org", "@type": "ProfilePage", "url": SITE + "/about/", "name": "About",
                    "mainEntity": {"@type": "Person", "@id": PERSON_ID, "name": "Rochdi Mohamed Amine",
                                   "jobTitle": "Linux & Infrastructure Engineer",
                                   "sameAs": ["https://github.com/Rocmine", "https://linkedin.com/in/rocmine"]}}) +
                    ld_script(breadcrumb_ld(("About", "/about/"))))


# ═══════════════════════════════════════════════════════════════════════════
#  STACK
# ═══════════════════════════════════════════════════════════════════════════
def stack():
    data = load("stack")
    gh = load("github")
    groups = []
    for g in data["groups"]:
        inner = chips(g["items"])
        if g.get("link"):
            inner += f'{chr(10)}        <p class="used-in"><a href="{g["link"]["href"]}">{esc(g["link"]["label"])}</a></p>'
        groups.append(sec(g["name"], inner))
    langs = " · ".join(esc(l["name"]) for l in gh["languages"])
    github = f'''        <dl class="kv">
          <dt>Account</dt><dd><a href="https://github.com/{gh["login"]}" target="_blank" rel="noopener noreferrer">github.com/{esc(gh["login"])}</a>, since {gh["since"]}</dd>
          <dt>Repos</dt><dd>{gh["public_repos"]} public ({gh["own_repos"]} of my own, {gh["forks"]} forks)</dd>
          <dt>Languages</dt><dd>{langs}</dd>
        </dl>
        <p class="diagram-note">Snapshot from the public GitHub API, {esc(gh["fetched"])}.</p>'''
    body = f'''  <main id="main" class="page">

{head_block(crumb_trail((None, "stack")), "Stack", data["lede"])}

{chr(10).join(groups)}

{sec("On GitHub", github)}

{case_nav("Next", "/about/", "About me")}

  </main>'''
    return page("/stack/", "Stack — ROCMINE",
                "The languages, tools and hardware behind Rochdi Mohamed Amine's work: Linux, Docker, GPUs and local LLMs, DevOps and a Proxmox homelab.",
                body, active="stack", extra_head=ld_script(breadcrumb_ld(("Stack", "/stack/"))))


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
        <a class="link-btn" href="/lab/">lab</a>
        <a class="link-btn" href="/stack/">stack</a>
        <a class="link-btn" href="/about/">about</a>
      </p>
    </div>
  </main>'''
    return page("/404.html", "404 — ROCMINE", "Page not found.", body, noindex=True)


