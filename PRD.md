Yes. The **PRD from Chat is good for the product vision**, while the **Work PRD is much better for engineering realism** because it explicitly distinguishes what is actually implemented from what is planned.

But I would improve both further. In particular, our PRD needs to capture the **real problem we discovered with the current project**: this is not merely a SAFE/WARNING/CRITICAL classifier. The real product is an **environmental intelligence and early-warning system** where each ML layer answers a different question.

I would lock this as the final `PRD.md`:

# `PRD.md` — Canonical Product Requirements Document

```markdown
# SIH Water Intelligence Platform
## Product Requirements Document

Version: 2.0
Status: Canonical
Project Type: AI-powered environmental intelligence and early-warning system

---

# 1. Product Vision

Build an AI-powered water-intelligence platform that transforms large-scale
water-quality observations into understandable, explainable, time-aware,
spatially-aware decision support.

The platform is designed to help water-resource authorities, environmental
monitoring teams, researchers, and operators answer:

1. Is something unusual happening?
2. Is the data reliable enough to trust?
3. How severe is the measured water-quality condition?
4. What parameters changed?
5. What event pattern might explain the change?
6. Is the condition likely to worsen?
7. Where could the condition propagate?
8. What should the operator consider doing?
9. Has contamination actually been confirmed?

The platform is NOT simply a SAFE/WARNING/CRITICAL classifier.

Its purpose is to transform:

OBSERVATION
→ EVIDENCE
→ INTELLIGENCE
→ FORECAST
→ DECISION SUPPORT

---

# 2. Problem Statement

Modern water-monitoring systems can generate large volumes of sensor
measurements, but raw measurements alone do not provide sufficient
operational intelligence.

An operator may see:

- changing pH,
- decreasing dissolved oxygen,
- increasing turbidity,
- changing conductivity,
- changing chlorophyll,
- changing fDOM,

without immediately knowing:

- whether the change is normal,
- whether multiple parameters are changing together,
- whether the pattern is unusual,
- how severe the measured condition is,
- whether the condition is deteriorating,
- whether a possible environmental event is occurring,
- whether downstream locations may be affected,
- what additional verification should be performed.

The platform therefore converts raw observations into a structured chain
of environmental intelligence.

---

# 3. Core Scientific Principle

The system must maintain a strict distinction between:

```text
OBSERVATION
    ↓
DATA QUALITY
    ↓
ANOMALY
    ↓
WATER-QUALITY RISK
    ↓
EVENT HYPOTHESIS
    ↓
FORECAST
    ↓
SPATIAL IMPACT
    ↓
RECOMMENDATION
    ↓
CONFIRMATION
```

These states must never be silently merged.

---

# 4. Scientific Safety Boundary

The platform must NOT claim that:

- an anomaly proves contamination,
- sensor changes identify a specific chemical contaminant,
- a CRITICAL prediction proves pollution,
- an event hypothesis is a confirmed pollution source,
- an ML model replaces laboratory analysis,
- an AI recommendation replaces an authorized human decision.

Changes in the six initial sensor variables can indicate abnormal or elevated
water-quality conditions, but they are not sufficient by themselves to
identify a specific contaminant.

Confirmed contamination requires appropriate evidence such as:

- laboratory analysis,
- contaminant-specific instrumentation,
- validated field measurements,
- or authorized human confirmation based on verified evidence.

---

# 5. Target Users

## 5.1 Water Resource Authorities

Need:

- basin-level status,
- station status,
- historical trends,
- alerts,
- event investigation,
- downstream impact,
- recommendations.

---

## 5.2 Dam / Reservoir Operators

Need:

- current sensor status,
- anomaly detection,
- risk assessment,
- event simulation,
- forecast,
- downstream awareness.

---

## 5.3 Environmental Monitoring Teams

Need:

- detailed sensor information,
- data-quality information,
- anomaly investigation,
- event analysis,
- historical comparison,
- laboratory verification workflow.

---

## 5.4 Researchers

Need:

- historical data,
- processed data,
- model outputs,
- model metrics,
- feature importance,
- event history,
- reproducible experiments.

---

## 5.5 SIH Evaluation / Demonstration Team

Need:

- clear problem definition,
- realistic simulation,
- explainable AI,
- visible end-to-end workflow,
- measurable results,
- professional visualization.

---

# 6. Product Goals

## Primary Goals

1. Detect unusual water-quality behaviour.
2. Assess measured water-quality risk.
3. Identify multivariate event patterns.
4. Forecast future conditions.
5. Estimate possible spatial propagation.
6. Support Mahanadi-specific environmental intelligence.
7. Provide explainable recommendations.
8. Provide basin and station-level visualization.
9. Provide a digital-twin simulation.
10. Provide an integrated backend API.
11. Preserve complete prediction provenance.
12. Support human verification and response.

---

# 7. Non-Goals

The initial platform will NOT:

- automatically confirm chemical contamination,
- identify unknown chemicals from the six core sensors,
- replace laboratory testing,
- autonomously control dams, gates, treatment systems, or other
  infrastructure,
- provide unverified public-health directives,
- represent simulated data as real-world observations.

---

# 8. Initial Water-Quality Parameters

The first system version uses:

| Parameter | Purpose |
|---|---|
| pH | Acidity/alkalinity behaviour |
| Dissolved Oxygen | Oxygen availability |
| Turbidity | Suspended material / water clarity |
| Specific Conductance | Ionic/conductivity behaviour |
| Chlorophyll | Biological/algal activity indicator |
| fDOM | Dissolved organic matter indicator |

Additional parameters may be introduced after validation.

---

# 9. Product Architecture

The platform consists of:

```text
DATA SOURCES
    ↓
DATA INGESTION
    ↓
VALIDATION + QUALITY CONTROL
    ↓
FEATURE GENERATION
    ↓
DATABASE
    ↓
┌──────────────────────────────────────────────┐
│                ML INTELLIGENCE               │
│                                              │
│ Model 1 → Anomaly                           │
│ Model 2 → Risk                              │
│ Model 3 → Event Intelligence                │
│ Model 4 → Forecasting                       │
│ Spatial Intelligence → Propagation          │
│ Model 5 → Decision Support                  │
└──────────────────────────────────────────────┘
    ↓
BACKEND / API
    ↓
┌──────────────────────┬───────────────────────┐
│ Web Dashboard        │ Unity Digital Twin    │
└──────────────────────┴───────────────────────┘
```

---

# 10. Data Layer

## 10.1 Data Sources

Potential sources include:

- NEON historical observations
- sensor observations
- laboratory results
- weather
- rainfall
- hydrology
- GIS
- river topology
- station metadata
- operational records.

Each source must have documented provenance.

---

## 10.2 Data Pipeline

```text
RAW DATA
   ↓
VALIDATION
   ↓
QUALITY CONTROL
   ↓
NORMALIZATION
   ↓
FEATURE ENGINEERING
   ↓
CANONICAL DATASET
   ↓
MODEL INPUT
```

Raw observations must remain immutable.

---

# 11. Model Architecture

The platform uses logically separate intelligence layers.

They communicate through structured outputs rather than becoming one giant
ML model.

---

# 12. Model 1 — Anomaly Detection

## Purpose

Determine whether current multivariate behaviour is unusual relative to
expected behaviour.

## Question

> Is something unusual happening?

## Inputs

Initial:

- pH
- dissolved oxygen
- turbidity
- specific conductance
- chlorophyll
- fDOM

Potential future inputs:

- temporal features
- station baseline
- seasonal context
- environmental context.

## Outputs

```text
anomaly_flag
anomaly_score
model_version
input_quality
contributing_features
```

## Current implementation

Isolation Forest.

## Scientific boundary

Anomaly ≠ contamination.

---

# 13. Model 2 — Water-Quality Risk Classification

## Purpose

Estimate how concerning the measured water-quality condition is.

## Question

> How severe is the observed water-quality condition?

## Outputs

```text
SAFE
WARNING
CRITICAL
```

plus:

- class probabilities,
- confidence,
- model version,
- input quality.

## Current implementation

Balanced Random Forest experiments.

## Important limitation

Current labels are derived/rule-based labels rather than necessarily
laboratory-confirmed ground truth.

Therefore Model 2 remains experimental until:

- labels are scientifically reviewed,
- temporal leakage is ruled out,
- minority-class performance is validated,
- evaluation is performed on untouched test data.

---

# 14. Model 3 — Event Intelligence

## Purpose

Identify patterns that may explain an observed abnormal/risky condition.

## Question

> What type of event does this pattern resemble?

Potential categories:

- normal variation
- seasonal variation
- rainfall/runoff
- sediment disturbance
- biological activity
- abnormal inflow
- operational event
- sensor/data anomaly
- pollution-suspected event
- unknown.

## Inputs

Potentially:

- Model 1 output
- Model 2 output
- sensor trends
- weather
- rainfall
- hydrology
- temporal context
- historical event patterns.

## Outputs

Ranked hypotheses:

```text
event_type
probability/confidence
supporting_evidence
alternative_hypotheses
uncertainty
```

The output must remain a hypothesis.

---

# 15. Model 4 — Forecasting

## Purpose

Predict future water-quality behaviour.

## Question

> What is likely to happen next?

Potential horizons:

- 30 minutes
- 1 hour
- 3 hours
- 6 hours
- 12 hours
- 24 hours.

## Outputs

- predicted sensor values,
- predicted risk,
- deterioration probability,
- trend,
- uncertainty interval.

## Development principle

Begin with simple statistical/baseline methods.

Introduce complex ML/deep learning only when justified by validation.

---

# 16. Spatial Intelligence

Spatial intelligence determines where a detected or predicted condition
could potentially propagate.

## Inputs

- station locations
- river topology
- flow direction
- hydrology
- Model 3 event information
- Model 4 forecasts
- station relationships.

## Outputs

- potentially affected stations
- downstream risk
- estimated propagation
- estimated arrival time
- uncertainty
- assumptions.

Spatial estimates must never be represented as measured boundaries.

---

# 17. Model 5 — Decision Support

## Purpose

Convert environmental intelligence into recommended operational actions.

## Question

> What should the operator consider doing?

## Inputs

- anomaly
- risk
- event hypothesis
- forecast
- spatial impact
- data quality
- severity
- historical context.

## Possible recommendations

- verify sensor
- increase monitoring frequency
- inspect upstream conditions
- collect laboratory sample
- monitor downstream stations
- initiate investigation
- escalate internal alert.

## Safety boundary

Model 5 provides decision support.

It does not autonomously control infrastructure.

---

# 18. Mahanadi Intelligence

The Mahanadi module will provide basin-specific intelligence.

It will incorporate, where validated:

- monitoring locations,
- river topology,
- upstream/downstream relationships,
- historical behaviour,
- seasonality,
- hydrology,
- local environmental context,
- spatial propagation.

The generic water-quality model should not simply be assumed to represent
every Mahanadi location equally.

Station-specific and basin-specific behaviour must be evaluated.

---

# 19. Digital Twin

Unity provides the visual simulation layer.

The digital twin contains:

- river/reservoir environment,
- virtual monitoring stations,
- virtual sensors,
- water-condition visualization,
- event injection,
- propagation visualization,
- forecast visualization,
- AI status.

---

## Digital Twin Scenario

Example:

```text
Normal State
     ↓
Simulated Upstream Event
     ↓
Virtual Sensor Changes
     ↓
Model 1
     ↓
Model 2
     ↓
Model 3
     ↓
Model 4
     ↓
Spatial Intelligence
     ↓
Model 5
     ↓
Dashboard Alert
     ↓
Unity Visualization
```

Unity must consume the backend's versioned APIs.

It must not contain independent ML logic.

---

# 20. Dashboard Requirements

## 20.1 Overview

Display:

- system health,
- active alerts,
- station count,
- anomaly count,
- risk distribution,
- data freshness,
- critical events.

---

## 20.2 Basin Map

Display:

- monitoring stations,
- river network,
- current risk,
- anomaly status,
- events,
- downstream relationships,
- possible affected areas.

---

## 20.3 Station Detail

Display:

- station identity,
- location,
- data quality,
- six sensor values,
- trends,
- anomaly,
- risk,
- event hypotheses,
- forecast,
- spatial impact,
- recommendations,
- history.

---

## 20.4 Event Detail

Display:

- event timeline,
- observations,
- data quality,
- anomaly result,
- risk result,
- event hypotheses,
- evidence,
- forecast,
- spatial impact,
- recommendation,
- confirmation status,
- acknowledgement history.

---

## 20.5 Alerts

Each alert should contain:

- severity,
- station,
- observed time,
- data freshness,
- affected parameters,
- anomaly,
- risk,
- event hypothesis,
- confidence,
- recommendation,
- confirmation state.

---

## 20.6 Analytics

Provide:

- parameter trends,
- risk trends,
- anomaly history,
- event history,
- station comparison,
- model performance,
- feature importance.

---

# 21. Backend Requirements

The backend is the central communication layer.

Responsibilities:

- ingest observations,
- validate payloads,
- store data,
- retrieve data,
- invoke models,
- store predictions,
- generate alerts,
- expose APIs,
- provide simulation endpoints,
- provide dashboard data,
- communicate with Unity,
- maintain audit records.

Recommended:

FastAPI.

---

# 22. Database Requirements

Recommended:

PostgreSQL.

Potential:

PostGIS for spatial data.

Potential:

TimescaleDB for time-series workloads.

Store:

- stations,
- raw observations,
- validated observations,
- quality flags,
- features,
- model results,
- alerts,
- events,
- forecasts,
- recommendations,
- confirmations,
- audit records.

The system must preserve enough information to answer:

> Why did the system produce this result?

---

# 23. API Requirements

Initial API surface:

```text
GET  /v1/stations
GET  /v1/stations/{id}
GET  /v1/stations/{id}/observations
GET  /v1/stations/{id}/status
GET  /v1/stations/{id}/risk
GET  /v1/stations/{id}/anomaly
GET  /v1/stations/{id}/forecast

GET  /v1/events
GET  /v1/alerts
GET  /v1/map/layers
GET  /v1/models/status

POST /v1/observations
POST /v1/simulation/event
GET  /v1/simulation/state

POST /v1/events/{id}/acknowledge
```

All production write endpoints require validation, authentication,
authorization, and audit logging.

---

# 24. Model Result Contract

Every model should return a structured result.

Example:

```json
{
  "result_id": "uuid",
  "station_id": "MHD-04",
  "window_start": "2026-08-15T10:00:00Z",
  "window_end": "2026-08-15T10:15:00Z",
  "model_name": "risk",
  "model_version": "2.0",
  "status": "WARNING",
  "score": 0.78,
  "confidence": 0.81,
  "input_data_quality": "GOOD",
  "explanation": {
    "top_factors": [
      "dissolvedOxygen",
      "turbidity"
    ]
  }
}
```

---

# 25. User Experience Requirements

The system should answer:

```text
What is happening?
        ↓
Where?
        ↓
Is the data reliable?
        ↓
How severe?
        ↓
Why might it be happening?
        ↓
What happens next?
        ↓
Where might it go?
        ↓
What should I consider doing?
        ↓
Has it been confirmed?
```

A user should not need to navigate through many pages to understand a
significant event.

---

# 26. Success Criteria

The platform is successful when:

### Data

A valid observation can be ingested, validated, stored, and retrieved.

### Model 1

An unusual multivariate pattern can be detected and explained.

### Model 2

Measured water-quality risk can be assessed with scientifically defensible
labels and minority-class performance.

### Model 3

Possible event patterns can be identified with uncertainty.

### Model 4

Future behaviour can be forecast with measurable performance and uncertainty.

### Spatial Intelligence

Potential downstream impact can be estimated with documented assumptions.

### Model 5

The system can provide traceable decision-support recommendations.

### Dashboard

An operator can understand the complete event.

### Unity

A simulated event can be visualized end-to-end.

---

# 27. Primary Demonstration Scenario

The primary SIH demonstration should tell one complete story.

## Step 1

System begins in normal conditions.

## Step 2

A clearly labelled simulated event is introduced upstream.

## Step 3

Virtual sensors change.

## Step 4

Model 1 detects an unusual pattern.

## Step 5

Model 2 evaluates operational risk.

## Step 6

Model 3 evaluates possible event patterns.

## Step 7

Model 4 predicts future deterioration.

## Step 8

Spatial intelligence estimates downstream impact.

## Step 9

Model 5 recommends an appropriate response.

## Step 10

Dashboard generates an alert.

## Step 11

Unity visualizes propagation.

## Step 12

The system identifies laboratory verification as required where
contamination confirmation is necessary.

This demonstrates the complete intelligence chain without pretending that
the simulation is real contamination.

---

# 28. Non-Functional Requirements

## Reliability

The system must degrade gracefully when:

- sensors are missing,
- data is stale,
- models fail,
- APIs fail,
- databases fail.

---

## Security

Never expose:

- API keys
- passwords
- database credentials
- model secrets
- private tokens.

---

## Performance

The system should support near-real-time inference for incoming observations
once deployed.

Exact latency targets will be defined after deployment constraints are known.

---

## Explainability

Every significant model output must provide sufficient metadata to trace:

```text
Input
→ Feature
→ Model
→ Version
→ Output
→ Explanation
```

---

## Reproducibility

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

# 29. Current Project Status

| Component | Status |
|---|---|
| NEON data acquisition | Existing |
| Data preprocessing | Existing / requires formalization |
| Canonical data contract | Planned |
| Model 1 — Anomaly Detection | Implemented |
| Model 2 — Risk Classification | Experimental |
| Historical minority-event expansion | Planned |
| Model 3 — Event Intelligence | Planned |
| Model 4 — Forecasting | Planned |
| Spatial Intelligence | Planned |
| Model 5 — Decision Support | Planned |
| Backend | Planned |
| Database | Planned |
| Web Dashboard | Prototype / planned integration |
| Unity Digital Twin | Planned |
| End-to-end integration | Planned |

Current status must be updated as implementation progresses.

---

# 30. Product Principles

The platform prioritizes:

1. Scientific validity
2. Data integrity
3. Honest model evaluation
4. Explainability
5. Reliability
6. Real-world usefulness
7. Human decision support
8. Visual clarity
9. Raw accuracy

Accuracy is important, but it is not the sole definition of success.

---

# 31. Final Product Definition

NEON Water Intelligence is not:

> "An AI that detects contaminated water."

It is:

> "An AI-powered environmental intelligence platform that detects unusual
> water-quality behaviour, evaluates operational risk, identifies possible
> event patterns, forecasts future conditions, estimates spatial impact, and
> provides explainable decision support while preserving the distinction
> between model inference and confirmed contamination."

This definition is the foundation for the architecture, rules, development
phases, design system, models, backend, dashboard, and Unity digital twin.
```

### One important correction from the earlier PRD

I would **not** describe Model 5 simply as a "response model" yet. That makes it sound like we have already decided a fifth ML algorithm must generate recommendations.

The stronger architecture is:

**Model 1 — Anomaly**  
→ *Is something unusual?*

**Model 2 — Risk**  
→ *How concerning is it?*

**Model 3 — Event Intelligence**  
→ *What might explain it?*

**Model 4 — Forecast**  
→ *What might happen next?*

**Spatial Intelligence**  
→ *Where might it go?*

**Model 5 / Decision Intelligence**  
→ *What should the operator consider doing?*

That distinction will make the project much easier to defend in front of a technically strong SIH jury.