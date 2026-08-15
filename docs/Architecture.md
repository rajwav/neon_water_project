# System Architecture Specification: NEON Water Intelligence Platform

**Document**: System Architecture & Technical Design  
**Target System**: Multi-Domain AI-Powered Water Contamination Detection & Digital Twin Platform  
**Version**: 3.0.0  
**Architecture Classification**: Hybrid Neuro-Symbolic Pipeline (Statistical ML + Multi-Domain Biogeochemical Constraints)

---

## 1. End-to-End System Architecture

The NEON Water Intelligence Platform operates across four integrated tiers: **Data Ingestion & Harmonization**, **Machine Learning & Neuro-Symbolic Intelligence**, **API Serving & Orchestration**, and **Interactive Visualization & IoT Emulation**.

```mermaid
graph TD
    subgraph Data Tier
        RAW_USGS_PC[USGS Physical/Chemical Dataset<br>resultphyschem.csv - 446k rows] --> ETL[ETL & Harmonization Engine]
        RAW_USGS_BIO[USGS Biological Dataset<br>biologicalresult.csv - 446k rows] --> ETL
        RAW_NEON[NEON Continuous Sensor Telemetry<br>ARIK, BARC, BIGC, BLDE, BLUE] --> ETL
        ETL --> PIVOT[Long-to-Wide Reshaping & Unit Standardization]
        PIVOT --> FE[Feature Engineering & Bio-Chem Fusion]
        FE --> PARQUET[(Processed Parquet Datastore)]
    end

    subgraph AI & Neuro-Symbolic Tier
        PARQUET --> TRAIN[Model Training Pipeline]
        TRAIN --> M1[Model 1: Multivariate Anomaly Detector<br>Isolation Forest]
        TRAIN --> M2[Model 2: Operational Risk Classifier<br>Balanced Random Forest / XGBoost]
        
        M1 --> HYB[Hybrid Decision & Safety Guardrail Engine]
        M2 --> HYB
        ENV_ENG[Biogeochemical Environmental Engine<br>WQI, OSI, CSI, OPI, ERI, Ecotoxicity] --> HYB
        HYB --> XAI[Explainable AI Attribution Generator]
    end

    subgraph Serving Tier [FastAPI Backend :8000]
        HYB --> API_CORE[FastAPI Application backend/main.py]
        XAI --> API_CORE
        API_CORE --> EP_PREDICT[POST /predict - Real-Time Inference]
        API_CORE --> EP_BATCH[POST /predict/batch - Bulk Catchment Analysis]
        API_CORE --> EP_HEALTH[GET /health - Service & Model Status]
    end

    subgraph Presentation & IoT Tier
        WOKWI[Wokwi ESP32 IoT Node<br>Physical Probes & Proxy Interfaces] -->|HTTP POST 5s| EP_PREDICT
        EP_PREDICT --> DASH[Streamlit Analytics Dashboard<br>dashboard/app.py]
        EP_BATCH --> DASH
        
        subgraph Dashboard Capabilities
            D1[Real-Time IoT Telemetry Stream]
            D2[Historical Catchment Geospatial Trends]
            D3[Neuro-Symbolic Decision Center]
            D4[Why the AI Reached This Conclusion XAI Panel]
        end
        DASH --> D1
        DASH --> D2
        DASH --> D3
        DASH --> D4
    end
```

---

## 2. Data Flow & Processing Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor Sensor as Wokwi ESP32 / USGS Sensor
    participant API as FastAPI Backend
    participant ML as AI Inference Engine (Model 1 & 2)
    participant Guardrail as Deterministic Safety Layer
    participant XAI as Explainable AI Generator
    participant UI as Streamlit Operational Dashboard

    Sensor->>API: POST /predict (JSON Telemetry)
    API->>ML: Pass normalized feature vector
    ML->>ML: Model 1 computes anomaly score & status
    ML->>ML: Model 2 computes multivariate risk & confidence
    ML->>Guardrail: Pass ML predictions + raw physical/biological telemetry
    Guardrail->>Guardrail: Evaluate hard constraints (pH, DO, Turbidity, Metals, Microbes)
    Guardrail->>Guardrail: Execute anti-eclipsing single-parameter guardrail
    Guardrail->>XAI: Pass final risk state + override triggers
    XAI->>XAI: Generate causal diagnostic attributions
    XAI-->>API: Assemble unified PredictionResponse
    API-->>UI: Deliver structured JSON payload
    UI->>UI: Render live gauges, risk alerts, and XAI explanation cards
```

---

## 3. Detailed Component Architecture

### 3.1 Data Ingestion & Harmonization Pipeline (`src/data/`)
- **Unit Normalization**: Translates disparate measurement units (`deg C`, `uS/cm @25C`, `FNU/NTU`, `mg/l as P`, `mg/l as N`) into standardized aquatic units.
- **Censored Value Handling**: Imputes Below-Detection-Limit (BDL) values using half the Method Detection Limit ($\frac{1}{2}\text{MDL}$) to eliminate missing-data bias.
- **Long-to-Wide Reshaping**: Groups atomic measurements by sampling station and timestamp, generating dense multi-parameter observation vectors.

### 3.2 Biological & Chemical Data Fusion
- **Nutrient Stoichiometry**: Computes total nitrogen to phosphorus ($\text{N}:\text{P}$) ratios to flag eutrophication thresholds.
- **Sediment-Organic Coupling**: Ratios of Suspended Sediment Concentration (SSC) to optical absorption (UV254/Sag) to identify agricultural vs. industrial runoff.
- **Taxonomic Ecotoxicity Index**: Aggregates bioindicator organism sensitivity scores (*Ceriodaphnia dubia*, *Hyalella azteca*) to produce an ecological health index.

### 3.3 Machine Learning Pipeline (`models/`)
- **Model 1 (Anomaly Detection)**:
  - Architecture: Multi-tree Isolation Forest.
  - Objective: Identify out-of-distribution multi-parameter interactions without relying on predefined thresholds.
- **Model 2 (Operational Risk Classifier)**:
  - Architecture: Cost-sensitive Balanced Random Forest / Gradient Boosted Trees.
  - Objective: Classify multi-parameter states into operational categories (`SAFE`, `WARNING`, `CRITICAL`).

### 3.4 Deterministic Environmental Safety Decision Engine (`backend/environmental_engine.py`)
- **Precedence Hierarchy**:
  1. `INSUFFICIENT_DATA` (Fewer than 2 valid sensor channels)
  2. `CRITICAL` Hard Constraint Violations (Acute lethal pH $<4$ or $>10$, DO $<2.0\text{ mg/L}$, Turbidity $>100\text{ FNU}$, SpCond $>1500\ \mu\text{S/cm}$, Heavy Metals $>0.70$)
  3. `WARNING` Moderate Constraint Violations (Sub-optimal envelope, elevated nutrients, bloom risk)
  4. `Model 2 ML Risk` (Preserved when within permissible physical envelope)
  5. `Model 1 Anomaly Watch` (Precautionary warning if ML predicts SAFE but multi-dimensional outlier detected)
  6. `SAFE` (All models and physical guardrails confirm normal operating conditions)

### 3.5 Serving & Dashboard Layer (`backend/`, `dashboard/`)
- **FastAPI Core**: Async REST API validating schemas via Pydantic v2, returning structured predictions in $<15\text{ms}$.
- **Streamlit Operational Dashboard**: Real-time monitoring console displaying:
  - Multi-station selector and telemetry streaming.
  - 4-column neuro-symbolic decision breakdown.
  - 5 Environmental Intelligence metric cards with anti-eclipsing warnings.
  - "Why the AI reached this conclusion" explainability panel.
  - Historical trend charts and observation tables.
- **Wokwi ESP32 Digital Twin**: Hardware simulation emulating physical sensor voltages, proxy interfaces, and hardware status indicator LEDs.
