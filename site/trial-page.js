(() => {
  'use strict';

  const RELEASE_FALLBACK = 'https://github.com/masarray/vst-enhancer/releases/latest';
  const OFFICIAL_ASSET_PREFIX = '/masarray/vst-enhancer/releases/download/';
  const installerCtas = [...document.querySelectorAll('[data-installer-cta]')];

  const copy = {
    en: {
      enabled: 'Download free for Windows',
      paused: 'View official release status'
    },
    id: {
      enabled: 'Unduh gratis untuk Windows',
      paused: 'Lihat status rilis resmi'
    }
  };

  const language = () => document.documentElement.lang === 'id' ? 'id' : 'en';

  const officialInstallerUrl = (value) => {
    if (typeof value !== 'string' || value.length > 500) return null;
    try {
      const url = new URL(value);
      if (url.protocol !== 'https:' || url.hostname !== 'github.com') return null;
      if (!url.pathname.startsWith(OFFICIAL_ASSET_PREFIX)) return null;
      if (!url.pathname.endsWith('.exe')) return null;
      return url.href;
    } catch (_) {
      return null;
    }
  };

  const setCtaState = (url, enabled) => {
    const text = copy[language()];
    installerCtas.forEach((cta) => {
      cta.href = url || RELEASE_FALLBACK;
      cta.textContent = enabled ? text.enabled : text.paused;
      if (enabled) {
        cta.removeAttribute('aria-disabled');
      } else {
        cta.setAttribute('aria-disabled', 'true');
      }
    });
  };

  const syncTextOnLanguageChange = () => {
    const observer = new MutationObserver(() => {
      const enabled = installerCtas.some((cta) => cta.getAttribute('aria-disabled') !== 'true');
      const currentUrl = installerCtas[0]?.href || RELEASE_FALLBACK;
      setCtaState(currentUrl, enabled);
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
  };

  syncTextOnLanguageChange();

  (async () => {
    try {
      const response = await fetch('./release.json', { cache: 'no-store', credentials: 'same-origin' });
      if (!response.ok) throw new Error(`Release metadata returned ${response.status}`);
      const release = await response.json();
      const installerUrl = officialInstallerUrl(release.installerUrl);
      const enabled = release.distributionEnabled === true && Boolean(installerUrl);
      setCtaState(enabled ? installerUrl : release.releaseUrl || RELEASE_FALLBACK, enabled);
    } catch (_) {
      setCtaState(RELEASE_FALLBACK, false);
    }
  })();
})();
