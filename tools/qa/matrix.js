/* Device matrix: loads every page at many screen sizes and reports layout problems.

   cd tools/qa && npm install
   npx playwright install firefox webkit        (once, for the other engines)
   node matrix.js                               Edge (default), all pages
   node matrix.js --engine firefox              chromium | msedge | firefox | webkit
   node matrix.js --pages home --shots          home only, save screenshots to tools/qa/shots/

   Failures: horizontal overflow, overlapping home blocks, text under 10.4px,
   links/buttons under 24px (44px on touch), console errors, home not fitting on desktop sizes. */
const { chromium, firefox, webkit } = require('playwright');
const http = require('http'); const fs = require('fs'); const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const args = process.argv.slice(2);
const opt = (n, d) => { const i = args.indexOf('--' + n); return i < 0 ? d : (args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true); };
const ENGINE = opt('engine', 'msedge'); const PAGES_OPT = opt('pages', 'all'); const SHOTS = !!opt('shots', false);

const PAGES = ['/', '/work/', '/work/earthquake-tracker/', '/work/datacenter-hci/', '/lab/', '/about/', '/stack/', '/404.html']
  .filter(p => fs.existsSync(path.join(ROOT, p.endsWith('/') ? p + 'index.html' : p)));
// name, width, height, deviceScaleFactor, touch
const VIEWPORTS = [
  ['fold-cover', 280, 653, 3, true], ['phone-se', 320, 568, 2, true], ['phone-360', 360, 640, 3, true], ['phone-375', 375, 667, 2, true],
  ['phone-390', 390, 844, 3, true], ['phone-430', 430, 932, 3, true], ['fold-inner', 600, 960, 2, true],
  ['tablet-768', 768, 1024, 2, true], ['tablet-820', 820, 1180, 2, true], ['tablet-1024p', 1024, 1366, 2, true],
  ['land-667', 667, 375, 2, true], ['land-844', 844, 390, 3, true], ['land-932', 932, 430, 3, true], ['tablet-1024', 1024, 768, 2, true],
  ['laptop-1280', 1280, 720, 1, false], ['laptop-1366', 1366, 768, 1, false], ['desk-1440', 1440, 900, 1, false],
  ['desk-1536', 1536, 864, 1, false], ['fhd-1920', 1920, 1080, 1, false], ['qhd-2560', 2560, 1440, 1, false],
  ['uw-3440', 3440, 1440, 1, false], ['uhd-3840', 3840, 2160, 1, false], ['zoom200', 640, 360, 2, false], ['zoom400', 320, 256, 2, false],
];
const TYPES = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.webm': 'video/webm', '.mp4': 'video/mp4', '.woff2': 'font/woff2', '.ico': 'image/x-icon', '.webp': 'image/webp', '.webmanifest': 'application/manifest+json', '.cur': 'image/x-icon', '.txt': 'text/plain', '.xml': 'text/xml' };

function serve() {
  return new Promise(res => {
    const s = http.createServer((q, r) => {
      let u = decodeURIComponent(q.url.split('?')[0]); if (u.endsWith('/')) u += 'index.html';
      const f = path.join(ROOT, u);
      fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' }); r.end(d); } });
    });
    s.listen(0, () => res(s));
  });
}

function inPage() {
  const vis = e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none'; };
  const hidden = e => !!e.closest('[aria-hidden="true"]');
  const de = document.documentElement;
  const out = { ox: de.scrollWidth > innerWidth + 1 };
  // text under 10.4px (skip aria-hidden decoration)
  const tiny = new Set();
  document.querySelectorAll('body *').forEach(e => {
    if (!vis(e) || hidden(e) || e.closest('svg')) return;
    if ([...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) && parseFloat(getComputedStyle(e).fontSize) < 10.4) tiny.add(e.className || e.tagName);
  });
  out.tiny = [...tiny].slice(0, 5);
  // link/button hit areas
  const min = matchMedia('(pointer: coarse)').matches ? 44 : 24;
  const small = [];
  document.querySelectorAll('a, button').forEach(e => {
    if (!vis(e) || e.classList.contains('skip')) return;
    // WCAG 2.2 (2.5.8) exempts links that sit inside running text
    if (getComputedStyle(e).display === 'inline' && e.parentElement && e.parentElement.textContent.trim().length > e.textContent.trim().length + 3) return;
    const r = e.getBoundingClientRect();
    if (r.height < min - 0.5 || r.width < min - 0.5 && r.height < min - 0.5) small.push((e.className || e.tagName) + ':' + Math.round(r.height));
  });
  out.small = [...new Set(small)].slice(0, 5); out.min = min;
  // home: block overlaps + face clearance + fits
  const home = document.querySelector('.main-home');
  if (home) {
    const rect = s => { const e = document.querySelector(s); return e && vis(e) ? e.getBoundingClientRect() : null; };
    const names = ['.role-line', '.name-block', '.specialties', '.name-stats', '.stack-ticker'].map(s => [s, rect(s)]).filter(x => x[1]);
    const hit = [];
    for (let i = 0; i < names.length; i++) for (let j = i + 1; j < names.length; j++) {
      const a = names[i][1], b = names[j][1];
      if (a.left < b.right - 1 && a.right > b.left + 1 && a.top < b.bottom - 1 && a.bottom > b.top + 1) hit.push(names[i][0] + '×' + names[j][0]);
    }
    out.overlap = hit;
    const pb = document.getElementById('portrait-bg').getBoundingClientRect();
    const band = Math.abs(pb.width - pb.height) < 4;      // square = band layout (face above the text)
    if (band) { const nb = document.querySelector('.name-block').getBoundingClientRect(); out.faceCovered = nb.top < pb.bottom - 4; }
    else { const lines = [...document.querySelectorAll('.name-line')].map(e => { const g = document.createRange(); g.selectNodeContents(e); return g.getBoundingClientRect().right; }); out.faceCovered = Math.max(...lines) > pb.left + pb.width * 0.42; }
    out.fits = de.scrollHeight <= innerHeight + 1;
  }
  return out;
}

(async () => {
  const srv = await serve(); const base = 'http://localhost:' + srv.address().port;
  const browserType = ENGINE === 'firefox' ? firefox : ENGINE === 'webkit' ? webkit : chromium;
  const browser = await browserType.launch(ENGINE === 'msedge' ? { channel: 'msedge' } : {});
  const pages = PAGES_OPT === 'home' ? ['/'] : PAGES;
  if (SHOTS) fs.mkdirSync(path.join(__dirname, 'shots'), { recursive: true });
  let fails = 0; const rows = [];
  for (const [name, w, h, dpr, touch] of VIEWPORTS) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: dpr, hasTouch: touch, isMobile: touch && ENGINE !== 'firefox' });
    for (const p of pages) {
      const pg = await ctx.newPage(); const errs = [];
      pg.on('console', m => m.type() === 'error' && errs.push(m.text())); pg.on('pageerror', e => errs.push(e.message));
      pg.on('response', r => r.status() >= 400 && !r.url().endsWith('/404.html') && errs.push(r.status() + ' ' + r.url().replace(base, '')));
      await pg.goto(base + p, { waitUntil: 'networkidle' }); await pg.waitForTimeout(p === '/' ? 2400 : 500);
      const m = await pg.evaluate(inPage);
      const desktop = w >= 1024 && h >= 700 && !touch;
      const prob = [];
      if (m.ox) prob.push('overflow-x');
      if (m.tiny.length) prob.push('tiny:' + m.tiny.join(','));
      if (m.small.length) prob.push(`targets<${m.min}:` + m.small.join(','));
      if (m.overlap && m.overlap.length) prob.push('overlap:' + m.overlap.join(','));
      if (m.faceCovered) prob.push('face-covered');
      if (desktop && m.fits === false) prob.push('home-scrolls');
      if (errs.length) prob.push('errors:' + errs.join('|'));
      if (prob.length) { fails++; rows.push(`${name.padEnd(13)} ${(w + 'x' + h).padEnd(10)} ${p.padEnd(28)} ${prob.join('  ')}`); }
      if (SHOTS && (p === '/' )) await pg.screenshot({ path: path.join(__dirname, 'shots', `${ENGINE}-${name}-home.png`) });
      await pg.close();
    }
    await ctx.close();
  }
  console.log(`engine=${ENGINE}  viewports=${VIEWPORTS.length}  pages=${pages.length}  problems=${fails}`);
  rows.forEach(r => console.log(r));
  await browser.close(); srv.close(); process.exit(fails ? 1 : 0);
})();
