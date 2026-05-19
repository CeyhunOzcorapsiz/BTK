"""
ERPilot AI - FastAPI REST backend.

Endpoint'ler:
  GET  /api/health        - saglik kontrolu
  POST /api/chat          - veriye dogal dil sorusu (Gemini function calling)
  GET  /api/dashboard     - trend, butce, kategori (opsiyonel ?ay=)
  GET  /api/anomalies     - anomali listesi (opsiyonel ?ay=)
  GET  /api/insights      - grafik basina AI yorumu (opsiyonel ?ay=)
  GET  /api/transactions  - ham hareket verisi (filtreli)
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from analytics import available_months, build_dashboard, build_insights
from anomaly import detect_anomalies
from config import PROJECT_DIR, settings
from datasource import DataSourceError, get_data_source

# --- Uygulama durumu ---------------------------------------------------------

state: dict = {}

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Baslangicta veri kaynagini yukle ve dogrula."""
    source = get_data_source()
    state["transactions"] = source.get_transactions()
    state["budgets"] = source.get_budgets()
    yield
    from gemini_client import close_client
    await close_client()
    state.clear()


app = FastAPI(title="ERPilot AI", version="0.1.0", lifespan=lifespan)
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origin_list,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def _no_cache_static(request: Request, call_next):
    """
    Frontend dosyalari (html/css/js) icin tarayici her istekte sunucuyu
    dogrular. Boylece kod degisince eski surum onbellekten servis edilmez.
    """
    response = await call_next(request)
    path = request.url.path
    if path == "/" or path.endswith((".html", ".css", ".js")):
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
    return response


# --- Tutarli hata govdesi ----------------------------------------------------

def _error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message}},
    )


@app.exception_handler(RateLimitExceeded)
async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return _error(429, "rate_limited",
                  "Cok fazla istek gonderildi, lutfen biraz bekleyin.")


@app.exception_handler(RequestValidationError)
async def _validation_handler(request: Request, exc: RequestValidationError):
    return _error(422, "validation_error",
                  "Gecersiz istek. Mesaj 1-500 karakter olmalidir.")


@app.exception_handler(DataSourceError)
async def _datasource_handler(request: Request, exc: DataSourceError):
    return _error(500, "datasource_error", str(exc))


@app.exception_handler(Exception)
async def _generic_handler(request: Request, exc: Exception):
    return _error(500, "internal_error", "Beklenmeyen bir hata olustu.")


def _resolve_ay(ay: str | None) -> tuple[str | None, JSONResponse | None]:
    """
    ?ay= parametresini dogrular. Donus: (gecerli_ay, hata_yaniti).
    ay bos ise (None, None); gecersizse (None, 400 hata); gecerliyse (ay, None).
    """
    if not ay:
        return None, None
    if ay not in available_months(state["transactions"]):
        return None, _error(400, "invalid_month", f"Gecersiz ay: {ay}")
    return ay, None


# --- Semalar -----------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    lang: str = Field(default="tr", max_length=5)


class ChatResponse(BaseModel):
    answer: str
    provider: str
    query: dict | None = None
    result: dict | None = None
    cached: bool = False


# --- Endpoint'ler ------------------------------------------------------------

@app.get("/api/health")
async def health() -> dict:
    tx = state.get("transactions")
    return {
        "status": "ok",
        "data_source": settings.data_source,
        "transaction_count": 0 if tx is None else int(len(tx)),
        "gemini_enabled": bool(settings.gemini_api_key),
    }


@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit(settings.chat_rate_limit)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    # gemini_client agirsiklikli import edilir (httpx vb. yalnizca gerektiginde)
    from gemini_client import answer_question

    result = await answer_question(body.message, state["transactions"], body.lang)
    return ChatResponse(
        answer=result["answer"],
        provider=result["provider"],
        query=result.get("query"),
        result=result.get("result"),
        cached=result.get("cached", False),
    )


@app.get("/api/transactions")
async def transactions(
    departman: str | None = Query(default=None),
    kategori: str | None = Query(default=None),
    ay: str | None = Query(default=None),
    tur: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
) -> dict:
    df = state["transactions"]
    for col, val in (("departman", departman), ("kategori", kategori),
                     ("ay", ay), ("tur", tur)):
        if val:
            df = df[df[col].astype(str).str.lower() == val.lower()]
    return {
        "count": int(len(df)),
        "rows": df.head(limit).to_dict(orient="records"),
    }


@app.get("/api/dashboard")
async def dashboard(ay: str | None = Query(default=None)):
    ay_val, err = _resolve_ay(ay)
    if err:
        return err
    return build_dashboard(state["transactions"], state["budgets"], ay_val)


@app.get("/api/anomalies")
async def anomalies(ay: str | None = Query(default=None)):
    ay_val, err = _resolve_ay(ay)
    if err:
        return err
    bulgular = detect_anomalies(state["transactions"], ay_val)
    return {"count": len(bulgular), "secili_ay": ay_val, "anomalies": bulgular}


@app.get("/api/insights")
async def insights(ay: str | None = Query(default=None)):
    from gemini_client import generate_insights

    ay_val, err = _resolve_ay(ay)
    if err:
        return err
    dash = build_dashboard(state["transactions"], state["budgets"], ay_val)
    anomaly_count = len(detect_anomalies(state["transactions"], ay_val))
    deterministic = {
        "tr": build_insights(dash, anomaly_count, "tr"),
        "en": build_insights(dash, anomaly_count, "en"),
    }
    return await generate_insights(deterministic, ay_val)


# --- Frontend statik dosyalari (API route'larindan SONRA mount edilir) -------

app.mount("/", StaticFiles(directory=PROJECT_DIR, html=True), name="frontend")
