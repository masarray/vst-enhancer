(() => {
  'use strict';

  const STORAGE_KEY = 'askp-language';
  const SUPPORTED = ['en', 'id'];
  const RELEASE_FALLBACK = 'https://github.com/masarray/vst-enhancer/releases/latest';
  const OFFICIAL_RELEASE_PATH = '/masarray/vst-enhancer/releases';
  const REQUIRED_CHECKOUT_FIELDS = [
    'purchaseUrl',
    'purchaseAllowedHosts',
    'sellerName',
    'purchaseProvider',
    'priceCurrency',
    'taxSummaryEn',
    'taxSummaryId',
    'refundSummaryEn',
    'refundSummaryId'
  ];

  let currentLanguage = 'en';
  let releaseState = null;

  const officialReleaseUrl = (value, asset = false) => {
    if (typeof value !== 'string' || value.length > 500) return null;
    try {
      const url = new URL(value);
      const releaseRoot = `${OFFICIAL_RELEASE_PATH}/`;
      const isOfficialPath = url.pathname === OFFICIAL_RELEASE_PATH || url.pathname.startsWith(releaseRoot);
      if (url.protocol !== 'https:' || url.hostname !== 'github.com' || !isOfficialPath) return null;
      if (asset && !url.pathname.includes('/releases/download/')) return null;
      return url.href;
    } catch (_) {
      return null;
    }
  };

  // Preserved for a future direct website checkout. The current release does not
  // publish purchaseUrl and instead initiates hosted Midtrans QRIS inside the app.
  const trustedCheckoutUrl = (release) => {
    if (!release || REQUIRED_CHECKOUT_FIELDS.some((field) => release[field] == null)) return null;
    if (!Array.isArray(release.purchaseAllowedHosts) || release.purchaseAllowedHosts.length === 0) return null;
    try {
      const url = new URL(release.purchaseUrl);
      const allowedHosts = release.purchaseAllowedHosts
        .filter((host) => typeof host === 'string')
        .map((host) => host.toLowerCase());
      if (url.protocol !== 'https:' || url.username || url.password) return null;
      if (url.port && url.port !== '443') return null;
      if (!allowedHosts.includes(url.hostname.toLowerCase())) return null;
      return url.href;
    } catch (_) {
      return null;
    }
  };

  const chooseLanguage = () => {
    const query = new URLSearchParams(location.search).get('lang');
    if (SUPPORTED.includes(query)) return query;
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (SUPPORTED.includes(stored)) return stored;
    } catch (_) {}
    return navigator.language?.toLowerCase().startsWith('id') ? 'id' : 'en';
  };

  const formattedPrice = (release) => {
    if (typeof release?.activationPriceFormatted === 'string' && release.activationPriceFormatted.trim()) {
      return release.activationPriceFormatted.trim();
    }
    const amount = Number(release?.activationPriceAmount);
    const currency = typeof release?.priceCurrency === 'string' ? release.priceCurrency : 'IDR';
    if (!Number.isFinite(amount)) return '—';
    try {
      return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency,
        maximumFractionDigits: 0
      }).format(amount).replace(/\u00a0/g, '');
    } catch (_) {
      return `${currency} ${amount}`;
    }
  };

  const setMetadataForCheckout = (ready) => {
    const robots = document.querySelector('meta[name="robots"]');
    const description = document.querySelector('meta[name="description"]');
    if (robots) {
      robots.setAttribute('content', ready
        ? 'index,follow,max-image-preview:large,max-snippet:-1'
        : 'noindex,follow');
    }
    if (description) {
      description.setAttribute('content', currentLanguage === 'id'
        ? 'Informasi aktivasi perpetual ArSonKuPik: Rp399.000, satu komputer aktif, dan checkout Midtrans QRIS dimulai dari aplikasi.'
        : 'ArSonKuPik perpetual activation information: IDR 399,000, one active computer, with hosted Midtrans QRIS checkout started inside the app.');
    }
  };

  const appendFact = (list, term, value) => {
    const dt = document.createElement('dt');
    dt.textContent = term;
    const dd = document.createElement('dd');
    dd.textContent = value;
    list.append(dt, dd);
  };

  const renderInAppCheckout = (release, title, status) => {
    setMetadataForCheckout(false);
    const price = formattedPrice(release);
    const provider = `${release.checkoutProvider || 'Midtrans'} ${release.checkoutMethod || 'QRIS'}`;
    const device = currentLanguage === 'id'
      ? 'Satu komputer aktif pada satu waktu'
      : 'One active computer at a time';

    if (title) title.textContent = currentLanguage === 'id'
      ? 'Checkout tersedia di dalam ArSonKuPik'
      : 'Checkout is available inside ArSonKuPik';
    if (status) status.textContent = currentLanguage === 'id'
      ? `Buka card aktivasi di aplikasi untuk memulai checkout ${provider}. Website ini tidak menampilkan tautan pembayaran langsung.`
      : `Open the activation card inside the application to start the hosted ${provider} checkout. This website does not expose a direct payment link.`;

    const panel = document.createElement('div');
    panel.id = 'checkout-ready';
    panel.className = 'checkout-ready';
    const details = document.createElement('dl');

    if (currentLanguage === 'id') {
      appendFact(details, 'Harga', price);
      appendFact(details, 'Perangkat', device);
      appendFact(details, 'Checkout', provider);
      appendFact(details, 'Aktivasi', 'Otomatis setelah pembayaran terverifikasi, dengan fallback manual');
    } else {
      appendFact(details, 'Price', price);
      appendFact(details, 'Device limit', device);
      appendFact(details, 'Checkout', provider);
      appendFact(details, 'Activation', 'Automatic after verified payment, with manual fallback');
    }

    const note = document.createElement('p');
    note.className = 'legal-note';
    note.textContent = currentLanguage === 'id'
      ? 'Evaluasi 365 hari tetap tersedia tanpa akun, kartu, langganan, atau tagihan otomatis. Pembelian hanya dimulai saat Anda memilihnya dari aplikasi.'
      : 'The 365-day evaluation remains available without an account, card, subscription or automatic charge. A purchase begins only when you deliberately start it inside the app.';

    const button = document.createElement('a');
    button.className = 'button primary';
    button.href = officialReleaseUrl(release.installerUrl, true) || officialReleaseUrl(release.releaseUrl) || RELEASE_FALLBACK;
    button.textContent = currentLanguage === 'id'
      ? 'Unduh atau buka ArSonKuPik'
      : 'Download or open ArSonKuPik';

    panel.append(details, note, button);
    document.querySelector('.activation-status')?.after(panel);
  };

  const renderDirectCheckout = (release, checkoutUrl, title, status) => {
    const ready = Boolean(checkoutUrl && release.purchasePageIndexable === true);
    setMetadataForCheckout(ready);
    if (!ready) {
      if (title) title.textContent = currentLanguage === 'id'
        ? 'Konfigurasi checkout belum lengkap'
        : 'Checkout configuration is incomplete';
      if (status) status.textContent = currentLanguage === 'id'
        ? 'Tautan pembayaran tidak ditampilkan sampai domain, penjual, mata uang, pajak, refund, dan status halaman tervalidasi.'
        : 'No payment link is shown until the domain, seller, currency, tax, refund and page status are validated.';
      return;
    }

    const panel = document.createElement('div');
    panel.id = 'checkout-ready';
    panel.className = 'checkout-ready';
    const details = document.createElement('dl');
    appendFact(details, currentLanguage === 'id' ? 'Penjual' : 'Seller', String(release.sellerName));
    appendFact(details, currentLanguage === 'id' ? 'Penyedia' : 'Provider', String(release.purchaseProvider));
    appendFact(details, currentLanguage === 'id' ? 'Harga' : 'Price', formattedPrice(release));
    appendFact(details, currentLanguage === 'id' ? 'Pajak' : 'Tax', String(currentLanguage === 'id' ? release.taxSummaryId : release.taxSummaryEn));
    appendFact(details, 'Refund', String(currentLanguage === 'id' ? release.refundSummaryId : release.refundSummaryEn));

    const button = document.createElement('a');
    button.className = 'button primary';
    button.href = checkoutUrl;
    button.target = '_blank';
    button.rel = 'noopener noreferrer';
    button.textContent = currentLanguage === 'id' ? 'Lanjut ke checkout aman' : 'Continue to secure checkout';
    panel.append(details, button);
    document.querySelector('.activation-status')?.after(panel);
  };

  const renderCheckout = () => {
    const title = document.getElementById('activation-status-title');
    const status = document.getElementById('activation-status-copy');
    document.getElementById('checkout-ready')?.remove();
    const release = releaseState;

    if (!release) {
      setMetadataForCheckout(false);
      if (title) title.textContent = currentLanguage === 'id' ? 'Status aktivasi tidak tersedia' : 'Activation status unavailable';
      if (status) status.textContent = currentLanguage === 'id'
        ? 'Buka ArSonKuPik untuk melihat informasi aktivasi terbaru.'
        : 'Open ArSonKuPik to review the latest activation information.';
      return;
    }

    if (release.inAppCheckoutAvailable === true) {
      renderInAppCheckout(release, title, status);
      return;
    }

    if (release.purchaseCheckoutAvailable === true) {
      renderDirectCheckout(release, trustedCheckoutUrl(release), title, status);
      return;
    }

    setMetadataForCheckout(false);
    if (title) title.textContent = currentLanguage === 'id' ? 'Checkout sedang tidak tersedia' : 'Checkout is currently unavailable';
    if (status) status.textContent = currentLanguage === 'id'
      ? 'Evaluasi gratis 365 hari tetap tersedia dan tidak berubah menjadi pembayaran otomatis.'
      : 'The free 365-day evaluation remains available and never converts into an automatic payment.';
  };

  const setLanguage = (language) => {
    if (!SUPPORTED.includes(language)) return;
    currentLanguage = language;
    document.documentElement.lang = language;
    document.querySelectorAll('[data-en][data-id]').forEach((element) => {
      element.textContent = element.dataset[language] || element.dataset.en || element.textContent;
    });
    document.querySelectorAll('[data-lang-button]').forEach((button) => {
      button.setAttribute('aria-pressed', String(button.dataset.langButton === language));
    });
    try { localStorage.setItem(STORAGE_KEY, language); } catch (_) {}
    document.title = language === 'id'
      ? 'Aktivasi Opsional ArSonKuPik | Rp399.000'
      : 'Optional ArSonKuPik Activation | IDR 399,000';
    renderCheckout();
  };

  document.querySelectorAll('[data-lang-button]').forEach((button) => {
    button.addEventListener('click', () => setLanguage(button.dataset.langButton));
  });

  setLanguage(chooseLanguage());

  (async () => {
    try {
      const response = await fetch('../release.json', { cache: 'no-store', credentials: 'same-origin' });
      if (!response.ok) throw new Error(`Release metadata returned ${response.status}`);
      releaseState = await response.json();
      document.getElementById('activation-price')?.replaceChildren(formattedPrice(releaseState));
      const freeDownload = document.getElementById('free-download-link');
      if (freeDownload) {
        const releaseUrl = officialReleaseUrl(releaseState.releaseUrl) || RELEASE_FALLBACK;
        const installerUrl = officialReleaseUrl(releaseState.installerUrl, true);
        freeDownload.href = releaseState.distributionEnabled === true && installerUrl ? installerUrl : releaseUrl;
      }
      renderCheckout();
    } catch (_) {
      releaseState = null;
      const freeDownload = document.getElementById('free-download-link');
      if (freeDownload) freeDownload.href = RELEASE_FALLBACK;
      renderCheckout();
    }
  })();
})();
