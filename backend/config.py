"""Ortam degiskeni tabanli uygulama ayarlari."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_max_concurrency: int = 3
    gemini_timeout_seconds: float = 20.0

    # Veri kaynagi
    data_source: str = "csv"  # csv | sap
    data_dir: str = "data"

    # Sunucu
    host: str = "127.0.0.1"
    port: int = 8000
    allowed_origins: str = "http://127.0.0.1:8000,http://localhost:8000"

    # Rate limiting / cache
    chat_rate_limit: str = "10/minute"
    cache_ttl_seconds: int = 120

    # SAP (future work)
    sap_odata_base_url: str = ""
    sap_odata_user: str = ""
    sap_odata_password: str = ""

    @property
    def data_path(self) -> Path:
        """CSV veri klasorunun mutlak yolu."""
        p = Path(self.data_dir)
        return p if p.is_absolute() else BACKEND_DIR / p

    @property
    def origin_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
