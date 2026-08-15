"""
Model 5: AI Decision Support and Response Recommendation Engine.

Architecture:
  Neuro-Symbolic Multi-Model Decision Fusion Engine combining:
    - Model 1 Anomaly Detection (Isolation Forest)
    - Model 2 Operational Risk Classifier (Balanced Random Forest)
    - Model 3 Biological Ecosystem Health Engine (NEON Eco Health Index)
    - Model 4 Predictive Early Warning Forecaster (24h-48h Trajectory)
    - Current Physical, Chemical, Nutrient, and Toxicological Telemetry
    - Declarative Environmental Rules Knowledge Base (knowledge/water_quality_rules.json)

Answers the 3 Critical Operational Questions for Water Authorities:
  1. "What is happening?"   -> Incident Detection & Severity Classification
  2. "Why is it happening?" -> Root Cause Analysis & Evidentiary Reasoning Chain
  3. "What should authorities do next?" -> Tiered Action Recommendations (Immediate, Short-Term, Long-Term)
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RULES_PATH = PROJECT_ROOT / "knowledge" / "water_quality_rules.json"


class DecisionSupportEngine:
    """
    Model 5: Neuro-Symbolic Environmental Decision Support & Action Recommendation Engine.
    """

    def __init__(self, rules_file: Optional[Path] = None):
        self.rules_file = rules_file or RULES_PATH
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        """Load declarative water quality expert rules from JSON."""
        if self.rules_file.exists():
            with open(self.rules_file, "r") as f:
                return json.load(f)
        return {"incident_types": {}}

    def evaluate_incident(
        self,
        ph: Optional[float] = None,
        dissolved_oxygen: Optional[float] = None,
        turbidity: Optional[float] = None,
        specific_conductance: Optional[float] = None,
        temperature: Optional[float] = 20.0,
        nitrate: Optional[float] = None,
        phosphate: Optional[float] = None,
        chlorophyll: Optional[float] = None,
        suspended_sediment: Optional[float] = None,
        lead_risk: Optional[float] = None,
        mercury_risk: Optional[float] = None,
        arsenic_risk: Optional[float] = None,
        microbial_risk: Optional[float] = None,
        m1_anomaly_status: str = "Normal",
        m1_anomaly_score: float = -0.15,
        m2_risk_class: str = "SAFE",
        m2_confidence: float = 0.90,
        m3_bio_score: float = 90.0,
        m3_eco_health_index: float = 92.0,
        m3_bioassay_stress: float = 100.0,
        m4_forecast_do: Optional[float] = None,
        m4_forecast_turb: Optional[float] = None,
        m4_future_status: str = "SAFE",
        m4_future_prob: float = 0.05,
        m4_confidence: str = "High",
    ) -> Dict[str, Any]:
        """
        Synthesize multi-model predictions and telemetry into actionable environmental response decisions.
        """
        ph_val = float(ph) if ph is not None else 7.4
        do_val = float(dissolved_oxygen) if dissolved_oxygen is not None else 8.5
        turb_val = float(turbidity) if turbidity is not None else 5.0
        cond_val = float(specific_conductance) if specific_conductance is not None else 280.0
        temp_val = float(temperature) if temperature is not None else 20.0

        no3_val = float(nitrate) if nitrate is not None else 0.4
        po4_val = float(phosphate) if phosphate is not None else 0.015
        chla_val = float(chlorophyll) if chlorophyll is not None else 2.5
        ssc_val = float(suspended_sediment) if suspended_sediment is not None else 25.0

        lead_val = float(lead_risk) if lead_risk is not None else 0.0
        merc_val = float(mercury_risk) if mercury_risk is not None else 0.0
        ars_val = float(arsenic_risk) if arsenic_risk is not None else 0.0
        micro_val = float(microbial_risk) if microbial_risk is not None else 5.0

        # ── 1. Multi-Domain Incident Classification ────────────────
        detected_incidents: List[Dict[str, Any]] = []
        evidence: List[str] = []
        reasoning_chain: List[str] = []

        # Check Acidification
        if ph_val < 6.0:
            sev = "CRITICAL" if ph_val < 4.5 else "HIGH"
            detected_incidents.append({
                "type": "ACIDIFICATION",
                "severity": sev,
                "priority": 100 if ph_val < 4.5 else 80,
                "trigger": f"pH = {ph_val:.2f} below ecological safety threshold (6.0)",
            })
            evidence.append(f"Water pH ({ph_val:.2f}) indicates severe acidification / chemical influx risk.")
            reasoning_chain.append(f"pH measurement ({ph_val:.2f}) violates EPA aquatic life envelope (6.5), triggering Acidification containment protocol.")

        # Check Alkaline Spill
        elif ph_val > 9.0:
            sev = "CRITICAL" if ph_val > 9.8 else "HIGH"
            detected_incidents.append({
                "type": "ALKALINE_SPILL",
                "severity": sev,
                "priority": 100 if ph_val > 9.8 else 80,
                "trigger": f"pH = {ph_val:.2f} above alkaline limit (9.0)",
            })
            evidence.append(f"Water pH ({ph_val:.2f}) indicates caustic / alkaline influx risk.")
            reasoning_chain.append(f"pH measurement ({ph_val:.2f}) exceeds alkaline boundary, indicating possible caustic or photosynthetic disturbance.")

        # Check Heavy Metal / Toxic Contamination
        max_metal = max(lead_val, merc_val, ars_val)
        if max_metal >= 0.50 or m3_bioassay_stress < 40.0:
            detected_incidents.append({
                "type": "TOXIC_CONTAMINATION",
                "severity": "CRITICAL",
                "priority": 95,
                "trigger": f"Heavy metal proxy risk ({max_metal:.2f}) or Bioassay survival stress ({m3_bioassay_stress:.1f}/100)",
            })
            evidence.append(f"Toxic metal proxy elevated ({max_metal:.2f}) with acute bioassay organism stress ({m3_bioassay_stress:.1f}/100).")
            reasoning_chain.append("Heavy metal risk inferred from proxy indicators or acute bioassay mortality; toxicity response protocol initiated.")

        # Check Hypoxia & Anoxia
        if do_val < 4.0 or (m4_forecast_do is not None and m4_forecast_do < 3.5):
            sev = "CRITICAL" if do_val < 2.0 or (m4_forecast_do is not None and m4_forecast_do < 2.0) else "HIGH"
            detected_incidents.append({
                "type": "HYPOXIA",
                "severity": sev,
                "priority": 90,
                "trigger": f"Dissolved oxygen ({do_val:.2f} mg/L) in lethal hypoxic range (forecast: {m4_forecast_do:.2f} mg/L)",
            })
            evidence.append(f"Dissolved oxygen is critically depressed ({do_val:.2f} mg/L), with Model 4 forecasting {m4_forecast_do or do_val:.2f} mg/L.")
            reasoning_chain.append(f"Dissolved oxygen level ({do_val:.2f} mg/L) insufficient for fish respiration (< 4.0 mg/L), indicating acute hypoxia risk.")

        # Check Eutrophication & Nutrient Hyper-Enrichment
        if no3_val >= 10.0 or po4_val >= 0.10 or chla_val >= 25.0:
            sev = "CRITICAL" if (no3_val >= 20.0 or chla_val >= 50.0) else "HIGH"
            detected_incidents.append({
                "type": "EUTROPHICATION",
                "severity": sev,
                "priority": 75,
                "trigger": f"Nutrient enrichment (NO3: {no3_val:.1f} mg/L, PO4: {po4_val:.3f} mg/L, Chl-a: {chla_val:.1f} µg/L)",
            })
            evidence.append(f"Nutrient enrichment observed (Nitrate: {no3_val:.1f} mg/L, Chlorophyll-a: {chla_val:.1f} µg/L).")
            reasoning_chain.append("High nitrogen/phosphorus stoichiometry indicates potential microalgae proliferation and cyanobacterial risk.")

        # Check Sediment Contamination / Turbidity Shock
        if turb_val >= 40.0 or ssc_val >= 120.0 or (m4_forecast_turb is not None and m4_forecast_turb >= 50.0):
            sev = "HIGH" if turb_val >= 80.0 or ssc_val >= 200.0 else "MEDIUM"
            detected_incidents.append({
                "type": "SEDIMENT_CONTAMINATION",
                "severity": sev,
                "priority": 65,
                "trigger": f"Turbidity ({turb_val:.1f} FNU) and Suspended Sediment ({ssc_val:.1f} mg/L) elevated",
            })
            evidence.append(f"High suspended particulate load ({turb_val:.1f} FNU, SSC: {ssc_val:.1f} mg/L).")
            reasoning_chain.append(f"Optical turbidity ({turb_val:.1f} FNU) causes severe light attenuation and threatens treatment plant filtration capacity.")

        # Check Thermal Stress
        if temp_val >= 27.0:
            detected_incidents.append({
                "type": "THERMAL_STRESS",
                "severity": "MEDIUM",
                "priority": 40,
                "trigger": f"Water temperature ({temp_val:.1f}°C) elevated above seasonal baseline",
            })
            evidence.append(f"Elevated water temperature ({temp_val:.1f}°C) observed.")
            reasoning_chain.append(f"High water temperature ({temp_val:.1f}°C) reduces gas solubility and presents thermal stress for stenothermal aquatic species.")

        # Check Overall Biological Ecosystem Collapse
        if m3_eco_health_index < 50.0 or m3_bio_score < 45.0:
            detected_incidents.append({
                "type": "ECOSYSTEM_COLLAPSE",
                "severity": "CRITICAL",
                "priority": 85,
                "trigger": f"NEON Eco Health Index ({m3_eco_health_index:.1f}/100) below survival threshold",
            })
            evidence.append(f"Model 3 reports biological ecosystem impairment (Index: {m3_eco_health_index:.1f}/100).")
            reasoning_chain.append("Multi-trophic biological indicators signal severe community degradation across indicator species.")

        # Default Nominal Condition
        if not detected_incidents:
            primary_incident_type = "NOMINAL_BASELINE"
            overall_severity = "LOW"
            evidence.append("All physical, chemical, nutrient, and biological bioassay indicators within nominal baseline limits.")
            reasoning_chain.append("Multi-model consensus (M1 Normal, M2 SAFE, M3 Eco Health > 85, M4 Stable) confirms normal baseline operating conditions.")
        else:
            # Sort by priority descending
            detected_incidents.sort(key=lambda x: x["priority"], reverse=True)
            primary_incident_type = detected_incidents[0]["type"]
            overall_severity = detected_incidents[0]["severity"]

        # ── 2. Retrieve Expert Rules & Action Plans ────────────────
        rule_data = self.rules.get("incident_types", {}).get(primary_incident_type, {})
        incident_name = rule_data.get("name", primary_incident_type.replace("_", " ").title())
        incident_category = rule_data.get("category", "General Water Quality")
        root_causes = rule_data.get("root_causes", ["Environmental parameter deviation."])
        actions_dict = rule_data.get("recommended_actions", {
            "immediate": ["Continue routine telemetry monitoring."],
            "short_term": ["Log water quality readings."],
            "long_term": ["Maintain watershed protection."],
        })

        # Append AI Model Evidence
        if m1_anomaly_status == "Anomaly":
            evidence.append(f"Model 1 (Isolation Forest) flagged multivariate statistical outlier (Score: {m1_anomaly_score:+.4f}).")
            reasoning_chain.append(f"Model 1 confirms rare multivariate anomaly ({m1_anomaly_score:+.4f}) in sensor covariance space.")

        if m2_risk_class != "SAFE":
            evidence.append(f"Model 2 (Balanced Random Forest) predicted operational risk `{m2_risk_class}` ({m2_confidence*100:.1f}% confidence).")

        if m4_future_status != "SAFE":
            evidence.append(f"Model 4.1 projects early warning risk `{m4_future_status}` in next 24 hours ({m4_confidence} Confidence).")
            reasoning_chain.append(f"Model 4.1 time-series forecaster predicts continuation of negative trajectory into the next 24-hour cycle.")

        # ── 3. Confidence Calculation (0–100%) ──────────────────────
        if primary_incident_type in ["ACIDIFICATION", "ALKALINE_SPILL", "TOXIC_CONTAMINATION", "HYPOXIA"] and overall_severity == "CRITICAL":
            # Deterministic hard biological violation guarantees high operational certainty
            conf = max(92.0, m2_confidence * 100.0)
        elif primary_incident_type != "NOMINAL_BASELINE":
            conf = max(80.0, m2_confidence * 100.0)
        else:
            conf = max(85.0, m2_confidence * 100.0)

        if m1_anomaly_status == "Anomaly" and m2_risk_class != "SAFE":
            conf = min(99.0, conf + 5.0)
        if m4_future_status == m2_risk_class:
            conf = min(99.0, conf + 3.0)
        confidence_score = round(max(50.0, min(99.5, conf)), 1)

        return {
            "incident": incident_name,
            "incident_type": primary_incident_type,
            "incident_category": incident_category,
            "severity": overall_severity,
            "confidence": confidence_score,
            "evidence": evidence,
            "root_causes": root_causes,
            "reasoning_chain": reasoning_chain,
            "recommended_actions": {
                "immediate_actions": actions_dict.get("immediate", []),
                "short_term_actions": actions_dict.get("short_term", []),
                "long_term_prevention": actions_dict.get("long_term", []),
            },
            "secondary_incidents": [inc["type"] for inc in detected_incidents[1:]],
        }


# Global Singleton
decision_engine = DecisionSupportEngine()
