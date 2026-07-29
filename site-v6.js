(() => {
  'use strict';

  const root = document.documentElement;
  const currentScript = document.currentScript;
  const storageKey = 'askp-language';

  const readPreference = () => {
    try {
      const value = localStorage.getItem(storageKey);
      return value === 'id' || value === 'en' ? value : null;
    } catch (_) {
      return null;
    }
  };

  const savePreference = (value) => {
    if (value !== 'id' && value !== 'en') return;
    try { localStorage.setItem(storageKey, value); } catch (_) {}
  };

  document.querySelectorAll('.language-switch a[lang]').forEach((link) => {
    link.addEventListener('click', () => savePreference(link.lang.toLowerCase().startsWith('id') ? 'id' : 'en'));
  });

  const currentLanguage = root.lang.toLowerCase().startsWith('id') ? 'id' : 'en';
  const preference = readPreference();
  let timeZone = '';
  try { timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (_) {}

  const indonesiaZones = new Set([
    'Asia/Jakarta',
    'Asia/Pontianak',
    'Asia/Makassar',
    'Asia/Ujung_Pandang',
    'Asia/Jayapura'
  ]);
  const browserLanguages = Array.isArray(navigator.languages) && navigator.languages.length
    ? navigator.languages
    : [navigator.language || ''];
  const detectedIndonesia = indonesiaZones.has(timeZone)
    || browserLanguages.some((value) => /^id(?:-|$)/i.test(value));

  if (currentLanguage === 'en' && (preference === 'id' || (!preference && detectedIndonesia))) {
    const target = new URL('id/', location.href);
    target.search = location.search;
    target.hash = location.hash;
    location.replace(target.href);
    return;
  }

  const source = currentScript?.src
    || new URL(`${root.dataset.siteBase || '.'}/site-v6.js`, location.href).href;
  const core = document.createElement('script');
  core.src = source.replace(/site-v6\.js(?:\?.*)?$/, 'site-v6-core.js');
  core.async = false;
  document.head.appendChild(core);
})();
