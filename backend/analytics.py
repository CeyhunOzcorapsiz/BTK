"""
Dashboard analiz modulu.

Tum fonksiyonlar normalize edilmis transactions / budgets DataFrame'leri
uzerinde calisir; veri kaynagini (CSV / SAP) bilmez.
"""

from __future__ import annotations

import pandas as pd


def summary(transactions: pd.DataFrame) -> dict:
    """Genel KPI'lar: toplam gelir, gider, net kar, kar marji."""
    gelir = float(transactions.loc[transactions["tur"] == "gelir", "tutar"].sum())
    gider = float(transactions.loc[transactions["tur"] == "gider", "tutar"].sum())
    net = gelir - gider
    margin = (net / gelir * 100.0) if gelir else 0.0
    return {
        "gelir": round(gelir, 2),
        "gider": round(gider, 2),
        "net_kar": round(net, 2),
        "kar_marji": round(margin, 1),
    }


def monthly_trend(transactions: pd.DataFrame) -> list[dict]:
    """Aylik gelir / gider / net seyri (ay sirasiyla)."""
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


def budget_vs_actual(transactions: pd.DataFrame, budgets: pd.DataFrame) -> list[dict]:
    """Departman bazli butce ile gerceklesen gideri karsilastirir."""
    actual = (
        transactions[transactions["tur"] == "gider"]
        .groupby("departman")["tutar"].sum()
    )
    planned = budgets.groupby("departman")["butce"].sum()
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


def category_distribution(transactions: pd.DataFrame) -> list[dict]:
    """Gider kategorilerinin dagilimi (buyukten kucuge)."""
    grouped = (
        transactions[transactions["tur"] == "gider"]
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


def build_dashboard(transactions: pd.DataFrame, budgets: pd.DataFrame) -> dict:
    """Tum dashboard verisini tek nesnede toplar."""
    return {
        "donem": _donem(transactions),
        "ozet": summary(transactions),
        "aylik_trend": monthly_trend(transactions),
        "butce_vs_gerceklesen": budget_vs_actual(transactions, budgets),
        "kategori_dagilimi": category_distribution(transactions),
    }


# --- Otomatik finansal yorum (deterministik - gercek sayilardan) -------------

def _fmt(value: float) -> str:
    return f"{value:,.0f} TL".replace(",", ".")


def trend_insight(trend: list[dict]) -> str:
    if len(trend) < 2:
        return "Trend yorumu icin yeterli ay verisi yok."
    son, onceki = trend[-1], trend[-2]
    if onceki["gider"] == 0:
        return "Onceki ay gideri sifir oldugu icin degisim hesaplanamadi."
    degisim = (son["gider"] - onceki["gider"]) / onceki["gider"] * 100.0
    yon = "artti" if degisim >= 0 else "azaldi"
    return (
        f"{son['ay']} ayinda giderler onceki aya gore %{abs(degisim):.1f} {yon} "
        f"({_fmt(son['gider'])}). Net sonuc {_fmt(son['net'])}."
    )


def budget_insight(rows: list[dict]) -> str:
    asanlar = [r for r in rows if r["sapma_yuzde"] > 0]
    if not asanlar:
        return "Tum departmanlar butce sinirlari icinde kaldi."
    en = max(asanlar, key=lambda r: r["sapma_yuzde"])
    return (
        f"{len(asanlar)} departman butceyi asti. En yuksek sapma {en['departman']} "
        f"departmaninda: %{en['sapma_yuzde']:.1f} ({_fmt(en['gerceklesen'])})."
    )


def category_insight(rows: list[dict]) -> str:
    if not rows:
        return "Kategori verisi bulunamadi."
    en = rows[0]
    return (
        f"En buyuk gider kalemi {en['kategori']}: toplam {_fmt(en['tutar'])} "
        f"(tum giderlerin %{en['yuzde']:.1f}'i)."
    )


def build_insights(dashboard: dict, anomaly_count: int) -> dict:
    """Her grafik icin otomatik yorum metni uretir."""
    return {
        "trend": trend_insight(dashboard["aylik_trend"]),
        "butce": budget_insight(dashboard["butce_vs_gerceklesen"]),
        "kategori": category_insight(dashboard["kategori_dagilimi"]),
        "anomali": (
            f"{anomaly_count} adet alisilmadik harcama tespit edildi."
            if anomaly_count else "Anormal harcama tespit edilmedi."
        ),
    }
