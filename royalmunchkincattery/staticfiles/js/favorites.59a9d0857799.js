(function () {
  "use strict";
  var host = document.getElementById("fav-results");
  if (!host) return;
  var url = host.getAttribute("data-url");
  function load() {
    var slugs = window.RMCFavs ? window.RMCFavs.read() : [];
    if (!slugs.length) { host.innerHTML = '<p class="empty-state">No saved kittens yet. Tap the heart on any kitten to keep it here.</p>'; return; }
    fetch(url + "?slugs=" + encodeURIComponent(slugs.join(",")), { headers: { "X-Requested-With": "fetch" } })
      .then(function (r) { return r.text(); })
      .then(function (html) { host.innerHTML = html; window.RMCPaintFavs && window.RMCPaintFavs(host); window.RMCBindTilt && window.RMCBindTilt(host); })
      .catch(function () { host.innerHTML = '<p class="empty-state">We could not load your saved kittens. Please refresh.</p>'; });
  }
  document.addEventListener("rmc:favorites", function (e) { if (!e.detail.added) { var card = document.querySelector('[data-fav="' + e.detail.slug + '"]'); if (card) { var c = card.closest(".kitten-card"); c.style.transition = "opacity .3s, transform .3s"; c.style.opacity = 0; c.style.transform = "scale(.94)"; setTimeout(load, 300); } } });
  load();
})();
