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
        url.searchParams.set(key, value);
      });
      link.href = url.pathname + url.search + url.hash;
    });
  }

  function bindEvents() {
    const pageType = document.body.dataset.pageType;
    if (pageType === 'partner') {
      track('partner_page_view', { page: document.body.dataset.pageName || '' });
    }

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
    bindEvents();
  });
})();
