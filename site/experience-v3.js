(() => {
  'use strict';

  const siteBase = document.documentElement.dataset.siteBase || (location.pathname.includes('/id/') ? '..' : '.');
  const language = location.pathname.includes('/id/') ? 'id' : 'en';

  const stylesheet = document.createElement('link');
  stylesheet.rel = 'stylesheet';
  stylesheet.href = `${siteBase}/experience-v3.css`;
  stylesheet.setAttribute('data-progressive-style', 'experience-v3');
  document.head.append(stylesheet);

  const text = language === 'id'
    ? {
        preview: 'Buka tampilan aplikasi ukuran besar',
        close: 'Tutup',
        caption: 'Tampilan asli ArSonKuPik dengan preset flagship Mas Ari Signature.',
        presets: 'Filter preset',
        all: 'Semua',
        visible: (count) => `${count} preset ditampilkan`
      }
    : {
        preview: 'Open a larger product interface preview',
        close: 'Close',
        caption: 'Actual ArSonKuPik interface with the flagship Mas Ari Signature preset.',
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

    const footer = document.createElement('div');
    footer.className = 'product-preview-footer';

    const caption = document.createElement('span');
    caption.textContent = text.caption;

    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'product-preview-close';
    close.textContent = text.close;
    close.addEventListener('click', () => dialog.close());

    footer.append(caption, close);
    shell.append(preview, footer);
    dialog.append(shell);
    document.body.append(dialog);

    const open = () => {
      if (!dialog.open) dialog.showModal();
      close.focus();
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
  };

  const setupPresetExplorer = () => {
    const universe = document.querySelector('.preset-universe');
    const groups = [...document.querySelectorAll('.preset-groups .preset-group')];
    if (!universe || groups.length === 0) return;

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

    const toolbar = document.createElement('div');
    toolbar.className = 'preset-toolbar';
    toolbar.setAttribute('aria-label', text.presets);

    const filters = document.createElement('div');
    filters.className = 'preset-filter-list';
    filters.setAttribute('role', 'group');
    filters.setAttribute('aria-label', text.presets);

    const result = document.createElement('span');
    result.className = 'preset-result-count';

    const total = groups.reduce((sum, group) => sum + Number(group.dataset.presetCount || 0), 0);
    result.textContent = text.visible(total);

    const choices = [{ key: 'all', heading: text.all }, ...categories];
    choices.forEach((choice, index) => {
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
    const groupsContainer = universe.querySelector('.preset-groups');
    universe.insertBefore(toolbar, groupsContainer);
  };

  setupProductPreview();
  setupPresetExplorer();
  document.documentElement.setAttribute('data-experience-layer', 'v3-proof-ready');
})();
