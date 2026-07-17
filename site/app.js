(() => {
  'use strict';

  const STORAGE_KEY = 'askp-language';
  const SUPPORTED_LANGUAGES = ['en', 'id'];
  const RELEASE_FALLBACK = 'https://github.com/masarray/vst-enhancer/releases/latest';
  const OFFICIAL_RELEASE_PATH = '/masarray/vst-enhancer/releases';

  const languageButtons = [...document.querySelectorAll('[data-lang-button]')];
  const translatableElements = [...document.querySelectorAll('[data-en][data-id]')];
  const installerButtons = [...document.querySelectorAll('[data-installer-cta]')];

  const packageLinks = {
    vst3: document.getElementById('vst3-link'),
    standalone: document.getElementById('standalone-link'),
    checksums: document.getElementById('checksums-link')
  };

  const copy = {
    en: {
      checkingTitle: 'Release status',
      checkingMessage: 'Checking official distribution status…',
      enabledTitle: 'Official free evaluation available',
      enabledMessage: 'Download from the official GitHub Release. SHA-256 verification is available before installation.',
      pausedTitle: 'Official download temporarily paused',
      pausedMessage: 'Open the Releases page for the current validation and packaging status.',
      errorTitle: 'Release status unavailable',
      errorMessage: 'Open the official Releases page before downloading.',
      installerFallback: 'Download free for Windows',
      installerPaused: 'View official release status',
      paidUnavailable: 'Paid checkout is not currently enabled. The free evaluation remains available separately.',
      paidAvailable: 'Paid checkout is available only through the authorised link and terms shown before payment.'
    },
    id: {
      checkingTitle: 'Status rilis',
      checkingMessage: 'Memeriksa status distribusi resmi…',
      enabledTitle: 'Evaluasi gratis resmi tersedia',
      enabledMessage: 'Unduh melalui GitHub Release resmi. Verifikasi SHA-256 tersedia sebelum instalasi.',
      pausedTitle: 'Unduhan resmi dijeda sementara',
      pausedMessage: 'Buka halaman Releases untuk melihat status validasi dan packaging terbaru.',
      errorTitle: 'Status rilis tidak tersedia',
      errorMessage: 'Buka halaman Releases resmi sebelum mengunduh.',
      installerFallback: 'Unduh gratis untuk Windows',
      installerPaused: 'Lihat status rilis resmi',
      paidUnavailable: 'Checkout berbayar saat ini belum diaktifkan. Evaluasi gratis tetap tersedia secara terpisah.',
      paidAvailable: 'Checkout berbayar hanya tersedia melalui tautan resmi dan ketentuan yang ditampilkan sebelum pembayaran.'
    }
  };

  let currentLanguage = 'en';
  let releaseState = {
    type: 'checking',
    releaseUrl: RELEASE_FALLBACK,
    purchaseCheckoutAvailable: false
  };

  const officialReleaseUrl = (value, kind = 'release') => {
    if (typeof value !== 'string' || value.length > 500) return null;

    try {
      const url = new URL(value);
      const releaseRoot = `${OFFICIAL_RELEASE_PATH}/`;
      const isOfficialPath = url.pathname === OFFICIAL_RELEASE_PATH || url.pathname.startsWith(releaseRoot);

      if (url.protocol !== 'https:' || url.hostname !== 'github.com' || !isOfficialPath) return null;
      if (kind === 'asset' && !url.pathname.includes('/releases/download/')) return null;
      return url.href;
    } catch (_) {
      return null;
    }
  };

  const chooseInitialLanguage = () => {
    const queryLanguage = new URLSearchParams(window.location.search).get('lang');
    if (SUPPORTED_LANGUAGES.includes(queryLanguage)) return queryLanguage;

    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (SUPPORTED_LANGUAGES.includes(saved)) return saved;
    } catch (_) {
      // Browser storage can be blocked; browser language remains the fallback.
    }

    return navigator.language?.toLowerCase().startsWith('id') ? 'id' : 'en';
  };

  const updateStructuredData = () => {
    const script = document.getElementById('software-structured-data');
    if (!script) return;

    try {
      const data = JSON.parse(script.textContent);
      const software = data['@graph']?.find((entry) => entry['@type'] === 'SoftwareApplication');

      if (software) {
        if (releaseState.version) software.softwareVersion = releaseState.version.replace(/^v/i, '');
        if (releaseState.releaseUrl) {
          software.downloadUrl = releaseState.releaseUrl;
          software.releaseNotes = releaseState.releaseUrl;
          if (software.offers) software.offers.url = releaseState.releaseUrl;
        }
      }

      script.textContent = JSON.stringify(data, null, 2);
    } catch (_) {
      // Keep the server-rendered JSON-LD if dynamic enhancement fails.
    }
  };

  const setLink = (element, url, enabled = true) => {
    if (!element) return;

    element.setAttribute('href', url || RELEASE_FALLBACK);
    if (enabled) {
      element.removeAttribute('aria-disabled');
      element.removeAttribute('data-release-pending');
    } else {
      element.setAttribute('aria-disabled', 'true');
      element.setAttribute('data-release-pending', 'true');
    }
  };

  const installerLabel = (button, enabled) => {
    const text = copy[currentLanguage];
    if (!enabled) return text.installerPaused;
    return button.dataset[currentLanguage] || text.installerFallback;
  };

  const updateChecksumCommand = (installerUrl, version) => {
    const command = document.getElementById('checksum-command');
    if (!command) return;

    let filename = version
      ? `ArSonKuPik-${version}-Windows-x64-Setup.exe`
      : 'ArSonKuPik-Windows-x64-Setup.exe';

    try {
      if (installerUrl) filename = decodeURIComponent(new URL(installerUrl).pathname.split('/').pop());
    } catch (_) {
      // Use the version-derived filename.
    }

    command.textContent = `Get-FileHash .\\${filename} -Algorithm SHA256`;
  };

  const announceReleaseState = () => {
    document.dispatchEvent(new CustomEvent('askp:release-ready', {
      detail: {
        type: releaseState.type,
        version: releaseState.version || null,
        releaseUrl: releaseState.releaseUrl || RELEASE_FALLBACK
      }
    }));
  };

  const renderReleaseState = () => {
    const text = copy[currentLanguage];
    const banner = document.getElementById('distribution-banner');
    const title = document.getElementById('distribution-title');
    const message = document.getElementById('distribution-message');
    const bannerLink = document.getElementById('distribution-link');
    const releaseLink = document.getElementById('release-link');
    const purchaseStatus = document.getElementById('purchase-status');
    const releaseUrl = releaseState.releaseUrl || RELEASE_FALLBACK;

    setLink(bannerLink, releaseUrl);
    setLink(releaseLink, releaseUrl);

    if (purchaseStatus) {
      purchaseStatus.textContent = releaseState.purchaseCheckoutAvailable
        ? text.paidAvailable
        : text.paidUnavailable;
      purchaseStatus.setAttribute(
        'data-checkout-state',
        releaseState.purchaseCheckoutAvailable ? 'available' : 'unavailable'
      );
    }

    if (releaseState.type === 'checking') {
      banner?.setAttribute('data-state', 'checking');
      if (title) title.textContent = text.checkingTitle;
      if (message) message.textContent = text.checkingMessage;
      return;
    }

    if (releaseState.type === 'enabled' && releaseState.installerUrl) {
      banner?.setAttribute('data-state', 'enabled');
      if (title) title.textContent = text.enabledTitle;
      if (message) message.textContent = text.enabledMessage;

      installerButtons.forEach((button) => {
        setLink(button, releaseState.installerUrl, true);
        button.textContent = installerLabel(button, true);
      });

      setLink(packageLinks.vst3, releaseState.vst3Url || releaseUrl, Boolean(releaseState.vst3Url));
      setLink(packageLinks.standalone, releaseState.standaloneUrl || releaseUrl, Boolean(releaseState.standaloneUrl));
      setLink(packageLinks.checksums, releaseState.checksumsUrl || releaseUrl, Boolean(releaseState.checksumsUrl));
      updateChecksumCommand(releaseState.installerUrl, releaseState.version);
      updateStructuredData();
      announceReleaseState();
      return;
    }

    const isPaused = releaseState.type === 'paused';
    banner?.setAttribute('data-state', isPaused ? 'paused' : 'error');
    if (title) title.textContent = isPaused ? text.pausedTitle : text.errorTitle;
    if (message) message.textContent = isPaused ? text.pausedMessage : text.errorMessage;

    installerButtons.forEach((button) => {
      setLink(button, releaseUrl, false);
      button.textContent = installerLabel(button, false);
    });

    setLink(packageLinks.vst3, releaseUrl, false);
    setLink(packageLinks.standalone, releaseUrl, false);
    setLink(packageLinks.checksums, releaseUrl, false);
    announceReleaseState();
  };

  const setLanguage = (language) => {
    if (!SUPPORTED_LANGUAGES.includes(language)) return;

    currentLanguage = language;
    document.documentElement.lang = language;

    translatableElements.forEach((element) => {
      element.textContent = element.dataset[language] || element.dataset.en || element.textContent;
    });

    languageButtons.forEach((button) => {
      button.setAttribute('aria-pressed', String(button.dataset.langButton === language));
    });

    try {
      localStorage.setItem(STORAGE_KEY, language);
    } catch (_) {
      // Language switching remains functional without storage.
    }

    renderReleaseState();
  };

  languageButtons.forEach((button) => {
    button.addEventListener('click', () => setLanguage(button.dataset.langButton));
  });

  setLanguage(chooseInitialLanguage());

  (async () => {
    try {
      const response = await fetch('./release.json', {
        cache: 'no-store',
        credentials: 'same-origin'
      });
      if (!response.ok) throw new Error(`Release metadata returned ${response.status}`);

      const release = await response.json();
      const releaseUrl = officialReleaseUrl(release.releaseUrl) || RELEASE_FALLBACK;
      const installerUrl = officialReleaseUrl(release.installerUrl, 'asset');
      const vst3Url = officialReleaseUrl(release.vst3Url, 'asset');
      const standaloneUrl = officialReleaseUrl(release.standaloneUrl, 'asset');
      const checksumsUrl = officialReleaseUrl(release.checksumsUrl, 'asset');

      if (release.version) {
        document.getElementById('release-version')?.replaceChildren(release.version);
      }

      releaseState = release.distributionEnabled === true && installerUrl
        ? {
            type: 'enabled',
            version: release.version,
            releaseUrl,
            installerUrl,
            vst3Url,
            standaloneUrl,
            checksumsUrl,
            purchaseCheckoutAvailable: release.purchaseCheckoutAvailable === true
          }
        : {
            type: 'paused',
            version: release.version,
            releaseUrl,
            purchaseCheckoutAvailable: release.purchaseCheckoutAvailable === true
          };

      renderReleaseState();
    } catch (_) {
      releaseState = {
        type: 'error',
        releaseUrl: RELEASE_FALLBACK,
        purchaseCheckoutAvailable: false
      };
      renderReleaseState();
    }
  })();
})();
