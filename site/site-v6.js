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

  // Platform CTAs and their safe fallbacks are already present in static HTML.
  // Release enrichment is useful but not required for first paint, so let
  // rendering finish before loading the larger manifest/runtime layer.
  if ('requestIdleCallback' in window) {
    window.requestIdleCallback(loadCore, { timeout: 1400 });
  } else {
    window.requestAnimationFrame(() => window.setTimeout(loadCore, 0));
  }
})();