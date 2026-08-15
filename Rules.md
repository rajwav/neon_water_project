Yes. The **Work rules are stronger technically**, while the **Chat rules are easier to follow**. The best version should combine them without becoming bloated.

I would make this the **canonical `Rules.md`** for the project:

# `Rules.md` — Canonical Engineering & AI Rules

```markdown
# SIH Water Intelligence Platform
## Engineering, AI, Scientific & Development Rules

Version: 2.0
Status: Canonical
Purpose: Source of truth for developers and AI coding agents

---

# 1. Core Principle

Build a scientifically defensible, reproducible, explainable, and
production-ready water-intelligence system.

Do NOT optimize the project merely for impressive accuracy numbers.

A model with 99% accuracy can still be poor if the dataset contains
99% SAFE observations and the model fails to detect WARNING events.

Therefore:

Accuracy ≠ Model Quality

Model quality must be evaluated using the complete evaluation context.

---

# 2. Scientific Truth and Safety

## Rule 2.1 — Anomaly is NOT contamination

Never make the claim:

"Anomaly detected = contamination confirmed."

Correct terminology includes:

- anomaly detected
- abnormal water-quality pattern
- elevated water-quality risk
- pollution-suspected event
- possible environmental event
- requires verification

---

## Rule 2.2 — Sensor changes do not identify a specific contaminant

Changes in:

- pH
- dissolved oxygen
- turbidity
- specific conductance
- chlorophyll
- fDOM

must NOT be used alone to claim that a specific chemical contaminant
is present.

The system may identify patterns that are consistent with a possible
event, but chemical identification requires appropriate contaminant-
specific measurements or laboratory analysis.

---

## Rule 2.3 — Confirmation is a separate state

The following must remain separate:

OBSERVATION
→ ANOMALY
→ RISK
→ EVENT HYPOTHESIS
→ FORECAST
→ RECOMMENDATION
→ CONFIRMATION

"Confirmed contamination" must never be generated simply because an ML
model predicts CRITICAL.

Confirmation requires traceable evidence such as:

- laboratory testing,
- approved contaminant-specific measurement,
- or authorized human confirmation based on verified evidence.

---

## Rule 2.4 — Use uncertainty honestly

If the system does not have enough information, use:

- UNKNOWN
- INSUFFICIENT_DATA
- LOW_CONFIDENCE
- VERIFICATION_REQUIRED

Never fabricate:

- sensor values,
- explanations,
- locations,
- thresholds,
- contamination sources,
- model performance,
- confidence.

---

# 3. Data Integrity Rules

## Rule 3.1 — Raw data is immutable

Raw observations must never be silently overwritten.

Use:

RAW DATA
↓
VALIDATED DATA
↓
PROCESSED DATA
↓
MODEL FEATURES

If a value is corrected, the original value must remain traceable.

---

## Rule 3.2 — Validate every observation

Before modelling, validate:

- timestamp
- timezone
- station ID
- parameter name
- unit
- numerical value
- physical range
- calibration status
- missingness
- duplicate status
- source
- quality flags.

Invalid observations should be flagged rather than silently deleted.

---

## Rule 3.3 — Use UTC internally

All stored timestamps and API timestamps must use UTC.

Local timezone conversion should happen only in the presentation layer.

---

## Rule 3.4 — Track provenance

Every external dataset must have documented:

- source
- dataset name
- download date
- time coverage
- spatial coverage
- license/usage restrictions
- preprocessing
- transformation history.

---

## Rule 3.5 — Never invent data

AI agents and developers must never invent:

- observations
- sensor readings
- station locations
- environmental conditions
- labels
- historical events.

Synthetic data may be generated only when it is explicitly identified as
synthetic and is never presented as real observations.

---

# 4. Label Rules

## Rule 4.1 — Distinguish labels from ground truth

If a label is generated using project rules rather than laboratory-confirmed
measurements, call it:

- derived label
- rule-based label
- pseudo-label
- operational risk label.

Do NOT call it confirmed contamination ground truth.

---

## Rule 4.2 — Never change labels just to improve accuracy

Labels must represent the approved scientific/operational definition.

Do not modify thresholds simply because doing so increases model accuracy.

Any label-definition change requires:

1. documented justification,
2. version change,
3. re-generation of affected labels,
4. re-training,
5. re-evaluation.

---

## Rule 4.3 — Label versioning

Every training dataset must identify:

- label version
- label-generation method
- thresholds/rules
- source data version.

---

# 5. Temporal and Spatial Leakage Rules

## Rule 5.1 — Protect the final test period

If 2025 is the final test period:

```text
2024 and earlier → training/validation
2025             → untouched final test
```

The final test set must not influence:

- preprocessing
- feature selection
- threshold tuning
- SMOTE
- hyperparameter selection
- model selection.

---

## Rule 5.2 — Time-aware evaluation

Water-quality data is time-dependent.

Do not randomly shuffle temporal data when doing so would allow future
information to influence the past.

Use time-based validation wherever appropriate.

---

## Rule 5.3 — Consider spatial leakage

If observations from the same station appear in both training and test
sets, performance may be overly optimistic.

Where appropriate, evaluate using:

- temporal holdout,
- station holdout,
- or combined temporal/spatial validation.

---

# 6. Machine Learning Evaluation Rules

## Rule 6.1 — Never optimize for accuracy alone

Every classification model must evaluate, where applicable:

- accuracy
- precision
- recall
- F1-score
- macro F1
- weighted F1
- confusion matrix
- ROC-AUC
- PR-AUC
- class support.

For rare WARNING and CRITICAL events, pay particular attention to:

- minority recall
- minority precision
- minority F1
- macro F1.

---

## Rule 6.2 — Class imbalance must be explicitly reported

Always report:

```text
Original distribution
Training distribution
Validation distribution
Final test distribution
```

Never hide the class imbalance.

---

## Rule 6.3 — Real minority data is preferred

Preferred order:

```text
Real historical observations
        >
Validated resampling
        >
Synthetic observations
```

Synthetic data must never replace real environmental observations when
real observations can reasonably be obtained.

---

# 7. Resampling and SMOTE Rules

## Rule 7.1 — Never blindly use SMOTE

SMOTE is an experiment, not automatically the correct solution.

Compare appropriate alternatives:

- baseline
- class weighting
- balanced algorithms
- undersampling
- SMOTE
- hybrid methods
- real historical minority data.

---

## Rule 7.2 — Resampling only occurs on training data

Never apply:

- SMOTE
- undersampling
- oversampling

to the final test set.

The test set must represent the real evaluation distribution.

---

## Rule 7.3 — Synthetic samples must be validated

If SMOTE or another synthetic technique is used, verify that generated
samples remain physically/environmentally plausible.

---

# 8. Preprocessing Rules

Any preprocessing step that learns parameters must be fitted using
training data only.

Examples:

```text
Scaler       → training only
Imputer      → training only
Feature selection → training only
Dimensionality reduction → training only
Threshold tuning → training/validation only
SMOTE        → training only
```

Then apply the learned transformation to validation/test/live data.

---

# 9. Model-Specific Rules

# Model 1 — Anomaly Detection

The model answers:

> "Is this observation or pattern unusual?"

It must NOT answer:

> "Is this contamination?"

Output should include:

- anomaly state
- anomaly score
- model version
- input quality
- explanation where available.

---

# Model 2 — Risk Classification

The model answers:

> "How concerning is the measured water-quality condition?"

It may output:

- SAFE
- WARNING
- CRITICAL
- class probabilities
- confidence.

It must NOT automatically infer:

- contamination type,
- pollution source,
- chemical identity.

The current Model 2 remains experimental until its labels and minority-class
performance are sufficiently validated.

---

# Model 3 — Event Intelligence

The model answers:

> "What event pattern could explain the observed behavior?"

Possible outputs:

- seasonal variation
- runoff/sediment event
- biological activity
- abnormal inflow
- sensor/data anomaly
- pollution-suspected event.

Use language such as:

"likely pattern"

or:

"possible event"

instead of:

"confirmed pollution source."

---

# Model 4 — Forecasting

The model answers:

> "What is likely to happen next?"

Forecasts must provide:

- prediction horizon
- predicted value/risk
- uncertainty where practical
- model version
- input quality.

Never present a forecast as certainty.

---

# Spatial Propagation Engine

Spatial propagation is an intelligence layer rather than automatically being
a separate ML model.

It may combine:

- GIS
- river topology
- station locations
- upstream/downstream relationships
- hydrology
- forecasts
- event information.

Output:

- potentially affected locations
- estimated propagation
- estimated arrival time
- uncertainty
- assumptions.

---

# Model 5 — Decision Support

The model answers:

> "What action should the operator consider?"

Possible outputs:

- increase monitoring
- verify sensor
- inspect upstream area
- collect laboratory sample
- monitor downstream stations
- initiate investigation
- escalate internal alert.

Recommendations are decision support.

They do NOT automatically control infrastructure or replace authorized
human decisions.

---

# 10. Model Versioning Rules

Every production or experimental model must have:

- model name
- model version
- training date
- training data version
- training period
- validation period
- test period
- feature version
- preprocessing version
- label version
- hyperparameters
- evaluation metrics
- known limitations.

Example:

```text
risk_model_2.pkl
risk_model_2_metadata.json
risk_model_2_scaler.pkl
risk_model_2_encoder.pkl
```

---

# 11. Model Result Rules

Every model prediction should preserve:

- result ID
- station ID
- observation/window time
- model name
- model version
- prediction
- score/probability
- confidence
- input data quality
- explanation where available
- creation timestamp.

Example:

```json
{
  "result_id": "uuid",
  "station_id": "ABC01",
  "model_name": "risk",
  "model_version": "2.1",
  "status": "WARNING",
  "probability": 0.81,
  "confidence": 0.84,
  "input_data_quality": "GOOD"
}
```

---

# 12. Code Quality Rules

Use:

- Python 3.x
- descriptive names
- modular functions
- type hints where practical
- configuration instead of magic numbers
- reusable preprocessing pipelines
- clear interfaces.

Avoid:

- duplicated code
- giant monolithic scripts
- hidden preprocessing
- unexplained constants
- unnecessary dependencies
- notebook-only production logic.

---

# 13. Dependency Rules

Prefer stable, well-supported libraries.

Current ML stack may include:

- pandas
- NumPy
- scikit-learn
- imbalanced-learn
- joblib
- matplotlib
- seaborn.

Additional libraries such as:

- XGBoost
- LightGBM
- PyTorch
- TensorFlow

must only be introduced when there is a documented reason.

Do not add a library simply because it is popular.

---

# 14. Error Handling Rules

Every production component must:

- validate inputs,
- handle missing values,
- handle malformed requests,
- log errors,
- return structured errors,
- avoid silent failures.

Never:

- swallow exceptions,
- return fake predictions,
- silently discard observations,
- hide model failures.

If a model cannot make a reliable prediction, return an explicit state such
as:

```text
UNKNOWN
INSUFFICIENT_DATA
MODEL_UNAVAILABLE
```

---

# 15. Backend Rules

The backend is the central communication layer.

Frontend and Unity must communicate with the backend rather than directly
loading ML models or accessing the database.

The backend is responsible for:

- validation
- authentication
- authorization
- database access
- model inference
- orchestration
- alerts
- simulation APIs.

---

# 16. Database Rules

Do not store only the final prediction.

Maintain traceability:

```text
Raw Observation
      +
Validated Observation
      +
Features
      +
Model Result
      +
Model Version
      +
Timestamp
```

Database records should make it possible to answer:

> "Why did the system produce this result?"

---

# 17. Dashboard Rules

The dashboard must clearly distinguish:

```text
LIVE
SIMULATED
HISTORICAL
PREDICTED
ANOMALY
RISK
EVENT HYPOTHESIS
CONFIRMED
```

Never display simulated data as live data.

Never display an anomaly as confirmed contamination.

Never use color alone to communicate severity.

Example:

```text
🔴 CRITICAL
```

rather than only:

```text
🔴
```

---

# 18. Explainability Rules

Important predictions should explain:

### WHAT

What changed?

### WHERE

Which station/location?

### WHEN

When did the change occur?

### WHY

Which features contributed?

### WHAT NEXT

What is predicted?

### ACTION

What should the operator consider doing?

The explanation must not claim causality unless causality is actually
supported.

---

# 19. Unity Rules

Unity is the:

- visualization layer,
- simulation layer,
- digital-twin client.

Unity must NOT duplicate:

- ML algorithms,
- risk logic,
- backend business rules,
- database logic.

All AI inference must occur through backend services.

Unity must clearly identify simulated conditions.

---

# 20. Security Rules

Never commit:

- API keys
- passwords
- database credentials
- access tokens
- private certificates
- secrets.

Use environment variables or appropriate secret management.

Use least-privilege access.

Recommended roles:

- viewer
- researcher
- analyst
- operator
- administrator.

---

# 21. AI Coding Agent Rules

Any AI coding agent working on this project MUST:

1. Inspect the existing code before modifying it.
2. Understand the existing data schema before writing data-processing code.
3. Inspect existing model artifacts before replacing them.
4. Preserve working functionality unless there is a documented reason to change it.
5. Make focused changes rather than rewriting unrelated components.
6. Never invent dataset columns.
7. Never invent sensor values.
8. Never invent station locations.
9. Never invent model metrics.
10. Never claim a model is accurate without evaluation.
11. Never modify labels solely to improve metrics.
12. Never introduce data leakage.
13. Run relevant tests after changes.
14. Explain breaking changes.
15. Update architecture/documentation when architecture changes.
16. Preserve model/data provenance.
17. Prefer the smallest working implementation.
18. Do not create future infrastructure merely for appearance.

---

# 22. Change Management

Before modifying a major component:

1. Inspect the current implementation.
2. Identify dependencies.
3. Identify affected data contracts.
4. Identify affected models.
5. Identify affected APIs.
6. Implement the smallest necessary change.
7. Run tests.
8. Compare before/after metrics.
9. Document the change.

Do not silently replace an existing model.

---

# 23. Testing Rules

Every meaningful feature should have appropriate tests.

Examples:

### ML

- preprocessing tests
- feature-generation tests
- prediction tests
- metric tests
- leakage checks.

### API

- schema tests
- validation tests
- authentication tests
- endpoint tests.

### Integration

Test:

```text
Data
→ Backend
→ Model
→ Database
→ Dashboard
```

and:

```text
Simulation
→ Backend
→ ML
→ Prediction
→ Unity
```

---

# 24. Reproducibility Rules

Randomized models must define:

```python
random_state = 42
```

where appropriate.

Training configurations must be recorded.

A model should be reproducible from:

```text
Dataset Version
+
Code Version
+
Feature Version
+
Label Version
+
Configuration
+
Random Seed
```

---

# 25. Observability Rules

Production monitoring should track:

- ingestion failures
- stale stations
- missing observations
- API errors
- API latency
- model inference errors
- model latency
- database health
- alert failures
- data drift
- model drift.

---

# 26. Definition of Done

A feature is NOT complete merely because the code runs.

A feature is complete when:

- implementation works,
- expected output exists,
- inputs are validated,
- errors are handled,
- relevant tests pass,
- documentation is updated,
- integration works,
- metrics are evaluated where applicable,
- known limitations are documented.

---

# 27. Scientific Definition of Done for ML

An ML model is NOT considered complete merely because:

```text
training completed
```

It must also have:

- clearly defined objective,
- documented dataset,
- documented labels,
- leakage-safe evaluation,
- class distribution analysis,
- appropriate metrics,
- confusion matrix where applicable,
- baseline comparison,
- known limitations,
- saved preprocessing,
- saved model,
- model metadata,
- reproducible training process.

---

# 28. Final Non-Negotiable Rule

The project must prioritize:

SCIENTIFIC VALIDITY
        >
HONEST EVALUATION
        >
RELIABILITY
        >
EXPLAINABILITY
        >
REAL-WORLD USEFULNESS
        >
RAW ACCURACY

A lower but trustworthy metric is better than an impressive metric produced
by leakage, bad labels, synthetic inflation, or misleading evaluation.
```

### Why this combined version is stronger

I would use **this one over either original version** because it combines the strongest parts of both:

- **Chat version:** clear model-specific rules, SMOTE guidance, accuracy warning, AI-agent rules.
- **Work version:** data provenance, immutable raw data, typed contracts, spatial leakage, model versioning, security, observability, API boundaries, and production discipline.

And one especially important addition is the hierarchy:

> **Scientific validity → honest evaluation → reliability → explainability → usefulness → raw accuracy**

That rule should protect us from exactly what happened with Model 2, where **99.11% accuracy looked impressive while WARNING recall was only 3.95%**. A top-level ML engineer would immediately question the model rather than celebrate the 99% number.