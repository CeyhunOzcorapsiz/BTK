# ERPilot AI

AI entegre kurumsal finans asistani. Kullanici dogal dilde soru sorar; sistem
finans verisini gercekten sorgular, dashboard'da gorsellestirir, otomatik
yorum uretir ve anomalileri tespit eder.

BTK Akademi Hackathon 2026 - Finans kategorisi.

## Ozellikler

- **Veriye sor** - dogal dil sorusu Gemini function calling ile yapisal
  sorguya cevrilir; veri pandas ile GERCEKTEN sorgulanir (sayi uydurma yok).
- **Dashboard** - gelir/gider trendi, butce vs gerceklesen, kategori dagilimi;
  her kartta kapsadigi donem etiketlenir.
- **AI yorumu** - her grafigin altinda Gemini'nin urettigi finansal yorum;
  sayilar koddan gelir, AI yalnizca yorumlar. Gemini yoksa deterministik
  ozete duser.
- **Anomali tespiti** - IQR yontemiyle alisilmadik harcamalar isaretlenir.
- **Kati kapsam** - panel yalnizca finans verisi sorularini yanitlar; konu
  disi / suistimal sorulari mimari duzeyde reddedilir.

## Teknoloji

| Katman | Teknoloji |
|---|---|
| Backend | FastAPI + Python |
| Veri analizi | pandas |
| AI | Gemini API (function calling) |
| Frontend | Vanilla HTML/JS + Chart.js |
| Veri | CSV (MVP) - SAP S/4HANA hedefli (future work) |

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

## REST API

| Method | Endpoint | Aciklama |
|---|---|---|
| GET | `/api/health` | Saglik kontrolu |
| POST | `/api/chat` | Veriye dogal dil sorusu |
| GET | `/api/dashboard` | Trend, butce, kategori verisi |
| GET | `/api/anomalies` | Anomali listesi |
| GET | `/api/insights` | Grafik basina otomatik yorum |
| GET | `/api/transactions` | Ham hareket verisi (filtreli) |

OpenAPI dokumantasyonu: `http://127.0.0.1:8000/docs`

## Proje Yapisi

```
backend/
  main.py           FastAPI uygulamasi ve endpoint'ler
  config.py         .env tabanli ayarlar
  datasource.py     DataSource soyutlamasi (CSV + SAP iskeleti)
  query_engine.py   allowlist dogrulamali guvenli sorgu motoru
  analytics.py      dashboard agregasyonlari + deterministik yorumlar
  anomaly.py        IQR tabanli anomali tespiti
  gemini_client.py  Gemini function calling + AI yorumu + rate limiting + fallback
  data/             demo CSV veri seti
scripts/
  generate_data.py  demo veri ureticisi
docs/
  MIMARI.md         mimari ve SAP entegrasyon diyagramlari
  DEMO.md           demo senaryosu
index.html, app.js, styles.css   frontend
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
- Detayli mimari icin `docs/MIMARI.md`.
