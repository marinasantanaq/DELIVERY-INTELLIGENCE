const API = "/api";
let revenueChart = null;
let hourlyChart = null;

const money = value => new Intl.NumberFormat("pt-BR", {
  style: "currency", currency: "BRL", maximumFractionDigits: 0
}).format(value || 0);

const number = value => new Intl.NumberFormat("pt-BR").format(value || 0);

function currentFilters() {
  return {
    restaurant: document.querySelector("#restaurantFilter").value || "Todos",
    period: document.querySelector("#periodFilter").value || "30d"
  };
}

async function api(path) {
  const filters = currentFilters();
  const params = new URLSearchParams(filters);
  const response = await fetch(`${API}/${path}?${params.toString()}`);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Falha ao consultar ${path}: ${detail}`);
  }
  return response.json();
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function showToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 2600);
}

async function loadFilters() {
  const data = await (await fetch(`${API}/filters`)).json();
  const select = document.querySelector("#restaurantFilter");
  select.innerHTML = data.restaurants.map(name =>
    `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`
  ).join("");
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[char]));
}

async function loadOverview() {
  const data = await api("overview");
  setText("revenueValue", money(data.revenue));
  setText("ordersValue", number(data.orders));
  setText("ticketValue", money(data.ticket));
  setText("cancelValue", `${data.cancellation_rate.toFixed(1).replace(".", ",")}%`);
  setText("prepValue", `${data.prep_time.toFixed(1).replace(".", ",")} min`);
  setText("deliveryValue", `${data.delivery_time.toFixed(1).replace(".", ",")} min`);
  setText("ratingValue", `${data.rating.toFixed(2).replace(".", ",")} / 5`);
  setText("deliveredValue", number(data.delivered));
}

function makeChart(canvasId, previous, config) {
  if (previous) previous.destroy();
  return new Chart(document.getElementById(canvasId), config);
}

async function loadCharts() {
  const [revenue, hourly] = await Promise.all([api("revenue"), api("hourly")]);
  revenueChart = makeChart("revenueChart", revenueChart, {
    type: "line",
    data: { labels: revenue.labels, datasets: [{
      data: revenue.values, borderColor: "#7968ed", backgroundColor: "rgba(121,104,237,.12)",
      fill: true, tension: .38, borderWidth: 2.5, pointRadius: 2, pointHoverRadius: 5
    }]},
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => money(ctx.raw) } } },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#9aa4b2", maxTicksLimit: 7, font: { size: 9 } } },
        y: { grid: { color: "#f0f2f6" }, ticks: { color: "#9aa4b2", font: { size: 9 }, callback: value => `R$${value}` } }
      }
    }
  });
  hourlyChart = makeChart("hourlyChart", hourlyChart, {
    type: "bar",
    data: { labels: hourly.labels, datasets: [{
      data: hourly.values, backgroundColor: hourly.values.map((_, i) => i >= 18 && i <= 21 ? "#7968ed" : "#dcd8fb"),
      borderRadius: 5, maxBarThickness: 13
    }]},
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => `${ctx.raw} pedidos` } } },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#9aa4b2", font: { size: 8 }, maxTicksLimit: 12 } },
        y: { beginAtZero: true, grid: { color: "#f0f2f6" }, ticks: { color: "#9aa4b2", precision: 0, font: { size: 9 } } }
      }
    }
  });
}

async function loadRestaurants() {
  const rows = await api("restaurants");
  const tbody = document.querySelector("#restaurantTable");
  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="4" class="empty">Nenhum dado para os filtros selecionados.</td></tr>';
    return;
  }
  tbody.innerHTML = rows.map(row => `
    <tr>
      <td>${escapeHtml(row.name)}</td>
      <td>${number(row.orders)}</td>
      <td>${money(row.revenue)}</td>
      <td>${row.cancellations.toFixed(1).replace(".", ",")}%</td>
    </tr>`).join("");
}

async function loadRecentOrders() {
  const rows = await api("recent-orders");
  const container = document.querySelector("#recentOrders");
  if (!rows.length) {
    container.innerHTML = '<div class="empty">Nenhum pedido encontrado.</div>';
    return;
  }
  container.innerHTML = rows.map(row => `
    <div class="recent-item">
      <div>
        <div class="recent-name">#${row.id} · ${escapeHtml(row.restaurant)}</div>
        <div class="recent-meta">${row.date}</div>
        <span class="status ${escapeHtml(row.status)}">${row.status.replace("_", " ")}</span>
      </div>
      <div class="recent-value">${money(row.value)}</div>
    </div>`).join("");
}

async function refreshDashboard() {
  const button = document.querySelector("#refreshButton");
  button.classList.add("spinning");
  try {
    await Promise.all([
      loadOverview(), loadCharts(), loadRestaurants(), loadRecentOrders()
    ]);
    setText("updatedLabel", `Atualizado às ${new Date().toLocaleTimeString("pt-BR", {hour: "2-digit", minute: "2-digit"})}`);
  } catch (error) {
    console.error(error);
    showToast("Não foi possível carregar os dados. Verifique se o pipeline foi executado.");
  } finally {
    button.classList.remove("spinning");
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  setText("todayLabel", new Date().toLocaleDateString("pt-BR", {day: "2-digit", month: "long", year: "numeric"}));
  try {
    await loadFilters();
    await refreshDashboard();
  } catch (error) {
    console.error(error);
    showToast("Não foi possível conectar à API. Execute o servidor pelo terminal.");
  }

  document.querySelector("#restaurantFilter").addEventListener("change", refreshDashboard);
  document.querySelector("#periodFilter").addEventListener("change", refreshDashboard);
  document.querySelector("#refreshButton").addEventListener("click", refreshDashboard);
  document.querySelector("#mobileMenu").addEventListener("click", () => {
    document.querySelector("#sidebar").classList.toggle("open");
  });
  document.querySelectorAll(".nav-link").forEach(link => link.addEventListener("click", () => {
    document.querySelector("#sidebar").classList.remove("open");
  }));
});
