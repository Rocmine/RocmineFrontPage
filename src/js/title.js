/* ─── ROCMINE Portfolio ─ title.js ───────────────────────────────────────────
   Pointer proximity for the big name: letters near the cursor lift and glow.
   Touch: a tap sends one wave through the letters. Does nothing when motion is off.
   The load animation and the glint wave are pure CSS (src/css/31-title.css). */

(function () {
  'use strict';

  const block = document.querySelector('.name-block');
  if (!block) return;

  const root = document.documentElement;
  const motionOn = () => root.dataset.motion !== 'reduced';
  const letters = [...block.querySelectorAll('.ch')];
  if (!letters.length) return;

  /* Release the line mask once the last letter has risen (see .intro-done in the CSS) */
  const last = letters[letters.length - 1];
  const release = () => block.classList.add('intro-done');
  if (motionOn()) last.addEventListener('animationend', e => { if (e.animationName === 'ch-rise') release(); }, { once: true });
  setTimeout(release, 3500);                      // safety net, also covers "motion off"

  /* ── pointer proximity (mouse / pen only) ─────────────────────────────── */
  const RADIUS = 150;                             // px of influence around the cursor
  let centers = [];
  let pointer = null, raf = 0;

  function measure() {
    const b = block.getBoundingClientRect();
    centers = letters.map(el => ({
      el,
      x: b.left + el.offsetLeft + el.offsetWidth / 2,
      y: b.top + el.offsetTop + el.offsetHeight / 2,
    }));
  }

  function frame() {
    raf = 0;
    if (!pointer || !motionOn()) return clear();
    measure();                                    // cheap (about 20 letters) and always correct after scroll/resize
    for (const c of centers) {
      const d = Math.hypot(c.x - pointer.x, c.y - pointer.y);
      const t = Math.max(0, 1 - d / RADIUS);
      c.el.style.setProperty('--near', (t * t * (3 - 2 * t)).toFixed(3));
    }
  }

  function clear() { letters.forEach(el => el.style.removeProperty('--near')); }
  function schedule() { if (!raf) raf = requestAnimationFrame(frame); }

  window.addEventListener('pointermove', e => {
    if (e.pointerType === 'touch') return;
    pointer = { x: e.clientX, y: e.clientY };
    schedule();
  }, { passive: true });
  document.addEventListener('pointerleave', () => { pointer = null; schedule(); });

  /* ── touch: tap the name for one wave ─────────────────────────────────── */
  block.addEventListener('pointerdown', e => {
    if (e.pointerType !== 'touch' || !motionOn() || !letters[0].animate) return;
    letters.forEach((el, i) => el.animate(
      [{ translate: '0 0' }, { translate: '0 -0.16em' }, { translate: '0 0' }],
      { duration: 520, delay: i * 26, easing: 'ease-out' }));
  });
})();
