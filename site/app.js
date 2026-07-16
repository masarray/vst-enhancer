(() => {
  'use strict';

  const storageKey = 'askp-language';
  const supportedLanguages = ['en', 'id'];
  const languageButtons = [...document.querySelectorAll('[data-lang-button]')];
  const translatableElements = [...document.querySelectorAll('[data-en][data-id]')];
  const installerButtons = [
    document.getElementById('installer-link'),
    document.getElementById('installer-link-bottom')
  ].filter(Boolean);

  const meta = {
    en: {
      title: 'ArSonKuPik — Smart Audio Enhancer | 365-Day Free Evaluation',
      description: 'ArSonKuPik is a smart Windows VST3 and standalone audio enhancer. Try all presets and controls for 365 days with no card, subscription, or automatic charge.',
      pausedTitle: 'Download paused',
      pausedMessage: 'The reviewed v0.5.12 JUCE 8.0.14 build is completing Windows QA and packaging checks.',
      enabledTitle: 'Official download available',
      enabledMessage: 'Download only from the official GitHub Release and verify its SHA-256 checksum.',
      unknownTitle: 'Release status unavailable',
      unknownMessage: 'Open the official Releases page before downloading.',
      pausedButton: 'View release status',
      enabledButton: 'Download ArSonKuPik',
      pausedCta: 'The official download will be enabled only after Windows QA and package verification succeed.',
      enabledCta: 'Download the official package, verify its checksum, and evaluate it in your own projects.',
      checkingTitle: 'Release status',
      checkingMessage: 'Checking official distribution status…'
    },
    id: {
      title: 'ArSonKuPik — Audio Enhancer Cerdas | Evaluasi Gratis 365 Hari',
      description: 'ArSonKuPik adalah audio enhancer VST3 dan standalone untuk Windows. Coba semua preset dan kontrol selama 365 hari tanpa kartu, langganan, atau tagihan otomatis.',
      pausedTitle: 'Unduhan dijeda',
      pausedMessage: 'Build v0.5.12 JUCE 8.0.14 yang telah ditinjau sedang menyelesaikan QA Windows dan pemeriksaan paket.',
      enabledTitle: 'Unduhan resmi tersedia',
      enabledMessage: 'Unduh hanya dari GitHub Release resmi dan verifikasi checksum SHA-256.',
      unknownTitle: 'Status rilis tidak tersedia',
      unknownMessage: 'Buka halaman Releases resmi sebelum mengunduh.',
      pausedButton: 'Lihat status rilis',
      enabledButton: 'Unduh ArSonKuPik',
      pausedCta: 'Unduhan resmi hanya akan diaktifkan setelah QA Windows dan verifikasi paket berhasil.',
      enabledCta: 'Unduh paket resmi, verifikasi checksum, lalu evaluasi pada project Anda sendiri.',
      checkingTitle: 'Status rilis',
      checkingMessage: 'Memeriksa status distribusi resmi…'
    }
  };

  let currentLanguage = 'en';
  let releaseState = { type: 'checking', releaseUrl: 'https://github.com/masarray/vst-enhancer/releases' };

  const chooseInitialLanguage = () => {
    const queryLanguage = new URLSearchParams(window.location.search).get('lang');
    if (supportedLanguages.includes(queryLanguage)) return queryLanguage;

    try {
      const saved = localStorage.getItem(storageKey);
      if (supportedLanguages.includes(saved)) return saved;
    } catch (_) {
      // Storage can be blocked; browser language remains a safe fallback.
    }

    return navigator.language?.toLowerCase().startsWith('id') ? 'id' : 'en';
  };

  const setMeta = (language) => {
    document.title = meta[language].title;
    document.querySelector('meta[name="description"]')?.setAttribute('content', meta[language].description);
    document.querySelector('meta[property="og:title"]')?.setAttribute('content', meta[language].title);
    document.querySelector('meta[property="og:description"]')?.setAttribute('content', meta[language].description);
    document.querySelector('meta[name="twitter:title"]')?.setAttribute('content', meta[language].title);
    document.querySelector('meta[name="twitter:description"]')?.setAttribute('content', meta[language].description);
  };

  const renderReleaseState = () => {
    const copy = meta[currentLanguage];
    const banner = document.getElementById('distribution-banner');
    const title = document.getElementById('distribution-title');
    const message = document.getElementById('distribution-message');
    const bannerLink = document.getElementById('distribution-link');
    const ctaCopy = document.querySelector('.release-cta-copy');
    const safeReleaseUrl = releaseState.releaseUrl || 'https://github.com/masarray/vst-enhancer/releases';

    if (bannerLink) bannerLink.setAttribute('href', safeReleaseUrl);
    document.getElementById('release-link')?.setAttribute('href', safeReleaseUrl);

    if (releaseState.type === 'enabled' && releaseState.installerUrl) {
      banner?.setAttribute('data-state', 'enabled');
      if (title) title.textContent = copy.enabledTitle;
      if (message) message.textContent = copy.enabledMessage;
      if (ctaCopy) ctaCopy.textContent = copy.enabledCta;
      installerButtons.forEach((button) => {
        button.setAttribute('href', releaseState.installerUrl);
        button.textContent = copy.enabledButton;
        button.setAttribute('aria-label', copy.enabledButton);
      });
      return;
    }

    if (releaseState.type === 'paused') {
      banner?.setAttribute('data-state', 'paused');
      if (title) title.textContent = copy.pausedTitle;
      if (message) message.textContent = copy.pausedMessage;
      if (ctaCopy) ctaCopy.textContent = copy.pausedCta;
      installerButtons.forEach((button) => {
        button.setAttribute('href', safeReleaseUrl);
        button.textContent = copy.pausedButton;
        button.setAttribute('aria-label', copy.pausedButton);
      });
      return;
    }

    if (releaseState.type === 'error') {
      banner?.setAttribute('data-state', 'error');
      if (title) title.textContent = copy.unknownTitle;
      if (message) message.textContent = copy.unknownMessage;
      if (ctaCopy) ctaCopy.textContent = copy.unknownMessage;
      installerButtons.forEach((button) => {
        button.setAttribute('href', safeReleaseUrl);
        button.textContent = copy.pausedButton;
      });
      return;
    }

    banner?.setAttribute('data-state', 'checking');
    if (title) title.textContent = copy.checkingTitle;
    if (message) message.textContent = copy.checkingMessage;
  };

  const setLanguage = (language, updateUrl = true) => {
    if (!supportedLanguages.includes(language)) return;
    currentLanguage = language;
    document.documentElement.lang = language;

    translatableElements.forEach((element) => {
      element.textContent = element.dataset[language] || element.dataset.en || element.textContent;
    });

    languageButtons.forEach((button) => {
      const active = button.dataset.langButton === language;
      button.setAttribute('aria-pressed', String(active));
    });

    try { localStorage.setItem(storageKey, language); } catch (_) {}

    if (updateUrl) {
      const url = new URL(window.location.href);
      url.searchParams.set('lang', language);
      history.replaceState(null, '', `${url.pathname}${url.search}${url.hash}`);
    }

    setMeta(language);
    renderReleaseState();
  };

  languageButtons.forEach((button) => {
    button.addEventListener('click', () => setLanguage(button.dataset.langButton));
  });

  setLanguage(chooseInitialLanguage(), false);

  (async () => {
    try {
      const response = await fetch('./release.json', { cache: 'no-store' });
      if (!response.ok) throw new Error(`release metadata returned ${response.status}`);
      const release = await response.json();

      if (release.version) {
        const version = document.getElementById('release-version');
        if (version) version.textContent = release.version;
      }

      const releaseUrl = release.releaseUrl || releaseState.releaseUrl;
      releaseState = release.distributionEnabled === true && release.installerUrl
        ? { type: 'enabled', installerUrl: release.installerUrl, releaseUrl }
        : { type: 'paused', releaseUrl };

      document.getElementById('checksums-link')?.setAttribute(
        'href', release.checksumsUrl || releaseUrl
      );
      renderReleaseState();
    } catch (_) {
      releaseState = { type: 'error', releaseUrl: releaseState.releaseUrl };
      renderReleaseState();
    }
  })();
})();
