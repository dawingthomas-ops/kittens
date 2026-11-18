/* Kitten match quiz: turns the questions into a one-at-a-time stepper.
   Without JS the whole form is visible and submits normally. */
(function () {
  "use strict";
  var form = document.getElementById("quiz-form");
  if (!form) return;
  var panes = Array.prototype.slice.call(form.querySelectorAll(".quiz-q"));
  var bars = Array.prototype.slice.call(document.querySelectorAll(".steps-bar i"));
  var back = form.querySelector("[data-back]"), next = form.querySelector("[data-next]"), submit = form.querySelector("[data-submit]");
  var i = 0;
  form.classList.add("is-stepper");
  var sb = document.querySelector(".steps-bar"); if (sb) sb.hidden = false;
  function render(dir) {
    panes.forEach(function (p, k) {
      p.hidden = k !== i; p.classList.remove("enter", "enter-back");
      if (k === i) { void p.offsetWidth; p.classList.add(dir < 0 ? "enter-back" : "enter"); }
    });
    bars.forEach(function (b, k) { b.classList.toggle("done", k <= i); });
    back.hidden = i === 0; next.hidden = i === panes.length - 1; submit.hidden = i !== panes.length - 1;
  }
  next.addEventListener("click", function () { if (i < panes.length - 1) { i++; render(1); } });
  back.addEventListener("click", function () { if (i > 0) { i--; render(-1); } });
  form.addEventListener("change", function (e) {
    if (e.target.type === "radio" && i < panes.length - 1) setTimeout(function () { i++; render(1); }, 260);
  });
  var budget = form.querySelector("#q-budget"), out = form.querySelector("#q-budget-out");
  function paint() { var pct = ((+budget.value - +budget.min) / (+budget.max - +budget.min)) * 100; budget.style.setProperty("--fill", pct + "%"); out.textContent = "$" + (+budget.value).toLocaleString(); }
  if (budget) { budget.addEventListener("input", paint); paint(); }
  render(1);
})();
