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

  const checkoutCopy = (release, checkoutUrl) => {
    const amount = Number.isFinite(release.activationPriceAmount)
      ? release.activationPriceAmount
      : release.activationPriceUsd;
    const price = Number.isFinite(amount)
      ? `${release.priceCurrency || 'USD'} ${amount}`
      : release.priceCurrency || '—';

    return currentLanguage === 'id'
      ? {
          title: 'Checkout resmi tersedia',
          status: 'Tinjau identitas penjual, jumlah final, pajak, refund, privasi, dan ketentuan penyedia sebelum membayar.',
          seller: 'Penjual',
          provider: 'Penyedia checkout',
          price: 'Harga publik',
          tax: 'Pajak',
          refund: 'Refund',
          taxValue: release.taxSummaryId,
          refundValue: release.refundSummaryId,
          button: 'Lanjut ke checkout aman',
          priceValue: price,
          checkoutUrl
        }
      : {
          title: 'Authorised checkout available',
          status: 'Review seller identity, final amount, tax, refund, privacy and provider terms before paying.',
          seller: 'Seller',
          provider: 'Checkout provider',
          price: 'Published price',
          tax: 'Tax',
          refund: 'Refund',
          taxValue: release.taxSummaryEn,
          refundValue: release.refundSummaryEn,
          button: 'Continue to secure checkout',
          priceValue: price,
          checkoutUrl
        };
  };

  const setMetadataForCheckout = (ready) => {
    const robots = document.querySelector('meta[name="robots"]');
    const description = document.querySelector('meta[name="description"]');

    if (robots) {
      robots.setAttribute(
        'content',
        ready
          ? 'index,follow,max-image-preview:large,max-snippet:-1'
          : 'noindex,follow'
      );
    }

    if (ready && description) {
      description.setAttribute(
        'content',
        currentLanguage === 'id'
          ? 'Aktivasi perpetual opsional ArSonKuPik bagi pengguna yang telah mengevaluasi produk dan ingin terus mengedit.'
          : 'Optional perpetual ArSonKuPik activation for users who have evaluated the product and want to keep editing.'
      );
    }
  };

  const renderCheckout = () => {
    const title = document.getElementById('activation-status-title');
    const status = document.getElementById('activation-status-copy');
    document.getElementById('checkout-ready')?.remove();

    const release = releaseState;
    if (!release || release.purchaseCheckoutAvailable !== true) {
      setMetadataForCheckout(false);
      if (title) title.textContent = currentLanguage === 'id' ? 'Checkout belum dibuka' : 'Checkout is not open yet';
      if (status) status.textContent = currentLanguage === 'id'
        ? 'Evaluasi gratis 365 hari tetap tersedia. Tidak ada pembayaran yang dapat dilakukan melalui halaman ini.'
        : 'The free 365-day evaluation remains available. No payment can be made through this page.';
      return;
    }

    const checkoutUrl = trustedCheckoutUrl(release);
    const ready = Boolean(checkoutUrl && release.purchasePageIndexable === true);
    setMetadataForCheckout(ready);

    if (!ready) {
      if (title) title.textContent = currentLanguage === 'id'
        ? 'Konfigurasi checkout belum lengkap'
        : 'Checkout configuration is incomplete';
      if (status) status.textContent = currentLanguage === 'id'
        ? 'Tautan pembayaran tidak ditampilkan sampai domain, identitas penjual, mata uang, pajak, refund, dan status index halaman tervalidasi.'
        : 'No payment link is shown until the domain, seller identity, currency, tax, refund and page-indexing status are validated.';
      return;
    }

    const text = checkoutCopy(release, checkoutUrl);
    if (title) title.textContent = text.title;
    if (status) status.textContent = text.status;

    const panel = document.createElement('div');
    panel.id = 'checkout-ready';
    panel.className = 'checkout-ready';

    const details = document.createElement('dl');
    for (const [label, value] of [
      [text.seller, release.sellerName],
      [text.provider, release.purchaseProvider],
      [text.price, text.priceValue],
      [text.tax, text.taxValue],
      [text.refund, text.refundValue]
    ]) {
      const term = document.createElement('dt');
      term.textContent = label;
      const description = document.createElement('dd');
      description.textContent = String(value);
      details.append(term, description);
    }

    const button = document.createElement('a');
    button.className = 'button primary';
    button.href = text.checkoutUrl;
    button.target = '_blank';
    button.rel = 'noopener noreferrer';
    button.textContent = text.button;

    panel.append(details, button);
    document.querySelector('.activation-status')?.after(panel);
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
      ? 'Aktivasi Opsional ArSonKuPik | Teruskan Editing'
      : 'Optional ArSonKuPik Activation | Keep Editing';

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

      const release = await response.json();
      releaseState = release;

      const amount = Number.isFinite(release.activationPriceAmount)
        ? release.activationPriceAmount
        : release.activationPriceUsd;
      const currency = typeof release.priceCurrency === 'string' ? release.priceCurrency : 'USD';

      if (Number.isFinite(amount)) {
        document.getElementById('activation-price')?.replaceChildren(`${currency} ${amount}`);
      }

      const freeDownload = document.getElementById('free-download-link');
      if (freeDownload) {
        const releaseUrl = officialReleaseUrl(release.releaseUrl) || RELEASE_FALLBACK;
        const installerUrl = officialReleaseUrl(release.installerUrl, true);
        freeDownload.href = release.distributionEnabled === true && installerUrl
          ? installerUrl
          : releaseUrl;
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