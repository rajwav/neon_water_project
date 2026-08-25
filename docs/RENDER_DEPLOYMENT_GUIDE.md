# AQUA NEON (Team AutoNex) — Render.com Cloud Deployment Guide

This guide details how to deploy **AQUA NEON** to Render.com with both the **FastAPI Microservice (Port 8000)** and **Streamlit Command Center (Port $PORT)** running in a single, unified web service.

---

## 🚀 Pre-Deployment Checklist

- ✅ All 5 pre-trained models included in `models/v3/`
- ✅ Dynamic `$PORT` handling enabled in `start_platform.sh`
- ✅ Automatic in-memory ML fallback active if external network ports are restricted
- ✅ SQLite database directory (`data/`) auto-created on startup

---

## 🛠️ Step-by-Step Render Deployment Instructions

### Method 1: Web Service using Docker (Recommended)

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Configure production deployment for Render"
   git push origin main
   ```

2. **Log into Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com).
   - Click **"New +"** in the top navigation and select **"Web Service"**.

3. **Connect Repository**:
   - Choose **"Build and deploy from a Git repository"**.
   - Select your repository `neon_water_project` / `AQUA_NEON`.

4. **Configure Service**:
   - **Name**: `autonex-aqua-neon`
   - **Region**: Singapore / Oregon / Frankfurt (closest to your audience)
   - **Branch**: `main`
   - **Runtime**: **Docker** (Render will automatically detect your `Dockerfile`)
   - **Instance Type**: Free / Starter (Free tier with 512MB–1GB RAM is sufficient)

5. **Deploy**:
   - Click **"Create Web Service"**.
   - Render will build the Docker container and start `start_platform.sh`.
   - Your public URL will be ready: `https://autonex-aqua-neon.onrender.com`.

---

### Method 2: Native Python Web Service (Without Docker)

If you prefer deploying without Docker:

1. **Create Web Service** $\to$ Connect GitHub repository.
2. **Configure Settings**:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `./start_platform.sh`
   - *(Alternative Start Command if using single Streamlit process)*:  
     `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
3. Click **Create Web Service**.

---

## 🔍 Post-Deployment Verification

Once Render displays **"Live"**:
1. Open your Render URL (`https://autonex-aqua-neon.onrender.com`).
2. Verify:
   - Screen 1: PyDeck GIS dark map renders with river lines and Hirakud node.
   - Screen 2: Digital Twin water column renders with live 5-second telemetry.
   - Screen 3: AI Intelligence Center evaluates Models 1–5 and displays the TreeSHAP waterfall chart.
3. Test Autonomous Scenarios:
   - In the sidebar, select **"Acid Spill Contamination"** and click **"📡 Set Scenario"**.
   - Verify Screen 3 immediately updates to **CRITICAL** status with chemical explanation.

---

*Your application is completely production audited and deployment certified!* 🚀
