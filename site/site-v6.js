(() => {
  'use strict';

  const root = document.documentElement;
  const siteBase = root.dataset.siteBase || '.';
  const language = root.lang === 'id' ? 'id' : 'en';
  const RELEASE_FALLBACK = 'https://github.com/masarray/vst-enhancer/releases/latest';
  const OFFICIAL_RELEASE_PATH = '/masarray/vst-enhancer/releases';

  const copy = language === 'id'
    ? {
        enabled: 'Rilis resmi tersedia',
        paused: 'Unduhan resmi sedang dijeda',
        error: 'Status rilis tidak dapat diperiksa',
        installer: 'Unduh gratis untuk Windows',
        installerShort: 'Unduh gratis'
      }
    : {
        enabled: 'Official release available',
        paused: 'Official download is temporarily paused',
        error: 'Release status could not be checked',
        installer: 'Download free for Windows',
        installerShort: 'Download free'
      };

  const officialReleaseUrl = (value, asset = false) => {
    if (typeof value !== 'string' || value.length > 500) return null;
    try {
      const url = new URL(value);
      const validPath = url.pathname === OFFICIAL_RELEASE_PATH || url.pathname.startsWith(`${OFFICIAL_RELEASE_PATH}/`);
      if (url.protocol !== 'https:' || url.hostname !== 'github.com' || !validPath) return null;
      if (asset && !url.pathname.includes('/releases/download/')) return null;
      return url.href;
    } catch (_) {
      return null;
    }
  };

  const setLink = (element, href, enabled = true) => {
    if (!element) return;
    element.href = href || RELEASE_FALLBACK;
    if (enabled) {
      element.removeAttribute('aria-disabled');
      element.removeAttribute('data-release-pending');
    } else {
      element.setAttribute('aria-disabled', 'true');
      element.setAttribute('data-release-pending', 'true');
    }
  };

  const updateStructuredData = (version, releaseUrl) => {
    const script = document.getElementById('software-structured-data');
    if (!script) return;
    try {
      const data = JSON.parse(script.textContent);
      const software = data['@graph']?.find((entry) => entry['@type'] === 'SoftwareApplication');
      if (!software) return;
      if (version) software.softwareVersion = version.replace(/^v/i, '');
      if (releaseUrl) {
        software.downloadUrl = releaseUrl;
        software.releaseNotes = releaseUrl;
        if (software.offers) software.offers.url = releaseUrl;
      }
      script.textContent = JSON.stringify(data, null, 2);
    } catch (_) {
      // Static JSON-LD remains valid when enhancement fails.
    }
  };

  const updateChecksumCommand = (installerUrl, version) => {
    const command = document.getElementById('checksum-command');
    if (!command) return;
    let filename = version ? `ArSonKuPik-${version}-Windows-x64-Setup.exe` : 'ArSonKuPik-Windows-x64-Setup.exe';
    try {
      if (installerUrl) filename = decodeURIComponent(new URL(installerUrl).pathname.split('/').pop());
    } catch (_) {}
    command.textContent = `Get-FileHash .\\${filename} -Algorithm SHA256`;
  };

  const renderRelease = (state) => {
    const installerButtons = [...document.querySelectorAll('[data-installer-cta]')];
    const installerUrl = state.installerUrl || state.releaseUrl || RELEASE_FALLBACK;
    const enabled = state.type === 'enabled' && Boolean(state.installerUrl);

    installerButtons.forEach((button) => {
      setLink(button, installerUrl, enabled);
      button.textContent = button.closest('#mobile-download-bar') || button.classList.contains('nav-download')
        ? copy.installerShort
        : copy.installer;
    });

    setLink(document.getElementById('vst3-link'), state.vst3Url || state.releaseUrl, Boolean(state.vst3Url));
    setLink(document.getElementById('standalone-link'), state.standaloneUrl || state.releaseUrl, Boolean(state.standaloneUrl));
    setLink(document.getElementById('checksums-link'), state.checksumsUrl || state.releaseUrl, Boolean(state.checksumsUrl));
    setLink(document.getElementById('release-link'), state.releaseUrl || RELEASE_FALLBACK, true);
    setLink(document.getElementById('distribution-link'), state.releaseUrl || RELEASE_FALLBACK, true);

    document.querySelectorAll('[data-release-version]').forEach((element) => {
      if (state.version) element.textContent = state.version;
    });

    const statusText = state.type === 'enabled' ? copy.enabled : state.type === 'paused' ? copy.paused : copy.error;
    document.querySelectorAll('[data-release-status]').forEach((element) => {
      element.textContent = statusText;
    });

    const banner = document.getElementById('distribution-banner');
    if (banner) banner.dataset.state = state.type;

    updateChecksumCommand(state.installerUrl, state.version);
    updateStructuredData(state.version, state.releaseUrl);
    document.dispatchEvent(new CustomEvent('askp:release-ready', { detail: state }));
  };

  const setupMobileNavigation = () => {
    const menu = document.querySelector('.mobile-nav');
    if (!menu) return;
    menu.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => menu.removeAttribute('open')));
    document.addEventListener('click', (event) => {
      if (menu.open && !menu.contains(event.target)) menu.removeAttribute('open');
    });
  };

  const setupMobileDownload = () => {
    const bar = document.getElementById('mobile-download-bar');
    const heroCta = document.getElementById('installer-link-bottom');
    if (!bar || !heroCta) return;
    bar.hidden = false;
    const setVisible = (visible) => {
      bar.dataset.visible = String(visible);
      bar.setAttribute('aria-hidden', String(!visible));
    };
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(([entry]) => setVisible(!entry.isIntersecting), { threshold: .15 }).observe(heroCta);
    } else {
      setVisible(true);
    }
  };

  setupMobileNavigation();
  setupMobileDownload();

  (async () => {
    try {
      const response = await fetch(`${siteBase}/release.json`, { cache: 'no-store', credentials: 'same-origin' });
      if (!response.ok) throw new Error(`Release metadata returned ${response.status}`);
      const release = await response.json();
      const releaseUrl = officialReleaseUrl(release.releaseUrl) || RELEASE_FALLBACK;
      const installerUrl = officialReleaseUrl(release.installerUrl, true);
      const state = release.distributionEnabled === true && installerUrl
        ? {
            type: 'enabled',
            version: release.version,
            releaseUrl,
            installerUrl,
            vst3Url: officialReleaseUrl(release.vst3Url, true),
            standaloneUrl: officialReleaseUrl(release.standaloneUrl, true),
            checksumsUrl: officialReleaseUrl(release.checksumsUrl, true)
          }
        : { type: 'paused', version: release.version, releaseUrl };
      renderRelease(state);
    } catch (_) {
      renderRelease({ type: 'error', releaseUrl: RELEASE_FALLBACK });
    }
  })();
})();
