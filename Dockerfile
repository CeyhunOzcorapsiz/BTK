# ERPilot AI - tek container (FastAPI hem API hem frontend'i serve eder)
FROM python:3.12-slim

WORKDIR /app

# Bagimliliklar once kopyalanir - kod degisince katman cache korunur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodu
COPY backend/ ./backend/
COPY index.html app.js styles.css ./

# Demo CSV verisi backend/data/ icinde repoda mevcut; uretime gerek yok.
ENV HOST=0.0.0.0 \
    PORT=8000 \
    DATA_SOURCE=csv

EXPOSE 8000

# GEMINI_API_KEY runtime'da -e ile veya host panelinden secret olarak verilir.
# uvicorn backend/ dizininden calistirilir; PORT host tarafindan ezilebilir.
CMD ["sh", "-c", "uvicorn main:app --app-dir backend --host 0.0.0.0 --port ${PORT}"]
