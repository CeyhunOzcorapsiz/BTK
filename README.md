# ERPilot AI

AI entegre kurumsal finans asistani. Kullanici dogal dilde soru sorar; sistem
finans verisini gercekten sorgular, dashboard'da gorsellestirir, otomatik
yorum uretir ve anomalileri tespit eder.

BTK Akademi Hackathon 2026 - Finans kategorisi.

## Ozellikler

- **Veriye sor** - dogal dil sorusu Gemini function calling ile yapisal
  sorguya cevrilir; veri pandas ile GERCEKTEN sorgulanir (sayi uydurma yok).
- **Cok sayfali dashboard** - navbar + soldan acilan menu ile 6 sayfa:
  Genel Bakis, Trend, Butce vs Gerceklesen, Kategori, Anomaliler, Veriye Sor.
- **Ay filtresi** - Butce/Kategori/Anomali sayfalarinda dropdown ile veri
  aya gore filtrelenir.
- **AI yorumu** - her grafigin altinda Gemini'nin urettigi finansal yorum;
  sayilar koddan gelir. Gemini yoksa deterministik ozete duser.
- **Anomali tespiti** - IQR yontemiyle alisilmadik harcamalar isaretlenir.
- **Dark / light tema** ve **TR / EN dil** secimi - tercih saklanir.
- **Kati kapsam** - panel yalnizca finans verisi sorularini yanitlar; konu
  disi / suistimal sorulari mimari duzeyde reddedilir.

## Teknoloji

| Katman | Teknoloji |
|---|---|
| Backend | FastAPI + Python |
| Veri analizi | pandas |
| AI | Gemini API (function calling) |
| Frontend | Vanilla HTML/JS + Chart.js (cok sayfali SPA) |
| Veri | CSV (MVP) - SAP S/4HANA hedefli (future work) |
| Calistirma | yerel uvicorn veya Docker |

## Kurulum

```powershell
# Sanal ortam ve bagimliliklar
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Demo veri setini uret
python scripts/generate_data.py

# (Istege bagli) Gemini API key'i
copy .env.example .env
# .env icine GEMINI_API_KEY yazin - bos birakilirsa lokal motor calisir

# Backend'i baslat
cd backend
..\.venv\Scripts\python.exe -m uvicorn main:app --port 8000
```

Tarayicida: `http://127.0.0.1:8000`

## Docker ile calistirma

```powershell
docker compose up --build
```

Tarayicida: `http://localhost:8000`

Tek container FastAPI hem API'yi hem frontend'i serve eder. `GEMINI_API_KEY`
ayni dizindeki `.env` dosyasindan okunur; verilmezse lokal fallback calisir.

## REST API

| Method | Endpoint | Aciklama |
|---|---|---|
| GET | `/api/health` | Saglik kontrolu |
| POST | `/api/chat` | Veriye dogal dil sorusu (`message`, `lang`) |
| GET | `/api/dashboard` | Trend, butce, kategori verisi (opsiyonel `?ay=`) |
| GET | `/api/anomalies` | Anomali listesi (opsiyonel `?ay=`) |
| GET | `/api/insights` | Grafik basina AI yorumu, TR+EN (opsiyonel `?ay=`) |
| GET | `/api/transactions` | Ham hareket verisi (filtreli) |

OpenAPI dokumantasyonu: `http://127.0.0.1:8000/docs`

## Sayfalar

Sol menuden (drawer) erisilen sayfalar:

- **Genel Bakis** - KPI'lar + tum grafikler + anomali tablosu + sagda chat
- **Gelir / Gider Trendi** - aylik seyir
- **Butce vs Gerceklesen** - departman bazli, ay filtreli
- **Kategori Dagilimi** - gider kategorileri, ay filtreli
- **Anomaliler** - alisilmadik harcamalar, ay filtreli
- **Veriye Sor** - tam ekran sohbet

## Proje Yapisi

```
backend/
  main.py           FastAPI uygulamasi ve endpoint'ler
  config.py         .env tabanli ayarlar
  datasource.py     DataSource soyutlamasi (CSV + SAP iskeleti)
  query_engine.py   allowlist dogrulamali guvenli sorgu motoru
  analytics.py      dashboard agregasyonlari + iki dilli yorumlar
  anomaly.py        IQR tabanli anomali tespiti
  gemini_client.py  Gemini function calling + AI yorumu + rate limiting + fallback
  data/             demo CSV veri seti
scripts/
  generate_data.py  demo veri ureticisi
docs/
  ARCHITECTURE.md   mimari ve SAP entegrasyon diyagramlari
  DEMO.md           demo senaryosu
index.html, app.js, styles.css   frontend (cok sayfali: navbar + drawer)
Dockerfile, docker-compose.yml   container ile calistirma
```

## Guvenlik

- AI ham SQL/kod uretmez; yalnizca `QuerySpec` semasina uygun yapisal sorgu
  uretir, backend bunu allowlist'e (`Literal` tipleri) karsi dogrular.
- Sorgu calistirma `eval`/`exec` veya string SQL olmadan, yalnizca sabit
  pandas fonksiyonlariyla yapilir.
- AI fonksiyon cagirmazsa serbest metni kullaniciya gosterilmez; panel
  yalnizca veriye dayali cevap veya sabit ret uretir.
- Ozetleme cagrisina kullanicinin ham metni verilmez; yalnizca dogrulanmis
  sorgu ve sonuc gonderilir - bir veri sorusuna bindirilmis konu disi istek
  (prompt injection) cevaba sizamaz.
- Gemini API key yalnizca backend'de tutulur (`.env`, `.gitignore`'da).
- Rate limiting: IP basina limit + es zamanlilik sinirlamasi + TTL cache.
- Frontend chat cevabini `textContent` ile basar (XSS'e kapali).
- Detayli mimari icin `docs/ARCHITECTURE.md`.
