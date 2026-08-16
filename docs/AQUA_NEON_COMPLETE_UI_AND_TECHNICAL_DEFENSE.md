# AQUA NEON: Complete UI Component Walkthrough & Technical Defense Blueprint
## Project: AQUA NEON (AI-Powered National Water Quality Monitoring & Digital Twin Platform)
### Team: AutoNex | Smart India Hackathon Grand Finale

---

# 📑 PART 1: COMPLETE WEBSITE & SCREEN-BY-SCREEN WALKTHROUGH

```
Application Technology Stack:
• UI Shell: Streamlit 1.42+ (Custom Cyber-Hydrology Dark Theme, Orbitron / JetBrains Mono / Inter typography)
• GIS Map Engine: PyDeck WebGL (Carto Dark Matter vector tiles, HydroRIVERS GeoJSON geometry)
• Digital Twin Renderer: Embedded SVG / Canvas 2D/3D physics-informed stratification viewport
• Visual Analytics: Plotly Interactive Diverging Bar Charts (TreeSHAP), Gauges, Multi-Horizon Time-Series
• Microservice Architecture: FastAPI Backend (Port 8000) with Async ASGI Uvicorn Event Loop
• Edge Telemetry: MQTT Client (neon/water/hirakud/telemetry) with SQLite time-series persistence
```

---

## 🖥️ GLOBAL SHELL & SIDEBAR NAVIGATION (Visible Across All Screens)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🚀 NEON NATIONAL WATER INTELLIGENCE PLATFORM  [🔴 ACTIVE: 1] [🟡 PROPOSED: 6] [🟢 UPTIME: 99.8%] [PORT: 8000] │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Global Header Status Bar
1. **Title & Branding ("NEON NATIONAL WATER INTELLIGENCE PLATFORM")**:
   - *On-Screen*: Luminous cyan banner with national scope indicator.
   - *Real-World Representation*: Centralized Command & Control interface for the Ministry of Jal Shakti, Central Pollution Control Board (CPCB), and State Pollution Control Boards (SPCBs).
   - *Technical Origin*: `dashboard/app.py` line 124.

2. **`🔴 ACTIVE OPERATIONAL NODES: 1`**:
   - *On-Screen*: Crimson-bordered status pill indicating 1 active node.
   - *Real-World Representation*: The physical/virtual in-situ telemetry sonde deployed at the **Hirakud Reservoir inflow reach (Mahanadi River Basin, Odisha)**.
   - *Technical Origin*: Computed from `len(geo_data.get("active_node"))`.

3. **`🟡 PROPOSED EXPANSION ZONES: 6 BASINS`**:
   - *On-Screen*: Amber-bordered pill indicating 6 expansion river basins.
   - *Real-World Representation*: Strategic future deployment zones across India: Ganga (Kanpur), Yamuna (Delhi), Godavari (Rajahmundry), Krishna (Vijayawada), Narmada (Jabalpur), and Cauvery (Mettur Dam).
   - *Technical Origin*: Extracted from `data/geo/water_nodes.json`.

4. **`🟢 FLEET UPTIME: 99.8%`**:
   - *On-Screen*: Emerald-bordered metric badge.
   - *Real-World Representation*: Continuous availability of remote telemetry stations over cellular/satellite networks, accounting for battery/solar health and sensor link reliability.
   - *Technical Origin*: Calculated from packet reception ratio: $\text{Uptime} = \frac{\text{Successful Ingested Packets}}{\text{Total Expected Ingestion Intervals}} \times 100\%$.

5. **`Engine: Live FastAPI Microservice (Port 8000)`**:
   - *On-Screen*: Monospace indicator specifying backend connection status.
   - *Real-World Representation*: The REST API microservice orchestrating AI Models 1–5, isolating frontend rendering from compute-heavy inference.
   - *Technical Origin*: Direct HTTP health check to `http://localhost:8000/health`.

---

### 2. Left Sidebar: Operations Console & Mode Switcher

1. **Screen Navigator ("Navigate Platform")**:
   - *On-Screen*: Radio selection:
     - `Screen 1: National Deployment Map`
     - `Screen 2: Hirakud Digital Twin Node`
     - `Screen 3: AI Model Intelligence Center`
   - *Real-World Representation*: Tiered hierarchical operational command: Macro National GIS $\to$ Meso Catchment/Digital Twin $\to$ Micro AI/Chemical Diagnostics.
   - *Technical Origin*: Streamlit Session State controller (`st.session_state["nav_screen"]`).

2. **Operational Data Source Switcher ("Telemetry Source Mode")**:
   - *On-Screen*: Two mutually exclusive operational modes:
     - `📡 LIVE SENSOR MODE (Autonomous Stream)`: Ingests live continuous 5-second MQTT telemetry.
     - `🎛️ MANUAL SIMULATION MODE (SIH Sandbox)`: Provides manual sliders to simulate arbitrary sensor configurations and disaster scenarios.
   - *Technical Origin*: `dashboard/app.py` lines 180–210.

3. **`📡 LIVE SENSOR STREAM` Status Card**:
   - *On-Screen*: Dynamic glassmorphic HUD panel displaying:
     - `Node: HIRAKUD_NODE_001`
     - `Status: 🟢 Connected` (or `🟡 SENSOR DELAY` / `🔴 SENSOR OFFLINE`)
     - `Last Packet: HH:MM:SS UTC`
     - `Sampling: 5 sec • SQLite: Active`
   - *Technical Origin*: Ingests live state from `iot.mqtt_client.telemetry_manager.get_connection_status()`.

4. **Autonomous Scenario Controller**:
   - *On-Screen*: Dropdown selector (`Normal Baseline Stream`, `Acid Spill Contamination`, `Toxic Heavy Metal Waste`, `Eutrophication Spike`) + `📡 Set Scenario` and `🔄 Poll Live` buttons.
   - *Technical Origin*: Triggers `telemetry_manager.set_sensor_scenario(key)`, which dynamically alters the Gaussian drift distribution of `iot.autonomous_sensor.AutonomousSensorNode`.

5. **Hardware Failure Simulation**:
   - *On-Screen*: `⏸️ Stop Sensor` and `▶️ Resume` buttons.
   - *Real-World Representation*: Simulates solar battery depletion, cellular antenna blackout, or physical probe severance.
   - *Technical Origin*: Pauses/resumes the background thread in `iot/autonomous_sensor.py` to trigger the backend timeout state machine ($>30\text{s}$ warning, $>120\text{s}$ offline).

---

## 🗺️ SCREEN 1: NATIONAL GIS COMMAND CENTER

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🔍 National Water Monitoring Discovery & Search Console                                                │
│ [ e.g. Hirakud, Mahanadi, Ganga, Kanpur, Delhi, Godavari, Krishna, Narmada, Cauvery, Sambalpur...   ] │
├──────────────────────────────────────────────────────────────────────┬─────────────────────────────────┤
│                                                                      │ 📍 Monitoring Node Drawer       │
│  🗺️ National Water Quality Monitoring Topology (PyDeck WebGL)       │ 🔴 Hirakud Reservoir (ACTIVE)   │
│  • India-focused dark-matter basemap (22.5° N, 79.0° E, Zoom: 4.5)   │ • Lat: 21.534° N, Lon: 83.872° E │
│  • Real HydroRIVERS hydrological reaches (7 major river systems)     │ • Sensors: pH, DO, Turb, Cond...│
│  • 🔴 Red Operational Node: Hirakud Reservoir                         │ • [Open Twin] [Open AI Center]  │
│  • 🟠 Orange Proposed Nodes: Ganga, Yamuna, Godavari, Krishna...     ├─────────────────────────────────┤
│                                                                      │ 🏛️ Expansion Roadmap Table      │
│                                                                      │ 🛰️ GIS Transparency Checklist    │
└──────────────────────────────────────────────────────────────────────┴─────────────────────────────────┘
```

### UI Component Breakdown:
1. **Search & Discovery Console**:
   - *What is displayed*: Global search input with auto-suggestions.
   - *Real-World Representation*: Emergency search for water authorities to instantly locate any river basin, dam, intake, or sensor node during a spill.
   - *Technical Implementation*: String token parser filtering `data/geo/water_nodes.json`.

2. **PyDeck WebGL Geospatial Map**:
   - *What is displayed*: High-performance WebGL map rendered on Carto dark-matter tiles, featuring real HydroRIVERS line geometries for 7 major rivers, the glowing red active Hirakud node, and 6 orange proposed nodes.
   - *Real-World Representation*: India’s national hydrological river grid and monitoring node topology.
   - *Technical Implementation*: `dashboard/components/geospatial_map.py` (`build_national_deployment_deck`), combining `pdk.Deck` with `pdk.Layer("GeoJsonLayer")` for rivers and `pdk.Layer("ScatterplotLayer")` for sensor nodes. Zero artificial hand-drawn country polygons.

3. **Monitoring Node Intelligence Drawer (Right Column)**:
   - *What is displayed*: Detailed telemetry, physical coordinates, sensor sonde array status, and direct deep-link navigation buttons (`🚀 Open Digital Twin`, `🤖 Open AI Intelligence Center`).
   - *Real-World Representation*: Station telemetric dossier for the on-duty hydrological engineer.

4. **National Expansion Phasing Roadmap & GIS Transparency Checklist**:
   - *What is displayed*: Phased deployment roadmap table and sovereign GIS data verification checklist confirming Survey of India / Natural Earth boundary compliance.

---

## 🌊 SCREEN 2: HIRAKUD RESERVOIR DIGITAL TWIN COMMAND CENTER

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 📍 NEON Digital Twin Node: Hirakud Reservoir (Mahanadi River Basin)                                    │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 🌊 Sub-Surface In-Situ Physical Digital Twin (SVG Stratified Water Column & Sonde Depth: 4.2m)        │
│ [4.2m Sampling: 5s | pH: 7.42 | DO: 8.65 mg/L | Turbidity: 4.5 FNU | Cond: 280 µS/cm | Temp: 21.3°C]   │
├──────────────────────────────────────┬─────────────────────────────────────────────────────────────────┤
│ 📊 Real-Time Quality Scores          │ 🗺️ Mahanadi River Catchment Geography & Downstream Reach       │
│ • WQI Gauge: 85.0 / 100              │ • Hirakud Dam $\to$ Sambalpur Intake $\to$ Bargarh $\to$ Chiplima│
│ • Eco Health Gauge: 90.7 / 100       │ • Dynamic Plume Trajectory Trace                                │
├──────────────────────────────────────┴─────────────────────────────────────────────────────────────────┤
│ 🌊 Downstream Contamination Impact & Asset Exposure Intelligence                                       │
│ • Exposed Population: 1,415,000 Citizens | Intakes: 2 | Command: 85,000 Ha | Velocity: 1.8 m/s (6.48 km/h)│
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 📋 Exposed Downstream Infrastructure & Arrival Time Matrix (Table with Distances, Times & Actions)     │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 📜 Continuous Telemetry & AI Inference History (Expandable SQLite Database Table)                      │
│ 🚀 [Open AI Intelligence Center] (Primary Navigation Button)                                           │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### UI Component Breakdown:
1. **Sub-Surface In-Situ Physical Digital Twin**:
   - *What is displayed*: Interactive cross-sectional visualization of the reservoir water column showing thermal stratification layers (**Epilimnion**, **Thermocline**, **Hypolimnion / Benthic**), submerged sensor sonde suspended at $4.2\text{m}$, water depth markers, dynamic particle animation, and live parameter readout banner.
   - *Real-World Representation*: Sub-surface physical conditions at the Hirakud Dam reservoir intake.
   - *Technical Implementation*: `dashboard/components/futuristic_hud.py` (`render_digital_twin_svg`), rendering animated SVG/CSS elements with dynamic color shifts (e.g. acidic yellow, turbid brown, toxic red).

2. **Real-Time Quality Score Gauges**:
   - *What is displayed*: Two dual Plotly semicircular gauge charts:
     - **Water Quality Index (WQI)**: General physical-chemical quality score ($0\text{–}100$).
     - **Eco Health Index**: Aquatic biological ecosystem carrying capacity ($0\text{–}100$).
   - *Technical Implementation*: `create_gauge_figure()` using Plotly `go.Indicator`.

3. **Mahanadi Catchment Downstream Reach Map**:
   - *What is displayed*: Focused GIS map tracing the Mahanadi River from Hirakud Dam downstream past critical municipal drinking water intakes, agricultural canal gates, and industrial powerhouses.
   - *Technical Implementation*: PyDeck Scatterplot and Path layers linking coordinates: Hirakud Inflow $\to$ Sambalpur Municipal Intake ($4.8\text{ km}$) $\to$ Bargarh Canal Gate ($11.2\text{ km}$) $\to$ Chiplima Industrial Intake ($15.6\text{ km}$) $\to$ Cuttack Delta Abstraction ($240.0\text{ km}$).

4. **Downstream Asset Exposure & Arrival Time Matrix**:
   - *What is displayed*: 4 critical summary metric cards + interactive exposure table displaying:
     - **Asset Name & Category** (e.g. *Sambalpur Municipal Raw Water Intake #1*, Drinking Water).
     - **Distance from Spill**: $4.8\text{ km}$.
     - **Plume Arrival Time**: $44\text{ minutes}$ (Calculated via $t = d/v$ at river velocity $v = 1.8\text{ m/s}$).
     - **Population / Capacity**: $340,000\text{ users}$.
     - **Mandatory Action**: `TRIGGER RAW WATER INTAKE ISOLATION GATE`.
   - *Technical Origin*: `src/decision/decision_engine.py` hydrodynamic kinematics matrix.

5. **Continuous Telemetry & AI Inference History (SQLite Database)**:
   - *What is displayed*: Expandable table displaying the most recent 15 telemetry records persisted in `data/telemetry_history.db`.

---

## 🤖 SCREEN 3: AI MODEL INTELLIGENCE & DECISION CENTER

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🤖 NEON AI Model Intelligence & Decision Center                                                        │
│ ⚡ LIVE AI SYNTHESIS: Incident: Pristine Baseline | Severity: LOW | Status: SAFE | Confidence: 95.0%    │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 🔄 5-Stage AI Model Intelligence Pipeline Execution (Step-by-step Execution Flowchart)                 │
│ [Telemetry Active] ──► [M1: Anomaly Normal] ──► [M2: Risk SAFE] ──► [M3: Eco 90.7] ──► [M4: Forecast] │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1️⃣ MODEL 1: Multivariate Anomaly Detection Engine (Isolation Forest)                                    │
│ • Decision: 🟢 NORMAL BASELINE (Score: -0.1585) | Telemetry Covariance Table vs Pristine Reference     │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2️⃣ MODEL 2: Contamination Risk Classifier & TreeSHAP Explainability                                    │
│ • Predicted Risk Tier: 🟢 SAFE (95.0% Confidence)                                                      │
│ • TreeSHAP Local Feature Attribution Waterfall (Plotly Diverging Bar Chart)                            │
│ • Top Risk-Driving Variables (Feature Force Table: Feature, Value, SHAP Impact, Direction)             │
│ • 🔍 [SHAP PIPELINE DEBUG] (Expandable Raw JSON Drawer)                                                │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 3️⃣ MODEL 3: Biological Ecosystem Health Assessment Engine (Eco Health: 90.7 / 100)                     │
│ • Sub-Scores: Biodiversity: 90/100 | Tolerance: 85/100 | Trophic: 91/100 | Bioassay Stress: 100/100    │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 4️⃣ MODEL 4: 24-Hour Predictive Early Warning Forecaster                                                │
│ • 24h Projected Status: 🟡 WARNING / 🟢 SAFE | 24-Hour Dissolved Oxygen & Turbidity Trajectory Plot    │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 5️⃣ MODEL 5: AI Decision Support & Response Recommendation Engine                                       │
│ • Incident Classification: NOMINAL_BASELINE | Root-Cause Evidence Chain | Immediate Containment SOPs   │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### UI Component Breakdown:
1. **Live AI Operational Synthesis Status**:
   - *What is displayed*: High-visibility alert bar showing classified incident name, severity tier (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), fused final status, and model confidence percentage.
   - *Technical Origin*: Fused output of `backend/environmental_engine.py` and `src/decision/decision_engine.py`.

2. **5-Stage AI Model Execution Flow**:
   - *What is displayed*: Horizontal execution pipeline connecting Telemetry $\to$ M1 Anomaly $\to$ M2 Risk $\to$ M3 Eco Health $\to$ M4 Forecaster $\to$ M5 Decision Support.
   - *Technical Origin*: `dashboard/app.py` (`render_pipeline_html`).

3. **Model 1 Expander (Isolation Forest Covariance Envelope)**:
   - *What is displayed*: Anomaly decision badge (`🟢 NORMAL BASELINE` vs `🔴 ANOMALY DETECTED`), isolation score, and 5-channel covariance analysis table comparing observed telemetry against pristine reference baselines.

4. **Model 2 Expander (Random Forest & TreeSHAP Waterfall)**:
   - *What is displayed*:
     - Risk Tier Badge: `🟢 SAFE` / `🟡 WARNING` / `🔴 CRITICAL`.
     - **TreeSHAP Local Feature Attribution Waterfall**: Diverging horizontal bar chart displaying exact signed mathematical force contributions (Crimson `#EF4444` for risk-increasing, Emerald `#10B981` for protective).
     - **AI Reasoning Explanation**: Plain-English narrative synthesized from top SHAP drivers.
     - **Feature Force Analysis Table**: 4-column breakdown: `Feature Name`, `Sensor Value`, `SHAP Contribution`, and `Risk Direction`.
     - **`🔍 SHAP PIPELINE DEBUG`**: Expandable raw JSON inspection drawer.

5. **Model 3 Expander (Biological Ecosystem Health Engine)**:
   - *What is displayed*: Composite Eco Health Index metric ($90.7/100$, `🟢 Excellent Pristine Ecosystem`) + 4 sub-indices: **Biodiversity (90/100)**, **Pollution Tolerance (85/100)**, **Trophic Balance (91/100)**, and **Bioassay Stress (100/100)**.

6. **Model 4 Expander (Predictive 24-Hour Forecaster)**:
   - *What is displayed*: Projected future status + Plotly trajectory timeline plotting observed Dissolved Oxygen and Turbidity into future $+6\text{h}, +12\text{h}, +24\text{h}$ confidence envelopes. If an acute shock occurs, displays **"⚠️ EMERGENCY OVERRIDE ACTIVE"**.

7. **Model 5 Expander (Decision Support & Response Engine)**:
   - *What is displayed*: Classified incident type, statutory evidence chain (BIS 10500 standard exceedances), immediate containment directives, and downstream asset protection protocols.

---

# 🏗️ PART 2: TECHNICAL ARCHITECTURE BEHIND EACH SCREEN

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              SYSTEM DATA FLOW PER SCREEN                               │
│                                                                                        │
│  [SCREEN 1: GIS]         data/geo/water_nodes.json + india_rivers.geojson ──► PyDeck   │
│  [SCREEN 2: TWIN]        iot/mqtt_client.py (5s packet) ──► SVG Canvas + Kinematics    │
│  [SCREEN 3: AI CENTER]   backend/model_loader.py (M1-M5 Pipeline) ──► Plotly & HUD     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Screen 1 (GIS View)**:
   - Evaluates GeoJSON coordinate streams using WebGL vertex shaders in PyDeck.
   - River lines are mapped as 3D vector paths with dynamic stroke width and opacity; active nodes use real GPS coordinates `[21.534, 83.872]`.
2. **Screen 2 (Digital Twin)**:
   - Generates dynamic SVG vectors where water turbidity controls layer opacity ($\alpha \propto \text{Turbidity}/100$), dissolved oxygen controls benthic bio-particle speed, and pH shifts color gradient from pristine cyan (`#00F0FF`) to acidic amber-yellow (`#FBBF24`).
3. **Screen 3 (AI Intelligence Center)**:
   - Directly executes the in-memory Python inference engine (`backend.model_loader.engine.predict()`), executing scikit-learn tree traversals in sub-millisecond CPU time.

---

# 🧠 PART 3: AI/ML ENGINEERING CONNECTED DIRECTLY TO UI

### 1. Model 1 (Isolation Forest Anomaly Isolation):
- **UI Element**: Anomaly Score `Score: -0.1585` and `NORMAL BASELINE` badge.
- **Mathematical Formula**:
  $$s(x, n) = 2^{-\frac{\mathbb{E}(h(x))}{c(n)}}, \quad c(n) = 2\ln(n-1) + 0.5772156649 - \frac{2(n-1)}{n}$$
- **UI Behavior**: When $s(x, n) > 0.0$, badge turns crimson `🔴 ANOMALY DETECTED`.

### 2. Model 2 (Balanced Random Forest & TreeSHAP):
- **UI Element**: Waterfall chart with green/red bars and `Classification Confidence: 95.0%`.
- **Mathematical Formula**:
  $$\phi_i(x) = \sum_{m=1}^{M} \frac{1}{M} \sum_{u \in \text{path}(x, T_m)} \left[ \mathbb{E}[f(x) \mid x \in \text{node}_{\text{child}}] - \mathbb{E}[f(x) \mid x \in \text{node}_{\text{parent}}] \right] \cdot \mathbb{I}(\text{split\_feat}(u) = i)$$
- **UI Behavior**: If an acid spill occurs, the pH bar extends negatively into the driver axis while conductance extends positively, generating the narrative: *"Warning status driven by elevated conductance and water pH."*

### 3. Model 3 (Biological Ecosystem Health Index):
- **UI Element**: `Composite Eco Health Index: 90.7 / 100`.
- **Mathematical Formula**:
  $$\text{Eco Health Index} = 0.35\cdot S_{\text{bio}} + 0.25\cdot S_{\text{tol}} + 0.20\cdot S_{\text{trophic}} + 0.20\cdot S_{\text{stress}}$$

### 4. Model 4 (Time-Series Trajectory Forecaster):
- **UI Element**: $+6\text{h}, +12\text{h}, +24\text{h}$ line chart.
- **Mathematical Formula**:
  $$\hat{y}_{t+k} = \mathbf{w}_k^T \mathbf{X}_{\text{lag}} + b_k, \quad \mathbf{X}_{\text{lag}} = [y_t, y_{t-1}, y_{t-2}, y_{t-3}, \sin(\omega d), \cos(\omega d)]$$

### 5. Model 5 (Decision Support & Hydrodynamics):
- **UI Element**: `Plume Arrival Time: 44 minutes` for Sambalpur Intake.
- **Mathematical Formula**:
  $$t_{\text{arrival}} = \frac{d_{\text{asset}}}{v_{\text{river}}} = \frac{4.8\text{ km}}{1.8\text{ m/s} \times 3.6} = 0.74\text{ hours} = 44.4\text{ minutes}$$

---

# 📡 PART 4: IOT & BACKEND ENGINEERING CONNECTED TO UI

```
Autonomous Virtual Sonde (iot/autonomous_sensor.py)
                 │
                 ▼ MQTT Topic: neon/water/hirakud/telemetry (5-sec stream)
       MQTT Ingestion Client (iot/mqtt_client.py)
                 │
                 ├─► Parameter Range Validation
                 ├─► State Machine (🟢 Connected / 🟡 Delay / 🔴 Offline)
                 ├─► Auto-trigger Models 1-5
                 └─► SQLite Ingestion (data/telemetry_history.db)
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   FastAPI Microservice              Streamlit Dashboard
(/telemetry/live, /telemetry/status) (📡 LIVE SENSOR MODE)
```

1. **Why Port 8000 is displayed**:
   - Indicates the FastAPI microservice running asynchronously on port 8000, decoupled from the Streamlit UI server (running on port 8501).
2. **Connectivity State Machine**:
   - $\Delta t \le 30\text{s}$: 🟢 `Connected` (Emerald `#10B981`)
   - $30\text{s} < \Delta t \le 120\text{s}$: 🟡 `SENSOR DELAY` (Amber `#F59E0B`)
   - $\Delta t > 120\text{s}$: 🔴 `SENSOR OFFLINE` (Crimson `#EF4444`)
3. **SQLite Telemetry History**:
   - Ingests every 5-second packet into `data/telemetry_history.db`, supporting the expandable table in Screen 2.

---

# ❓ PART 5: COMPREHENSIVE JUDGE Q&A FROM EVERY UI ELEMENT

#### Q1: [Judge points to "Fleet Uptime 99.8%"] What does this number mean and how is it monitored?
- **Answer**: *"Fleet Uptime represents the percentage of expected 5-second telemetry intervals successfully received without packet dropout across our sensor grid. It is computed in `iot/mqtt_client.py` as $\frac{\text{Received Packets}}{\text{Expected Packets}} \times 100\%$. In real deployment, it tracks cellular signal stability and solar battery health."*

#### Q2: [Judge points to "TreeSHAP Local Feature Attribution Waterfall"] Why is this bar chart red and green?
- **Answer**: *"This is our local TreeSHAP explainability decomposition. Green bars represent protective parameters that keep water in the SAFE tier (e.g. high dissolved oxygen and low nitrogen). Red bars represent risk-increasing factors (e.g. elevated conductivity or abnormal pH). It proves to CPCB regulators exactly which chemical parameter drove the AI's risk classification."*

#### Q3: [Judge points to Sub-Surface Digital Twin in Screen 2] How is this different from a video animation?
- **Answer**: *"This is not a static video; it is a code-driven physics visualization rendered dynamically from live sensor telemetry. If you inject an acid spill, the water color in the SVG canvas turns yellow, the chemical sonde depth readout reflects live telemetry, and the benthic bioassay survival particles disperse, reflecting real-time physical conditions."*

#### Q4: [Judge points to "Plume Arrival Time: 44 mins"] How did you calculate this arrival time?
- **Answer**: *"We use 1D hydrodynamic advection kinematics $t = d/v$. The Sambalpur Municipal Water Intake is $4.8\text{ km}$ downstream from the Hirakud Dam inflow node. At a calibrated river flow velocity of $1.8\text{ m/s}$ ($6.48\text{ km/h}$), the plume takes exactly $44.4\text{ minutes}$ to arrive, giving municipal authorities a precise window to lock drinking water sluice gates."*

#### Q5: [Judge points to "Anomaly Score: -0.1585"] Why is this score negative?
- **Answer**: *"Model 1 uses Isolation Forest. The decision function outputs negative scores for data points deep inside the pristine baseline envelope (requiring many random partitions to isolate). Values $> 0.0$ indicate anomalous outliers that were isolated near the root of the tree."*

#### Q6: [Judge points to "Port 8000" in header] Why do you need both Port 8000 and Port 8501?
- **Answer**: *"Port 8501 runs our Streamlit frontend dashboard for user interaction. Port 8000 runs our standalone FastAPI asynchronous microservice. This decouples user interface rendering from the high-throughput AI inference engine and external IoT hardware gateways."*

---

# 🏛️ PART 6: REAL-WORLD INDUSTRIAL DEPLOYMENT INTERPRETATION

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        GOVERNMENT REGULATORY WORKFLOW                                  │
│                                                                                        │
│  1. In-Situ Sonde flags chemical shock in < 5 seconds                                  │
│  2. Model 5 auto-calculates travel time to downstream city intake                      │
│  3. System triggers automated SMS/Webhook to Municipal Sluice Gate Operator            │
│  4. Immutable SQLite/Blockchain audit record generated for SPCB legal prosecution     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **For Central Pollution Control Board (CPCB)**:
   - Provides real-time automated compliance auditing across all 311 polluted river stretches in India, eliminating the 7–14 day laboratory testing delay.
2. **For State Pollution Control Boards (SPCBs)**:
   - Generates legally enforceable Section 33A closure notices with cryptographic evidence chains and TreeSHAP attribution.
3. **For Municipal Water Treatment Plants**:
   - Guarantees zero-delay intake lockouts, protecting millions of citizens from consuming contaminated river water.

---

*This master document is fully aligned with your live application and screenshots. You are completely prepared for the SIH Grand Finale!* 🚀
