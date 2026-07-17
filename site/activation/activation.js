(() => {
  'use strict';

  const STORAGE_KEY = 'askp-language';
  const SUPPORTED = ['en', 'id'];
  const RELEASE_FALLBACK = 'https://github.com/masarray/vst-enhancer/releases/latest';
  const OFFICIAL_RELEASE_PATH = '/masarray/vst-enhancer/releases';

  const officialReleaseUrl = (value, asset = false) => {
    if (typeof value !== 'string' || value.length > 500) return null;
    try {
      const url = new URL(value);
      if (url.protocol !== 'https:' || url.hostname !== 'github.com') return null;
      if (!url.pathname.startsWith(OFFICIAL_RELEASE_PATH)) return null;
      if (asset && !url.pathname.includes('/releases/download/')) return null;
      return url.href;
    } catch (_) {
      return null;
    }
  };

  const buttons = [...document.querySelectorAll('[data-lang-button]')];
  const translated = [...document.querySelectorAll('[data-en][data-id]')];

  const chooseLanguage = () => {
    const query = new URLSearchParams(location.search).get('lang');
    if (SUPPORTED.includes(query)) return query;
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (SUPPORTED.includes(stored)) return stored;
    } catch (_) {}
    return navigator.language?.toLowerCase().startsWith('id') ? 'id' : 'en';
  };

  const setLanguage = (language, updateUrl = true) => {
    if (!SUPPORTED.includes(language)) return;
    document.documentElement.lang = language;
    translated.forEach((element) => {
      element.textContent = element.dataset[language] || element.dataset.en || element.textContent;
    });
    buttons.forEach((button) => {
      button.setAttribute('aria-pressed', String(button.dataset.langButton === language));
    });
    try { localStorage.setItem(STORAGE_KEY, language); } catch (_) {}
    if (updateUrl) {
      const url = new URL(location.href);
      url.searchParams.set('lang', language);
      history.replaceState(null, '', `${url.pathname}${url.search}${url.hash}`);
    }
    document.title = language === 'id'
      ? 'Aktivasi Opsional ArSonKuPik | Teruskan Editing dan Dukung Development'
      : 'Optional ArSonKuPik Activation | Keep Editing and Support Development';
  };

  buttons.forEach((button) => {
    button.addEventListener('click', () => setLanguage(button.dataset.langButton));
  });
  setLanguage(chooseLanguage(), false);

  (async () => {
    try {
      const response = await fetch('../release.json', { cache: 'no-store', credentials: 'same-origin' });
      if (!response.ok) return;
      const release = await response.json();

      if (Number.isFinite(release.activationPriceUsd)) {
        document.getElementById('activation-price')?.replaceChildren(`USD ${release.activationPriceUsd}`);
      }

      const freeDownload = document.getElementById('free-download-link');
      if (freeDownload) {
        const releaseUrl = officialReleaseUrl(release.releaseUrl) || RELEASE_FALLBACK;
        const installerUrl = officialReleaseUrl(release.installerUrl, true);
        freeDownload.href = release.distributionEnabled === true && installerUrl
          ? installerUrl
          : releaseUrl;
      }

      const title = document.getElementById('activation-status-title');
      const copy = document.getElementById('activation-status-copy');
      const language = document.documentElement.lang === 'id' ? 'id' : 'en';

      if (release.purchaseCheckoutAvailable === true && typeof release.purchaseUrl === 'string') {
        if (title) title.textContent = language === 'id' ? 'Checkout resmi tersedia' : 'Authorised checkout available';
        if (copy) copy.textContent = language === 'id'
          ? 'Gunakan hanya tautan checkout resmi dan tinjau identitas penjual, jumlah final, pajak, refund, privasi, serta ketentuan penyedia sebelum membayar.'
          : 'Use only the authorised checkout and review seller identity, final amount, tax, refund, privacy and provider terms before paying.';
      }
    } catch (_) {
      const freeDownload = document.getElementById('free-download-link');
      if (freeDownload) freeDownload.href = RELEASE_FALLBACK;
    }
  })();
})();