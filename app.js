const erpData = {
  finance: {
    revenue: 1284000,
    expense: 842000,
    profit: 442000,
    biggestExpense: "Pazarlama giderleri",
    biggestExpenseChange: 24,
  },
  risks: [
    { customer: "Atlas Tekstil", amount: 78500, delay: 18 },
    { customer: "Mira Gida", amount: 64000, delay: 12 },
    { customer: "Kuzey Lojistik", amount: 44000, delay: 9 },
  ],
  stock: [
    { product: "Termal etiket", current: 42, min: 100 },
    { product: "Barkod okuyucu", current: 7, min: 15 },
  ],
  sales: {
    bestChannel: "B2B bayi kanali",
    growth: 18,
    topProduct: "Endustriyel yazici",
  },
};

const modules = {
  dashboard: {
    title: "Genel Bakis",
    text: "ERPilot AI, finans, muhasebe, stok, satis ve cari hesap verilerini tek bir is panelinde yorumlar.",
    metrics: [
      ["AI yanit suresi", "2 sn"],
      ["Analiz edilen modul", "5"],
      ["Kritik uyari", "5"],
      ["Rapor durumu", "Hazir"],
    ],
  },
  finance: {
    title: "Finans",
    text: "Gelir, gider, net kar ve nakit akisi tek ekranda okunur. Asistan, degisimin nedenini sade bir dille aciklar.",
    metrics: [
      ["Net kar", formatCurrency(erpData.finance.profit)],
      ["Kar marji", "%34,4"],
      ["En buyuk gider", "Pazarlama"],
      ["Gider artisi", "%24"],
    ],
  },
  accounting: {
    title: "Muhasebe",
    text: "Fatura, tahsilat, cari bakiye ve donem kapanisi gibi muhasebe akislarini ozetler.",
    metrics: [
      ["Bekleyen fatura", "14"],
      ["Vadesi gelen", "₺219.000"],
      ["Mutabakat", "%92"],
      ["Kapanis riski", "Orta"],
    ],
  },
  stock: {
    title: "Stok",
    text: "Kritik stok seviyelerini yakalar ve satin alma ekibine oncelikli aksiyon onerir.",
    metrics: [
      ["Kritik urun", "2"],
      ["Stok devir hizi", "4,8"],
      ["Siparis onerisi", "Var"],
      ["Depo doluluk", "%71"],
    ],
  },
  sales: {
    title: "Satis",
    text: "Kanal bazli satis performansini, en iyi urunleri ve hedefe ilerleme durumunu raporlar.",
    metrics: [
      ["Aylik buyume", "%18"],
      ["En iyi kanal", "B2B"],
      ["Hedef gerceklesme", "%87"],
      ["Top urun", "Yazici"],
    ],
  },
  customers: {
    title: "Cari Hesaplar",
    text: "Geciken tahsilatlari, riskli musterileri ve arama onceligini otomatik siralar.",
    metrics: [
      ["Riskli musteri", "3"],
      ["Geciken bakiye", "₺186.500"],
      ["Ortalama gecikme", "13 gun"],
      ["Oncelik", "Yuksek"],
    ],
  },
};

const alertList = document.querySelector("#alertList");
const riskTable = document.querySelector("#riskTable");
const moduleTitle = document.querySelector("#moduleTitle");
const moduleText = document.querySelector("#moduleText");
const moduleMetrics = document.querySelector("#moduleMetrics");
const chatWindow = document.querySelector("#chatWindow");
const chatForm = document.querySelector("#chatForm");
const chatInput = document.querySelector("#chatInput");

function formatCurrency(value) {
  return new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: "TRY",
    maximumFractionDigits: 0,
  }).format(value);
}

function renderAlerts() {
  const alerts = [
    {
      type: "risk",
      title: "Tahsilat riski yukseldi",
      text: `${erpData.risks.length} musteride toplam ${formatCurrency(186500)} gecikmis bakiye var.`,
    },
    {
      type: "stock",
      title: "Stok kritik seviyede",
      text: "Termal etiket ve barkod okuyucu icin satin alma onerisi olustu.",
    },
    {
      type: "info",
      title: "Satis performansi iyi",
      text: `${erpData.sales.bestChannel} gecen aya gore %${erpData.sales.growth} buyudu.`,
    },
  ];

  alertList.innerHTML = alerts
    .map(
      (alert) => `
        <div class="alert-item ${alert.type}">
          <div>
            <strong>${alert.title}</strong>
            <span>${alert.text}</span>
          </div>
        </div>
      `
    )
    .join("");
}

function renderRiskTable() {
  riskTable.innerHTML = erpData.risks
    .map(
      (risk) => `
        <tr>
          <td>${risk.customer}</td>
          <td>${formatCurrency(risk.amount)}</td>
          <td>${risk.delay} gun</td>
          <td><span class="tag">Oncelikli</span></td>
        </tr>
      `
    )
    .join("");
}

function renderModule(moduleKey) {
  const selected = modules[moduleKey];
  moduleTitle.textContent = selected.title;
  moduleText.textContent = selected.text;
  moduleMetrics.innerHTML = selected.metrics
    .map(
      ([label, value]) => `
        <div class="mini-metric">
          <span>${label}</span>
          <strong>${value}</strong>
        </div>
      `
    )
    .join("");
}

function addMessage(role, text) {
  const message = document.createElement("div");
  message.className = `message ${role}`;
  message.textContent = text;
  chatWindow.appendChild(message);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function fallbackAnswerPrompt(prompt) {
  const text = prompt.toLocaleLowerCase("tr-TR");

  if (text.includes("risk") || text.includes("musteri") || text.includes("cari")) {
    return `Riskli musteriler: Atlas Tekstil ${formatCurrency(78500)} ile 18 gun, Mira Gida ${formatCurrency(64000)} ile 12 gun, Kuzey Lojistik ${formatCurrency(44000)} ile 9 gun gecikmede. Ilk aksiyon Atlas Tekstil tahsilat gorusmesi olmali.`;
  }

  if (text.includes("stok") || text.includes("urun")) {
    return "Stokta 2 kritik urun var: Termal etiket 42 adet ile minimum 100 seviyesinin altinda, barkod okuyucu 7 adet ile minimum 15 seviyesinin altinda. Sistem satin alma talebi acilmasini oneriyor.";
  }

  if (text.includes("rapor") || text.includes("yonetici") || text.includes("ozet")) {
    return `Yonetici ozeti: Mayis geliri ${formatCurrency(erpData.finance.revenue)}, gider ${formatCurrency(erpData.finance.expense)}, net kar ${formatCurrency(erpData.finance.profit)}. Satislar %18 buyudu, ancak ${formatCurrency(186500)} tahsilat riski ve 2 kritik stok kalemi takip edilmeli.`;
  }

  if (text.includes("gider") || text.includes("finans") || text.includes("kar") || text.includes("durum")) {
    return `Finansal durum pozitif: net kar ${formatCurrency(erpData.finance.profit)} ve kar marji %34,4. En buyuk dikkat noktasi ${erpData.finance.biggestExpense}; gecen aya gore %${erpData.finance.biggestExpenseChange} artmis.`;
  }

  if (text.includes("satis")) {
    return `Satis tarafinda en guclu kanal ${erpData.sales.bestChannel}. Aylik buyume %${erpData.sales.growth}; en cok katkı veren urun ${erpData.sales.topProduct}.`;
  }

  return "Bu soru icin finans, muhasebe, stok, satis veya cari hesap verilerinden ilgili ozet cikarabilirim. Ornek: 'Bu ay finansal durumum nasil?'";
}

async function answerPrompt(prompt) {
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: prompt,
        erpData,
      }),
    });

    if (!response.ok) {
      throw new Error("Gemini API yaniti basarisiz");
    }

    const data = await response.json();
    return data.answer || fallbackAnswerPrompt(prompt);
  } catch (error) {
    return fallbackAnswerPrompt(prompt);
  }
}

async function askAssistant(prompt) {
  addMessage("user", prompt);
  addMessage("assistant", "ERP verilerini okuyorum...");
  const loadingMessage = chatWindow.lastElementChild;
  const answer = await answerPrompt(prompt);
  loadingMessage.textContent = answer;
}

document.querySelectorAll(".module-item").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".module-item").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    renderModule(button.dataset.module);
  });
});

document.querySelectorAll(".quick-prompts button").forEach((button) => {
  button.addEventListener("click", () => {
    const prompt = button.dataset.prompt;
    askAssistant(prompt);
  });
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const prompt = chatInput.value.trim();
  if (!prompt) return;
  chatInput.value = "";
  await askAssistant(prompt);
});

document.querySelector("#monthlySummaryBtn").addEventListener("click", () => {
  const prompt = "Bana yonetici raporu hazirla.";
  askAssistant(prompt);
});

document.querySelector("#riskReportBtn").addEventListener("click", () => {
  const prompt = "Hangi musteriler riskli?";
  askAssistant(prompt);
});

renderAlerts();
renderRiskTable();
renderModule("dashboard");
