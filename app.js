"use strict";

// --- i18n sozlugu ------------------------------------------------------------

const I18N = {
  tr: {
    brandSub: "AI entegre kurumsal finans asistani",
    navGenel: "Genel Bakis", navTrend: "Gelir / Gider Trendi",
    navButce: "Butce vs Gerceklesen", navKategori: "Kategori Dagilimi",
    navAnomali: "Anomaliler", navSor: "Veriye Sor",
    kpiGelir: "Toplam Gelir", kpiGider: "Toplam Gider",
    kpiNet: "Net Kar", kpiMarj: "Kar Marji",
    cardKategori: "Gider Kategori Dagilimi", cardAnomali: "Anomali Tespiti",
    cardTrendSub: "Aylik Seyir", cardButceSub: "Departman Bazli",
    cardKategoriSub: "Kategori Payi", cardAnomaliSub: "Alisilmadik Harcamalar",
    thTarih: "Tarih", thDepartman: "Departman", thKategori: "Kategori",
    thTutar: "Tutar", thSapma: "Sapma",
    chatDesc: "Dogal dilde soru sor; AI gercek veriyi sorgular.",
    chatSend: "Sor", chatPlaceholder: "Verilere bir soru sorun...",
    qp1: "Ocak'ta en cok harcayan departman", qp2: "Toplam gelir",
    qp3: "En buyuk gider kalemi",
    insightLabel: "AI yorumu:", insightLoading: "Analiz yukleniyor...",
    chatWelcome: "Merhaba! Finans verisi hakkinda soru sorabilirsiniz.",
    chatLoading: "Veriyi sorguluyorum...", chatError: "Bir hata olustu.",
    chatNoServer: "Sunucuya ulasilamadi.",
    sourceLabel: "Kaynak", srcGemini: "Gemini", srcLocal: "lokal motor",
    cached: "cache",
    allYear: "Tum yil", anomalyEmpty: "Bu donem icin anomali bulunamadi.",
    periodMonthly: "Aylik", yearTotal: "yil toplami", allPeriod: "tum donem",
    giderWord: "gider", dataBadge: "veri", aiBadge: "AI", aiConnErr: "baglanti yok",
    chartGelir: "Gelir", chartGider: "Gider", chartButce: "Butce",
    chartGerceklesen: "Gerceklesen", axisAmount: "Tutar (TL)",
  },
  en: {
    brandSub: "AI-integrated corporate finance assistant",
    navGenel: "Overview", navTrend: "Revenue / Expense Trend",
    navButce: "Budget vs Actual", navKategori: "Category Breakdown",
    navAnomali: "Anomalies", navSor: "Ask the Data",
    kpiGelir: "Total Revenue", kpiGider: "Total Expense",
    kpiNet: "Net Profit", kpiMarj: "Profit Margin",
    cardKategori: "Expense Category Breakdown", cardAnomali: "Anomaly Detection",
    cardTrendSub: "Monthly Trend", cardButceSub: "By Department",
    cardKategoriSub: "Category Share", cardAnomaliSub: "Unusual Expenses",
    thTarih: "Date", thDepartman: "Department", thKategori: "Category",
    thTutar: "Amount", thSapma: "Deviation",
    chatDesc: "Ask in natural language; the AI queries the real data.",
    chatSend: "Ask", chatPlaceholder: "Ask a question about the data...",
    qp1: "Top spending department in January", qp2: "Total revenue",
    qp3: "Largest expense item",
    insightLabel: "AI insight:", insightLoading: "Loading analysis...",
    chatWelcome: "Hello! You can ask questions about the finance data.",
    chatLoading: "Querying the data...", chatError: "An error occurred.",
    chatNoServer: "Could not reach the server.",
    sourceLabel: "Source", srcGemini: "Gemini", srcLocal: "local engine",
    cached: "cached",
    allYear: "All year", anomalyEmpty: "No anomalies found for this period.",
    periodMonthly: "Monthly", yearTotal: "annual total", allPeriod: "all period",
    giderWord: "expense", dataBadge: "data", aiBadge: "AI", aiConnErr: "no connection",
    chartGelir: "Revenue", chartGider: "Expense", chartButce: "Budget",
    chartGerceklesen: "Actual", axisAmount: "Amount (TL)",
  },
};

let currentLang = localStorage.getItem("lang") || "tr";
const t = (k) => (I18N[currentLang] && I18N[currentLang][k]) || I18N.tr[k] || k;

// --- Yardimcilar -------------------------------------------------------------

const TL = new Intl.NumberFormat("tr-TR", {
  style: "currency", currency: "TRY", maximumFractionDigits: 0,
});
const COMPACT = new Intl.NumberFormat("tr-TR", {
  notation: "compact", maximumFractionDigits: 1,
});
const fmtTL = (v) => TL.format(v ?? 0);
const fmtAxis = (v) => COMPACT.format(v ?? 0);
const $ = (id) => document.getElementById(id);

async function getJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url} -> ${res.status}`);
  return res.json();
}

const PALETTE = [
  "#4f46e5", "#0ea5e9", "#16a34a", "#d97706", "#dc2626",
  "#9333ea", "#0d9488", "#db2777", "#65a30d", "#475569",
];

// --- Veri cache (ay bazli) ---------------------------------------------------

const cache = { dashboard: {}, anomalies: {}, insights: {} };
const charts = {};
let monthsLoaded = false;

const ayKey = (ay) => ay || "all";
const ayQuery = (ay) => (ay ? `?ay=${encodeURIComponent(ay)}` : "");

async function getDashboard(ay) {
  const k = ayKey(ay);
  if (!cache.dashboard[k]) cache.dashboard[k] = await getJson("/api/dashboard" + ayQuery(ay));
  return cache.dashboard[k];
}
async function getAnomalies(ay) {
  const k = ayKey(ay);
  if (!cache.anomalies[k]) cache.anomalies[k] = await getJson("/api/anomalies" + ayQuery(ay));
  return cache.anomalies[k];
}
async function getInsights(ay) {
  const k = ayKey(ay);
  if (!cache.insights[k]) cache.insights[k] = await getJson("/api/insights" + ayQuery(ay));
  return cache.insights[k];
}
// Insight yaniti iki dillidir: {tr:{...}, en:{...}}. Aktif dili sec.
const pickInsights = (ins) => ins[currentLang] || ins.tr;

// --- Tema --------------------------------------------------------------------

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  $("themeToggle").textContent = theme === "dark" ? "☀️" : "🌙";
  const dark = theme === "dark";
  Chart.defaults.color = dark ? "#94a3b8" : "#64748b";
  Chart.defaults.borderColor = dark ? "#334155" : "#e2e8f0";
}

// --- Dil ---------------------------------------------------------------------

function applyLang(lang) {
  currentLang = lang;
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPh);
  });
  document.querySelectorAll(".month-select").forEach((s) => {
    if (s.options[0]) s.options[0].textContent = t("allYear");
  });
  document.querySelectorAll("[data-welcome]").forEach((el) => {
    el.textContent = t("chatWelcome");
  });
  $("langSelect").value = lang;
}

// --- Durum -------------------------------------------------------------------

async function loadStatus() {
  try {
    const h = await getJson("/api/health");
    $("sourceBadge").textContent = `${t("dataBadge")}: ${h.data_source} (${h.transaction_count})`;
    $("geminiBadge").textContent = `${t("aiBadge")}: ${h.gemini_enabled ? "Gemini" : t("srcLocal")}`;
  } catch {
    $("geminiBadge").textContent = `${t("aiBadge")}: ${t("aiConnErr")}`;
  }
}

function populateMonths(aylar) {
  if (monthsLoaded) return;
  const opts = `<option value="">${t("allYear")}</option>` +
    aylar.map((a) => `<option value="${a}">${a}</option>`).join("");
  ["monthButce", "monthKategori", "monthAnomali"].forEach((id) => {
    $(id).innerHTML = opts;
  });
  monthsLoaded = true;
}

// --- Grafikler ---------------------------------------------------------------

function destroyChart(id) {
  if (charts[id]) { charts[id].destroy(); delete charts[id]; }
}

function buildTrendChart(canvasId, trend) {
  destroyChart(canvasId);
  charts[canvasId] = new Chart($(canvasId), {
    type: "line",
    data: {
      labels: trend.map((r) => r.ay),
      datasets: [
        { label: t("chartGelir"), data: trend.map((r) => r.gelir),
          borderColor: "#16a34a", backgroundColor: "#16a34a22", tension: .3, fill: true },
        { label: t("chartGider"), data: trend.map((r) => r.gider),
          borderColor: "#dc2626", backgroundColor: "#dc262622", tension: .3, fill: true },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom" },
        tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${fmtTL(c.parsed.y)}` } },
      },
      scales: {
        y: { beginAtZero: true, title: { display: true, text: t("axisAmount") },
             ticks: { callback: (v) => fmtAxis(v) } },
      },
    },
  });
}

function buildBudgetChart(canvasId, rows) {
  destroyChart(canvasId);
  charts[canvasId] = new Chart($(canvasId), {
    type: "bar",
    data: {
      labels: rows.map((r) => r.departman),
      datasets: [
        { label: t("chartButce"), data: rows.map((r) => r.butce), backgroundColor: "#c7d2fe" },
        { label: t("chartGerceklesen"), data: rows.map((r) => r.gerceklesen), backgroundColor: "#4f46e5" },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom" },
        tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${fmtTL(c.parsed.y)}` } },
      },
      scales: {
        y: { beginAtZero: true, title: { display: true, text: t("axisAmount") },
             ticks: { callback: (v) => fmtAxis(v) } },
      },
    },
  });
}

function buildCategoryChart(canvasId, rows) {
  destroyChart(canvasId);
  charts[canvasId] = new Chart($(canvasId), {
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

function renderAnomalyTable(tbodyId, anomalies) {
  const tbody = $(tbodyId);
  if (!anomalies.length) {
    tbody.innerHTML = `<tr><td colspan="5">${t("anomalyEmpty")}</td></tr>`;
    return;
  }
  tbody.innerHTML = anomalies.map((a) => `
    <tr class="${a.sapma_yuzde >= 100 ? "severe" : ""}">
      <td>${a.tarih}</td><td>${a.departman}</td><td>${a.kategori}</td>
      <td>${fmtTL(a.tutar)}</td>
      <td><span class="sapma-tag">+%${a.sapma_yuzde}</span></td>
    </tr>`).join("");
}

// --- Sayfa render -----------------------------------------------------------

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

async function renderGenel() {
  const dash = await getDashboard();
  renderKpis(dash.ozet);
  $("ovPeriodTrend").textContent = `${t("periodMonthly")} - ${dash.donem}`;
  $("ovPeriodBudget").textContent = `${dash.donem} ${t("yearTotal")}`;
  $("ovPeriodCategory").textContent = `${dash.donem} ${t("yearTotal")} - ${t("giderWord")}`;
  $("ovPeriodAnomaly").textContent = `${dash.donem} - ${t("allPeriod")}`;
  buildTrendChart("ovTrendChart", dash.aylik_trend);
  buildBudgetChart("ovBudgetChart", dash.butce_vs_gerceklesen);
  buildCategoryChart("ovCategoryChart", dash.kategori_dagilimi);
  renderAnomalyTable("ovAnomalyTable", (await getAnomalies()).anomalies);
  const ins = pickInsights(await getInsights());
  $("ovTrendIns").textContent = ins.trend;
  $("ovBudgetIns").textContent = ins.butce;
  $("ovCategoryIns").textContent = ins.kategori;
  $("ovAnomalyIns").textContent = ins.anomali;
}

async function renderTrend() {
  const dash = await getDashboard();
  $("periodTrend").textContent = `${t("periodMonthly")} - ${dash.donem}`;
  buildTrendChart("trendChart", dash.aylik_trend);
  $("insightTrend").textContent = pickInsights(await getInsights()).trend;
}

async function renderButce(ay) {
  const dash = await getDashboard(ay);
  buildBudgetChart("budgetChart", dash.butce_vs_gerceklesen);
  $("insightBudget").textContent = pickInsights(await getInsights(ay)).butce;
}

async function renderKategori(ay) {
  const dash = await getDashboard(ay);
  buildCategoryChart("categoryChart", dash.kategori_dagilimi);
  $("insightCategory").textContent = pickInsights(await getInsights(ay)).kategori;
}

async function renderAnomali(ay) {
  renderAnomalyTable("anomalyTable", (await getAnomalies(ay)).anomalies);
  $("insightAnomaly").textContent = pickInsights(await getInsights(ay)).anomali;
}

// --- Router ------------------------------------------------------------------

const PAGES = ["genel", "trend", "butce", "kategori", "anomali", "sor"];

function currentPage() {
  const h = location.hash.replace("#", "");
  return PAGES.includes(h) ? h : "genel";
}

function showPage(page) {
  document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"));
  $("page-" + page).classList.add("active");
  document.querySelectorAll(".nav-item").forEach((n) =>
    n.classList.toggle("active", n.dataset.page === page));
}

async function route() {
  const page = currentPage();
  showPage(page);
  try {
    if (page === "genel") await renderGenel();
    else if (page === "trend") await renderTrend();
    else if (page === "butce") await renderButce($("monthButce").value);
    else if (page === "kategori") await renderKategori($("monthKategori").value);
    else if (page === "anomali") await renderAnomali($("monthAnomali").value);
  } catch (err) {
    console.error("Sayfa yuklenemedi:", err);
  }
  if (window.innerWidth <= 900) document.body.classList.remove("drawer-open");
}

window.addEventListener("hashchange", route);

// --- Kontroller --------------------------------------------------------------

$("drawerToggle").addEventListener("click", () =>
  document.body.classList.toggle("drawer-open"));

$("themeToggle").addEventListener("click", () => {
  const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
  localStorage.setItem("theme", next);
  applyTheme(next);
  route();
});

$("langSelect").addEventListener("change", (e) => {
  localStorage.setItem("lang", e.target.value);
  applyLang(e.target.value);
  route();
});

$("monthButce").addEventListener("change", (e) => renderButce(e.target.value));
$("monthKategori").addEventListener("change", (e) => renderKategori(e.target.value));
$("monthAnomali").addEventListener("change", (e) => renderAnomali(e.target.value));

// --- Chat (yeniden kullanilabilir; iki ayri instance) -----------------------

function setupChat(windowId, formId, inputId, quickId) {
  const win = $(windowId);
  const form = $(formId);
  const input = $(inputId);
  const btn = form.querySelector("button");

  function addMessage(role, text) {
    const el = document.createElement("div");
    el.className = `message ${role}`;
    el.textContent = text;
    win.appendChild(el);
    win.scrollTop = win.scrollHeight;
    return el;
  }
  function addMeta(text) {
    const el = document.createElement("div");
    el.className = "msg-meta";
    el.textContent = text;
    win.appendChild(el);
    win.scrollTop = win.scrollHeight;
  }

  async function ask(prompt) {
    addMessage("user", prompt);
    const loading = addMessage("assistant loading", t("chatLoading"));
    btn.disabled = true;
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: prompt, lang: currentLang }),
      });
      const data = await res.json();
      loading.classList.remove("loading");
      if (!res.ok) {
        loading.textContent = data.error?.message || t("chatError");
        return;
      }
      loading.textContent = data.answer;
      const src = data.provider === "gemini" ? t("srcGemini") : t("srcLocal");
      addMeta(`${t("sourceLabel")}: ${src}${data.cached ? " (" + t("cached") + ")" : ""}`);
    } catch {
      loading.classList.remove("loading");
      loading.textContent = t("chatNoServer");
    } finally {
      btn.disabled = false;
    }
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const prompt = input.value.trim();
    if (!prompt) return;
    input.value = "";
    ask(prompt);
  });
  $(quickId).querySelectorAll("button").forEach((b) => {
    b.addEventListener("click", () => ask(b.dataset.prompt));
  });

  const welcome = addMessage("assistant", t("chatWelcome"));
  welcome.dataset.welcome = "1";
}

// --- Baslangic ---------------------------------------------------------------

async function init() {
  applyTheme(localStorage.getItem("theme") || "light");
  applyLang(currentLang);
  loadStatus();
  setupChat("ovChatWindow", "ovChatForm", "ovChatInput", "ovQuickPrompts");
  setupChat("chatWindow", "chatForm", "chatInput", "quickPrompts");
  try {
    const dash = await getDashboard();
    populateMonths(dash.aylar);
  } catch (err) {
    console.error("Veri yuklenemedi:", err);
  }
  if (window.innerWidth <= 900) document.body.classList.remove("drawer-open");
  route();
}

init();
