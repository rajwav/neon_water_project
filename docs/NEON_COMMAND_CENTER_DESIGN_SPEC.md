# NEON Unified GIS Map-First National Water Intelligence Command Center
## Detailed Operational Wireframes & Interaction Design Specification

**Role**: Lead Product Designer & Principal UX Architect  
**Platform Version**: v6.0-Unified-Command-Center  
**Status**: Detailed Wireframes & Design Blueprint (Awaiting Approval to Code)  

---

## 1. The Unified Operational Decision Framework

The entire interface is built strictly around the **4 Operational Questions**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               OPERATIONAL DECISION APEX                                 │
├───────────────────────────────────┬─────────────────────────────────────────────────────┤
│ 1. WHERE IS THE PROBLEM?          │ Geospatial Coordinate, River Basin, Reach Order,    │
│                                   │ Station Node, & Downstream Exposure Distance        │
├───────────────────────────────────┼─────────────────────────────────────────────────────┤
│ 2. HOW SEVERE IS IT?              │ 🔴 CRITICAL / 🟠 HIGH / 🟡 WARNING / 🟢 SAFE        │
│                                   │ with AI Multi-Model Fusion Confidence (0-100%)      │
├───────────────────────────────────┼─────────────────────────────────────────────────────┤
│ 3. WHY DID AI DETECT THIS?        │ Multi-Model Evidence Chain + TreeSHAP Attributions  │
│                                   │ + Probabilistic Root Cause Field Diagnostics        │
├───────────────────────────────────┼─────────────────────────────────────────────────────┤
│ 4. WHAT ACTION MUST AUTHORITIES   │ 🚨 Tier 1: Immediate Tactical Response (0-2h)       │
│    TAKE IMMEDIATELY?              │ ⏱️ Tier 2: Short-Term Catchment Containment (2-24h) │
│                                   │ 🏛️ Tier 3: Long-Term Watershed Prevention Policy    │
└───────────────────────────────────┴─────────────────────────────────────────────────────┘
```

---

## 2. Master Navigation & Fluid Drill-Down Journey

Instead of disconnected, siloed pages, NEON uses a **Single Unified GIS Map-First Command Canvas** with a hierarchical spatial breadcrumb and adaptive slide-over intelligence panels:

$$\mathbf{National\ Map\ (Macro)} \xrightarrow{\text{Select Basin}} \mathbf{Basin\ Reach\ (Meso)} \xrightarrow{\text{Select Node}} \mathbf{Digital\ Twin\ (Micro)} \xrightarrow{\text{Escalate}} \mathbf{Crisis\ War\ Room}$$

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ [NEON COMMAND CENTER]  🌐 National Fleet > 🌊 Mahanadi Basin > 📍 Hirakud Node > 🚨 HazMat │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. High-Fidelity Wireframes

### Wireframe 1: National Map View (Macro-Scale Fleet Surveillance)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 🛰️ NEON WATER INTELLIGENCE PLATFORM :: NATIONAL COMMAND CONSOLE           [LIVE TELEMETRY]│
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ [📊 2,547 Active Nodes] [💧 National WQI: 78.4/100] [🔴 3 Critical] [🟠 12 Warning] [🟢 2,532 Safe] │
├────────────────────────────────────────────────────────┬────────────────────────────────┤
│                                                        │ 🚨 ACTIVE INCIDENT QUEUE       │
│                                                        │ 🔴 Mahanadi (Hirakud): Acid    │
│                 GEOSPATIAL FLEET MAP                   │ 🔴 Ganga (Kanpur): Toxic Metal │
│               (Hardware-Accelerated WebGL)             │ 🔴 Godavari (Rajahmundry): Hyp │
│                                                        │ 🟠 Yamuna (Delhi): Eutrophic   │
│           [ 🟢 ]                 [ 🔴 Ganga Basin ]    ├────────────────────────────────┤
│                    [ 🟠 ]                              │ 🌊 BASIN HEALTH RANKINGS       │
│                                                        │ 1. Narmada Basin: 92.4 WQI     │
│       [ 🟢 Narmada ]              [ 🔴 Mahanadi ]      │ 2. Cauvery Basin: 86.1 WQI     │
│                                                        │ 3. Krishna Basin: 81.0 WQI     │
│                     [ 🔴 Godavari ]                    │ 4. Mahanadi Basin: 42.1 (RISK) │
│                                                        │ 5. Ganga Basin: 38.5 (CRIT)    │
│           [ 🟢 Krishna ]                               ├────────────────────────────────┤
│                                                        │ 🔬 AI FLEET DIAGNOSTICS        │
│                     [ 🟢 Cauvery ]                     │ - 99.4% Sonde Telemetry Uptime │
│                                                        │ - 0 Sensor Drift Faults        │
├────────────────────────────────────────────────────────┴────────────────────────────────┤
│ 💡 CLICK ANY RIVER BASIN OR INCIDENT NODE TO ENTER TACTICAL BASIN COMMAND VIEW           │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Wireframe 2: Basin Command View (Meso-Scale Catchment Topology)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 🌐 National > 🌊 MAHANADI RIVER BASIN COMMAND CONSOLE [Basin Area: 141,600 km² • Order: 7]│
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ [📍 18 Basin Stations] [⚠️ Basin Risk: HIGH (82%)] [🌊 Discharge: 1,420 m³/s] [⏱️ Flow: 1.8 m/s]│
├────────────────────────────────────────────────────────┬────────────────────────────────┤
│                                                        │ 🎯 CATCHMENT RISK CASCADE      │
│               RIVER REACH TOPOLOGY MAP                 │                                │
│                                                        │ [Station 01: Sambalpur Upstr]  │
│  [Station 01: 🟢 7.4 pH]                               │  └─ Status: 🟢 SAFE (88 WQI)   │
│         \                                              │                                │
│          \  (Flow Vector ──► 1.8 m/s)                  │ [Station 02: Hirakud Inflow]   │
│           ▼                                            │  └─ Status: 🔴 CRITICAL        │
│      [Station 02: 🔴 2.8 pH (ACID PLUME DETECTED)]     │  └─ Incident: ACID SPILL       │
│           │                                            │                                │
│           ▼ ── Contaminant Wave Front ──► (2.4h travel)│ [Station 03: Bargarh Canal]    │
│      [Station 03: 🟡 Warning Horizon (T-minus 2.1h)]   │  └─ Status: 🟡 AT-RISK IN 2.1h │
│           │                                            │                                │
│           ▼                                            │ [Station 04: Cuttack Delta]    │
│      [Station 04: 🟢 Baseline Nominal]                 │  └─ Status: 🟢 BASELINE        │
├────────────────────────────────────────────────────────┴────────────────────────────────┤
│ 🔬 UPSTREAM ──► DOWNSTREAM SYNCHRONIZED TELEMETRY TIMELINE (Wave Arrival Forecaster)    │
│ Sambalpur (00:00) ──► Hirakud (00:30 Spike) ──► Canal Intake (02:45 Projected Plume)    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Wireframe 3: Node Digital Twin View (Micro-Scale Physical Sensor & AI Layer)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 🌐 National > 🌊 Mahanadi > 📍 HIRAKUD RESERVOIR NODE #002 [Digital Twin Telemetry Console]│
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. WHERE: Hirakud Inflow (21.52° N, 83.87° E)  •  2. SEVERITY: 🔴 CRITICAL (94.2% Conf) │
├────────────────────────────┬────────────────────────────────────────────────────────────┤
│ 🌊 DYNAMIC DIGITAL TWIN    │ 🤖 5-STAGE AI MODEL PIPELINE                               │
│ (Real-Time Sub-Surface)    │                                                            │
│ ┌────────────────────────┐ │ 1. Model 1 (Isolation Forest): 🔴 OUTLIER (+0.2140 Score) │
│ │ ~~~ Water Surface ~~~  │ │ 2. Model 2 (Balanced RF):      🔴 CRITICAL (94.2% Prob)    │
│ │  [🟡 Buoy Sonde #002]  │ │ 3. Model 3 (Bio Health):       🔴 32.4/100 (COLLAPSE RISK) │
│ │       │                │ │ 4. Model 4.1 (Forecaster):     ⚠️ EMERGENCY OVERRIDE       │
│ │       ▼ Depth: 4.2m    │ │ 5. Model 5 (Decision Support): 🔴 ACIDIFICATION INFLUX     │
│ │   [🔴 Acid Plume]      │ ├────────────────────────────────────────────────────────────┤
│ │  ════════════════════  │ │ 📊 SHAP XAI EXPLAINABILITY (Why AI Detected This)          │
│ └────────────────────────┘ │ pH (2.80) ───────────────► [+0.48 Impact on Critical Risk] │
│ Telemetry Readout:         │ Conductance (1450 µS/cm) ──► [+0.26 Impact on Critical Risk] │
│ • pH: 2.80 (Nominal: 7.4)  │ Dissolved O₂ (4.50 mg/L) ──► [+0.14 Impact on Critical Risk] │
│ • DO: 4.50 mg/L            │ Turbidity (48.0 FNU) ─────► [+0.08 Impact on Critical Risk] │
│ • SpCond: 1,450 µS/cm      │ Summary: Severe acidification with elevated ionic leaching.│
├────────────────────────────┴────────────────────────────────────────────────────────────┤
│ 🚨 MODEL 5 APEX DECISION ACTION CENTER                                                  │
│ ┌──────────────────────────┬──────────────────────────┬───────────────────────────────┐ │
│ │ 🚨 IMMEDIATE (0–2 HOURS) │ ⏱️ SHORT-TERM (2–24 HOURS)│ 🏛️ LONG-TERM PREVENTION       │ │
│ │ 1. SHUTDOWN RAW INTAKE   │ 1. Trace metal screening │ 1. Construct limestone drains │ │
│ │ 2. Dispatch HazMat Lime  │ 2. Triangulate pipeline  │ 2. Enforce ZLD gate locks     │ │
│ │ 3. Notify Downstream     │                          │                               │ │
│ └──────────────────────────┴──────────────────────────┴───────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Wireframe 4: Emergency Crisis War Room View (HazMat Tactical Incident Control)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 🚨 INCIDENT WAR ROOM :: ACTIVE CHEMICAL SPILL & ACIDIFICATION CRISIS [INCIDENT #2026-08A]│
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 🔴 SEVERITY: CRITICAL  •  📍 LOCATION: Mahanadi Basin (Hirakud)  •  ⏱️ TIME ELAPSED: 18m │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. INCIDENT PROVENANCE & EVIDENCE CHAIN (Why AI Escalated to Crisis):                   │
│    📌 Water pH (2.80) severely violates EPA aquatic baseline envelope (< 4.5).          │
│    📌 Model 1 confirms extreme multivariate anomaly (+0.2140) in sensor covariance.     │
│    📌 Model 3 projects benthic macroinvertebrate mortality if uncontained within 2h.   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. DOWNSTREAM ASSET EXPOSURE MATRIX (What is at Risk):                                  │
│    ⚠️ Sambalpur Municipal Water Intake #1 (Distance: 4.8 km • Time to Impact: 45 min)   │
│    ⚠️ Bargarh Irrigation Canal Sluice Gate (Distance: 11.2 km • Time to Impact: 1h 45m) │
│    ⚠️ Protected Inland Fishery Reach Zone B (Distance: 16.0 km • Time to Impact: 2h 30m)│
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. MANDATORY OPERATIONAL COMMAND EXECUTION CHECKLIST:                                   │
│    [X] ⚡ STEP 1: TRIGGER IMMEDIATE INTAKE SHUTDOWN (Automated telemetry sluice lock)   │
│    [ ] ⚡ STEP 2: DISPATCH HAZMAT ALKALINE NEUTRALIZATION UNIT (Lime dosing at weir)    │
│    [ ] ⚡ STEP 3: ISSUE DOWNSTREAM PUBLIC HEALTH & WATER UTILITY EMERGENCY ADVISORY    │
│    [ ] 🔍 STEP 4: MOBILIZE MOBILE ICP-MS LAB FOR TRACE HEAVY METAL ION SCREENING        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ [ 📄 EXPORT FORENSIC PDF BRIEFING ]    [ 📢 BROADCAST EMERGENCY ALERT ]   [ 🔄 RE-EVAL ] │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Interaction & Implementation Architecture

1. **Stateful Spatial Context Manager**:
   - `st.session_state["spatial_level"]`: `"NATIONAL"`, `"BASIN"`, `"NODE"`, `"WAR_ROOM"`.
   - `st.session_state["selected_basin"]`: `"Mahanadi"`, `"Ganga"`, `"Godavari"`, etc.
   - `st.session_state["selected_node"]`: `"HIRAKUD_002"`, `"WOKWI_IOT"`, etc.
2. **Pydeck Hardware-Accelerated Viewport**:
   - Camera coordinates and zoom smoothly adjust when switching between National ($Z=4$), Basin ($Z=8$), and Station Node ($Z=14$).
3. **Zero Backend Modifications**:
   - Fully compatible with current FastAPI `/predict` schema and verified 29/29 regression tests.
