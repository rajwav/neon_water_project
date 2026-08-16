"""
Script to audit, verify, and trace live data flow across all 5 models.
Tests:
  - CASE A: Normal water
  - CASE B: Sudden chemical discharge (pH=2.5, cond=1800, turb=200, lead_risk_index=0.9)
  - CASE C: Eutrophication (nitrate=20, phosphate=1, chlorophyll=100, DO=2)
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.model_loader import engine

def audit_case(case_name: str, payload: dict):
    print(f"\n=======================================================")
    print(f"AUDITING: {case_name}")
    print(f"INPUT PAYLOAD: {json.dumps(payload, indent=2)}")
    print(f"=======================================================")

    res = engine.predict(**payload)

    # 1. Model 1: Anomaly Detection
    m1 = res.get("anomaly_detection", {})
    print(f"\n--- MODEL 1: ISOLATION FOREST ANOMALY DETECTOR ---")
    print(f"  Status: {m1.get('status')}")
    print(f"  Anomaly Score: {m1.get('score')}")

    # 2. Model 2: Contamination Risk Classification
    m2 = res.get("risk_prediction", {})
    print(f"\n--- MODEL 2: BALANCED RANDOM FOREST RISK CLASSIFIER ---")
    print(f"  Risk Class: {m2.get('class')}")
    print(f"  Confidence Probability: {m2.get('probability')}")

    # XAI
    xai = res.get("xai_explanation", {})
    print(f"\n--- XAI: TREESHAP EXPLAINABILITY ---")
    print(f"  Prediction: {xai.get('prediction')}")
    print(f"  Reason: {xai.get('prediction_reason')}")
    print(f"  Top Feature Contributions:")
    for feat in xai.get("feature_contributions", [])[:4]:
        print(f"    - {feat.get('feature')}: val={feat.get('value')}, impact={feat.get('impact')}, direction={feat.get('direction')}")

    # 3. Model 3: Biological Ecosystem Health
    m3 = res.get("biological_health", {})
    print(f"\n--- MODEL 3: BIOLOGICAL ECOSYSTEM HEALTH ENGINE ---")
    print(f"  Eco Health Score: {m3.get('score')}")
    print(f"  Classification: {m3.get('classification')}")
    print(f"  Sub-Scores: {m3.get('sub_scores')}")

    # 4. Model 4: Early Warning Forecaster
    m4 = res.get("early_warning_forecast", {})
    print(f"\n--- MODEL 4: 24-HOUR EARLY WARNING FORECASTER ---")
    print(f"  Projected 24h DO: {m4.get('predicted_dissolved_oxygen_24h')}")
    print(f"  Projected 24h Turbidity: {m4.get('predicted_turbidity_24h')}")
    print(f"  Future Projected Status: {m4.get('future_projected_status')}")
    print(f"  Forecast Confidence: {m4.get('forecast_confidence')}")
    print(f"  Explanations: {m4.get('early_warning_explanation')}")

    # 5. Model 5: Neuro-Symbolic Decision Support
    m5 = res.get("decision_support", {})
    print(f"\n--- MODEL 5: NEURO-SYMBOLIC DECISION SUPPORT APEX LAYER ---")
    print(f"  Incident: {m5.get('incident')}")
    print(f"  Severity: {m5.get('severity')}")
    print(f"  Confidence: {m5.get('confidence')}%")
    print(f"  Evidence Chain: {m5.get('evidence')}")
    print(f"  Root Causes: {m5.get('root_causes')}")
    actions = m5.get("recommended_actions", {})
    print(f"  Immediate Actions (0-2h): {actions.get('immediate_actions')}")
    print(f"  Short-Term Actions (2-24h): {actions.get('short_term_actions')}")
    print(f"  Long-Term Prevention: {actions.get('long_term_prevention')}")

    return res

if __name__ == "__main__":
    # Case A: Normal water
    case_a = {
        "ph": 7.42,
        "dissolved_oxygen": 8.65,
        "turbidity": 4.5,
        "specific_conductance": 280.0,
        "temperature": 21.3,
        "site_id": "HIRAKUD_NODE",
    }
    audit_case("CASE A: Normal Water", case_a)

    # Case B: Sudden chemical discharge
    case_b = {
        "ph": 2.5,
        "dissolved_oxygen": 7.2,
        "turbidity": 200.0,
        "specific_conductance": 1800.0,
        "temperature": 23.0,
        "lead_risk": 0.9,
        "site_id": "HIRAKUD_NODE",
    }
    audit_case("CASE B: Sudden Chemical Discharge (pH 2.5, Lead 0.9, Cond 1800, Turb 200)", case_b)

    # Case C: Eutrophication
    case_c = {
        "ph": 8.8,
        "dissolved_oxygen": 2.0,
        "turbidity": 45.0,
        "specific_conductance": 650.0,
        "temperature": 28.0,
        "tn_mg_l": 20.0,
        "tp_mg_l": 1.0,
        "chlorophyll": 100.0,
        "site_id": "HIRAKUD_NODE",
    }
    audit_case("CASE C: Eutrophication (Nitrate 20, Phosphate 1, Chl-a 100, DO 2.0)", case_c)
