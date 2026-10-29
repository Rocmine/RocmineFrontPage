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

  /* ── Mobile menu (hamburger) ─────────────────────────────────────────── */
  const header = document.getElementById('header');
  const navToggle = document.getElementById('nav-toggle');
  const siteNav = document.getElementById('site-nav');
  if (header && navToggle && siteNav) {
    const phone = window.matchMedia('(max-width: 640px)');
    const isOpen = () => header.classList.contains('nav-open');
    const setOpen = (open, returnFocus) => {
      header.classList.toggle('nav-open', open);
      root.classList.toggle('nav-lock', open);
      navToggle.setAttribute('aria-expanded', String(open));
      navToggle.setAttribute('aria-label', open ? 'Close menu' : 'Menu');
      if (open) { const first = siteNav.querySelector('a'); if (first) first.focus(); }
      else if (returnFocus) navToggle.focus();
    };
    navToggle.addEventListener('click', () => setOpen(!isOpen(), true));
    siteNav.addEventListener('click', e => { if (e.target.closest('a')) setOpen(false, false); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && isOpen()) setOpen(false, true); });
    document.addEventListener('click', e => { if (isOpen() && !header.contains(e.target)) setOpen(false, false); });
    header.addEventListener('focusout', e => { if (isOpen() && e.relatedTarget && !header.contains(e.relatedTarget)) setOpen(false, false); });
    phone.addEventListener('change', () => setOpen(false, false));
  }

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

  /* ── Copy email (footer button + hero button); falls back to mailto ──── */
  document.querySelectorAll('[data-email]').forEach(el => {
    const email = el.dataset.email || 'amine.rochdi@rocmine.net';
    el.addEventListener('click', async e => {
      e.preventDefault();
      try {
        await navigator.clipboard.writeText(email);
        showToast('✓ copied to clipboard');
      } catch (err) {
        window.location.href = `mailto:${email}`;
        showToast('opening mail client…');
      }
    });
  });

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
