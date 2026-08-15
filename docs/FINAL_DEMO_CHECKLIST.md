# SIH 2026 Live Demonstration Checklist & Contingency Manual
## NEON Water Intelligence Platform

**Document Purpose**: Step-by-step checklist for live stage demonstrations, technical evaluations, and offline fallback procedures.  
**Repository**: `neon_water_project`

---

# 1. PRE-DEMO SYSTEM INITIALIZATION (COMMANDS)

Open **two terminal windows** in the project directory:

### Terminal 1: Launch FastAPI Serving Backend
```bash
cd /Users/raj/neon_water_project
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
*Expected Output*:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Terminal 2: Launch Streamlit Operations Console
```bash
cd /Users/raj/neon_water_project
source .venv/bin/activate
streamlit run dashboard/app.py --server.port 8501
```
*Expected Output*:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### Terminal 3 (Optional): Verify Backend Test Suite
```bash
pytest tests/test_backend_api.py -v
```
*Expected Output*: `10 passed in ~5s` (100% test pass rate).

---

# 2. STEP-BY-STEP LIVE PRESENTATION FLOW

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   LIVE DEMONSTRATION WORKFLOW                                   │
├──────┬───────────────────────────────────────┬──────────────────────────────────────────────────┤
│ Step │ Presenter Action                      │ Key Talking Points & Expected Dashboard Reaction │
├──────┼───────────────────────────────────────┼──────────────────────────────────────────────────┤
│ 1    │ Open Dashboard (http://localhost:8501)│ Highlight Header: "API Service: Online (v3.0.0)",│
│      │                                       │ "IoT Node: Connected", "Multi-Domain Telemetry". │
├──────┼───────────────────────────────────────┼──────────────────────────────────────────────────┤
│ 2    │ Click "1. Pristine Baseline" Preset   │ • Banner turns 🟢 GREEN (SAFE).                  │
│      │                                       │ • Eco Health Index: 96.5/100 (Pristine).         │
│      │                                       │ • Model 1 Score: -0.159 (Inlier).                │
│      │                                       │ • Model 2 Confidence: 73.6% SAFE.                │
├──────┼───────────────────────────────────────┼──────────────────────────────────────────────────┤
│ 3    │ Click "2. Turbidity Shock" Preset     │ • Banner turns 🟡 AMBER WARNING.                 │
│      │                                       │ • Turbidity: 85.0 FNU, SSC: 240 mg/L.            │
│      │                                       │ • Model 1 flags statistical Anomaly (+0.08).     │
│      │                                       │ • XAI diagnoses light attenuation stress.        │
├──────┼───────────────────────────────────────┼──────────────────────────────────────────────────┤
│ 4    │ Click "3. Eutrophic Anoxia" Preset    │ • Banner turns 🔴 RED CRITICAL (Lethal Anoxia).  │
│      │                                       │ • DO: 1.80 mg/L, Nitrate: 12.8 mg/L.             │
│      │                                       │ • Deterministic Safety Guardrail overrides ML.   │
│      │                                       │ • Eco Health Index caps at 24.5/100 (Collapse).  │
├──────┼───────────────────────────────────────┼──────────────────────────────────────────────────┤
│ 5    │ Click "4. Toxic Heavy Metal" Preset   │ • Banner turns 🔴 RED CRITICAL (Metal Toxicity). │
│      │                                       │ • Lead Risk: 0.85, Bioassay Stress: 15.0/100.    │
│      │                                       │ • Demonstrates biological bioassay protection.   │
├──────┼───────────────────────────────────────┼──────────────────────────────────────────────────┤
│ 6    │ Click "5. Acid Spill" Preset          │ • Banner turns 🔴 RED CRITICAL (Acid Dump).      │
│      │                                       │ • pH: 2.80, Conductance: 1450 µS/cm.             │
│      │                                       │ • Demonstrates lethal chemical boundary guard.   │
├──────┼───────────────────────────────────────┼──────────────────────────────────────────────────┤
│ 7    │ Switch to Tab 2: "Historical USGS     │ • Showcase 77,641 sampling events from USGS/EPA. │
│      │ Catchment Analytics"                  │ • Filter by station to display live histograms   │
│      │                                       │   and dominant EPA bioassay test species.        │
├──────┼───────────────────────────────────────┼──────────────────────────────────────────────────┤
│ 8    │ Switch to Tab 3: "Multi-Domain AI     │ • Show Gini feature importance chart (Turbidity  │
│      │ Architecture"                         │   29.6%, Conductance 16.4%, pH 14.4%, DO 14.2%). │
└──────┴───────────────────────────────────────┴──────────────────────────────────────────────────┘
```

---

# 3. WOKWI DIGITAL TWIN LIVE CONNECTION (OPTIONAL HARDWARE DEMO)

1. Open [wokwi.com/projects/new/esp32](https://wokwi.com/projects/new/esp32).
2. Paste `wokwi/diagram.json` and `wokwi/sketch.ino`.
3. Click **Play (▶)**.
4. Rotate the **`pot_turb` (Turbidity)** potentiometer clockwise $\rightarrow$ Watch the Streamlit dashboard update live and observe the ESP32 status LED turn from Green to Yellow/Red.

---

# 4. CONTINGENCY & OFFLINE BACKUP PLAN (IF INTERNET OR WOKWI FAILS)

```
┌──────────────────────────────────────┬──────────────────────────────────────────────────────────┐
│ Failure Scenario                     │ Built-in Automatic Mitigation                            │
├──────────────────────────────────────┼──────────────────────────────────────────────────────────┤
│ 1. Internet connection drops         │ • Entire platform runs 100% locally on localhost:8000    │
│                                      │   and localhost:8501. Zero cloud dependencies.           │
├──────────────────────────────────────┼──────────────────────────────────────────────────────────┤
│ 2. FastAPI backend process crashes   │ • Dashboard has built-in In-Process Direct Engine        │
│                                      │   Fallback (imports backend.model_loader directly).      │
│                                      │ • Dashboard automatically shows:                         │
│                                      │   "Direct ML Engine (In-Process Fallback)".              │
├──────────────────────────────────────┼──────────────────────────────────────────────────────────┤
│ 3. Wokwi website unreachable         │ • Use Sidebar "Simulated IoT Telemetry Stream" mode in   │
│                                      │   Streamlit dashboard to generate real-time IoT packets. │
├──────────────────────────────────────┼──────────────────────────────────────────────────────────┤
│ 4. Hardware probe values corrupted   │ • Click any of the 5 Quick SIH Preset buttons to restore │
│                                      │   calibrated scientific reference vectors instantly.     │
└──────────────────────────────────────┴──────────────────────────────────────────────────────────┘
```
