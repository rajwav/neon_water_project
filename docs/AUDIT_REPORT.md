# Technical Audit Report: NEON Water Intelligence System

**Auditor**: Lead AI Engineer & System Architect  
**Project**: SIH Water Intelligence Platform (NEON & USGS Multi-Domain Sensing)  
**Date**: August 2026  
**Repository**: `neon_water_project`  
**Status**: Comprehensive Baseline Audit Complete

---

## 1. Executive Summary

The **NEON Water Intelligence System** is an AI-powered water contamination detection, ecological risk assessment, and digital twin monitoring platform. The codebase currently possesses a functional end-to-end prototype trained on high-frequency continuous NEON surface water telemetry (DP1.20288.001 & DP1.20093.001), featuring a 2-stage ML pipeline (Isolation Forest + Random Forest), a deterministic environmental safety decision engine, a FastAPI inference backend, a Streamlit operational dashboard, and a Wokwi ESP32 digital twin simulator.

Two large-scale real-world USGS/WQP datasets were recently added:
1. `resultphyschem.csv` (445,998 rows, 81 columns, ~261 MB)
2. `biologicalresult.csv` (445,998 rows, 156 columns, ~265 MB)

This report details the architectural state of the repository, data characteristics, system gaps, and recommended expansion roadmap for SIH presentation.

---

## 2. Repository Structure & Component Audit

### 2.1 Workspace Inventory

| Directory / File | Description | Operational Status |
|---|---|---|
| `backend/main.py` | FastAPI application (`/health`, `/predict`) with Pydantic v2 validation | **Active & Passing Tests** (v2.2.0) |
| `backend/model_loader.py` | Inference orchestrator coordinating Model 1, Model 2, and Environmental Engine | **Active** |
| `backend/environmental_engine.py` | WQI, oxygen/chemical stress indices, deterministic safety guardrails, XAI | **Active** |
| `dashboard/app.py` | Streamlit user interface with live telemetry, gauges, XAI panels, and trend charts | **Active** |
| `models/v2/anomaly_detector_v2.joblib` | Model 1: Isolation Forest trained on 50,000 NEON continuous records | **Trained & Serialized** |
| `models/v2/risk_classifier_v2.joblib` | Model 2: Balanced Random Forest trained on labeled operational risk classes | **Trained & Serialized** |
| `data/raw/neon/` | Raw continuous sensor CSV files (ARIK, BARC, BIGC, BLDE, BLUE) | **Curated** |
| `data/labeled/` | Labeled operational risk parquet dataset (`operational_risk_labels_v2.parquet`) | **Curated** |
| `resultphyschem.csv` | USGS Physical & Chemical discrete water quality observations (445,998 rows) | **Raw / Unprocessed** |
| `biologicalresult.csv` | USGS Biological & Taxonomic water quality observations (445,998 rows) | **Raw / Unprocessed** |
| `wokwi/` | ESP32 digital twin simulation (`sketch.ino`, `diagram.json`, `libraries.txt`) | **Active & Calibrated** (v3.0) |
| `tests/test_backend_api.py` | Pytest integration test suite (9 test cases covering safety overrides) | **Passing (9/9)** |
| `src/data/`, `src/labels/` | Data validation, pipeline ingestion, and heuristic labeler modules | **Functional baseline** |

### 2.2 Environment & Dependency Status

- **Python Runtime**: Python 3.14.6 in isolated virtual environment (`.venv/`)
- **Core ML / Data Stack**: `pandas 3.0.5`, `numpy 2.5.2`, `scikit-learn 1.9.0`, `pyarrow 24.0.0`, `joblib 1.5.3`
- **Serving & UI Stack**: `fastapi 0.141.1`, `uvicorn 0.52.1`, `streamlit 1.61.1`, `pydantic 2.13.4`, `httpx 0.28.1`
- **Visualization**: `matplotlib 3.11.1`, `seaborn 0.13.2`, `plotly 6.9.0`
- **Testing**: `pytest 9.1.1`

---

## 3. Dataset Audit: USGS Physical/Chemical vs. Biological

### 3.1 Dataset Profile Comparison

```
┌──────────────────────────────────────┬──────────────────────────┬──────────────────────────┐
│ Characteristic                       │ resultphyschem.csv       │ biologicalresult.csv     │
├──────────────────────────────────────┼──────────────────────────┼──────────────────────────┤
│ Total Records                        │ 445,998 rows             │ 445,998 rows             │
│ Column Count                         │ 81 columns               │ 156 columns              │
│ File Size                            │ 261.3 MB                 │ 265.0 MB                 │
│ Format Standard                      │ WQP / WQX Standard       │ WQP / WQX Standard       │
│ Unique Sampling Activities           │ 89,240 sampling events   │ 89,240 sampling events   │
│ Temporal Range                       │ Multi-year historical    │ Multi-year historical    │
│ Spatial Coverage                     │ USGS Monitoring Stations │ USGS Monitoring Stations │
└──────────────────────────────────────┴──────────────────────────┴──────────────────────────┘
```

### 3.2 Key Measurement Parameters in `resultphyschem.csv`

1. **Suspended Sediment Concentration (SSC)**: ~174,000 observations (critical for sediment contamination).
2. **Water Temperature**: ~83,000 observations ($^\circ\text{C}$).
3. **Specific Conductance**: ~29,000 observations ($\mu\text{S/cm}$).
4. **Nutrient Suite**:
   - Orthophosphate & Phosphorus: ~42,000 observations ($\text{mg/L as P}$).
   - Nitrate, Nitrite, Ammonia, Mixed Nitrogen: ~85,000 observations ($\text{mg/L}$).
5. **pH & Acidity**: ~24,000 observations (Standard units & $\text{H}^+$ acidity).
6. **Turbidity**: ~16,000 observations ($\text{FNU / NTU}$).
7. **Dissolved Oxygen (DO)**: Discrete sampling values ($\text{mg/L}$).
8. **UV 254 & Optical Absorption (Sag)**: Dissolved organic carbon absorption proxies.

### 3.3 Biological & Taxonomic Parameters in `biologicalresult.csv`

1. **Taxa Identification (`SubjectTaxonomicName`)**:
   - Dominant bioindicator organisms: *Ceriodaphnia dubia* (water flea), *Hyalella azteca* (amphipod crustacean), *Pimephales promelas* (fathead minnow), *Thalassiosira pseudonana* (diatom).
2. **Biological Intent**: Ecotoxicity bioassays, population density, community assemblages.
3. **Taxonomic Pollution Tolerance**: Numerical/categorical sensitivity indices measuring organism resilience to organic/chemical stress.

### 3.4 Data Quality Findings & Identified Issues

1. **Long-Format Key-Value Structure**: Both datasets are stored in narrow long format (one measurement per row with `CharacteristicName` and `ResultMeasureValue`). A single water sample spanning 15 parameters occupies 15 rows.
2. **Mixed Units**: Parameters like Turbidity have mixed units (`FNU`, `NTU`, `NTRU`). Specific Conductance uses `uS/cm @25C`. Phosphorus has `mg/l as P` vs `mg/l as PO4`.
3. **Detection Limits & Qualifiers**: Non-detects (e.g. `< 0.05 mg/L`) appear as text in `ResultMeasureValue` with flags in `ResultDetectionConditionText` and `DetectionQuantitationLimitMeasure/MeasureValue`.
4. **Biological Sparsity**: Bioassay taxa are recorded on specific toxicological/biological sampling runs (~9,671 taxonomic records), while physicochemical parameters are recorded continuously/routinely.

---

## 4. Problems Identified in Current Codebase

1. **Dataset Disconnect**:
   - The current ML models (`Model 1` and `Model 2`) were trained exclusively on NEON continuous sensors (`data/raw/neon/`).
   - The newly downloaded USGS physical/chemical and biological datasets (`resultphyschem.csv` and `biologicalresult.csv`, 445k rows each) are not yet integrated into the feature engineering pipeline.
2. **Long-to-Wide Reshaping Needed**:
   - The platform lacks an automated ingestion pipeline to pivot USGS long-format observations into wide feature vectors `(ActivityIdentifier, Site, Timestamp -> pH, DO, Turbidity, SSC, Nitrate, Phosphate, BioIndex)`.
3. **Biological Ecotoxicity Fusion Missing**:
   - Biological indicator metrics (e.g., organism mortality, species abundance, Hilsenhoff Biotic Index) have not been fused with physical-chemical water chemistry.
4. **Static Inference Pipeline**:
   - While real-time IoT/Wokwi streaming and manual slider testing work, batch offline analysis of historical USGS water bodies is not yet exposed in the Streamlit UI.

---

## 5. Recommended Architecture & Immediate Next Steps

1. **Phase A (Data Ingestion & Harmonization Pipeline)**:
   - Build a robust ETL module (`src/data/usgs_pipeline.py`) that parses `resultphyschem.csv` and `biologicalresult.csv`, standardizes measurement units, imputes or handles below-detection-limit (BDL) values, and pivots rows into unified multi-parameter sampling events.
2. **Phase B (Biological-Chemical Feature Fusion)**:
   - Create multi-domain feature vectors combining physical chemistry, nutrient stoichiometry (N:P ratios), sediment loading (SSC), and biological toxicity responses.
3. **Phase C (Enhanced Multi-Domain Model Suite)**:
   - Train expanded multi-domain models:
     - **Model 1B**: Multivariate Anomaly Detection across physical, chemical, and biological features.
     - **Model 2B**: Ecotoxicity & Contamination Classifier predicting ecosystem health and regulatory compliance.
4. **Phase D (Unified Platform & Dashboard Integration)**:
   - Connect the upgraded data pipeline and models to FastAPI and the Streamlit dashboard, providing both real-time IoT stream monitoring and historical USGS catchment batch analytics.
