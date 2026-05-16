# ERPilot AI Sunum Taslagi

## Problem

ERP sistemleri isletmeler icin guclu ama karmasik yapilardir. Kullanici bir rapora, geciken tahsilata veya stok uyarisina ulasmak icin cok sayida menu, filtre ve tablo ile ugrasir.

## Cozum

ERPilot AI, ERP icine gomulu bir yapay zeka asistani olarak calisir. Kullanici dogal dille soru sorar, sistem ilgili ERP modulunu yorumlar ve kisa, anlasilir bir cevap verir.

## Ornek Sorular

- Bu ay finansal durumum nasil?
- Hangi musteriler riskli?
- Stokta kritik seviyeye dusen urun var mi?
- Bana yonetici raporu hazirla.
- En buyuk gider kalemim ne?

## Deger Onerisi

- Kullanici menuler arasinda kaybolmaz.
- Raporlama suresi azalir.
- Riskler daha erken gorulur.
- Yonetici kararlarini destekleyen ozetler uretilir.
- ERP verisi aksiyona donusur.

## MVP Kapsami

- Dashboard
- AI asistan paneli
- Finansal ozet
- Riskli cari hesaplar
- Kritik stok uyarilari
- Demo veri seti ile akilli cevaplar

## Teknik Mimari

Frontend:
HTML, CSS, JavaScript

Backend:
Node.js HTTP server

AI Katmani:
Gemini API ile dogal dil yorumlama. API key backend tarafinda tutulur; frontend yalnizca `/api/chat` endpointine soru gonderir.

Veri Katmani:
Demo ERP veri objeleri

ERP Entegrasyonu:
Gercek senaryoda SQL, REST API veya ERP servis katmani uzerinden finans, muhasebe, stok ve cari hesap verileri okunur.

## Demo Kapanis Cumlesi

ERPilot AI, ERP ekranlarina yeni bir rapor daha eklemek yerine ERP ile konusabilen bir is asistani sunar.
