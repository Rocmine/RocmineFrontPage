# RocmineFrontPage

Source of [rocmine.net](https://rocmine.net): a small static portfolio served by GitHub Pages.

The site is plain HTML, CSS and JS. The pages are generated from `src/` by a small Python script, and the **generated files are committed**, so GitHub Pages needs no build step.

```
src/            sources: content (JSON), css partials, js
tools/          build.py (generator), make_assets.py, fetch_fonts.py, fetch_github.py, check.py, qa/
originals/      masters the images and video are derived from (not published)
docs/           architecture, content guide, testing guide
-- generated and committed (do not edit by hand) --
index.html  404.html  about/ lab/ stack/ work/  assets/css/main.css  assets/js/main.js  sitemap.xml  robots.txt
-- static assets --
assets/img  assets/video  assets/cursor
```

## Everyday commands

```bash
python tools/build.py            # regenerate the site from src/
python tools/build.py --serve    # build, then preview on http://localhost:8080
python tools/build.py --check    # fail if the committed output is out of date (also run by CI)
python tools/check.py            # links, anchors, assets, meta tags, JSON-LD, size budget
```

Edit text in `src/content/*.json`, styles in `src/css/`, behaviour in `src/js/`, then rebuild. See `docs/` (`ARCHITECTURE.md`, `CONTENT.md`, `TESTING.md`) for details.

## Animation

Animations are on by default and ignore the OS "show animations" setting. The `motion: on/off` switch in the footer turns them off and remembers the choice (`localStorage` key `rocmine-motion`).
