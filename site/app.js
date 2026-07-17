(() => {
  'use strict';

  const STORAGE_KEY = 'askp-language';
  const SUPPORTED_LANGUAGES = ['en', 'id'];
  const SITE_URL = 'https://masarray.github.io/vst-enhancer/';
  const RELEASE_FALLBACK = 'https://github.com/masarray/vst-enhancer/releases/latest';
  const OFFICIAL_RELEASE_PATH = '/masarray/vst-enhancer/releases';

  const languageButtons = [...document.querySelectorAll('[data-lang-button]')];
  const translatableElements = [...document.querySelectorAll('[data-en][data-id]')];
  const installerButtons = [
    document.getElementById('installer-link'),
    document.getElementById('installer-link-bottom'),
    document.getElementById('installer-link-final')
  ].filter(Boolean);

  const packageLinks = {
    vst3: document.getElementById('vst3-link'),
    standalone: document.getElementById('standalone-link'),
    checksums: document.getElementById('checksums-link')
  };

  const copy = {
    en: {
      title: 'ArSonKuPik VST3 Audio Enhancer | Free 365-Day Evaluation',
      description: 'ArSonKuPik is a Windows VST3 and standalone audio enhancer for mastering, mix bus, vocals, tracks and podcasts. Try every preset and control for 365 days, no card.',
      socialTitle: 'ArSonKuPik VST3 Audio Enhancer',
      socialDescription: 'A focused Windows VST3 and standalone enhancer with a transparent 365-day evaluation. No card, subscription or automatic charge.',
      checkingTitle: 'Release status',
      checkingMessage: 'Checking official distribution status…',
      enabledTitle: 'Official evaluation download available',
      enabledMessage: 'Download only from the official GitHub Release and verify SHA-256 before running the file.',
      pausedTitle: 'Official download temporarily paused',
      pausedMessage: 'Open the release page for the current validation and packaging status.',
      errorTitle: 'Release status unavailable',
      errorMessage: 'Open the official Releases page before downloading.',
      installerEnabled: 'Download Windows installer',
      installerPaused: 'View official release status',
      paidUnavailable: 'Paid checkout is not currently enabled; the free evaluation download is available separately.',
      paidAvailable: 'Paid checkout is available only through the authorised link and terms shown before payment.'
    },
    id: {
      title: 'ArSonKuPik Audio Enhancer VST3 | Evaluasi Gratis 365 Hari',
      description: 'ArSonKuPik adalah audio enhancer VST3 dan standalone untuk Windows, mastering, mix bus, vokal, track, dan podcast. Evaluasi seluruh preset dan kontrol selama 365 hari tanpa kartu atau langganan.',
      socialTitle: 'ArSonKuPik Audio Enhancer VST3',
      socialDescription: 'Audio enhancer Windows VST3 dan standalone dengan evaluasi transparan 365 hari. Tanpa kartu, langganan, atau tagihan otomatis.',
      checkingTitle: 'Status rilis',
      checkingMessage: 'Memeriksa status distribusi resmi…',
      enabledTitle: 'Unduhan evaluasi resmi tersedia',
      enabledMessage: 'Unduh hanya dari GitHub Release resmi dan verifikasi SHA-256 sebelum menjalankan file.',
      pausedTitle: 'Unduhan resmi dijeda sementara',
      pausedMessage: 'Buka halaman rilis untuk melihat status validasi dan packaging terbaru.',
      errorTitle: 'Status rilis tidak tersedia',
      errorMessage: 'Buka halaman Releases resmi sebelum mengunduh.',
      installerEnabled: 'Unduh installer Windows',
      installerPaused: 'Lihat status rilis resmi',
      paidUnavailable: 'Checkout berbayar saat ini belum diaktifkan; unduhan evaluasi gratis tersedia secara terpisah.',
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
      if (url.protocol !== 'https:' || url.hostname !== 'github.com') return null;
      if (!url.pathname.startsWith(OFFICIAL_RELEASE_PATH)) return null;
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

  const localizedUrl = (language) => {
    const url = new URL(SITE_URL);
    url.searchParams.set('lang', language);
    return url.href;
  };

  const updateStructuredData = (language) => {
    const script = document.getElementById('software-structured-data');
    if (!script) return;

    try {
      const data = JSON.parse(script.textContent);
      const software = data['@graph']?.find((entry) => entry['@type'] === 'SoftwareApplication');
      if (software) {
        software.url = localizedUrl(language);
        software.inLanguage = language;
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

  const setMetadata = (language) => {
    const text = copy[language];
    const pageUrl = localizedUrl(language);
    document.title = text.title;
    document.querySelector('meta[name="description"]')?.setAttribute('content', text.description);
    document.querySelector('meta[property="og:title"]')?.setAttribute('content', text.socialTitle);
    document.querySelector('meta[property="og:description"]')?.setAttribute('content', text.socialDescription);
    document.querySelector('meta[property="og:url"]')?.setAttribute('content', pageUrl);
    document.querySelector('meta[property="og:locale"]')?.setAttribute('content', language === 'id' ? 'id_ID' : 'en_US');
    document.querySelector('meta[name="twitter:title"]')?.setAttribute('content', text.socialTitle);
    document.querySelector('meta[name="twitter:description"]')?.setAttribute('content', text.socialDescription);
    document.getElementById('canonical-link')?.setAttribute('href', pageUrl);
    updateStructuredData(language);
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
      purchaseStatus.setAttribute('data-checkout-state', releaseState.purchaseCheckoutAvailable ? 'available' : 'unavailable');
    }

    if (releaseState.type === 'enabled' && releaseState.installerUrl) {
      banner?.setAttribute('data-state', 'enabled');
      if (title) title.textContent = text.enabledTitle;
      if (message) message.textContent = text.enabledMessage;
      installerButtons.forEach((button) => {
        setLink(button, releaseState.installerUrl, true);
        button.textContent = text.installerEnabled;
      });
      setLink(packageLinks.vst3, releaseState.vst3Url || releaseUrl, Boolean(releaseState.vst3Url));
      setLink(packageLinks.standalone, releaseState.standaloneUrl || releaseUrl, Boolean(releaseState.standaloneUrl));
      setLink(packageLinks.checksums, releaseState.checksumsUrl || releaseUrl, Boolean(releaseState.checksumsUrl));
      updateChecksumCommand(releaseState.installerUrl, releaseState.version);
      updateStructuredData(currentLanguage);
      return;
    }

    const isPaused = releaseState.type === 'paused';
    banner?.setAttribute('data-state', isPaused ? 'paused' : 'error');
    if (title) title.textContent = isPaused ? text.pausedTitle : text.errorTitle;
    if (message) message.textContent = isPaused ? text.pausedMessage : text.errorMessage;
    installerButtons.forEach((button) => {
      setLink(button, releaseUrl, false);
      button.textContent = text.installerPaused;
    });
    setLink(packageLinks.vst3, releaseUrl, false);
    setLink(packageLinks.standalone, releaseUrl, false);
    setLink(packageLinks.checksums, releaseUrl, false);
  };

  const setLanguage = (language, updateUrl = true) => {
    if (!SUPPORTED_LANGUAGES.includes(language)) return;
    currentLanguage = language;
    document.documentElement.lang = language;

    translatableElements.forEach((element) => {
      element.textContent = element.dataset[language] || element.dataset.en || element.textContent;
    });

    languageButtons.forEach((button) => {
      button.setAttribute('aria-pressed', String(button.dataset.langButton === language));
    });

    try { localStorage.setItem(STORAGE_KEY, language); } catch (_) {}

    if (updateUrl) {
      const url = new URL(window.location.href);
      url.searchParams.set('lang', language);
      history.replaceState(null, '', `${url.pathname}${url.search}${url.hash}`);
    }

    setMetadata(language);
    renderReleaseState();
  };

  languageButtons.forEach((button) => {
    button.addEventListener('click', () => setLanguage(button.dataset.langButton));
  });

  setLanguage(chooseInitialLanguage(), false);

  (async () => {
    try {
      const response = await fetch('./release.json', { cache: 'no-store', credentials: 'same-origin' });
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
