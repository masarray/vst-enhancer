(() => {
  'use strict';

  const root = document.documentElement;
  const siteBase = root.dataset.siteBase || '.';
  const language = root.lang === 'id' ? 'id' : 'en';
  const REPOSITORY = 'masarray/vst-enhancer';
  const RELEASES_ROOT = `https://github.com/${REPOSITORY}/releases`;
  const RELEASE_FALLBACK = `${RELEASES_ROOT}/latest`;
  const LATEST_API = `https://api.github.com/repos/${REPOSITORY}/releases/latest`;
  const OFFICIAL_RELEASE_PATH = `/${REPOSITORY}/releases`;
  const OFFICIAL_DOWNLOAD_PREFIX = `/${REPOSITORY}/releases/download/`;
  const VERSION_RE = /^v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$/;

  const copy = language === 'id'
    ? {
        enabled: 'Rilis resmi tersedia',
        paused: 'Unduhan resmi sedang dijeda',
        error: 'Status rilis tidak dapat diperiksa',
        installer: 'Unduh gratis untuk Windows',
        installerShort: 'Unduh gratis',
        eyebrow: 'Rilis terbaru',
        heading: 'Apa yang meningkat di',
        notes: 'Buka catatan rilis lengkap',
        published: 'Diterbitkan',
        liveSource: 'Data langsung GitHub Releases',
        reviewedSource: 'Metadata rilis tervalidasi',
        fallbackHighlight: 'Catatan peningkatan lengkap tersedia di halaman GitHub Release resmi.'
      }
    : {
        enabled: 'Official release available',
        paused: 'Official download is temporarily paused',
        error: 'Release status could not be checked',
        installer: 'Download free for Windows',
        installerShort: 'Download free',
        eyebrow: 'Latest release',
        heading: 'What improved in',
        notes: 'Open full release notes',
        published: 'Published',
        liveSource: 'Live GitHub Releases data',
        reviewedSource: 'Reviewed release metadata',
        fallbackHighlight: 'The complete improvement notes are available on the official GitHub Release page.'
      };

  const officialReleaseUrl = (value, asset = false) => {
    if (typeof value !== 'string' || value.length > 800) return null;
    try {
      const url = new URL(value);
      const validPath = url.pathname === OFFICIAL_RELEASE_PATH || url.pathname.startsWith(`${OFFICIAL_RELEASE_PATH}/`);
      if (url.protocol !== 'https:' || url.hostname !== 'github.com' || !validPath) return null;
      if (asset && !url.pathname.startsWith(OFFICIAL_DOWNLOAD_PREFIX)) return null;
      return url.href;
    } catch (_) {
      return null;
    }
  };

  const officialAsset = (asset) => {
    if (!asset || typeof asset.name !== 'string' || typeof asset.browser_download_url !== 'string') return null;
    if (asset.state && asset.state !== 'uploaded') return null;
    const url = officialReleaseUrl(asset.browser_download_url, true);
    return url ? { name: asset.name, url } : null;
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

  const cleanMarkdown = (value) => value
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/[`*_~>#]/g, '')
    .replace(/<[^>]+>/g, '')
    .replace(/\s+/g, ' ')
    .trim();

  const extractHighlights = (body, maximum = 6) => {
    if (typeof body !== 'string') return [];
    const ignored = /^(full changelog|contributors?|new contributors?|assets?|checksums?|sha-?256)\b/i;
    const unique = new Set();
    const highlights = [];
    const add = (value) => {
      const cleaned = cleanMarkdown(value).replace(/^[-+*]\s+/, '').replace(/^\d+[.)]\s+/, '');
      if (!cleaned || cleaned.length < 8 || ignored.test(cleaned) || unique.has(cleaned.toLowerCase())) return;
      unique.add(cleaned.toLowerCase());
      highlights.push(cleaned.length > 220 ? `${cleaned.slice(0, 217).trim()}…` : cleaned);
    };

    body.split(/\r?\n/).forEach((line) => {
      const trimmed = line.trim();
      if (/^[-+*]\s+/.test(trimmed) || /^\d+[.)]\s+/.test(trimmed)) add(trimmed);
    });

    if (!highlights.length) {
      body.split(/\r?\n\s*\r?\n/).forEach((paragraph) => {
        const trimmed = paragraph.trim();
        if (!trimmed.startsWith('#')) add(trimmed);
      });
    }
    return highlights.slice(0, maximum);
  };

  const parseGitHubRelease = (payload) => {
    if (!payload || payload.draft === true || payload.prerelease === true) return null;
    if (typeof payload.tag_name !== 'string' || !VERSION_RE.test(payload.tag_name)) return null;
    const releaseUrl = officialReleaseUrl(payload.html_url);
    const assets = Array.isArray(payload.assets) ? payload.assets.map(officialAsset).filter(Boolean) : [];
    const installer = chooseAsset(assets, (name) => name.endsWith('.exe'), scoreInstaller);
    if (!releaseUrl || !installer || scoreInstaller(installer.name) < 20) return null;
    return {
      type: 'enabled',
      source: 'github-latest-api',
      version: payload.tag_name,
      releaseName: cleanMarkdown(payload.name || payload.tag_name),
      publishedAt: payload.published_at || payload.created_at || null,
      releaseUrl,
      installerUrl: installer.url,
      installerName: installer.name,
      vst3Url: chooseAsset(assets, (name) => name.endsWith('.zip') && name.includes('vst3'))?.url || null,
      standaloneUrl: chooseAsset(assets, (name) => name.endsWith('.zip') && name.includes('standalone'))?.url || null,
      checksumsUrl: chooseAsset(assets, (name) => name === 'sha256sums.txt' || name.includes('sha256'))?.url || null,
      highlights: extractHighlights(payload.body)
    };
  };

  const parseManifest = (release) => {
    if (!release || typeof release !== 'object' || !VERSION_RE.test(String(release.version || ''))) return null;
    const releaseUrl = officialReleaseUrl(release.releaseUrl) || RELEASE_FALLBACK;
    const installerUrl = officialReleaseUrl(release.installerUrl, true);
    const highlights = Array.isArray(release.releaseHighlights)
      ? release.releaseHighlights.map(cleanMarkdown).filter(Boolean).slice(0, 6)
      : [];
    return release.distributionEnabled === true && installerUrl
      ? {
          type: 'enabled',
          source: 'local-release-manifest',
          version: release.version,
          releaseName: cleanMarkdown(release.releaseName || release.version),
          publishedAt: release.publishedAt || null,
          releaseUrl,
          installerUrl,
          installerName: decodeURIComponent(new URL(installerUrl).pathname.split('/').pop()),
          vst3Url: officialReleaseUrl(release.vst3Url, true),
          standaloneUrl: officialReleaseUrl(release.standaloneUrl, true),
          checksumsUrl: officialReleaseUrl(release.checksumsUrl, true),
          highlights
        }
      : { type: 'paused', source: 'local-release-manifest', version: release.version, releaseUrl, highlights };
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

  const updateStructuredData = (release) => {
    const script = document.getElementById('software-structured-data');
    if (!script || !release) return;
    try {
      const data = JSON.parse(script.textContent);
      const software = data['@graph']?.find((entry) => entry['@type'] === 'SoftwareApplication');
      if (!software) return;
      software.softwareVersion = release.version.replace(/^v/i, '');
      software.downloadUrl = release.installerUrl || release.releaseUrl;
      software.releaseNotes = release.releaseUrl;
      if (software.offers) software.offers.url = release.installerUrl || release.releaseUrl;
      script.textContent = JSON.stringify(data, null, 2);
    } catch (_) {
      // Keep the static JSON-LD when enhancement fails.
    }
  };

  const ensureReleasePanelStyles = () => {
    if (document.getElementById('latest-release-panel-style')) return;
    const style = document.createElement('style');
    style.id = 'latest-release-panel-style';
    style.textContent = `
      .release-update-section{padding-top:clamp(42px,6vw,74px);padding-bottom:clamp(42px,6vw,74px)}
      .release-update-shell{display:grid;grid-template-columns:minmax(0,.78fr) minmax(0,1.22fr);gap:clamp(24px,4vw,56px);align-items:start;padding:clamp(22px,3vw,34px);border:1px solid rgba(255,255,255,.11);border-radius:22px;background:linear-gradient(135deg,rgba(255,255,255,.055),rgba(255,255,255,.018));box-shadow:0 18px 50px rgba(0,0,0,.18)}
      .release-update-copy h2{margin:.45rem 0 .7rem;font-size:clamp(1.65rem,3vw,2.5rem);line-height:1.08;font-weight:650;letter-spacing:-.03em}
      .release-update-copy p{margin:0;color:var(--muted,#b7b2c2);font-size:.94rem}
      .release-update-list{display:grid;gap:10px;margin:0;padding:0;list-style:none}
      .release-update-list li{position:relative;padding:12px 14px 12px 38px;border:1px solid rgba(255,255,255,.08);border-radius:14px;background:rgba(0,0,0,.14);font-size:.96rem;line-height:1.48}
      .release-update-list li::before{content:'↗';position:absolute;left:14px;top:11px;color:#d58cff;font-weight:700}
      .release-update-actions{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-top:18px}
      .release-update-source{font-size:.78rem;color:var(--muted,#9892a4)}
      @media (max-width:760px){.release-update-shell{grid-template-columns:1fr;border-radius:18px;padding:20px}.release-update-copy h2{font-size:1.65rem}.release-update-list li{font-size:.91rem}}
    `;
    document.head.appendChild(style);
  };

  const ensureReleasePanel = () => {
    let section = document.getElementById('latest-release');
    if (section) return section;
    ensureReleasePanelStyles();
    section = document.createElement('section');
    section.id = 'latest-release';
    section.className = 'section release-update-section';
    section.setAttribute('aria-labelledby', 'latest-release-title');
    section.innerHTML = `
      <div class="container">
        <div class="release-update-shell">
          <div class="release-update-copy">
            <span class="eyebrow">${copy.eyebrow}</span>
            <h2 id="latest-release-title">${copy.heading} <span data-latest-release-version>—</span></h2>
            <p><span data-latest-release-name></span><span data-release-published-wrap hidden> · ${copy.published} <time data-release-published></time></span></p>
            <div class="release-update-actions">
              <a class="text-link" data-latest-release-link href="${RELEASE_FALLBACK}">${copy.notes}</a>
              <span class="release-update-source" data-release-source-label></span>
            </div>
          </div>
          <ul class="release-update-list" data-release-highlights aria-live="polite"></ul>
        </div>
      </div>`;
    const download = document.getElementById('download');
    if (download?.parentNode) download.parentNode.insertBefore(section, download);
    else document.querySelector('main')?.appendChild(section);
    return section;
  };

  const renderHighlights = (release) => {
    const panel = ensureReleasePanel();
    if (!panel) return;
    panel.querySelector('[data-latest-release-version]').textContent = release.version || '—';
    panel.querySelector('[data-latest-release-name]').textContent = release.releaseName && release.releaseName !== release.version ? release.releaseName : '';
    setLink(panel.querySelector('[data-latest-release-link]'), release.releaseUrl || RELEASE_FALLBACK, true);
    const list = panel.querySelector('[data-release-highlights]');
    list.replaceChildren();
    const highlights = release.highlights?.length ? release.highlights : [copy.fallbackHighlight];
    highlights.forEach((text) => {
      const item = document.createElement('li');
      item.textContent = text;
      list.appendChild(item);
    });
    const publishedWrap = panel.querySelector('[data-release-published-wrap]');
    const published = panel.querySelector('[data-release-published]');
    if (release.publishedAt && publishedWrap && published) {
      const date = new Date(release.publishedAt);
      if (!Number.isNaN(date.getTime())) {
        published.dateTime = date.toISOString();
        published.textContent = new Intl.DateTimeFormat(language === 'id' ? 'id-ID' : 'en-US', {
          day: 'numeric', month: 'short', year: 'numeric'
        }).format(date);
        publishedWrap.hidden = false;
      }
    }
    const source = panel.querySelector('[data-release-source-label]');
    if (source) source.textContent = release.source === 'github-latest-api' ? copy.liveSource : copy.reviewedSource;
  };

  const updateChecksumCommand = (installerUrl, version, installerName) => {
    const command = document.getElementById('checksum-command');
    if (!command) return;
    let filename = installerName || (version ? `ArSonKuPik-${version}-Windows-x64-Setup.exe` : 'ArSonKuPik-Windows-x64-Setup.exe');
    try {
      if (installerUrl) filename = decodeURIComponent(new URL(installerUrl).pathname.split('/').pop());
    } catch (_) {}
    command.textContent = `Get-FileHash .\\${filename} -Algorithm SHA256`;
  };

  const renderRelease = (release) => {
    const state = release || { type: 'error', source: 'fallback', releaseUrl: RELEASE_FALLBACK, highlights: [] };
    const installerUrl = state.installerUrl || state.releaseUrl || RELEASE_FALLBACK;
    const enabled = state.type === 'enabled' && Boolean(state.installerUrl);

    document.querySelectorAll('[data-installer-cta]').forEach((button) => {
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
    root.dataset.releaseSource = state.source || 'fallback';

    updateChecksumCommand(state.installerUrl, state.version, state.installerName);
    updateStructuredData(state);
    renderHighlights(state);
    document.dispatchEvent(new CustomEvent('askp:release-ready', { detail: state }));
  };

  const fetchJson = async (url, options = {}, timeoutMs = 4500) => {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(url, { ...options, signal: controller.signal });
      if (!response.ok) throw new Error(`Release metadata returned ${response.status}`);
      return await response.json();
    } finally {
      window.clearTimeout(timer);
    }
  };

  const resolveRelease = async () => {
    const localPromise = fetchJson(`${siteBase}/release.json`, {
      cache: 'no-store', credentials: 'same-origin'
    }, 3000).then(parseManifest).catch(() => null);

    const latestPromise = fetchJson(LATEST_API, {
      cache: 'no-cache',
      headers: { Accept: 'application/vnd.github+json' },
      referrerPolicy: 'no-referrer'
    }, 4500).then(parseGitHubRelease).catch(() => null);

    const [latest, local] = await Promise.all([latestPromise, localPromise]);
    return latest || local || null;
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
  ensureReleasePanel();
  resolveRelease().then(renderRelease).catch(() => renderRelease(null));
})();
