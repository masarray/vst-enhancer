(async () => {
  try {
    const response = await fetch('./release.json', { cache: 'no-store' });
    if (!response.ok) return;

    const release = await response.json();
    const versionLabel = release.channel === 'public-beta'
      ? `${release.version} Public Beta`
      : release.version;

    if (versionLabel) document.getElementById('release-version').textContent = versionLabel;
    if (release.installerUrl) document.getElementById('installer-link').href = release.installerUrl;
    if (release.releaseUrl) document.getElementById('release-link')?.setAttribute('href', release.releaseUrl);
    if (release.checksumsUrl) document.getElementById('checksums-link').href = release.checksumsUrl;
  } catch (_) {
    // Static v0.5.1 public-beta links remain available.
  }
})();
