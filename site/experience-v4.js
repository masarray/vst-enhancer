(() => {
  'use strict';

  const root = document.documentElement;
  const language = root.lang === 'id' ? 'id' : 'en';
  const text = language === 'id'
    ? {
        preview: 'Buka tampilan aplikasi ukuran besar',
        close: 'Tutup',
        caption: 'Tampilan asli ArSonKuPik dengan Mas Ari Signature engine dan selector preset profesional.',
        presets: 'Filter preset',
        all: 'Semua',
        visible: (count) => `${count} preset ditampilkan`
      }
    : {
        preview: 'Open a larger product interface preview',
        close: 'Close',
        caption: 'Actual ArSonKuPik interface with the Mas Ari Signature engine and professional preset selector.',
        presets: 'Filter presets',
        all: 'All',
        visible: (count) => `${count} presets shown`
      };

  const setupProductPreview = () => {
    const source = document.querySelector('.product-stage img');
    if (!source || typeof HTMLDialogElement === 'undefined') return;

    source.setAttribute('role', 'button');
    source.setAttribute('tabindex', '0');
    source.setAttribute('aria-label', text.preview);
    source.setAttribute('aria-haspopup', 'dialog');

    const dialog = document.createElement('dialog');
    dialog.className = 'product-preview-dialog';
    dialog.setAttribute('aria-label', text.preview);

    const shell = document.createElement('div');
    shell.className = 'product-preview-shell';
    const preview = document.createElement('img');
    preview.src = source.currentSrc || source.src;
    preview.alt = source.alt;
    preview.width = source.width || 1080;
    preview.height = source.height || 612;
    preview.decoding = 'async';

    const footer = document.createElement('div');
    footer.className = 'product-preview-footer';
    const caption = document.createElement('span');
    caption.textContent = text.caption;
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'product-preview-close';
    closeButton.textContent = text.close;
    closeButton.addEventListener('click', () => dialog.close());

    footer.append(caption, closeButton);
    shell.append(preview, footer);
    dialog.append(shell);
    document.body.append(dialog);

    const open = () => {
      if (!dialog.open) dialog.showModal();
      closeButton.focus({ preventScroll: true });
    };
    source.addEventListener('click', open);
    source.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        open();
      }
    });
    dialog.addEventListener('click', (event) => {
      if (event.target === dialog) dialog.close();
    });
    dialog.addEventListener('close', () => source.focus({ preventScroll: true }));
  };

  const setupPresetExplorer = () => {
    const universe = document.querySelector('.preset-universe');
    const groupsContainer = universe?.querySelector('.preset-groups');
    const groups = groupsContainer ? [...groupsContainer.querySelectorAll('.preset-group')] : [];
    if (!universe || !groupsContainer || !groups.length || universe.dataset.explorerReady === 'true') return;

    universe.dataset.explorerReady = 'true';
    universe.classList.add('preset-explorer-ready');

    const categories = groups.map((group, index) => {
      const heading = group.querySelector('header strong')?.textContent?.trim() || `Group ${index + 1}`;
      const key = heading.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
      group.dataset.presetCategory = key;
      const paragraph = group.querySelector(':scope > p');
      if (paragraph && !group.classList.contains('flagship')) {
        const names = paragraph.textContent.split('·').map((name) => name.trim()).filter(Boolean);
        const list = document.createElement('p');
        list.className = 'preset-chip-list';
        names.forEach((name) => {
          const chip = document.createElement('span');
          chip.className = 'preset-chip';
          chip.textContent = name;
          list.append(chip);
        });
        paragraph.replaceWith(list);
        group.dataset.presetCount = String(names.length);
      } else {
        group.dataset.presetCount = '1';
      }
      return { key, heading };
    });

    const browser = document.createElement('div');
    browser.className = 'preset-browser';
    const toolbar = document.createElement('div');
    toolbar.className = 'preset-toolbar';
    toolbar.setAttribute('aria-label', text.presets);
    const filters = document.createElement('div');
    filters.className = 'preset-filter-list';
    filters.setAttribute('role', 'group');
    filters.setAttribute('aria-label', text.presets);
    const result = document.createElement('span');
    result.className = 'preset-result-count';
    result.setAttribute('aria-live', 'polite');

    const total = groups.reduce((sum, group) => sum + Number(group.dataset.presetCount || 0), 0);
    result.textContent = text.visible(total);

    [{ key: 'all', heading: text.all }, ...categories].forEach((choice, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'preset-filter';
      button.dataset.presetFilter = choice.key;
      button.textContent = choice.heading;
      button.setAttribute('aria-pressed', String(index === 0));
      button.addEventListener('click', () => {
        filters.querySelectorAll('.preset-filter').forEach((item) => {
          item.setAttribute('aria-pressed', String(item === button));
        });
        let visibleCount = 0;
        groups.forEach((group) => {
          const visible = choice.key === 'all' || group.dataset.presetCategory === choice.key;
          group.hidden = !visible;
          if (visible) visibleCount += Number(group.dataset.presetCount || 0);
        });
        result.textContent = text.visible(visibleCount);
      });
      filters.append(button);
    });

    toolbar.append(filters, result);
    groupsContainer.before(browser);
    browser.append(toolbar, groupsContainer);
  };

  const setupNavigationState = () => {
    const nav = document.querySelector('.landing-nav');
    const links = [...document.querySelectorAll('.landing-nav nav a[href^="#"]')];
    if (!nav) return;

    let frame = 0;
    const updateScrolledState = () => {
      frame = 0;
      nav.classList.toggle('is-scrolled', window.scrollY > 18);
    };
    window.addEventListener('scroll', () => {
      if (frame) return;
      frame = window.requestAnimationFrame(updateScrolledState);
    }, { passive: true });
    updateScrolledState();

    if (!('IntersectionObserver' in window) || !links.length) return;
    const sections = links
      .map((link) => ({ link, section: document.querySelector(link.getAttribute('href')) }))
      .filter((item) => item.section);
    if (!sections.length) return;

    const byId = new Map(sections.map((item) => [item.section.id, item.link]));
    const setActive = (id) => {
      sections.forEach(({ link, section }) => {
        const selected = section.id === id;
        link.classList.toggle('is-active', selected);
        if (selected) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    };

    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting && byId.has(entry.target.id))
        .sort((a, b) => Math.abs(a.boundingClientRect.top) - Math.abs(b.boundingClientRect.top));
      if (visible[0]) setActive(visible[0].target.id);
    }, { rootMargin: '-18% 0px -70% 0px', threshold: 0 });

    sections.forEach(({ section }) => observer.observe(section));
  };

  const initializeEnhancements = () => {
    setupPresetExplorer();
    setupProductPreview();
    setupNavigationState();
    root.setAttribute('data-experience-layer', 'v7-static-first');
  };

  // All critical copy, SEO metadata and the LCP image are already present in
  // HTML. Keep enhancement work out of the initial rendering path.
  if ('requestIdleCallback' in window) {
    window.requestIdleCallback(initializeEnhancements, { timeout: 1600 });
  } else {
    window.requestAnimationFrame(() => window.setTimeout(initializeEnhancements, 0));
  }
})();
