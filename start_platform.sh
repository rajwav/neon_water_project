#!/bin/bash
# =============================================================================
# AQUA NEON (Team AutoNex) — Production Platform Launch Script
# Starts FastAPI Microservice (Port 8000) & Streamlit Command Center (Dynamic PORT)
# =============================================================================

set -e

echo "🌊 Starting AQUA NEON National Water Intelligence Platform..."

# 1. Start FastAPI Backend Microservice in Background (Port 8000)
echo "🚀 Launching FastAPI Backend on port 8000..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

# Trap signals to gracefully terminate FastAPI when Streamlit stops
trap "kill $FASTAPI_PID 2>/dev/null || true" EXIT

# Allow FastAPI to initialize
sleep 2

# 2. Launch Streamlit National Command Center (Dynamic Port for Render/Heroku/Docker)
STREAMLIT_PORT=${PORT:-8501}
echo "🖥️ Launching Streamlit Command Center on port ${STREAMLIT_PORT}..."
streamlit run app.py --server.port "${STREAMLIT_PORT}" --server.address 0.0.0.0 --server.headless true
