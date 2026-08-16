# AQUA NEON (Project NEON) — Team AutoNex
## Complete Production & Cloud Deployment Guide

---

## 🚀 Deployment Readiness Checklist

- ✅ **All 5 Machine Learning Models Loaded**: Models 1–5 pre-serialized in `models/` directory.
- ✅ **Decoupled Architecture**: FastAPI REST backend (`backend/main.py`) on Port 8000 + Streamlit Command Center on Port 8501.
- ✅ **Standalone In-Memory Fallback**: If FastAPI is not running externally, Streamlit gracefully evaluates models directly in-memory via `backend.model_loader.engine`.
- ✅ **Persistent Time-Series Database**: SQLite database in `data/telemetry_history.db`.
- ✅ **Automated Test Verification**: All 37 unit, integration, and safety tests passing ($100\%$).

---

# 🌐 OPTION 1: Streamlit Community Cloud (Recommended — Free & Instant)

**Best for**: Live SIH jury demonstrations and sharing public URL.

### Step-by-Step Instructions:
1. **Push Code to GitHub**:
   Ensure your repository is pushed to GitHub:
   ```bash
   git add .
   git commit -m "Deploy AQUA NEON to production"
   git push origin main
   ```
2. **Open Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io).
   - Sign in with your GitHub account.
3. **Deploy App**:
   - Click **"New app"**.
   - Select your repository (`neon_water_project` or `AQUA_NEON`).
   - Branch: `main`.
   - Main file path: **`app.py`** (or `dashboard/app.py`).
   - Click **"Deploy!"**.
4. **Result**: Your app will be live with a public HTTPS URL (e.g. `https://aqua-neon.streamlit.app`) in under 2 minutes!

---

# 🐳 OPTION 2: Docker / Docker-Compose (AWS / DigitalOcean / Local)

**Best for**: Production servers, cloud VMs, and on-premise government deployment.

### 1-Command Local or Cloud Launch:
```bash
# Build and start both FastAPI (Port 8000) and Streamlit (Port 8501)
docker-compose up -d --build
```

### Access Services:
- **Streamlit Command Center**: `http://<SERVER_IP>:8501`
- **FastAPI OpenAPI Interactive Docs**: `http://<SERVER_IP>:8000/docs`
- **Health Endpoint**: `http://<SERVER_IP>:8000/health`

---

# ☁️ OPTION 3: Render / Railway / Hugging Face Spaces

### A. Deploy on Render:
1. Go to [render.com](https://render.com) and create a **New Web Service**.
2. Connect your GitHub repository.
3. Configuration:
   - **Environment**: `Python 3` (or `Docker`).
   - **Build Command**: `pip install -r requirements.txt`.
   - **Start Command**: `./start_platform.sh` (or `streamlit run app.py --server.port $PORT`).
4. Click **Deploy Web Service**.

### B. Deploy on Hugging Face Spaces:
1. Create a new Space on [huggingface.co/spaces](https://huggingface.co/spaces).
2. Space SDK: **Streamlit**.
3. Push your repository files into the Space.
4. Hugging Face will automatically detect `app.py` and `requirements.txt` and launch the app immediately.

---

# 💻 OPTION 4: Local Production Run (macOS / Linux / Windows)

To run the complete platform locally:

```bash
# Option A: Run the unified launch script (Starts FastAPI + Streamlit)
./start_platform.sh

# Option B: Run via Streamlit directly
streamlit run app.py
```

Open your browser at `http://localhost:8501`.
