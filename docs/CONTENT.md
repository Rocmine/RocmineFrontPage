# Editing content

After any change run `python tools/build.py` and commit the sources plus the generated files.

| To change | Edit |
|---|---|
| Home tagline, role line, ticker, specialties, stats | `src/content/site.json` |
| Work list and "Other projects" | `src/content/projects.json` (`href` makes a row a link, `thumb` is a file in `assets/img/work/`) |
| Experience timeline | `src/content/experience.json` (bullets are HTML: write `&amp;` for &) |
| Skill groups and "used in" links | `src/content/skills.json` |
| Stack page groups | `src/content/stack.json` (`_confirm` lists items that rest on local files only) |
| Share-card text | `src/content/cards.json`, then `python tools/make_assets.py cards` |
| GitHub numbers on /stack/ | `python tools/fetch_github.py` (writes `src/content/github.json`) |
| Case-study prose, lab and about text | `tools/sitegen/pages.py` |
| Styles | `src/css/*.css` (never edit `assets/css/main.css`) |
| Behaviour | `src/js/*.js` (never edit `assets/js/main.js`) |

Rules for public content: English, email as the only contact, no CV file, and nothing that is not in the CV, your repos or your own words.

## Adding a page

1. Write a builder function in `tools/sitegen/pages.py` (copy `stack()` as a model).
2. Register it in `PAGES` in `tools/sitegen/build.py`; it is added to the sitemap automatically.
3. Add a card to `src/content/cards.json` and run `python tools/make_assets.py cards`.
4. Add it to `NAV` in `tools/sitegen/layout.py` if it belongs in the menu.
