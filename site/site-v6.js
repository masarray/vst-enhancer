(() => {
  'use strict';

  const root = document.documentElement;
  const currentScript = document.currentScript;
  const storageKey = 'askp-language';
  const isIndonesian = root.lang.toLowerCase().startsWith('id');

  const savePreference = (value) => {
    if (value !== 'id' && value !== 'en') return;
    try { localStorage.setItem(storageKey, value); } catch (_) {}
  };

  document.querySelectorAll('.language-switch a[lang]').forEach((link) => {
    link.addEventListener('click', () => {
      savePreference(link.lang.toLowerCase().startsWith('id') ? 'id' : 'en');
    });
  });

  if (isIndonesian) {
    document.querySelectorAll('a.activation-soft-link[href="../activation/"]').forEach((link) => {
      link.setAttribute('href', 'activation/');
    });
  }

  // Keep both primary platform CTAs visible immediately. The Mac CTA uses a
  // safe #download fallback first; the idle release runtime upgrades it to the
  // exact reviewed DMG URL from release.json when that manifest is available.
  const ensureHeroMacCta = () => {
    if (document.getElementById('mac-dmg-link-hero')) return;
    const actions = document.querySelector('.landing-hero .hero-copy .actions');
    if (!actions) return;

    const link = document.createElement('a');
    link.id = 'mac-dmg-link-hero';
    link.className = 'button secondary hero-mac-download';
    link.href = '#download';
    link.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.79 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.53 4.1M12.03 7.25C11.88 5.02 13.69 3.18 15.77 3c.29 2.58-2.34 4.5-3.74 4.25"/></svg><span>${isIndonesian ? 'Unduh gratis untuk Mac' : 'Download free for Mac'}</span>`;

    const explore = actions.querySelector('a[href^="#"]');
    actions.insertBefore(link, explore || null);
  };

  ensureHeroMacCta();

  const source = currentScript?.src
    || new URL(`${root.dataset.siteBase || '.'}/site-v6.js`, location.href).href;

  let coreRequested = false;
  const loadCore = () => {
    if (coreRequested) return;
    coreRequested = true;
    const core = document.createElement('script');
    core.src = source.replace(/site-v6\.js(?:\?.*)?$/, 'site-v6-core.js');
    core.async = true;
    document.head.appendChild(core);
  };

  // Release enrichment is useful but not required for the first paint. The
  // reviewed static HTML already routes users to the official GitHub Release,
  // so let LCP/rendering finish before parsing the larger enhancement runtime.
  if ('requestIdleCallback' in window) {
    window.requestIdleCallback(loadCore, { timeout: 1400 });
  } else {
    window.requestAnimationFrame(() => window.setTimeout(loadCore, 0));
  }
})();