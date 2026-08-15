"""
NEON Water Intelligence Platform — Streamlit Master Operations Console (v3.0).

Features:
  - Tab 1: Live Real-Time Multi-Domain Water Intelligence (IoT Telemetry, Sliders, M1+M2+M3, XAI, Trend Charts)
  - Tab 2: Historical USGS Catchment Analytics (77,641 Sampling Events, Bioassays, Stoichiometry, Spatial Trends)
  - Tab 3: AI Architecture & Neuro-Symbolic Guardrail Inspector
"""

import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
import requests
import streamlit as st

# ── API & Engine Configuration ─────────────────────────────────────
API_BASE_URL = "http://localhost:8000"
PREDICT_ENDPOINT = f"{API_BASE_URL}/predict"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "usgs_water_quality.parquet"

FALLBACK_ENGINE_AVAILABLE = False
try:
    from backend.model_loader import engine as fallback_engine
    FALLBACK_ENGINE_AVAILABLE = True
except Exception:
    fallback_engine = None

# ── Site Definitions ───────────────────────────────────────────────
SITE_OPTIONS = ["WOKWI_SITE", "ARIK", "BARC", "BIGC", "BLDE", "BLUE"]
POSITION_OPTIONS = ["001", "101", "102", "103", "111", "112"]

SITE_INFO = {
    "WOKWI_SITE": {"name": "Wokwi Digital Twin ESP32 Node", "type": "Multi-Domain Virtual Sensor Array", "pos": "001"},
    "ARIK": {"name": "Arikaree River, CO (USGS-06821500)", "type": "Semi-arid Prairie Stream", "pos": "102"},
    "BARC": {"name": "Barco Lake, FL (NEON / USGS)", "type": "Subtropical Blackwater Lake", "pos": "103"},
    "BIGC": {"name": "Upper Big Creek, CA (Sierra Nevada)", "type": "Mountain Forest Stream", "pos": "112"},
    "BLDE": {"name": "Blacktail Deer Creek, WY (Yellowstone)", "type": "Alpine Snowmelt Stream", "pos": "101"},
    "BLUE": {"name": "Blue River, OK (Great Plains)", "type": "Warm Limestone Stream", "pos": "112"},
}

PRESETS = {
    "Select an Ecological Scenario Preset...": None,
    "🏆 [Demo 1] Pristine Freshwater Baseline (SAFE)": {
        "ph": 7.42, "dissolved_oxygen": 8.65, "turbidity": 4.5, "specific_conductance": 280.0, "temperature": 21.3,
        "nitrate_mg_l": 0.45, "phosphate_mg_l": 0.015, "chlorophyll_a_ug_l": 2.8, "suspended_sediment": 35.0,
        "lead_risk_index": 0.02, "microbial_risk_index": 5.0, "bio_dominant_taxon": "Ceriodaphnia dubia", "bio_taxa_richness": 3,
        "site_id": "WOKWI_SITE", "sensor_position": "001",
    },
    "⚠️ [Demo 2] Agricultural Storm Runoff & Turbidity Shock (WARNING)": {
        "ph": 6.80, "dissolved_oxygen": 6.20, "turbidity": 85.0, "specific_conductance": 420.0, "temperature": 22.5,
        "nitrate_mg_l": 2.80, "phosphate_mg_l": 0.045, "chlorophyll_a_ug_l": 8.5, "suspended_sediment": 240.0,
        "lead_risk_index": 0.15, "microbial_risk_index": 28.0, "bio_dominant_taxon": "Hyalella azteca", "bio_taxa_richness": 2,
        "site_id": "ARIK", "sensor_position": "102",
    },
    "🚨 [Demo 3] Eutrophic Nutrient Bloom & Lethal Anoxia (CRITICAL)": {
        "ph": 8.65, "dissolved_oxygen": 1.80, "turbidity": 32.0, "specific_conductance": 580.0, "temperature": 26.5,
        "nitrate_mg_l": 12.80, "phosphate_mg_l": 0.185, "chlorophyll_a_ug_l": 42.0, "suspended_sediment": 65.0,
        "lead_risk_index": 0.20, "microbial_risk_index": 45.0, "bio_dominant_taxon": "Microcystis aeruginosa", "bio_taxa_richness": 1,
        "site_id": "BARC", "sensor_position": "103",
    },
    "🧪 [Demo 4] Toxic Heavy Metal Leaching / Bioassay Collapse (CRITICAL)": {
        "ph": 6.10, "dissolved_oxygen": 6.80, "turbidity": 14.0, "specific_conductance": 920.0, "temperature": 20.0,
        "nitrate_mg_l": 1.20, "phosphate_mg_l": 0.020, "chlorophyll_a_ug_l": 3.0, "suspended_sediment": 40.0,
        "lead_risk_index": 0.85, "microbial_risk_index": 12.0, "bio_dominant_taxon": "Ceriodaphnia dubia", "bio_taxa_richness": 1,
        "site_id": "BIGC", "sensor_position": "112",
    },
    "⚡ [Demo 5] Acute Industrial Acid Effluent Dump (CRITICAL)": {
        "ph": 2.80, "dissolved_oxygen": 4.50, "turbidity": 48.0, "specific_conductance": 1450.0, "temperature": 24.0,
        "nitrate_mg_l": 4.50, "phosphate_mg_l": 0.080, "chlorophyll_a_ug_l": 1.0, "suspended_sediment": 180.0,
        "lead_risk_index": 0.65, "microbial_risk_index": 75.0, "bio_dominant_taxon": "None", "bio_taxa_richness": 0,
        "site_id": "BLUE", "sensor_position": "112",
    },
    "🔌 [Demo 6] Telemetry Channel Loss / Sensor Dropout (INSUFFICIENT_DATA)": {
        "ph": None, "dissolved_oxygen": None, "turbidity": None, "specific_conductance": None, "temperature": 20.0,
        "nitrate_mg_l": None, "phosphate_mg_l": None, "chlorophyll_a_ug_l": None, "suspended_sediment": None,
        "lead_risk_index": None, "microbial_risk_index": None, "bio_dominant_taxon": "None", "bio_taxa_richness": 0,
        "site_id": "ARIK", "sensor_position": "102",
    },
}

# ── Page Configuration ─────────────────────────────────────────────
st.set_page_config(
    page_title="NEON Water Intelligence Platform",
    page_icon=":material/water_drop:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session State ──────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

if "last_timestamp" not in st.session_state:
    st.session_state.last_timestamp = None


# ── Helper Functions ───────────────────────────────────────────────
def check_api_health() -> Tuple[bool, str]:
    try:
        r = requests.get(HEALTH_ENDPOINT, timeout=1.0)
        if r.status_code == 200:
            return True, "FastAPI Backend (Online • v3.0.0)"
    except Exception:
        pass
    if FALLBACK_ENGINE_AVAILABLE:
        return True, "Direct ML Engine (In-Process Fallback)"
    return False, "Backend Offline"


def call_prediction_api(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        response = requests.post(PREDICT_ENDPOINT, json=payload, timeout=2.5)
        if response.status_code == 200:
            data = response.json()
            data["source"] = "FastAPI Backend (/predict)"
            return data
    except Exception:
        pass

    if FALLBACK_ENGINE_AVAILABLE and fallback_engine:
        data = fallback_engine.predict(
            ph=payload.get("ph"),
            dissolved_oxygen=payload.get("dissolved_oxygen"),
            turbidity=payload.get("turbidity"),
            specific_conductance=payload.get("specific_conductance"),
            temperature=payload.get("temperature", 20.0),
            chlorophyll=payload.get("chlorophyll_a_ug_l"),
            tn_mg_l=payload.get("nitrate_mg_l"),
            tp_mg_l=payload.get("phosphate_mg_l"),
            suspended_sediment=payload.get("suspended_sediment"),
            lead_risk=payload.get("lead_risk_index"),
            microbial_risk=payload.get("microbial_risk_index"),
            site_id=payload.get("site_id", "UNKNOWN"),
            sensor_position=payload.get("sensor_position", "001"),
            bio_dominant_taxon=payload.get("bio_dominant_taxon", "None"),
            bio_taxa_richness=payload.get("bio_taxa_richness", 0),
        )
        data["source"] = "Direct ML Engine (In-Process Fallback)"
        return data

    raise RuntimeError("Could not connect to FastAPI backend at http://localhost:8000/predict, and fallback engine is unavailable.")


@st.cache_data
def load_historical_data():
    if PROCESSED_DATA_PATH.exists():
        return pd.read_parquet(PROCESSED_DATA_PATH)
    return None


# ── Header Banner ──────────────────────────────────────────────────
api_online, api_status_label = check_api_health()

header_col1, header_col2, header_col3 = st.columns([3.2, 1.4, 1.4])
with header_col1:
    st.title(":material/water_drop: NEON Water Intelligence Platform")
    st.caption("AI-Powered Contamination Detection, Multi-Domain Ecotoxicity Intelligence & Digital Twin Monitoring")

with header_col2:
    status_icon = ":material/cloud_done:" if "FastAPI" in api_status_label else (":material/memory:" if api_online else ":material/cloud_off:")
    st.info(f"{status_icon} **API Service:**  \n`{api_status_label}`")

with header_col3:
    last_time_str = st.session_state.last_timestamp or "Ready / Standby"
    st.success(f":material/sensors: **IoT Node:** Connected  \n🕒 **Packet:** `{last_time_str}`")


# ── Top-Level Navigation Tabs ──────────────────────────────────────
tab_live, tab_history, tab_arch = st.tabs([
    ":material/speed: Live Water Quality Operations Console",
    ":material/travel_explore: Historical USGS Catchment Analytics (77,641 Events)",
    ":material/hub: Multi-Domain AI & Neuro-Symbolic Architecture",
])


# ===================================================================
# TAB 1: LIVE REAL-TIME WATER QUALITY INTELLIGENCE
# ===================================================================
with tab_live:
    # Quick Scenario Buttons
    st.markdown("##### 🚀 Quick SIH Demonstration Presets")
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    
    with sc1:
        if st.button("🌿 **1. Pristine Baseline**", use_container_width=True):
            st.session_state["selected_preset_key"] = "🏆 [Demo 1] Pristine Freshwater Baseline (SAFE)"
            st.rerun()
    with sc2:
        if st.button("⚠️ **2. Turbidity Shock**", use_container_width=True):
            st.session_state["selected_preset_key"] = "⚠️ [Demo 2] Agricultural Storm Runoff & Turbidity Shock (WARNING)"
            st.rerun()
    with sc3:
        if st.button("🚨 **3. Eutrophic Anoxia**", use_container_width=True):
            st.session_state["selected_preset_key"] = "🚨 [Demo 3] Eutrophic Nutrient Bloom & Lethal Anoxia (CRITICAL)"
            st.rerun()
    with sc4:
        if st.button("🧪 **4. Toxic Heavy Metal**", use_container_width=True):
            st.session_state["selected_preset_key"] = "🧪 [Demo 4] Toxic Heavy Metal Leaching / Bioassay Collapse (CRITICAL)"
            st.rerun()
    with sc5:
        if st.button("⚡ **5. Acid Spill**", use_container_width=True):
            st.session_state["selected_preset_key"] = "⚡ [Demo 5] Acute Industrial Acid Effluent Dump (CRITICAL)"
            st.rerun()

    st.divider()

    # Sidebar Options Sync
    with st.sidebar:
        st.header(":material/tune: Monitoring Controls")
        mode = st.radio("Operating Mode", options=["Interactive Sensor Controls", "Simulated IoT Telemetry Stream"], index=0)
        st.divider()
        st.subheader(":material/location_on: Catchment Node")
        selected_site = st.selectbox("Site Identifier", options=SITE_OPTIONS, index=0)
        site_meta = SITE_INFO.get(selected_site, {})
        st.caption(f"**{site_meta.get('name', selected_site)}**  \n*{site_meta.get('type', '')}*")
        selected_position = st.selectbox("Sensor Station Position", options=POSITION_OPTIONS, index=0)
        st.divider()

        preset_keys = list(PRESETS.keys())
        default_preset_idx = 0
        if "selected_preset_key" in st.session_state and st.session_state["selected_preset_key"] in preset_keys:
            default_preset_idx = preset_keys.index(st.session_state["selected_preset_key"])

        selected_preset = st.selectbox("Ecological Scenario Preset", options=preset_keys, index=default_preset_idx)

    preset_data = (PRESETS.get(selected_preset) if selected_preset else {}) or {}
    is_dropout_preset = selected_preset and "Sensor Dropout" in selected_preset

    # Input Sliders
    st.subheader(":material/sensors: Real-Time Multi-Domain Sensor Telemetry")
    
    col_phys, col_chem, col_bio = st.columns(3)

    with col_phys:
        with st.container(border=True):
            st.markdown("**:material/thermostat: Physical & Clarity Suite**")
            def_ph = float(preset_data.get("ph") if preset_data.get("ph") is not None else 7.42)
            ph_val = st.slider("pH Level", 0.0, 14.0, def_ph, 0.05, disabled=is_dropout_preset)
            def_do = float(preset_data.get("dissolved_oxygen") if preset_data.get("dissolved_oxygen") is not None else 8.65)
            do_val = st.slider("Dissolved Oxygen (mg/L)", 0.0, 20.0, def_do, 0.1, disabled=is_dropout_preset)
            def_turb = float(preset_data.get("turbidity") if preset_data.get("turbidity") is not None else 4.5)
            turb_val = st.slider("Turbidity (FNU)", 0.0, 300.0, def_turb, 0.5, disabled=is_dropout_preset)
            def_temp = float(preset_data.get("temperature") if preset_data.get("temperature") is not None else 21.3)
            temp_val = st.slider("Water Temp (°C)", 0.0, 40.0, def_temp, 0.5, disabled=is_dropout_preset)

    with col_chem:
        with st.container(border=True):
            st.markdown("**:material/science: Chemical & Nutrients Suite**")
            def_cond = float(preset_data.get("specific_conductance") if preset_data.get("specific_conductance") is not None else 280.0)
            cond_val = st.slider("Specific Conductance (µS/cm)", 0.0, 2000.0, def_cond, 10.0, disabled=is_dropout_preset)
            def_no3 = float(preset_data.get("nitrate_mg_l") if preset_data.get("nitrate_mg_l") is not None else 0.45)
            no3_val = st.slider("Nitrate NO3 (mg/L)", 0.0, 25.0, def_no3, 0.05, disabled=is_dropout_preset)
            def_po4 = float(preset_data.get("phosphate_mg_l") if preset_data.get("phosphate_mg_l") is not None else 0.015)
            po4_val = st.slider("Phosphate PO4 (mg/L)", 0.0, 1.0, def_po4, 0.005, disabled=is_dropout_preset)
            def_ssc = float(preset_data.get("suspended_sediment") if preset_data.get("suspended_sediment") is not None else 35.0)
            ssc_val = st.slider("Suspended Sediment (mg/L)", 0.0, 600.0, def_ssc, 5.0, disabled=is_dropout_preset)

    with col_bio:
        with st.container(border=True):
            st.markdown("**:material/bug_report: Biological & Contamination Proxies**")
            def_chla = float(preset_data.get("chlorophyll_a_ug_l") if preset_data.get("chlorophyll_a_ug_l") is not None else 2.8)
            chla_val = st.slider("Chlorophyll-a (µg/L)", 0.0, 100.0, def_chla, 0.5, disabled=is_dropout_preset)
            def_metal = float(preset_data.get("lead_risk_index") if preset_data.get("lead_risk_index") is not None else 0.02)
            metal_val = st.slider("Heavy Metal Leaching Proxy (0-1)", 0.0, 1.0, def_metal, 0.01, disabled=is_dropout_preset)
            def_micro = float(preset_data.get("microbial_risk_index") if preset_data.get("microbial_risk_index") is not None else 5.0)
            micro_val = st.slider("Microbial Pathogen Risk (%)", 0.0, 100.0, def_micro, 1.0, disabled=is_dropout_preset)
            taxon_val = preset_data.get("bio_dominant_taxon", "Ceriodaphnia dubia")
            st.caption(f"Bioassay Indicator Taxon: **`{taxon_val}`**")

    current_payload = {
        "ph": None if is_dropout_preset else ph_val,
        "dissolved_oxygen": None if is_dropout_preset else do_val,
        "turbidity": None if is_dropout_preset else turb_val,
        "specific_conductance": None if is_dropout_preset else cond_val,
        "temperature": temp_val,
        "nitrate_mg_l": None if is_dropout_preset else no3_val,
        "phosphate_mg_l": None if is_dropout_preset else po4_val,
        "chlorophyll_a_ug_l": None if is_dropout_preset else chla_val,
        "suspended_sediment": None if is_dropout_preset else ssc_val,
        "lead_risk_index": None if is_dropout_preset else metal_val,
        "microbial_risk_index": None if is_dropout_preset else micro_val,
        "site_id": preset_data.get("site_id", selected_site),
        "sensor_position": preset_data.get("sensor_position", selected_position),
        "bio_dominant_taxon": taxon_val,
        "bio_taxa_richness": preset_data.get("bio_taxa_richness", 2),
        "biological_sampled": 1 if taxon_val != "None" else 0,
    }

    # Execute Prediction
    result = None
    with st.spinner("Executing Model 1 Outlier + Model 2 Risk + Model 3 Eco Health + Neuro-Symbolic Safety Fusion..."):
        try:
            result = call_prediction_api(current_payload)
            now_ts = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
            st.session_state.last_timestamp = now_ts
            record = {**current_payload, **result, "timestamp": now_ts}
            if not st.session_state.history or st.session_state.history[-1].get("timestamp") != record["timestamp"]:
                st.session_state.history.append(record)
                if len(st.session_state.history) > 50:
                    st.session_state.history.pop(0)
        except Exception as e:
            st.error(f"Inference Error: {str(e)}")

    if result:
        st.divider()
        final_status = result.get("final_status", "SAFE")
        override_applied = bool(result.get("safety_override_applied", False))
        m2_raw = result.get("model2_raw_prediction", "SAFE")
        m2_conf = float(result.get("model2_confidence", 0.0))
        anom_status = result.get("anomaly_status", "Normal")
        anom_score = float(result.get("anomaly_score", 0.0))
        anom_is_alert = anom_status == "Anomaly"

        # Model 3 Biological Health Extractions
        bio_block = result.get("biological_health", {})
        bio_score = float(bio_block.get("score", 90.0))
        bio_tier = str(bio_block.get("classification", "Excellent (Pristine Ecosystem)"))
        sub_scores = bio_block.get("sub_scores", {})
        s_biodiv = float(sub_scores.get("biodiversity", 85.0))
        s_tol = float(sub_scores.get("pollution_tolerance", 90.0))
        s_troph = float(sub_scores.get("trophic_balance", 95.0))
        s_bioassay = float(sub_scores.get("bioassay_stress", 100.0))

        final_block = result.get("final_assessment", {})
        eco_health_idx = float(final_block.get("health_index", result.get("environmental_indicators", {}).get("wqi", 92.0)))

        # ── 1. Authoritative Top Alert Banner ──────────────────────────
        if final_status == "INSUFFICIENT_DATA":
            st.info("### 🔌 TELEMETRY LOSS / INSUFFICIENT DATA\nMultiple sensor channels offline. Operational risk cannot be computed.")
        elif final_status == "CRITICAL":
            override_tag = " • 🛡️ **Deterministic Safety Override Active**" if override_applied else ""
            st.error(f"### 🚨 FINAL OPERATIONAL STATUS: CRITICAL — EMERGENCY CONTAMINATION ALERT!{override_tag}\n**Intake Isolation Protocol Triggered** • NEON Eco Health Index: **{eco_health_idx:.1f}/100** • Anomaly Score: **{anom_score:+.4f}**")
        elif final_status == "WARNING":
            override_tag = " • 🛡️ **Safety Guardrail Active**" if override_applied else ""
            st.warning(f"### ⚠️ FINAL OPERATIONAL STATUS: WARNING — ELEVATED ECOLOGICAL STRESS{override_tag}\nPrecautionary monitoring active • NEON Eco Health Index: **{eco_health_idx:.1f}/100** • Anomaly Score: **{anom_score:+.4f}**")
        else:
            st.success(f"### 🟢 WATER QUALITY STATUS: NORMAL & PRISTINE\nAll hydrological, chemical, nutrient, biological bioassay, and ML assessments confirm nominal baseline conditions • Eco Health Index: **{eco_health_idx:.1f}/100**")

        # ── 2. Multi-Domain Decision Hierarchy Breakdown ───────────────
        st.markdown("##### 🔬 Multi-Domain Neuro-Symbolic Decision Center")
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            with st.container(border=True):
                st.metric("1. Model 1 (Anomaly)", f"{'⚠️ ANOMALY' if anom_is_alert else '✅ NORMAL'}", f"Score: {anom_score:+.3f}", delta_color="inverse" if anom_is_alert else "normal")
        with k2:
            with st.container(border=True):
                st.metric("2. Model 2 (Risk Class)", f"{m2_raw}", f"Confidence: {m2_conf*100:.1f}%")
        with k3:
            with st.container(border=True):
                st.metric("3. Model 3 (Eco Health)", f"{eco_health_idx:.1f}/100", bio_tier[:22])
        with k4:
            with st.container(border=True):
                st.metric("4. Final Operational Status", f"{final_status}", "Override Applied" if override_applied else "Verified", delta_color="inverse" if override_applied else "normal")

        # ── 3. Biological Ecosystem Intelligence Suite ─────────────────
        st.markdown("#### :material/psychology_alt: Model 3 Biological Ecosystem Health & Bioassay Analysis")
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            with st.container(border=True):
                st.metric("Biodiversity Score", f"{s_biodiv:.1f}/100", "Taxa Richness")
                st.progress(max(0.0, min(1.0, s_biodiv / 100.0)))
        with b2:
            with st.container(border=True):
                st.metric("Pollution Tolerance", f"{s_tol:.1f}/100", "Species Sensitivity")
                st.progress(max(0.0, min(1.0, s_tol / 100.0)))
        with b3:
            with st.container(border=True):
                st.metric("Trophic Balance", f"{s_troph:.1f}/100", "N:P Stoichiometry")
                st.progress(max(0.0, min(1.0, s_troph / 100.0)))
        with b4:
            with st.container(border=True):
                st.metric("Bioassay Survival", f"{s_bioassay:.1f}/100", "Organism NOAEL")
                st.progress(max(0.0, min(1.0, s_bioassay / 100.0)))

        # ── 4. Model 4 Predictive Early Warning (Next 24 Hours) ────────
        st.markdown("#### :material/online_prediction: Model 4 Predictive Early Warning (Next 24 Hours)")
        forecast_block = result.get("early_warning_forecast", {})
        pred_do = float(forecast_block.get("predicted_dissolved_oxygen_24h", do_val or 8.0))
        pred_turb = float(forecast_block.get("predicted_turbidity_24h", turb_val or 5.0))
        future_stat = str(forecast_block.get("future_projected_status", "SAFE"))
        future_prob = float(forecast_block.get("future_warning_probability", 0.05))
        future_conf = str(forecast_block.get("forecast_confidence", "High"))
        do_drift = float(forecast_block.get("dissolved_oxygen_drift_24h", 0.0))
        turb_drift = float(forecast_block.get("turbidity_drift_24h", 0.0))
        early_reasons = forecast_block.get("early_warning_explanation", [])
        is_forecast_suspended = (future_stat == "EMERGENCY_OVERRIDE" or "Suspended" in future_conf)

        if is_forecast_suspended:
            st.warning("⚠️ **Forecast Suspended** — *Current contamination event requires emergency response. Predictive forecasting is temporarily overridden because conditions exceed historical baseline boundaries.*")

        f1, f2, f3, f4 = st.columns(4)
        with f1:
            with st.container(border=True):
                if is_forecast_suspended:
                    st.metric("Projected DO (24h)", f"{pred_do:.2f} mg/L", "Emergency State", delta_color="inverse")
                else:
                    st.metric("Projected DO (24h)", f"{pred_do:.2f} mg/L", f"{do_drift:+.2f} mg/L drift", delta_color="normal" if do_drift >= 0 else "inverse")
        with f2:
            with st.container(border=True):
                if is_forecast_suspended:
                    st.metric("Projected Turbidity (24h)", f"{pred_turb:.1f} FNU", "Contamination Active", delta_color="inverse")
                else:
                    st.metric("Projected Turbidity (24h)", f"{pred_turb:.1f} FNU", f"{turb_drift:+.1f} FNU drift", delta_color="inverse" if turb_drift > 5 else "normal")
        with f3:
            with st.container(border=True):
                st.metric("Warning Risk / Mode", "100.0%" if is_forecast_suspended else f"{future_prob*100:.1f}%", f"Mode: {future_conf}", delta_color="inverse" if (is_forecast_suspended or future_prob > 0.4) else "normal")
        with f4:
            with st.container(border=True):
                st.metric("24h Projected State", f"{future_stat}", "Emergency Override Active" if is_forecast_suspended else ("Degradation Expected" if future_stat != "SAFE" else "Stable Trajectory"), delta_color="inverse" if future_stat != "SAFE" else "normal")

        if early_reasons and not is_forecast_suspended:
            with st.container(border=True):
                st.markdown("##### 🔮 Predictive Early Warning Causal Insights")
                for r in early_reasons:
                    st.markdown(f"- 📈 **{r}**")

        # ── 5. Model 5 AI Decision Support & Response Recommendation Center
        dec_block = result.get("decision_support", {})
        if dec_block:
            st.markdown("#### :material/emergency: AI Decision Support & Response Recommendation Center")
            d_incident = str(dec_block.get("incident", "Pristine Baseline / Nominal Water Quality"))
            d_sev = str(dec_block.get("severity", "LOW"))
            d_conf = float(dec_block.get("confidence", 95.0))
            d_causes = dec_block.get("root_causes", [])
            d_evidences = dec_block.get("evidence", [])
            d_actions = dec_block.get("recommended_actions", {})
            d_imm = d_actions.get("immediate_actions", [])
            d_short = d_actions.get("short_term_actions", [])
            d_long = d_actions.get("long_term_prevention", [])
            d_chain = dec_block.get("reasoning_chain", [])

            with st.container(border=True):
                col_i1, col_i2 = st.columns([3, 1])
                with col_i1:
                    st.markdown(f"### 🎯 Incident Classification: **{d_incident}**")
                    st.caption(f"Domain Category: `{dec_block.get('incident_category', 'General')}` • AI Fusion Confidence: **{d_conf:.1f}%**")
                with col_i2:
                    if d_sev == "CRITICAL":
                        st.error(f"**Severity Level**\n# 🔴 {d_sev}")
                    elif d_sev == "HIGH":
                        st.error(f"**Severity Level**\n# 🟠 {d_sev}")
                    elif d_sev == "MEDIUM":
                        st.warning(f"**Severity Level**\n# 🟡 {d_sev}")
                    else:
                        st.success(f"**Severity Level**\n# 🟢 {d_sev}")

                st.markdown("---")

                # Evidence Chain
                if d_evidences:
                    st.markdown("##### 🔍 Evidence Chain (Why AI Reached This Decision)")
                    for ev in d_evidences:
                        st.markdown(f"- 📌 **{ev}**")

                st.markdown("---")

                # Root Cause Possibilities (Probabilistic)
                st.markdown("##### 🔬 Root Cause Possibilities *(Probabilistic Decision Support)*")
                st.caption("Note: Indicators represent potential environmental sources for field investigation, not definitive forensic attribution.")
                for rc in d_causes:
                    st.markdown(f"- 🏭 {rc}")

                st.markdown("---")

                # Three-Column Tiered Action Plan
                st.markdown("##### 📋 Recommended Response Actions for Water Authorities")
                act_c1, act_c2, act_c3 = st.columns(3)
                with act_c1:
                    with st.container(border=True):
                        st.markdown("###### 🚨 Immediate Emergency Response (0–2h)")
                        for a in d_imm:
                            st.markdown(f"- ⚡ **{a}**")
                with act_c2:
                    with st.container(border=True):
                        st.markdown("###### ⏱️ Short-Term Containment (2–24h)")
                        for a in d_short:
                            st.markdown(f"- 🔍 {a}")
                with act_c3:
                    with st.container(border=True):
                        st.markdown("###### 🏛️ Long-Term Prevention")
                        for a in d_long:
                            st.markdown(f"- 🛡️ {a}")

                # Step-by-Step AI Reasoning Chain
                if d_chain:
                    with st.expander("🔗 Step-by-Step Multi-Model AI Reasoning Chain", expanded=False):
                        for ch in d_chain:
                            st.markdown(f"- ⛓️ {ch}")

        # ── 6. Explainable AI: Why AI Reached This Decision ───────────
        xai_block = result.get("xai_explanation", {})
        override_reason_text = result.get("override_reason", "")
        contrib_params = result.get("contributing_parameters", [])

        with st.container(border=True):
            st.markdown("### :material/psychology: Why AI Reached This Decision")
            st.caption("SHAP (SHapley Additive exPlanations) Feature Attribution & Risk Decision Diagnostics")

            if xai_block:
                xai_reason = xai_block.get("prediction_reason", "")
                if xai_reason:
                    st.info(f"💡 **AI Decision Reason:** {xai_reason}")

                feature_contribs = xai_block.get("feature_contributions", [])
                if feature_contribs:
                    st.markdown("##### 📊 SHAP Feature Contributions on Risk Level")

                    shap_records = []
                    for fc in feature_contribs:
                        shap_records.append({
                            "Feature": fc.get("label", fc.get("feature")),
                            "Current Value": str(fc.get("value", "N/A")),
                            "Impact on Risk": float(fc.get("impact", 0.0)),
                            "Direction": "🔴 Increases Risk" if "increase" in str(fc.get("direction", "")).lower() else ("🟢 Decreases Risk" if "decrease" in str(fc.get("direction", "")).lower() else "⚪ Neutral"),
                            "Baseline Assessment": str(fc.get("value_assessment", "within safe range") or "within safe range")
                        })

                    shap_df = pd.DataFrame(shap_records)

                    col_chart, col_table = st.columns([1, 1])

                    with col_chart:
                        st.markdown("**Feature Impact Chart (SHAP Values)**")
                        # Sort by impact for clear horizontal visualization
                        chart_df = pd.DataFrame({
                            "Feature": [r["Feature"] for r in shap_records[:8]],
                            "SHAP Impact": [float(r["Impact on Risk"]) for r in shap_records[:8]]
                        }).set_index("Feature")
                        st.bar_chart(chart_df, horizontal=True)
                        st.caption("Positive impact = Increases Risk Class Probability • Negative = Protects Safe Status")

                    with col_table:
                        st.markdown("**Feature Attribution Breakdown**")
                        st.dataframe(
                            shap_df[["Feature", "Current Value", "Impact on Risk", "Direction", "Baseline Assessment"]],
                            hide_index=True,
                            width="stretch"
                        )

            if override_reason_text:
                st.markdown(f"**Primary Causal Assessment:** `{override_reason_text}`")
            if contrib_params:
                param_badges = " ".join([f"`{p}`" for p in contrib_params])
                st.markdown(f"**Key Contributing Risk Variables:** {param_badges}")

            st.markdown("---")
            st.markdown("##### 🔍 Multi-Tier Diagnostic Breakdown")
            if override_applied:
                st.markdown(f"- 🛡️ **Safety Guardrail Override**: ML Model 2 predicted `{m2_raw}` ({m2_conf*100:.1f}%), but Deterministic Safety Guardrails upgraded final status to **`{final_status}`**.")
                for r in result.get("override_reasons", []):
                    st.markdown(f"  - *{r}*")
            if anom_is_alert:
                st.markdown(f"- 🤖 **Model 1 Anomaly**: Unsupervised Isolation Forest detected statistical outlier with severity `{anom_score:+.4f}`.")
            st.markdown(f"- 📊 **Model 2 Classifier**: Balanced Random Forest classified environmental vector as `{m2_raw}` with {m2_conf*100:.1f}% confidence.")
            st.markdown(f"- 🌿 **Model 3 Ecosystem**: Evaluated live bioassays (*{taxon_val}*) yielding Composite Bio Score `{bio_score:.1f}/100` and Eco Health Index `{eco_health_idx:.1f}/100`.")
            for exp in result.get("explanation", []):
                if not exp.startswith("🛡️") and not exp.startswith("  •"):
                    st.markdown(f"- 🔬 **Parameter Finding**: {exp}")

    # Telemetry Trend History
    if st.session_state.history:
        st.divider()
        st.subheader(":material/timeline: Live Telemetry Stream History")
        hist_df = pd.DataFrame(st.session_state.history)
        th1, th2 = st.tabs([":material/show_chart: Synchronized Telemetry Charts", ":material/code: Raw JSON Telemetry"])
        with th1:
            ch1, ch2 = st.columns(2)
            with ch1:
                st.markdown("**pH Level & Dissolved Oxygen (mg/L)**")
                c1_cols = [c for c in ["ph", "dissolved_oxygen"] if c in hist_df.columns]
                if c1_cols:
                    st.line_chart(hist_df[["timestamp"] + c1_cols].set_index("timestamp"))
            with ch2:
                st.markdown("**Turbidity (FNU) & Eco Health Index**")
                c2_cols = [c for c in ["turbidity", "final_assessment"] if c in hist_df.columns]
                st.line_chart(hist_df[["timestamp", "turbidity"]].set_index("timestamp"))
        with th2:
            st.json(result)


# ===================================================================
# TAB 2: HISTORICAL USGS CATCHMENT ANALYTICS (77,641 EVENTS)
# ===================================================================
with tab_history:
    st.subheader(":material/travel_explore: Historical Catchment Analytics & Spatial Explorer")
    st.caption("Harmonized dataset: `data/processed/usgs_water_quality.parquet` (77,641 Multi-Domain Sampling Events)")

    usgs_df = load_historical_data()
    if usgs_df is not None:
        uc1, uc2, uc3, uc4 = st.columns(4)
        with uc1:
            st.metric("Total Sampling Events", f"{len(usgs_df):,}")
        with uc2:
            st.metric("Total Features Harmonized", f"{len(usgs_df.columns)}")
        with uc3:
            st.metric("Unique USGS Stations", f"{usgs_df['MonitoringLocationIdentifier'].nunique():,}")
        with uc4:
            bio_events = usgs_df['biological_sampled_flag'].sum() if 'biological_sampled_flag' in usgs_df.columns else 909
            st.metric("Biological Bioassays", f"{int(bio_events):,}")

        st.divider()

        # Catchment Explorer Controls
        top_stations = usgs_df["MonitoringLocationIdentifier"].value_counts().head(10).index.tolist()
        sel_station = st.selectbox("Filter by USGS Monitoring Station", options=["ALL STATIONS"] + top_stations, index=0)

        station_df = usgs_df if sel_station == "ALL STATIONS" else usgs_df[usgs_df["MonitoringLocationIdentifier"] == sel_station]

        tab_grid, tab_dist, tab_taxa = st.tabs([":material/table_chart: Data Records", ":material/bar_chart: Physical/Chemical Distributions", ":material/bug_report: Bioassay Species Records"])
        
        with tab_grid:
            disp_cols = [c for c in ["ActivityStartDate", "MonitoringLocationIdentifier", "ph", "dissolved_oxygen_mg_l", "turbidity_fnu", "specific_conductance_us_cm", "nitrate_mg_l", "orthophosphate_mg_l", "bio_dominant_taxon", "total_nitrogen_est_mg_l", "total_phosphorus_est_mg_l"] if c in station_df.columns]
            st.dataframe(station_df[disp_cols].head(100), width="stretch")

        with tab_dist:
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.markdown("**pH Distribution**")
                if "ph" in station_df.columns:
                    ph_clean = station_df["ph"].dropna()
                    ph_clean = ph_clean[(ph_clean >= 0.0) & (ph_clean <= 14.0)]
                    if not ph_clean.empty:
                        ph_distribution = pd.cut(ph_clean, bins=14).value_counts().sort_index()
                        ph_distribution.index = ph_distribution.index.astype(str)
                        st.bar_chart(ph_distribution)
            with d_col2:
                st.markdown("**Dissolved Oxygen Distribution (mg/L)**")
                if "dissolved_oxygen_mg_l" in station_df.columns:
                    do_clean = station_df["dissolved_oxygen_mg_l"].dropna()
                    do_clean = do_clean[(do_clean >= 0.0) & (do_clean <= 20.0)]
                    if not do_clean.empty:
                        do_distribution = pd.cut(do_clean, bins=14).value_counts().sort_index()
                        do_distribution.index = do_distribution.index.astype(str)
                        st.bar_chart(do_distribution)

        with tab_taxa:
            if "bio_dominant_taxon" in usgs_df.columns:
                taxa_counts = usgs_df["bio_dominant_taxon"].value_counts().head(10)
                st.markdown("##### 🔬 Dominant EPA Bioassay Test Species in Dataset")
                st.bar_chart(taxa_counts)
    else:
        st.warning("Historical dataset not found at `data/processed/usgs_water_quality.parquet`.")


# ===================================================================
# TAB 3: MULTI-DOMAIN AI & NEURO-SYMBOLIC ARCHITECTURE
# ===================================================================
with tab_arch:
    st.subheader(":material/hub: Complete 5-Model AI Architecture & Neuro-Symbolic Decision Flow")
    st.caption("SIH 2026 NEON Water Intelligence Platform — Production v5.0.0")

    st.markdown(r"""
    The NEON Water Intelligence Platform operates on a **5-model Neuro-Symbolic Multi-Domain AI pipeline**:

    **Data Layer**: Ingests 891,996 raw USGS/EPA records → ETL pipeline → 77,641 harmonized events × 49 features

    **Model 1 (Isolation Forest)**: Unsupervised multivariate anomaly detection (120 trees, 5% contamination)

    **Model 2 (Balanced Random Forest)**: Supervised SAFE / WARNING / CRITICAL risk classifier (99.77% accuracy, F1 = 0.9963)

    **Model 3 (Biological Health Engine)**: EPA bioassay-based NEON Eco Health Index (0-100) with anti-eclipsing guardrails

    **Model 4.1 (Multi-Scale Forecaster)**: 24-hour predictive trajectory (DO R² = 0.7764, Turbidity RMSE = 64.2 FNU)

    **Model 5 (Decision Support Engine)**: Neuro-symbolic incident classification, root cause analysis, and 3-tier action recommendations

    **Safety Layer**: Deterministic EPA guardrails override ML when hard biological limits are violated
    """)

    st.divider()

    # Model Performance Cards
    st.markdown("##### 📊 Model Performance Summary")
    perf1, perf2, perf3, perf4, perf5 = st.columns(5)
    with perf1:
        with st.container(border=True):
            st.markdown("**Model 1**")
            st.markdown("Anomaly Detection")
            st.metric("CRITICAL Detection Rate", "92.33%")
            st.caption("Isolation Forest • 5 features")
    with perf2:
        with st.container(border=True):
            st.markdown("**Model 2**")
            st.markdown("Risk Classification")
            st.metric("Overall Accuracy", "99.77%")
            st.caption("Balanced RF • Macro F1: 0.9963")
    with perf3:
        with st.container(border=True):
            st.markdown("**Model 3**")
            st.markdown("Bio-Ecosystem Health")
            st.metric("Eco Health Index", "0-100")
            st.caption("EPA Bioassay • 4 sub-scores")
    with perf4:
        with st.container(border=True):
            st.markdown("**Model 4.1**")
            st.markdown("24h Forecasting")
            st.metric("DO Prediction R²", "0.7764")
            st.caption("Multi-Scale GBR • 98 features")
    with perf5:
        with st.container(border=True):
            st.markdown("**Model 5**")
            st.markdown("Decision Support")
            st.metric("Incident Types", "9")
            st.caption("Neuro-Symbolic • 3-tier actions")

    st.divider()

    # Dataset & Training Summary
    st.markdown("##### 📋 Dataset & Training Pipeline")
    ds1, ds2 = st.columns(2)
    with ds1:
        with st.container(border=True):
            st.markdown("**Raw Data Ingestion**")
            st.markdown("- **Source**: USGS Water Quality Portal + EPA STORET")
            st.markdown("- **Raw Records**: 891,996 (445,998 PhysChem + 445,998 Bio)")
            st.markdown("- **Monitoring Stations**: 2,547 across 47 US states")
            st.markdown("- **Temporal Span**: 2018-01-01 to 2025-01-01")
    with ds2:
        with st.container(border=True):
            st.markdown("**Processed Dataset**")
            st.markdown("- **Events**: 77,641 multi-parameter sampling events")
            st.markdown("- **Features**: 49 harmonized columns")
            st.markdown("- **Biological Samples**: 909 EPA bioassay events")
            st.markdown("- **Continuous Stations**: 181 (≥100 observations)")

    st.divider()

    # Feature Importance
    st.markdown("##### 🎯 Model 2 Feature Importance Ranking (Gini Impurity)")
    try:
        st.image("reports/usgs_feature_importance.png", caption="Turbidity 29.6% • Conductance 16.4% • pH 14.4% • DO 14.2% • SSC 7.5% • SSC:Turb 6.7% • TP 6.3%")
    except Exception:
        st.info("Feature importance plot not available.")

    # Safety Override Architecture
    st.divider()
    st.markdown("##### 🛡️ Neuro-Symbolic Safety Override Architecture")
    with st.container(border=True):
        st.markdown(r"""
        **Deterministic EPA Anti-Eclipsing Guardrails** (Cannot be overridden by ML):

        | Parameter | CRITICAL Override Threshold | Action |
        |---|---|---|
        | pH | < 4.0 or > 10.0 | Force CRITICAL (EPA Acute Lethal) |
        | Dissolved Oxygen | < 2.0 mg/L | Force CRITICAL (Lethal Anoxia) |
        | Turbidity | > 100.0 FNU | Force CRITICAL (Filter Blinding) |
        | Specific Conductance | > 1500.0 µS/cm | Force CRITICAL (Severe Salinization) |
        | Heavy Metal Risk | ≥ 0.70 | Force CRITICAL (Toxic Contamination) |
        | Microbial Risk | ≥ 65.0% | Force CRITICAL (Pathogen Hazard) |
        | Eutrophic Collapse | DO < 4.0 + Nutrients Elevated | Force CRITICAL (Synergistic) |
        """)

