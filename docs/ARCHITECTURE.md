# ERPilot AI - Mimari ve SAP Entegrasyonu

## 1. Sistem Mimarisi

```mermaid
flowchart TB
    subgraph FE[Frontend - cok sayfali SPA]
        UI["Navbar + sol drawer<br/>6 sayfa - Chart.js<br/>dark/light + TR/EN"]
    end
    subgraph BE[FastAPI Backend]
        API["REST API<br/>/api/chat, /api/dashboard,<br/>/api/anomalies, /api/insights"]
        RL["Rate Limiting<br/>slowapi + semaphore + cache"]
        GC["Gemini Client<br/>function calling + guardrail"]
        QE["Query Engine<br/>allowlist dogrulama"]
        AN["Analytics + Anomaly<br/>pandas / IQR"]
        DS["DataSource katmani"]
    end
    subgraph EXT[Dis Servis]
        GM["Gemini API"]
    end
    subgraph DATA[Veri Kaynaklari]
        CSV[("CSV - MVP")]
        SAP[("SAP S/4HANA - future work")]
    end

    UI -->|HTTPS REST| API
    API --> RL --> GC
    API --> AN
    GC -->|tool call| GM
    GC --> QE
    QE --> DS
    AN --> DS
    DS --> CSV
    DS -.future.-> SAP
```

Katmanlar:

- **Frontend** — navbar + soldan acilan drawer ile gezilen 6 sayfali tek
  sayfa uygulamasi (Genel Bakis, Trend, Butce, Kategori, Anomali, Veriye Sor).
  Hash tabanli yonlendirme, Chart.js grafikler, dark/light tema ve TR/EN dil
  destegi. Backend ile yalnizca REST uzerinden konusur.
- **REST API** — kaynak odakli endpoint'ler; Pydantic ile girdi/cikti
  dogrulamasi. Dashboard/anomali/insight endpoint'leri opsiyonel `?ay=` alir.
- **Rate Limiting** — IP basina limit, Gemini'ye es zamanli istek sinirlamasi,
  TTL cache, tek httpx istemcisi.
- **Gemini Client** — function calling akisi ve dashboard AI yorumlari; konu
  disi sorulari mimari duzeyde reddeder.
- **Query Engine** — AI'in urettigi yapisal sorguyu allowlist'e karsi dogrular
  ve sabit pandas islemleriyle calistirir.
- **Analytics / Anomaly** — dashboard agregasyonlari (ay filtreli),
  deterministik yorum tabani ve IQR tabanli anomali tespiti.
- **DataSource** — veri kaynagini soyutlar; is mantigi CSV mi SAP mi bilmez.

## 2. "Veriye Sor" Akisi (function calling + guvenlik)

```mermaid
sequenceDiagram
    participant U as Kullanici
    participant F as Frontend
    participant B as FastAPI
    participant G as Gemini
    participant Q as Query Engine
    participant D as Veri (pandas)

    U->>F: Dogal dil sorusu
    F->>B: POST /api/chat (message, lang)
    B->>G: Soru + query_finance_data tanimi
    alt Konu disi soru (kodlama, sohbet)
        G-->>B: Fonksiyon CAGRILMAZ
        B-->>F: Sabit ret mesaji
    else Finans veri sorusu
        G-->>B: query_finance_data(yapisal sorgu)
        B->>Q: QuerySpec dogrula (allowlist)
        Q->>D: Sabit pandas islemleri
        D-->>Q: Gercek sayilar
        Q-->>B: Sonuc
        B->>G: Ozetle (spec + sonuc, ham kullanici metni YOK)
        G-->>B: Dogal dil cevap (secilen dilde)
        B-->>F: Cevap
    end
```

Onemli guvenlik noktalari:

- AI **ham SQL/kod uretmez**; yalnizca `QuerySpec` semasina uygun yapisal nesne uretir.
- `QuerySpec` Pydantic `Literal` tipleri = **allowlist**; kolon, operator ve metrik degerleri sabittir.
- Calistirma `eval`/`exec` veya string SQL olmadan, yalnizca sabit pandas fonksiyonlariyla yapilir.
- AI fonksiyon cagirmazsa serbest metni kullaniciya **gosterilmez**; panel yalnizca veriye dayali cevap veya ret uretir.
- **Ozetleme cagrisina kullanicinin ham metni verilmez**; yalnizca dogrulanmis `QuerySpec` ve sorgu sonucu gonderilir. Boylece mesru bir veri sorusuna bindirilmis konu disi istek (piggyback prompt injection) cevaba sizamaz.

## 3. SAP Entegrasyonu (Future Work)

MVP demo verisini CSV'den okur. Gercek senaryoda veri SAP S/4HANA'dan gelir.
Anahtar tasarim: **is mantigi degismez** - yalnizca `DataSource` implementasyonu degisir.

```mermaid
flowchart LR
    subgraph LOGIC[Is Mantigi - kaynak bagimsiz]
        QE[Query Engine]
        AN[Analytics / Anomaly]
    end
    DS{{"DataSource<br/>soyut arayuz"}}
    CSV["CsvDataSource<br/>(MVP)"]
    SAPDS["SapDataSource<br/>(future work)"]
    GW[SAP Gateway / OData]
    S4[("SAP S/4HANA<br/>FI ve CO modulleri")]

    QE --> DS
    AN --> DS
    DS --> CSV
    DS --> SAPDS
    SAPDS -->|"OData REST (httpx)"| GW
    GW --> S4
```

### Entegrasyon yontemi

`SapDataSource`, SAP S/4HANA'nin **OData REST servislerine** `httpx` ile baglanir:

1. SAP OData endpoint'ine kimlik dogrulamali GET istegi (OAuth2 / Basic).
2. Donen JSON `results` listesi pandas DataFrame'e cevrilir.
3. SAP alan adlari normalize semaya eslenir.
4. Sonuc `TRANSACTION_COLUMNS` / `BUDGET_COLUMNS` semasinda dondurulur.

### Ornek alan eslemesi

| SAP alani | ERPilot normalize alani |
|---|---|
| CompanyCode / CostCenter | departman |
| GLAccountGroup | kategori |
| FiscalPeriod | ay / ay_no |
| AmountInCompanyCodeCrcy | tutar |
| DebitCreditCode (S/H) | tur (gider / gelir) |
| PostingDate | tarih |

Alternatif: `pyrfc` ile dogrudan BAPI/RFC cagrisi (SAP NW RFC SDK gerektirir).

### Gecis

`.env` icinde `DATA_SOURCE=csv` -> `DATA_SOURCE=sap` degisikligi yeterlidir.
`query_engine`, `analytics`, `anomaly` ve frontend katmanlarinda **hicbir degisiklik gerekmez**.

## 4. Dil Destegi ve Insight Cache (Optimizasyon)

Arayuz TR/EN destekler. AI uretilen metinleri her dil degisiminde yeniden
uretmek maliyetli olacagi icin su yaklasim kullanilir:

- **Insight'lar** statik veriden uretilir; bir ayin yorumu hic degismez.
  Bu yuzden Gemini **tek cagrida hem TR hem EN** uretir ve sonuc **kalici
  cache**'lenir (TTL yok). Dil degisince yeni API cagrisi yapilmaz - cache'ten
  gelir. Maliyet: ay basina 1 cagri, omur boyu (~13 cagri toplam).
- **Chat** cevaplari tek seferliktir; istek ile gelen `lang` parametresine
  gore Gemini zaten yaptigi tek cagrida secilen dilde yanitlar - ek maliyet yok.
- **Fallback** (API key yoksa) deterministik metinler hem TR hem EN kodda
  hazirdir - sifir maliyet.

> Not: Tema (dark/light) ve dil secimi `localStorage`'da saklanir; SPA oldugu
> icin sayfa gecislerinde korunur, tam yenilemede de kalici kalir.
