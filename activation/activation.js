(() => {
  'use strict';

  const root = document.documentElement;
  const language = root.lang.toLowerCase().startsWith('id') ? 'id' : 'en';
  const siteBase = root.dataset.siteBase || '..';
  const releaseFallback = 'https://github.com/masarray/vst-enhancer/releases/latest';
  const officialReleasePath = '/masarray/vst-enhancer/releases';
  const requiredCheckoutFields = [
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

  let releaseState = null;

  const formatPrice = (amount, currency) => {
    if (!Number.isFinite(amount)) return currency || '—';
    try {
      return new Intl.NumberFormat(currency === 'IDR' ? 'id-ID' : 'en-US', {
        style: 'currency',
        currency: currency || 'USD',
        maximumFractionDigits: currency === 'IDR' ? 0 : 2
      }).format(amount);
    } catch (_) {
      return `${currency || 'USD'} ${amount}`;
    }
  };

  const officialReleaseUrl = (value, asset = false) => {
    if (typeof value !== 'string' || value.length > 500) return null;
    try {
      const url = new URL(value);
      const releaseRoot = `${officialReleasePath}/`;
      const officialPath = url.pathname === officialReleasePath || url.pathname.startsWith(releaseRoot);
      if (url.protocol !== 'https:' || url.hostname !== 'github.com' || !officialPath) return null;
      if (asset && !url.pathname.includes('/releases/download/')) return null;
      return url.href;
    } catch (_) {
      return null;
    }
  };

  const trustedCheckoutUrl = (release) => {
    if (!release || requiredCheckoutFields.some((field) => release[field] == null)) return null;
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

  const checkoutCopy = (release, checkoutUrl) => {
    const amount = Number.isFinite(release.activationPriceAmount)
      ? release.activationPriceAmount
      : release.activationPriceUsd;
    const price = formatPrice(amount, release.priceCurrency || 'USD');

    return language === 'id'
      ? {
          title: 'Checkout resmi tersedia',
          status: 'Tinjau identitas penjual, jumlah final, pajak, refund, privasi, dan ketentuan penyedia sebelum membayar.',
          labels: ['Penjual', 'Penyedia checkout', 'Harga publik', 'Pajak', 'Refund'],
          values: [release.sellerName, release.purchaseProvider, price, release.taxSummaryId, release.refundSummaryId],
          button: 'Lanjut ke checkout aman',
          checkoutUrl
        }
      : {
          title: 'Authorised checkout available',
          status: 'Review seller identity, final amount, tax, refund, privacy and provider terms before paying.',
          labels: ['Seller', 'Checkout provider', 'Published price', 'Tax', 'Refund'],
          values: [release.sellerName, release.purchaseProvider, price, release.taxSummaryEn, release.refundSummaryEn],
          button: 'Continue to secure checkout',
          checkoutUrl
        };
  };

  const renderCheckout = () => {
    const title = document.getElementById('activation-status-title');
    const status = document.getElementById('activation-status-copy');
    document.getElementById('checkout-ready')?.remove();

    const release = releaseState;
    if (!release || release.purchaseCheckoutAvailable !== true) {
      const inAppAvailable = release?.purchaseStatus === 'available-in-app';
      if (title) {
        title.textContent = language === 'id'
          ? (inAppAvailable ? 'Checkout tersedia di dalam ArSonKuPik' : 'Checkout belum dibuka')
          : (inAppAvailable ? 'Checkout is available inside ArSonKuPik' : 'Checkout is not open yet');
      }
      if (status) {
        status.textContent = language === 'id'
          ? (inAppAvailable
              ? 'Buka kartu Unlock di VST3 atau Standalone untuk checkout hosted dan pemulihan order. Website ini tidak menerima data pembayaran.'
              : 'Evaluasi gratis tetap tersedia. Tidak ada pembayaran yang dapat dilakukan melalui halaman ini.')
          : (inAppAvailable
              ? 'Open the Unlock card in the VST3 or Standalone app for hosted checkout and order recovery. This website does not collect payment data.'
              : 'The free evaluation remains available. No payment can be made through this page.');
      }
      return;
    }

    const checkoutUrl = trustedCheckoutUrl(release);
    const ready = Boolean(checkoutUrl && release.purchasePageIndexable === true);
    if (!ready) {
      if (title) title.textContent = language === 'id'
        ? 'Konfigurasi checkout belum lengkap'
        : 'Checkout configuration is incomplete';
      if (status) status.textContent = language === 'id'
        ? 'Tautan pembayaran tidak ditampilkan sampai domain, identitas penjual, mata uang, pajak, refund, dan keamanan checkout tervalidasi.'
        : 'No payment link is shown until the domain, seller identity, currency, tax, refund and checkout security are validated.';
      return;
    }

    const copy = checkoutCopy(release, checkoutUrl);
    if (title) title.textContent = copy.title;
    if (status) status.textContent = copy.status;

    const panel = document.createElement('div');
    panel.id = 'checkout-ready';
    panel.className = 'checkout-ready';

    const details = document.createElement('dl');
    copy.labels.forEach((label, index) => {
      const term = document.createElement('dt');
      term.textContent = label;
      const description = document.createElement('dd');
      description.textContent = String(copy.values[index] ?? '');
      details.append(term, description);
    });

    const button = document.createElement('a');
    button.className = 'button primary';
    button.href = copy.checkoutUrl;
    button.target = '_blank';
    button.rel = 'noopener noreferrer';
    button.textContent = copy.button;

    panel.append(details, button);
    document.querySelector('.activation-status')?.after(panel);
  };

  const loadRelease = async () => {
    try {
      const response = await fetch(`${siteBase}/release.json`, {
        cache: 'no-store',
        credentials: 'same-origin'
      });
      if (!response.ok) throw new Error(`Release metadata returned ${response.status}`);

      releaseState = await response.json();
      const amount = Number.isFinite(releaseState.activationPriceAmount)
        ? releaseState.activationPriceAmount
        : releaseState.activationPriceUsd;
      const currency = typeof releaseState.priceCurrency === 'string'
        ? releaseState.priceCurrency
        : 'USD';

      if (Number.isFinite(amount)) {
        document.getElementById('activation-price')?.replaceChildren(formatPrice(amount, currency));
      }

      const freeDownload = document.getElementById('free-download-link');
      if (freeDownload) {
        const releaseUrl = officialReleaseUrl(releaseState.releaseUrl) || releaseFallback;
        const installerUrl = officialReleaseUrl(releaseState.installerUrl, true);
        freeDownload.href = releaseState.distributionEnabled === true && installerUrl
          ? installerUrl
          : releaseUrl;
      }
    } catch (_) {
      releaseState = null;
      const freeDownload = document.getElementById('free-download-link');
      if (freeDownload) freeDownload.href = releaseFallback;
    }

    renderCheckout();
  };

  loadRelease();
})();
