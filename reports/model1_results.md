# Model 1 Anomaly Detection (v2.0) Evaluation Report

**Model**: Isolation Forest (`v2.0`)
**Dataset**: `data/labeled/operational_risk_labels_v2.parquet`
**Validation Strategy**: Strict Temporal Hold-Out (2024 Train $\rightarrow$ 2025 Test)
**Features Evaluated**: `ph, dissolved_oxygen, turbidity, specific_conductance, fdom`
**Train Records**: 80,000 (2024)
**Test Records**: 20,000 (2025)
**Evaluation Date**: 2026-08-15 08:48:32 UTC

---

## 1. Anomaly Detection Summary

| Metric | 2024 Train Partition | 2025 Test Partition |
|---|---:|---:|
| **Total Sampled Records** | 80,000 | 20,000 |
| **Normal Observations** | 76,000 (95.00%) | 17,649 (88.25%) |
| **Detected Anomalies** | 4,000 (**5.00%**) | 2,351 (**11.76%**) |

## 2. Site-Wise Anomaly Distribution (2025 Test Set)

| Site | Normal | Anomaly | Total | Anomaly Rate |
|---|---:|---:|---:|---:|
| **ARIK** | 4,417 | 1,122 | 5,539 | **20.26%** |
| **BARC** | 285 | 292 | 577 | **50.61%** |
| **BIGC** | 4,909 | 712 | 5,621 | **12.67%** |
| **BLDE** | 5,444 | 69 | 5,513 | **1.25%** |
| **BLUE** | 2,594 | 156 | 2,750 | **5.67%** |

## 3. Anomaly vs. Operational Risk Cross-Tabulation

> [!NOTE]
> Per `Rules.md` 2.3, Anomaly detection is independent of contamination confirmation. Below demonstrates the empirical relationship on unseen 2025 data:

| Risk State (v2.0) | Normal | Anomaly | Total | Anomaly Rate |
|---|---:|---:|---:|---:|
| **CRITICAL** | 61 | 734 | 795 | **92.33%** |
| **INSUFFICIENT_DATA** | 3,307 | 37 | 3,344 | **1.11%** |
| **SAFE** | 11,840 | 254 | 12,094 | **2.10%** |
| **WARNING** | 2,441 | 1,326 | 3,767 | **35.20%** |

## 4. Sample Predictions on Unseen 2025 Records

| Observation ID | Site | pH | DO (mg/L) | Turbidity (FNU) | SpCond (µS/cm) | fDOM (QSU) | Anomaly Score | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Row 9 | ARIK | 7.63 | 3.74 | 19.81 | 380.9 | 175.9 | **0.0856** | `Anomaly` |
| Row 24 | ARIK | nan | nan | 447.89 | -0.0 | 36.2 | **0.0977** | `Anomaly` |
| Row 27 | BIGC | 7.03 | 0.00 | 0.98 | 202.4 | 23.4 | **0.0100** | `Anomaly` |
| Row 32 | BIGC | 9.22 | 0.00 | 1.90 | 191.7 | 18.6 | **0.0298** | `Anomaly` |
| Row 33 | BIGC | 7.02 | 0.00 | 0.86 | 210.8 | 21.9 | **0.0133** | `Anomaly` |

## 5. Architectural Improvements over Legacy Model 1

1. **Full Temporal Separation**: Trained on 2024 and validated on 2025; no data leakage.
2. **Robust Multi-Parameter Scaling**: Utilizes `RobustScaler` to prevent extreme flash turbidity/SpCond spikes from skewing the spatial tree partitioning.
3. **Continuous Anomaly Scoring**: Produces both calibrated continuous `anomaly_score` and discrete `anomaly_status`.
4. **Decoupled Architecture**: Zero leakage into or from risk classification labels.
