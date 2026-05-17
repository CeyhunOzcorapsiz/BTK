"""
Veri kaynagi soyutlamasi.

Is mantigi (query_engine, anomaly, dashboard) ham veri kaynagini ASLA bilmez.
Tum kaynaklar ayni normalize edilmis sema ile DataFrame dondurur:

  transactions: tarih, yil, ay, ay_no, departman, kategori, tur, tutar, aciklama
  budgets     : yil, ay, ay_no, departman, kategori, butce

Boylece kaynak CSV'den SAP'ye gectiginde yukaridaki katmanlar hic degismez.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from config import settings

TRANSACTION_COLUMNS = [
    "tarih", "yil", "ay", "ay_no", "departman",
    "kategori", "tur", "tutar", "aciklama",
]
BUDGET_COLUMNS = ["yil", "ay", "ay_no", "departman", "kategori", "butce"]


class DataSourceError(RuntimeError):
    """Veri kaynagi okunamadiginda firlatilir."""


class DataSource(ABC):
    """Tum veri kaynaklarinin uymasi gereken arayuz."""

    @abstractmethod
    def get_transactions(self) -> pd.DataFrame:
        """Normalize edilmis gelir/gider hareketlerini dondurur."""

    @abstractmethod
    def get_budgets(self) -> pd.DataFrame:
        """Normalize edilmis butce satirlarini dondurur."""


class CsvDataSource(DataSource):
    """MVP veri kaynagi: yerel CSV dosyalari. Okunan veri bellekte cache'lenir."""

    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir
        self._transactions: pd.DataFrame | None = None
        self._budgets: pd.DataFrame | None = None

    def _read_csv(self, name: str, required_columns: list[str]) -> pd.DataFrame:
        path = self._data_dir / name
        if not path.exists():
            raise DataSourceError(
                f"Veri dosyasi bulunamadi: {path}. "
                f"Once 'python scripts/generate_data.py' calistirin."
            )
        df = pd.read_csv(path, encoding="utf-8")
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise DataSourceError(f"{name} dosyasinda eksik kolon(lar): {missing}")
        return df

    def get_transactions(self) -> pd.DataFrame:
        if self._transactions is None:
            df = self._read_csv("transactions.csv", TRANSACTION_COLUMNS)
            self._transactions = df[TRANSACTION_COLUMNS].copy()
        return self._transactions

    def get_budgets(self) -> pd.DataFrame:
        if self._budgets is None:
            df = self._read_csv("budgets.csv", BUDGET_COLUMNS)
            self._budgets = df[BUDGET_COLUMNS].copy()
        return self._budgets


class SapDataSource(DataSource):
    """
    FUTURE WORK - SAP entegrasyonu iskeleti.

    Gercek senaryoda SAP S/4HANA verisi OData REST servisleri uzerinden okunur.
    Akis (her metot icin):
      1. httpx ile SAP OData endpoint'ine kimlik dogrulamali GET istegi
         ornek: GET {SAP_ODATA_BASE_URL}/sap/opu/odata/sap/ZFI_BUDGET_SRV/Transactions
      2. Donen JSON (results listesi) pandas DataFrame'e cevrilir
      3. SAP alan adlari bizim normalize semamiza eslenir, ornek:
           CompanyCode/CostCenter -> departman
           GLAccountGroup         -> kategori
           AmountInCompanyCode    -> tutar
           FiscalPeriod           -> ay_no / ay
           DebitCreditCode        -> tur (S=gider, H=gelir)
      4. Sonuc TRANSACTION_COLUMNS / BUDGET_COLUMNS semasinda dondurulur.

    Alternatif: pyrfc ile dogrudan BAPI/RFC cagrisi (SAP NW RFC SDK gerektirir).

    Bu sinif su an bilincli olarak NotImplementedError firlatir; MVP'de
    DATA_SOURCE=csv kullanilir. Mimarinin amaci: bu sinif tamamlandiginda
    query_engine / anomaly / dashboard katmanlarinda HICBIR degisiklik gerekmez.
    """

    def __init__(self, base_url: str, user: str, password: str) -> None:
        self._base_url = base_url
        self._user = user
        self._password = password

    def get_transactions(self) -> pd.DataFrame:  # pragma: no cover - future work
        raise NotImplementedError(
            "SAP entegrasyonu future work kapsamindadir. "
            "MVP icin DATA_SOURCE=csv kullanin."
        )

    def get_budgets(self) -> pd.DataFrame:  # pragma: no cover - future work
        raise NotImplementedError(
            "SAP entegrasyonu future work kapsamindadir. "
            "MVP icin DATA_SOURCE=csv kullanin."
        )


def get_data_source() -> DataSource:
    """Config'e gore aktif veri kaynagini olusturur (factory)."""
    kind = settings.data_source.lower()
    if kind == "csv":
        return CsvDataSource(settings.data_path)
    if kind == "sap":
        return SapDataSource(
            settings.sap_odata_base_url,
            settings.sap_odata_user,
            settings.sap_odata_password,
        )
    raise DataSourceError(f"Bilinmeyen DATA_SOURCE: {settings.data_source}")
