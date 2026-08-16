"""
Comprehensive Test Suite for FastAPI Backend, Models 1-5, Hybrid Neuro-Symbolic Safety Engine,
and SIH Demo Scenario Validation.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify /health returns 200 and indicates multi-domain models (M1-M5) are loaded."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["models_loaded"] is True
    assert data["version"] in ["3.0.0", "4.0.0", "5.0.0"]
    assert "model_3" in data["architecture"]
    assert "model_4" in data["architecture"]
    assert "model_5" in data["architecture"]


# ── Safety Test A: Normal Pristine Water ───────────────────────────
def test_safety_case_a_normal():
    """Verify standard nominal water quality produces SAFE final status."""
    payload = {
        "ph": 7.42,
        "dissolved_oxygen": 8.65,
        "turbidity": 4.5,
        "specific_conductance": 280.0,
        "temperature": 21.3,
        "nitrate_mg_l": 0.45,
        "phosphate_mg_l": 0.015,
        "chlorophyll_a_ug_l": 2.8,
        "site_id": "WOKWI_SITE",
        "sensor_position": "001",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["final_status"] == "SAFE"
    assert data["ml_prediction"] == "SAFE"
    assert data["environmental_risk"] == "SAFE"
    assert data["safety_override_applied"] is False
    assert "safe" in data["override_reason"].lower()
    assert data["anomaly_detection"]["status"] == "Normal"
    assert data["biological_health"]["score"] >= 80.0


# ── Safety Test B: Severe Acidification (pH = 0.25) ────────────────
def test_safety_case_b_severe_acidification():
    """Verify pH = 0.25 is strictly classified as CRITICAL and overrides any ML SAFE prediction."""
    payload = {
        "ph": 0.25,
        "dissolved_oxygen": 8.0,
        "turbidity": 5.0,
        "specific_conductance": 300.0,
        "site_id": "BIGC",
        "sensor_position": "112",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["final_status"] == "CRITICAL", f"Expected CRITICAL for pH=0.25, got {data['final_status']}"
    assert data["safety_override_applied"] is True
    assert "ph" in data["contributing_parameters"]
    assert any("acid" in exp.lower() for exp in data["explanation"])


# ── Safety Test C: Severe Alkalinity (pH = 13.65) ──────────────────
def test_safety_case_c_severe_alkalinity():
    """Verify pH = 13.65 is strictly classified as CRITICAL and overrides ML prediction."""
    payload = {
        "ph": 13.65,
        "dissolved_oxygen": 8.0,
        "turbidity": 5.0,
        "specific_conductance": 300.0,
        "site_id": "BIGC",
        "sensor_position": "112",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["final_status"] == "CRITICAL", f"Expected CRITICAL for pH=13.65, got {data['final_status']}"
    assert data["safety_override_applied"] is True
    assert "ph" in data["contributing_parameters"]


# ── Safety Test D: Severe Hypoxia / Anoxia (DO = 0.5 mg/L) ─────────
def test_safety_case_d_severe_hypoxia():
    """Verify DO = 0.5 mg/L is strictly classified as CRITICAL."""
    payload = {
        "ph": 7.4,
        "dissolved_oxygen": 0.5,
        "turbidity": 5.0,
        "specific_conductance": 140.0,
        "site_id": "BIGC",
        "sensor_position": "112",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["final_status"] == "CRITICAL", f"Expected CRITICAL for DO=0.5, got {data['final_status']}"
    assert "dissolved_oxygen" in data["contributing_parameters"]
    assert data["environmental_indicators"]["oxygen_stress_index"] == 1.0


# ── Safety Test E: Missing All Sensor Values ───────────────────────
def test_safety_case_e_missing_all():
    """Verify missing all sensor values strictly returns INSUFFICIENT_DATA."""
    payload = {
        "ph": None,
        "dissolved_oxygen": None,
        "turbidity": None,
        "specific_conductance": None,
        "site_id": "ARIK",
        "sensor_position": "102",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["final_status"] == "INSUFFICIENT_DATA"
    assert data["confidence"] == 0.0


# ── Safety Test F: Eutrophication & Hypoxia Synergy ────────────────
def test_safety_case_f_eutrophication_synergy():
    """
    Verify low DO (1.8 mg/L) combined with elevated nutrients (nitrate=12.0) and chlorophyll (35.0)
    triggers CRITICAL with clear causal attribution.
    """
    payload = {
        "ph": 7.8,
        "dissolved_oxygen": 1.8,
        "turbidity": 22.0,
        "specific_conductance": 350.0,
        "nitrate_mg_l": 12.0,
        "phosphate_mg_l": 0.15,
        "chlorophyll_a_ug_l": 35.0,
        "site_id": "BARC",
        "sensor_position": "101",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["final_status"] == "CRITICAL"
    assert "eutrophication" in data["override_reason"].lower() or "nutrients" in data["override_reason"].lower()
    assert "dissolved_oxygen" in data["contributing_parameters"]
    assert "nitrate" in data["contributing_parameters"] or "phosphate" in data["contributing_parameters"]


# ── Safety Test G: Heavy Metal Contamination Override ──────────────
def test_safety_case_g_heavy_metal_override():
    """Verify high heavy metal risk index (e.g. Lead = 0.85) forces CRITICAL status."""
    payload = {
        "ph": 6.8,
        "dissolved_oxygen": 7.5,
        "turbidity": 8.0,
        "specific_conductance": 400.0,
        "lead_risk_index": 0.85,
        "mercury_risk_index": 0.20,
        "arsenic_risk_index": 0.15,
        "site_id": "BIGC",
        "sensor_position": "112",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["final_status"] == "CRITICAL"
    assert "lead_risk_index" in data["contributing_parameters"]
    assert "heavy metal" in data["override_reason"].lower()


# ── Safety Test H: Microbial Risk Override ─────────────────────────
def test_safety_case_h_microbial_risk_override():
    """Verify high microbial contamination risk (> 65%) triggers CRITICAL status."""
    payload = {
        "ph": 7.2,
        "dissolved_oxygen": 7.8,
        "turbidity": 12.0,
        "specific_conductance": 320.0,
        "microbial_risk_index": 82.0,
        "site_id": "BLDE",
        "sensor_position": "101",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["final_status"] == "CRITICAL"
    assert "microbial_risk_index" in data["contributing_parameters"]
    assert "microbial" in data["override_reason"].lower() or "pathogen" in data["override_reason"].lower()


# ── Safety Test I: Model 3 Biological Health & Bioassay Response ──
def test_model3_biological_health_response():
    """Verify Model 3 returns full structured biological block and sub-scores."""
    payload = {
        "ph": 7.35,
        "dissolved_oxygen": 8.40,
        "turbidity": 3.8,
        "specific_conductance": 260.0,
        "temperature": 19.5,
        "nitrate_mg_l": 0.35,
        "phosphate_mg_l": 0.012,
        "suspended_sediment": 25.0,
        "bio_dominant_taxon": "Ceriodaphnia dubia",
        "bio_taxa_richness": 2,
        "biological_sampled": 1,
        "site_id": "WOKWI_SITE",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "biological_health" in data
    bio = data["biological_health"]
    assert bio["score"] >= 85.0
    assert "sub_scores" in bio
    assert "biodiversity" in bio["sub_scores"]
    assert "pollution_tolerance" in bio["sub_scores"]
    assert "trophic_balance" in bio["sub_scores"]
    assert "bioassay_stress" in bio["sub_scores"]

    assert "final_assessment" in data
    assert data["final_assessment"]["health_index"] >= 85.0
    assert data["final_assessment"]["decision"] == "SAFE"


# ── Safety Test J: Model 4 Predictive Early Warning Response ──────
def test_model4_early_warning_response():
    """Verify Model 4 returns 24-hour predictive trajectory and trend diagnostics."""
    payload = {
        "ph": 7.42,
        "dissolved_oxygen": 8.65,
        "turbidity": 4.5,
        "specific_conductance": 280.0,
        "temperature": 21.3,
        "site_id": "WOKWI_SITE",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "early_warning_forecast" in data
    fc = data["early_warning_forecast"]
    assert "predicted_dissolved_oxygen_24h" in fc
    assert "predicted_turbidity_24h" in fc
    assert "future_warning_probability" in fc
    assert "future_projected_status" in fc
    assert "dissolved_oxygen_drift_24h" in fc
    assert "turbidity_drift_24h" in fc
    assert isinstance(fc["early_warning_explanation"], list)
    assert len(fc["early_warning_explanation"]) >= 1


# ── Safety Test K: Model 5 AI Decision Support & Action Plans ─────
def test_model5_decision_support_response():
    """Verify Model 5 returns structured incident classification, severity, and tiered actions."""
    # Test Acid Spill Trigger
    payload = {
        "ph": 2.80,
        "dissolved_oxygen": 8.40,
        "turbidity": 4.5,
        "specific_conductance": 1450.0,
        "temperature": 21.0,
        "site_id": "WOKWI_SITE",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "decision_support" in data
    dec = data["decision_support"]
    assert dec["incident_type"] == "ACIDIFICATION"
    assert dec["severity"] == "CRITICAL"
    assert dec["confidence"] >= 90.0
    assert len(dec["evidence"]) >= 1
    assert len(dec["root_causes"]) >= 1
    assert len(dec["reasoning_chain"]) >= 1

    actions = dec["recommended_actions"]
    assert len(actions["immediate_actions"]) >= 1
    assert len(actions["short_term_actions"]) >= 1
    assert len(actions["long_term_prevention"]) >= 1


# ══════════════════════════════════════════════════════════════════════
# DEMO SCENARIO VALIDATION TESTS
# ══════════════════════════════════════════════════════════════════════

# ── Demo Scenario 1: Normal River Water ────────────────────────────
def test_demo_scenario_1_normal_river():
    """Verify Demo Scenario 1: Pristine baseline produces SAFE with NOMINAL_BASELINE decision."""
    payload = {
        "ph": 7.42, "dissolved_oxygen": 8.65, "turbidity": 4.5,
        "specific_conductance": 280.0, "temperature": 21.3,
        "nitrate_mg_l": 0.45, "phosphate_mg_l": 0.015,
        "chlorophyll_a_ug_l": 2.8, "suspended_sediment": 35.0,
        "lead_risk_index": 0.02, "microbial_risk_index": 5.0,
        "site_id": "WOKWI_SITE", "sensor_position": "001",
        "bio_dominant_taxon": "Ceriodaphnia dubia", "bio_taxa_richness": 3,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["final_status"] == "SAFE"
    dec = data["decision_support"]
    assert dec["incident_type"] == "NOMINAL_BASELINE"
    assert dec["severity"] == "LOW"


# ── Demo Scenario 2: Industrial Acid Spill ─────────────────────────
def test_demo_scenario_2_acid_spill():
    """Verify Demo Scenario 2: Industrial acid spill triggers ACIDIFICATION CRITICAL."""
    payload = {
        "ph": 2.80, "dissolved_oxygen": 4.50, "turbidity": 48.0,
        "specific_conductance": 1450.0, "temperature": 24.0,
        "nitrate_mg_l": 4.50, "phosphate_mg_l": 0.080,
        "chlorophyll_a_ug_l": 1.0, "suspended_sediment": 180.0,
        "lead_risk_index": 0.65, "microbial_risk_index": 75.0,
        "site_id": "BLUE", "sensor_position": "112",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["final_status"] == "CRITICAL"
    dec = data["decision_support"]
    assert dec["incident_type"] == "ACIDIFICATION"
    assert dec["severity"] == "CRITICAL"


# ── Demo Scenario 3: Eutrophication Event ──────────────────────────
def test_demo_scenario_3_eutrophication():
    """Verify Demo Scenario 3: Eutrophic nutrient bloom triggers HYPOXIA/EUTROPHICATION CRITICAL."""
    payload = {
        "ph": 8.65, "dissolved_oxygen": 1.80, "turbidity": 32.0,
        "specific_conductance": 580.0, "temperature": 26.5,
        "nitrate_mg_l": 12.80, "phosphate_mg_l": 0.185,
        "chlorophyll_a_ug_l": 42.0, "suspended_sediment": 65.0,
        "lead_risk_index": 0.20, "microbial_risk_index": 45.0,
        "site_id": "BARC", "sensor_position": "103",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["final_status"] == "CRITICAL"
    dec = data["decision_support"]
    assert dec["severity"] == "CRITICAL"
    # Primary incident should be hypoxia (DO=1.80 < 4.0, priority 90) or eutrophication
    assert dec["incident_type"] in ["HYPOXIA", "EUTROPHICATION", "ECOSYSTEM_COLLAPSE"]


# ── Demo Scenario 4: Sediment Runoff ───────────────────────────────
def test_demo_scenario_4_sediment_runoff():
    """Verify Demo Scenario 4: Severe sediment runoff triggers SEDIMENT_CONTAMINATION."""
    payload = {
        "ph": 6.80, "dissolved_oxygen": 6.20, "turbidity": 185.0,
        "specific_conductance": 420.0, "temperature": 22.5,
        "nitrate_mg_l": 2.80, "phosphate_mg_l": 0.045,
        "chlorophyll_a_ug_l": 8.5, "suspended_sediment": 350.0,
        "lead_risk_index": 0.15, "microbial_risk_index": 28.0,
        "site_id": "ARIK", "sensor_position": "102",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Safety override: turbidity 185 > 100 → CRITICAL
    assert data["final_status"] in ["WARNING", "CRITICAL"]
    dec = data["decision_support"]
    assert dec["incident_type"] == "SEDIMENT_CONTAMINATION"
    assert dec["severity"] in ["MEDIUM", "HIGH"]


# ── Demo Scenario 5: Toxic Contamination ───────────────────────────
def test_demo_scenario_5_toxic_contamination():
    """Verify Demo Scenario 5: Heavy metal toxic contamination triggers TOXIC_CONTAMINATION CRITICAL."""
    payload = {
        "ph": 5.80, "dissolved_oxygen": 6.80, "turbidity": 14.0,
        "specific_conductance": 1120.0, "temperature": 20.0,
        "nitrate_mg_l": 1.20, "phosphate_mg_l": 0.020,
        "chlorophyll_a_ug_l": 3.0, "suspended_sediment": 40.0,
        "lead_risk_index": 0.88, "mercury_risk_index": 0.72,
        "arsenic_risk_index": 0.65, "microbial_risk_index": 12.0,
        "site_id": "BIGC", "sensor_position": "112",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["final_status"] == "CRITICAL"
    dec = data["decision_support"]
    assert dec["incident_type"] == "TOXIC_CONTAMINATION"
    assert dec["severity"] == "CRITICAL"
    assert dec["confidence"] >= 90.0


# ══════════════════════════════════════════════════════════════════════
# MODEL LOADING & INTEGRATION VERIFICATION
# ══════════════════════════════════════════════════════════════════════

def test_model_loading_verification():
    """Verify all model artifacts load correctly and engine is operational."""
    from backend.model_loader import engine
    assert engine.is_loaded is True
    assert engine.anomaly_model is not None
    assert engine.risk_model is not None
    assert engine.eco_engine is not None
    assert engine.forecaster is not None


def test_decision_engine_standalone():
    """Verify Model 5 DecisionSupportEngine can be loaded and evaluated independently."""
    from src.decision.decision_engine import decision_engine
    result = decision_engine.evaluate_incident(ph=7.4, dissolved_oxygen=8.5, turbidity=5.0)
    assert result["incident_type"] == "NOMINAL_BASELINE"
    assert result["severity"] == "LOW"
    assert result["confidence"] >= 50.0
    assert "recommended_actions" in result


def test_all_response_blocks_present():
    """Verify POST /predict returns all structured model blocks including XAI."""
    payload = {"ph": 7.42, "dissolved_oxygen": 8.65, "turbidity": 4.5,
               "specific_conductance": 280.0, "temperature": 21.3}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "anomaly_detection" in data
    assert "risk_prediction" in data
    assert "biological_health" in data
    assert "early_warning_forecast" in data
    assert "decision_support" in data
    assert "xai_explanation" in data
    assert "final_assessment" in data


# ══════════════════════════════════════════════════════════════════════
# EXPLAINABLE AI (SHAP) UNIT TESTS
# ══════════════════════════════════════════════════════════════════════

def test_xai_explanation_safe_condition():
    """Verify SHAP XAI explanation for SAFE water quality conditions."""
    payload = {
        "ph": 7.42,
        "dissolved_oxygen": 8.65,
        "turbidity": 4.5,
        "specific_conductance": 280.0,
        "temperature": 21.3,
        "nitrate_mg_l": 0.45,
        "phosphate_mg_l": 0.015,
        "site_id": "WOKWI_SITE",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "xai_explanation" in data
    xai = data["xai_explanation"]
    assert xai is not None
    assert xai["prediction"] == "SAFE"
    assert len(xai["prediction_reason"]) > 0
    assert len(xai["feature_contributions"]) >= 5
    assert len(xai["top_features"]) >= 1

    # Check structure of top feature item
    top1 = xai["top_features"][0]
    assert "feature" in top1
    assert "value" in top1
    assert "impact" in top1
    assert "direction" in top1


def test_xai_explanation_critical_condition():
    """Verify SHAP XAI explanation for CRITICAL water quality conditions."""
    payload = {
        "ph": 2.80,
        "dissolved_oxygen": 1.80,
        "turbidity": 120.0,
        "specific_conductance": 1450.0,
        "temperature": 24.0,
        "site_id": "BLUE",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "xai_explanation" in data
    xai = data["xai_explanation"]
    assert xai is not None
    assert xai["prediction"] == "CRITICAL"
    assert len(xai["prediction_reason"]) > 0
    assert len(xai["feature_contributions"]) >= 5

    # Verify at least one high-impact feature exists
    impacts = [fc["abs_impact"] for fc in xai["feature_contributions"]]
    assert max(impacts) > 0.01


def test_xai_explainer_standalone():
    """Verify SHAPExplainer module operates standalone without backend dependencies."""
    from src.ml.xai_explainer import shap_explainer
    assert shap_explainer.is_loaded is True

    # Test explain method
    res = shap_explainer.explain(
        ph=7.4, dissolved_oxygen=8.5, turbidity=4.0, specific_conductance=250.0
    )
    assert res["prediction"] == "SAFE"
    assert "prediction_reason" in res
    assert "feature_contributions" in res
    assert "top_features" in res
    assert len(res["top_features"]) <= 5


def test_model4_forecast_safety_layer_emergency_override():
    """
    Verify Model 4 Operational Safety Layer:
    When an acute contamination event occurs (CRITICAL state), normal statistical
    time-series forecasting is suppressed with an EMERGENCY_OVERRIDE state.
    """
    payload = {
        "ph": 13.80,
        "dissolved_oxygen": 1.20,
        "turbidity": 280.0,
        "specific_conductance": 1950.0,
        "temperature": 25.0,
        "site_id": "BIGC",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["final_status"] == "CRITICAL"

    fc = data["early_warning_forecast"]
    assert fc["future_projected_status"] == "EMERGENCY_OVERRIDE"
    assert "Suspended" in fc["forecast_confidence"]
    assert "message" in fc
    assert "suppressed" in fc["message"].lower() or "exceeds" in fc["message"].lower()


# ══════════════════════════════════════════════════════════════════════
# MODEL 5 DECISION RECOMMENDATION REGRESSION SUITE
# ══════════════════════════════════════════════════════════════════════

def test_model5_returns_actions_acid_spill():
    """Verify Model 5 returns immediate, short-term, and long-term actions for acid spill."""
    payload = {
        "ph": 2.80,
        "dissolved_oxygen": 4.50,
        "turbidity": 48.0,
        "specific_conductance": 1450.0,
        "temperature": 24.0,
        "site_id": "BLUE",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    dec = data["decision_support"]
    assert dec["incident_type"] == "ACIDIFICATION"
    assert dec["severity"] == "CRITICAL"

    actions = dec["recommended_actions"]
    assert len(actions["immediate_actions"]) >= 2
    assert any("shutdown" in a.lower() or "intake" in a.lower() for a in actions["immediate_actions"])
    assert len(actions["short_term_actions"]) >= 1
    assert len(actions["long_term_prevention"]) >= 1


def test_model5_returns_actions_toxic_event():
    """Verify Model 5 returns immediate, short-term, and long-term actions for heavy metal toxicity."""
    payload = {
        "ph": 6.20,
        "dissolved_oxygen": 7.0,
        "turbidity": 10.0,
        "specific_conductance": 900.0,
        "lead_risk_index": 0.85,
        "mercury_risk_index": 0.60,
        "site_id": "BIGC",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    dec = data["decision_support"]
    assert dec["incident_type"] == "TOXIC_CONTAMINATION"
    assert dec["severity"] == "CRITICAL"

    actions = dec["recommended_actions"]
    assert len(actions["immediate_actions"]) >= 2
    assert any("shutdown" in a.lower() or "drinking" in a.lower() or "icp-ms" in a.lower() for a in actions["immediate_actions"])
    assert len(actions["short_term_actions"]) >= 1
    assert len(actions["long_term_prevention"]) >= 1


def test_model5_returns_actions_eutrophication():
    """Verify Model 5 returns immediate, short-term, and long-term actions for eutrophication."""
    payload = {
        "ph": 8.65,
        "dissolved_oxygen": 2.50,
        "turbidity": 35.0,
        "specific_conductance": 600.0,
        "nitrate_mg_l": 15.0,
        "phosphate_mg_l": 0.25,
        "chlorophyll_a_ug_l": 45.0,
        "site_id": "BARC",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    dec = data["decision_support"]
    assert dec["severity"] in ["HIGH", "CRITICAL"]

    actions = dec["recommended_actions"]
    assert len(actions["immediate_actions"]) >= 1
    assert len(actions["short_term_actions"]) >= 1
    assert len(actions["long_term_prevention"]) >= 1


def test_model5_returns_actions_normal_case():
    """Verify Model 5 returns nominal guidance for safe pristine river water."""
    payload = {
        "ph": 7.42,
        "dissolved_oxygen": 8.65,
        "turbidity": 4.5,
        "specific_conductance": 280.0,
        "temperature": 21.3,
        "site_id": "WOKWI_SITE",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    dec = data["decision_support"]
    assert dec["incident_type"] == "NOMINAL_BASELINE"
    assert dec["severity"] == "LOW"

    actions = dec["recommended_actions"]
    assert len(actions["immediate_actions"]) >= 1
    assert any("standard" in a.lower() or "routine" in a.lower() for a in actions["immediate_actions"])
    assert len(actions["short_term_actions"]) >= 1
    assert len(actions["long_term_prevention"]) >= 1


def test_dashboard_payload_contains_recommendations():
    """Verify the entire prediction response payload contains complete decision support structures."""
    payload = {
        "ph": 7.42,
        "dissolved_oxygen": 8.65,
        "turbidity": 4.5,
        "specific_conductance": 280.0,
        "temperature": 21.3,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "decision_support" in data
    ds = data["decision_support"]
    assert "incident" in ds
    assert "severity" in ds
    assert "confidence" in ds
    assert "evidence" in ds
    assert "root_causes" in ds
    assert "reasoning_chain" in ds
    assert "recommended_actions" in ds
    assert "immediate_actions" in ds["recommended_actions"]
    assert "short_term_actions" in ds["recommended_actions"]
    assert "long_term_prevention" in ds["recommended_actions"]




