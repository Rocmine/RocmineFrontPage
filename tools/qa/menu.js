/* Mobile hamburger menu test: phones only.
   node tools/qa/menu.js [--shots] */
const { chromium } = require('playwright');
const http = require('http'); const fs = require('fs'); const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..'); const SHOTS = process.argv.includes('--shots');
const T = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.webm': 'video/webm', '.mp4': 'video/mp4', '.woff2': 'font/woff2', '.ico': 'image/x-icon' };
const srv = http.createServer((q, r) => { let u = q.url.split('?')[0]; if (u.endsWith('/')) u += 'index.html'; const f = path.join(ROOT, u); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'Content-Type': T[path.extname(f)] || 'application/octet-stream' }); r.end(d); } }); });
let bad = 0; const ok = (n, c, x = '') => { console.log((c ? 'PASS ' : 'FAIL ') + n + (x ? '  ' + x : '')); if (!c) bad++; };

srv.listen(0, async () => {
  const base = 'http://localhost:' + srv.address().port;
  const b = await chromium.launch({ channel: 'msedge' });
  const st = p => p.evaluate(() => {
    const nav = document.getElementById('site-nav'), t = document.getElementById('nav-toggle');
    const links = [...nav.querySelectorAll('a')];
    return {
      expanded: t.getAttribute('aria-expanded'), label: t.getAttribute('aria-label'),
      toggleShown: getComputedStyle(t).display !== 'none',
      navVisible: getComputedStyle(nav).visibility === 'visible' && +getComputedStyle(nav).opacity > 0.9,
      navHidden: getComputedStyle(nav).visibility === 'hidden',
      focusOnFirst: document.activeElement === links[0], focusOnToggle: document.activeElement === t,
      minLinkH: Math.min(...links.map(a => a.getBoundingClientRect().height)), n: links.length,
      lock: document.documentElement.classList.contains('nav-lock'), path: location.pathname,
      noOverflow: document.documentElement.scrollWidth <= innerWidth,
    };
  });
  for (const [name, w, h] of [['phone-se', 320, 568], ['phone-390', 390, 844], ['fold-inner', 600, 960]]) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, hasTouch: true, isMobile: true, deviceScaleFactor: 2 });
    const p = await ctx.newPage(); const errs = [];
    p.on('console', m => m.type() === 'error' && errs.push(m.text())); p.on('pageerror', e => errs.push(e.message));
    await p.goto(base + '/about/', { waitUntil: 'networkidle' }); await p.waitForTimeout(400);
    let s = await st(p);
    ok(`${name}: closed at load (button shown, panel hidden)`, s.toggleShown && s.navHidden && s.expanded === 'false' && s.label === 'Menu');
    await p.tap('#nav-toggle'); await p.waitForTimeout(400); s = await st(p);
    ok(`${name}: tap opens (aria-expanded, panel visible, 4 links, scroll locked)`, s.expanded === 'true' && s.navVisible && s.n === 4 && s.lock && s.label === 'Close menu');
    ok(`${name}: focus moves to the first link`, s.focusOnFirst);
    ok(`${name}: links are at least 44px tall`, s.minLinkH >= 44, 'min=' + Math.round(s.minLinkH));
    if (SHOTS) { fs.mkdirSync(path.join(__dirname, 'shots'), { recursive: true }); await p.screenshot({ path: path.join(__dirname, 'shots', `menu-open-${name}.png`) }); }
    await p.keyboard.press('Escape'); await p.waitForTimeout(400); s = await st(p);
    ok(`${name}: Esc closes and returns focus to the button`, s.expanded === 'false' && s.navHidden && s.focusOnToggle && !s.lock);
    await p.tap('#nav-toggle'); await p.waitForTimeout(350);
    await p.touchscreen.tap(w / 2, h - 40); await p.waitForTimeout(350); s = await st(p);
    ok(`${name}: tap outside closes`, s.expanded === 'false' && s.navHidden);
    await p.tap('#nav-toggle'); await p.waitForTimeout(350);
    await Promise.all([p.waitForURL('**/work/'), p.tap('#site-nav a[href="/work/"]')]); await p.waitForLoadState('networkidle'); await p.waitForTimeout(300); s = await st(p);
    ok(`${name}: tapping a link navigates, menu closed on the new page`, s.path === '/work/' && s.expanded === 'false' && s.navHidden, s.path);
    ok(`${name}: no horizontal overflow`, s.noOverflow);
    ok(`${name}: no console errors`, errs.length === 0, errs.join('|'));
    if (w <= 400) {
      await p.tap('#nav-toggle'); await p.waitForTimeout(350);
      await p.setViewportSize({ width: 820, height: 1000 }); await p.waitForTimeout(400); s = await st(p);
      ok(`${name}: growing past 640px closes it and shows the inline nav`, !s.toggleShown && s.expanded === 'false' && !s.lock);
    }
    await ctx.close();
  }
  // motion switched off: still works
  { const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
    const p = await ctx.newPage(); await p.goto(base + '/', { waitUntil: 'networkidle' }); await p.evaluate(() => { document.documentElement.dataset.motion = 'reduced'; });
    await p.tap('#nav-toggle'); await p.waitForTimeout(300); const s = await st(p);
    ok('motion off: menu still opens', s.expanded === 'true' && s.navVisible); await ctx.close(); }
  // no JavaScript: links stay visible as a row, no dead button
  { const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, javaScriptEnabled: false });
    const p = await ctx.newPage(); await p.goto(base + '/', { waitUntil: 'load' }); await p.waitForTimeout(500);
    const r = await p.evaluate(() => ({ toggle: getComputedStyle(document.getElementById('nav-toggle')).display, nav: getComputedStyle(document.getElementById('site-nav')).visibility, pos: getComputedStyle(document.getElementById('site-nav')).position }));
    ok('no JS: nav links visible inline, no hamburger', r.toggle === 'none' && r.nav === 'visible' && r.pos !== 'absolute', JSON.stringify(r)); await ctx.close(); }
  await b.close(); srv.close(); process.exit(bad ? 1 : 0);
});
