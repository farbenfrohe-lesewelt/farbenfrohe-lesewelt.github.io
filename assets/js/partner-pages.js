(function () {
  const META_PIXEL_ID = '1599368868061138';
  const META_CONSENT_KEY = 'flw_meta_consent';
  const passthroughKeys = ['src', 'partner', 'campaign', 'medium'];
  let metaPixelLoaded = false;

  function loadMetaPixel() {
    if (metaPixelLoaded || window.fbq) return;
    metaPixelLoaded = true;

    !(function(f,b,e,v,n,t,s){
      if(f.fbq) return;
      n=f.fbq=function(){n.callMethod ? n.callMethod.apply(n,arguments) : n.queue.push(arguments)};
      if(!f._fbq) f._fbq=n;
      n.push=n;
      n.loaded=!0;
      n.version='2.0';
      n.queue=[];
      t=b.createElement(e);
      t.async=!0;
      t.src=v;
      s=b.getElementsByTagName(e)[0];
      s.parentNode.insertBefore(t,s);
    })(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');

    fbq('init', META_PIXEL_ID);
  }

  function eventParams(extra) {
    const params = new URLSearchParams(window.location.search);
    return Object.assign({
      src: params.get('src') || '',
      partner: params.get('partner') || '',
      campaign: params.get('campaign') || '',
      medium: params.get('medium') || ''
    }, extra || {});
  }

  function track(eventName, params) {
    if (localStorage.getItem(META_CONSENT_KEY) !== 'granted') return;
    loadMetaPixel();
    if (typeof fbq !== 'function') return;
    fbq('trackCustom', eventName, eventParams(params));
  }

  function preserveParams() {
    const currentParams = new URLSearchParams(window.location.search);
    const keptParams = new URLSearchParams();

    passthroughKeys.forEach(function (key) {
      const value = currentParams.get(key);
      if (value) keptParams.set(key, value);
    });

    if (!keptParams.toString()) return;

    document.querySelectorAll('a[data-preserve-params]').forEach(function (link) {
      const url = new URL(link.getAttribute('href'), window.location.href);
      keptParams.forEach(function (value, key) {
        if (!url.searchParams.has(key)) url.searchParams.set(key, value);
      });
      link.href = url.pathname + url.search + url.hash;
    });
  }

  function trackPageView() {
    if (document.body.dataset.pageType === 'partner') {
      track('partner_page_view', { page: document.body.dataset.pageName || '' });
    }
  }

  function ensureConsentBanner() {
    if (localStorage.getItem(META_CONSENT_KEY)) return;

    const banner = document.createElement('div');
    banner.className = 'cookie-banner';
    banner.setAttribute('role', 'region');
    banner.setAttribute('aria-label', 'Cookie-Hinweis');
    banner.innerHTML = [
      '<h2>Cookies & Statistik</h2>',
      '<p>Wenn Sie zustimmen, messen wir anonymisiert, welche Seiten und Buttons genutzt werden. So können wir Hinweise und Material verbessern. Mehr dazu in der <a href="/legal/datenschutz.html">Datenschutzerklärung</a>.</p>',
      '<div class="cookie-actions">',
      '<button class="btn btn-primary" type="button" data-cookie-accept>Akzeptieren</button>',
      '<button class="btn btn-ghost" type="button" data-cookie-decline>Ablehnen</button>',
      '</div>'
    ].join('');

    document.body.appendChild(banner);

    banner.querySelector('[data-cookie-accept]').addEventListener('click', function () {
      localStorage.setItem(META_CONSENT_KEY, 'granted');
      banner.hidden = true;
      trackPageView();
    });

    banner.querySelector('[data-cookie-decline]').addEventListener('click', function () {
      localStorage.setItem(META_CONSENT_KEY, 'denied');
      banner.hidden = true;
    });
  }

  function bindEvents() {
    trackPageView();

    document.querySelectorAll('[data-event]').forEach(function (link) {
      link.addEventListener('click', function () {
        track(this.dataset.event, {
          label: this.dataset.label || this.textContent.trim(),
          page: document.body.dataset.pageName || ''
        });
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    preserveParams();
    ensureConsentBanner();
    bindEvents();
  });
})();
