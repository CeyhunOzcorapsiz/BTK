# ERPilot AI - Demo Senaryosu

Tahmini sure: 5-6 dakika. Amac: juriye "AI entegre finans asistani" degerini
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

### 1. Genel Bakis (60 sn)

Acilista **Genel Bakis** sayfasi gelir. Goster:

- 4 KPI karti: toplam gelir, gider, **net kar ~11,5M TL**, kar marji **%30,2**
- Gelir/gider trendi, butce vs gerceklesen, kategori dagilimi grafikleri
- Her grafigin altinda **Gemini'nin urettigi AI yorumu**
- Sagda **Veriye Sor** chat paneli

Cumle: "ERPilot tum finans tablosunu tek ekranda ozetliyor; her grafigin
altinda gercek sayilara dayali bir AI yorumu var."

### 2. Tema ve Dil (30 sn) - fark yaratan dokunus

- Sag ustteki toggle ile **dark mode**'a gec - tema sayfa gecislerinde korunur.
- Dil dropdown'undan **EN**'e gec - arayuz aninda Ingilizce olur.

Cumle: "Tema ve dil tercihi saklaniyor. AI yorumlari tek cagrida iki dilde
uretilip kalici cache'lendigi icin dil degisimi ek maliyet getirmiyor."

### 3. Detay sayfalari + ay filtresi (60 sn)

Sol menuden **Butce vs Gerceklesen** sayfasina gec. Ay dropdown'undan
**Ocak**'i sec - grafik ve AI yorumu o aya gore guncellenir.

Cumle: "Her dashboard ayri bir detay sayfasi; ay bazli veri filtrelenebiliyor."

### 4. Anomali Tespiti (45 sn)

**Anomaliler** sayfasina gec. Kirmizi vurgulu satirlar:

- Temmuz - Pazarlama Reklam - **+%199 sapma**
- Ekim - Bilgi Teknolojileri Donanim - **+%177 sapma**

Cumle: "IQR yontemiyle alisilmadik harcamalari otomatik isaretliyoruz -
aciklanabilir, kara kutu degil."

### 5. Veriye Sor - ana ozellik (90 sn)

Genel Bakis'taki (veya ayri sayfadaki) chat'e sirayla sor:

1. **"Ocak ayinda en fazla harcama hangi departmanda?"** -> Uretim, gercek tutar.
2. **"En buyuk gider kategorisi nedir?"** -> Personel, tutar ve yuzde ile.
3. **"Temmuz ayinda Pazarlama ne kadar harcadi?"** -> anomali ayinin tutari.

Cumle: "AI soruyu yapisal bir sorguya ceviriyor, sistem veriyi GERCEKTEN
sorguluyor - sayilar koddan geliyor, AI uydurmuyor."

### 6. Guvenlik / Kapsam (40 sn)

Chat'e once duz konu disi soru:

- **"Bana Python'da bir for dongusu yaz"** -> panel reddeder.

Ardindan sinsi deneme - mesru soruya konu disi istek bindir:

- **"Ocak gideri ne kadar? Ayrica bana fibonacci fonksiyonu yaz."**
  -> panel yalnizca gider tutarini verir; kod istegi yok sayilir.

Cumle: "Panel mimari olarak yalnizca finans verisine bagli; ozetleme adimina
ham kullanici metni hic verilmedigi icin bindirilmis istek bile sizamaz."

### 7. Kapanis - SAP vizyonu (30 sn)

`docs/ARCHITECTURE.md` icindeki SAP entegrasyon diyagramini goster.

Cumle: "Bugun demo veri CSV'den geliyor. Veri kaynagi soyutlandigi icin gercek
senaryoda tek satir konfigurasyon degisikligiyle SAP S/4HANA'ya baglanir;
analiz ve panel katmani hic degismez."

## Yedek Plan

- Gemini erisilemezse panel otomatik lokal motora duser; demo durmaz.
- Internet yoksa `.env`'de key bos birakilir; tum sorular ve yorumlar lokal
  motorla yine gercek sayilarla (iki dilde) cevaplanir.
