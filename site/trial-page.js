(() => {
  'use strict';

  const RELEASE_FALLBACK = 'https://github.com/masarray/vst-enhancer/releases/latest';
  const OFFICIAL_ASSET_PREFIX = '/masarray/vst-enhancer/releases/download/';
  const metaCopy = {
    en: {
      title: 'ArSonKuPik VST3 Audio Enhancer | Free for 365 Days',
      description: 'Hear ArSonKuPik in your own mix. Use every preset and control free for 365 days with no account, card, subscription, automatic charge or obligation to buy.',
      socialTitle: 'ArSonKuPik VST3 Audio Enhancer — Free for 365 Days',
      socialDescription: 'Use every preset and control in your own music for a full year. No account, card, subscription, automatic charge or obligation to buy.'
    },
    id: {
      title: 'ArSonKuPik Audio Enhancer VST3 | Gratis 365 Hari',
      description: 'Dengarkan ArSonKuPik pada mix Anda sendiri. Gunakan seluruh preset dan kontrol gratis 365 hari tanpa akun, kartu, langganan, tagihan otomatis, atau kewajiban membeli.',
      socialTitle: 'ArSonKuPik Audio Enhancer VST3 — Gratis 365 Hari',
      socialDescription: 'Gunakan seluruh preset dan kontrol pada musik Anda selama satu tahun. Tanpa akun, kartu, langganan, tagihan otomatis, atau kewajiban membeli.'
    }
  };

  const currentLanguage = () => document.documentElement.lang === 'id' ? 'id' : 'en';

  const applyCtaCopy = () => {
    const language = currentLanguage();
    document.querySelectorAll('[data-installer-cta][data-en][data-id]').forEach((link) => {
      link.textContent = link.dataset[language] || link.dataset.en || link.textContent;
    });
  };

  const applyMetadata = () => {
    const text = metaCopy[currentLanguage()];
    document.title = text.title;
    document.querySelector('meta[name="description"]')?.setAttribute('content', text.description);
    document.querySelector('meta[property="og:title"]')?.setAttribute('content', text.socialTitle);
    document.querySelector('meta[property="og:description"]')?.setAttribute('content', text.socialDescription);
    document.querySelector('meta[name="twitter:title"]')?.setAttribute('content', text.socialTitle);
    document.querySelector('meta[name="twitter:description"]')?.setAttribute('content', text.socialDescription);
    applyCtaCopy();
  };

  document.querySelectorAll('[data-lang-button]').forEach((button) => {
    button.addEventListener('click', () => queueMicrotask(applyMetadata));
  });

  applyMetadata();

  const officialInstallerUrl = (value) => {
    if (typeof value !== 'string') return null;
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

  (async () => {
    try {
      const response = await fetch('./release.json', { cache: 'no-store', credentials: 'same-origin' });
      if (!response.ok) return;
      const release = await response.json();
      const installerUrl = release.distributionEnabled === true
        ? officialInstallerUrl(release.installerUrl)
        : null;
      document.querySelectorAll('[data-installer-cta]').forEach((link) => {
        link.href = installerUrl || release.releaseUrl || RELEASE_FALLBACK;
      });
      applyCtaCopy();
    } catch (_) {
      document.querySelectorAll('[data-installer-cta]').forEach((link) => {
        link.href = RELEASE_FALLBACK;
      });
      applyCtaCopy();
    }
  })();
})();