/* Social proof: occasionally shows a recent, real reservation (last 3 days).
   Content comes from the public API and is inserted as text, never HTML. */
(function () {
  "use strict";
  var SEEN = "rmc_toast_seen", LAST = "rmc_toast_last", EVERY = 180000, SHOW = 6500;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  function get(k, d) { try { var v = sessionStorage.getItem(k); return v === null ? d : v; } catch (e) { return d; } }
  function set(k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }
  function seen() { try { return JSON.parse(get(SEEN, "[]")); } catch (e) { return []; } }
  var active = false;

  function hide(t) { if (!t.parentNode) return; t.classList.remove("is-visible"); t.classList.add("is-hiding"); setTimeout(function () { t.parentNode && t.parentNode.removeChild(t); active = false; }, 300); }
  function show(item) {
    var box = document.querySelector(".reservation-toast-container");
    if (!box) { box = document.createElement("div"); box.className = "reservation-toast-container"; box.setAttribute("aria-live", "polite"); document.body.appendChild(box); }
    var t = document.createElement("a"); t.className = "reservation-toast"; t.href = item.url || "/kittens/";
    var pic;
    if (item.image) { pic = document.createElement("img"); pic.src = item.image; pic.alt = ""; pic.className = "reservation-toast__image"; pic.width = 48; pic.height = 48; pic.onerror = function () { this.style.display = "none"; }; }
    else { pic = document.createElement("div"); pic.className = "reservation-toast__icon"; pic.textContent = "RM"; }
    var c = document.createElement("div"); c.className = "reservation-toast__content";
    var title = document.createElement("div"); title.className = "reservation-toast__title"; title.textContent = "Recently reserved";
    var msg = document.createElement("div"); msg.className = "reservation-toast__message"; msg.textContent = item.toast_message || (item.name + " was reserved recently.");
    c.appendChild(title); c.appendChild(msg);
    var x = document.createElement("button"); x.type = "button"; x.className = "reservation-toast__close"; x.setAttribute("aria-label", "Dismiss"); x.textContent = "\u00d7";
    x.addEventListener("click", function (e) { e.preventDefault(); e.stopPropagation(); hide(t); });
    t.appendChild(pic); t.appendChild(c); t.appendChild(x); box.appendChild(t);
    requestAnimationFrame(function () { t.classList.add("is-visible"); });
    setTimeout(function () { hide(t); }, SHOW);
  }
  function maybe() {
    if (active) return;
    fetch("/api/kittens/reserved-toasts/").then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (p) {
      var done = seen(), pool = (p.results || []).filter(function (k) { return k && k.name && done.indexOf(k.id) === -1; });
      if (!pool.length) return;
      var k = pool[Math.floor(Math.random() * pool.length)]; done.push(k.id); set(SEEN, JSON.stringify(done));
      active = true; show(k);
    }).catch(function () {});
  }
  function tick() { var last = +get(LAST, "0"); if (!last || Date.now() - last >= EVERY) { set(LAST, String(Date.now())); maybe(); } }
  setTimeout(tick, 9000); setInterval(tick, 20000);
})();
