# RocmineFrontPage

Source of [rocmine.net](https://rocmine.net): a small static portfolio (plain HTML, CSS and JS) served by GitHub Pages.

```
index.html  404.html  robots.txt  sitemap.xml  CNAME  _config.yml
about/  lab/  work/            pages (generated, see below)
assets/
  css/main.css                 all styles
  js/main.js                   year, toast, email copy, typewriter, diagrams, motion switch
  img/brand/                   favicons, share card, logo poster
  img/portrait/                lit portrait for the home page
  img/work/                    thumbnails for the work list
  cursor/                      custom cursor
  video/                       header logo (webm + mp4)
source/                        originals the assets are derived from (not published)
tools/                         build_pages.py, make_assets.py (not published)
```

## Editing

- **Text and layout of pages:** edit `tools/build_pages.py`, then run `python tools/build_pages.py`. It rewrites the HTML pages, `sitemap.xml` and `robots.txt`.
- **Styles and behaviour:** edit `assets/css/main.css` and `assets/js/main.js` directly.
- **Derived images and video:** `python tools/make_assets.py` rebuilds the logo video, favicons, share card and portrait from `source/` (needs Pillow, numpy and ffmpeg; set `FFMPEG` if it is not on PATH).
- **Preview:** `python -m http.server 8080` from the repo root (pages use root-absolute paths), then open http://localhost:8080.

## Animation

Animations are on by default and ignore the OS "show animations" setting. The `motion: on/off` switch in the footer turns them off and remembers the choice (`localStorage`, key `rocmine-motion`).
