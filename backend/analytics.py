"""
Dashboard analiz modulu.

Tum fonksiyonlar normalize edilmis transactions / budgets DataFrame'leri
uzerinde calisir; veri kaynagini (CSV / SAP) bilmez.

Cogu fonksiyon istege bagli bir 'ay' parametresi alir: verilirse hesap
yalnizca o aya gore yapilir, verilmezse tum donem (yil) kullanilir.
"""

from __future__ import annotations

import pandas as pd


def available_months(transactions: pd.DataFrame) -> list[str]:
    """Veri setindeki aylari kronolojik sirayla dondurur."""
    aylar = transactions.sort_values("ay_no")["ay"].drop_duplicates()
    return [str(a) for a in aylar]


def _filter_month(df: pd.DataFrame, ay: str | None) -> pd.DataFrame:
    """ay verilmisse DataFrame'i o aya gore filtreler."""
    if ay:
        return df[df["ay"] == ay]
    return df


def summary(transactions: pd.DataFrame, ay: str | None = None) -> dict:
    """Genel KPI'lar: toplam gelir, gider, net kar, kar marji."""
    df = _filter_month(transactions, ay)
    gelir = float(df.loc[df["tur"] == "gelir", "tutar"].sum())
    gider = float(df.loc[df["tur"] == "gider", "tutar"].sum())
    net = gelir - gider
    margin = (net / gelir * 100.0) if gelir else 0.0
    return {
        "gelir": round(gelir, 2),
        "gider": round(gider, 2),
        "net_kar": round(net, 2),
        "kar_marji": round(margin, 1),
    }


def monthly_trend(transactions: pd.DataFrame) -> list[dict]:
    """Aylik gelir / gider / net seyri (ay sirasiyla). Her zaman tum yil."""
    rows: list[dict] = []
    for ay_no, grup in transactions.groupby("ay_no"):
        gelir = float(grup.loc[grup["tur"] == "gelir", "tutar"].sum())
        gider = float(grup.loc[grup["tur"] == "gider", "tutar"].sum())
        rows.append({
            "ay_no": int(ay_no),
            "ay": str(grup["ay"].iloc[0]),
            "gelir": round(gelir, 2),
            "gider": round(gider, 2),
            "net": round(gelir - gider, 2),
        })
    return sorted(rows, key=lambda r: r["ay_no"])


def budget_vs_actual(
    transactions: pd.DataFrame, budgets: pd.DataFrame, ay: str | None = None
) -> list[dict]:
    """Departman bazli butce ile gerceklesen gideri karsilastirir."""
    tx = _filter_month(transactions, ay)
    bd = _filter_month(budgets, ay)
    actual = tx[tx["tur"] == "gider"].groupby("departman")["tutar"].sum()
    planned = bd.groupby("departman")["butce"].sum()
    departments = sorted(set(actual.index) | set(planned.index))

    rows: list[dict] = []
    for dept in departments:
        b = float(planned.get(dept, 0.0))
        a = float(actual.get(dept, 0.0))
        sapma = ((a - b) / b * 100.0) if b else 0.0
        rows.append({
            "departman": dept,
            "butce": round(b, 2),
            "gerceklesen": round(a, 2),
            "sapma_yuzde": round(sapma, 1),
        })
    return rows


def category_distribution(
    transactions: pd.DataFrame, ay: str | None = None
) -> list[dict]:
    """Gider kategorilerinin dagilimi (buyukten kucuge)."""
    df = _filter_month(transactions, ay)
    grouped = (
        df[df["tur"] == "gider"]
        .groupby("kategori")["tutar"].sum()
        .sort_values(ascending=False)
    )
    total = float(grouped.sum()) or 1.0
    return [
        {
            "kategori": str(kat),
            "tutar": round(float(val), 2),
            "yuzde": round(float(val) / total * 100.0, 1),
        }
        for kat, val in grouped.items()
    ]


def _donem(transactions: pd.DataFrame) -> str:
    """Veri setinin kapsadigi donemi metne cevirir (orn. '2025')."""
    years = sorted(int(y) for y in transactions["yil"].unique())
    if not years:
        return "-"
    if len(years) == 1:
        return str(years[0])
    return f"{years[0]}-{years[-1]}"


def build_dashboard(
    transactions: pd.DataFrame, budgets: pd.DataFrame, ay: str | None = None
) -> dict:
    """Tum dashboard verisini tek nesnede toplar. ay verilirse o aya gore."""
    return {
        "donem": _donem(transactions),
        "secili_ay": ay,
        "aylar": available_months(transactions),
        "ozet": summary(transactions, ay),
        "aylik_trend": monthly_trend(transactions),
        "butce_vs_gerceklesen": budget_vs_actual(transactions, budgets, ay),
        "kategori_dagilimi": category_distribution(transactions, ay),
    }


# --- Otomatik finansal yorum (deterministik - gercek sayilardan) -------------
#
# Insight fonksiyonlari iki dillidir (tr / en). Sayilar koddan gelir; yalnizca
# cevreleyen metin dile gore degisir. Bu deterministik metin, Gemini'nin AI
# yorumu uretemedigi durumda fallback olarak kullanilir.

_MONTHS_EN = {
    "Ocak": "January", "Subat": "February", "Mart": "March", "Nisan": "April",
    "Mayis": "May", "Haziran": "June", "Temmuz": "July", "Agustos": "August",
    "Eylul": "September", "Ekim": "October", "Kasim": "November", "Aralik": "December",
}


def _fmt(value: float, lang: str = "tr") -> str:
    s = f"{value:,.0f}"  # 1,234,567
    if lang == "tr":
        s = s.replace(",", ".")
    return f"{s} TL"


def _month(ay: str, lang: str) -> str:
    return _MONTHS_EN.get(ay, ay) if lang == "en" else ay


def trend_insight(trend: list[dict], lang: str = "tr") -> str:
    if len(trend) < 2:
        return ("Not enough monthly data for a trend comment."
                if lang == "en" else "Trend yorumu icin yeterli ay verisi yok.")
    son, onceki = trend[-1], trend[-2]
    if onceki["gider"] == 0:
        return ("Change could not be computed (previous month was zero)."
                if lang == "en" else "Onceki ay gideri sifir; degisim hesaplanamadi.")
    degisim = (son["gider"] - onceki["gider"]) / onceki["gider"] * 100.0
    ay = _month(son["ay"], lang)
    if lang == "en":
        yon = "increased by" if degisim >= 0 else "decreased by"
        return (f"In {ay}, expenses {yon} {abs(degisim):.1f}% versus the previous "
                f"month ({_fmt(son['gider'], lang)}). Net result "
                f"{_fmt(son['net'], lang)}.")
    yon = "artti" if degisim >= 0 else "azaldi"
    return (f"{ay} ayinda giderler onceki aya gore %{abs(degisim):.1f} {yon} "
            f"({_fmt(son['gider'], lang)}). Net sonuc {_fmt(son['net'], lang)}.")


def budget_insight(rows: list[dict], ay: str | None = None, lang: str = "tr") -> str:
    asanlar = [r for r in rows if r["sapma_yuzde"] > 0]
    if lang == "en":
        kapsam = f"In {_month(ay, lang)}" if ay else "Across the year"
        if not asanlar:
            return f"{kapsam}, all departments stayed within budget."
        en = max(asanlar, key=lambda r: r["sapma_yuzde"])
        return (f"{kapsam}, {len(asanlar)} departments exceeded budget. Largest "
                f"deviation in {en['departman']}: {en['sapma_yuzde']:.1f}% "
                f"({_fmt(en['gerceklesen'], lang)}).")
    kapsam = f"{ay} ayinda" if ay else "Yil genelinde"
    if not asanlar:
        return f"{kapsam} tum departmanlar butce sinirlari icinde kaldi."
    en = max(asanlar, key=lambda r: r["sapma_yuzde"])
    return (f"{kapsam} {len(asanlar)} departman butceyi asti. En yuksek sapma "
            f"{en['departman']}: %{en['sapma_yuzde']:.1f} "
            f"({_fmt(en['gerceklesen'], lang)}).")


def category_insight(rows: list[dict], ay: str | None = None, lang: str = "tr") -> str:
    if lang == "en":
        kapsam = f"In {_month(ay, lang)}" if ay else "Across the year"
        if not rows:
            return f"{kapsam}, no category data found."
        en = rows[0]
        return (f"{kapsam}, the largest expense item is {en['kategori']}: "
                f"{_fmt(en['tutar'], lang)} ({en['yuzde']:.1f}% of expenses).")
    kapsam = f"{ay} ayinda" if ay else "Yil genelinde"
    if not rows:
        return f"{kapsam} kategori verisi bulunamadi."
    en = rows[0]
    return (f"{kapsam} en buyuk gider kalemi {en['kategori']}: "
            f"{_fmt(en['tutar'], lang)} (giderlerin %{en['yuzde']:.1f}'i).")


def _anomaly_insight(ay: str | None, count: int, lang: str) -> str:
    if lang == "en":
        kapsam = f"In {_month(ay, lang)}" if ay else "Across the year"
        return (f"{kapsam}, {count} unusual expenses were detected." if count
                else f"{kapsam}, no unusual expenses were detected.")
    kapsam = f"{ay} ayinda" if ay else "Yil genelinde"
    return (f"{kapsam} {count} adet alisilmadik harcama tespit edildi." if count
            else f"{kapsam} anormal harcama tespit edilmedi.")


def build_insights(dashboard: dict, anomaly_count: int, lang: str = "tr") -> dict:
    """Her grafik icin otomatik yorum metni uretir (tek dil)."""
    ay = dashboard.get("secili_ay")
    return {
        "trend": trend_insight(dashboard["aylik_trend"], lang),
        "butce": budget_insight(dashboard["butce_vs_gerceklesen"], ay, lang),
        "kategori": category_insight(dashboard["kategori_dagilimi"], ay, lang),
        "anomali": _anomaly_insight(ay, anomaly_count, lang),
    }
