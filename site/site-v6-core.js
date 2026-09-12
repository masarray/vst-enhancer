(() => {
  'use strict';

  const root = document.documentElement;
  const siteBase = root.dataset.siteBase || '.';
  const language = root.lang === 'id' ? 'id' : 'en';
  const REPOSITORY = 'masarray/vst-enhancer';
  const RELEASES_ROOT = `https://github.com/${REPOSITORY}/releases`;
  const RELEASE_FALLBACK = `${RELEASES_ROOT}/latest`;
  const VERSION_RE = /^v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$/;

  const copy = language === 'id'
    ? {
        enabled: 'Rilis resmi tersedia',
        paused: 'Unduhan resmi sedang dijeda',
        error: 'Status rilis tidak dapat diperiksa'
      }
    : {
        enabled: 'Official release available',
        paused: 'Official download is temporarily paused',
        error: 'Release status could not be checked'
      };

  const officialReleaseUrl = (value, version, asset = false) => {
    if (typeof value !== 'string' || value.length > 800 || !VERSION_RE.test(version || '')) return null;
    try {
      const url = new URL(value);
      if (url.protocol !== 'https:' || url.hostname !== 'github.com') return null;
      const releasePath = `/${REPOSITORY}/releases/tag/${version}`;
      const assetPrefix = `/${REPOSITORY}/releases/download/${version}/`;
      const valid = asset ? url.pathname.startsWith(assetPrefix) : url.pathname === releasePath;
      return valid ? url.href : null;
    } catch (_) {
      return null;
    }
  };

  const parseManifest = (payload) => {
    if (!payload || typeof payload !== 'object') return null;
    const version = String(payload.version || '');
    if (!VERSION_RE.test(version) || Number(payload.schemaVersion || 0) < 3) return null;

    const platforms = new Set(Array.isArray(payload.platforms) ? payload.platforms : []);
    if (!platforms.has('windows-x64') || !platforms.has('macos-universal')) return null;

    const releaseUrl = officialReleaseUrl(payload.releaseUrl, version, false);
    if (!releaseUrl) return null;

    const asset = (key) => officialReleaseUrl(payload[key], version, true);
    const enabled = payload.distributionEnabled === true && payload.distributionStatus !== 'paused';
    const installerUrl = asset('installerUrl');

    if (enabled && !installerUrl) return null;

    return {
      type: enabled ? 'enabled' : 'paused',
      source: 'local-release-manifest',
      version,
      releaseUrl,
      installerUrl,
      vst3Url: asset('vst3Url'),
      standaloneUrl: asset('standaloneUrl'),
      macDmgUrl: asset('macDmgUrl'),
      macVst3Url: asset('macVst3Url'),
      macStandaloneUrl: asset('macStandaloneUrl'),
      checksumsUrl: asset('checksumsUrl')
    };
  };

  const setLink = (element, href, enabled = true) => {
    if (!element) return;
    if (enabled && href) {
      element.href = href;
      element.removeAttribute('aria-disabled');
      element.removeAttribute('data-release-pending');
    } else {
      element.href = RELEASE_FALLBACK;
      element.setAttribute('aria-disabled', 'true');
      element.setAttribute('data-release-pending', 'true');
    }
  };

  const updateChecksumCommand = (installerUrl) => {
    const command = document.getElementById('checksum-command');
    if (!command || !installerUrl) return;
    try {
      const filename = decodeURIComponent(new URL(installerUrl).pathname.split('/').pop());
      command.textContent = `Get-FileHash .\\${filename} -Algorithm SHA256`;
    } catch (_) {}
  };

  const renderRelease = (release) => {
    const state = release || {
      type: 'error',
      source: 'local-release-manifest-error',
      releaseUrl: RELEASE_FALLBACK
    };
    const enabled = state.type === 'enabled' && Boolean(state.installerUrl);

    document.querySelectorAll('[data-installer-cta]').forEach((button) => {
      setLink(button, state.installerUrl, enabled);
    });
    setLink(document.getElementById('vst3-link'), state.vst3Url, Boolean(state.vst3Url));
    setLink(document.getElementById('standalone-link'), state.standaloneUrl, Boolean(state.standaloneUrl));
    setLink(document.getElementById('mac-dmg-link'), state.macDmgUrl, Boolean(state.macDmgUrl));
    setLink(document.getElementById('mac-vst3-link'), state.macVst3Url, Boolean(state.macVst3Url));
    setLink(document.getElementById('mac-standalone-link'), state.macStandaloneUrl, Boolean(state.macStandaloneUrl));
    setLink(document.getElementById('checksums-link'), state.checksumsUrl, Boolean(state.checksumsUrl));
    setLink(document.getElementById('release-link'), state.releaseUrl || RELEASE_FALLBACK, true);
    setLink(document.getElementById('distribution-link'), state.releaseUrl || RELEASE_FALLBACK, true);

    if (state.version) {
      document.querySelectorAll('[data-release-version]').forEach((element) => {
        element.textContent = state.version;
      });
    }

    const statusText = state.type === 'enabled'
      ? copy.enabled
      : state.type === 'paused'
        ? copy.paused
        : copy.error;
    document.querySelectorAll('[data-release-status]').forEach((element) => {
      element.textContent = statusText;
    });

    const banner = document.getElementById('distribution-banner');
    if (banner) banner.dataset.state = state.type;
    root.dataset.releaseSource = state.source;
    updateChecksumCommand(state.installerUrl);
    document.dispatchEvent(new CustomEvent('askp:release-ready', { detail: state }));
  };

  const resolveRelease = async () => {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 3000);
    try {
      const response = await fetch(`${siteBase}/release.json`, {
        cache: 'no-store',
        credentials: 'same-origin',
        signal: controller.signal
      });
      if (!response.ok) throw new Error(`release.json returned ${response.status}`);
      return parseManifest(await response.json());
    } catch (_) {
      return null;
    } finally {
      window.clearTimeout(timer);
    }
  };

  const setupMobileNavigation = () => {
    const menu = document.querySelector('.mobile-nav');
    if (!menu) return;
    menu.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => menu.removeAttribute('open'));
    });
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
  resolveRelease().then(renderRelease).catch(() => renderRelease(null));
})();
