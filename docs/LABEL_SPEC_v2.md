# Label Specification: `operational_risk_labels_v2.0`

**Document**: `docs/LABEL_SPEC_v2.md`  
**Version**: 2.0  
**Status**: Draft — Awaiting Approval  
**Strategy**: C (Hybrid — Literature Anchors + Percentile Refinement)  
**Governing Documents**: `PRD.md`, `Architecture.md`, `Rules.md`, `Phases.md`, `Phase2_Label_Strategy.md`

---

## 1. Purpose

This document defines the complete specification for generating **operational risk labels v2.0** — a scientifically defensible, site-adapted, anomaly-decoupled labeling methodology for the SIH Water Intelligence Platform.

These labels replace the legacy `final_status` pseudo-labels (v1.0) and serve as training targets for Model 2 (Risk Classification).

> [!CAUTION]
> **These labels are explicitly classified as derived operational risk labels (Rule 4.1).** They are NOT laboratory-confirmed ground truth, and must never be presented as confirmed contamination evidence. Every downstream consumer of these labels must acknowledge this limitation.

---

## 2. Design Principles

| Principle | Implementation |
|---|---|
| **Anomaly decoupling** | Zero dependence on Model 1 output. Risk labels are derived solely from sensor observations and ecological thresholds. |
| **Ecological validity** | Thresholds are adapted per site ecosystem type, using literature references where available and site-specific percentiles where not. |
| **Temporal integrity** | All statistical baselines computed exclusively from the 2024 training partition (`temporal_2024.parquet`). |
| **Data completeness awareness** | Labels include a confidence indicator that degrades when input data is incomplete or quality-flagged. |
| **Missing ≠ Safe** | Structurally or incidentally missing parameters do not automatically contribute "normal" status. |
| **Reproducibility** | Labels are deterministically reproducible from the canonical dataset + this specification. |
| **Versioning** | Label version is embedded in all training metadata, model artifacts, and result contracts. |

---

## 3. Scope of This Specification

### 3.1 What This Specification Defines

- Per-parameter, per-site threshold definitions for NORMAL / ELEVATED / EXTREME states.
- Multi-parameter aggregation rule for overall SAFE / WARNING / CRITICAL labels.
- Data completeness scoring methodology.
- Label confidence classification.
- Handling of structurally missing parameters.
- Handling of quality-flagged observations.

### 3.2 What This Specification Does NOT Define

- Model 2 architecture, hyperparameters, or training procedure.
- Model 1 anomaly detection methodology.
- Feature engineering for Model 2 (separate from label generation).
- How models should consume quality-flagged data at inference time.

---

## 4. Threshold Source Classification

Every threshold in this specification falls into one of two categories:

| Source Type | Code | Definition |
|---|---|---|
| **Literature-referenced** | `LIT` | Derived from published ecological criteria, EPA guidelines, state standards, or peer-reviewed research. Cited with specific document reference. |
| **Percentile-derived** | `PCT` | Computed from site-specific statistical distributions of the 2024 training partition. Used where no applicable literature threshold exists. |

---

## 5. Per-Parameter Threshold Definitions

### 5.1 pH

**Source**: `LIT` — EPA Freshwater Aquatic Life Criteria (40 CFR 131.11; EPA 440/5-88-001) specifies pH 6.5–9.0 for freshwater aquatic life protection. Extended tolerance based on state-level criteria for naturally acidic/alkaline waterbodies.

**Site-Type Adaptation**:

| Site | Ecosystem | NORMAL Range | ELEVATED Range | EXTREME Range | Rationale |
|---|---|---|---|---|---|
| **ARIK** | Semi-arid prairie stream | 7.0 – 8.5 | 6.5–7.0 or 8.5–9.0 | <6.5 or >9.0 | Standard EPA freshwater; baseline pH ~8.0 |
| **BARC** | Subtropical blackwater lake | 4.5 – 6.5 | 4.0–4.5 or 6.5–7.0 | <4.0 or >7.0 | Naturally acidic (pH 5.0–6.0); EPA criteria acknowledge acidic blackwater lakes |
| **BIGC** | Mountain forest stream | 6.5 – 8.0 | 6.0–6.5 or 8.0–8.5 | <6.0 or >8.5 | Well-buffered mountain stream; baseline pH ~7.2 |
| **BLDE** | Alpine snowmelt stream | 7.0 – 8.5 | 6.5–7.0 or 8.5–9.0 | <6.5 or >9.0 | Carbonate geology; baseline pH ~7.8 |
| **BLUE** | Great Plains stream | 7.5 – 9.0 | 7.0–7.5 or 9.0–9.5 | <7.0 or >9.5 | Alkaline prairie geology; baseline pH ~8.0 |

---

### 5.2 Dissolved Oxygen (mg/L)

**Source**: `LIT` — EPA freshwater DO criteria (EPA 440/5-86-003). Cold-water aquatic life: >6.5 mg/L (growth), >5.0 mg/L (survival). Warm-water aquatic life: >5.5 mg/L (growth), >3.0 mg/L (survival). Supersaturation (>120% saturation or >15 mg/L at sea level) also indicates potential concern (algal blooms, sensor issues).

**Site-Type Adaptation**:

| Site | Water Type | NORMAL Range | ELEVATED (Low) | ELEVATED (High) | EXTREME (Low) | EXTREME (High) |
|---|---|---|---|---|---|---|
| **ARIK** | Warm-water intermittent | 5.0 – 14.0 | 3.0–5.0 | 14.0–18.0 | <3.0 | >18.0 |
| **BARC** | Warm subtropical lake | 4.0 – 12.0 | 2.0–4.0 | 12.0–16.0 | <2.0 | >16.0 |
| **BIGC** | Cold mountain stream | 6.5 – 13.0 | 5.0–6.5 | 13.0–16.0 | <5.0 | >16.0 |
| **BLDE** | Cold alpine stream | 7.0 – 13.0 | 5.0–7.0 | 13.0–16.0 | <5.0 | >16.0 |
| **BLUE** | Warm-water stream | 5.0 – 14.0 | 3.0–5.0 | 14.0–18.0 | <3.0 | >18.0 |

**Note on ARIK**: This site has naturally low DO during dry-season low-flow periods (2024 training median: 8.13 mg/L; p1: 0.09 mg/L). DO values near 0 during summer are expected for this intermittent semi-arid stream, but remain ecologically concerning.

---

### 5.3 Turbidity (FNU)

**Source**: `LIT` + `PCT` — EPA recommends turbidity not exceed 25% above ambient conditions (EPA 440/5-86-001). Since absolute thresholds depend heavily on site baseline, we use literature guidance for general ranges supplemented by site-specific 90th/99th percentiles to define "elevated" relative to each site's natural turbidity regime.

| Site | Baseline Turbidity (p50) | NORMAL | ELEVATED | EXTREME | Source |
|---|---|---|---|---|---|
| **ARIK** | 1.61 FNU | 0 – 15 | 15 – 225 | >225 | `PCT`: p90=14.22, p99=225.02 |
| **BARC** | 0.94 FNU | 0 – 2 | 2 – 10 | >10 | `PCT`+`LIT`: p95=1.62; low-turbidity lake |
| **BIGC** | 1.99 FNU | 0 – 5 | 5 – 50 | >50 | `PCT`: p95=4.92; rare outliers |
| **BLDE** | 2.33 FNU | 0 – 6 | 6 – 50 | >50 | `PCT`: p95=5.84 |
| **BLUE** | 3.43 FNU | 0 – 18 | 18 – 100 | >100 | `PCT`: p95=17.61; naturally more turbid |

**Note**: Negative turbidity values indicate sensor malfunction (optical interference) and should be classified as sensor artifacts, not water-quality events. Observations with negative turbidity receive a `SENSOR_ARTIFACT` quality notation rather than being assessed for risk.

---

### 5.4 Specific Conductance (µS/cm)

**Source**: `PCT` — No universal freshwater conductance threshold exists in EPA criteria. Ecoregional conductance benchmarks vary from <50 µS/cm (dilute systems) to >1000 µS/cm (naturally mineralized streams). Site-specific percentiles from 2024 training data are used.

| Site | Baseline SpCond (p50) | NORMAL | ELEVATED | EXTREME | Source |
|---|---|---|---|---|---|
| **ARIK** | 519.04 µS/cm | 0 – 750 | 750 – 1000 | >1000 | `PCT`: p99=737.06; semi-arid mineralized stream |
| **BARC** | 26.91 µS/cm | 20 – 30 | 15–20 or 30–40 | <15 or >40 | `PCT`: p1=25.86, p99=28.84; extremely stable |
| **BIGC** | 139.38 µS/cm | 50 – 220 | 30–50 or 220–280 | <30 or >280 | `PCT`: p1=67.63, p99=217.56 |
| **BLDE** | 111.64 µS/cm | 50 – 140 | 30–50 or 140–180 | <30 or >180 | `PCT`: p1=56.14, p99=133.95 |
| **BLUE** | 575.05 µS/cm | 450 – 670 | 350–450 or 670–800 | <350 or >800 | `PCT`: p1=488.25, p99=664.49 |

**Note on ARIK SpCond**: The bimodal distribution (many values near 0 µS/cm from sensor failures, and valid values >400 µS/cm) means the p1-p25 percentiles are unreliable. Values near 0 µS/cm at ARIK almost certainly represent sensor exposure during dry periods rather than actual dilute water. These should be treated as sensor artifacts.

---

### 5.5 Fluorescent Dissolved Organic Matter — fDOM (QSU)

**Source**: `PCT` — No universal regulatory or ecological standard exists for fDOM. Thresholds are derived entirely from site-specific 2024 training percentiles.

| Site | Baseline fDOM (p50) | NORMAL | ELEVATED | EXTREME | Note |
|---|---|---|---|---|---|
| **ARIK** | 55.16 QSU | 0 – 105 | 105 – 130 | >130 | `PCT`: p95=103.09, p99=121.58 |
| **BARC** | 14.38 QSU | 8 – 20 | 5–8 or 20–30 | <5 or >30 | Valid readings only; 25% negatives = sensor failure |
| **BIGC** | 22.32 QSU | 10 – 56 | 56 – 80 | >80 | `PCT`: p97.5=55.84, p99=71.03 |
| **BLDE** | 43.78 QSU | 25 – 85 | 85 – 100 | >100 | `PCT`: p97.5=83.22, p99=90.17 |
| **BLUE** | 4.42 QSU | 0 – 17 | 17 – 40 | >40 | `PCT`: p97.5=17.09, p99=32.05 |

**Critical note**: fDOM is only available at downstream stations and lake buoy. It is structurally absent at upstream stations (101, 111). Negative fDOM values indicate sensor electronic artifacts and must be classified as `SENSOR_ARTIFACT`.

---

### 5.6 Chlorophyll a (µg/L) — BARC Only

**Source**: `LIT` + `PCT` — WHO/EPA trophic state classification: oligotrophic (<2 µg/L), mesotrophic (2–8 µg/L), eutrophic (8–25 µg/L), hypereutrophic (>25 µg/L). Applied only to BARC (the only site with chlorophyll sensors).

| Site | Baseline Chl (p50) | NORMAL | ELEVATED | EXTREME | Source |
|---|---|---|---|---|---|
| **BARC** | 2.56 µg/L | 0 – 8 | 8 – 25 | >25 | `LIT`: WHO/EPA trophic state |
| Other sites | N/A | — | — | — | NOT INSTALLED |

---

## 6. Per-Parameter State Classification Logic

For each observation, each available parameter is independently classified into one of three states:

```
NORMAL   = Value falls within the site-specific NORMAL range
ELEVATED = Value falls outside NORMAL but within the ELEVATED range
EXTREME  = Value falls outside the ELEVATED range into the EXTREME range
```

**Special cases**:
- **Missing value (NaN)**: Parameter state = `MISSING`. Does NOT contribute to risk count but degrades data completeness score.
- **Sensor artifact** (negative turbidity, negative fDOM, SpCond ≈ 0 at ARIK when expected >400): Parameter state = `SENSOR_ARTIFACT`. Treated as data quality issue, not risk signal. Does NOT count as NORMAL, but does NOT count as elevated risk either. Degrades data completeness.
- **Out-of-instrument-range flagged**: Parameter state = `INSTRUMENT_LIMIT`. Treated as potential sensor failure. Degrades data completeness.

---

## 7. Multi-Parameter Aggregation Rule

### 7.1 Assessable Parameter Count

For each observation, count the number of **assessable parameters** — parameters that are:
1. Installed at this site/position (not structurally absent).
2. Not missing (has a numerical value).
3. Not classified as `SENSOR_ARTIFACT` or `INSTRUMENT_LIMIT`.

```
assessable_count = count of parameters with state ∈ {NORMAL, ELEVATED, EXTREME}
```

### 7.2 Exceedance Counts

```
elevated_count = count of parameters with state = ELEVATED
extreme_count  = count of parameters with state = EXTREME
```

### 7.3 Overall Label Assignment

```
if assessable_count < 2:
    label = INSUFFICIENT_DATA
    
elif extreme_count >= 2:
    label = CRITICAL
    
elif extreme_count == 1 and elevated_count >= 1:
    label = CRITICAL
    
elif extreme_count == 1 and elevated_count == 0:
    label = WARNING
    
elif elevated_count >= 3:
    label = CRITICAL
    
elif elevated_count >= 1:
    label = WARNING
    
else:
    label = SAFE
```

### 7.4 Rationale

- **CRITICAL** requires either multiple extreme exceedances OR a combination of extreme + elevated conditions. This prevents single-parameter sensor glitches from triggering critical alerts.
- **WARNING** requires at least one parameter outside its normal range.
- **SAFE** requires all assessable parameters to be within normal range.
- **INSUFFICIENT_DATA** is assigned when fewer than 2 parameters are assessable, making a risk determination unreliable.

---

## 8. Data Completeness Score

Each observation receives a **data completeness score** reflecting how much information is available for the risk assessment:

### 8.1 Computation

```
installed_count    = number of parameters installed at this site/position
available_count    = number of parameters with non-null, non-artifact values
qf_clean_count     = number of available parameters that also have NEON QF = PASS (0)

completeness_ratio = available_count / installed_count
quality_ratio      = qf_clean_count / installed_count
```

### 8.2 Data Completeness Classification

| Classification | Condition |
|---|---|
| **FULL** | `completeness_ratio ≥ 0.80` AND `quality_ratio ≥ 0.60` |
| **PARTIAL** | `completeness_ratio ≥ 0.50` AND `quality_ratio ≥ 0.30` |
| **DEGRADED** | `completeness_ratio ≥ 0.25` OR at least 2 parameters assessable |
| **INSUFFICIENT** | `completeness_ratio < 0.25` AND fewer than 2 assessable parameters |

### 8.3 Installed Parameter Count by Site/Position

| Site | Position | Installed Parameters | Count |
|---|---|---|---|
| **ARIK** | 101 (upstream) | pH, DO, Turbidity, SpCond | 4 |
| **ARIK** | 102 (downstream) | pH, DO, Turbidity, SpCond, fDOM | 5 |
| **BARC** | 103 (lake buoy) | pH, DO, Turbidity, SpCond, fDOM, Chlorophyll | 6 |
| **BIGC** | 111 (upstream) | pH, DO, Turbidity, SpCond | 4 |
| **BIGC** | 112 (downstream) | pH, DO, Turbidity, SpCond, fDOM | 5 |
| **BLDE** | 101 (upstream) | pH, DO, Turbidity, SpCond | 4 |
| **BLDE** | 102 (downstream) | pH, DO, Turbidity, SpCond, fDOM | 5 |
| **BLUE** | 112 (downstream) | pH, DO, Turbidity, SpCond, fDOM | 5 |

---

## 9. Label Confidence

Each label receives a confidence classification combining the risk label certainty with data completeness:

| Confidence Level | Condition |
|---|---|
| **HIGH** | Data completeness = FULL, and the label is SAFE or the exceedance count is unambiguous |
| **MODERATE** | Data completeness = PARTIAL, or the observation is borderline between categories |
| **LOW** | Data completeness = DEGRADED, or multiple parameters are at boundary thresholds |
| **UNRELIABLE** | Data completeness = INSUFFICIENT, or label = INSUFFICIENT_DATA |

---

## 10. Handling Quality-Flagged Observations

### 10.1 NEON QF Failures

Observations where a parameter has `FinalQF == 1` (NEON quality flag failure):
- The measurement is **preserved** and **assessed** for risk classification.
- The NEON QF failure is recorded in the data completeness scoring (degrades `quality_ratio`).
- The label confidence may be reduced from HIGH to MODERATE.
- The QF failure does NOT prevent the measurement from contributing to the risk label.

**Rationale**: Per Phase 1 policy, QF failures indicate possible calibration drift or sensor issues but do not prove the measurement is invalid. Excluding them would reintroduce the ARIK exclusion bias.

### 10.2 Out-of-Instrument-Range Values

Measurements outside manufacturer hardware operating bounds:
- Classified as `INSTRUMENT_LIMIT` and excluded from risk assessment.
- Treated as data completeness degradation.
- Not counted as either normal or elevated.

---

## 11. Relationship to Legacy Labels

| Attribute | Legacy v1.0 | This Specification v2.0 |
|---|---|---|
| **Column name** | `final_status` | `risk_label_v2` |
| **Score column** | `final_risk_score` | Not applicable (rule-based, not score-based) |
| **Anomaly coupling** | Yes (`+40 × anomaly`) | None |
| **Normalization** | Global `max()` across all sites | Site-specific thresholds |
| **pH reference** | Universal pH=7 | Site-specific ecological baseline |
| **Parameters used** | 4 (pH, turbidity, DO, fDOM) | All installed parameters per site |
| **Threshold source** | Ad-hoc constants | Literature + site-specific percentiles |
| **Completeness tracking** | None | Full data completeness score |
| **Confidence** | None | HIGH / MODERATE / LOW / UNRELIABLE |
| **Additional class** | None | `INSUFFICIENT_DATA` |

> [!IMPORTANT]
> Legacy `final_status`, `water_risk_score`, and `anomaly_status` columns are **not modified or deleted**. They remain in the legacy dataset (`results/final_water_quality_prediction.csv`) as historical baseline. New labels are generated as **additional columns** in a new labeled dataset.

---

## 12. Output Schema

Each labeled observation will include the following new columns:

| Column | Type | Description |
|---|---|---|
| `risk_label_v2` | string | `SAFE`, `WARNING`, `CRITICAL`, or `INSUFFICIENT_DATA` |
| `label_version` | string | `operational_risk_labels_v2.0` |
| `elevated_count` | int | Number of parameters in ELEVATED state |
| `extreme_count` | int | Number of parameters in EXTREME state |
| `assessable_count` | int | Number of parameters with assessable readings |
| `data_completeness` | string | `FULL`, `PARTIAL`, `DEGRADED`, or `INSUFFICIENT` |
| `label_confidence` | string | `HIGH`, `MODERATE`, `LOW`, or `UNRELIABLE` |
| `per_param_state` | JSON string | Per-parameter state dictionary, e.g. `{"ph": "NORMAL", "dissolved_oxygen": "ELEVATED", ...}` |

---

## 13. Versioning and Provenance

### 13.1 Label Version Identifier

```
operational_risk_labels_v2.0
```

### 13.2 Required Metadata for Any Model Trained on These Labels

```yaml
label_version: "operational_risk_labels_v2.0"
label_specification: "docs/LABEL_SPEC_v2.md"
label_type: "derived_operational_risk_label"
label_is_ground_truth: false
threshold_sources:
  pH: "LIT - EPA 440/5-88-001 + site adaptation"
  dissolved_oxygen: "LIT - EPA 440/5-86-003 + site adaptation"
  turbidity: "LIT+PCT - EPA 440/5-86-001 + site-specific p90/p99"
  specific_conductance: "PCT - site-specific percentiles"
  fdom: "PCT - site-specific percentiles"
  chlorophyll: "LIT - WHO/EPA trophic state (BARC only)"
baseline_data_source: "data/canonical/temporal_2024.parquet"
baseline_data_version: "Phase 1 canonical dataset"
```

### 13.3 Version Change Policy

Any modification to:
- Threshold values
- Aggregation rules
- Parameter inclusion/exclusion
- Confidence classification logic

requires:
1. A new version number (e.g., `v2.1`).
2. Updated `LABEL_SPEC_v2.md` document.
3. Re-generation of all affected labels.
4. Re-training of all models using these labels.
5. Re-evaluation on held-out test data.

---

## 14. Known Limitations

1. **No laboratory ground truth**: All labels remain derived/rule-based. Minority class (WARNING, CRITICAL) labels have not been validated against independent environmental assessments.

2. **Literature threshold applicability**: EPA criteria are designed for regulatory compliance assessment, not real-time operational early warning. The thresholds may be more conservative or more permissive than optimal for operational use.

3. **Seasonal variation**: Current thresholds do not explicitly account for seasonal expected ranges. A winter pH value at ARIK may differ from a summer value, and both may be "normal" for their season. Future label versions should consider seasonal baseline adaptation.

4. **fDOM sensor reliability**: ARIK fDOM has 50% QF failure rate, and BARC fDOM has 25% negative-artifact contamination. fDOM-based risk classification at these sites carries inherently lower reliability.

5. **BLUE data availability**: 59% of BLUE observations are missing across all parameters. Labels for BLUE will have systematically lower data completeness and confidence.

6. **Cross-site transferability**: These labels are calibrated for the 5 NEON sites in this dataset. They should NOT be applied to Mahanadi or other waterbodies without recalibration.

---

> **This specification is a draft pending user approval. No labels should be generated until this document is reviewed and accepted.**
