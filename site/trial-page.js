(() => {
  'use strict';

  const CANONICAL_URL = 'https://masarray.github.io/vst-enhancer/';

  // EN/ID is a display preference on one canonical product page. Remove the
  // legacy query-language alternate signals from the rendered document so
  // canonical metadata cannot vary by browser language or local storage.
  document.querySelectorAll('link[rel="alternate"][hreflang]').forEach((link) => link.remove());

  const canonical = document.getElementById('canonical-link');
  if (canonical) canonical.setAttribute('href', CANONICAL_URL);

  document.querySelector('meta[property="og:url"]')?.setAttribute('content', CANONICAL_URL);

  const currentUrl = new URL(window.location.href);
  if (currentUrl.searchParams.has('lang')) {
    currentUrl.searchParams.delete('lang');
    const query = currentUrl.searchParams.toString();
    history.replaceState(
      null,
      '',
      `${currentUrl.pathname}${query ? `?${query}` : ''}${currentUrl.hash}`
    );
  }

  document.documentElement.setAttribute('data-canonical-mode', 'single-url');
})();
