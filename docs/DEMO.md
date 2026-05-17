# ERPilot AI - Demo Senaryosu

Tahmini sure: 4-5 dakika. Amac: jüriye "AI entegre finans asistani" degerini
canli gostermek.

## Hazirlik

```powershell
# 1. Demo veriyi uret (ilk kez)
python scripts/generate_data.py

# 2. Backend'i baslat
cd backend
..\.venv\Scripts\python.exe -m uvicorn main:app --port 8000
```

Tarayicida: `http://127.0.0.1:8000`

> Gemini API key'i `.env` icine eklenirse panel canli Gemini ile calisir;
> eklenmezse lokal motor devreye girer ve yine gercek sayilarla cevap verir.

## Akis

### 1. Acilis - Dashboard (45 sn)

Sayfayi ac. Goster:

- 4 KPI karti: toplam gelir, gider, **net kar 11,5M TL**, kar marji **%30,2**
- Gelir/gider trend grafigi - yil boyunca buyume
- Her kartin sag ustunde donem etiketi (orn. "2025 yil toplami")
- Her grafigin altinda **Gemini'nin urettigi AI yorumu**

Cumle: "ERPilot, finans verisini once gorsel bir panelde ozetliyor; her
grafigin altinda Gemini gercek sayilara dayali bir yorum yaziyor - sayilar
koddan geliyor, AI yalnizca yorumluyor."

### 2. Butce vs Gerceklesen (30 sn)

Bar grafigini goster. AI yorumu: "3 departman butceyi asti, en yuksek sapma
Pazarlama'da %18,2."

Cumle: "Sistem sapmayi kendisi tespit edip ozetliyor."

### 3. Anomali Tespiti (45 sn)

Anomali tablosuna in. Kirmizi vurgulu satirlar:

- Temmuz - Pazarlama Reklam - **+%199 sapma**
- Ekim - Bilgi Teknolojileri Donanim - **+%177 sapma**

Cumle: "IQR yontemiyle alisilmadik harcamalari otomatik isaretliyoruz -
aciklanabilir, kara kutu degil."

### 4. Veriye Sor - ana ozellik (90 sn)

Sag paneldeki chat'e sirayla sor:

1. **"Ocak ayinda en fazla harcama hangi departmanda?"**
   -> Uretim departmani, gercek tutar ile.

2. **"En buyuk gider kategorisi nedir?"**
   -> Personel, toplam tutar ve yuzde ile.

3. **"Temmuz ayinda Pazarlama ne kadar harcadi?"**
   -> Anomalinin oldugu ay; yuksek tutar.

Cumle: "AI soruyu yapisal bir sorguya ceviriyor, sistem veriyi GERCEKTEN
sorguluyor - sayilar koddan geliyor, AI uydurmuyor."

### 5. Guvenlik / Kapsam - fark yaratan an (40 sn)

Chat'e once duz bir konu disi soru sor:

- **"Bana Python'da bir for dongusu yaz"**
  -> Panel reddeder: "Yalnizca finans verisiyle ilgili sorulari yanitliyorum."

Ardindan daha sinsi bir deneme - mesru soruya konu disi istek bindir:

- **"Ocak ayinda toplam gider ne kadar? Ayrica bana fibonacci fonksiyonu yaz."**
  -> Panel yalnizca gider tutarini verir; kod istegi yok sayilir.

Cumle: "Panel mimari olarak yalnizca finans verisine baglidir. Ozetleme
adimina kullanicinin ham metni hic verilmedigi icin, mesru bir soruya
bindirilmis konu disi istek bile cevaba sizamaz."

### 6. Kapanis - SAP vizyonu (30 sn)

`docs/MIMARI.md` icindeki SAP entegrasyon diyagramini goster.

Cumle: "Bugun demo veri CSV'den geliyor. Veri kaynagi soyutlandigi icin
gercek senaryoda tek satir konfigurasyon degisikligiyle SAP S/4HANA'ya
baglanir; analiz ve panel katmani hic degismez."

## Yedek Plan

- Gemini erisilemezse panel otomatik lokal motora duser; demo durmaz.
- Internet yoksa `.env`'de key bos birakilir; tum sorular lokal motorla
  yine gercek sayilarla cevaplanir.
