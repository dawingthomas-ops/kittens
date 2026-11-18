/* Reservation form: three animated steps. Server-side validation still runs
   on submit; if the server returns errors the pane containing them opens. */
(function () {
  "use strict";
  var form = document.getElementById("reserve-form");
  if (!form) return;
  var panes = Array.prototype.slice.call(form.querySelectorAll(".step-pane"));
  var bars = Array.prototype.slice.call(document.querySelectorAll(".steps-bar i"));
  var back = form.querySelector("[data-back]"), next = form.querySelector("[data-next]"), submit = form.querySelector("[data-submit]");
  var i = 0;
  var errPane = panes.findIndex(function (p) { return p.querySelector(".errorlist"); });
  if (errPane > -1) i = errPane;
  form.classList.add("is-stepper");
  var sb = document.querySelector(".steps-bar"); if (sb) sb.hidden = false;
  function valid(p) {
    var ok = true;
    p.querySelectorAll("input, select, textarea").forEach(function (el) { if (!el.checkValidity()) { if (ok) el.reportValidity(); ok = false; } });
    return ok;
  }
  function render(dir) {
    panes.forEach(function (p, k) { p.hidden = k !== i; p.classList.remove("enter", "enter-back"); if (k === i) { void p.offsetWidth; p.classList.add(dir < 0 ? "enter-back" : "enter"); } });
    bars.forEach(function (b, k) { b.classList.toggle("done", k <= i); });
    back.hidden = i === 0; next.hidden = i === panes.length - 1; submit.hidden = i !== panes.length - 1;
  }
  next.addEventListener("click", function () { if (valid(panes[i])) { i++; render(1); window.scrollTo({ top: form.offsetTop - 120, behavior: "smooth" }); } });
  back.addEventListener("click", function () { i--; render(-1); });
  render(1);
})();
