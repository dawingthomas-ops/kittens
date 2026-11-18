/* Kitten gallery: thumbnail swap, lightbox with keyboard + swipe, and the
   sticky mobile reserve bar. */
(function () {
  "use strict";
  var main = document.querySelector("[data-gallery-main]");
  var thumbs = Array.prototype.slice.call(document.querySelectorAll("[data-gallery-thumb]"));
  if (!main) return;
  var img = main.querySelector("img");
  var items = thumbs.length ? thumbs.map(function (t) { return { src: t.getAttribute("data-full"), alt: t.getAttribute("data-alt") || "" }; }) : [{ src: img.src, alt: img.alt }];
  var index = 0;

  function show(i) {
    index = (i + items.length) % items.length;
    img.classList.add("swap");
    setTimeout(function () {
      img.src = items[index].src; img.alt = items[index].alt;
      img.onload = function () { img.classList.remove("swap"); }; setTimeout(function () { img.classList.remove("swap"); }, 250);
    }, 160);
    thumbs.forEach(function (t, k) { t.setAttribute("aria-current", k === index ? "true" : "false"); });
  }
  thumbs.forEach(function (t, i) { t.addEventListener("click", function () { show(i); }); });

  var lb = document.createElement("div");
  lb.className = "lightbox"; lb.setAttribute("role", "dialog"); lb.setAttribute("aria-modal", "true"); lb.setAttribute("aria-label", "Photo viewer");
  lb.innerHTML = '<button class="lb-btn lb-close" aria-label="Close photo viewer">&times;</button><button class="lb-btn lb-prev" aria-label="Previous photo">&#8249;</button><img alt=""><button class="lb-btn lb-next" aria-label="Next photo">&#8250;</button><div class="lb-cap"></div>';
  document.body.appendChild(lb);
  var lbImg = lb.querySelector("img"), cap = lb.querySelector(".lb-cap"), opener = null;
  function paint() { lbImg.src = items[index].src; lbImg.alt = items[index].alt; cap.textContent = items[index].alt + (items.length > 1 ? "  (" + (index + 1) + " of " + items.length + ")" : ""); }
  function open() { opener = document.activeElement; paint(); lb.classList.add("open"); document.body.style.overflow = "hidden"; lb.querySelector(".lb-close").focus(); }
  function close() { lb.classList.remove("open"); document.body.style.overflow = ""; if (opener) opener.focus(); }
  function step(d) { index = (index + d + items.length) % items.length; paint(); show(index); }
  main.addEventListener("click", open);
  lb.addEventListener("click", function (e) { if (e.target === lb || e.target.closest(".lb-close")) close(); });
  lb.querySelector(".lb-prev").addEventListener("click", function () { step(-1); });
  lb.querySelector(".lb-next").addEventListener("click", function () { step(1); });
  if (items.length < 2) { lb.querySelector(".lb-prev").hidden = true; lb.querySelector(".lb-next").hidden = true; }
  document.addEventListener("keydown", function (e) {
    if (!lb.classList.contains("open")) return;
    if (e.key === "Escape") close(); if (e.key === "ArrowLeft") step(-1); if (e.key === "ArrowRight") step(1);
  });
  var sx = 0;
  lb.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener("touchend", function (e) { var dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 50) step(dx < 0 ? 1 : -1); });

  var bar = document.querySelector(".mobile-bar"), cta = document.querySelector("[data-primary-cta]");
  if (bar && cta && "IntersectionObserver" in window) {
    new IntersectionObserver(function (en) { bar.classList.toggle("show", !en[0].isIntersecting); }, { threshold: 0 }).observe(cta);
  }
})();
