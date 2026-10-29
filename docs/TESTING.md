# Testing

## Static checks (no setup)

```bash
python tools/build.py --check    # committed pages match src/
python tools/check.py            # links, anchors, assets, meta tags, JSON-LD, ids, alt text, size budget
```

Both run in CI (`.github/workflows/check.yml`).

## Device matrix (Playwright, local)

```bash
cd tools/qa
npm install
node matrix.js                      # 24 screen sizes x every page, in Microsoft Edge
node matrix.js --pages home --shots # home only, screenshots saved to tools/qa/shots/
node matrix.js --engine firefox     # chromium | msedge | firefox | webkit (needs: npx playwright install firefox webkit)
node title.js --shots               # name animation, pointer effect, motion switch
```

The matrix fails on horizontal overflow, overlapping blocks on the home page, the face being covered by the name,
text under 10.4px, links and buttons under 24px (44px on touch; inline links in running text are exempt, WCAG 2.2 2.5.8),
console errors, and the home page not fitting one screen on desktop sizes.

Screen sizes covered: 280px foldable cover, 320 to 430px phones, 600px foldable inner, tablets (portrait and landscape),
landscape phones, 1280 to 1920px laptops and desktops, 2560px, 3440px ultrawide, 3840px 4K, and 200% / 400% zoom.
