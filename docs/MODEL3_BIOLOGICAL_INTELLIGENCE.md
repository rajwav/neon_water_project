# Model 3: Biological Ecosystem Health & Ecotoxicity Engine

**Module Source**: [`src/ml/biological_health_model.py`](file:///Users/raj/neon_water_project/src/ml/biological_health_model.py)  
**Artifact**: `models/v3/ecological_health_engine.joblib`  
**Dataset Assessed**: [`data/processed/usgs_water_quality.parquet`](file:///Users/raj/neon_water_project/data/processed/usgs_water_quality.parquet) (77,641 observation events)  
**Classification Hierarchy**: Multi-Domain Bio-Chemical Fusion with Anti-Eclipsing Ecological Guardrails

---

## 1. Executive Summary & Why Biological Monitoring is Essential

Traditional water monitoring relies heavily on instantaneous physical-chemical measurements (e.g., pH, conductivity, turbidity). However, chemical grab samples have fundamental limitations:
1. **Transient Chemical Spikes**: An industrial acid dump or pesticide pulse may clear within 2 hours before a grab sample is taken, but the lethal damage to living aquatic organisms persists for weeks.
2. **Chemical Cocktails & Synergistic Toxicity**: Complex mixtures of sub-threshold heavy metals, pesticides, and un-ionized ammonia often produce lethal toxicity even when each individual chemical falls within legal limits.
3. **Bioaccumulation & Trophic Transfer**: Biological bioindicator organisms integrate environmental stress over time, providing a living sensor of watershed health.

**Model 3 (Biological Health Assessment Engine)** fuses direct EPA-standard bioassay indicators (*Ceriodaphnia dubia*, *Hyalella azteca*, *Pimephales promelas*) with water chemistry to calculate the **NEON Eco Health Index ($0 - 100$)**.

---

## 2. Biological Health Engine Architecture

```mermaid
graph TD
    subgraph Multi-Domain Input Vectors
        TAXA[Taxonomic Data: Dominant Species & Richness] --> BIO_MOD[Biological Health Sub-Engines]
        BIOASSAY[Standard Bioassays: Ceriodaphnia, Hyalella, Minnow] --> BIO_MOD
        CHEM[Water Chemistry: pH, DO, Cond, Nutrients, SSC, Ammonia] --> BIO_MOD
        CHEM --> CHEM_MOD[Chemical Health Sub-Engine]
    end

    subgraph Biological Sub-Indicators (0-100)
        BIO_MOD --> S_DIV[1. Biodiversity Score: Taxa Richness & Community Capacity]
        BIO_MOD --> S_TOL[2. Pollution Tolerance Score: Species Sensitivity & Stress Penalties]
        BIO_MOD --> S_TROPH[3. Trophic Balance Score: Stoichiometry N:P & Sediment Coupling]
        BIO_MOD --> S_BIOASSAY[4. Bioassay Stress Score: Acute Lethal & Sub-Lethal Survival]
    end

    subgraph Fusion & Anti-Eclipsing Guardrails
        S_DIV & S_TOL & S_TROPH & S_BIOASSAY --> BIO_COMP["Composite Biological Health Score (0-100)"]
        CHEM_MOD --> CHEM_COMP["Chemical Health Score (0-100)"]
        
        BIO_COMP --> FUSION[Weighted Neuro-Symbolic Fusion: 50% Bio + 50% Chem]
        CHEM_COMP --> FUSION
        
        GUARD[Anti-Eclipsing Ecological Guardrail<br>Acute Chemical pH/DO Breach OR Bioassay Shock < 25] -->|Caps Index <= 28| FUSION
        
        FUSION --> FINAL_INDEX["NEON Eco Health Index (0-100)"]
        FINAL_INDEX --> TIER[Qualitative Ecological Tier: Pristine / Good / Moderate / Poor / Ecotoxic Collapse]
    end
```

---

## 3. Mathematical Formulation & Scoring Methodology

### 3.1 Four Ecological Sub-Indicators

#### 1. Biodiversity Score ($S_{\text{biodiv}} \in [0, 100]$)
Evaluates taxonomic richness ($R$) and ecological niche capacity:
$$S_{\text{biodiv}} = \begin{cases} \min\left(100, 60.0 + 15.0 \times R\right) & \text{if biological sampling present} \\ \text{Habitat capacity inferred from } \text{DO} \ge 7.5\text{ mg/L and } \text{Turbidity} \le 20\text{ FNU} & \text{otherwise} \end{cases}$$

#### 2. Pollution Tolerance Score ($S_{\text{tol}} \in [0, 100]$)
Evaluates the physiological health of the dominant bioassay organism relative to species-specific environmental thresholds:
$$S_{\text{tol}} = \text{Base}_{\text{clean}} - \left(\text{Penalty}_{\text{pH}} + \text{Penalty}_{\text{DO}} + \text{Penalty}_{\text{Ammonia}} + \text{Penalty}_{\text{Salinity}}\right)$$

*Organism Profiles Calibrated:*
- **_Ceriodaphnia dubia_ (Water flea)**: $\text{Optimal pH } 6.5 - 8.5$, $\text{DO} \ge 5.0\text{ mg/L}$, $\text{Max NH}_3 \le 0.5\text{ mg/L}$.
- **_Hyalella azteca_ (Amphipod)**: $\text{Optimal pH } 6.0 - 8.8$, $\text{DO} \ge 4.0\text{ mg/L}$, $\text{Max SSC} \le 150\text{ mg/L}$.
- **_Pimephales promelas_ (Fathead minnow)**: $\text{Optimal pH } 6.0 - 9.0$, $\text{DO} \ge 4.5\text{ mg/L}$, $\text{Max NH}_3 \le 1.2\text{ mg/L}$.

#### 3. Trophic Balance Score ($S_{\text{trophic}} \in [0, 100]$)
Measures nutrient equilibrium and autotroph-heterotroph stability:
$$S_{\text{trophic}} = 95.0 - \left(\text{Excess Total Phosphorus} \times 4.0 + \text{Excess Total Nitrogen} \times 3.0 + \text{Stoichiometric Imbalance}(\text{N}:\text{P} > 30 \lor < 4)\right)$$

#### 4. Bioassay Stress Score ($S_{\text{bioassay}} \in [0, 100]$)
Quantifies immediate ecotoxicity survival probability ($100 = \text{No Adverse Effect Level (NOAEL)}$, $0 = \text{Acute Lethal Mortality}$):
$$\text{Stress} = \text{Lethal Acid/Alkali Shock} + \text{Hypoxic Asphyxiation} + \text{Un-ionized Ammonia} + \text{Abrasive Gill Clogging (SSC)}$$
$$S_{\text{bioassay}} = 100.0 - \min(100.0, \text{Stress})$$

---

### 3.2 Composite Scores & Anti-Eclipsing Fusion

#### Composite Biological Health Score ($S_{\text{bio}}$)
$$S_{\text{bio}} = 0.30 \times S_{\text{biodiv}} + 0.30 \times S_{\text{tol}} + 0.20 \times S_{\text{trophic}} + 0.20 \times S_{\text{bioassay}}$$

#### Chemical Health Score ($S_{\text{chem}}$)
Integrated water quality score based on EPA aquatic life criteria penalties for pH, DO, Turbidity, Specific Conductance, Nutrients, and Suspended Sediment.

#### NEON Eco Health Index ($\text{EHI}$)
$$\text{Raw EHI} = 0.50 \times S_{\text{bio}} + 0.50 \times S_{\text{chem}}$$

$$\text{EHI} = \begin{cases} \min(\text{Raw EHI}, 28.0) & \text{if } S_{\text{chem}} < 30 \lor \text{pH} \notin [4, 10] \lor \text{DO} < 2.0\text{ mg/L} \lor S_{\text{bioassay}} < 25 \\ \text{Raw EHI} & \text{otherwise} \end{cases}$$

---

## 4. Ecological Classification Tiers

| NEON Eco Health Index | Ecological Status Tier | Operational Verdict | Ecological Significance |
|---|---|---|---|
| **$85.0 - 100.0$** | **Excellent (Pristine Ecosystem)** | **`SAFE`** | Unpolluted natural baseline; sensitive macroinvertebrates and bioassays thrive |
| **$70.0 - 84.9$** | **Good (Minor Stress)** | **`SAFE`** | Slight nutrient/turbidity elevation; full community reproductive capacity maintained |
| **$50.0 - 69.9$** | **Moderate (Impaired Community)** | **`WARNING`** | Chronic sub-lethal stress; sensitive bioassays displaced by tolerant taxa |
| **$30.0 - 49.9$** | **Poor (Severe Stress)** | **`WARNING`** | Severe nutrient enrichment, sediment blanketing, or dissolved oxygen deficit |
| **$0.0 - 29.9$** | **Ecotoxic Collapse** | **`CRITICAL`** | Acute chemical shock, lethal hypoxia ($\text{DO} < 2\text{ mg/L}$), or toxic bioassay mortality |

---

## 5. Dataset Assessment Results (USGS Harmonized Catchments)

Evaluated across all **77,641 sampling events**:

- **Mean Biological Health Score**: **87.48 / 100**
- **Mean Chemical Health Score**: **96.75 / 100**
- **Mean NEON Eco Health Index**: **92.00 / 100**

### Distribution of Ecological Tiers
- **Pristine Ecosystem ($85-100$)**: 70,728 events (91.1%)
- **Good / Minor Stress ($70-84$)**: 4,899 events (6.3%)
- **Moderate Impairment ($50-69$)**: 1,459 events (1.9%)
- **Ecotoxic Collapse ($<30$)**: 537 events (0.7%)
- **Poor / Severe Stress ($30-49$)**: 18 events (0.0%)

---

## 6. Diagnostic Evaluation Plots

1. `reports/usgs_eco_health_distribution.png`: Histogram and KDE distribution of NEON Eco Health Index across USGS catchments.
2. `reports/usgs_bio_vs_chem_correlation.png`: Scatter coupling of Biological Health vs. Chemical Health Scores stratified by operational risk verdict.
