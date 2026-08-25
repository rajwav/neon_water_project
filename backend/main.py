"""
FastAPI Backend for SIH Water Intelligence Platform (Production Master v5.0).

Endpoints:
  - GET  /health   -> Health check, service status, and model catalog (Models 1, 2, 3, 4, 5)
  - POST /predict  -> Integrated AI pipeline (M1 Anomaly + M2 Risk + M3 Bio + M4 Forecaster + M5 Decision Support)
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from backend.model_loader import engine

app = FastAPI(
    title="SIH Water Intelligence Platform API",
    description="Production FastAPI backend serving Model 1 (Anomaly Detection), Model 2 (Risk Classification), Model 3 (Biological Ecosystem Health Engine), Model 4 (Predictive Early Warning Forecaster), and Model 5 (AI Decision Support & Response Recommendation Engine).",
    version="5.0.0",
)

# Enable CORS for frontend / dashboard / IoT integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Schemas ─────────────────────────────────────

class PredictionRequest(BaseModel):
    # Physical / Chemical Core
    ph: Optional[float] = Field(None, examples=[7.42], description="Water pH level")
    dissolved_oxygen: Optional[float] = Field(None, examples=[8.65], description="Dissolved oxygen in mg/L")
    turbidity: Optional[float] = Field(None, examples=[4.5], description="Turbidity in FNU/NTU")
    specific_conductance: Optional[float] = Field(None, examples=[280.0], description="Specific conductance in µS/cm")
    fdom: Optional[float] = Field(None, examples=[22.0], description="Fluorescent DOM in QSU")
    temperature: Optional[float] = Field(None, examples=[21.3], description="Water temperature in Celsius")
    site_id: str = Field(default="WOKWI_SITE", examples=["WOKWI_SITE"], description="Monitoring site code (ARIK, BARC, BIGC, BLDE, BLUE, WOKWI_SITE)")
    sensor_position: str = Field(default="001", examples=["001"], description="Sensor station position (e.g. 101, 102, 001)")

    # Nutrients Suite
    chlorophyll_a_ug_l: Optional[float] = Field(None, examples=[2.8], description="Chlorophyll a in µg/L")
    chlorophyll: Optional[float] = Field(None, examples=[2.8], description="Alias for chlorophyll a in µg/L")
    nitrate_mg_l: Optional[float] = Field(None, examples=[0.45], description="Nitrate NO3 in mg/L")
    nitrate: Optional[float] = Field(None, examples=[0.45], description="Alias for nitrate in mg/L")
    phosphate_mg_l: Optional[float] = Field(None, examples=[0.015], description="Phosphate PO4 in mg/L")
    phosphate: Optional[float] = Field(None, examples=[0.015], description="Alias for phosphate in mg/L")
    suspended_sediment: Optional[float] = Field(None, examples=[35.0], description="Suspended Sediment Concentration (SSC) in mg/L")

    # Contamination Proxies
    lead_risk_index: Optional[float] = Field(None, examples=[0.05], description="Estimated Lead (Pb) risk index (0-1)")
    mercury_risk_index: Optional[float] = Field(None, examples=[0.02], description="Estimated Mercury (Hg) risk index (0-1)")
    arsenic_risk_index: Optional[float] = Field(None, examples=[0.04], description="Estimated Arsenic (As) risk index (0-1)")
    heavy_metal_risk: Optional[float] = Field(None, examples=[0.05], description="Overall heavy metal contamination risk proxy (0-1)")
    microbial_risk_index: Optional[float] = Field(None, examples=[8.5], description="Estimated microbial risk index (0-100%)")
    microbial_risk: Optional[float] = Field(None, examples=[8.5], description="Alias for microbial risk index")
    ecoli_probability: Optional[float] = Field(None, examples=[0.08], description="Estimated E. coli probability (0-1)")

    # Biological & Taxonomic Inputs
    bio_dominant_taxon: Optional[str] = Field(default="None", examples=["Ceriodaphnia dubia"], description="Dominant bioassay species")
    bio_taxa_richness: Optional[int] = Field(default=0, examples=[2], description="Observed taxonomic richness")
    biological_sampled: Optional[int] = Field(default=0, examples=[1], description="Biological sampling occurrence flag (0 or 1)")


class AnomalyDetectionBlock(BaseModel):
    status: str = Field(..., examples=["Normal"], description="Anomaly detection flag: 'Normal' or 'Anomaly'")
    score: float = Field(..., examples=[-0.1410], description="Continuous anomaly score")


class RiskPredictionBlock(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    model: Optional[str] = Field("Random Forest Risk Classifier", description="Model architecture name")
    risk_class: str = Field(..., alias="class", examples=["SAFE"], description="Predicted risk class: SAFE, WARNING, CRITICAL")
    prediction: Optional[str] = Field(None, examples=["SAFE"], description="Authoritative risk prediction alias")
    risk_tier: Optional[str] = Field(None, examples=["SAFE"], description="Operational risk tier alias")
    confidence: Optional[float] = Field(None, examples=[0.95], description="Prediction confidence (0-1)")
    probability: float = Field(..., examples=[0.95], description="Prediction confidence probability (0-1)")
    probabilities: Optional[Dict[str, float]] = Field(default_factory=dict, description="Class-wise probability distribution")
    decision_boundary: Optional[Dict[str, str]] = Field(default_factory=dict, description="Operational decision boundary descriptions")
    explanation: Optional[List[str]] = Field(default_factory=list, description="Specific Model 2 causal drivers")


class BiologicalSubScoresBlock(BaseModel):
    biodiversity: float = Field(..., examples=[85.0], description="Biodiversity Sub-Score (0-100)")
    pollution_tolerance: float = Field(..., examples=[90.0], description="Pollution Tolerance Sub-Score (0-100)")
    trophic_balance: float = Field(..., examples=[95.0], description="Trophic Balance Sub-Score (0-100)")
    bioassay_stress: float = Field(..., examples=[100.0], description="Bioassay Stress Sub-Score (0-100)")


class BiologicalHealthBlock(BaseModel):
    score: float = Field(..., examples=[92.5], description="Composite Biological Health Score (0-100)")
    classification: str = Field(..., examples=["Excellent (Pristine Ecosystem)"], description="Qualitative ecological status tier")
    sub_scores: BiologicalSubScoresBlock


class EarlyWarningForecastBlock(BaseModel):
    predicted_dissolved_oxygen_24h: float = Field(..., examples=[8.42], description="Projected Dissolved Oxygen next 24 hours (mg/L)")
    predicted_turbidity_24h: float = Field(..., examples=[4.8], description="Projected Turbidity next 24 hours (FNU)")
    future_warning_probability: float = Field(..., examples=[0.082], description="Probability of future water quality warning (0-1)")
    future_projected_status: str = Field(..., examples=["SAFE"], description="Projected operational state in next 24 hours")
    forecast_confidence: Optional[str] = Field(default="High", examples=["High"], description="Uncertainty quantification tier: High, Medium, Low, Suspended (Emergency)")
    forecast_status: Optional[str] = Field(default=None, description="Operational forecast state override if contamination active")
    message: Optional[str] = Field(default=None, description="Operational explanation if forecast suppressed")
    dissolved_oxygen_drift_24h: float = Field(..., examples=[-0.23], description="Expected 24-hour DO change rate (mg/L)")
    turbidity_drift_24h: float = Field(..., examples=[0.3], description="Expected 24-hour turbidity drift (FNU)")
    early_warning_explanation: List[str] = Field(default_factory=list, description="Causal trend diagnostic reasons")
    top_reasons: Optional[List[str]] = Field(default_factory=list, description="Top causal trend drivers")


class RecommendedActionsBlock(BaseModel):
    immediate_actions: List[str] = Field(default_factory=list, description="Urgent responses required within 0-2 hours")
    short_term_actions: List[str] = Field(default_factory=list, description="Investigation & containment within 2-24 hours")
    long_term_prevention: List[str] = Field(default_factory=list, description="Policy & watershed engineering prevention")


class DecisionSupportBlock(BaseModel):
    incident: str = Field(..., examples=["Pristine Baseline / Nominal Water Quality"], description="Identified incident name")
    incident_type: str = Field(..., examples=["NOMINAL_BASELINE"], description="Standard incident enum type code")
    incident_category: str = Field(..., examples=["Nominal"], description="Ecological / chemical incident domain")
    severity: str = Field(..., examples=["LOW"], description="Operational severity tier: LOW, MEDIUM, HIGH, CRITICAL")
    confidence: float = Field(..., examples=[92.0], description="Decision synthesis confidence (0-100%)")
    evidence: List[str] = Field(default_factory=list, description="All empirical and AI signals triggering the conclusion")
    root_causes: List[str] = Field(default_factory=list, description="Diagnosed scientific and environmental root causes")
    reasoning_chain: List[str] = Field(default_factory=list, description="Step-by-step causal logic chain from sensor to decision")
    recommended_actions: RecommendedActionsBlock
    secondary_incidents: List[str] = Field(default_factory=list, description="Secondary co-occurring incident types")


class FinalAssessmentBlock(BaseModel):
    health_index: float = Field(..., examples=[94.2], description="NEON Eco Health Index (0-100)")
    decision: str = Field(..., examples=["SAFE"], description="Authoritative final operational status")
    override_applied: bool = Field(..., examples=[False], description="Whether deterministic environmental guardrails overrode ML Model 2")
    explanation: str = Field(..., examples=["All parameters within safe operating bounds."], description="Primary causal diagnostic summary")
    contributing_parameters: List[str] = Field(default_factory=list, description="Key sensor parameters contributing to risk or override")


class EnvironmentalIndicators(BaseModel):
    wqi: float = Field(..., examples=[95.1], description="Weighted Water Quality Index (0-100)")
    wqi_grade: str = Field(..., examples=["Excellent (Pristine)"], description="Qualitative WQI classification")
    wqi_note: str = Field(default="", description="Anti-eclipsing single parameter violation note")
    oxygen_stress_index: float = Field(..., examples=[0.0], description="Oxygen Stress Index (0.0-1.0)")
    chemical_stress_index: float = Field(..., examples=[0.0], description="Chemical Stress Index (0.0-1.0)")
    organic_pollution_indicator: float = Field(..., examples=[0.08], description="Organic Pollution Indicator (0.0-1.0)")
    eutrophication_risk: float = Field(..., examples=[0.05], description="Eutrophication Risk (0.0-1.0 / 0-100%)")


class FeatureContributionItem(BaseModel):
    feature: str = Field(..., description="Feature identifier")
    label: Optional[str] = Field(None, description="Human readable label")
    value: Optional[str] = Field(None, description="Current value string")
    raw_value: Optional[float] = Field(None, description="Current numeric value")
    shap_value: Optional[float] = Field(None, description="SHAP feature attribution value")
    impact: Any = Field(..., description="SHAP contribution value or formatted string")
    abs_impact: Optional[float] = Field(None, description="Absolute SHAP contribution")
    direction: str = Field(..., description="Direction: risk_increasing / risk_decreasing / neutral")
    value_assessment: Optional[str] = Field(None, description="Ecological baseline assessment")



class XAIExplanationBlock(BaseModel):
    prediction: Optional[str] = Field(None, description="Predicted risk class")
    prediction_reason: str = Field(..., description="Natural language explanation of risk drivers")
    feature_contributions: List[FeatureContributionItem] = Field(default_factory=list, description="Full SHAP feature contributions")
    top_features: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Top impactful features")
    base_rate: Optional[Dict[str, float]] = Field(default_factory=dict, description="Class probabilities")


class PredictionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # Structured Model Blocks
    anomaly_detection: AnomalyDetectionBlock
    risk_prediction: RiskPredictionBlock
    risk_classification: Optional[RiskPredictionBlock] = None
    biological_health: BiologicalHealthBlock
    early_warning_forecast: Optional[EarlyWarningForecastBlock] = None
    decision_support: Optional[DecisionSupportBlock] = None
    xai_explanation: Optional[XAIExplanationBlock] = None
    final_assessment: FinalAssessmentBlock

    # Flat Backwards-Compatible Keys
    ml_prediction: str
    ml_confidence: float
    environmental_risk: str
    final_status: str
    override_reason: str
    contributing_parameters: List[str]
    anomaly_status: str
    anomaly_score: float
    model2_raw_prediction: str
    model2_confidence: float
    environmental_assessment: str
    safety_override_applied: bool
    override_reasons: List[str]
    risk_label: str
    confidence: float
    timestamp: str
    environmental_indicators: EnvironmentalIndicators
    explanation: List[str]


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
    version: str
    architecture: dict


# ── Endpoints ──────────────────────────────────────────────────────

@app.get("/")
def root_endpoint():
    """Root endpoint providing service status and links to documentation."""
    return {
        "service": "AQUA NEON Water Intelligence Platform API",
        "status": "online",
        "health": "/health",
        "docs": "/docs",
        "version": "5.0.0",
    }


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint confirming service status and multi-domain model catalog."""
    return {
        "status": "ok",
        "models_loaded": engine.is_loaded,
        "version": "5.0.0",
        "architecture": {
            "model_1": "IsolationForest (Multivariate Anomaly Detection)",
            "model_2": "RandomForestClassifier (Balanced Operational Risk)",
            "model_3": "BiologicalHealthEngine (Biodiversity & Bioassay Stress)",
            "model_4": "HistGradientBoostingForecaster (24h Predictive Early Warning)",
            "model_5": "DecisionSupportEngine (Neuro-Symbolic Response Recommendation)",
            "environmental_safety_layer": "Neuro-Symbolic Decision Fusion with Anti-Eclipsing Guardrails",
        },
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Execute full multi-domain AI water intelligence, predictive early warning & response recommendation pipeline:
      1. Model 1 calculates continuous anomaly score & status.
      2. Model 2 calculates operational risk classification & confidence probabilities.
      3. Model 3 calculates biological health, bioassay survival, and NEON Eco Health Index.
      4. Model 4 predicts 24h trajectory forecasts (DO, Turbidity, Early Warning Risk).
      5. Model 5 synthesizes AI predictions into prioritized action recommendations.
      6. Neuro-Symbolic Decision Engine enforces deterministic EPA safety guardrails.
    """
    try:
        chl = request.chlorophyll_a_ug_l if request.chlorophyll_a_ug_l is not None else request.chlorophyll
        nitrate = request.nitrate_mg_l if request.nitrate_mg_l is not None else request.nitrate
        phosphate = request.phosphate_mg_l if request.phosphate_mg_l is not None else request.phosphate

        microbial = request.microbial_risk if request.microbial_risk is not None else (
            request.microbial_risk_index if request.microbial_risk_index is not None else request.ecoli_probability
        )

        lead = request.lead_risk_index if request.lead_risk_index is not None else request.heavy_metal_risk
        merc = request.mercury_risk_index if request.mercury_risk_index is not None else request.heavy_metal_risk
        ars = request.arsenic_risk_index if request.arsenic_risk_index is not None else request.heavy_metal_risk

        result = engine.predict(
            ph=request.ph,
            dissolved_oxygen=request.dissolved_oxygen,
            turbidity=request.turbidity,
            specific_conductance=request.specific_conductance,
            fdom=request.fdom,
            temperature=request.temperature,
            site_id=request.site_id,
            sensor_position=request.sensor_position,
            chlorophyll=chl,
            tn_mg_l=nitrate,
            tp_mg_l=phosphate,
            suspended_sediment=request.suspended_sediment,
            lead_risk=lead,
            mercury_risk=merc,
            arsenic_risk=ars,
            microbial_risk=microbial,
            bio_dominant_taxon=request.bio_dominant_taxon or "None",
            bio_taxa_richness=request.bio_taxa_richness or 0,
            biological_sampled=request.biological_sampled or 0,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


# ── IoT Telemetry & MQTT Endpoints ─────────────────────────────────

@app.get("/telemetry/live")
def get_live_telemetry():
    """
    Fetch the latest validated in-situ telemetry stream from Hirakud Node #001,
    connection health metrics, and real-time AI diagnostic synthesis.
    """
    try:
        from iot.mqtt_client import telemetry_manager
        telemetry_manager.set_ai_engine(engine)
        status_data = telemetry_manager.get_connection_status()
        return status_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telemetry retrieval error: {str(e)}")


@app.get("/telemetry/status")
def get_telemetry_status():
    """
    Get live sensor connection health (🟢 Connected, 🟡 SENSOR DELAY, 🔴 SENSOR OFFLINE).
    """
    try:
        from iot.mqtt_client import telemetry_manager
        return telemetry_manager.get_connection_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telemetry status error: {str(e)}")


@app.post("/telemetry/publish")
def publish_telemetry_packet(packet: Dict[str, Any]):
    """
    Ingest a telemetry packet (from virtual sensor simulator, external MQTT bridge, or hardware gateway).
    """
    try:
        from iot.mqtt_client import telemetry_manager
        telemetry_manager.set_ai_engine(engine)
        success, msg = telemetry_manager.ingest_packet(packet)
        if not success:
            raise HTTPException(status_code=400, detail=msg)
        return {"status": "success", "message": msg, "node_id": packet.get("node_id", "UNKNOWN")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telemetry publication error: {str(e)}")


@app.get("/telemetry/history")
def get_telemetry_history(limit: int = 50):
    """
    Fetch recent telemetry packets and AI inference outcomes from persistent SQLite store.
    """
    try:
        from iot.mqtt_client import telemetry_manager
        records = telemetry_manager.get_history(limit=limit)
        return {"total_records": len(records), "history": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telemetry history retrieval error: {str(e)}")


