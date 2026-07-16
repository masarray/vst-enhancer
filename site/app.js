(async () => {
  const installerButtons = [
    document.getElementById('installer-link'),
    document.getElementById('installer-link-bottom')
  ].filter(Boolean);

  const pauseDownloads = (releaseUrl) => {
    const safeUrl = releaseUrl || 'https://github.com/masarray/vst-enhancer/releases';
    installerButtons.forEach((button) => {
      button.setAttribute('href', safeUrl);
      button.textContent = 'Compliance rebuild pending';
      button.setAttribute('aria-label', 'View ArSonKuPik release and compliance status');
    });

    const status = document.getElementById('distribution-status');
    if (status) {
      status.hidden = false;
      status.textContent = 'Downloads are temporarily paused while the JUCE 8.0.14 compliance rebuild completes Windows QA.';
    }
  };

  try {
    const response = await fetch('./release.json', { cache: 'no-store' });
    if (!response.ok) return;

    const release = await response.json();
    if (release.version) {
      const version = document.getElementById('release-version');
      if (version) version.textContent = release.version;
    }

    if (release.distributionEnabled === false) {
      pauseDownloads(release.releaseUrl);
    } else if (release.installerUrl) {
      installerButtons.forEach((button) => button.setAttribute('href', release.installerUrl));
    }

    if (release.releaseUrl)
      document.getElementById('release-link')?.setAttribute('href', release.releaseUrl);
    if (release.checksumsUrl)
      document.getElementById('checksums-link')?.setAttribute('href', release.checksumsUrl);
    else
      document.getElementById('checksums-link')?.setAttribute('href', release.releaseUrl || 'https://github.com/masarray/vst-enhancer/releases');
  } catch (_) {
    // Static release-status links remain available when metadata cannot be loaded.
  }
})();
