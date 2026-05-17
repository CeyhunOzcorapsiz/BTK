"""
Anomali tespiti - IQR (Interquartile Range) yontemi.

ML/egitim gerektirmez; aciklanabilir ve deterministiktir.
Her (departman, kategori) grubu icin gider hareketlerinin dagilimina bakilir:
  Q1, Q3 -> IQR = Q3 - Q1
  ust sinir = Q3 + 1.5 * IQR
Bu sinirin uzerindeki hareketler "alisilmadik harcama" olarak isaretlenir.

Gruplama (departman, kategori) bazindadir cunku tutar olcegi kategoriye gore
cok degisir (orn. Uretim/Personel ile IK/Egitim ayni esikle olculemez).
"""

from __future__ import annotations

import pandas as pd

# 1.5 standart "outlier" esigidir; kucuk gruplarda gurultuyu azaltmak icin
# 2.0 kullaniyoruz - yalnizca belirgin aykiri harcamalar isaretlenir.
IQR_MULTIPLIER = 2.0
MIN_GROUP_SIZE = 4  # IQR'in anlamli olmasi icin minimum hareket sayisi


def detect_anomalies(transactions: pd.DataFrame) -> list[dict]:
    """Alisilmadik yuksek gider hareketlerini dondurur (buyukten kucuge)."""
    giderler = transactions[transactions["tur"] == "gider"]
    bulgular: list[dict] = []

    for (dept, kategori), grup in giderler.groupby(["departman", "kategori"]):
        if len(grup) < MIN_GROUP_SIZE:
            continue
        q1 = grup["tutar"].quantile(0.25)
        q3 = grup["tutar"].quantile(0.75)
        iqr = q3 - q1
        if iqr <= 0:
            continue
        ust_sinir = q3 + IQR_MULTIPLIER * iqr

        for _, satir in grup[grup["tutar"] > ust_sinir].iterrows():
            tutar = float(satir["tutar"])
            sapma = (tutar - ust_sinir) / ust_sinir * 100.0
            bulgular.append({
                "tarih": str(satir["tarih"]),
                "departman": dept,
                "kategori": kategori,
                "ay": str(satir["ay"]),
                "tutar": round(tutar, 2),
                "beklenen_ust_sinir": round(float(ust_sinir), 2),
                "sapma_yuzde": round(sapma, 1),
                "aciklama": str(satir["aciklama"]),
            })

    return sorted(bulgular, key=lambda b: b["sapma_yuzde"], reverse=True)
