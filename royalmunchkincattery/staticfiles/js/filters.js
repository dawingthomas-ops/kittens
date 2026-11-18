/* Instant filtering: fetches the same server-rendered results partial, so
   markup lives in one template. Falls back to a normal GET submit on error. */
(function () {
  "use strict";
  var form = document.getElementById("filter-form");
  var host = document.getElementById("results");
  if (!form || !host) return;
  var timer = 0, controller = null;

  var range = form.querySelector("#f-max"), out = form.querySelector("#f-max-out");
  function paintRange() {
    if (!range) return;
    var min = +range.min, max = +range.max, pct = ((+range.value - min) / (max - min)) * 100;
    range.style.setProperty("--fill", pct + "%");
    if (out) out.textContent = "$" + (+range.value).toLocaleString();
  }
  paintRange();

  function queryString() {
    var params = new URLSearchParams(new FormData(form));
    Array.from(params.keys()).forEach(function (k) { if (!params.get(k)) params.delete(k); });
    if (range && +range.value >= +range.max) params.delete("max_price");
    return params.toString();
  }

  function run(push) {
    if (controller) controller.abort();
    controller = new AbortController();
    var qs = queryString(), url = form.getAttribute("action") || location.pathname;
    var grid = host.querySelector(".kitten-grid"); if (grid) grid.classList.add("is-loading");
    host.setAttribute("aria-busy", "true");
    fetch(url + (qs ? "?" + qs : ""), { headers: { "X-Requested-With": "fetch" }, signal: controller.signal })
      .then(function (r) { if (!r.ok) throw new Error("bad response"); return r.text(); })
      .then(function (html) {
        host.innerHTML = html;
        if (push !== false) history.replaceState({}, "", url + (qs ? "?" + qs : ""));
        if (window.RMCPaintFavs) window.RMCPaintFavs(host);
        if (window.RMCBindTilt) window.RMCBindTilt(host);
        host.querySelectorAll(".kitten-card").forEach(function (c, i) { c.animate([{ opacity: 0, transform: "translateY(16px) scale(.98)" }, { opacity: 1, transform: "none" }], { duration: 480, delay: Math.min(i, 8) * 45, easing: "cubic-bezier(.22,1,.36,1)", fill: "backwards" }); });
        host.removeAttribute("aria-busy");
      })
      .catch(function (err) { if (err.name !== "AbortError") form.submit(); });
  }

  form.addEventListener("input", function (e) {
    if (e.target === range) paintRange();
    clearTimeout(timer); timer = setTimeout(run, e.target.type === "text" ? 320 : 120);
  });
  form.addEventListener("submit", function (e) { e.preventDefault(); clearTimeout(timer); run(); });
  var reset = form.querySelector("[data-reset]");
  if (reset) reset.addEventListener("click", function (e) { e.preventDefault(); form.reset(); if (range) range.value = range.max; paintRange(); run(); });

  host.addEventListener("click", function (e) {
    var a = e.target.closest("a[data-page]"); if (!a) return;
    e.preventDefault();
    fetch(a.href, { headers: { "X-Requested-With": "fetch" } }).then(function (r) { return r.text(); }).then(function (html) {
      host.innerHTML = html; history.replaceState({}, "", a.href);
      if (window.RMCPaintFavs) window.RMCPaintFavs(host); if (window.RMCBindTilt) window.RMCBindTilt(host);
      host.scrollIntoView({ behavior: "smooth", block: "start" });
    }).catch(function () { location.href = a.href; });
  });
})();
