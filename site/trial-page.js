(() => {
  'use strict';

  const CANONICAL_URL = 'https://masarray.github.io/vst-enhancer/';

  const latestReleaseScript = document.createElement('script');
  latestReleaseScript.src = 'latest-release.js';
  latestReleaseScript.async = true;
  latestReleaseScript.setAttribute('data-release-resolver', 'github-latest');
  document.head.append(latestReleaseScript);

  const premiumStylesheet = document.createElement('link');
  premiumStylesheet.rel = 'stylesheet';
  premiumStylesheet.href = 'premium-polish.css';
  premiumStylesheet.setAttribute('data-visual-layer', 'p1-premium');
  document.head.append(premiumStylesheet);
  document.documentElement.setAttribute('data-visual-polish', 'p1');

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

  const statusBar = document.getElementById('distribution-banner');
  if (statusBar) statusBar.hidden = true;

  for (const selector of [
    '.hero-promises',
    '.hero-trust',
    '.product-stage .stage-label',
    '.product-stage figcaption'
  ]) {
    const element = document.querySelector(selector);
    if (element) element.hidden = true;
  }

  const language = document.documentElement.lang === 'id' ? 'id' : 'en';
  const trustFacts = [
    {
      en: ['Windows 10/11 x64', 'Installer and manual packages for 64-bit Windows.'],
      id: ['Windows 10/11 x64', 'Installer dan paket manual untuk Windows 64-bit.']
    },
    {
      en: ['VST3 + Standalone', 'Use it inside a DAW or as a separate application.'],
      id: ['VST3 + Standalone', 'Gunakan di dalam DAW atau sebagai aplikasi terpisah.']
    },
    {
      en: ['Local processing', 'No intentional audio upload or automatic telemetry.'],
      id: ['Processing lokal', 'Tanpa unggahan audio atau telemetri otomatis yang disengaja.']
    },
    {
      en: ['Official releases', 'Direct installer with SHA-256 verification.'],
      id: ['Rilis resmi', 'Installer langsung dengan verifikasi SHA-256.']
    }
  ];

  const trustStrip = document.querySelector('.trust-strip');
  if (trustStrip) {
    trustStrip.setAttribute('aria-label', 'Product compatibility and trust');
    trustStrip.querySelectorAll('.trust-grid > div').forEach((card, index) => {
      const fact = trustFacts[index];
      const title = card.querySelector('strong');
      const copy = card.querySelector('span');
      if (!fact || !title || !copy) return;

      title.dataset.en = fact.en[0];
      title.dataset.id = fact.id[0];
      title.textContent = fact[language][0];

      copy.dataset.en = fact.en[1];
      copy.dataset.id = fact.id[1];
      copy.textContent = fact[language][1];
    });
  }

  const downloadHeading = document.querySelector('#download .section-heading');
  if (downloadHeading && !document.getElementById('download-release-status')) {
    const releaseStatus = document.createElement('div');
    releaseStatus.id = 'download-release-status';
    releaseStatus.className = 'download-release-status';
    releaseStatus.innerHTML = `
      <span data-en="Latest published release" data-id="Rilis publik terbaru">Latest published release</span>
      <strong id="download-release-version">v0.5.12</strong>
      <span aria-hidden="true">·</span>
      <span data-en="Direct Windows installer" data-id="Installer Windows langsung">Direct Windows installer</span>
      <span aria-hidden="true">·</span>
      <span data-en="SHA-256 available" data-id="SHA-256 tersedia">SHA-256 available</span>
      <a href="https://github.com/masarray/vst-enhancer/releases/latest"
         data-en="Release details"
         data-id="Detail rilis">Release details</a>
    `;
    releaseStatus.querySelectorAll('[data-en][data-id]').forEach((element) => {
      element.textContent = element.dataset[language] || element.dataset.en || element.textContent;
    });
    downloadHeading.after(releaseStatus);

    const sourceVersion = document.getElementById('release-version');
    const targetVersion = document.getElementById('download-release-version');
    const syncVersion = () => {
      if (sourceVersion && targetVersion) targetVersion.textContent = sourceVersion.textContent;
    };
    syncVersion();

    if (sourceVersion && targetVersion) {
      new MutationObserver(syncVersion).observe(sourceVersion, {
        childList: true,
        characterData: true,
        subtree: true
      });
    }
  }

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
