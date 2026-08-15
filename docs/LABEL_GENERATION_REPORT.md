# Label Generation Report: `operational_risk_labels_v2.0`

**Generated**: 2026-08-15T08:13:42Z
**Label Version**: `operational_risk_labels_v2.0`
**Specification**: `docs/LABEL_SPEC_v2.md`
**Processing Time**: 488.5 seconds
**Output**: `data/labeled/operational_risk_labels_v2.parquet`

---

## 1. Records Processed

| Metric | Count |
|---|---:|
| **Total Records** | **7,579,008** |
| 2024 Partition | 3,794,688 |
| 2025 Partition | 3,784,320 |

## 2. Risk Label Distribution

| Label | Count | Percentage |
|---|---:|---:|
| **SAFE** | 4,904,355 | 64.71% |
| **WARNING** | 1,032,835 | 13.63% |
| **CRITICAL** | 177,155 | 2.34% |
| **INSUFFICIENT_DATA** | 1,464,663 | 19.33% |

## 3. Site-Wise Label Distribution

| Site | CRITICAL | INSUFFICIENT_DATA | SAFE | WARNING | All |
| ---: | ---: | ---: | ---: | ---: | ---: |
| **ARIK** | 74,835 | 588,499 | 1,027,280 | 414,666 | 2,105,280 |
| **BARC** | 6,236 | 31,024 | 147,110 | 26,158 | 210,528 |
| **BIGC** | 74,532 | 222,535 | 1,461,674 | 346,539 | 2,105,280 |
| **BLDE** | 3,329 | 142,066 | 1,814,840 | 145,045 | 2,105,280 |
| **BLUE** | 18,223 | 480,539 | 453,451 | 100,427 | 1,052,640 |
| **All** | 177,155 | 1,464,663 | 4,904,355 | 1,032,835 | 7,579,008 |

## 4. Label Confidence Distribution

| Confidence | Count | Percentage |
|---|---:|---:|
| **HIGH** | 5,746,019 | 75.81% |
| **MODERATE** | 115,304 | 1.52% |
| **LOW** | 253,022 | 3.34% |
| **UNRELIABLE** | 1,464,663 | 19.33% |

## 5. Data Completeness Distribution

| Completeness | Count | Percentage |
|---|---:|---:|
| **FULL** | 5,746,019 | 75.81% |
| **PARTIAL** | 115,304 | 1.52% |
| **DEGRADED** | 519,408 | 6.85% |
| **INSUFFICIENT** | 1,198,277 | 15.81% |

## 6. Per-Parameter State Distribution

### ph

| State | Count | Percentage |
|---|---:|---:|
| NORMAL | 5,903,430 | 77.89% |
| ELEVATED | 47,974 | 0.63% |
| EXTREME | 67,014 | 0.88% |
| MISSING | 1,539,904 | 20.32% |
| SENSOR_ARTIFACT | 0 | 0.00% |
| INSTRUMENT_LIMIT | 20,686 | 0.27% |

### dissolved_oxygen

| State | Count | Percentage |
|---|---:|---:|
| NORMAL | 5,512,398 | 72.73% |
| ELEVATED | 140,863 | 1.86% |
| EXTREME | 302,252 | 3.99% |
| MISSING | 1,606,596 | 21.20% |
| SENSOR_ARTIFACT | 0 | 0.00% |
| INSTRUMENT_LIMIT | 16,899 | 0.22% |

### turbidity

| State | Count | Percentage |
|---|---:|---:|
| NORMAL | 5,773,432 | 76.18% |
| ELEVATED | 574,257 | 7.58% |
| EXTREME | 80,224 | 1.06% |
| MISSING | 1,038,276 | 13.70% |
| SENSOR_ARTIFACT | 112,187 | 1.48% |
| INSTRUMENT_LIMIT | 632 | 0.01% |

### specific_conductance

| State | Count | Percentage |
|---|---:|---:|
| NORMAL | 5,705,308 | 75.28% |
| ELEVATED | 175,431 | 2.31% |
| EXTREME | 71,977 | 0.95% |
| MISSING | 1,047,641 | 13.82% |
| SENSOR_ARTIFACT | 578,651 | 7.63% |
| INSTRUMENT_LIMIT | 0 | 0.00% |

### fdom

| State | Count | Percentage |
|---|---:|---:|
| NORMAL | 3,232,634 | 42.65% |
| ELEVATED | 141,367 | 1.87% |
| EXTREME | 74,114 | 0.98% |
| MISSING | 3,950,248 | 52.12% |
| SENSOR_ARTIFACT | 180,126 | 2.38% |
| INSTRUMENT_LIMIT | 519 | 0.01% |

### chlorophyll

| State | Count | Percentage |
|---|---:|---:|
| NORMAL | 177,533 | 2.34% |
| ELEVATED | 1,937 | 0.03% |
| EXTREME | 31 | 0.00% |
| MISSING | 7,399,504 | 97.63% |
| SENSOR_ARTIFACT | 0 | 0.00% |
| INSTRUMENT_LIMIT | 3 | 0.00% |

## 7. Legacy Artifact Integrity

> [!NOTE]
> All legacy files verified unchanged. Pre- and post-generation SHA-256 checksums match.

| File | Status |
|---|---|
| `results/final_water_quality_prediction.csv` | ✅ Unchanged |
| `results/neon_anomaly_results.csv` | ✅ Unchanged |
| `models/saved_models/risk_model.pkl` | ✅ Unchanged |
| `models/saved_models/anomaly_model.pkl` | ✅ Unchanged |
| `models/saved_models/anomaly_scaler.pkl` | ✅ Unchanged |
| `models/saved_models/status_encoder.pkl` | ✅ Unchanged |
| `models/saved_models/model_metadata.pkl` | ✅ Unchanged |
| `models/saved_models/anomaly_features.pkl` | ✅ Unchanged |

## 8. Anomaly Independence Verification

The label generation pipeline does **not** read, reference, or depend on:
- `anomaly_status` (legacy Model 1 output)
- `water_risk_score` (legacy heuristic score)
- `final_status` (legacy pseudo-label)
- `final_risk_score` (legacy coupled score)

Labels are derived exclusively from sensor observations and site-specific ecological thresholds.
