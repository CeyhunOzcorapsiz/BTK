"""
Guvenli sorgu motoru.

AI ham SQL/kod URETMEZ. AI yalnizca asagidaki QuerySpec semasina uygun
yapisal bir nesne uretir. Bu motor:
  1. Gelen spec'i allowlist'e karsi dogrular (Pydantic Literal tipleri = allowlist).
  2. Yalnizca sabit, onceden yazilmis pandas islemlerini calistirir.
     eval / exec / DataFrame.query(string) KULLANILMAZ.

Boylece AI'in ifade gucu kasitli olarak kisitlidir: uretebilecegi tek sey
semaya uyan bir nesnedir; calistirma mantigi tamamen bu dosyadadir.
"""

from __future__ import annotations

from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field, field_validator

# --- Allowlist'ler ------------------------------------------------------------

DIMENSION_FIELDS = Literal["departman", "kategori", "ay", "tur", "yil"]
NUMERIC_FIELD = Literal["tutar"]
METRIC = Literal["toplam", "ortalama", "sayim", "minimum", "maksimum"]
OPERATOR = Literal[
    "esittir", "esit_degil", "buyuktur", "kucuktur",
    "buyuk_esit", "kucuk_esit", "iceriyor",
]
SORT = Literal["artan", "azalan"]

# Metric adi -> pandas agregasyon fonksiyonu (sabit eslesme)
_METRIC_FUNCS = {
    "toplam": "sum",
    "ortalama": "mean",
    "sayim": "count",
    "minimum": "min",
    "maksimum": "max",
}

MAX_LIMIT = 100


class QueryValidationError(ValueError):
    """Sorgu spec'i allowlist disinda bir deger icerdiginde firlatilir."""


# --- Sorgu semasi (AI bunu doldurur) -----------------------------------------

class QueryFilter(BaseModel):
    field: DIMENSION_FIELDS
    operator: OPERATOR
    value: str | int | float


class QuerySpec(BaseModel):
    """AI'in uretebilecegi tek sorgu yapisi. Tum tipler allowlist'tir."""

    metric: METRIC = "toplam"
    field: NUMERIC_FIELD = "tutar"
    group_by: DIMENSION_FIELDS | None = None
    filters: list[QueryFilter] = Field(default_factory=list)
    sort: SORT | None = None
    limit: int = 10

    @field_validator("limit")
    @classmethod
    def _clamp_limit(cls, v: int) -> int:
        return max(1, min(v, MAX_LIMIT))


# --- Calistirma (yalnizca sabit pandas islemleri) ----------------------------

def _apply_filter(df: pd.DataFrame, f: QueryFilter) -> pd.DataFrame:
    """Tek bir filtreyi sabit pandas islemleriyle uygular."""
    col = df[f.field]

    if f.operator == "iceriyor":
        # regex=False: filtre degeri duz metin olarak islenir (regex degil).
        # Aksi halde ozel karakterli deger regex hatasi/beklenmedik eslesme uretir.
        return df[col.astype(str).str.contains(
            str(f.value), case=False, na=False, regex=False
        )]

    if f.operator == "esittir":
        return df[col.astype(str).str.lower() == str(f.value).lower()]

    if f.operator == "esit_degil":
        return df[col.astype(str).str.lower() != str(f.value).lower()]

    # Sayisal karsilastirmalar - deger sayiya cevrilebilmeli
    try:
        num = float(f.value)
    except (TypeError, ValueError):
        raise QueryValidationError(
            f"'{f.operator}' operatoru sayisal deger gerektirir, alinan: {f.value!r}"
        )
    numeric_col = pd.to_numeric(col, errors="coerce")
    if f.operator == "buyuktur":
        return df[numeric_col > num]
    if f.operator == "kucuktur":
        return df[numeric_col < num]
    if f.operator == "buyuk_esit":
        return df[numeric_col >= num]
    if f.operator == "kucuk_esit":
        return df[numeric_col <= num]

    raise QueryValidationError(f"Bilinmeyen operator: {f.operator}")


def run_query(spec: QuerySpec, transactions: pd.DataFrame) -> dict:
    """
    Dogrulanmis bir QuerySpec'i transactions DataFrame uzerinde calistirir.
    Sonuc: {"metric", "group_by", "filtered_row_count", "rows": [...]}
    """
    df = transactions

    for f in spec.filters:
        df = _apply_filter(df, f)

    agg = _METRIC_FUNCS[spec.metric]
    filtered_count = int(len(df))

    if spec.group_by:
        if df.empty:
            rows: list[dict] = []
        else:
            grouped = df.groupby(spec.group_by)[spec.field].agg(agg)
            ascending = spec.sort != "azalan"
            grouped = grouped.sort_values(ascending=ascending)
            grouped = grouped.head(spec.limit)
            rows = [
                {spec.group_by: str(idx), "deger": round(float(val), 2)}
                for idx, val in grouped.items()
            ]
    else:
        if df.empty:
            value = 0.0
        elif spec.metric == "sayim":
            value = float(len(df))
        else:
            value = float(getattr(df[spec.field], agg)())
        rows = [{"deger": round(value, 2)}]

    return {
        "metric": spec.metric,
        "group_by": spec.group_by,
        "filtered_row_count": filtered_count,
        "rows": rows,
    }
