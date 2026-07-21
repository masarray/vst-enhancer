(() => {
  'use strict';

  const CANONICAL_URL = 'https://masarray.github.io/vst-enhancer/';
  const METADATA = {
    en: {
      title: 'ArSonKuPik — Musical VST3 Audio Enhancer for Windows',
      description: 'Achieve fuller, clearer and more dimensional sound without building a complex plug-in chain. Download ArSonKuPik VST3 and Standalone free for Windows.',
      socialTitle: 'ArSonKuPik — Musical VST3 Audio Enhancer',
      socialDescription: 'Fuller, clearer and more dimensional sound through one focused musical workflow for Windows VST3 and Standalone.'
    },
    id: {
      title: 'ArSonKuPik — VST3 Audio Enhancer Musikal untuk Windows',
      description: 'Buat audio lebih berisi, jernih, dan berdimensi tanpa rangkaian plug-in yang rumit. Unduh ArSonKuPik VST3 dan Standalone gratis untuk Windows.',
      socialTitle: 'ArSonKuPik — VST3 Audio Enhancer Musikal',
      socialDescription: 'Suara lebih berisi, jernih, dan berdimensi melalui satu workflow musikal yang fokus untuk Windows VST3 dan Standalone.'
    }
  };

  const latestReleaseScript = document.createElement('script');
  latestReleaseScript.src = 'latest-release.js';
  latestReleaseScript.async = true;
  latestReleaseScript.setAttribute('data-release-resolver', 'github-latest');
  document.head.append(latestReleaseScript);

  document.documentElement.setAttribute('data-visual-polish', 'v2-product-first');
  document.querySelectorAll('link[rel="alternate"][hreflang]').forEach((link) => link.remove());

  const canonical = document.getElementById('canonical-link');
  if (canonical) canonical.setAttribute('href', CANONICAL_URL);
  document.querySelector('meta[property="og:url"]')?.setAttribute('content', CANONICAL_URL);

  const currentUrl = new URL(window.location.href);
  if (currentUrl.searchParams.has('lang')) {
    currentUrl.searchParams.delete('lang');
    const query = currentUrl.searchParams.toString();
    history.replaceState(null, '', `${currentUrl.pathname}${query ? `?${query}` : ''}${currentUrl.hash}`);
  }

  document.documentElement.setAttribute('data-canonical-mode', 'single-url');

  const currentLanguage = () => document.documentElement.lang === 'id' ? 'id' : 'en';

  const translateDynamic = (root = document) => {
    const language = currentLanguage();
    root.querySelectorAll('[data-en][data-id]').forEach((element) => {
      element.textContent = element.dataset[language] || element.dataset.en || element.textContent;
    });
  };

  const setMeta = (selector, value) => {
    const element = document.querySelector(selector);
    if (element) element.setAttribute('content', value);
  };

  const applyMetadata = () => {
    const copy = METADATA[currentLanguage()];
    document.title = copy.title;
    setMeta('meta[name="description"]', copy.description);
    setMeta('meta[property="og:title"]', copy.socialTitle);
    setMeta('meta[property="og:description"]', copy.socialDescription);
    setMeta('meta[name="twitter:title"]', copy.socialTitle);
    setMeta('meta[name="twitter:description"]', copy.socialDescription);

    const dynamicReleaseStatus = document.getElementById('download-release-status');
    if (dynamicReleaseStatus) translateDynamic(dynamicReleaseStatus);
  };

  applyMetadata();
  new MutationObserver(applyMetadata).observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['lang']
  });

  const statusBar = document.getElementById('distribution-banner');
  if (statusBar) statusBar.hidden = true;

  const downloadHeading = document.querySelector('#download .section-heading');
  if (downloadHeading && !document.getElementById('download-release-status')) {
    const releaseStatus = document.createElement('div');
    releaseStatus.id = 'download-release-status';
    releaseStatus.className = 'download-release-status';
    releaseStatus.innerHTML = `
      <span data-en="Latest published release" data-id="Rilis publik terbaru">Latest published release</span>
      <strong id="download-release-version">v0.5.13</strong>
      <span aria-hidden="true">·</span>
      <span data-en="Direct Windows installer" data-id="Installer Windows langsung">Direct Windows installer</span>
      <span aria-hidden="true">·</span>
      <span data-en="SHA-256 available" data-id="SHA-256 tersedia">SHA-256 available</span>
      <a href="https://github.com/masarray/vst-enhancer/releases/latest"
         data-en="Release details"
         data-id="Detail rilis">Release details</a>
    `;

    translateDynamic(releaseStatus);
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
