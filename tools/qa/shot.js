/* Screenshot helper: node tools/qa/shot.js <path> <width>x<height> [out-name] [--full] [--touch]
   Saves tools/qa/shots/<out-name>.png (default: derived from the path). */
const { chromium } = require('playwright');
const http = require('http'); const fs = require('fs'); const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const [urlPath = '/', size = '1440x900', outName] = process.argv.slice(2).filter(a => !a.startsWith('--'));
const FULL = process.argv.includes('--full'); const TOUCH = process.argv.includes('--touch');
const [w, h] = size.split('x').map(Number);
const T = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.webm': 'video/webm', '.mp4': 'video/mp4', '.woff2': 'font/woff2', '.ico': 'image/x-icon' };
const srv = http.createServer((q, r) => { let u = q.url.split('?')[0]; if (u.endsWith('/')) u += 'index.html'; const f = path.join(ROOT, u); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'Content-Type': T[path.extname(f)] || 'application/octet-stream' }); r.end(d); } }); });
srv.listen(0, async () => {
  const b = await chromium.launch({ channel: 'msedge' });
  const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: TOUCH ? 2 : 1, isMobile: TOUCH, hasTouch: TOUCH });
  const p = await ctx.newPage();
  await p.goto('http://localhost:' + srv.address().port + urlPath, { waitUntil: 'networkidle' });
  await p.waitForTimeout(urlPath === '/' ? 3600 : 900);
  fs.mkdirSync(path.join(__dirname, 'shots'), { recursive: true });
  const name = outName || (urlPath.replace(/[^a-z0-9]+/gi, '_') + '_' + size);
  const file = path.join(__dirname, 'shots', name + '.png');
  await p.screenshot({ path: file, fullPage: FULL });
  console.log(file);
  await b.close(); srv.close();
});
