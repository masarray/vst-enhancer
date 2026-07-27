(() => {
  'use strict';

  if (document.documentElement.dataset.experienceLayer === 'v4-audio-motion') return;
  if ([...document.scripts].some((script) => script.src.includes('/experience-v4.js'))) return;

  const siteBase = document.documentElement.dataset.siteBase || (location.pathname.includes('/id/') ? '..' : '.');
  const script = document.createElement('script');
  script.src = `${siteBase}/experience-v4.js`;
  script.defer = true;
  script.setAttribute('data-compatibility-bridge', 'v3-to-v4');
  document.head.append(script);
})();