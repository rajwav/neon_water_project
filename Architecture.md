

# `Architecture.md` — Canonical Version

```markdown
# NEON Water Intelligence System
## System Architecture

Version: 2.0
Status: Canonical Architecture
Purpose: SIH Development Blueprint

---

# 1. Architecture Vision

The NEON Water Intelligence System is a layered AI-powered water-quality
early-warning and decision-support platform.

The system is designed to:

1. Ingest water-quality observations.
2. Validate and quality-control measurements.
3. Detect unusual water-quality behavior.
4. Assess water-quality risk.
5. Identify likely event patterns.
6. Forecast future water-quality conditions.
7. Estimate spatial/downstream impact.
8. Recommend appropriate response actions.
9. Visualize the complete situation through a web dashboard.
10. Simulate events through a Unity digital twin.
11. Preserve a clear distinction between AI inference and confirmed
    contamination.

The system is NOT designed to claim that an anomalous sensor measurement
automatically proves contamination.

---

# 2. Core Architecture Principle

The system separates:

OBSERVATION
DERIVED FEATURE
ANOMALY
RISK
EVENT HYPOTHESIS
FORECAST
SPATIAL IMPACT
RECOMMENDATION
CONFIRMATION

These are separate concepts and must remain separate in the database,
backend, ML pipeline, dashboard, and Unity system.

Example:

Anomaly detected
≠
Contamination confirmed

Risk = CRITICAL
≠
Specific pollutant confirmed

Pollution-suspected event
≠
Laboratory confirmation

---

# 3. Complete System Architecture

```text
                         DATA SOURCES
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
    NEON Historical      Live Sensors       Laboratory Data
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                  +-----------------------+
                  | INGESTION LAYER       |
                  | API / File / Stream   |
                  +-----------+-----------+
                              |
                              v
                  +-----------------------+
                  | DATA VALIDATION       |
                  | Units / Range / QC    |
                  | Missing / Duplicate   |
                  +-----------+-----------+
                              |
                              v
                  +-----------------------+
                  | FEATURE ENGINEERING   |
                  | Temporal / Statistical|
                  | Environmental Context |
                  +-----------+-----------+
                              |
                              v
                  +-----------------------+
                  | DATABASE              |
                  | PostgreSQL             |
                  | + PostGIS              |
                  | + TimescaleDB*         |
                  +-----------+-----------+
                              |
                +-------------+-------------+
                |                           |
                v                           v
        +---------------+          +----------------+
        | ML ENGINE     |          | CONTEXT ENGINE |
        +-------+-------+          +--------+-------+
                |                           |
        +-------+--------+           +------+------+
        |       |        |           |      |      |
        v       v        v           v      v      v
       M1      M2       M3       Weather  GIS  Hydrology
        |       |        |
        |       |        |
        |       |        |
        +-------+--------+
                |
                v
        +------------------+
        | MODEL 4          |
        | FORECASTING      |
        +--------+---------+
                 |
                 v
        +------------------+
        | SPATIAL          |
        | PROPAGATION      |
        | ENGINE           |
        +--------+---------+
                 |
                 v
        +------------------+
        | MODEL 5          |
        | DECISION SUPPORT |
        +--------+---------+
                 |
        +--------+---------+
        |                  |
        v                  v
 +-------------+    +-------------+
 | WEB         |    | UNITY       |
 | DASHBOARD   |    | DIGITAL     |
 | + MAP       |    | TWIN        |
 +------+------+    +------+------+
        |                  |
        +--------+---------+
                 |
                 v
       WATER OPERATORS /
       AUTHORITIES /
       RESEARCHERS
                 |
                 v
      HUMAN / LABORATORY
        CONFIRMATION
```

*TimescaleDB is optional and should be adopted only if the time-series
workload justifies it.

---

# 4. Architectural Layers

The system consists of nine major layers.

## Layer 1 — Data Sources

Sources include:

- NEON historical datasets
- live sensor streams
- simulated sensor data
- laboratory measurements
- weather data
- hydrological data
- GIS/geographic information
- reservoir/river information

---

# 5. Layer 2 — Data Ingestion

The ingestion layer receives:

- CSV files
- API data
- sensor readings
- simulation events
- laboratory results.

Responsibilities:

- schema validation
- timestamp normalization
- unit normalization
- source identification
- ingestion timestamp
- duplicate detection
- malformed-data rejection.

All timestamps are stored in UTC.

---

# 6. Layer 3 — Data Quality and Validation

Every observation should have quality information.

Example:

```json
{
  "station_id": "ABC01",
  "observed_at": "2026-08-15T10:30:00Z",
  "parameter": "pH",
  "value": 7.12,
  "unit": "pH",
  "source": "sensor",
  "quality_flags": [],
  "schema_version": "1.0"
}
```

Potential quality flags:

- missing
- out_of_range
- duplicate
- stale
- sensor_error
- calibration_required
- interpolated
- simulated.

Raw data must remain immutable.

Corrected/validated data must be stored separately.

---

# 7. Layer 4 — Feature Engineering

Features may include:

## Sensor features

- pH
- dissolved oxygen
- turbidity
- specific conductance
- chlorophyll
- fDOM

## Temporal features

- hour
- day
- month
- season
- rolling mean
- rolling standard deviation
- rate of change
- lag features

## Spatial features

- station
- upstream/downstream relationship
- distance
- river segment
- watershed

## Environmental context

- rainfall
- temperature
- flow
- reservoir level
- operational information.

Only features that are scientifically justified should be introduced.

---

# 8. Layer 5 — ML Intelligence

The system contains five specialized model layers.

The models are logically independent but communicate through standardized
model-result contracts.

---

# 9. Model 1 — Anomaly Detection

## Question

"Is the current water-quality behavior unusual compared with expected
behavior?"

### Input

Validated multivariate sensor history.

### Output

- anomaly flag
- anomaly score
- baseline information
- contributing features where possible.

Example:

```json
{
  "model_name": "anomaly",
  "model_version": "1.0",
  "status": "anomalous",
  "score": 0.91,
  "confidence": 0.88
}
```

### Current implementation

Isolation Forest.

### Important limitation

Anomaly detection does NOT prove contamination.

---

# 10. Model 2 — Water Quality Risk Classification

## Question

"How concerning is the current water-quality condition?"

### Input

Validated water-quality measurements and approved features.

### Output

- SAFE
- WARNING
- CRITICAL
- class probabilities
- confidence.

Example:

```json
{
  "model_name": "risk",
  "model_version": "2.0",
  "status": "warning",
  "probabilities": {
    "safe": 0.12,
    "warning": 0.81,
    "critical": 0.07
  }
}
```

### Current implementation

Balanced Random Forest.

### Current known problem

The existing Model 2 has severe class imbalance and poor WARNING recall.

The current derived-label methodology must be validated before treating
these labels as ground truth.

### Critical rule

Anomaly information must not automatically be converted into a CRITICAL
classification simply by adding an arbitrary fixed score.

---

# 11. Model 3 — Event Intelligence

## Question

"What type of event does the observed pattern resemble?"

Potential categories:

- normal variation
- seasonal variation
- sediment/runoff event
- biological activity
- abnormal inflow
- sensor/data anomaly
- pollution-suspected event.

### Input

- sensor features
- temporal features
- Model 1 output
- Model 2 output
- weather
- hydrology
- operational context.

### Output

Ranked event hypotheses.

Example:

```json
{
  "event": "sediment_runoff_suspected",
  "probability": 0.76,
  "alternatives": [
    {
      "event": "abnormal_inflow",
      "probability": 0.18
    }
  ]
}
```

The output represents a hypothesis, not confirmed causation.

---

# 12. Model 4 — Forecasting

## Question

"What is likely to happen next?"

Forecast horizons may include:

- 30 minutes
- 1 hour
- 3 hours
- 6 hours
- 12 hours
- 24 hours.

### Inputs

Historical time series plus relevant environmental context.

### Outputs

- future parameter values
- future risk
- deterioration probability
- confidence/uncertainty interval.

The system must never represent a forecast as certainty.

---

# 13. Spatial Propagation Engine

Spatial analysis is NOT necessarily a sixth ML model.

It is a separate intelligence layer combining:

- GIS
- river topology
- station locations
- upstream/downstream relationships
- hydrology
- forecast output
- event information.

Example:

```text
Upstream Station A
        |
        v
   River Segment
        |
        v
Station B
        |
        v
Station C
```

If Station A experiences a significant event, the system can estimate
which downstream locations may become affected.

Outputs:

- potentially affected stations
- estimated arrival time
- spatial risk
- confidence
- assumptions.

---

# 14. Model 5 — Decision Support

## Question

"What should the operator consider doing?"

### Inputs

- anomaly result
- risk result
- event hypotheses
- forecast
- spatial impact
- data quality.

### Outputs

Examples:

- increase monitoring frequency
- verify sensor
- inspect upstream area
- collect laboratory sample
- monitor downstream station
- initiate investigation
- escalate alert.

The system provides recommendations.

Authorized humans remain responsible for operational decisions.

---

# 15. Model Independence

The five models must NOT become one giant model.

Each model performs one primary task.

```text
Model 1
"What changed?"

Model 2
"How concerning is it?"

Model 3
"What pattern might explain it?"

Model 4
"What happens next?"

Spatial Engine
"Where might it go?"

Model 5
"What should we consider doing?"
```

This makes the architecture:

- explainable,
- testable,
- replaceable,
- modular,
- easier to improve.

---

# 16. Standard Model Result Contract

All models should return a common base structure.

```json
{
  "result_id": "uuid",
  "station_id": "ABC01",
  "window_start": "ISO-8601 UTC",
  "window_end": "ISO-8601 UTC",
  "model_name": "risk",
  "model_version": "2.0",
  "status": "warning",
  "score": 0.81,
  "confidence": 0.84,
  "explanation": {
    "top_factors": []
  },
  "input_data_quality": "good",
  "created_at": "ISO-8601 UTC"
}
```

Specialized models can add their own typed fields.

---

# 17. Contamination Confirmation

Confirmed contamination is NOT an ML classification state.

It must be represented separately.

Example:

```text
AI:
pollution-suspected event
        |
        v
Laboratory investigation
        |
        v
Confirmed / Not confirmed
```

This prevents the dashboard from misleading users.

---

# 18. Database Architecture

Recommended:

PostgreSQL

Optional:

TimescaleDB for large-scale time-series queries.

PostGIS for spatial data.

## Core entities

### stations

- station_id
- name
- latitude
- longitude
- river
- watershed
- metadata.

### observations

- observation_id
- station_id
- parameter
- value
- unit
- observed_at
- source
- quality_flags.

### model_results

- result_id
- model_name
- model_version
- station_id
- prediction
- confidence
- created_at.

### events

- event_id
- event_type
- start_time
- end_time
- affected_stations
- severity
- status.

### forecasts

- forecast_id
- station_id
- horizon
- predicted_value
- uncertainty
- model_version.

### recommendations

- recommendation_id
- event_id
- action
- priority
- rationale.

### confirmations

- confirmation_id
- event_id
- laboratory result
- reviewer
- confirmation status
- timestamp.

---

# 19. Backend Architecture

Recommended:

FastAPI + Pydantic.

Responsibilities:

- authentication
- authorization
- input validation
- database access
- model inference
- event orchestration
- alert generation
- simulation control
- dashboard APIs.

The backend is the central communication layer.

---

# 20. API Structure

Initial API:

GET /v1/stations

GET /v1/stations/{station_id}

GET /v1/stations/{station_id}/observations

GET /v1/stations/{station_id}/status

GET /v1/stations/{station_id}/risk

GET /v1/stations/{station_id}/anomaly

GET /v1/stations/{station_id}/forecast

GET /v1/events

GET /v1/alerts

GET /v1/map/layers

GET /v1/models/status

POST /v1/observations

POST /v1/simulation/event

GET /v1/simulation/state

POST /v1/events/{event_id}/acknowledge

---

# 21. API Security

All write endpoints must provide:

- authentication
- authorization
- input validation
- audit logging
- rate limiting where required
- idempotency for appropriate operations.

Never expose:

- database credentials
- model files
- secret keys
- internal paths.

---

# 22. Frontend Architecture

Recommended:

React + TypeScript.

Responsibilities:

- dashboard
- maps
- station pages
- analytics
- alerts
- forecasts
- event investigation
- model explanations
- reports.

---

# 23. Map Architecture

Recommended:

MapLibre GL JS or Leaflet.

The map displays:

- monitoring stations
- river network
- risk
- anomalies
- events
- affected zones
- forecast propagation.

Station selection opens detailed intelligence.

---

# 24. Station Detail Page

Example:

```text
Station: XYZ-01
Location: Mahanadi

Current Status:
WARNING

Anomaly:
DETECTED

Forecast:
DETERIORATING

Event:
RUNOFF-SUSPECTED

Data Quality:
GOOD
```

Sensor cards:

- pH
- DO
- turbidity
- conductivity
- chlorophyll
- fDOM.

Each includes:

- current value
- unit
- timestamp
- trend
- historical comparison.

---

# 25. Dashboard Architecture

Main pages:

1. Overview
2. Live Monitoring
3. Map
4. Stations
5. Alerts
6. Events
7. Forecasts
8. Analytics
9. Mahanadi Intelligence
10. Digital Twin
11. Reports
12. Model Intelligence.

---

# 26. Unity Digital Twin

Unity is a simulation and visualization client.

Unity must NOT duplicate ML logic.

Unity communicates through backend APIs.

Example:

```text
Unity
  |
  | POST /v1/simulation/event
  v
Backend
  |
  v
Simulation Engine
  |
  v
ML Pipeline
  |
  v
Predictions
  |
  v
Database
  |
  v
Unity
```

Unity displays:

- water body
- stations
- virtual sensors
- event origin
- event propagation
- risk
- forecast
- affected areas.

---

# 27. Simulation Workflow

Example:

```text
Normal State
     ↓
Inject Event
     ↓
Sensor values change
     ↓
Data validation
     ↓
Model 1
Anomaly detected
     ↓
Model 2
Risk increases
     ↓
Model 3
Event pattern identified
     ↓
Model 4
Future deterioration forecast
     ↓
Spatial Engine
Downstream impact estimated
     ↓
Model 5
Recommended actions
     ↓
Dashboard + Unity
```

This becomes the primary demonstration scenario.

---

# 28. Mahanadi Intelligence

The Mahanadi module should incorporate:

- monitoring stations
- river geometry
- upstream/downstream relationships
- historical patterns
- seasonal behavior
- hydrology
- location-specific baselines
- event propagation.

The Mahanadi system must not assume that generic NEON behavior represents
the Mahanadi.

Local calibration is required.

---

# 29. Repository Structure

```text
neon_water_project/

├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
│
├── data_contracts/
│
├── models/
│   ├── train_anomaly_model.py
│   ├── train_risk_model.py
│   ├── train_event_model.py
│   ├── train_forecast_model.py
│   ├── train_response_model.py
│   └── saved_models/
│
├── ml/
│   ├── features/
│   ├── preprocessing/
│   ├── evaluation/
│   └── inference/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── database/
│   │   ├── schemas/
│   │   └── models/
│   └── tests/
│
├── frontend/
│   ├── pages/
│   ├── components/
│   ├── charts/
│   ├── map/
│   └── services/
│
├── unity/
│   └── WaterDigitalTwin/
│
├── notebooks/
│
├── results/
│
├── tests/
│
├── scripts/
│
├── docs/
│
├── PRD.md
├── Architecture.md
├── Rules.md
├── Phases.md
├── Design.md
└── Memory.md
```

Memory.md should only be created after implementation begins.

Do not create folders simply for appearance. Introduce components when their
first working implementation exists.

---

# 30. Model Storage

Each model must have:

- model artifact
- preprocessing artifact
- encoder if required
- metadata
- training configuration
- evaluation results.

Example:

```text
models/saved_models/

risk_model_2.pkl
status_encoder_2.pkl
feature_scaler_2.pkl
model_2_metadata.pkl
```

---

# 31. Model Metadata

Metadata should include:

- model name
- version
- training date
- training data range
- test data range
- features
- preprocessing
- metrics
- class distribution
- known limitations.

---

# 32. Data Leakage Prevention

Training preprocessing must NEVER learn from final test data.

Examples:

Scaler:
fit on training only.

Imputer:
fit on training only.

SMOTE:
training data only.

Feature selection:
training data only.

Threshold optimization:
training/validation data only.

Final test data remains untouched until final evaluation.

---

# 33. Model Evaluation

Do not evaluate primarily on accuracy.

Track:

- precision
- recall
- F1
- macro F1
- weighted F1
- confusion matrix
- ROC-AUC
- PR-AUC where appropriate
- class support
- calibration where practical.

For rare critical events, minority recall is especially important.

---

# 34. Historical Data

Historical data must pass through the same validated preprocessing pipeline.

Do not manually extract WARNING/CRITICAL rows using inconsistent rules.

Historical labels must be generated using the approved labeling methodology.

Real minority observations are preferred over synthetic observations.

---

# 35. Current Model 2 Issue

Current Model 2 experiments show:

- very high overall accuracy,
- extremely dominant SAFE class,
- weak WARNING recall.

Therefore:

Accuracy alone must NOT be used to claim Model 2 is excellent.

Model 2 requires further evaluation and potentially:

- improved labels,
- historical minority events,
- class weighting,
- carefully validated resampling,
- alternative algorithms,
- threshold optimization,
- temporal validation.

---

# 36. Observability

Monitor:

- ingestion failures
- stale stations
- missing data
- API latency
- model latency
- model errors
- database health
- alert failures
- model drift
- data drift.

---

# 37. Deployment

Recommended:

Docker-based services.

Potential services:

```text
backend
database
ml-service
frontend
```

Unity remains a client/simulation application.

Development should work locally before cloud deployment.

---

# 38. Security

Never commit:

- API keys
- passwords
- database credentials
- tokens
- private certificates.

Use:

.env

secret management in deployment.

Use role-based access:

- viewer
- researcher
- analyst
- operator
- administrator.

---

# 39. Scientific Integrity

The system must never transform:

ANOMALY
into
CONFIRMED CONTAMINATION

without independent evidence.

The dashboard must distinguish:

LIVE
SIMULATED
HISTORICAL
PREDICTED
ANOMALOUS
RISK
SUSPECTED EVENT
CONFIRMED EVENT.

---

# 40. Architecture Success Criterion

The architecture is considered successfully implemented when the following
end-to-end workflow works:

```text
Data
 ↓
Validation
 ↓
Feature Engineering
 ↓
Database
 ↓
Model 1
 ↓
Model 2
 ↓
Model 3
 ↓
Model 4
 ↓
Spatial Propagation
 ↓
Model 5
 ↓
Backend API
 ↓
Dashboard / Map
 ↓
Unity Digital Twin
 ↓
Operator Decision
 ↓
Laboratory/Human Confirmation
```

The system should be demonstrable using both historical data and controlled
simulation.

---

# 41. Final Design Principle

The system is not five disconnected ML models.

It is one water-intelligence platform composed of specialized intelligence
layers.

The architecture should allow each model to be independently improved or
replaced without rebuilding the entire platform.
```

## This is the one I would lock in.

The most important change from both previous versions is this:

**Model 5 is Decision Support, while spatial propagation is a separate intelligence layer.**

So our final intelligence chain is:

**Model 1 → Detect**  
**Model 2 → Assess**  
**Model 3 → Explain/Event hypothesis**  
**Model 4 → Predict**  
**Spatial Engine → Locate/Propagate**  
**Model 5 → Recommend**

And the final human/lab layer answers the question the ML system **cannot honestly answer by itself**:

**“Is contamination actually confirmed?”**

That gives us a much stronger foundation for the rest of the project.