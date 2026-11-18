document.addEventListener("DOMContentLoaded", async function () {
  var trend = document.getElementById("viewsTrendChart"), status = document.getElementById("statusBreakdownChart");
  if ((!trend && !status) || typeof Chart === "undefined") return;
  var url = (trend || status).dataset.analyticsUrl;
  var data;
  try { var res = await fetch(url, { credentials: "same-origin" }); data = await res.json(); } catch (e) { return; }
  var grid = "rgba(43,22,66,.08)", tick = "#655B76";
  if (trend) new Chart(trend, {
    type: "line",
    data: { labels: data.daily_views.map(function (d) { return d.day.slice(5); }), datasets: [{ label: "Page views", data: data.daily_views.map(function (d) { return d.count; }), borderColor: "#5B3A9A", backgroundColor: "rgba(91,58,154,.14)", borderWidth: 3, pointBackgroundColor: "#fff", pointBorderColor: "#5B3A9A", pointBorderWidth: 2, pointRadius: 3, fill: true, tension: .38 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false }, ticks: { color: tick } }, y: { beginAtZero: true, grid: { color: grid }, ticks: { color: tick, precision: 0 } } } }
  });
  if (status) new Chart(status, {
    type: "doughnut",
    data: { labels: data.status_breakdown.map(function (s) { return s.label; }), datasets: [{ data: data.status_breakdown.map(function (s) { return s.count; }), backgroundColor: ["#5B3A9A", "#C79A3B", "#2B7A58", "#2B1642", "#B3363F"], borderWidth: 0 }] },
    options: { responsive: true, maintainAspectRatio: false, cutout: "66%", plugins: { legend: { position: "bottom", labels: { color: tick, usePointStyle: true } } } }
  });
});
