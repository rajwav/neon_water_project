# USGS Multi-Domain AI Model Evaluation Report (v3.0)

**Project**: SIH NEON & USGS Water Intelligence Platform  
**Dataset**: `data/processed/usgs_water_quality.parquet`  
**Training Regime**: 17,450 Verified Multi-Domain Sampling Events  
**Artifacts**: `models/v3/anomaly_detector_usgs.joblib` & `models/v3/risk_classifier_usgs.joblib`

---

## 1. Executive Summary

This report documents the performance of the upgraded v3 multi-domain machine learning models trained on harmonized physical, chemical, nutrient, sediment, and biological observations from the USGS Water Quality Portal.

- **Total Assessed Sampling Events**: **17,450**
- **Model 1 (Isolation Forest Anomaly Detector)**: Outlier contamination baseline calibrated at $8.0\%$.
- **Model 2 (Balanced Random Forest Risk Classifier)**: Achieved **99.77\% overall accuracy** and **0.9963 Macro F1-Score** across multi-class operational states.

---

## 2. Model 2 (Operational Risk Classifier) Performance Metrics

### Overall Classification Summary
- **Overall Accuracy**: **99.77%**
- **Macro Average Precision**: **99.79%**
- **Macro Average Recall**: **99.47%**
- **Macro Average F1-Score**: **0.9963**
- **Weighted Average F1-Score**: **0.9977**
- **5-Fold Cross-Validation Macro F1**: **0.9961 (+/- 0.0010)**

### Per-Class Performance Breakdown

| Operational State | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **`SAFE`** | 99.77% | 99.96% | 0.9987 | 2,638.0 |
| **`WARNING`** | 99.60% | 99.01% | 0.9930 | 504.0 |
| **`CRITICAL`** | 100.00% | 99.43% | 0.9971 | 348.0 |

---

## 3. Multi-Domain Feature Importance Ranking (Gini Reduction)

| `turbidity_fnu` | 0.2958 | 29.58% |
| `specific_conductance_us_cm` | 0.1641 | 16.41% |
| `ph` | 0.1437 | 14.37% |
| `dissolved_oxygen_mg_l` | 0.1415 | 14.15% |
| `suspended_sediment_conc_mg_l` | 0.0749 | 7.49% |
| `ssc_to_turbidity_ratio` | 0.0669 | 6.69% |
| `total_phosphorus_est_mg_l` | 0.0631 | 6.31% |
| `temperature_c` | 0.0314 | 3.14% |
| `total_nitrogen_est_mg_l` | 0.0126 | 1.26% |
| `n_to_p_ratio` | 0.0060 | 0.60% |
| `bio_taxa_richness` | 0.0000 | 0.00% |
| `biological_sampled_flag` | 0.0000 | 0.00% |


---

## 4. Model 1 (Isolation Forest Anomaly Detector) Baseline

- **Training Samples**: 17,450
- **Calibrated Inliers (Normal)**: 16,054 (92.0%)
- **Calibrated Outliers (Anomalies)**: 1,396 (8.0%)
- **Mean Decision Function Score**: 0.0264 (Std: 0.0240)

---

## 5. Diagnostic Figures

1. **Confusion Matrix**: `reports/usgs_confusion_matrix.png`
2. **Feature Importance Plot**: `reports/usgs_feature_importance.png`
3. **Spearman Correlation Matrix**: `reports/usgs_correlation_matrix.png`
