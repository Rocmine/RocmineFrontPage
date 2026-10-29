# Architecture

rocmine.net is a static site. GitHub Pages serves the files at the repo root; there is no build step on GitHub.
A small Python generator turns `src/` into those files, and the **generated files are committed**.

```
src/content/*.json   text and data (site, projects, experience, skills, stack, cards, github)
src/css/*.css        ordered partials (00-… to 99-…), concatenated into assets/css/main.css
src/js/*.js          concatenated into assets/js/main.js
tools/sitegen/       the generator: config, layout (head/header/footer), svg (diagrams), pages, build
tools/build.py       entry point (--check, --serve)
tools/make_assets.py logo video, icons, share cards, portrait   (from originals/)
tools/fetch_fonts.py self-hosted fonts (assets/fonts)
tools/fetch_github.py GitHub snapshot for /stack/ (src/content/github.json)
tools/check.py       static checks (links, anchors, assets, meta, JSON-LD, size budget)
tools/qa/            Playwright device matrix + animation test (dev only)
originals/           masters the assets are derived from (not published; see _config.yml)
```

## Build flow

1. `python tools/build.py` reads `src/`, writes every page, `assets/css/main.css`, `assets/js/main.js`,
   `sitemap.xml`, `robots.txt`, `site.webmanifest`, `humans.txt`, `.well-known/security.txt`.
2. CSS and JS get a content hash (`?v=…`) so browsers never keep a stale file.
3. `python tools/build.py --check` rebuilds into a temp folder and fails if anything differs from the repo.
4. Commit the sources **and** the generated files together.

## Design rules worth knowing

- **Dark only.** Tokens live in `src/css/00-tokens.css`; the accent is `#3b6dff`, violet and magenta come from the logo.
- **Fluid first.** Sizes use `clamp()`, container units (`cqi`) and `svh`; breakpoints in `90-responsive.css` only change structure.
  Above 1920px the root font size grows from 16px to 24px so the whole UI scales.
- **Animation is on by default** and ignores the OS "show animations" setting (Windows keeps turning it off).
  The footer `motion: on/off` switch sets `html[data-motion="reduced"]` and remembers it in `localStorage` (`rocmine-motion`).
  All motion CSS is scoped to `html[data-motion="full"]` or reset in `99-motion.css`.
- **No third-party requests.** Fonts are self-hosted; there is no analytics. `tools/check.py` fails on any.
- **Logo video** is pre-composited on the page colour (the source has transparency that ffmpeg's default decoder drops).
  See `originals/README.md`.
