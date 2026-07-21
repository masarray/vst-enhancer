(() => {
  'use strict';

  const ROOT_URL = 'https://masarray.github.io/vst-enhancer/';
  const ID_URL = `${ROOT_URL}id/`;
  const siteBase = document.documentElement.dataset.siteBase || (location.pathname.includes('/id/') ? '..' : '.');
  const pageLanguage = location.pathname.includes('/id/') ? 'id' : 'en';

  const latestReleaseScript = document.createElement('script');
  latestReleaseScript.src = `${siteBase}/latest-release.js`;
  latestReleaseScript.async = true;
  latestReleaseScript.setAttribute('data-release-resolver', 'github-latest');
  document.head.append(latestReleaseScript);

  const experienceScript = document.createElement('script');
  experienceScript.src = `${siteBase}/experience-v4.js`;
  experienceScript.defer = true;
  experienceScript.setAttribute('data-experience-loader', 'v4-audio-motion');
  document.head.append(experienceScript);

  document.documentElement.setAttribute('data-visual-polish', 'v4-audio-motion');

  const translateToPageLanguage = (root = document) => {
    document.documentElement.lang = pageLanguage;
    root.querySelectorAll('[data-en][data-id]').forEach((element) => {
      element.textContent = element.dataset[pageLanguage] || element.dataset.en || element.textContent;
    });
    root.querySelectorAll('[data-lang-button]').forEach((button) => {
      button.setAttribute('aria-pressed', String(button.dataset.langButton === pageLanguage));
    });
  };

  const ensureAlternate = (language, href) => {
    let link = document.querySelector(`link[rel="alternate"][hreflang="${language}"]`);
    if (!link) {
      link = document.createElement('link');
      link.rel = 'alternate';
      link.hreflang = language;
      document.head.append(link);
    }
    link.href = href;
  };

  ensureAlternate('en', ROOT_URL);
  ensureAlternate('id', ID_URL);
  ensureAlternate('x-default', ROOT_URL);

  document.querySelectorAll('[data-lang-button]').forEach((control) => {
    control.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopImmediatePropagation();
      const language = control.dataset.langButton === 'id' ? 'id' : 'en';
      try { localStorage.setItem('askp-language', language); } catch (_) {}
      window.location.assign(language === 'id' ? ID_URL : ROOT_URL);
    }, true);
  });

  translateToPageLanguage();
  document.addEventListener('askp:release-ready', () => translateToPageLanguage(), { passive: true });

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
    translateToPageLanguage(releaseStatus);
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