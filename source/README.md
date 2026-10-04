# source/

Originals the site assets are derived from. Nothing here is loaded by the site, and `_config.yml` keeps this folder out of the published site.

| File | What it is | Used to make |
|---|---|---|
| `logo-spin-1080-alpha.webm` | 5 s spinning chrome "R", 1080x1080, **transparent background** (alpha in the WebM side channel) | `assets/video/logo-spin.*`, `assets/img/brand/logo-poster.png` |
| `logo-spin-1920x1080-alpha.webm` | Same animation, 1920x1080 frame | (spare) |
| `logo-render-1080p.jpg` | Still of the logo on the navy background | favicons, apple-touch icon, share card |
| `wallpaper-navy-2k.png` | Navy/violet gradient wallpaper | (spare) |
| `portrait-original-400.png` | Portrait, 400x400, very dark | `assets/img/portrait/portrait.png` (plain copy, no processing) |

Decode the alpha WebM with `-c:v libvpx-vp9` in ffmpeg; the default decoder ignores alpha and turns the glow white.
