#!/bin/bash
# =============================================================================
# AQUA NEON (Team AutoNex) — Production Platform Launch Script
# Starts FastAPI Microservice (Port 8000) & Streamlit Command Center (Dynamic PORT)
# =============================================================================

set -e

echo "🌊 Starting AQUA NEON National Water Intelligence Platform..."

# 1. Determine Public Streamlit Port (Render provides $PORT, default 8501)
STREAMLIT_PORT=${PORT:-8501}

# 2. Start FastAPI Backend Microservice on internal loopback (avoids collision if PORT=8000)
if [ "$STREAMLIT_PORT" = "8000" ]; then
    FASTAPI_PORT=8008
else
    FASTAPI_PORT=8000
fi

export FASTAPI_URL="http://127.0.0.1:${FASTAPI_PORT}"
echo "🚀 Launching FastAPI Backend on internal loopback ${FASTAPI_URL}..."
uvicorn backend.main:app --host 127.0.0.1 --port "${FASTAPI_PORT}" &
FASTAPI_PID=$!

# Trap signals to gracefully terminate FastAPI when Streamlit stops
trap "kill $FASTAPI_PID 2>/dev/null || true" EXIT

# Allow FastAPI to initialize
sleep 2

# 3. Launch Streamlit National Command Center on Public Port
echo "🖥️ Launching Streamlit Command Center on port ${STREAMLIT_PORT}..."
exec streamlit run app.py --server.port "${STREAMLIT_PORT}" --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false
