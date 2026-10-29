"""Inline SVG diagrams, hardware drawings and work-list thumbnails."""
from .config import esc
from .layout import write


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
        write(f"assets/img/work/{name}.svg", wrap(body))


