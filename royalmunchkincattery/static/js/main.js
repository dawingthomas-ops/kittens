/* American Munchkin House: site behaviour. Everything here is progressive
   enhancement; every page works with JavaScript disabled. */
(function () {
  "use strict";
  var doc = document.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  /* ---------- favorites (localStorage) ---------- */
  var KEY = "rmc_favorites_v1";
  var Favs = {
    read: function () { try { var v = JSON.parse(localStorage.getItem(KEY) || "[]"); return Array.isArray(v) ? v : []; } catch (e) { return []; } },
    write: function (list) { try { localStorage.setItem(KEY, JSON.stringify(list.slice(0, 40))); } catch (e) { /* storage blocked */ } },
    has: function (slug) { return this.read().indexOf(slug) !== -1; },
    toggle: function (slug) {
      var list = this.read(), i = list.indexOf(slug);
      if (i === -1) list.push(slug); else list.splice(i, 1);
      this.write(list); return i === -1;
    }
  };
  window.RMCFavs = Favs;

  function paintFavs(root) {
    (root || document).querySelectorAll("[data-fav]").forEach(function (btn) {
      var on = Favs.has(btn.getAttribute("data-fav"));
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
    var n = Favs.read().length;
    document.querySelectorAll("[data-fav-count]").forEach(function (el) { el.textContent = n; el.hidden = n === 0; });
  }
  window.RMCPaintFavs = paintFavs;

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-fav]");
    if (!btn) return;
    e.preventDefault();
    var slug = btn.getAttribute("data-fav");
    var added = Favs.toggle(slug);
    btn.setAttribute("aria-pressed", added ? "true" : "false");
    btn.classList.remove("burst"); void btn.offsetWidth; if (added) btn.classList.add("burst");
    paintFavs();
    document.querySelectorAll("[data-fav-count]").forEach(function (el) { el.classList.remove("bump"); void el.offsetWidth; el.classList.add("bump"); });
    document.dispatchEvent(new CustomEvent("rmc:favorites", { detail: { slug: slug, added: added } }));
  });

  /* ---------- nav drawer ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("primary-nav");
  if (nav) nav.querySelectorAll("a").forEach(function (a, i) { a.style.setProperty("--i", i); });
  function setNav(open) {
    document.body.classList.toggle("nav-open", open);
    if (toggle) { toggle.setAttribute("aria-expanded", open ? "true" : "false"); toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu"); }
  }
  if (toggle) toggle.addEventListener("click", function () { setNav(toggle.getAttribute("aria-expanded") !== "true"); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") setNav(false); });
  if (nav) nav.addEventListener("click", function (e) { if (e.target.closest("a")) setNav(false); });
  window.matchMedia("(min-width: 1061px)").addEventListener("change", function () { setNav(false); });

  /* ---------- header shrink + scroll progress ---------- */
  var header = document.getElementById("site-header");
  var bar = document.querySelector(".scroll-progress span");
  var ticking = false;
  function onScroll() {
    var y = window.scrollY || doc.scrollTop;
    if (header) header.classList.toggle("is-scrolled", y > 12);
    if (bar) { var max = doc.scrollHeight - window.innerHeight; bar.style.transform = "scaleX(" + (max > 0 ? Math.min(1, y / max) : 0) + ")"; }
    ticking = false;
  }
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  /* ---------- reveal on scroll ---------- */
  doc.classList.add("js");
  var revealEls = document.querySelectorAll(".reveal, [data-observe]");
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-visible", "reveal-in"); io.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
    revealEls.forEach(function (el, i) {
      if (el.classList.contains("reveal") && !el.style.getPropertyValue("--i")) {
        var sib = el.parentElement ? Array.prototype.indexOf.call(el.parentElement.children, el) : 0;
        el.style.setProperty("--i", Math.min(sib, 6));
      }
      io.observe(el);
    });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-visible", "reveal-in"); });
  }

  /* ---------- journey line draws as it enters view ---------- */
  document.querySelectorAll(".journey").forEach(function (j) {
    j.querySelectorAll(".journey-step").forEach(function (s, i) { s.style.setProperty("--i", i); });
    if (reduce || !("IntersectionObserver" in window)) { j.classList.add("is-in"); j.style.setProperty("--p", 1); return; }
    new IntersectionObserver(function (en, obs) {
      if (en[0].isIntersecting) { j.classList.add("is-in"); j.style.setProperty("--p", 1); obs.disconnect(); }
    }, { threshold: 0.35 }).observe(j);
  });

  /* ---------- count-up numbers ---------- */
  document.querySelectorAll("[data-count]").forEach(function (el) {
    var target = parseInt(el.getAttribute("data-count"), 10);
    if (isNaN(target) || reduce || !("IntersectionObserver" in window)) { el.textContent = target; return; }
    new IntersectionObserver(function (en, obs) {
      if (!en[0].isIntersecting) return; obs.disconnect();
      var start = performance.now(), dur = 900;
      (function step(t) { var p = Math.min(1, (t - start) / dur); el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(step); })(start);
    }).observe(el);
  });

  /* ---------- 3D tilt on kitten cards (mouse only) ---------- */
  function bindTilt(root) {
    if (reduce || !finePointer) return;
    (root || document).querySelectorAll("[data-tilt]:not([data-tilt-bound])").forEach(function (card) {
      card.setAttribute("data-tilt-bound", "1");
      card.addEventListener("pointermove", function (e) {
        var r = card.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        card.style.transform = "perspective(900px) rotateX(" + ((0.5 - y) * 5).toFixed(2) + "deg) rotateY(" + ((x - 0.5) * 6).toFixed(2) + "deg) translateY(-4px)";
        card.style.setProperty("--mx", (x * 100) + "%"); card.style.setProperty("--my", (y * 100) + "%");
      });
      card.addEventListener("pointerleave", function () { card.style.transform = ""; });
    });
  }
  window.RMCBindTilt = bindTilt; bindTilt();

  /* ---------- hero cat: eyes follow the cursor ---------- */
  var scene = document.querySelector(".cat-scene");
  if (scene && !reduce) {
    var pupils = scene.querySelectorAll(".pupil"), raf = 0, px = 0, py = 0;
    var move = function (e) {
      var pt = e.touches ? e.touches[0] : e;
      px = pt.clientX; py = pt.clientY;
      if (!raf) raf = requestAnimationFrame(function () {
        raf = 0;
        var r = scene.getBoundingClientRect(), cx = r.left + r.width * 0.5, cy = r.top + r.height * 0.5;
        var dx = px - cx, dy = py - cy, dist = Math.hypot(dx, dy) || 1, m = Math.min(7, dist / 40);
        var tx = (dx / dist) * m, ty = (dy / dist) * m * 0.8;
        pupils.forEach(function (p) { p.style.transform = "translate(" + tx.toFixed(1) + "px," + ty.toFixed(1) + "px)"; });
      });
    };
    window.addEventListener("pointermove", move, { passive: true });
    window.addEventListener("touchmove", move, { passive: true });
  }

  /* ---------- FAQ accordion: smooth open/close ---------- */
  document.querySelectorAll(".faq-item").forEach(function (item) {
    var summary = item.querySelector("summary"), panel = item.querySelector(".faq-answer");
    if (!summary || !panel || reduce) return;
    summary.addEventListener("click", function (e) {
      e.preventDefault();
      if (item.dataset.busy) return; item.dataset.busy = "1";
      var opening = !item.open, done = function () { delete item.dataset.busy; panel.style.height = ""; };
      if (opening) {
        item.open = true; var h = panel.scrollHeight; panel.style.height = "0px";
        panel.animate({ height: ["0px", h + "px"] }, { duration: 380, easing: "cubic-bezier(.22,1,.36,1)" }).onfinish = done;
      } else {
        var h2 = panel.offsetHeight;
        panel.animate({ height: [h2 + "px", "0px"] }, { duration: 300, easing: "cubic-bezier(.22,1,.36,1)" }).onfinish = function () { item.open = false; done(); };
      }
    });
  });

  /* ---------- share / copy link ---------- */
  document.querySelectorAll("[data-share]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var data = { title: document.title, url: location.href.split("#")[0] };
      if (navigator.share) { navigator.share(data).catch(function () {}); return; }
      if (navigator.clipboard) navigator.clipboard.writeText(data.url).then(function () { var old = btn.textContent; btn.textContent = "Link copied"; setTimeout(function () { btn.textContent = old; }, 1800); });
    });
  });

  /* ---------- reservation phone requirement ---------- */
  var prefs = document.querySelectorAll('input[name="contact_preference"]'), phone = document.getElementById("id_phone");
  if (prefs.length && phone) {
    var sync = function () { var c = document.querySelector('input[name="contact_preference"]:checked'); phone.required = !!c && c.value === "phone"; };
    prefs.forEach(function (r) { r.addEventListener("change", sync); }); sync();
  }

  /* ---------- form submit feedback ---------- */
  document.querySelectorAll("form[data-loading]").forEach(function (form) {
    form.addEventListener("submit", function () {
      var b = form.querySelector('button[type="submit"]'); if (b && form.checkValidity()) { b.classList.add("is-loading"); b.textContent = b.getAttribute("data-loading") || "Sending..."; }
    });
  });

  paintFavs();
  window.addEventListener("pageshow", function () { paintFavs(); });
})();
