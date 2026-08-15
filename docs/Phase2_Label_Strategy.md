# Phase 2 — Label Validation: Scientific Audit & Strategy

**Document**: `docs/Phase2_Label_Strategy.md`  
**Version**: 1.0  
**Status**: Design Document — Awaiting Approval  
**Phase**: Phase 2 — Scientific & Label Validation  
**Governing Documents**: `PRD.md`, `Architecture.md`, `Rules.md`, `Phases.md`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Audit of Current Labeling Pipeline](#2-audit-of-current-labeling-pipeline)
3. [Why the Previous `final_status` Labels Are Unreliable](#3-why-the-previous-final_status-labels-are-unreliable)
4. [Separating Anomaly, Risk, Event, and Contamination](#4-separating-anomaly-risk-event-and-contamination)
5. [Possible Label Strategies to Replace Current Pseudo-Labels](#5-possible-label-strategies-to-replace-current-pseudo-labels)
6. [Evaluation Metrics for Model 2](#6-evaluation-metrics-for-model-2)
7. [How to Design Model 2 Scientifically](#7-how-to-design-model-2-scientifically)
8. [Recommendations and Open Questions](#8-recommendations-and-open-questions)

---

## 1. Executive Summary

The current `final_status` labels (`SAFE`, `WARNING`, `CRITICAL`) used to train Model 2 are **scientifically indefensible pseudo-labels** that suffer from at least seven independent structural defects. They cannot be treated as ground truth.

This document provides:
- A complete forensic reconstruction of the existing labeling pipeline.
- An identification and classification of every defect.
- A separation of the concepts of anomaly, risk, event, and contamination.
- Three candidate label strategies ranked by scientific defensibility.
- A complete evaluation framework for Model 2.
- A scientifically grounded design specification for Model 2 retraining.

> [!CAUTION]
> **No model trained on the current `final_status` labels should be treated as production-ready.** The existing Model 2 (97.41% accuracy) masks catastrophic minority-class failure: WARNING recall of 5.51%, with 94.5% of WARNING and 46.2% of CRITICAL observations misclassified as SAFE.

---

## 2. Audit of Current Labeling Pipeline

### 2.1 End-to-End Reconstruction

The complete label-generation chain, reconstructed from [`01_EDA.ipynb`](file:///Users/raj/neon_water_project/01_EDA.ipynb) (cells 28–32), is:

```
Step 1: Legacy Preprocessing (scripts/process_neon.py)
    ↓  Drops all rows where ANY FinalQF == 1
    ↓  Drops all rows with ANY missing core feature
    ↓  → Silently eliminates 100% of ARIK (fDOMFinalQF=1 for all ARIK fDOM)
    ↓  → Reduces 7.58M raw records to 2.13M
    
Step 2: Global Scaling (01_EDA.ipynb, cell 9)
    ↓  StandardScaler.fit_transform() on ALL data (2024 + 2025)
    ↓  → Temporal leakage: test period statistics influence training scaling
    
Step 3: Isolation Forest Anomaly Detection (01_EDA.ipynb, cell 10)
    ↓  IsolationForest(contamination=0.01) fitted on ALL scaled data
    ↓  → anomaly_status ∈ {-1, +1}
    ↓  → No temporal split: anomaly model sees 2025 test data during training
    
Step 4: Heuristic Risk Score (01_EDA.ipynb, cell 28)
    ↓  ph_risk     = |pH - 7| / 3
    ↓  turb_risk   = turbidity / turbidity.max()        ← global max
    ↓  do_risk     = 1 - (DO / DO.max())                ← global max
    ↓  fdom_risk   = fDOM / fDOM.max()                  ← global max
    ↓
    ↓  water_risk_score = ph_risk×25 + turb_risk×30 + do_risk×20 + fdom_risk×25
    ↓  clipped to [0, 100]
    
Step 5: Anomaly Coupling (01_EDA.ipynb, cell 31)
    ↓  final_risk_score = water_risk_score + (anomaly_status == -1) × 40
    ↓  clipped to [0, 100]
    
Step 6: Threshold Application (01_EDA.ipynb, cell 31)
    ↓  final_status = SAFE     if final_risk_score < 30
    ↓                 WARNING  if 30 ≤ final_risk_score < 60
    ↓                 CRITICAL if final_risk_score ≥ 60
```

### 2.2 Formula Summary

The label that Model 2 is trained to predict is computed as:

$$\text{final\_risk\_score} = \text{clip}\Bigl(\underbrace{\frac{|pH - 7|}{3} \times 25 + \frac{\text{turb}}{\max(\text{turb})} \times 30 + \Bigl(1 - \frac{DO}{\max(DO)}\Bigr) \times 20 + \frac{fDOM}{\max(fDOM)} \times 25}_{\text{water\_risk\_score}} + \underbrace{(\text{anomaly} = -1) \times 40}_{\text{circular coupling}},\; 0,\; 100\Bigr)$$

This means that **any observation flagged as anomalous by the Isolation Forest automatically receives a +40 point boost**, pushing nearly all anomalies into the `CRITICAL` category (≥60), regardless of the actual sensor values.

---

## 3. Why the Previous `final_status` Labels Are Unreliable

Seven independent structural defects render these labels scientifically indefensible:

### Defect 1: Circular Anomaly–Label Coupling

**Severity: CRITICAL**

The `anomaly_status` from Model 1 (Isolation Forest) is injected directly into the label formula via the `+40` term. This creates a closed logical loop:

```
Model 1 predicts anomaly
    → anomaly adds +40 to risk score
    → risk score generates final_status label
    → Model 2 is trained on final_status
    → Model 2 learns to predict anomaly outputs, not risk
```

**Consequence**: Model 2 does not independently learn water-quality risk. It learns to replicate Model 1's anomaly decisions with a deterministic offset. The two models are not independent intelligence layers — they are circularly coupled.

> [!IMPORTANT]
> **`Rules.md` Rule 2.3** explicitly requires that anomaly and risk remain separate states. The current pipeline violates this requirement by design.

---

### Defect 2: Global Min/Max Scaling Across Heterogeneous Sites

**Severity: HIGH**

The risk formula uses `parameter.max()` as the denominator for turbidity, dissolved oxygen, and fDOM normalization. This maximum is computed **globally** across all sites, all seasons, and all sensor positions.

The five NEON sites span radically different ecosystems:

| Site | Ecosystem | Typical SpCond (µS/cm) | Typical DO (mg/L) | Typical pH |
|---|---|---|---|---|
| **ARIK** | Prairie semi-arid stream (CO) | 500–2,000+ | 6–12 | 7.5–8.5 |
| **BARC** | Subtropical blackwater lake (FL) | 20–30 | 8–10 | 5.0–6.0 |
| **BIGC** | Mountain forest stream (CA) | 40–80 | 8–12 | 7.0–8.0 |
| **BLDE** | Alpine snowmelt stream (WY) | 100–300 | 7–13 | 7.5–8.5 |
| **BLUE** | Great Plains stream (OK) | 200–600 | 5–12 | 7.0–8.5 |

**Consequence**: A dissolved oxygen reading of 8.0 mg/L is perfectly normal for BARC's warm subtropical water but could represent seasonal stress at BLDE's cold alpine stream. Using the global maximum to normalize treats every site as if it had the same ecological baseline. The resulting risk score is ecologically meaningless.

---

### Defect 3: Arbitrary pH Reference Point

**Severity: MODERATE**

The formula computes pH risk as `|pH - 7| / 3`, assuming pH 7.0 is the universal "safe" neutral point.

**Problem**: Lake Barco (BARC) has a naturally acidic pH baseline of 5.0–6.0 due to tannin-rich blackwater chemistry. Under the current formula, **every BARC observation is penalized for being naturally acidic**, receiving a chronic pH risk contribution of ~8–17 points (out of 25).

This is not a water-quality defect — it is the ecological baseline of a healthy blackwater lake.

---

### Defect 4: Incomplete Parameter Coverage

**Severity: MODERATE**

The risk formula uses only 4 of 6 available parameters:
- ✅ pH (weight 25)
- ✅ Turbidity (weight 30)
- ✅ Dissolved Oxygen (weight 20)
- ✅ fDOM (weight 25)
- ❌ **Specific Conductance** (ignored)
- ❌ **Chlorophyll** (ignored)

Yet Model 2 uses all 6 parameters as input features. This means the model's feature space includes parameters that have **zero influence on the labels it is trained to predict**. Model 2 can never learn meaningful relationships between specific conductance/chlorophyll and risk because those relationships don't exist in the label definition.

---

### Defect 5: No Temporal Split in Model 1

**Severity: HIGH**

The Isolation Forest was fitted on **all data** (2024 + 2025) simultaneously. The `StandardScaler` was also fitted on all data. Since Model 1's anomaly predictions are baked into the labels, this means:

1. The scaler learned statistics from the 2025 test period → **preprocessing leakage**.
2. The anomaly model saw 2025 observations during fitting → **temporal leakage**.
3. Labels derived from these anomalies are contaminated for both the 2024 training partition and the 2025 test partition.

No evaluation performed on 2025 data is a valid out-of-sample test.

---

### Defect 6: Unjustified Threshold Values

**Severity: MODERATE**

The thresholds 30 (SAFE/WARNING boundary) and 60 (WARNING/CRITICAL boundary) appear to have no documented scientific, regulatory, or operational justification. There is no reference to:

- EPA water quality criteria
- WHO drinking water guidelines
- NEON ecological thresholds
- State or domain-specific regulations
- Peer-reviewed ecological literature

The weights (25, 30, 20, 25) and the +40 anomaly bonus are similarly unjustified. These are ad-hoc constants that produce an arbitrary class distribution.

---

### Defect 7: ARIK Exclusion Bias

**Severity: HIGH**

The legacy preprocessing pipeline ([`scripts/process_neon.py`](file:///Users/raj/neon_water_project/scripts/process_neon.py)) applied a strict boolean filter: `df = df[(df[col] == 0) | (df[col].isna())]` for each quality flag column. Because ARIK's fDOM sensor had `fDOMFinalQF == 1` for 100% of downstream measurements, **every ARIK observation was silently dropped**.

This means:
- 2,105,280 records (27.8% of the total dataset) were lost.
- An entire NEON domain (D10, Colorado semi-arid prairie) was excluded from model training.
- Model 2 never learned prairie stream behavior.
- The labels were generated from a biased, incomplete view of the data.

---

### 3.1 Summary of Defects

| # | Defect | Severity | Root Cause | Consequence |
|---|---|---|---|---|
| 1 | Circular anomaly coupling | CRITICAL | `+40 × anomaly` in label formula | Model 2 learns Model 1 outputs, not independent risk |
| 2 | Global min/max scaling | HIGH | Cross-site `max()` normalization | Ecologically meaningless risk scores |
| 3 | Arbitrary pH reference | MODERATE | `\|pH - 7\|` assumption | Healthy blackwater lakes penalized |
| 4 | Incomplete parameter coverage | MODERATE | Only 4 of 6 parameters in formula | Features-to-label disconnect |
| 5 | No temporal split in Model 1 | HIGH | All-data scaler and anomaly fitting | Temporal leakage in labels |
| 6 | Unjustified thresholds | MODERATE | Ad-hoc constants (30, 60, +40) | Arbitrary class boundaries |
| 7 | ARIK exclusion bias | HIGH | Strict QF boolean filter | 27.8% data loss, domain bias |

---

## 4. Separating Anomaly, Risk, Event, and Contamination

Per `Rules.md` Rule 2.3, `Architecture.md` Section 2, and `Phases.md` Phase 2, the system must maintain a strict separation between:

```
OBSERVATION          → "What was measured?"
    ↓
DATA QUALITY         → "Can the measurement be trusted?"
    ↓
ANOMALY              → "Is this measurement unusual?" (Model 1)
    ↓
WATER-QUALITY RISK   → "How concerning is the condition?" (Model 2)
    ↓
EVENT HYPOTHESIS     → "What might explain this?" (Model 3)
    ↓
FORECAST             → "What happens next?" (Model 4)
    ↓
RECOMMENDATION       → "What should the operator do?" (Model 5)
    ↓
CONFIRMATION         → "Has contamination actually been verified?"
```

### 4.1 What Each Layer Must NOT Do

| Layer | Must NOT |
|---|---|
| **Anomaly (Model 1)** | Claim contamination. Use risk labels as input. Assume anomaly = dangerous. |
| **Risk (Model 2)** | Use anomaly predictions as features. Conflate risk with contamination. Train on labels derived from Model 1. |
| **Event (Model 3)** | Claim specific pollutant. Treat hypotheses as confirmed. |
| **Confirmation** | Be generated by any ML model alone. |

### 4.2 How This Applies to Label Design

The label for Model 2 must answer **one question only**:

> "Based solely on the measured water-quality parameters, how concerning is the current condition relative to the ecological baseline of this site?"

The label must be derived **exclusively from sensor observations and scientifically established thresholds**. It must not incorporate:
- Model 1 anomaly output (that's a different question)
- Globally normalized scores (that's ecologically invalid)
- Arbitrary weights without documented justification

---

## 5. Possible Label Strategies to Replace Current Pseudo-Labels

Given that no laboratory-confirmed ground truth exists in the dataset, all labels will remain **derived/rule-based operational risk labels** (per `Rules.md` Rule 4.1). The key is to make the derivation scientifically defensible and decoupled.

### Strategy A: Site-Specific Percentile-Based Risk Labels

**Approach**: Define risk thresholds using the statistical distribution of each parameter **within each site**, reflecting the ecological baseline of that specific waterbody.

**Method**:
1. Compute per-site, per-parameter percentile distributions from the training partition (2024 only).
2. Define risk tiers using percentile thresholds (e.g., 90th and 99th percentiles for parameters where high values indicate concern; 10th and 1st percentiles for parameters where low values indicate concern).
3. Count the number of parameters in elevated/extreme states for each observation.
4. Assign labels based on the count and severity of parameter exceedances.

**Label Definition**:
```
SAFE     = 0 parameters in elevated/extreme state
WARNING  = 1-2 parameters in elevated state, OR 1 parameter in extreme state
CRITICAL = 3+ parameters in elevated state, OR 2+ in extreme state
```

**Strengths**:
- Each site has an ecologically meaningful baseline.
- No cross-site contamination of statistics.
- No dependency on Model 1.
- Uses only the training partition for threshold computation → no temporal leakage.
- Scientifically defensible: extremes are defined relative to observed ecological behavior.

**Weaknesses**:
- Still a derived label, not ground truth.
- Percentile thresholds are a statistical convention, not an ecological standard.
- An extremely stable site would generate very few WARNING/CRITICAL labels even if conditions are degraded compared to a different reference.

**Scientific Defensibility**: ★★★★☆

---

### Strategy B: Literature-Referenced Ecological Threshold Labels

**Approach**: Define risk thresholds based on published ecological and regulatory criteria, adapted per aquatic system type (wadeable stream vs. lake).

**Method**:
1. Identify parameter-specific ecological thresholds from published sources:
   - **pH**: EPA freshwater criteria (6.5–9.0 for most aquatic life); site-type adjustments for blackwater systems.
   - **Dissolved Oxygen**: State standards and EPA criteria (typically >5 mg/L for warm water, >6.5 mg/L for cold water).
   - **Turbidity**: EPA recommended benchmarks; NEON site-specific expected ranges.
   - **Specific Conductance**: Ecoregion-specific conductance benchmarks.
   - **fDOM**: Site-baseline relative thresholds (no universal standard exists).
   - **Chlorophyll**: Trophic state indicators where applicable.
2. Classify each parameter observation relative to appropriate thresholds.
3. Aggregate multi-parameter exceedances to assign overall risk.

**Label Definition**:
```
SAFE     = All parameters within expected ecological/regulatory range
WARNING  = 1+ parameters outside expected range but within extended tolerance
CRITICAL = 1+ parameters severely outside expected range
```

**Strengths**:
- Scientifically grounded in published ecological criteria.
- Thresholds are externally verifiable and citable.
- Differentiates between ecosystem types (lake vs. stream).

**Weaknesses**:
- Published thresholds may not exist for all parameter × site combinations (e.g., fDOM has no universal ecological standard).
- Thresholds designed for regulatory compliance may not align with operational early-warning needs.
- Some parameters require site-specific calibration that may not be available from literature alone.
- Requires careful research and documentation of each threshold source.

**Scientific Defensibility**: ★★★★★ (where literature exists)

---

### Strategy C: Hybrid — Literature Anchors + Percentile Refinement

**Approach**: Use published ecological criteria as primary anchors where available, and fill gaps with site-specific statistical thresholds. This combines the scientific grounding of Strategy B with the completeness of Strategy A.

**Method**:
1. For parameters with well-established ecological criteria (pH, DO, turbidity), use literature-based thresholds with site-type adaptation.
2. For parameters without universal criteria (fDOM, chlorophyll at stream sites), use per-site percentile thresholds from the training partition.
3. For specific conductance, use ecoregion-specific benchmarks where available, supplemented by per-site percentiles.
4. Document each threshold source explicitly (literature citation or statistical derivation).
5. Apply per-parameter risk classification, then aggregate using a multi-parameter exceedance rule.

**Label Definition**:
```
Per-parameter states:
  NORMAL  = Within expected range (literature or percentile-based)
  ELEVATED = Outside expected range, within extended tolerance
  EXTREME  = Severely outside expected range

Overall observation labels:
  SAFE     = All parameters NORMAL
  WARNING  = ≥1 parameter ELEVATED, or exactly 1 EXTREME
  CRITICAL = ≥2 parameters EXTREME, or ≥3 ELEVATED
```

**Strengths**:
- Maximum scientific defensibility: every threshold has a documented source.
- Complete parameter coverage (no gaps).
- Site-specific adaptation where ecological heterogeneity demands it.
- Fully decoupled from Model 1.
- Only uses training-partition statistics → no temporal leakage.
- Versioned and reproducible.

**Weaknesses**:
- More complex to implement and document.
- Still a derived label, not laboratory-confirmed ground truth.
- Hybrid thresholds require careful documentation to avoid mixing standards.

**Scientific Defensibility**: ★★★★★

---

### 5.1 Strategy Recommendation

> [!IMPORTANT]
> **Recommended: Strategy C (Hybrid)**, with the following implementation constraints:
> 1. Literature thresholds must be cited with specific document references.
> 2. Percentile thresholds must be computed only from the 2024 temporal partition.
> 3. Every threshold must be documented in a versioned **Label Specification** artifact.
> 4. The label version must be explicitly recorded in all training metadata.
> 5. The labels must be explicitly called **"operational risk labels v2.0"**, never "ground truth" or "confirmed contamination."

---

## 6. Evaluation Metrics for Model 2

Per `Rules.md` Rules 6.1–6.3, `Phases.md` Phase 4, and the project's core principle ("Accuracy ≠ Model Quality"), Model 2 must be evaluated using a comprehensive metric suite.

### 6.1 Primary Metrics

| Metric | Purpose | Priority |
|---|---|---|
| **Macro F1** | Balanced performance across all classes regardless of support | **PRIMARY** |
| **WARNING Recall** | Ability to detect the minority warning class | **PRIMARY** |
| **CRITICAL Recall** | Ability to detect the rare critical class | **PRIMARY** |
| **WARNING F1** | Precision-recall balance for warning class | **PRIMARY** |
| **CRITICAL F1** | Precision-recall balance for critical class | **PRIMARY** |

### 6.2 Secondary Metrics

| Metric | Purpose | Priority |
|---|---|---|
| **Weighted F1** | Performance weighted by class support | SECONDARY |
| **Per-class Precision** | False positive rate per class | SECONDARY |
| **Per-class Recall** | False negative rate per class | SECONDARY |
| **Confusion Matrix** | Full error distribution | SECONDARY |
| **ROC-AUC (OVR)** | Discriminative ability across thresholds | SECONDARY |
| **PR-AUC (per class)** | Particularly important for minority classes | SECONDARY |

### 6.3 Diagnostic Metrics

| Metric | Purpose | Priority |
|---|---|---|
| **Overall Accuracy** | Reported but NOT used as primary selection criterion | DIAGNOSTIC |
| **Class Support** | Reported for all partitions | DIAGNOSTIC |
| **Calibration Curve** | Are predicted probabilities trustworthy? | DIAGNOSTIC |
| **Feature Importance** | Which features drive predictions? | DIAGNOSTIC |

### 6.4 Minimum Acceptable Performance

Before Model 2 can be considered operational (not merely experimental):

| Criterion | Minimum Threshold | Rationale |
|---|---|---|
| **WARNING Recall** | ≥ 0.50 | Must detect at least half of warning conditions |
| **CRITICAL Recall** | ≥ 0.60 | Must detect most critical conditions (safety-critical) |
| **Macro F1** | ≥ 0.50 | Balanced performance, not accuracy-dominated |
| **SAFE Precision** | ≥ 0.90 | When the system says SAFE, it should be reliable |

> [!WARNING]
> If these thresholds cannot be met, **Model 2 must remain labelled as "experimental"** per `Phases.md` Phase 4 Exit Criteria: *"If not, Model 2 remains experimental."*

### 6.5 What Must Be Reported

Every Model 2 evaluation must include:

```
1. Label version used
2. Training data: partition, row count, class distribution
3. Validation data: partition, row count, class distribution
4. Test data: partition, row count, class distribution
5. Full confusion matrix
6. Per-class precision, recall, F1, support
7. Macro F1, weighted F1, accuracy
8. ROC-AUC (OVR)
9. Feature importance ranking
10. Known limitations
```

---

## 7. How to Design Model 2 Scientifically

### 7.1 Architecture Principles

1. **Independence**: Model 2 must not use Model 1 outputs as features or label components. Their intelligence layers must be independently evaluable.

2. **Ecological validity**: Risk thresholds must reflect the ecological characteristics of each site, not arbitrary global normalization.

3. **Temporal integrity**: All preprocessing parameters (scalers, imputers, encoders) must be fitted exclusively on the training partition. The test partition must remain untouched until final evaluation.

4. **Honest uncertainty**: When confidence is low, the model should communicate this through calibrated probabilities, not force a high-confidence label.

### 7.2 Label Generation (Pre-Training)

```
Input: Canonical observations from data/canonical/temporal_2024.parquet

Step 1: Compute per-site, per-parameter baseline statistics
        (only from 2024 training data)

Step 2: Apply literature-referenced ecological thresholds where available
        (pH, DO, turbidity — cite sources)

Step 3: Apply site-specific percentile thresholds where literature
        is unavailable or insufficient (fDOM, chlorophyll, SpCond)

Step 4: Classify each parameter-observation as NORMAL / ELEVATED / EXTREME

Step 5: Aggregate per-observation multi-parameter exceedance
        → SAFE / WARNING / CRITICAL

Step 6: Version the label specification as "operational_risk_labels_v2.0"
        Document every threshold with source
```

### 7.3 Feature Engineering

**Core Features** (6 water quality parameters):
- `ph`, `dissolved_oxygen`, `turbidity`, `specific_conductance`, `fdom`, `chlorophyll`

**Data Quality Features** (from Phase 1 canonical schema):
- Per-parameter NEON QF flags (`*_flag_qf`)
- Per-parameter instrument range flags (`*_flag_range`)
- `is_duplicate`

**Contextual Features** (derived from timestamps — no leakage risk):
- `hour_of_day` (cyclic encoded)
- `month` (cyclic encoded)
- `site_id` (categorical encoded)
- `sensor_position` (categorical or ordinal)

**Derived Statistical Features** (computed from training data only):
- Per-site z-scores for each parameter (deviation from site-specific mean)
- Rolling window features (if temporal windows are used)

> [!IMPORTANT]
> **Specific Conductance and Chlorophyll must NOT be excluded from risk assessment.** The legacy formula's omission of these parameters was a design error.

### 7.4 Preprocessing Pipeline

```
1. Missing value strategy:
   - Median imputation per site, fitted on training data only
   - Alternatively: indicator variables for missingness patterns

2. Scaling:
   - StandardScaler or RobustScaler, fitted on training data only
   - Consider per-site scaling to preserve ecological baselines

3. Encoding:
   - Site ID: One-hot or target encoding
   - Temporal: Cyclic sine/cosine encoding

4. Feature selection:
   - Use training data only for any feature selection
```

### 7.5 Model Selection Strategy

Per `Rules.md` Rules 7.1–7.3, multiple approaches must be compared:

| Approach | Description | Purpose |
|---|---|---|
| **Baseline** | Majority-class classifier | Minimum bar |
| **Class-weighted RF** | RandomForest with `class_weight='balanced'` | Standard balanced approach |
| **BalancedRandomForest** | Balanced bootstrap sampling | Current legacy approach |
| **XGBoost + scale_pos_weight** | Gradient boosted trees with class balancing | Potentially better minority detection |
| **LightGBM + is_unbalance** | Fast gradient boosting | Efficiency + performance |
| **Threshold tuning** | Optimize decision threshold on validation set | Improve minority recall |

**Rules for comparison:**
- All models use the same preprocessed training data.
- All models are evaluated on the same untouched test set.
- SMOTE is evaluated as one experiment, not the default (`Rules.md` 7.1).
- Synthetic samples from SMOTE must be validated for physical plausibility (`Rules.md` 7.3).
- Model selection uses macro F1 and minority recall as primary criteria, **not accuracy**.

### 7.6 Validation Strategy

```
Training:    temporal_2024.parquet (subset: months 1-9, ~75%)
Validation:  temporal_2024.parquet (subset: months 10-12, ~25%)
Final Test:  temporal_2025.parquet (100% — NEVER touched until final eval)
```

- Time-based split within 2024 for training/validation.
- No random shuffling of temporal data (`Rules.md` 5.2).
- Final test on 2025 data only after model selection is complete.
- Consider station-holdout evaluation as additional diagnostic (`Rules.md` 5.3).

### 7.7 Output Specification

Per `Architecture.md` Section 10 and `Rules.md` Section 11, Model 2 must output:

```json
{
  "result_id": "uuid",
  "station_id": "ARIK",
  "sensor_position": "101.100.100",
  "timestamp_utc": "2025-03-15T14:30:00Z",
  "model_name": "risk",
  "model_version": "2.0",
  "label_version": "operational_risk_labels_v2.0",
  "prediction": "WARNING",
  "probabilities": {
    "SAFE": 0.18,
    "WARNING": 0.72,
    "CRITICAL": 0.10
  },
  "confidence": 0.72,
  "input_data_quality": "GOOD",
  "feature_contributions": {
    "dissolved_oxygen": 0.31,
    "turbidity": 0.28,
    "ph": 0.15
  },
  "preprocessing_version": "2.0",
  "created_at": "2026-08-15T12:00:00Z"
}
```

---

## 8. Recommendations and Open Questions

### 8.1 Immediate Recommendations

1. **Do not retrain Model 2 until the label specification is approved.**
2. **Preserve existing model artifacts** (`models/saved_models/*`) as historical baseline.
3. **Create a versioned Label Specification document** (`docs/LABEL_SPEC_v2.md`) before generating any new labels.
4. **Conduct a literature review** of ecological thresholds for pH, DO, turbidity, and specific conductance by aquatic system type, to ground Strategy C.
5. **Compute site-specific parameter statistics** from `temporal_2024.parquet` only, and publish them as baseline profiles.

### 8.2 Open Questions for User Decision

> [!IMPORTANT]
> The following decisions require user input before implementation can proceed.

**Q1. Label Strategy Selection**
- **Strategy A**: Pure percentile-based (simpler, less scientifically anchored)
- **Strategy B**: Pure literature-based (strongest science, may have gaps)
- **Strategy C** (Recommended): Hybrid literature + percentile

**Q2. Percentile Thresholds**
- If Strategy A or C is selected, which percentiles should define the boundaries?
  - Proposed: 90th/10th for ELEVATED, 99th/1st for EXTREME
  - Alternative: 95th/5th for ELEVATED, 99.5th/0.5th for EXTREME

**Q3. Multi-Parameter Aggregation Rule**
- Should the aggregation count all parameters equally, or should some parameters (e.g., DO) carry higher weight due to direct ecological impact?
- Proposed: Equal weighting of exceedance counts initially; parameter-specific weights can be introduced in a future label version with documented justification.

**Q4. Handling Structurally Missing Parameters**
- Chlorophyll and sensor depth are available only at BARC. fDOM is absent at upstream stations.
- Should risk labels for upstream stations be computed from the 4 available parameters only?
- Should missing parameters count as "NORMAL" (no evidence of concern) or "UNKNOWN" (separate handling)?

**Q5. Class Distribution Target**
- The new labels will almost certainly produce a different class distribution than the legacy labels. Should we accept whatever distribution the scientifically defensible thresholds produce, even if WARNING/CRITICAL remain rare?
- **Recommended**: Accept the natural distribution. Address imbalance through algorithmic techniques (class weighting, balanced sampling), not threshold manipulation.

**Q6. Minimum Recall Thresholds**
- Are the proposed minimum recall thresholds (WARNING ≥ 0.50, CRITICAL ≥ 0.60) acceptable?
- These can be adjusted based on operational requirements.

---

> **This document is a design artifact. No code modifications, model retraining, or label generation should occur until this strategy is reviewed and approved.**
