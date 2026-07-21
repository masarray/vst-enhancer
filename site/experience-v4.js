(() => {
  'use strict';

  const siteBase = document.documentElement.dataset.siteBase || (location.pathname.includes('/id/') ? '..' : '.');
  const language = location.pathname.includes('/id/') ? 'id' : 'en';
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  const stylesheet = document.createElement('link');
  stylesheet.rel = 'stylesheet';
  stylesheet.href = `${siteBase}/experience-v4.css`;
  stylesheet.setAttribute('data-progressive-style', 'experience-v4');
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
    if (!universe || !groupsContainer || groups.length === 0 || universe.dataset.explorerReady === 'true') return;

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

    const showGroup = (group, visible) => {
      group.getAnimations?.().forEach((animation) => animation.cancel());
      group.dataset.filterTarget = visible ? 'visible' : 'hidden';

      if (reducedMotion || typeof group.animate !== 'function') {
        group.hidden = !visible;
        return;
      }

      if (visible) {
        group.hidden = false;
        group.animate(
          [
            { opacity: 0, transform: 'translateY(8px) scale(.995)' },
            { opacity: 1, transform: 'translateY(0) scale(1)' }
          ],
          { duration: 240, easing: 'cubic-bezier(.22, 1, .36, 1)' }
        );
      } else if (!group.hidden) {
        const animation = group.animate(
          [
            { opacity: 1, transform: 'translateY(0) scale(1)' },
            { opacity: 0, transform: 'translateY(5px) scale(.995)' }
          ],
          { duration: 140, easing: 'ease-out' }
        );
        animation.addEventListener('finish', () => {
          if (group.dataset.filterTarget === 'hidden') group.hidden = true;
        }, { once: true });
      }
    };

    const applyFilter = (choice, activeButton) => {
      filters.querySelectorAll('.preset-filter').forEach((item) => {
        item.setAttribute('aria-pressed', String(item === activeButton));
      });

      let visibleCount = 0;
      groups.forEach((group) => {
        const visible = choice === 'all' || group.dataset.presetCategory === choice;
        showGroup(group, visible);
        if (visible) visibleCount += Number(group.dataset.presetCount || 0);
      });
      result.textContent = text.visible(visibleCount);
    };

    const choices = [{ key: 'all', heading: text.all }, ...categories];
    choices.forEach((choice, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'preset-filter';
      button.dataset.presetFilter = choice.key;
      button.textContent = choice.heading;
      button.setAttribute('aria-pressed', String(index === 0));
      button.addEventListener('click', () => applyFilter(choice.key, button));
      filters.append(button);
    });

    toolbar.append(filters, result);
    groupsContainer.before(browser);
    browser.append(toolbar, groupsContainer);
  };

  const setupSignalAccent = () => {
    const title = document.querySelector('.signature-title');
    const badge = title?.querySelector(':scope > span');
    if (!title || !badge || title.querySelector('.signal-accent')) return;

    const row = document.createElement('div');
    row.className = 'signature-status-row';
    const meter = document.createElement('span');
    meter.className = 'signal-accent';
    meter.setAttribute('aria-hidden', 'true');
    for (let index = 0; index < 7; index += 1) {
      const bar = document.createElement('i');
      bar.style.setProperty('--bar-index', String(index));
      meter.append(bar);
    }
    badge.before(row);
    row.append(badge, meter);
  };

  const setupScrollReveals = () => {
    const targets = [
      ...document.querySelectorAll('.trust-grid > div'),
      document.querySelector('.signature-copy'),
      document.querySelector('.signature-panel'),
      ...document.querySelectorAll('.outcome-grid > article'),
      ...document.querySelectorAll('.test-flow > article'),
      ...document.querySelectorAll('.listening-controls > article'),
      document.querySelector('.preset-intro'),
      document.querySelector('.preset-browser'),
      ...document.querySelectorAll('.download-option'),
      document.querySelector('.freedom-copy'),
      document.querySelector('.freedom-facts'),
      ...document.querySelectorAll('.faq-grid > details'),
      document.querySelector('.cta-card')
    ].filter(Boolean);

    if (reducedMotion || !('IntersectionObserver' in window)) {
      targets.forEach((target) => target.classList.add('is-visible'));
      return;
    }

    targets.forEach((target, index) => {
      target.dataset.reveal = '';
      target.style.setProperty('--reveal-delay', `${(index % 4) * 55}ms`);
    });
    document.documentElement.classList.add('motion-ready');

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -9% 0px', threshold: 0.08 });

    targets.forEach((target) => observer.observe(target));
  };

  const setupHeroEntrance = () => {
    if (reducedMotion || typeof Element.prototype.animate !== 'function') return;
    const items = [
      ...document.querySelectorAll('.landing-hero .hero-copy > *'),
      document.querySelector('.landing-hero .product-stage')
    ].filter(Boolean);

    items.forEach((item, index) => {
      item.animate(
        [
          { opacity: 0, transform: 'translateY(12px)' },
          { opacity: 1, transform: 'translateY(0)' }
        ],
        {
          duration: index === items.length - 1 ? 720 : 520,
          delay: 45 + index * 65,
          easing: 'cubic-bezier(.22, 1, .36, 1)',
          fill: 'both'
        }
      );
    });
  };

  const setupNavigationState = () => {
    const nav = document.querySelector('.landing-nav');
    const links = [...document.querySelectorAll('.landing-nav nav a[href^="#"]')];
    const sections = links.map((link) => ({ link, section: document.querySelector(link.getAttribute('href')) })).filter((item) => item.section);
    if (!nav || sections.length === 0) return;

    let scheduled = false;
    const update = () => {
      scheduled = false;
      nav.classList.toggle('is-scrolled', window.scrollY > 18);
      const probe = window.scrollY + Math.min(window.innerHeight * 0.34, 320);
      let active = sections[0];
      sections.forEach((item) => {
        if (item.section.offsetTop <= probe) active = item;
      });
      sections.forEach((item) => {
        const selected = item === active;
        item.link.classList.toggle('is-active', selected);
        if (selected) item.link.setAttribute('aria-current', 'location');
        else item.link.removeAttribute('aria-current');
      });
    };

    const requestUpdate = () => {
      if (scheduled) return;
      scheduled = true;
      requestAnimationFrame(update);
    };
    window.addEventListener('scroll', requestUpdate, { passive: true });
    window.addEventListener('resize', requestUpdate, { passive: true });
    update();
  };

  const setupPointerDepth = () => {
    if (!finePointer || reducedMotion) return;

    const stage = document.querySelector('.product-stage');
    const spotlights = [stage, document.querySelector('.signature-panel'), document.querySelector('.download-option.recommended'), document.querySelector('.cta-card')].filter(Boolean);

    spotlights.forEach((element) => {
      let frame = 0;
      element.addEventListener('pointermove', (event) => {
        if (frame) cancelAnimationFrame(frame);
        frame = requestAnimationFrame(() => {
          const rect = element.getBoundingClientRect();
          const x = Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width));
          const y = Math.min(1, Math.max(0, (event.clientY - rect.top) / rect.height));
          element.style.setProperty('--spot-x', `${x * 100}%`);
          element.style.setProperty('--spot-y', `${y * 100}%`);
          if (element === stage) {
            element.style.setProperty('--tilt-y', `${(x - .5) * 1.5}deg`);
            element.style.setProperty('--tilt-x', `${(.5 - y) * 1.1}deg`);
            element.dataset.depthActive = 'true';
          }
        });
      }, { passive: true });

      element.addEventListener('pointerleave', () => {
        element.style.removeProperty('--spot-x');
        element.style.removeProperty('--spot-y');
        if (element === stage) {
          element.style.setProperty('--tilt-y', '0deg');
          element.style.setProperty('--tilt-x', '0deg');
          delete element.dataset.depthActive;
        }
      }, { passive: true });
    });
  };

  setupPresetExplorer();
  setupProductPreview();
  setupSignalAccent();
  setupScrollReveals();
  setupHeroEntrance();
  setupNavigationState();
  setupPointerDepth();
  document.documentElement.setAttribute('data-experience-layer', 'v4-audio-motion');
})();