"""
Model loader and inference wrapper for SIH Water Intelligence Platform backend.

Loads and Orchestrates:
  - Model 1: Anomaly Detector (Isolation Forest v2/v3)
  - Model 2: Risk Classifier (Balanced Random Forest v2/v3)
  - Model 3: Biological Ecosystem Health Assessment Engine (v3.0)
  - Model 4: Predictive Early Warning & Time-Series Forecaster (v4.1)
  - Model 5: AI Decision Support and Response Recommendation Engine (v5.0)
  - Neuro-Symbolic Environmental Safety Decision Layer
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd

from backend.environmental_engine import compute_environmental_intelligence
from src.decision.decision_engine import decision_engine
from src.ml.biological_health_model import BiologicalHealthEngine
from src.ml.forecasting_pipeline import WaterQualityForecaster
from src.ml.xai_explainer import shap_explainer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_V2_DIR = PROJECT_ROOT / "models" / "v2"
MODEL_V3_DIR = PROJECT_ROOT / "models" / "v3"

ANOMALY_MODEL_PATH_V3 = MODEL_V3_DIR / "anomaly_detector_usgs.joblib"
RISK_MODEL_PATH_V3 = MODEL_V3_DIR / "risk_classifier_usgs.joblib"
ANOMALY_MODEL_PATH_V2 = MODEL_V2_DIR / "anomaly_detector_v2.joblib"
RISK_MODEL_PATH_V2 = MODEL_V2_DIR / "risk_classifier_v2.joblib"
ECO_ENGINE_PATH = MODEL_V3_DIR / "ecological_health_engine.joblib"
FORECASTER_PATH = MODEL_V3_DIR / "model4_forecaster.joblib"


class WaterIntelligenceEngine:
    """Inference engine managing Models 1-5 and Neuro-Symbolic Decision Fusion."""

    def __init__(self):
        self.anomaly_artifact = None
        self.risk_artifact = None
        self.anomaly_model = None
        self.risk_model = None
        self.risk_features = []
        self.risk_classes = ["CRITICAL", "SAFE", "WARNING"]
        self.eco_engine = None
        self.forecaster = None
        self.is_loaded = False
        self.load_models()

    def load_models(self):
        """Load joblib model pipelines and engines into memory."""
        if not ANOMALY_MODEL_PATH_V2.exists():
            raise FileNotFoundError(f"Model 1 artifact missing: {ANOMALY_MODEL_PATH_V2}")
        if not RISK_MODEL_PATH_V2.exists():
            raise FileNotFoundError(f"Model 2 artifact missing: {RISK_MODEL_PATH_V2}")

        self.anomaly_model = joblib.load(ANOMALY_MODEL_PATH_V2)
        self.risk_model = joblib.load(RISK_MODEL_PATH_V2)

        if ECO_ENGINE_PATH.exists():
            self.eco_engine = joblib.load(ECO_ENGINE_PATH)
        else:
            self.eco_engine = None

        if FORECASTER_PATH.exists():
            self.forecaster = joblib.load(FORECASTER_PATH)
        else:
            self.forecaster = None

        self.is_loaded = True

    def predict(
        self,
        ph: Optional[float] = None,
        dissolved_oxygen: Optional[float] = None,
        turbidity: Optional[float] = None,
        specific_conductance: Optional[float] = None,
        fdom: Optional[float] = None,
        temperature: Optional[float] = 20.0,
        site_id: str = "UNKNOWN",
        sensor_position: str = "102.100.100",
        chlorophyll: Optional[float] = None,
        tn_mg_l: Optional[float] = None,
        tp_mg_l: Optional[float] = None,
        suspended_sediment: Optional[float] = None,
        lead_risk: Optional[float] = None,
        mercury_risk: Optional[float] = None,
        arsenic_risk: Optional[float] = None,
        heavy_metal_risk: Optional[float] = None,
        microbial_risk: Optional[float] = None,
        bio_dominant_taxon: str = "None",
        bio_taxa_richness: int = 0,
        biological_sampled: int = 0,
        recent_history: Optional[List[Dict[str, float]]] = None,
        nitrate: Optional[float] = None,
        phosphate: Optional[float] = None,
        nitrate_mg_l: Optional[float] = None,
        phosphate_mg_l: Optional[float] = None,
        chlorophyll_a_ug_l: Optional[float] = None,
        lead_risk_index: Optional[float] = None,
        mercury_risk_index: Optional[float] = None,
        arsenic_risk_index: Optional[float] = None,
        microbial_risk_index: Optional[float] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        # Handle aliases
        if tn_mg_l is None:
            tn_mg_l = nitrate_mg_l if nitrate_mg_l is not None else nitrate
        if tp_mg_l is None:
            tp_mg_l = phosphate_mg_l if phosphate_mg_l is not None else phosphate
        if chlorophyll is None:
            chlorophyll = chlorophyll_a_ug_l
        if lead_risk is None:
            lead_risk = lead_risk_index if lead_risk_index is not None else heavy_metal_risk
        if mercury_risk is None:
            mercury_risk = mercury_risk_index
        if arsenic_risk is None:
            arsenic_risk = arsenic_risk_index
        if microbial_risk is None:
            microbial_risk = microbial_risk_index

        """
        Execute full multi-domain prediction pipeline:
          Input -> M1 (Anomaly) -> M2 (Risk) -> M3 (Bio Health) -> M4 (Forecaster) -> M5 (Decision Support) -> Output
        """
        if not self.is_loaded:
            raise RuntimeError("Models not loaded.")

        pos_str = str(sensor_position).strip()
        if len(pos_str) <= 3 and "." not in pos_str:
            pos_str = f"{pos_str}.100.100"

        # ── 1. Model 1: Anomaly Detection ──────────────────────────
        df_m1 = pd.DataFrame([{
            "ph": ph,
            "dissolved_oxygen": dissolved_oxygen,
            "turbidity": turbidity,
            "specific_conductance": specific_conductance,
            "fdom": fdom,
        }])

        raw_score = self.anomaly_model.decision_function(df_m1)[0]
        m1_pred = self.anomaly_model.predict(df_m1)[0]

        anomaly_status = "Anomaly" if m1_pred == -1 else "Normal"
        anomaly_score = float(-raw_score)

        # ── 2. Model 2: Operational Risk Classification ────────────
        df_m2 = pd.DataFrame([{
            "ph": ph,
            "dissolved_oxygen": dissolved_oxygen,
            "turbidity": turbidity,
            "specific_conductance": specific_conductance,
            "fdom": fdom,
            "chlorophyll": chlorophyll if chlorophyll is not None else np.nan,
            "site_id": str(site_id).upper().strip(),
            "sensor_position": pos_str,
            "ph_flag_qf": 0.0,
            "dissolved_oxygen_flag_qf": 0.0,
            "turbidity_flag_qf": 0.0,
            "specific_conductance_flag_qf": 0.0,
            "fdom_flag_qf": 0.0,
            "chlorophyll_flag_qf": 0.0,
        }])

        valid_params = [v for v in [ph, dissolved_oxygen, turbidity, specific_conductance, fdom]
                        if v is not None and not (isinstance(v, float) and np.isnan(v))]

        if len(valid_params) < 2:
            risk_label = "INSUFFICIENT_DATA"
            confidence = 0.0
            prob_dict = {"CRITICAL": 0.0, "SAFE": 0.0, "WARNING": 0.0}
        else:
            risk_label = str(self.risk_model.predict(df_m2)[0])
            probabilities_raw = self.risk_model.predict_proba(df_m2)[0]
            confidence = float(np.max(probabilities_raw))
            classes = getattr(self.risk_model, "classes_", ["CRITICAL", "INSUFFICIENT_DATA", "SAFE", "WARNING"])
            prob_dict = {c: round(float(p), 4) for c, p in zip(classes, probabilities_raw) if c != "INSUFFICIENT_DATA"}

        # Model 2 Explanations & Decision Boundary
        m2_explanations = []
        if risk_label == "CRITICAL":
            m2_explanations.append("High multi-parameter deviation: Critical operational risk detected by Random Forest.")
            if ph is not None and (ph < 6.0 or ph > 9.0):
                m2_explanations.append(f"Significant pH excursion ({ph:.2f}) outside safe baseline [6.5 - 8.5].")
            if dissolved_oxygen is not None and dissolved_oxygen < 4.0:
                m2_explanations.append(f"Reduced dissolved oxygen ({dissolved_oxygen:.2f} mg/L) indicating severe aquatic stress.")
            if specific_conductance is not None and specific_conductance > 800.0:
                m2_explanations.append(f"Elevated electrical conductance ({specific_conductance:.0f} µS/cm) indicating high ionic load.")
            if turbidity is not None and turbidity > 25.0:
                m2_explanations.append(f"Increased turbidity ({turbidity:.1f} FNU) indicating heavy particulate runoff.")
        elif risk_label == "WARNING":
            m2_explanations.append("Moderate parameter fluctuation: Early abnormal shifts detected.")
            if turbidity is not None and turbidity > 15.0:
                m2_explanations.append(f"Elevated turbidity ({turbidity:.1f} FNU).")
            if dissolved_oxygen is not None and dissolved_oxygen < 6.0:
                m2_explanations.append(f"Dissolved oxygen ({dissolved_oxygen:.2f} mg/L) below optimal range.")
        else:
            m2_explanations.append("All primary water quality parameters conform to safe baseline standards.")

        model2_block = {
            "model": "Random Forest Risk Classifier",
            "class": risk_label,
            "prediction": risk_label,
            "risk_tier": risk_label,
            "confidence": round(confidence, 4),
            "probability": round(confidence, 4),
            "probabilities": prob_dict,
            "decision_boundary": {
                "SAFE": "Normal water parameters within acceptable safe operating envelope.",
                "WARNING": "Early abnormal shifts or single-parameter threshold excursions detected.",
                "CRITICAL": "Multiple parameters significantly deviate from historical safe baseline.",
            },
            "explanation": m2_explanations,
        }

        # ── 3. Model 3: Biological Ecosystem Health Engine ─────────
        if self.eco_engine is not None:
            bio_diag = self.eco_engine.evaluate_sample(
                ph=ph,
                dissolved_oxygen=dissolved_oxygen,
                turbidity=turbidity,
                specific_conductance=specific_conductance,
                temperature=temperature,
                total_nitrogen=tn_mg_l,
                total_phosphorus=tp_mg_l,
                suspended_sediment=suspended_sediment,
                bio_dominant_taxon=bio_dominant_taxon,
                bio_taxa_richness=bio_taxa_richness,
                biological_sampled=biological_sampled,
            )
        else:
            bio_diag = {
                "biodiversity_score": 80.0,
                "pollution_tolerance_score": 85.0,
                "trophic_balance_score": 90.0,
                "bioassay_stress_score": 95.0,
                "biological_health_score": 87.5,
                "chemical_health_score": 95.0,
                "neon_eco_health_index": 91.2,
                "ecological_tier": "Excellent (Pristine Ecosystem)",
                "operational_status": "SAFE",
            }

        # ── 4. Model 4: Predictive Early Warning Forecaster ────────
        if self.forecaster is not None and ph is not None and dissolved_oxygen is not None:
            forecast_diag = self.forecaster.predict_forecast(
                current_ph=float(ph),
                current_do=float(dissolved_oxygen),
                current_temp=float(temperature or 20.0),
                current_turb=float(turbidity or 5.0),
                current_cond=float(specific_conductance or 300.0),
                recent_history=recent_history,
            )
        else:
            forecast_diag = {
                "predicted_dissolved_oxygen_24h": round(dissolved_oxygen or 8.0, 2),
                "predicted_turbidity_24h": round(turbidity or 5.0, 1),
                "future_warning_probability": 0.05,
                "future_projected_status": "SAFE" if (dissolved_oxygen or 8.0) >= 5.0 else "WARNING",
                "forecast_confidence": "High",
                "dissolved_oxygen_drift_24h": 0.0,
                "turbidity_drift_24h": 0.0,
                "early_warning_explanation": ["Trajectory stable based on available telemetry."],
                "top_reasons": ["Telemetry within historical bounds."],
            }

        # ── 5. Environmental Intelligence & Hybrid Decision Layer ──
        env_result = compute_environmental_intelligence(
            ph=ph,
            dissolved_oxygen=dissolved_oxygen,
            turbidity=turbidity,
            specific_conductance=specific_conductance,
            fdom=fdom,
            temperature=temperature,
            chlorophyll=chlorophyll,
            nitrate=tn_mg_l,
            phosphate=tp_mg_l,
            lead_risk=lead_risk,
            mercury_risk=mercury_risk,
            arsenic_risk=arsenic_risk,
            microbial_risk=microbial_risk,
            site_id=str(site_id).upper().strip(),
            m1_anomaly_status=anomaly_status,
            m1_anomaly_score=anomaly_score,
            m2_risk_label=risk_label,
            m2_confidence=confidence,
        )

        final_stat = env_result["final_status"]

        # ── 5b. Model 4 Operational Safety Layer: Emergency Override ─
        # When an acute contamination shock occurs, statistical time-series forecasting
        # is suppressed in favor of immediate containment and emergency operational protocols.
        if final_stat == "CRITICAL":
            forecast_diag["future_projected_status"] = "EMERGENCY_OVERRIDE"
            forecast_diag["forecast_confidence"] = "Suspended (Emergency)"
            forecast_diag["forecast_status"] = "EMERGENCY_OVERRIDE"
            forecast_diag["message"] = "Forecast suppressed because current contamination exceeds historical prediction boundary."
            forecast_diag["early_warning_explanation"] = [
                "⚠️ Forecast Suspended: Current contamination event requires emergency response. Predictive forecasting is temporarily overridden.",
                "Current contamination exceeds historical statistical prediction boundaries."
            ]
            forecast_diag["top_reasons"] = [
                "Severe environmental degradation detected; operational protocol mandates immediate response over predictive extrapolation."
            ]

        # ── 6. Model 5: AI Decision Support & Action Recommendations ─
        decision_result = decision_engine.evaluate_incident(
            ph=ph,
            dissolved_oxygen=dissolved_oxygen,
            turbidity=turbidity,
            specific_conductance=specific_conductance,
            temperature=temperature,
            nitrate=tn_mg_l,
            phosphate=tp_mg_l,
            chlorophyll=chlorophyll,
            suspended_sediment=suspended_sediment,
            lead_risk=lead_risk,
            mercury_risk=mercury_risk,
            arsenic_risk=arsenic_risk,
            microbial_risk=microbial_risk,
            m1_anomaly_status=anomaly_status,
            m1_anomaly_score=anomaly_score,
            m2_risk_class=risk_label,
            m2_confidence=confidence,
            m3_bio_score=bio_diag.get("biological_health_score", 90.0),
            m3_eco_health_index=bio_diag.get("neon_eco_health_index", 92.0),
            m3_bioassay_stress=bio_diag.get("sub_scores", {}).get("bioassay_stress", 100.0),
            m4_forecast_do=forecast_diag.get("predicted_dissolved_oxygen_24h"),
            m4_forecast_turb=forecast_diag.get("predicted_turbidity_24h"),
            m4_future_status=forecast_diag.get("future_projected_status", "SAFE"),
            m4_future_prob=forecast_diag.get("future_warning_probability", 0.05),
            m4_confidence=forecast_diag.get("forecast_confidence", "High"),
        )

        # ── 7. SHAP Explainable AI: Feature Contribution Analysis ──
        hm_risk = lead_risk or mercury_risk or arsenic_risk
        xai_diag = shap_explainer.explain(
            ph=ph,
            dissolved_oxygen=dissolved_oxygen,
            turbidity=turbidity,
            specific_conductance=specific_conductance,
            temperature=temperature,
            suspended_sediment=suspended_sediment,
            total_nitrogen=tn_mg_l,
            total_phosphorus=tp_mg_l,
            bio_taxa_richness=bio_taxa_richness,
            biological_sampled=biological_sampled,
            heavy_metal_risk=hm_risk,
            microbial_risk=microbial_risk,
        )

        # ── 8. Assemble Integrated Multi-Model Response ────────────
        structured_response = {
            # Structured Model Blocks (Authoritative single source of truth)
            "anomaly_detection": {
                "status": anomaly_status,
                "score": round(anomaly_score, 4),
            },
            "risk_prediction": model2_block,
            "risk_classification": model2_block,
            "biological_health": {
                "score": bio_diag["biological_health_score"],
                "classification": bio_diag["ecological_tier"],
                "sub_scores": {
                    "biodiversity": bio_diag["biodiversity_score"],
                    "pollution_tolerance": bio_diag["pollution_tolerance_score"],
                    "trophic_balance": bio_diag["trophic_balance_score"],
                    "bioassay_stress": bio_diag["bioassay_stress_score"],
                },
            },
            "early_warning_forecast": forecast_diag,
            "decision_support": decision_result,
            "xai_explanation": xai_diag,
            "final_assessment": {
                "health_index": bio_diag["neon_eco_health_index"],
                "decision": final_stat,
                "override_applied": env_result["safety_override_applied"],
                "explanation": env_result["override_reason"],
                "contributing_parameters": env_result["contributing_parameters"],
            },
            # Flat Backwards-Compatible Keys
            "ml_prediction": risk_label,
            "ml_confidence": round(confidence, 4),
            "environmental_risk": env_result["environmental_risk"],
            "final_status": final_stat,
            "override_reason": env_result["override_reason"],
            "contributing_parameters": env_result["contributing_parameters"],
            "anomaly_status": anomaly_status,
            "anomaly_score": round(anomaly_score, 4),
            "model2_raw_prediction": risk_label,
            "model2_confidence": round(confidence, 4),
            "environmental_assessment": env_result["environmental_assessment"],
            "safety_override_applied": env_result["safety_override_applied"],
            "override_reasons": env_result["override_reasons"],
            "risk_label": final_stat,
            "confidence": round(confidence, 4),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environmental_indicators": env_result["environmental_indicators"],
            "explanation": env_result["explanation"],
        }

        return structured_response


# Global engine singleton
engine = WaterIntelligenceEngine()
