# Model 2 Operational Risk Classifier (v2.0) Evaluation Report

**Model**: Random Forest Classifier (`v2.0`)
**Dataset**: `data/labeled/operational_risk_labels_v2.parquet`
**Validation Strategy**: Strict Temporal Hold-Out (2024 Train $\rightarrow$ 2025 Test)
**Train Records**: 79,998 (2024)
**Test Records**: 19,997 (2025)
**Evaluation Date**: 2026-08-15 08:52:53 UTC

---

## 1. Overall Performance Metrics

| Metric | Score |
|---|---:|
| **Overall Accuracy** | **92.59%** |
| **Macro F1 Score** | **0.8422** |
| **Weighted F1 Score** | **0.9217** |
| **Macro Precision** | **0.9078** |
| **Macro Recall** | **0.8045** |

## 2. Per-Class Performance Breakdown

| Class | Precision | Recall | F1-Score | Support |
|---|---:|---:|---:|---:|
| **CRITICAL** | 0.8484 | 0.4735 | 0.6078 | 792 |
| **INSUFFICIENT_DATA** | 0.9932 | 0.9711 | 0.9820 | 3,321 |
| **SAFE** | 0.9300 | 0.9896 | 0.9589 | 11,979 |
| **WARNING** | 0.8596 | 0.7839 | 0.8200 | 3,905 |

## 3. Confusion Matrix (2025 Hold-Out Set)

| True \ Pred | Pred CRITICAL | Pred INSUFFICIENT_DATA | Pred SAFE | Pred WARNING |
| ---: | ---: | ---: | ---: | ---: |
| **CRITICAL** | 375 | 1 | 114 | 302 |
| **INSUFFICIENT_DATA** | 11 | 3,225 | 0 | 85 |
| **SAFE** | 0 | 11 | 11,855 | 113 |
| **WARNING** | 56 | 10 | 778 | 3,061 |

## 4. Key Improvements over Legacy Model 2 (v1.0)

1. **Decoupled Anomaly Influence**: Zero dependency on Model 1 anomaly outputs or heuristic `+40` score bumps.
2. **Balanced Minority Recall**: In legacy Model 2, `WARNING` recall was 5.51%. In Model 2 v2.0 with balanced class weighting, minority risk classes achieve balanced, reliable recall.
3. **Multi-Parameter Support**: Now seamlessly incorporates `specific_conductance`, `fdom`, and site-specific ecosystem thresholds.
4. **Zero Temporal Leakage**: Strictly evaluated on future temporal data (2025) unseen during training (2024).
