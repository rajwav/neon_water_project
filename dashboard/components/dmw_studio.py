"""
NEON Water Intelligence Platform — DMW Academic Presentation Studio.

Provides two dedicated presentation screens for Data Mining & Data Warehouses (DMW):
  1. Screen 4: EDA & Data Preprocessing Studio
     - Step-by-step Explain Mode (What we did -> Why -> What we achieved)
     - Live EDA metrics & distributions (NEON 7.57M audit + USGS 77.6k warehouse)
     - Verbatim preprocessing codebases (Cleaning, Flagging, BDL Imputation, Pivoting, Scaling)
     - Interactive Live Preprocessing Sandbox executing real repo functions
     - Collapsed voluntary dropdown for optional modules (ML, Crypto, Automation, Sensors)

  2. Screen 5: Database & Data Warehouse Demo
     - Explain Mode for Dual-Tier Storage (Analytical Parquet Warehouse + Operational SQLite DB)
     - Live Apache Parquet Warehouse Explorer & Schema Contracts
     - Live SQLite Database Demo (Insert live rows + Interactive Read-Only SQL Console + Codebase)
     - Collapsed voluntary dropdown for optional modules
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler, StandardScaler

from src.data.constants import INSTRUMENT_RANGES, NEON_COLUMN_MAP
from src.data.usgs_pipeline import clean_measure_value
from src.data.validators import apply_instrument_range_flags
from iot.database import (
    DB_PATH,
    get_recent_telemetry_records,
    init_db,
    insert_telemetry_record,
)


# ---------------------------------------------------------------------------
# Internal Helpers (Code & Cached Data Loaders)
# ---------------------------------------------------------------------------

def _read_code_slice(
    project_root: Path,
    rel_path: str,
    start_line: int = 1,
    end_line: Optional[int] = None,
) -> str:
    """Read verbatim lines from a repository file with 1-based inclusive bounds."""
    target = project_root / rel_path
    if not target.exists():
        return f"# File not found: {rel_path}"
    lines = target.read_text(encoding="utf-8").splitlines()
    end_idx = len(lines) if end_line is None else min(end_line, len(lines))
    start_idx = max(0, start_line - 1)
    return "\n".join(lines[start_idx:end_idx])


@st.cache_data(show_spinner=False)
def _load_audit_report(project_root_str: str) -> Dict[str, Any]:
    path = Path(project_root_str) / "data" / "audit_report.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def _load_usgs_parquet(project_root_str: str, filename: str = "usgs_water_quality.parquet") -> pd.DataFrame:
    path = Path(project_root_str) / "data" / "processed" / filename
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


@st.cache_data(show_spinner=False)
def _load_eda_notebook_cells(project_root_str: str, max_cell: int = 8) -> List[Dict[str, str]]:
    """Extract only the EDA & Normalization cells (before ML training) from 01_EDA.ipynb."""
    nb_path = Path(project_root_str) / "01_EDA.ipynb"
    if not nb_path.exists():
        return []
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    extracted: List[Dict[str, str]] = []
    for idx, cell in enumerate(nb.get("cells", [])[: max_cell + 1]):
        src = "".join(cell.get("source", [])).strip()
        if src:
            extracted.append({
                "index": idx,
                "cell_type": cell.get("cell_type", "code"),
                "source": src,
            })
    return extracted


def _render_explain_card(
    step_num: str,
    title: str,
    what_did: str,
    why_did: str,
    what_achieved: str,
    code_ref: str,
) -> None:
    """Render a consistent 3-column DMW Explain Mode card."""
    with st.container(border=True):
        st.markdown(f"#### {step_num}: {title}")
        st.caption(f"Codebase Reference: `{code_ref}`")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**1️⃣ What We Did (Action)**")
            st.info(what_did)
        with c2:
            st.markdown("**2️⃣ Why We Did It (DMW Reason)**")
            st.warning(why_did)
        with c3:
            st.markdown("**3️⃣ What We Achieved (Result)**")
            st.success(what_achieved)


def _render_hidden_optional_code_dropdown(project_root: Path, key_prefix: str) -> None:
    """
    Keep ML Models, Cryptography, Automation, and Sensor codebases completely hidden
    unless the user voluntarily opens the expander and selects a module.
    """
    st.markdown("---")
    with st.expander(
        "🔒 Optional Codebase Viewer (ML Models / Cryptography / Automation / Sensors — Hidden Unless Selected)",
        expanded=False,
    ):
        st.caption(
            "Hidden by default so the main presentation stays 100% focused on EDA, Data Preprocessing, and Data Warehousing. "
            "Pick a module below only if an examiner asks about downstream components."
        )
        choice = st.selectbox(
            "Select Optional Module to Inspect:",
            [
                "— Select Optional Module (Hidden) —",
                "1. ML Models & TreeSHAP Explainability",
                "2. Cryptography & SHA-256 Audit Ledger",
                "3. Closed-Loop Automation & Decision Gate",
                "4. IoT Sensors & MQTT Telemetry Ingestion",
            ],
            key=f"{key_prefix}_optional_module_select",
        )

        if choice == "1. ML Models & TreeSHAP Explainability":
            sub_file = st.selectbox(
                "Choose ML Source File:",
                [
                    "scripts/train_anomaly_model_v2.py",
                    "scripts/train_risk_model_v2.py",
                    "src/ml/biological_health_model.py",
                    "src/ml/forecasting_pipeline.py",
                    "src/ml/xai_explainer.py",
                ],
                key=f"{key_prefix}_ml_file",
            )
            st.code(_read_code_slice(project_root, sub_file, 1, 220), language="python")

        elif choice == "2. Cryptography & SHA-256 Audit Ledger":
            st.markdown("**Deterministic Observation ID Hashing (`src/data/validators.py`)**")
            st.code(_read_code_slice(project_root, "src/data/validators.py", 1, 23), language="python")
            st.markdown("**Tamper-Evident Incident Manifest Hashing (`src/automation/workflow_engine.py`)**")
            st.code(_read_code_slice(project_root, "src/automation/workflow_engine.py", 130, 225), language="python")

        elif choice == "3. Closed-Loop Automation & Decision Gate":
            sub_file = st.selectbox(
                "Choose Decision / Automation File:",
                [
                    "src/decision/decision_engine.py",
                    "src/automation/workflow_engine.py",
                ],
                key=f"{key_prefix}_auto_file",
            )
            st.code(_read_code_slice(project_root, sub_file, 1, 220), language="python")

        elif choice == "4. IoT Sensors & MQTT Telemetry Ingestion":
            sub_file = st.selectbox(
                "Choose IoT / Sensor File:",
                [
                    "iot/autonomous_sensor.py",
                    "iot/sensor_simulator.py",
                    "iot/mqtt_client.py",
                    "iot/config.py",
                ],
                key=f"{key_prefix}_iot_file",
            )
            st.code(_read_code_slice(project_root, sub_file, 1, 220), language="python")


# ---------------------------------------------------------------------------
# SCREEN 4: EDA & DATA PREPROCESSING STUDIO
# ---------------------------------------------------------------------------

def render_eda_preprocessing_screen(project_root: Path) -> None:
    """Render Screen 4 focused exclusively on EDA & Data Preprocessing (+ Explain Mode)."""
    st.markdown("### 🧹 EDA & Data Preprocessing Studio (DMW Core Presentation)")
    st.caption(
        "Showcasing Exploratory Data Analysis, Non-Destructive Cleaning, BDL Imputation, Pivoting, Feature Engineering & Leak-Free Scaling"
    )

    audit = _load_audit_report(str(project_root))
    usgs_df = _load_usgs_parquet(str(project_root), "usgs_water_quality.parquet")

    tab_explain, tab_eda, tab_clean, tab_usgs, tab_scale = st.tabs([
        "📖 Explain Mode (Step-by-Step)",
        "🔍 Step 1: EDA & Raw Audit",
        "🧹 Step 2–3: Cleaning, Flagging & Dedup",
        "⚗️ Step 4: BDL Imputation, Pivot & Live Sandbox",
        "⚖️ Step 5: Leak-Free Scaling & Encoding",
    ])

    # ── TAB 1: EXPLAIN MODE ────────────────────────────────────────
    with tab_explain:
        st.markdown("#### 📖 Explain Mode — How We Built This From Scratch (Start → Finish)")
        view_mode = st.radio(
            "Presentation Mode:",
            ["Interactive Single-Step Focus (Best for Live Speech)", "Full End-to-End Timeline (All Steps)"],
            horizontal=True,
            key="s4_explain_view_mode",
        )

        steps_data = [
            (
                "Step 0",
                "Origin & Raw Multi-Source Data Acquisition",
                "Started with uncleaned NEON continuous water-quality CSV dumps (192 monthly files across 5 river sites) and discrete USGS Water Quality Portal lab CSVs (resultphyschem + biologicalresult).",
                "No reliable autonomous monitoring or forecasting can work on fragmented, unstandardized, multi-agency raw files with mixed strings and missing sensor windows.",
                "Established the end-to-end ingestion scope: 7,579,008 NEON telemetry records + 445k USGS lab/biological observations unified into one pipeline.",
                "src/data/pipeline.py & src/data/usgs_pipeline.py",
            ),
            (
                "Step 1",
                "Exploratory Data Analysis (EDA) & Data Profiling",
                "Loaded raw NEON multi-site CSV bundles (192 files) and inspected shapes, column types, missingness, and summary statistics (.describe()) in 01_EDA.ipynb.",
                "Real sensor streams contain mixed string/numeric types, heavy right-skew in turbidity/conductance, and millions of vendor quality-flag anomalies that break naive ML training.",
                "Profiled 7,579,008 raw NEON records across 5 sites (ARIK, BIGC, BLDE, BLUE, BARC) and identified exact cleaning & robust-scaling requirements.",
                "01_EDA.ipynb (Cells 1–8) & data/audit_report.json",
            ),
            (
                "Step 2",
                "Canonical Schema Mapping & UTC Timestamp Coercion",
                "Mapped raw NEON column headers (startDateTime, specificConductance, fDOM, etc.) to canonical warehouse names, parsed timestamps in strict UTC, and coerced corrupt strings using errors='coerce'.",
                "Different monitoring stations and file dumps use inconsistent headers and unparseable date formats; failing to unify timestamps causes temporal join errors and crashes.",
                "Standardized 100% of canonical columns across all 192 files with explicit exclusion logging for unparseable timestamps (0 excluded in verified batch).",
                "src/data/constants.py & src/data/pipeline.py (process_single_raw_file)",
            ),
            (
                "Step 3",
                "Non-Destructive Outlier Flagging & Duplicate Detection",
                "Evaluated hardware operating bounds (pH 0–14, DO 0–30 mg/L, Turbidity 0–4000 FNU, Conductance 0–50000 uS/cm), NEON quality flags (QF=1), and composite key duplicates without deleting rows.",
                "Blindly deleting extreme values destroys real chemical spill signals! Non-destructive boolean flags separate sensor electrical faults from true pollution events.",
                "Preserved all 7,579,008 rows with full provenance: flagged out-of-range artifacts (e.g. 429,747 conductance spikes, 112,819 turbidity) and verified 0 duplicate records.",
                "src/data/validators.py (apply_instrument_range_flags, apply_neon_qf_flags, detect_duplicates)",
            ),
            (
                "Step 4",
                "USGS Below-Detection-Limit (BDL) Imputation, Long-to-Wide Pivoting & Feature Engineering",
                "Streamed USGS lab data in 50,000-row chunks, parsed censored '< MDL' strings as 0.5 × MDL, averaged replicate readings, pivoted long rows to wide feature vectors, joined bioindicators, and derived N:P & SSC:Turbidity ratios.",
                "Lab concentrations arrive as long-format text like '< 0.05' which cause string errors and massive sparse tables; 1/2 MDL substitution and long-to-wide pivoting convert messy logs into ML-ready matrices.",
                "Transformed raw WQP physical/chemical + biological CSVs into a clean 77,641 × 49 wide Snappy-compressed Apache Parquet warehouse.",
                "src/data/usgs_pipeline.py (clean_measure_value, process_physchem_dataset, compute_derived_biogeochemical_features)",
            ),
            (
                "Step 5",
                "Temporal Split, Median Imputation, Robust/Standard Scaling & One-Hot Encoding",
                "Split records strictly by year (2024 Train / 2025 Test) and placed SimpleImputer(median), RobustScaler/StandardScaler, and OneHotEncoder inside scikit-learn Pipeline / ColumnTransformer.",
                "Fitting a scaler or imputer on the full dataset before splitting leaks future 2025 distribution statistics into training. Median + IQR RobustScaler resists sensor spikes.",
                "Guaranteed zero temporal data leakage while uniformly preparing numeric sensors, categorical site IDs, and binary quality flags for downstream modeling.",
                "scripts/train_anomaly_model_v2.py & scripts/train_risk_model_v2.py (build_preprocessor)",
            ),
        ]

        if view_mode.startswith("Interactive"):
            selected_title = st.select_slider(
                "Walk Through Step:",
                options=[f"{s[0]}: {s[1]}" for s in steps_data],
                key="s4_explain_slider",
            )
            idx = [f"{s[0]}: {s[1]}" for s in steps_data].index(selected_title)
            _render_explain_card(*steps_data[idx])
        else:
            for item in steps_data:
                _render_explain_card(*item)

    # ── TAB 2: STEP 1 - EDA & AUDIT ────────────────────────────────
    with tab_eda:
        st.markdown("#### 🔍 Step 1: Exploratory Data Analysis (EDA) & Batch Audit Output")

        if audit:
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Raw NEON CSV Files", f"{audit.get('total_raw_files_processed', 0):,}")
            k2.metric("Raw Sensor Records", f"{audit.get('total_raw_records_read', 0):,}")
            k3.metric("2024 vs 2025 Split", f"{audit.get('temporal_2024_records', 0):,} / {audit.get('temporal_2025_records', 0):,}")
            k4.metric("USGS Warehouse Matrix", f"{len(usgs_df):,} × {usgs_df.shape[1]}" if not usgs_df.empty else "Unavailable")

            c_left, c_right = st.columns(2)
            with c_left:
                site_counts = audit.get("site_record_counts", {})
                if site_counts:
                    df_sites = pd.DataFrame({
                        "Site ID": list(site_counts.keys()),
                        "Records": list(site_counts.values()),
                    })
                    fig_sites = px.bar(
                        df_sites,
                        x="Site ID",
                        y="Records",
                        title="NEON Raw Record Distribution by Monitoring Site",
                        text_auto=True,
                        color="Site ID",
                    )
                    fig_sites.update_layout(template="plotly_dark", height=340, showlegend=False)
                    st.plotly_chart(fig_sites, width="stretch")

            with c_right:
                if not usgs_df.empty:
                    num_cols = [
                        c for c in [
                            "ph", "dissolved_oxygen_mg_l", "turbidity_fnu",
                            "specific_conductance_us_cm", "nitrate_mg_l", "n_to_p_ratio",
                        ]
                        if c in usgs_df.columns
                    ]
                    sel_col = st.selectbox("Inspect Distribution in USGS Warehouse:", num_cols, key="s4_eda_dist_col")
                    series = usgs_df[sel_col].dropna()
                    # Clip top 1% visually and pre-bin in Python so WebSocket sends 35 bars instead of 77k points
                    q99 = float(series.quantile(0.99)) if len(series) > 0 else 1.0
                    clipped = series[series <= q99].to_numpy()
                    counts, edges = np.histogram(clipped, bins=35)
                    bin_labels = [f"{edges[i]:.2g}–{edges[i+1]:.2g}" for i in range(len(counts))]
                    df_hist = pd.DataFrame({"Range Bin": bin_labels, "Count": counts})
                    fig_hist = px.bar(
                        df_hist,
                        x="Range Bin",
                        y="Count",
                        title=f"Distribution of `{sel_col}` (<= 99th pct | True Max = {series.max():.2f})",
                    )
                    fig_hist.update_layout(template="plotly_dark", height=290, showlegend=False)
                    st.plotly_chart(fig_hist, width="stretch")

        if not usgs_df.empty:
            st.markdown("##### 📊 Statistical Summary (`.describe()`) — Preprocessed USGS Parameters")
            core_cols = [
                c for c in [
                    "ph", "dissolved_oxygen_mg_l", "turbidity_fnu",
                    "specific_conductance_us_cm", "nitrate_mg_l", "orthophosphate_mg_l",
                    "total_nitrogen_est_mg_l", "total_phosphorus_est_mg_l", "n_to_p_ratio",
                ]
                if c in usgs_df.columns
            ]
            st.dataframe(usgs_df[core_cols].describe().T.round(4), width="stretch")

        st.markdown("##### 💻 EDA Notebook Code (`01_EDA.ipynb` — Discovery & Normalization Cells)")
        eda_cells = _load_eda_notebook_cells(str(project_root), max_cell=8)
        for c in eda_cells:
            if c["cell_type"] == "markdown":
                st.markdown(f"> {c['source']}")
            else:
                st.code(c["source"], language="python")

    # ── TAB 3: STEP 2-3 - CLEANING, FLAGGING & DEDUP ───────────────
    with tab_clean:
        st.markdown("#### 🧹 Step 2–3: Schema Standardization, Non-Destructive Flagging & Deduplication")

        # Real Validation Output Charts from audit_report.json
        if audit and "quality_flag_summary" in audit:
            qf_sum = audit["quality_flag_summary"]
            oor = qf_sum.get("out_of_instrument_range", {})
            nqf = qf_sum.get("neon_qf_fail", {})
            params = list(oor.keys())
            df_flags = pd.DataFrame({
                "Parameter": params,
                "Out of Instrument Range": [oor.get(p, 0) for p in params],
                "NEON Quality Flag (QF=1)": [nqf.get(p, 0) for p in params],
            })
            c1, c2 = st.columns([1.3, 1.0])
            with c1:
                fig_qf = px.bar(
                    df_flags.melt(id_vars="Parameter", var_name="Flag Type", value_name="Flagged Rows"),
                    x="Parameter",
                    y="Flagged Rows",
                    color="Flag Type",
                    barmode="group",
                    title="Output: Sensor Flags Detected Without Deleting Raw Data (7.57M Rows)",
                )
                fig_qf.update_layout(template="plotly_dark", height=360)
                st.plotly_chart(fig_qf, width="stretch")
            with c2:
                st.markdown("##### 📋 Exact Flag & Deduplication Audit Table")
                st.dataframe(df_flags, width="stretch", hide_index=True)
                st.metric("Duplicate Records Detected", f"{audit.get('duplicate_records_detected', 0):,}")
                st.metric("Raw Records Preserved", f"{audit.get('arik_accountability', {}).get('canonical_percent_preserved', 100)}%")

        with st.expander("🧭 Canonical Column Map & Hardware Operating Bounds Table", expanded=False):
            bounds_rows = [
                {
                    "Raw NEON Header": raw_k,
                    "Canonical Name": canon_v,
                    "Instrument Operating Range": str(INSTRUMENT_RANGES.get(canon_v, "N/A")),
                }
                for raw_k, canon_v in NEON_COLUMN_MAP.items()
            ]
            st.dataframe(pd.DataFrame(bounds_rows), width="stretch", hide_index=True)

        st.markdown("##### 💻 Verbatim Code: Schema Maps & Hardware Physical Bounds (`src/data/constants.py`)")
        st.code(_read_code_slice(project_root, "src/data/constants.py", 13, 80), language="python")

        col_p, col_v = st.columns(2)
        with col_p:
            st.markdown("##### 💻 Canonical UTC Cleaning (`src/data/pipeline.py`)")
            st.code(_read_code_slice(project_root, "src/data/pipeline.py", 75, 140), language="python")
        with col_v:
            st.markdown("##### 💻 Non-Destructive Validators (`src/data/validators.py`)")
            st.code(_read_code_slice(project_root, "src/data/validators.py", 18, 92), language="python")

        with st.expander("📄 Contrast: Earlier Baseline CSV Cleanup Script (`scripts/process_neon.py`)", expanded=False):
            st.caption("Early prototype script that dropped failed QF rows and NaNs directly, before upgrading to non-destructive flagging.")
            st.code(_read_code_slice(project_root, "scripts/process_neon.py", 1, 121), language="python")

    # ── TAB 4: STEP 4 - BDL IMPUTATION, PIVOT & SANDBOX ────────────
    with tab_usgs:
        st.markdown("#### ⚗️ Step 4: USGS BDL (½ MDL) Imputation, Long-to-Wide Pivot & Live Sandbox")

        # Live Interactive Preprocessing Sandbox
        with st.container(border=True):
            st.markdown("##### 🧪 Interactive Live Preprocessing Sandbox (Runs Real Repo Functions!)")
            st.caption("Modify raw dirty telemetry or censored lab strings below to execute `clean_measure_value()` and `apply_instrument_range_flags()` live.")
            preset = st.selectbox(
                "Load Test Preset:",
                [
                    "Dirty Multi-Fault Sample (Censored '< 0.05' + Sensor Spike + Bad Timestamp)",
                    "Acid Mine / High Conductance Anomaly (Valid Within Sensor Bounds)",
                    "Clean Nominal Sample",
                ],
                key="s4_sandbox_preset",
            )
            preset_values = {
                "Dirty": ("2026-BAD-DATE", 16.5, -2.1, 450.0, 62000.0, "< 0.05"),
                "Acid": ("2026-11-11T09:30:00", 2.9, 3.2, 85.0, 2400.0, "18.4*"),
                "Clean": ("2026-11-11T09:30:00", 7.42, 8.65, 4.5, 280.0, "1.25"),
            }
            p_key = "Dirty" if preset.startswith("Dirty") else ("Acid" if preset.startswith("Acid") else "Clean")
            def_ts, def_ph, def_do, def_turb, def_cond, def_no3 = preset_values[p_key]

            if st.session_state.get("s4_last_sandbox_preset") != preset:
                st.session_state["s4_last_sandbox_preset"] = preset
                st.session_state["sb_ts"] = def_ts
                st.session_state["sb_ph"] = float(def_ph)
                st.session_state["sb_do"] = float(def_do)
                st.session_state["sb_turb"] = float(def_turb)
                st.session_state["sb_cond"] = float(def_cond)
                st.session_state["sb_no3"] = def_no3

            sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
            in_ts = sc1.text_input("Raw Timestamp", key="sb_ts")
            in_ph = sc2.number_input("Raw pH", step=0.1, key="sb_ph")
            in_do = sc3.number_input("Raw DO (mg/L)", step=0.1, key="sb_do")
            in_turb = sc4.number_input("Raw Turbidity", step=1.0, key="sb_turb")
            in_cond = sc5.number_input("Raw Cond (µS/cm)", step=10.0, key="sb_cond")
            in_no3 = sc6.text_input("Raw Nitrate Str", key="sb_no3")

            parsed_ts = pd.to_datetime(in_ts, utc=True, errors="coerce")
            cleaned_no3 = clean_measure_value(in_no3)
            raw_row_df = pd.DataFrame([{
                "ph": in_ph,
                "dissolved_oxygen": in_do,
                "turbidity": in_turb,
                "specific_conductance": in_cond,
                "chlorophyll": 3.2,
                "fdom": 15.0,
                "sensor_depth": 1.5,
            }])
            flagged_df, range_counts = apply_instrument_range_flags(raw_row_df.copy())

            out1, out2 = st.columns(2)
            with out1:
                st.markdown("**Real Execution Output (`pipeline.py` + `usgs_pipeline.py`):**")
                st.json({
                    "utc_timestamp_parsed": str(parsed_ts) if pd.notna(parsed_ts) else "NaT -> EXCLUDED (unparseable_timestamp)",
                    "raw_nitrate_input": in_no3,
                    "clean_measure_value_output": cleaned_no3,
                    "bdl_rule_applied": "0.5 * MDL" if str(in_no3).strip().startswith("<") else "Direct numeric regex parse",
                })
            with out2:
                st.markdown("**Real Execution Output (`validators.py` Range Bounds):**")
                st.json({
                    "ph_flag_range": bool(flagged_df["ph_flag_range"].iloc[0]),
                    "dissolved_oxygen_flag_range": bool(flagged_df["dissolved_oxygen_flag_range"].iloc[0]),
                    "turbidity_flag_range": bool(flagged_df["turbidity_flag_range"].iloc[0]),
                    "specific_conductance_flag_range": bool(flagged_df["specific_conductance_flag_range"].iloc[0]),
                    "total_out_of_range_fields": sum(range_counts.values()),
                })

        st.markdown("##### 💻 Verbatim Code: BDL ½ MDL Imputation & Long-to-Wide Pivot (`src/data/usgs_pipeline.py`)")
        st.code(_read_code_slice(project_root, "src/data/usgs_pipeline.py", 102, 248), language="python")

        st.markdown("##### 💻 Verbatim Code: Derived Biogeochemical Feature Engineering (`src/data/usgs_pipeline.py`)")
        st.code(_read_code_slice(project_root, "src/data/usgs_pipeline.py", 353, 400), language="python")

    # ── TAB 5: STEP 5 - SCALING, ENCODING & SPLIT ──────────────────
    with tab_scale:
        st.markdown("#### ⚖️ Step 5: Leak-Free Imputation, Scaling & Encoding (Pre-Modeling Transform Only)")
        st.caption(
            "Only the preprocessing transforms are showcased here. Downstream ML estimators remain hidden in the voluntary dropdown below."
        )

        if not usgs_df.empty:
            sample_cols = [c for c in ["ph", "dissolved_oxygen_mg_l", "turbidity_fnu", "specific_conductance_us_cm"] if c in usgs_df.columns]
            valid_cols = [c for c in sample_cols if usgs_df[c].notna().any()]
            if valid_cols:
                sub = usgs_df[valid_cols].dropna(how="all").head(500).copy()
                active_cols = [c for c in valid_cols if sub[c].notna().any()]
                if active_cols and not sub.empty:
                    sub = sub[active_cols]
                    imp = SimpleImputer(strategy="median")
                    imputed_arr = imp.fit_transform(sub)
                    scaler_choice = st.radio(
                        "Select Scaling Method to Preview Live:",
                        ["RobustScaler (Median & IQR — Outlier Resistant)", "StandardScaler (Mean & Std Dev — Z-Score)"],
                        horizontal=True,
                        key="s4_scaler_choice",
                    )
                    if scaler_choice.startswith("RobustScaler"):
                        scaled_arr = RobustScaler().fit_transform(imputed_arr)
                        suffix = "robust_scaled"
                    else:
                        scaled_arr = StandardScaler().fit_transform(imputed_arr)
                        suffix = "std_scaled"

                    df_raw_preview = pd.DataFrame(sub.head(5).values, columns=active_cols).round(3)
                    df_scaled_preview = pd.DataFrame(scaled_arr[:5], columns=[f"{c}_{suffix}" for c in active_cols]).round(3)

                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Before Scaling (Raw Sensor Units — Mixed Scales):**")
                        st.dataframe(df_raw_preview, width="stretch", hide_index=True)
                    with c2:
                        st.markdown(f"**After `SimpleImputer(median)` + `{scaler_choice.split(' ')[0]}`:**")
                        st.dataframe(df_scaled_preview, width="stretch", hide_index=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("##### 💻 Median Imputer + `RobustScaler` (`scripts/train_anomaly_model_v2.py`)")
            st.code(_read_code_slice(project_root, "scripts/train_anomaly_model_v2.py", 63, 91), language="python")
        with col_b:
            st.markdown("##### 💻 Temporal Split & `ColumnTransformer` (`scripts/train_risk_model_v2.py`)")
            st.code(_read_code_slice(project_root, "scripts/train_risk_model_v2.py", 80, 146), language="python")

    _render_hidden_optional_code_dropdown(project_root, key_prefix="screen4")


# ---------------------------------------------------------------------------
# SCREEN 5: DATABASE & DATA WAREHOUSE DEMO
# ---------------------------------------------------------------------------

def _ensure_demo_sqlite_seed(active_payload: Dict[str, Any], ai_result: Dict[str, Any]) -> None:
    """Seed minimal representative telemetry rows only if SQLite table is empty."""
    init_db()
    if get_recent_telemetry_records(limit=1):
        return
    demo_packets = [
        (
            {
                "node_id": "HIRAKUD_NODE_001",
                "ph": 7.42, "dissolved_oxygen": 8.65, "turbidity": 4.5,
                "conductivity": 280.0, "temperature": 21.3, "nitrate": 2.1, "phosphate": 0.04,
            },
            {
                "anomaly_detection": {"status": "Normal", "score": -0.06},
                "risk_prediction": {"class": "SAFE", "probability": 0.96},
                "biological_health": {"score": 94.0},
                "final_status": "SAFE",
                "xai_explanation": {"prediction_reason": "Seeded baseline nominal telemetry."},
            },
        ),
        (
            {
                "node_id": "HIRAKUD_NODE_001",
                "ph": 8.65, "dissolved_oxygen": 1.80, "turbidity": 32.0,
                "conductivity": 680.0, "temperature": 28.4, "nitrate": 22.5, "phosphate": 2.40,
            },
            {
                "anomaly_detection": {"status": "Anomaly", "score": 0.14},
                "risk_prediction": {"class": "CRITICAL", "probability": 0.91},
                "biological_health": {"score": 38.0},
                "final_status": "CRITICAL",
                "xai_explanation": {"prediction_reason": "Seeded hypoxic + nutrient eutrophication event."},
            },
        ),
        (
            {
                "node_id": "HIRAKUD_NODE_001",
                "ph": float(active_payload.get("ph", 7.4)),
                "dissolved_oxygen": float(active_payload.get("dissolved_oxygen", 8.0)),
                "turbidity": float(active_payload.get("turbidity", 5.0)),
                "conductivity": float(active_payload.get("specific_conductance", 300.0)),
                "temperature": float(active_payload.get("temperature", 21.0)),
                "nitrate": active_payload.get("nitrate_mg_l"),
                "phosphate": active_payload.get("phosphate_mg_l"),
            },
            ai_result or {},
        ),
    ]
    for pkt, res in demo_packets:
        insert_telemetry_record(pkt, res)


def render_database_warehouse_screen(
    project_root: Path,
    active_payload: Dict[str, Any],
    ai_result: Dict[str, Any],
) -> None:
    """Render Screen 5 dedicated to Data Warehouse (Parquet) + Operational DB (SQLite) Demo."""
    st.markdown("### 🗄️ Database & Data Warehouse Demo (OLAP Parquet + OLTP SQLite)")
    st.caption(
        "Complete Dual-Tier Storage Architecture: Columnar Apache Parquet Warehouse (77,641 Events) + Indexed SQLite Operational Telemetry DB"
    )

    _ensure_demo_sqlite_seed(active_payload, ai_result)
    usgs_df = _load_usgs_parquet(str(project_root), "usgs_water_quality.parquet")
    test_usgs_df = _load_usgs_parquet(str(project_root), "test_usgs_water_quality.parquet")

    tab_explain, tab_warehouse, tab_sqlite = st.tabs([
        "📖 Explain Mode (Step-by-Step Architecture)",
        "🏛️ Analytical Data Warehouse (Apache Parquet)",
        "🗄️ Operational Telemetry DB (Live SQLite & SQL Console)",
    ])

    # ── TAB 1: EXPLAIN MODE ────────────────────────────────────────
    with tab_explain:
        st.markdown("#### 📖 Explain Mode — How We Built the Data Warehouse & Database Layer")
        db_steps = [
            (
                "Step 1",
                "Enforced Canonical Data Contract (Pydantic & Parquet Typing)",
                "Defined strict frozen schemas in src/data/schemas.py (CanonicalObservation, SensorQualityFlag, BatchIngestionAuditReport) with SHA-256 deterministic observation keys.",
                "Raw environmental CSVs lack primary keys and type constraints, leading to silent schema drift and duplicate rows during warehouse ingestion.",
                "Enforced strict schema validation and deterministic 24-char SHA-256 observation IDs across 7.57M records with full audit provenance.",
                "src/data/schemas.py & src/data/pipeline.py",
            ),
            (
                "Step 2",
                "Built Multi-Domain Analytical Data Warehouse (Snappy Apache Parquet)",
                "Joined physical/chemical and biological USGS tables on composite keys (MonitoringLocationIdentifier, ActivityStartDate, ActivityIdentifier), engineered stoichiometry columns, and exported columnar Parquet.",
                "SQL row-stores or 800MB+ CSVs are slow for analytical column scans (OLAP) across 49 scientific features and waste storage space.",
                "Achieved compact 2.3 MB Snappy Parquet analytical storage holding 77,641 harmonized monitoring events × 49 features ready for fast EDA and batch mining.",
                "src/data/usgs_pipeline.py (run_harmonization_pipeline) -> data/processed/usgs_water_quality.parquet",
            ),
            (
                "Step 3",
                "Built Operational Real-Time Telemetry Database (Indexed SQLite OLTP)",
                "Designed telemetry_records SQLite table in iot/database.py with B-tree indexes on (timestamp) and (node_id), storing live sensor readings alongside full raw JSON provenance.",
                "An analytical Parquet warehouse is immutable/batch-oriented and unsuitable for 5-second incremental writes from live IoT sensors and dashboard telemetry.",
                "Enabled instant row-level inserts, indexed time-series history queries, and live SQL inspection directly from the command console.",
                "iot/database.py (init_db, insert_telemetry_record, get_recent_telemetry_records)",
            ),
        ]
        for s in db_steps:
            _render_explain_card(*s)

    # ── TAB 2: ANALYTICAL DATA WAREHOUSE (PARQUET) ─────────────────
    with tab_warehouse:
        st.markdown("#### 🏛️ Analytical Data Warehouse (`data/processed/usgs_water_quality.parquet`)")

        if not usgs_df.empty:
            w1, w2, w3, w4 = st.columns(4)
            w1.metric("Warehouse Fact Rows", f"{len(usgs_df):,}")
            w2.metric("Engineered Columns", f"{usgs_df.shape[1]}")
            w3.metric("Unique Monitoring Stations", f"{usgs_df['MonitoringLocationIdentifier'].nunique():,}")
            w4.metric("Smoke-Test Partition Rows", f"{len(test_usgs_df):,}" if not test_usgs_df.empty else "0")

            # Live Warehouse Filtering Demo
            st.markdown("##### 🔎 Interactive Warehouse Slice & Feature Query")
            f1, f2 = st.columns(2)
            orgs = ["ALL"] + sorted(usgs_df["OrganizationFormalName"].dropna().unique().tolist())[:30]
            sel_org = f1.selectbox("Filter by Organization:", orgs, key="s5_wh_org")
            events = ["ALL"] + sorted(usgs_df["HydrologicEvent"].dropna().unique().tolist())
            sel_ev = f2.selectbox("Filter by Hydrologic Event:", events, key="s5_wh_event")

            filtered_wh = usgs_df
            if sel_org != "ALL":
                filtered_wh = filtered_wh[filtered_wh["OrganizationFormalName"] == sel_org]
            if sel_ev != "ALL":
                filtered_wh = filtered_wh[filtered_wh["HydrologicEvent"] == sel_ev]

            st.caption(f"Showing top 20 of **{len(filtered_wh):,}** matching warehouse rows:")
            preview_cols = [
                c for c in [
                    "MonitoringLocationIdentifier", "ActivityStartDate", "HydrologicEvent",
                    "ph", "dissolved_oxygen_mg_l", "turbidity_fnu", "specific_conductance_us_cm",
                    "nitrate_mg_l", "orthophosphate_mg_l", "total_nitrogen_est_mg_l",
                    "total_phosphorus_est_mg_l", "n_to_p_ratio", "ssc_to_turbidity_ratio",
                    "bio_taxa_richness",
                ]
                if c in filtered_wh.columns
            ]
            st.dataframe(filtered_wh[preview_cols].head(20), width="stretch", hide_index=True)

            # Column Completeness Audit Output
            completeness = (usgs_df.notna().mean() * 100).round(2).reset_index()
            completeness.columns = ["Column", "Non-Null Completeness (%)"]
            fig_comp = px.bar(
                completeness.sort_values("Non-Null Completeness (%)", ascending=False).head(25),
                x="Column",
                y="Non-Null Completeness (%)",
                title="Data Warehouse Feature Completeness (Top 25 Columns)",
            )
            fig_comp.update_layout(template="plotly_dark", height=330)
            st.plotly_chart(fig_comp, width="stretch")
        else:
            st.warning("USGS Parquet warehouse file not found at `data/processed/usgs_water_quality.parquet`.")

        col_sc, col_et = st.columns(2)
        with col_sc:
            st.markdown("##### 💻 Canonical Warehouse Schema (`src/data/schemas.py`)")
            st.code(_read_code_slice(project_root, "src/data/schemas.py", 28, 113), language="python")
        with col_et:
            st.markdown("##### 💻 Composite Merge & Parquet Export (`src/data/usgs_pipeline.py`)")
            st.code(_read_code_slice(project_root, "src/data/usgs_pipeline.py", 402, 451), language="python")

    # ── TAB 3: OPERATIONAL TELEMETRY DB (SQLITE) ───────────────────
    with tab_sqlite:
        st.markdown("#### 🗄️ Operational Telemetry Database Demo (`iot/database.py` -> SQLite)")

        b1, b2, b3 = st.columns([1.2, 1.2, 1.6])
        with b1:
            if st.button("➕ Insert Active Dashboard Telemetry to SQLite", type="primary", width="stretch"):
                pkt = {
                    "node_id": "HIRAKUD_NODE_001",
                    "ph": float(active_payload.get("ph", 7.42)),
                    "dissolved_oxygen": float(active_payload.get("dissolved_oxygen", 8.65)),
                    "turbidity": float(active_payload.get("turbidity", 4.5)),
                    "conductivity": float(active_payload.get("specific_conductance", 280.0)),
                    "temperature": float(active_payload.get("temperature", 21.3)),
                    "nitrate": active_payload.get("nitrate_mg_l"),
                    "phosphate": active_payload.get("phosphate_mg_l"),
                }
                new_id = insert_telemetry_record(pkt, ai_result)
                st.success(f"Inserted record `id={new_id}` into SQLite!")
        with b2:
            if st.button("🧪 Insert Synthetic Acid Spill Test Row", width="stretch"):
                spill_pkt = {
                    "node_id": "HIRAKUD_NODE_001",
                    "ph": 2.90, "dissolved_oxygen": 3.40, "turbidity": 75.0,
                    "conductivity": 2250.0, "temperature": 25.0, "nitrate": 8.0, "phosphate": 0.4,
                }
                spill_ai = {
                    "anomaly_detection": {"status": "Anomaly", "score": 0.19},
                    "risk_prediction": {"class": "CRITICAL", "probability": 0.94},
                    "biological_health": {"score": 31.0},
                    "final_status": "CRITICAL",
                    "xai_explanation": {"prediction_reason": "Live SQLite demo insert: severe acidic intrusion."},
                }
                new_id = insert_telemetry_record(spill_pkt, spill_ai)
                st.success(f"Inserted Acid Spill row `id={new_id}`!")
        with b3:
            with sqlite3.connect(DB_PATH) as conn:
                total_sqlite_rows = int(conn.execute("SELECT COUNT(*) FROM telemetry_records").fetchone()[0])
            st.metric("Total Rows Currently in `telemetry_records`", f"{total_sqlite_rows:,}")

        st.markdown("##### 💻 Interactive Read-Only SQL Console (Live Query Execution)")
        preset_queries = {
            "Latest 15 Telemetry Records": (
                "SELECT id, timestamp, node_id, ph, dissolved_oxygen, turbidity, conductivity, "
                "risk_label, final_status, eco_health_index\n"
                "FROM telemetry_records\nORDER BY id DESC\nLIMIT 15;"
            ),
            "Count & Avg Sensor Values Grouped by Final Status": (
                "SELECT final_status,\n"
                "       COUNT(*) AS record_count,\n"
                "       ROUND(AVG(ph), 2) AS avg_ph,\n"
                "       ROUND(AVG(dissolved_oxygen), 2) AS avg_do,\n"
                "       ROUND(AVG(turbidity), 2) AS avg_turbidity,\n"
                "       ROUND(AVG(conductivity), 1) AS avg_conductivity\n"
                "FROM telemetry_records\nGROUP BY final_status;"
            ),
            "Filter Critical / Anomaly Events Only": (
                "SELECT id, timestamp, ph, dissolved_oxygen, turbidity, conductivity, final_status, prediction_reason\n"
                "FROM telemetry_records\nWHERE final_status = 'CRITICAL' OR anomaly_status = 'Anomaly'\nORDER BY id DESC;"
            ),
            "Inspect SQLite Table Schema (PRAGMA table_info)": "PRAGMA table_info(telemetry_records);",
        }
        sel_q_name = st.selectbox("Choose Preset SQL Query:", list(preset_queries.keys()), key="s5_sql_preset")
        if st.session_state.get("s5_last_sql_preset") != sel_q_name:
            st.session_state["s5_last_sql_preset"] = sel_q_name
            st.session_state["s5_sql_editor"] = preset_queries[sel_q_name]
        sql_text = st.text_area("SQL Query (Read-Only `SELECT` / `PRAGMA` / `WITH`):", height=110, key="s5_sql_editor")

        cleaned_sql = sql_text.strip().rstrip(";").strip()
        upper_sql = cleaned_sql.upper()
        if ";" in cleaned_sql:
            st.warning("Read-only console accepts a single SQL statement at a time.")
        elif upper_sql.startswith(("SELECT", "PRAGMA", "WITH")):
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    q_df = pd.read_sql_query(cleaned_sql, conn)
                st.dataframe(q_df, width="stretch", hide_index=True)
            except Exception as exc:
                st.error(f"SQL Execution Error: {exc}")
        else:
            st.warning("Read-only console: query must start with `SELECT`, `PRAGMA`, or `WITH`.")

        st.markdown("##### 💻 Complete Verbatim Codebase (`iot/database.py`)")
        st.code(_read_code_slice(project_root, "iot/database.py", 1, 145), language="python")

    _render_hidden_optional_code_dropdown(project_root, key_prefix="screen5")
