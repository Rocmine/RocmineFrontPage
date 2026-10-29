# ROCMINE design style (instructions for me, Claude)

Read this before designing or building anything visual for Rochdi (UI, web pages, overlays, graphics, docs).
It describes the look of rocmine.net, which he loves: **"especially the font and the animation of the big title."**
The source of truth is the code in the `Rocmine/RocmineFrontPage` repo (`src/css/`, `src/js/`, `tools/`). When this file and that code disagree, the code wins; then fix this file.

> Reuse, don't reinvent. For a new project, start from the tokens and snippets below, keep the same type pairing and the same motion language, and change only what the new subject needs.

---

## 1. Who and what

- **Rochdi Mohamed Amine ("ROCMINE")**, State Engineer, Rabat, Morocco. **Linux servers and Docker first**, homelab (Proxmox, Nginx, Cloudflare), datacenter study (VMware, Nutanix, TrueNAS, Veeam), local LLMs on NVIDIA GPUs (CUDA, Ollama) in Docker, plus DIY, modding and hacking (router firmware, phone OS, custom Windows installs, hardware). He is **not** "mainly AI". Don't headline AI for him.
- Public content rules: **English**, **email as the only contact** (no phone, no birth date, no CV file), and **nothing invented**. Use only facts from his CV, his GitHub, or his own words. When unsure, leave it out or ask.
- Voice: plain, direct, specific. Short sentences. Active voice. Numerals for counts ("10 million visits"). No hype, no filler, no "passionate". Labels in a terminal flavour (`~/work`, `~/stack`, `linux · docker · infrastructure engineer`).

## 2. Principles

1. **Editorial / Swiss on dark navy.** Hairline rules, a label column beside a content column, generous space, one grid.
2. **One bold element per screen.** On the home page it is the huge name. Everything around it is quiet, small, monospaced.
3. **Structure is information.** Rules, rails, numbers and labels exist because they carry meaning. No decoration, no card kits, no shadows.
4. **Motion has a job.** One orchestrated load sequence, and motion that answers the user's action. No per-section fade-ups, no hover transitions on everything.
5. **Fluid first.** Sizes come from `clamp()`, container units and `svh`, not from a pile of breakpoints.
6. **Dark only.** The brand look is navy; don't add a light theme unless asked.

Avoid: cream/serif "editorial" looks, terracotta or acid-green accents, Inter/Roboto/Arial, rounded SaaS cards with soft shadows, gradient washes as decoration, glassmorphism, emoji as icons, all-caps eyebrows above every heading.

## 3. Tokens (copy exactly)

```css
:root {
  --bg:       #06060f;   /* page navy */
  --fg:       #ececf2;
  --accent:   #3b6dff;   /* the blue from the logo */
  --accent-2: #8a4dff;   /* violet, sampled from the logo */
  --accent-3: #ee1681;   /* magenta, sampled from the logo */
  --muted:    rgba(236,236,242,0.66);   /* secondary text   (>= 4.5:1) */
  --dim:      rgba(236,236,242,0.52);   /* tertiary / labels (>= 4.5:1) */
  --rule:     rgba(236,236,242,0.09);   /* hairlines */
  --body:     rgba(236,236,242,0.76);   /* paragraphs */
  --pad:      clamp(1.25rem, 3.5vw, 2.75rem);
  --ease:     cubic-bezier(0.22, 1, 0.36, 1);   /* the only easing curve */
}
html {
  background: radial-gradient(ellipse at 50% 30%, #0e0c1c 0%, var(--bg) 68%) fixed;
  background-color: var(--bg);
  color: var(--fg); color-scheme: dark; -webkit-font-smoothing: antialiased;
}
::selection { background: var(--accent-2); color: #fff; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
```

- Accent blue is for interaction and emphasis (numbers, prompts, underlines, buttons). Violet and magenta appear only in the **name rail gradient**, selection, the title **glint**, and diagram highlights.
- Status green `#4ade80` (badge only).
- **Grain**: one fixed, non-interactive layer: an inline SVG `feTurbulence` (baseFrequency .85, 4 octaves) at `opacity: .028`, `z-index: 0`, under the content.

## 4. Typography

Two families, clearly distinct:

| Role | Font | Use |
|---|---|---|
| Display | **Unbounded**, weight **900** | The name, page titles, big list titles, the logotype. **UPPERCASE**, `letter-spacing: -0.04em`, tight leading (`.88` for the name block, `.95` for page titles). |
| Everything else | **JetBrains Mono** 400/600/700 | Body, nav, labels, buttons, chips, stats. |

Scale and rules:

- Name: `clamp(2.4rem, min(8.2cqi, 15svh), 10rem)`. Page title: `clamp(2.3rem, 7.2vw, 6rem)`, case-study titles a bit smaller (`clamp(2rem, 5.2vw, 4.4rem)`).
- Body paragraph: `.82rem`, `line-height: 1.8`, color `--body`, `max-width: 64ch`.
- Micro labels (section labels, stat keys, nav): `.66-.74rem`, **uppercase**, `letter-spacing: .1-.2em`, color `--dim`/`--muted`.
- **No text under ~10.4px.** Hit areas: at least 24px, 44px on touch.
- Numbers in lists (`01`, `02`) only when the content is a real sequence or a specialties list, in `--accent`.
- `text-wrap: balance` on headings, `pretty` on paragraphs.

Self-host the fonts (no Google requests). Variable woff2, latin subset:

```css
@font-face { font-family:'Unbounded'; src:url('/assets/fonts/Unbounded-latin.woff2') format('woff2');
  font-weight:400 900; font-display:swap; }
@font-face { font-family:'JetBrains Mono'; src:url('/assets/fonts/JetBrainsMono-latin.woff2') format('woff2');
  font-weight:400 700; font-display:swap; }
```
```html
<link rel="preload" href="/assets/fonts/Unbounded-latin.woff2" as="font" type="font/woff2" crossorigin>
```
`tools/fetch_fonts.py` in the repo downloads them (Google Fonts CSS with a modern User-Agent, take the `latin` block).

## 5. Layout

- **Frame (every page):** header (logo clip, nav, status badge) / main / footer, each separated by a 1px `--rule` hairline. `#grid` is `container-type: inline-size`, `max-width: 140rem`, padding `max(var(--pad), env(safe-area-inset-*))`.
- **Home = poster.** Left column vertically centred: typed role line (`~/ linux · docker · infrastructure engineer▌`), the giant name with a **gradient rail** (2.5px bar, blue → violet → magenta, drawn with `scaleY` on load), tagline, two buttons, specialties row, stats row, ticker, footer. Photo on the right at 28% opacity, faded from the left with `mask-image: linear-gradient(to right, transparent, black 40%)`.
- **Inner pages:** `page-head` (crumb `~/work / …`, giant uppercase title with the rail, lede) then sections.
- **Section = label | content:** `grid-template-columns: minmax(8.5rem, 15rem) minmax(0, 1fr); gap: clamp(1rem,3vw,3rem); border-top: 1px solid var(--rule); padding-block: clamp(1.4rem,3.5vh,2.4rem)`. The label is a small uppercase `--dim` heading. Below 860px it stacks.
- **Large screens:** `html { font-size: clamp(16px, calc(.55vw + 5.5px), 24px) }` from 1920px up so the whole rem-based UI scales.
- **Phones:** the photo becomes a square band above the name with a `radial-gradient(closest-side, #000 52%, transparent)` mask; the header collapses to logo, status and a hamburger.

## 6. Components (all in `src/css/`)

- **Nav link:** uppercase `.68-.74rem`, `.12em` tracking, `--muted`; a 1px accent underline grows from 0 to 100% on hover and stays for `aria-current="page"`.
- **Status badge:** green dot with a slow pulse + `AVAILABLE`.
- **Button `.btn`:** 1px `--accent` border, mono uppercase `.72rem` `.12em`, transparent; hover fills accent. Ghost variant: border `rgba(236,236,242,.3)`.
- **Chips:** `1px solid var(--rule)`, `.68rem`, `--muted`; monochrome **icon** (14px, `currentColor`, `--dim`, accent on hover). Linked chips hover with a faint blue tint.
- **Work row:** number | big Unbounded title | meta | arrow, hairline between rows; a schematic thumbnail unfolds on hover/focus (`grid-template-rows: 0fr → 1fr`), always open on touch.
- **Timeline / key-value lists / "used in" lines:** small mono, hairline separators, accent numerals.
- **Toast:** small bordered mono pill, bottom centre, `role="status"`.
- **Diagrams:** inline SVG, 1px strokes in `rgba(236,236,242,.34)`; `core` nodes in accent, `hot` in magenta, dashed enclosures; mono text. They **draw themselves** once when scrolled into view (see motion). On phones they scroll sideways inside their own container.
- **Icons:** one SVG sprite (`assets/icons/sprite.svg`, Simple Icons CC0 + hand-drawn 24px line glyphs, `stroke-width 1.6`), used with `<svg class="ic" aria-hidden="true"><use href="/assets/icons/sprite.svg#docker"/></svg>`. Always monochrome (`currentColor`); never brand colours.

### Seamless ticker (marquee) recipe

Several identical copies side by side, each ending with the same separator, moving by exactly one copy:

```html
<span class="ticker-run" style="--n:6">
  <span class="ticker-items">LINUX · DOCKER · … · </span>  <!-- x6; copies 2-6 aria-hidden -->
</span>
```
```css
.ticker-run   { display:inline-flex; animation: ticker 40s linear infinite; }
.ticker-items { white-space:nowrap; }              /* no padding: the separator is the gap */
@keyframes ticker { to { transform: translateX(calc(-100% / var(--n, 6))); } }
```
Never use two copies and `-50%` with trailing padding: on wide screens a copy is shorter than the strip and a gap shows.

### Hamburger (phones only, <= 640px)

Button with three 1.5px bars that morph to an X (`top` + `rotate(±45deg)`, `.35s var(--ease)`); the links move into a panel under the header (solid `#07070f`, hairline border, 51px rows, accent bar on the current page). `aria-expanded`/`aria-controls`, closes on link, `Esc`, outside tap, focus leaving, or growing past 640px; focus goes to the first link, then back to the button; page scroll locked while open. Without JS the links stay a visible row (hidden state applies only under `.js`).

## 7. Motion

Language: one curve (`--ease`), 0.2-0.95s, transform and opacity only.

- **Page-load sequence:** `.reveal` (opacity 0, `translateY(10px)`, `0.5s var(--ease) forwards`) with delays `.04 .14 .22 .33 .44 .56 .68 .78 .88s` (`d-0 … d-8`). Rail: `scaleY 0 → 1` in `.55s` at `.22s`. Typewriter on the role line (34ms per character) with a blinking block cursor.
- **The big title** (the signature):
  1. Build time: split the name into `<span class="ch" style="--i:N">X</span>` (index continues across lines); the visible text is `aria-hidden`, an `sr-only` `<h1>` carries the real text.
  2. **Rise:** each letter rises out of its line mask: `translateY(112%) skewY(7deg)` to none, `.95s var(--ease)`, delay `.25s + i*38ms`.
  3. **Glint:** a colour wave runs through the letters every ~9s: `color` keyframes `fg → #a9c1ff → #c9a6ff → #ff9ccf → fg` inside the first 11% of a 9s loop, delay `3.2s + i*70ms`.
  4. **Pointer proximity (fine pointers):** letters within 150px of the cursor lift (`translate: 0 -0.09em`) and glow (`text-shadow` blue), driven by `--near` (0..1) set from JS in a `requestAnimationFrame` loop. Uses `translate`/`text-shadow` (not `transform`) so it never fights the animations. On touch, a tap sends one wave (Web Animations API, 26ms stagger).
  5. The line mask (`overflow:hidden`) is released with `.intro-done` after the last letter lands so lifted letters aren't clipped.

```css
.name-line .ch { display:inline-block;
  translate: 0 calc(var(--near,0) * -0.09em);
  text-shadow: 0 0 calc(var(--near,0) * .45em) rgba(59,109,255, calc(var(--near,0) * .95));
  transition: translate .22s var(--ease), text-shadow .22s var(--ease); }
html[data-motion="full"] .name-line .ch {
  animation: ch-rise .95s var(--ease) both, ch-glint 9s linear infinite;
  animation-delay: calc(.25s + var(--i) * 38ms), calc(3.2s + var(--i) * 70ms); }
@keyframes ch-rise  { from { transform: translateY(112%) skewY(7deg); opacity: 0 } to { transform: none; opacity: 1 } }
@keyframes ch-glint { 0%,11%,100% { color: var(--fg) } 3% { color:#a9c1ff } 6% { color:#c9a6ff } 8.5% { color:#ff9ccf } }
.name-block.intro-done > .name-line { overflow: visible; }
```
```js
// proximity: centers from offsetLeft/offsetTop (ignore transforms), t = smoothstep(1 - dist/150)
const t = Math.max(0, 1 - d / 150); el.style.setProperty('--near', (t*t*(3-2*t)).toFixed(3));
```
- **Diagram draw-on:** every shape has `pathLength="1"`; `.draw { stroke-dasharray:1; stroke-dashoffset:1 }` and, once an `IntersectionObserver` adds `.in`, `animation: draw 1.5s var(--ease) forwards` with per-shape `--d` delays; labels use a `fade`.
- **Motion switch (important):** **animation is on by default and ignores the OS "show animations" setting** (his Windows keeps turning it off, which silently killed everything). A tiny head script sets `html[data-motion]` to `full`, or `reduced` if `localStorage['rocmine-motion'] === 'off'`; the footer button `motion: on/off` toggles it and pauses the logo video. All motion CSS is under `html[data-motion="full"]` or reset by `html[data-motion="reduced"]`. Always offer this switch; never silently follow `prefers-reduced-motion` for this user unless he asks.

## 8. Responsive and accessibility rules

- Fluid sizes with `clamp()`, `cqi` (container) and `svh`; breakpoints only change structure: 360 (very narrow), 640 (phones: hamburger, band photo), 860 (sections stack), 1023 (tablet), 1600/1920 (large). Provide a `@supports not (width:1cqi)` fallback with `vw`.
- The home page must **scroll instead of clipping** when it doesn't fit; it stays a one-screen poster when it does.
- Touch (`pointer: coarse`): links and buttons >= 44px. Fine pointers: >= 24px. Inline links inside running text are exempt.
- Text >= ~10.4px, contrast >= 4.5:1, visible `:focus-visible`, a skip link, one `<h1>` per page, landmarks, `aria-current` on the active nav item, `alt` on images, decorative SVG `aria-hidden`.
- Support `prefers-contrast: more` and `forced-colors: active` (borders, focus, diagram strokes use system colours).
- Safe areas (`viewport-fit=cover`, `env(safe-area-inset-*)`), `dvh/svh`, `overflow-x: clip` on `body`.
- Custom cursor only for fine pointers.

## 9. Assets and build lessons

- **Logo clip with transparency:** the WebM has alpha in a side channel; ffmpeg's default VP9 decoder drops it and the glow turns **white**. Decode with `-c:v libvpx-vp9`, composite onto the exact page colour behind it (sample it from a screenshot: `--bg` plus the grain lifts it to `#090912` at the header corner), then encode an opaque WebM + MP4. Don't circle-crop a glowing logo.
- **Share cards** (1200x630, one per page): Pillow with the variable TTFs (`font.set_variation_by_axes([900])`), navy background, logo faded in with a radial mask, the rail, `~/path` in accent mono.
- Favicon set: `favicon.ico` (16/32/48), 32, 180 apple-touch, 192, 512, `site.webmanifest`, `theme-color #06060f`.
- Static site: generate pages from content JSON + small Python modules, commit the generated files, CSS split into ordered partials (`00-tokens` … `99-motion`) concatenated into one file with a hash for cache-busting. A `check.py` validates links, anchors, assets, meta, JSON-LD and a size budget; CI runs `build --check` and `check`.
- No third-party requests, no analytics unless asked.
- A photo that is very dark: use it exactly as shot at low opacity with the left gradient; don't "fix" it (he rejected lifting, tinting and vignettes).

## 10. Working agreements (how Rochdi likes me to work)

- Start non-trivial work in **plan mode**; ask only what you can't decide yourself.
- **Test proportionally.** Check only what the change touches (mobile change: phones only; ticker: wide screens only). Don't run exhaustive device matrices or other browser engines unless he asks. He finds that wasteful.
- Work in small commits; **never push without being asked**; say plainly what was and wasn't verified.
- Keep what he liked; when he gives feedback, change that and nothing else.

## 11. New-project checklist

1. Copy tokens (section 3) and the two `@font-face` rules; self-host the fonts.
2. Frame: header / main / footer with hairlines, `container-type: inline-size`, grain layer, radial background.
3. One bold display element in Unbounded 900 uppercase; everything else in JetBrains Mono small.
4. Gradient rail, label | content sections, chips, buttons, status badge as above.
5. Motion: load sequence, title recipe (if there is a big title), motion switch ignoring the OS setting.
6. Fluid sizing, 44px touch targets, hamburger under 640px, text >= 10.4px.
7. Content: English, plain, only true facts from him.
8. Check: no horizontal overflow, no console errors, links work, and review one screenshot at desktop and one at phone width.
