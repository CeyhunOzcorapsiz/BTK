"use strict";

// --- Yardimcilar -------------------------------------------------------------

const TL = new Intl.NumberFormat("tr-TR", {
  style: "currency",
  currency: "TRY",
  maximumFractionDigits: 0,
});

const fmtTL = (v) => TL.format(v ?? 0);
const $ = (id) => document.getElementById(id);

async function getJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url} -> ${res.status}`);
  return res.json();
}

// --- Durum / saglik ----------------------------------------------------------

async function loadStatus() {
  try {
    const h = await getJson("/api/health");
    $("sourceBadge").textContent = `veri: ${h.data_source} (${h.transaction_count})`;
    $("geminiBadge").textContent = h.gemini_enabled ? "AI: Gemini" : "AI: lokal motor";
  } catch {
    $("geminiBadge").textContent = "AI: baglanti yok";
  }
}

// --- KPI ---------------------------------------------------------------------

function renderPeriods(donem) {
  $("periodTrend").textContent = `Aylik - ${donem}`;
  $("periodBudget").textContent = `${donem} yil toplami`;
  $("periodCategory").textContent = `${donem} yil toplami - gider`;
  $("periodAnomaly").textContent = `${donem} - tum donem`;
}

function renderKpis(ozet) {
  $("kpiGelir").textContent = fmtTL(ozet.gelir);
  $("kpiGider").textContent = fmtTL(ozet.gider);
  const net = $("kpiNet");
  net.textContent = fmtTL(ozet.net_kar);
  net.className = ozet.net_kar >= 0 ? "good" : "bad";
  const marj = $("kpiMarj");
  marj.textContent = `%${ozet.kar_marji}`;
  marj.className = ozet.kar_marji >= 0 ? "good" : "bad";
}

// --- Grafikler ---------------------------------------------------------------

const PALETTE = [
  "#4f46e5", "#0ea5e9", "#16a34a", "#d97706", "#dc2626",
  "#9333ea", "#0d9488", "#db2777", "#65a30d", "#475569",
];

function renderTrend(trend) {
  new Chart($("trendChart"), {
    type: "line",
    data: {
      labels: trend.map((r) => r.ay),
      datasets: [
        { label: "Gelir", data: trend.map((r) => r.gelir),
          borderColor: "#16a34a", backgroundColor: "#16a34a22", tension: .3, fill: true },
        { label: "Gider", data: trend.map((r) => r.gider),
          borderColor: "#dc2626", backgroundColor: "#dc262622", tension: .3, fill: true },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" } },
      scales: { y: { ticks: { callback: (v) => `${(v / 1000000).toFixed(1)}M` } } },
    },
  });
}

function renderBudget(rows) {
  new Chart($("budgetChart"), {
    type: "bar",
    data: {
      labels: rows.map((r) => r.departman),
      datasets: [
        { label: "Butce", data: rows.map((r) => r.butce), backgroundColor: "#c7d2fe" },
        { label: "Gerceklesen", data: rows.map((r) => r.gerceklesen), backgroundColor: "#4f46e5" },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" } },
      scales: { y: { ticks: { callback: (v) => `${(v / 1000000).toFixed(1)}M` } } },
    },
  });
}

function renderCategory(rows) {
  new Chart($("categoryChart"), {
    type: "doughnut",
    data: {
      labels: rows.map((r) => r.kategori),
      datasets: [{ data: rows.map((r) => r.tutar), backgroundColor: PALETTE }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { position: "right", labels: { boxWidth: 12, font: { size: 11 } } },
        tooltip: { callbacks: { label: (c) => `${c.label}: ${fmtTL(c.parsed)}` } },
      },
    },
  });
}

// --- Anomali tablosu ---------------------------------------------------------

function renderAnomalies(data) {
  const tbody = $("anomalyTable");
  if (!data.anomalies.length) {
    tbody.innerHTML = `<tr><td colspan="5">Anomali bulunamadi.</td></tr>`;
    return;
  }
  tbody.innerHTML = data.anomalies
    .map((a) => `
      <tr class="${a.sapma_yuzde >= 100 ? "severe" : ""}">
        <td>${a.tarih}</td>
        <td>${a.departman}</td>
        <td>${a.kategori}</td>
        <td>${fmtTL(a.tutar)}</td>
        <td><span class="sapma-tag">+%${a.sapma_yuzde}</span></td>
      </tr>`)
    .join("");
}

// --- Insight metinleri -------------------------------------------------------

function renderInsights(ins) {
  $("insightTrend").textContent = ins.trend;
  $("insightBudget").textContent = ins.butce;
  $("insightCategory").textContent = ins.kategori;
  $("insightAnomaly").textContent = ins.anomali;
}

// --- Chat --------------------------------------------------------------------

const chatWindow = $("chatWindow");
const chatForm = $("chatForm");
const chatInput = $("chatInput");
const chatBtn = chatForm.querySelector("button");

function addMessage(role, text) {
  const el = document.createElement("div");
  el.className = `message ${role}`;
  el.textContent = text;
  chatWindow.appendChild(el);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return el;
}

function addMeta(text) {
  const el = document.createElement("div");
  el.className = "msg-meta";
  el.textContent = text;
  chatWindow.appendChild(el);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function askAssistant(prompt) {
  addMessage("user", prompt);
  const loading = addMessage("assistant loading", "Veriyi sorguluyorum...");
  chatBtn.disabled = true;
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: prompt }),
    });
    const data = await res.json();
    if (!res.ok) {
      loading.classList.remove("loading");
      loading.textContent = data.error?.message || "Bir hata olustu.";
      return;
    }
    loading.classList.remove("loading");
    loading.textContent = data.answer;
    const kaynak = data.provider === "gemini" ? "Gemini" : "lokal motor";
    addMeta(`Kaynak: ${kaynak}${data.cached ? " (cache)" : ""}`);
  } catch {
    loading.classList.remove("loading");
    loading.textContent = "Sunucuya ulasilamadi.";
  } finally {
    chatBtn.disabled = false;
  }
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const prompt = chatInput.value.trim();
  if (!prompt) return;
  chatInput.value = "";
  askAssistant(prompt);
});

document.querySelectorAll(".quick-prompts button").forEach((btn) => {
  btn.addEventListener("click", () => askAssistant(btn.dataset.prompt));
});

// --- Baslangic ---------------------------------------------------------------

async function init() {
  loadStatus();
  addMessage("assistant", "Merhaba! Finans verisi hakkinda soru sorabilirsiniz.");
  try {
    const [dash, anomalies, insights] = await Promise.all([
      getJson("/api/dashboard"),
      getJson("/api/anomalies"),
      getJson("/api/insights"),
    ]);
    renderPeriods(dash.donem);
    renderKpis(dash.ozet);
    renderTrend(dash.aylik_trend);
    renderBudget(dash.butce_vs_gerceklesen);
    renderCategory(dash.kategori_dagilimi);
    renderAnomalies(anomalies);
    renderInsights(insights);
  } catch (err) {
    console.error("Dashboard yuklenemedi:", err);
    document.querySelectorAll(".insight").forEach((el) => {
      el.textContent = "Veri yuklenemedi. Backend calisiyor mu?";
    });
  }
}

init();
