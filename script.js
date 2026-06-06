/* ─── ROCMINE Portfolio v2 ─ script.js ─────────────────────────────────── */

(function () {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── Footer year ─────────────────────────────────────────────────────── */
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ── Video autoplay fallback ─────────────────────────────────────────── */
  const video = document.getElementById('logo-video');
  if (video) video.play().catch(() => {});

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

  /* ── Copy email ──────────────────────────────────────────────────────── */
  const emailBtn = document.getElementById('btn-email');
  if (emailBtn) {
    const email = emailBtn.dataset.email || 'amini.rochd.hr@gmail.com';
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
  if (roleEl && !prefersReducedMotion) {
    const full = roleEl.textContent;
    roleEl.textContent = '';
    let i = 0;
    // delay until after the header-right reveal animation (d-1 = 140ms + ~500ms anim)
    setTimeout(() => {
      const iv = setInterval(() => {
        roleEl.textContent += full[i++];
        if (i >= full.length) clearInterval(iv);
      }, 38);
    }, 680);
  }

})();
