(() => {
  'use strict';

  const CANONICAL_URL = 'https://masarray.github.io/vst-enhancer/';

  const mobileTypography = document.createElement('style');
  mobileTypography.id = 'mobile-readable-type';
  mobileTypography.textContent = `
    @media (max-width: 740px) {
      :root {
        --micro: 12px;
        --small: 12px;
        --copy: 13px;
      }

      body {
        font-size: 13px;
      }
    }
  `;
  document.head.append(mobileTypography);

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

  const mobileBar = document.getElementById('mobile-download-bar');
  const heroCta = document.getElementById('installer-link-bottom');

  if (mobileBar && heroCta) {
    mobileBar.hidden = false;

    const setVisible = (visible) => {
      mobileBar.setAttribute('data-visible', String(visible));
      mobileBar.setAttribute('aria-hidden', String(!visible));
    };

    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(
        ([entry]) => setVisible(!entry.isIntersecting),
        { threshold: 0.15 }
      );
      observer.observe(heroCta);
    } else {
      setVisible(true);
    }
  }
})();