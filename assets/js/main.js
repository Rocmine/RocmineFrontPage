/* ─── ROCMINE Portfolio ─ main.js ────────────────────────────────────────── */

(function () {
  'use strict';

  const root = document.documentElement;

  /* Animation is on unless the visitor switched it off with #btn-motion.
     The OS "show animations" setting is deliberately not consulted. */
  const motionOn = () => root.dataset.motion !== 'reduced';

  /* ── Footer year ─────────────────────────────────────────────────────── */
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ── Logo video ──────────────────────────────────────────────────────── */
  const video = document.getElementById('logo-video');
  function syncVideo() {
    if (!video) return;
    if (motionOn()) video.play().catch(() => {});
    else video.pause();
  }
  syncVideo();

  /* ── Toast ───────────────────────────────────────────────────────────── */
  const toast = document.getElementById('toast');
  let toastTimer;
  function showToast(msg, ms = 2200) {
    if (!toast) return;
    clearTimeout(toastTimer);
    toast.textContent = msg;
    toast.classList.add('show');
    toastTimer = setTimeout(() => toast.classList.remove('show'), ms);
  }

  /* ── Motion switch ───────────────────────────────────────────────────── */
  const motionBtn = document.getElementById('btn-motion');
  function paintMotionBtn() {
    if (!motionBtn) return;
    motionBtn.textContent = motionOn() ? 'motion: on' : 'motion: off';
  }
  if (motionBtn) {
    paintMotionBtn();
    motionBtn.addEventListener('click', () => {
      const turnOff = motionOn();
      root.dataset.motion = turnOff ? 'reduced' : 'full';
      try { localStorage.setItem('rocmine-motion', turnOff ? 'off' : 'on'); } catch (e) { /* storage blocked */ }
      paintMotionBtn();
      syncVideo();
      showToast(turnOff ? 'animations off' : 'animations on', 1400);
    });
  }

  /* ── Copy email (falls back to mailto) ───────────────────────────────── */
  const emailBtn = document.getElementById('btn-email');
  if (emailBtn) {
    const email = emailBtn.dataset.email || 'amine.rochdi@rocmine.net';
    emailBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(email);
        showToast('✓ copied to clipboard');
      } catch {
        window.location.href = `mailto:${email}`;
        showToast('opening mail client…');
      }
    });
  }

  /* ── External link toasts ────────────────────────────────────────────── */
  ['btn-github', 'btn-linkedin'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('click', () =>
      showToast(`opening ${id === 'btn-github' ? 'github' : 'linkedin'}…`, 1400));
  });

  /* ── Typewriter on role text ─────────────────────────────────────────── */
  const roleEl = document.querySelector('.role-text');
  if (roleEl && motionOn()) {
    const full = roleEl.textContent;
    roleEl.textContent = '';
    let i = 0;
    // wait for the reveal animation (d-1 = 140ms + ~500ms)
    setTimeout(() => {
      const iv = setInterval(() => {
        roleEl.textContent += full[i++];
        if (i >= full.length) clearInterval(iv);
      }, 34);
    }, 480);
  }

  /* ── Diagrams: draw once when scrolled into view ─────────────────────── */
  const diagrams = document.querySelectorAll('.diagram');
  if (diagrams.length) {
    if (!('IntersectionObserver' in window)) {
      diagrams.forEach(d => d.classList.add('in'));
    } else {
      const io = new IntersectionObserver((entries) => {
        entries.forEach(e => {
          if (!e.isIntersecting) return;
          e.target.classList.add('in');
          io.unobserve(e.target);
        });
      }, { threshold: 0.2 });
      diagrams.forEach(d => io.observe(d));
    }
  }

})();
