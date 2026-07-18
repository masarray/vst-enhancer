(() => {
  'use strict';

  const REPOSITORY = 'masarray/vst-enhancer';
  const RELEASES_ROOT = `https://github.com/${REPOSITORY}/releases`;
  const RELEASES_LATEST = `${RELEASES_ROOT}/latest`;
  const LATEST_API = `https://api.github.com/repos/${REPOSITORY}/releases/latest`;
  const OFFICIAL_DOWNLOAD_PREFIX = `/masarray/vst-enhancer/releases/download/`;

  let expectedInstallerUrl = RELEASES_LATEST;
  const protectedLinks = new WeakSet();

  const directInstallerLinks = () => [
    ...document.querySelectorAll('[data-installer-cta]'),
    document.getElementById('free-download-link')
  ].filter(Boolean);

  const officialReleaseUrl = (value) => {
    if (typeof value !== 'string' || value.length > 500) return null;
    try {
      const url = new URL(value);
      if (url.protocol !== 'https:' || url.hostname !== 'github.com') return null;
      if (!url.pathname.startsWith('/masarray/vst-enhancer/releases/')) return null;
      return url.href;
    } catch (_) {
      return null;
    }
  };

  const officialAssetUrl = (asset) => {
    if (!asset || typeof asset.name !== 'string' || typeof asset.browser_download_url !== 'string') return null;
    if (asset.state && asset.state !== 'uploaded') return null;
    try {
      const url = new URL(asset.browser_download_url);
      if (url.protocol !== 'https:' || url.hostname !== 'github.com') return null;
      if (!url.pathname.startsWith(OFFICIAL_DOWNLOAD_PREFIX)) return null;
      return { name: asset.name, url: url.href };
    } catch (_) {
      return null;
    }
  };

  const scoreInstaller = (name) => {
    const lower = name.toLowerCase();
    if (!lower.endsWith('.exe')) return -1;
    let score = 0;
    if (lower.includes('arsonkupik')) score += 20;
    if (lower.includes('windows')) score += 10;
    if (lower.includes('x64') || lower.includes('win64')) score += 8;
    if (lower.includes('setup')) score += 12;
    if (lower.includes('installer')) score += 10;
    if (lower.includes('portable')) score -= 30;
    if (lower.includes('activator') || lower.includes('key')) score -= 100;
    return score;
  };

  const chooseAsset = (assets, predicate, scorer = () => 0) => assets
    .filter((asset) => predicate(asset.name.toLowerCase()))
    .sort((a, b) => scorer(b.name) - scorer(a.name))[0] || null;

  const parseLatestRelease = (payload) => {
    if (!payload || payload.draft === true || payload.prerelease === true) return null;
    if (typeof payload.tag_name !== 'string' || !/^v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$/.test(payload.tag_name)) return null;

    const releaseUrl = officialReleaseUrl(payload.html_url);
    const assets = Array.isArray(payload.assets)
      ? payload.assets.map(officialAssetUrl).filter(Boolean)
      : [];
    const installer = chooseAsset(assets, (name) => name.endsWith('.exe'), scoreInstaller);
    if (!releaseUrl || !installer || scoreInstaller(installer.name) < 20) return null;

    return {
      version: payload.tag_name,
      releaseUrl,
      installerUrl: installer.url,
      installerName: installer.name,
      vst3Url: chooseAsset(assets, (name) => name.endsWith('.zip') && name.includes('vst3'))?.url || null,
      standaloneUrl: chooseAsset(assets, (name) => name.endsWith('.zip') && name.includes('standalone'))?.url || null,
      checksumsUrl: chooseAsset(assets, (name) => name === 'sha256sums.txt' || name.includes('sha256'))?.url || null
    };
  };

  const latestReleasePromise = fetch(LATEST_API, {
    cache: 'no-store',
    headers: {
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
    },
    referrerPolicy: 'no-referrer'
  })
    .then((response) => {
      if (!response.ok) throw new Error(`Latest release API returned ${response.status}`);
      return response.json();
    })
    .then(parseLatestRelease)
    .catch(() => null);

  const syncDirectLinks = () => {
    directInstallerLinks().forEach((link) => {
      if (link.getAttribute('href') !== expectedInstallerUrl) {
        link.setAttribute('href', expectedInstallerUrl);
      }
      link.removeAttribute('aria-disabled');
      link.removeAttribute('data-release-pending');

      if (!protectedLinks.has(link)) {
        const observer = new MutationObserver(() => {
          if (link.getAttribute('href') !== expectedInstallerUrl) {
            link.setAttribute('href', expectedInstallerUrl);
          }
        });
        observer.observe(link, { attributes: true, attributeFilter: ['href'] });
        protectedLinks.add(link);
      }
    });
  };

  const setExpectedInstaller = (url) => {
    expectedInstallerUrl = url;
    syncDirectLinks();
  };

  const updateStructuredData = (release) => {
    const script = document.getElementById('software-structured-data');
    if (!script) return;
    try {
      const data = JSON.parse(script.textContent);
      const software = data['@graph']?.find((entry) => entry['@type'] === 'SoftwareApplication');
      if (!software) return;
      software.softwareVersion = release.version.replace(/^v/i, '');
      software.downloadUrl = release.installerUrl;
      software.releaseNotes = release.releaseUrl;
      if (software.offers) software.offers.url = release.installerUrl;
      script.textContent = JSON.stringify(data, null, 2);
    } catch (_) {
      // Preserve the server-rendered structured data when enhancement fails.
    }
  };

  const applyLatestRelease = (release) => {
    if (!release) {
      setExpectedInstaller(RELEASES_LATEST);
      document.documentElement.setAttribute('data-release-source', 'github-latest-page-fallback');
      return;
    }

    setExpectedInstaller(release.installerUrl);
    document.getElementById('release-version')?.replaceChildren(release.version);

    const packageTargets = [
      ['vst3-link', release.vst3Url],
      ['standalone-link', release.standaloneUrl],
      ['checksums-link', release.checksumsUrl]
    ];
    packageTargets.forEach(([id, url]) => {
      const link = document.getElementById(id);
      if (link) link.setAttribute('href', url || release.releaseUrl);
    });

    document.getElementById('release-link')?.setAttribute('href', release.releaseUrl);
    document.getElementById('distribution-link')?.setAttribute('href', release.releaseUrl);

    const command = document.getElementById('checksum-command');
    if (command) command.textContent = `Get-FileHash .\\${release.installerName} -Algorithm SHA256`;

    updateStructuredData(release);
    document.documentElement.setAttribute('data-release-source', 'github-latest-api');
    document.dispatchEvent(new CustomEvent('askp:latest-release-resolved', { detail: release }));
  };

  // Lock every CTA to the moving latest-release target before legacy metadata can resolve.
  syncDirectLinks();
  latestReleasePromise.then(applyLatestRelease);
})();
