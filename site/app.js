(async () => {
  try {
    const response = await fetch('./release.json', { cache: 'no-store' });
    if (!response.ok) return;
    const release = await response.json();
    if (release.version) document.getElementById('release-version').textContent = release.version;
    if (release.installerUrl) document.getElementById('installer-link').href = release.installerUrl;
    if (release.releaseUrl) document.getElementById('release-link').href = release.releaseUrl;
    if (release.checksumsUrl) document.getElementById('checksums-link').href = release.checksumsUrl;
  } catch (_) {
    // Static v0.5.0 fallback links remain available.
  }
})();
