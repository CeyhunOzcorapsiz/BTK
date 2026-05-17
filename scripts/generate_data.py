"""
ERPilot AI - Demo veri seti ureticisi.

Departman bazli kurumsal butce senaryosu icin iki CSV uretir:
  - backend/data/transactions.csv : gerceklesen gelir/gider hareketleri
  - backend/data/budgets.csv      : departman/kategori/ay bazli butce

Deterministiktir (sabit seed) - her calistirildiginda ayni veri uretilir.
Anomali tespitini gosterebilmek icin birkac bilincli aykiri deger eklenir.

Calistirma:
    python scripts/generate_data.py
"""

import csv
import random
from datetime import date
from pathlib import Path

SEED = 42
YEAR = 2025

MONTHS = [
    "Ocak", "Subat", "Mart", "Nisan", "Mayis", "Haziran",
    "Temmuz", "Agustos", "Eylul", "Ekim", "Kasim", "Aralik",
]

# Departman -> o departmanin tipik gider kategorileri ve aylik taban tutar araliklari (TL)
DEPARTMENTS = {
    "Pazarlama": {
        "Reklam": (60000, 110000),
        "Danismanlik": (15000, 35000),
        "Seyahat": (8000, 20000),
        "Yazilim Lisans": (5000, 12000),
    },
    "Satis": {
        "Personel": (180000, 240000),
        "Seyahat": (20000, 45000),
        "Yazilim Lisans": (8000, 15000),
    },
    "Bilgi Teknolojileri": {
        "Yazilim Lisans": (40000, 80000),
        "Donanim": (25000, 70000),
        "Personel": (150000, 210000),
        "Bakim Onarim": (6000, 18000),
    },
    "Insan Kaynaklari": {
        "Personel": (90000, 130000),
        "Egitim": (10000, 30000),
        "Danismanlik": (8000, 20000),
    },
    "Uretim": {
        "Personel": (300000, 420000),
        "Bakim Onarim": (30000, 75000),
        "Donanim": (20000, 60000),
    },
    "Finans": {
        "Personel": (110000, 150000),
        "Danismanlik": (15000, 40000),
        "Yazilim Lisans": (10000, 22000),
    },
    "Ar-Ge": {
        "Personel": (200000, 280000),
        "Donanim": (30000, 90000),
        "Yazilim Lisans": (15000, 35000),
    },
    "Lojistik": {
        "Lojistik Nakliye": (70000, 140000),
        "Personel": (80000, 120000),
        "Bakim Onarim": (10000, 25000),
    },
}

# Gelir senaryosu: aylik gelir kalemleri (taban araliklar)
# Toplam gelir, giderin uzerinde kalacak sekilde ayarlanmistir (saglikli kar marji).
INCOME_STREAMS = {
    "Urun Satisi": (1700000, 2150000),
    "Hizmet Geliri": (520000, 700000),
    "Bayi Geliri": (330000, 470000),
}

# (departman, kategori, ay_index) -> carpan : bilincli anomaliler
ANOMALIES = {
    ("Pazarlama", "Reklam", 6): 3.4,        # Temmuz - asiri reklam harcamasi
    ("Bilgi Teknolojileri", "Donanim", 9): 4.1,  # Ekim - buyuk donanim alimi
    ("Uretim", "Bakim Onarim", 2): 3.0,     # Mart - beklenmedik bakim maliyeti
}


def trend_factor(month_index: int) -> float:
    """Yil boyunca hafif buyume trendi (Ocak 1.00 -> Aralik ~1.13)."""
    return 1.0 + month_index * 0.012


def main() -> None:
    rng = random.Random(SEED)
    data_dir = Path(__file__).resolve().parent.parent / "backend" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    tx_rows: list[dict] = []
    budget_rows: list[dict] = []

    for m_idx, month in enumerate(MONTHS):
        trend = trend_factor(m_idx)

        # ----- Giderler -----
        for dept, categories in DEPARTMENTS.items():
            for category, (low, high) in categories.items():
                base = rng.uniform(low, high) * trend
                anomaly_mult = ANOMALIES.get((dept, category, m_idx), 1.0)
                actual = base * anomaly_mult

                # Butce: trend dahil taban beklenti (anomaliyi bilmez)
                budget = round(rng.uniform(low, high) * trend, -2)
                budget_rows.append({
                    "yil": YEAR,
                    "ay": month,
                    "ay_no": m_idx + 1,
                    "departman": dept,
                    "kategori": category,
                    "butce": int(budget),
                })

                # Gerceklesen tutari 1-3 harekete bol
                n = rng.randint(1, 3)
                parts = [rng.random() for _ in range(n)]
                total = sum(parts)
                for i, p in enumerate(parts):
                    amount = round(actual * p / total, -1)
                    if amount <= 0:
                        continue
                    day = rng.randint(1, 28)
                    note = f"{category} - {dept}"
                    if anomaly_mult > 1.0 and i == 0:
                        note = f"{category} - {dept} (buyuk kalem)"
                    tx_rows.append({
                        "tarih": date(YEAR, m_idx + 1, day).isoformat(),
                        "yil": YEAR,
                        "ay": month,
                        "ay_no": m_idx + 1,
                        "departman": dept,
                        "kategori": category,
                        "tur": "gider",
                        "tutar": int(amount),
                        "aciklama": note,
                    })

        # ----- Gelirler (Satis departmanina yazilir) -----
        for stream, (low, high) in INCOME_STREAMS.items():
            amount = round(rng.uniform(low, high) * trend, -2)
            day = rng.randint(1, 28)
            tx_rows.append({
                "tarih": date(YEAR, m_idx + 1, day).isoformat(),
                "yil": YEAR,
                "ay": month,
                "ay_no": m_idx + 1,
                "departman": "Satis",
                "kategori": stream,
                "tur": "gelir",
                "tutar": int(amount),
                "aciklama": f"{stream} geliri",
            })

    tx_path = data_dir / "transactions.csv"
    budget_path = data_dir / "budgets.csv"

    with tx_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["tarih", "yil", "ay", "ay_no", "departman",
                        "kategori", "tur", "tutar", "aciklama"],
        )
        writer.writeheader()
        writer.writerows(tx_rows)

    with budget_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["yil", "ay", "ay_no", "departman", "kategori", "butce"],
        )
        writer.writeheader()
        writer.writerows(budget_rows)

    print(f"transactions.csv  -> {len(tx_rows)} satir")
    print(f"budgets.csv       -> {len(budget_rows)} satir")
    print(f"Klasor: {data_dir}")


if __name__ == "__main__":
    main()
