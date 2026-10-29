/* Checks the name animation on the home page (Edge by default).
   node title.js [--shots]   frames are saved to tools/qa/shots/ */
const { chromium } = require('playwright');
const http = require('http'); const fs = require('fs'); const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..'); const SHOTS = process.argv.includes('--shots');
const T = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.webm': 'video/webm', '.mp4': 'video/mp4', '.woff2': 'font/woff2', '.ico': 'image/x-icon', '.webp': 'image/webp', '.cur': 'image/x-icon' };
const srv = http.createServer((q, r) => { let u = q.url.split('?')[0]; if (u.endsWith('/')) u += 'index.html'; const f = path.join(ROOT, u); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'Content-Type': T[path.extname(f)] || 'application/octet-stream' }); r.end(d); } }); });
let bad = 0; const ok = (name, cond, extra = '') => { console.log((cond ? 'PASS ' : 'FAIL ') + name + (extra ? '  ' + extra : '')); if (!cond) bad++; };

srv.listen(0, async () => {
  const base = 'http://localhost:' + srv.address().port;
  const b = await chromium.launch({ channel: 'msedge' });
  // the OS says "reduce motion" (Windows: animations off); the site must still animate
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  const p = await ctx.newPage(); const errs = [];
  p.on('console', m => m.type() === 'error' && errs.push(m.text())); p.on('pageerror', e => errs.push(e.message));
  await p.goto(base + '/', { waitUntil: 'domcontentloaded' });
  const state = () => p.evaluate(() => {
    const chs = [...document.querySelectorAll('.name-line .ch')];
    const cs = el => getComputedStyle(el);
    return { n: chs.length, op: chs.map(c => +cs(c).opacity), anim: cs(chs[0]).animationName, introDone: document.querySelector('.name-block').classList.contains('intro-done'), motion: document.documentElement.dataset.motion };
  });
  const frames = [];
  for (const [ms, label] of [[250, 't250'], [700, 't700'], [1300, 't1300'], [2600, 't2600']]) {
    await p.waitForTimeout(ms - (frames.length ? frames[frames.length - 1].ms : 0));
    frames.push({ ms, label, ...(await state()) });
    if (SHOTS) { fs.mkdirSync(path.join(__dirname, 'shots'), { recursive: true }); await p.screenshot({ path: path.join(__dirname, 'shots', `title-${label}.png`), clip: { x: 0, y: 200, width: 1000, height: 380 } }); }
  }
  const [f1, f2, f3, f4] = frames;
  ok('OS reduce-motion ignored (data-motion=full)', f1.motion === 'full');
  ok('title split into letters', f1.n === 18, 'letters=' + f1.n);
  ok('letters animate in (rise)', f1.anim.includes('ch-rise'));
  const mean = a => a.reduce((x, y) => x + y, 0) / a.length;
  ok('staggered: opacity grows over time', mean(f1.op) < mean(f2.op) && mean(f2.op) <= mean(f3.op) + 0.01, `${mean(f1.op).toFixed(2)} → ${mean(f2.op).toFixed(2)} → ${mean(f3.op).toFixed(2)} → ${mean(f4.op).toFixed(2)}`);
  ok('all letters fully visible at the end', f4.op.every(o => o > 0.99));
  ok('line mask released after intro', f4.introDone);

  // pointer proximity
  const target = await p.evaluate(() => { const r = document.querySelectorAll('.name-line .ch')[8].getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; });
  await p.mouse.move(target.x - 400, target.y); await p.mouse.move(target.x, target.y, { steps: 6 }); await p.waitForTimeout(400);
  const near = await p.evaluate(() => [...document.querySelectorAll('.name-line .ch')].map(c => +c.style.getPropertyValue('--near') || 0));
  ok('letter under the pointer is lit', near[8] > 0.9, 'near[8]=' + near[8]);
  ok('far letters are not', near[0] < 0.05 || near[17] < 0.05, `first=${near[0]} last=${near[17]}`);
  if (SHOTS) await p.screenshot({ path: path.join(__dirname, 'shots', 'title-hover.png'), clip: { x: 0, y: 200, width: 1000, height: 380 } });
  await p.mouse.move(1300, 800); await p.waitForTimeout(300);
  ok('lift fades when the pointer leaves', (await p.evaluate(() => +document.querySelectorAll('.name-line .ch')[8].style.getPropertyValue('--near') || 0)) < 0.05);

  // the footer switch turns everything off
  await p.click('#btn-motion'); await p.waitForTimeout(200);
  const off = await p.evaluate(() => ({ m: document.documentElement.dataset.motion, a: getComputedStyle(document.querySelector('.name-line .ch')).animationName }));
  ok('switch off: animations stop', off.m === 'reduced' && off.a === 'none', JSON.stringify(off));
  await p.mouse.move(target.x, target.y, { steps: 3 }); await p.waitForTimeout(200);
  ok('switch off: pointer effect stops', (await p.evaluate(() => +document.querySelectorAll('.name-line .ch')[8].style.getPropertyValue('--near') || 0)) === 0);
  ok('no console errors', errs.length === 0, errs.join(' | '));
  await b.close(); srv.close(); process.exit(bad ? 1 : 0);
});
