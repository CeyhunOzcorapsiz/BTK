# ERPilot AI

Hackathon fikri: ERP sistemi icinde calisan Gemini API destekli yapay zeka asistani.

Klasik ERP ekranlarinda kullanici rapor, muhasebe, stok ve cari hesap verilerine ulasmak icin cok sayida menu gezer. ERPilot AI, kullanicinin dogal dilde sordugu soruyu anlayip ilgili ERP verisini ozetler, riskleri gosterir ve aksiyon onerir.

## Calistirma

Gemini API ile calistirmak icin:

```powershell
$env:GEMINI_API_KEY="BURAYA_GEMINI_API_KEY"
.\run-server.ps1
```

Sonra tarayicida:

```text
http://127.0.0.1:5173
```

API key verilmezse demo yine acilir; asistan yerel demo cevap motoruna duser.

## Demo Akisi

1. Uygulamayi `http://127.0.0.1:5173` adresinde ac.
2. Dashboard uzerinden gelir, gider, net kar ve tahsilat riski metriklerini goster.
3. Sag panelde asistana sor: `Bu ay finansal durumum nasil?`
4. Ardindan sor: `Hangi musteriler riskli?`
5. `Bana yonetici raporu hazirla.` komutu ile kapanis demosunu yap.

## Ana Ozellikler

- ERP dashboard
- Gemini API destekli AI asistan
- Finans, muhasebe, stok, satis ve cari hesap modulleri
- Dogal dil ile soru-cevap
- Riskli tahsilat listesi
- Kritik stok uyarilari
- Yonetici ozeti

## Juriye Anlatim Cumlesi

ERPilot AI, ERP kullanicisinin rapor aramak icin menulerde kaybettigi zamani azaltir. Kullanici sadece ne istedigini yazar; asistan Gemini API ile ilgili ERP verisini yorumlar ve aksiyona donusturur.
