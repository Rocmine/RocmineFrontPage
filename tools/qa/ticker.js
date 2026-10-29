/* Checks that the home-page ticker loops with no gap: desktop and wide screens only.
   node tools/qa/ticker.js
   Samples one full animation cycle (jumping currentTime, so it takes milliseconds). */
const { chromium } = require('playwright');
const http = require('http'); const fs = require('fs'); const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const T = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.webm': 'video/webm', '.mp4': 'video/mp4', '.woff2': 'font/woff2', '.ico': 'image/x-icon' };
const srv = http.createServer((q, r) => { let u = q.url.split('?')[0]; if (u.endsWith('/')) u += 'index.html'; const f = path.join(ROOT, u); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'Content-Type': T[path.extname(f)] || 'application/octet-stream' }); r.end(d); } }); });
let bad = 0; const ok = (n, c, x = '') => { console.log((c ? 'PASS ' : 'FAIL ') + n + (x ? '  ' + x : '')); if (!c) bad++; };

srv.listen(0, async () => {
  const b = await chromium.launch({ channel: 'msedge' });
  for (const [w, h] of [[1440, 900], [1920, 1080], [3440, 1440], [3840, 2160]]) {
    const p = await (await b.newContext({ viewport: { width: w, height: h } })).newPage();
    await p.goto('http://localhost:' + srv.address().port + '/', { waitUntil: 'networkidle' });
    const r = await p.evaluate(() => {
      const run = document.querySelector('.ticker-run'), body = document.querySelector('.ticker-body');
      const anim = run.getAnimations().find(a => a.animationName === 'ticker-scroll'); anim.pause();
      const dur = anim.effect.getComputedTiming().duration;
      const bodyR = body.getBoundingClientRect();
      const items = [...run.querySelectorAll('.ticker-items')];
      const rects = () => items.map(i => i.getBoundingClientRect());
      let worstGap = 0, covered = true;
      for (let k = 0; k <= 200; k++) {                       // 201 samples over one full cycle
        anim.currentTime = dur * k / 200;
        const rs = rects().sort((a, b) => a.left - b.left);
        if (rs[0].left > bodyR.left + 0.5) { covered = false; worstGap = Math.max(worstGap, rs[0].left - bodyR.left); }
        for (let i = 1; i < rs.length; i++) worstGap = Math.max(worstGap, rs[i].left - rs[i - 1].right);
        if (rs[rs.length - 1].right < bodyR.right - 0.5) { covered = false; worstGap = Math.max(worstGap, bodyR.right - rs[rs.length - 1].right); }
      }
      // loop alignment: moving one full cycle must shift the strip by exactly one copy width
      anim.currentTime = 0; const x0 = rects()[0].left;
      anim.currentTime = dur - 0.001; const x1 = rects()[0].left;
      const copyW = rects()[1].left - rects()[0].left;
      return { covered, worstGap: +worstGap.toFixed(2), shift: +(x0 - x1).toFixed(2), copyW: +copyW.toFixed(2), copies: items.length, bodyW: Math.round(bodyR.width) };
    });
    ok(`${w}x${h}: no empty gap in the visible strip over a full cycle`, r.covered && r.worstGap < 0.6, `worstGap=${r.worstGap}px copies=${r.copies} strip=${r.bodyW}px copyWidth=${r.copyW}px`);
    ok(`${w}x${h}: loop point lines up (shift = one copy)`, Math.abs(r.shift - r.copyW) < 0.6, `shift=${r.shift} copy=${r.copyW}`);
  }
  await b.close(); srv.close(); process.exit(bad ? 1 : 0);
});
