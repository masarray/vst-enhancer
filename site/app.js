(async () => {
  try {
    const response = await fetch('./release.json', { cache: 'no-store' });
    if (!response.ok) return;

    const release = await response.json();
    if (release.version) {
      const version = document.getElementById('release-version');
      if (version) version.textContent = release.version;
    }
    if (release.installerUrl) {
      document.getElementById('installer-link')?.setAttribute('href', release.installerUrl);
      document.getElementById('installer-link-bottom')?.setAttribute('href', release.installerUrl);
    }
    if (release.releaseUrl)
      document.getElementById('release-link')?.setAttribute('href', release.releaseUrl);
    if (release.checksumsUrl)
      document.getElementById('checksums-link')?.setAttribute('href', release.checksumsUrl);
  } catch (_) {
    // Static release links remain available when metadata cannot be loaded.
  }
})();