"""
Environmental Intelligence & Deterministic Safety Decision Layer (v2.1).

Scientific modules:
  1. Water Quality Index (WQI) — Weighted Arithmetic with Anti-Eclipsing Single-Parameter Guardrails
  2. Oxygen Stress Index (OSI) — Weiss DO Saturation & Hypoxia Deficit
  3. Chemical Stress Index (CSI) — pH & Conductance Deviation
  4. Organic Pollution Indicator (OPI) — fDOM & DOC Carbon Proxy
  5. Eutrophication Risk Indicator (ERI) — Multi-factor Nutrient & Trophic Model
  6. Final Environmental Safety Decision Engine — Deterministic Hard Constraint Overrides
  7. Explainable AI (XAI) — Root-Cause Parameter Attribution & Safety Override Explanations

Authoritative References & Thresholds:
  - EPA National Recommended Water Quality Criteria (Aquatic Life Freshwater Guidelines):
      * pH: 6.5 - 9.0 (Criteria envelope); pH < 4.0 or > 10.0 (Acute toxicity / lethal threshold)
      * Dissolved Oxygen: >= 5.0 mg/L (Continuous warmwater criteria); < 2.0 mg/L (Acute lethal hypoxia/anoxia)
      * Specific Conductance: Benchmark 500-800 µS/cm; > 1500 µS/cm (Extreme ionic contamination)
      * Turbidity: Permissible < 10 FNU; > 100 FNU (Severe ecological impairment / sediment loading)
  - WHO Guidelines for Drinking-water Quality (4th Edition):
      * pH: 6.5 - 8.5 (Target envelope)
  - Ott (1978), Swamee & Tyagi (2000), Abbasi (2002):
      * Anti-Eclipsing single-parameter override methodology in environmental index design
  - NEON DP1.20093.001 (Chemical Properties of Surface Water)
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np

# Authoritative Threshold Standards
THRESHOLDS = {
    "ph_critical_acid": 4.0,       # EPA Acute Lethal Acidification
    "ph_warning_acid": 6.0,        # EPA Sub-optimal Acidification
    "ph_warning_alkaline": 9.0,    # EPA Sub-optimal Alkalinity
    "ph_critical_alkaline": 10.0,  # EPA Acute Lethal Alkalinity
    "do_critical_hypoxia": 2.0,    # EPA/USGS Lethal Anoxia (mg/L)
    "do_warning_hypoxia": 4.0,     # EPA Aquatic Stress Hypoxia (mg/L)
    "turbidity_warning": 25.0,     # Elevated particulate runoff (FNU)
    "turbidity_critical": 100.0,   # Severe ecological impairment (FNU)
    "spcond_warning": 800.0,       # Significant ionic load (µS/cm)
    "spcond_critical": 1500.0,     # Extreme salinization / industrial effluent (µS/cm)
    "fdom_warning": 75.0,          # Elevated dissolved organic carbon (QSU)
    "fdom_critical": 150.0,        # Heavy organic sewage / leachate contamination (QSU)
}

# Site baseline medians derived from NEON DP1.20093.001 (Chemical Properties)
SITE_LAB_BASELINES = {
    "ARIK": {"median_tn": 0.425, "median_tp": 0.0317, "median_doc": 5.66, "median_tds": 330.5},
    "BARC": {"median_tn": 0.310, "median_tp": 0.0073, "median_doc": 2.84, "median_tds": 16.0},
    "BIGC": {"median_tn": 0.090, "median_tp": 0.0154, "median_doc": 2.00, "median_tds": 82.5},
    "BLDE": {"median_tn": 0.250, "median_tp": 0.0539, "median_doc": 3.21, "median_tds": 85.0},
    "BLUE": {"median_tn": 0.545, "median_tp": 0.0208, "median_doc": 0.91, "median_tds": 312.0},
}


def calculate_do_saturation(temp_c: float = 20.0) -> float:
    """
    Calculate theoretical dissolved oxygen saturation (mg/L) at 1 atm.
    Uses Weiss (1970) polynomial formulation.
    """
    t = float(np.clip(temp_c, 0.0, 40.0))
    do_sat = 14.652 - 0.41022 * t + 0.007991 * (t ** 2) - 0.000077774 * (t ** 3)
    return max(6.0, float(do_sat))


def calculate_wqi(
    ph: Optional[float],
    dissolved_oxygen: Optional[float],
    turbidity: Optional[float],
    specific_conductance: Optional[float],
    fdom: Optional[float],
    site_id: str = "UNKNOWN",
) -> Dict[str, Any]:
    """
    Calculate Weighted Arithmetic Water Quality Index (WQI) with Anti-Eclipsing protection.
    Scale: 0 - 100 (100 = Pristine / Excellent, 0 = Extremely Degraded).
    
    Prevents single-parameter eclipsing (e.g. pH=0.25 resulting in high average WQI).
    """
    sub_indices = {}
    weights = {}
    critical_violations = []

    # 1. pH (Ideal = 7.0, Standard envelope = 6.5 - 8.5)
    if ph is not None and not np.isnan(ph):
        deviation = abs(ph - 7.0)
        q_ph = max(0.0, 100.0 - (deviation / 1.5) * 50.0)
        sub_indices["ph"] = float(np.clip(q_ph, 0.0, 100.0))
        weights["ph"] = 0.20
        if ph < THRESHOLDS["ph_critical_acid"]:
            critical_violations.append(f"Severe Acidification (pH = {ph:.2f} < {THRESHOLDS['ph_critical_acid']})")
        elif ph > THRESHOLDS["ph_critical_alkaline"]:
            critical_violations.append(f"Severe Alkalinity (pH = {ph:.2f} > {THRESHOLDS['ph_critical_alkaline']})")

    # 2. Dissolved Oxygen (Ideal >= 8.0 mg/L, Poor < 4.0 mg/L)
    if dissolved_oxygen is not None and not np.isnan(dissolved_oxygen):
        if dissolved_oxygen >= 8.0:
            q_do = 100.0
        elif dissolved_oxygen >= 5.0:
            q_do = 70.0 + ((dissolved_oxygen - 5.0) / 3.0) * 30.0
        elif dissolved_oxygen >= 2.0:
            q_do = 30.0 + ((dissolved_oxygen - 2.0) / 3.0) * 40.0
        else:
            q_do = max(0.0, (dissolved_oxygen / 2.0) * 30.0)
        sub_indices["dissolved_oxygen"] = float(np.clip(q_do, 0.0, 100.0))
        weights["dissolved_oxygen"] = 0.30
        if dissolved_oxygen < THRESHOLDS["do_critical_hypoxia"]:
            critical_violations.append(f"Lethal Hypoxia/Anoxia (DO = {dissolved_oxygen:.2f} mg/L < {THRESHOLDS['do_critical_hypoxia']} mg/L)")

    # 3. Turbidity (Ideal <= 2.0 FNU, Standard limit = 10.0 FNU, Severe > 50 FNU)
    if turbidity is not None and not np.isnan(turbidity):
        if turbidity <= 2.0:
            q_turb = 100.0
        elif turbidity <= 10.0:
            q_turb = 100.0 - ((turbidity - 2.0) / 8.0) * 30.0
        elif turbidity <= 50.0:
            q_turb = 70.0 - ((turbidity - 10.0) / 40.0) * 40.0
        else:
            q_turb = max(0.0, 30.0 - ((turbidity - 50.0) / 100.0) * 30.0)
        sub_indices["turbidity"] = float(np.clip(q_turb, 0.0, 100.0))
        weights["turbidity"] = 0.20
        if turbidity > THRESHOLDS["turbidity_critical"]:
            critical_violations.append(f"Severe Turbidity Spike ({turbidity:.1f} FNU > {THRESHOLDS['turbidity_critical']} FNU)")

    # 4. Specific Conductance (Ideal <= 250 µS/cm, Standard limit = 750 µS/cm)
    if specific_conductance is not None and not np.isnan(specific_conductance):
        if specific_conductance <= 250.0:
            q_cond = 100.0
        elif specific_conductance <= 750.0:
            q_cond = 100.0 - ((specific_conductance - 250.0) / 500.0) * 40.0
        else:
            q_cond = max(0.0, 60.0 - ((specific_conductance - 750.0) / 750.0) * 60.0)
        sub_indices["specific_conductance"] = float(np.clip(q_cond, 0.0, 100.0))
        weights["specific_conductance"] = 0.15
        if specific_conductance > THRESHOLDS["spcond_critical"]:
            critical_violations.append(f"Severe Salinization / Ionic Shock ({specific_conductance:.1f} µS/cm > {THRESHOLDS['spcond_critical']} µS/cm)")

    # 5. fDOM (Ideal <= 25 QSU, Elevated > 70 QSU)
    if fdom is not None and not np.isnan(fdom):
        if fdom <= 25.0:
            q_fdom = 100.0
        elif fdom <= 75.0:
            q_fdom = 100.0 - ((fdom - 25.0) / 50.0) * 40.0
        else:
            q_fdom = max(0.0, 60.0 - ((fdom - 75.0) / 100.0) * 60.0)
        sub_indices["fdom"] = float(np.clip(q_fdom, 0.0, 100.0))
        weights["fdom"] = 0.15

    if not weights:
        return {"wqi_score": 0.0, "wqi_grade": "INSUFFICIENT_DATA", "wqi_note": "No telemetry channels available", "sub_indices": {}}

    total_weight = sum(weights.values())
    raw_wqi = sum(sub_indices[k] * (weights[k] / total_weight) for k in sub_indices)
    raw_wqi = round(float(raw_wqi), 1)

    # Apply Anti-Eclipsing single-parameter penalty
    if critical_violations:
        wqi_grade = "CRITICAL VIOLATION (Safety Override)"
        wqi_note = f"Index score: {raw_wqi:.1f}/100 — but critical parameter violation detected ({'; '.join(critical_violations)})"
    elif raw_wqi >= 90.0:
        wqi_grade = "Excellent (Pristine)"
        wqi_note = f"Index score: {raw_wqi:.1f}/100 — pristine baseline water quality"
    elif raw_wqi >= 70.0:
        wqi_grade = "Good (Suitable for Habitat)"
        wqi_note = f"Index score: {raw_wqi:.1f}/100 — acceptable for aquatic ecosystem"
    elif raw_wqi >= 50.0:
        wqi_grade = "Fair (Moderate Impact)"
        wqi_note = f"Index score: {raw_wqi:.1f}/100 — moderate stress detected"
    elif raw_wqi >= 25.0:
        wqi_grade = "Poor (Significant Stress)"
        wqi_note = f"Index score: {raw_wqi:.1f}/100 — significant parameter degradation"
    else:
        wqi_grade = "Very Poor (Critical Degradation)"
        wqi_note = f"Index score: {raw_wqi:.1f}/100 — severe multi-parameter failure"

    return {
        "wqi_score": raw_wqi,
        "wqi_grade": wqi_grade,
        "wqi_note": wqi_note,
        "sub_indices": sub_indices,
        "critical_violations": critical_violations,
    }


def calculate_oxygen_stress(dissolved_oxygen: Optional[float], temperature: Optional[float] = 20.0) -> float:
    """
    Oxygen Stress Index (OSI): 0.0 (Optimal) to 1.0 (Severe Anoxia / Hypoxia).
    """
    if dissolved_oxygen is None or np.isnan(dissolved_oxygen):
        return 0.0

    t = temperature if temperature is not None and not np.isnan(temperature) else 20.0
    do_sat = calculate_do_saturation(t)

    if dissolved_oxygen <= THRESHOLDS["do_critical_hypoxia"]:
        return 1.00  # Lethal anoxia
    elif dissolved_oxygen <= THRESHOLDS["do_warning_hypoxia"]:
        return round(0.70 + 0.30 * ((THRESHOLDS["do_warning_hypoxia"] - dissolved_oxygen) / 2.0), 3)
    elif dissolved_oxygen <= 6.0:
        return round(0.30 + 0.40 * ((6.0 - dissolved_oxygen) / 2.0), 3)
    elif dissolved_oxygen < do_sat:
        deficit = (do_sat - dissolved_oxygen) / do_sat
        return round(float(np.clip(deficit * 0.30, 0.0, 0.30)), 3)
    else:
        return 0.00


def calculate_chemical_stress(ph: Optional[float], specific_conductance: Optional[float], site_id: str = "UNKNOWN") -> float:
    """
    Chemical Stress Index (CSI): 0.0 (Balanced) to 1.0 (Severe Chemical Shock).
    """
    stresses = []

    # pH stress component
    if ph is not None and not np.isnan(ph):
        if ph < THRESHOLDS["ph_critical_acid"] or ph > THRESHOLDS["ph_critical_alkaline"]:
            stresses.append(1.00)
        elif ph < THRESHOLDS["ph_warning_acid"]:
            # Note: BARC is naturally acidic blackwater lake (pH 5.0-6.0)
            if site_id == "BARC" and ph >= 4.8:
                stresses.append(0.10)
            else:
                stresses.append(round((THRESHOLDS["ph_warning_acid"] - ph) / (THRESHOLDS["ph_warning_acid"] - THRESHOLDS["ph_critical_acid"]), 3))
        elif ph > THRESHOLDS["ph_warning_alkaline"]:
            stresses.append(round((ph - THRESHOLDS["ph_warning_alkaline"]) / (THRESHOLDS["ph_critical_alkaline"] - THRESHOLDS["ph_warning_alkaline"]), 3))
        else:
            stresses.append(0.0)

    # Conductance stress component
    if specific_conductance is not None and not np.isnan(specific_conductance):
        norm_limit = 500.0 if site_id != "ARIK" else 850.0
        if specific_conductance <= norm_limit:
            stresses.append(0.0)
        elif specific_conductance >= THRESHOLDS["spcond_critical"]:
            stresses.append(1.00)
        else:
            stresses.append(round((specific_conductance - norm_limit) / (THRESHOLDS["spcond_critical"] - norm_limit), 3))

    return round(float(np.max(stresses)), 3) if stresses else 0.0


def calculate_organic_pollution(fdom: Optional[float], chlorophyll: Optional[float] = None) -> float:
    """
    Organic Pollution Indicator (OPI): 0.0 (Low Carbon) to 1.0 (High Organic Inflow).
    """
    if fdom is None or np.isnan(fdom):
        return 0.0

    if fdom <= 20.0:
        base_opi = 0.05
    elif fdom <= 60.0:
        base_opi = 0.05 + ((fdom - 20.0) / 40.0) * 0.45
    elif fdom <= THRESHOLDS["fdom_critical"]:
        base_opi = 0.50 + ((fdom - 60.0) / 90.0) * 0.40
    else:
        base_opi = min(1.0, 0.90 + ((fdom - THRESHOLDS["fdom_critical"]) / 100.0) * 0.10)

    if chlorophyll is not None and not np.isnan(chlorophyll):
        chl_factor = min(0.20, (chlorophyll / 20.0) * 0.20)
        base_opi = min(1.0, base_opi + chl_factor)

    return round(float(base_opi), 3)


def calculate_eutrophication_risk(
    osi: float,
    opi: float,
    turbidity: Optional[float],
    specific_conductance: Optional[float],
    chlorophyll: Optional[float] = None,
    tn_mg_l: Optional[float] = None,
    tp_mg_l: Optional[float] = None,
) -> float:
    """
    Eutrophication Risk Indicator (ERI) (0.0 to 1.0 / 0 - 100%):
      ERI = 40% Nutrient Load + 30% Chlorophyll Response + 20% Oxygen Stress + 10% Organic Matter
    """
    if tn_mg_l is not None and tp_mg_l is not None:
        nut_score = min(1.0, 0.5 * (tn_mg_l / 1.5) + 0.5 * (tp_mg_l / 0.05))
    else:
        turb_proxy = min(1.0, (turbidity / 50.0)) if turbidity is not None and not np.isnan(turbidity) else 0.0
        cond_proxy = min(1.0, (specific_conductance / 800.0)) if specific_conductance is not None and not np.isnan(specific_conductance) else 0.0
        nut_score = min(1.0, 0.6 * opi + 0.2 * turb_proxy + 0.2 * cond_proxy)

    if chlorophyll is not None and not np.isnan(chlorophyll):
        chl_score = min(1.0, chlorophyll / 15.0)
    else:
        chl_score = min(1.0, 0.7 * opi + 0.3 * (min(1.0, turbidity / 30.0) if turbidity is not None else 0.0))

    eri = 0.40 * nut_score + 0.30 * chl_score + 0.20 * osi + 0.10 * opi
    return round(float(np.clip(eri, 0.0, 1.0)), 3)


# ── DETERMINISTIC FINAL ENVIRONMENTAL SAFETY DECISION ENGINE ──────

def final_environmental_status(
    ph: Optional[float] = None,
    dissolved_oxygen: Optional[float] = None,
    turbidity: Optional[float] = None,
    specific_conductance: Optional[float] = None,
    fdom: Optional[float] = None,
    temperature: Optional[float] = 20.0,
    chlorophyll: Optional[float] = None,
    nitrate: Optional[float] = None,
    phosphate: Optional[float] = None,
    lead_risk: Optional[float] = None,
    mercury_risk: Optional[float] = None,
    arsenic_risk: Optional[float] = None,
    microbial_risk: Optional[float] = None,
    m1_anomaly_status: str = "Normal",
    m1_anomaly_score: float = 0.0,
    m2_risk_label: str = "SAFE",
    m2_confidence: float = 0.0,
    site_id: str = "UNKNOWN",
) -> Tuple[str, str, bool, List[str], str, List[str]]:
    """
    Hybrid Environmental Decision Engine:
      ML Prediction + Scientific Guardrails + Multi-Domain Indicators.

    Evaluates scientific hard-constraints against ML predictions:
      - pH limits & chemical shocks
      - DO hypoxia & biological oxygen stress
      - Nutrient concentrations (NO3, PO4) & Chlorophyll-a
      - Eutrophication synergy: Low DO + High nutrients/chlorophyll -> CRITICAL
      - Heavy metal contamination risk indicators (Lead, Mercury, Arsenic)
      - Microbial contamination risk indicators (E. coli probability)

    Returns:
      (final_status, assessment_label, safety_override_applied, override_reasons, primary_override_reason, contributing_params)
    """
    valid_params = [v for v in [ph, dissolved_oxygen, turbidity, specific_conductance, fdom]
                    if v is not None and not (isinstance(v, float) and np.isnan(v))]

    # 1. Telemetry Completeness Check
    if len(valid_params) < 2:
        return (
            "INSUFFICIENT_DATA",
            "INSUFFICIENT_DATA",
            False,
            ["Fewer than 2 valid sensor channels available. Operational status cannot be verified."],
            "Insufficient sensor telemetry available to establish conclusive operational safety.",
            [],
        )

    critical_overrides = []
    warning_overrides = []
    contributing_params = []

    # ── 2. Hard Environmental Constraints (CRITICAL) ───────────────
    
    # A. Multi-Factor Eutrophication & Hypoxia Synergy
    # Low DO (< 4.0 mg/L) combined with high nutrients or algal bloom
    has_high_nutrients = (nitrate is not None and nitrate >= 5.0) or (phosphate is not None and phosphate >= 0.08)
    has_high_algae = (chlorophyll is not None and chlorophyll >= 25.0) or (fdom is not None and fdom >= 60.0)
    
    if dissolved_oxygen is not None and not np.isnan(dissolved_oxygen) and dissolved_oxygen < 4.0 and (has_high_nutrients or has_high_algae):
        critical_overrides.append(
            f"Eutrophic Ecological Collapse (DO = {dissolved_oxygen:.2f} mg/L, High Nutrients/Algae): Low dissolved oxygen combined with elevated nutrients indicates possible eutrophication leading to severe aquatic stress."
        )
        contributing_params.extend(["dissolved_oxygen"])
        if has_high_nutrients:
            contributing_params.extend(["nitrate" if nitrate and nitrate >= 5.0 else "phosphate"])
        if has_high_algae:
            contributing_params.append("chlorophyll_a" if chlorophyll and chlorophyll >= 25.0 else "fdom")

    # B. pH Hard Lethal Violations (EPA Freshwater Aquatic Life Criteria)
    if ph is not None and not np.isnan(ph):
        if ph < THRESHOLDS["ph_critical_acid"]:
            critical_overrides.append(
                f"Severe Acidification (pH = {ph:.2f} < {THRESHOLDS['ph_critical_acid']}): Violates EPA freshwater aquatic life survival envelope (corrosive/toxic shock)."
            )
            contributing_params.append("ph")
        elif ph > THRESHOLDS["ph_critical_alkaline"]:
            critical_overrides.append(
                f"Severe Alkalinity (pH = {ph:.2f} > {THRESHOLDS['ph_critical_alkaline']}): Violates EPA freshwater aquatic life survival envelope (caustic/ammonia toxicity)."
            )
            contributing_params.append("ph")

    # C. Dissolved Oxygen Lethal Anoxia (USGS/EPA Criteria)
    if dissolved_oxygen is not None and not np.isnan(dissolved_oxygen):
        if dissolved_oxygen < THRESHOLDS["do_critical_hypoxia"]:
            critical_overrides.append(
                f"Lethal Hypoxia/Anoxia (DO = {dissolved_oxygen:.2f} mg/L < {THRESHOLDS['do_critical_hypoxia']} mg/L): Acute asphyxiation hazard for fish and macroinvertebrates."
            )
            contributing_params.append("dissolved_oxygen")

    # D. Turbidity Extreme Impairment
    if turbidity is not None and not np.isnan(turbidity):
        if turbidity > THRESHOLDS["turbidity_critical"]:
            critical_overrides.append(
                f"Catastrophic Turbidity ({turbidity:.1f} FNU > {THRESHOLDS['turbidity_critical']} FNU): Massive particulate suspension / industrial effluent."
            )
            contributing_params.append("turbidity")

    # E. Specific Conductance Extreme Salinization
    if specific_conductance is not None and not np.isnan(specific_conductance):
        if specific_conductance > THRESHOLDS["spcond_critical"]:
            critical_overrides.append(
                f"Severe Ionic Shock ({specific_conductance:.1f} µS/cm > {THRESHOLDS['spcond_critical']} µS/cm): Extreme salinization / chemical discharge."
            )
            contributing_params.append("specific_conductance")

    # F. fDOM Extreme Organic Contamination
    if fdom is not None and not np.isnan(fdom):
        if fdom > THRESHOLDS["fdom_critical"]:
            critical_overrides.append(
                f"Extreme Organic Pollution (fDOM = {fdom:.1f} QSU > {THRESHOLDS['fdom_critical']} QSU): Heavy organic sewage or leachate contamination."
            )
            contributing_params.append("fdom")

    # G. Heavy Metal Contamination High Risk
    max_metal = max([m for m in [lead_risk, mercury_risk, arsenic_risk] if m is not None] or [0.0])
    if max_metal >= 0.70:
        critical_overrides.append(
            f"Severe Heavy Metal Contamination Risk (Max Metal Risk = {max_metal:.2f} > 0.70): High toxic metals mobilization (Lead/Mercury/Arsenic proxies)."
        )
        if lead_risk and lead_risk >= 0.70: contributing_params.append("lead_risk_index")
        if mercury_risk and mercury_risk >= 0.70: contributing_params.append("mercury_risk_index")
        if arsenic_risk and arsenic_risk >= 0.70: contributing_params.append("arsenic_risk_index")

    # H. Microbial Contamination Acute Risk
    if microbial_risk is not None and (microbial_risk >= 65.0 or (microbial_risk <= 1.0 and microbial_risk >= 0.65)):
        mb_pct = microbial_risk if microbial_risk > 1.0 else microbial_risk * 100.0
        critical_overrides.append(
            f"Acute Microbial Contamination Risk (E. coli Probability = {mb_pct:.1f}% > 65%): Severe biological pathogen risk in water catchment."
        )
        contributing_params.append("microbial_risk_index")

    # If any CRITICAL hard constraint violated:
    if critical_overrides:
        safety_override = (m2_risk_label != "CRITICAL")
        primary_reason = critical_overrides[0]
        # Clean up unique params
        unique_params = list(dict.fromkeys(contributing_params))
        return "CRITICAL", "CRITICAL", safety_override, critical_overrides, primary_reason, unique_params

    # ── 3. Moderate Environmental Constraints (WARNING) ────────────
    if ph is not None and not np.isnan(ph):
        if ph < THRESHOLDS["ph_warning_acid"] and not (site_id == "BARC" and ph >= 4.8):
            warning_overrides.append(f"Sub-optimal Acidification (pH = {ph:.2f} < {THRESHOLDS['ph_warning_acid']})")
            contributing_params.append("ph")
        elif ph > THRESHOLDS["ph_warning_alkaline"]:
            warning_overrides.append(f"Sub-optimal Alkalinity (pH = {ph:.2f} > {THRESHOLDS['ph_warning_alkaline']})")
            contributing_params.append("ph")

    if dissolved_oxygen is not None and not np.isnan(dissolved_oxygen):
        if dissolved_oxygen < THRESHOLDS["do_warning_hypoxia"]:
            warning_overrides.append(f"Hypoxic Stress (DO = {dissolved_oxygen:.2f} mg/L < {THRESHOLDS['do_warning_hypoxia']} mg/L)")
            contributing_params.append("dissolved_oxygen")

    if turbidity is not None and not np.isnan(turbidity):
        if turbidity > THRESHOLDS["turbidity_warning"]:
            warning_overrides.append(f"Elevated Turbidity ({turbidity:.1f} FNU > {THRESHOLDS['turbidity_warning']} FNU)")
            contributing_params.append("turbidity")

    if specific_conductance is not None and not np.isnan(specific_conductance):
        spcond_limit = 500.0 if site_id != "ARIK" else 850.0
        if specific_conductance > spcond_limit:
            warning_overrides.append(f"Elevated Conductance ({specific_conductance:.1f} µS/cm > {spcond_limit} µS/cm)")
            contributing_params.append("specific_conductance")

    if nitrate is not None and nitrate >= 10.0:
        warning_overrides.append(f"Elevated Nitrate (NO3 = {nitrate:.2f} mg/L >= 10 mg/L EPA MCL)")
        contributing_params.append("nitrate_mg_l")

    if phosphate is not None and phosphate >= 0.10:
        warning_overrides.append(f"Elevated Phosphate (PO4 = {phosphate:.3f} mg/L >= 0.10 mg/L Trophic Threshold)")
        contributing_params.append("phosphate_mg_l")

    if chlorophyll is not None and chlorophyll >= 30.0:
        warning_overrides.append(f"Algal Bloom Risk (Chlorophyll-a = {chlorophyll:.1f} µg/L >= 30 µg/L)")
        contributing_params.append("chlorophyll_a_ug_l")

    if max_metal >= 0.35:
        warning_overrides.append(f"Moderate Heavy Metal Contamination Risk (Index = {max_metal:.2f} >= 0.35)")
        contributing_params.append("heavy_metal_risk")

    if microbial_risk is not None and ((microbial_risk >= 25.0 and microbial_risk < 65.0) or (microbial_risk >= 0.25 and microbial_risk < 0.65)):
        mb_pct = microbial_risk if microbial_risk > 1.0 else microbial_risk * 100.0
        warning_overrides.append(f"Elevated Microbial Risk (E. coli Probability = {mb_pct:.1f}%)")
        contributing_params.append("microbial_risk_index")

    if warning_overrides:
        final_stat = "CRITICAL" if m2_risk_label == "CRITICAL" else "WARNING"
        safety_override = (m2_risk_label == "SAFE")
        primary_reason = warning_overrides[0]
        unique_params = list(dict.fromkeys(contributing_params))
        return final_stat, "WARNING", safety_override, warning_overrides, primary_reason, unique_params

    # ── 4. Fallback to Model 2 ML Predictions ──────────────────────
    if m2_risk_label == "CRITICAL":
        return (
            "CRITICAL",
            "SAFE",
            False,
            ["Model 2 Random Forest multi-parameter classifier predicted CRITICAL based on correlated feature interactions."],
            "Random Forest ML risk classifier flagged CRITICAL operational risk based on learned multivariate risk distributions.",
            ["ml_multivariate_correlation"],
        )
    elif m2_risk_label == "WARNING":
        return (
            "WARNING",
            "SAFE",
            False,
            ["Model 2 Random Forest multi-parameter classifier predicted WARNING."],
            "Random Forest ML risk classifier flagged WARNING operational risk.",
            ["ml_multivariate_correlation"],
        )

    # ── 5. Model 1 Statistical Anomaly Check ───────────────────────
    if m1_anomaly_status == "Anomaly" and m1_anomaly_score > 0.0:
        return (
            "WARNING",
            "ANOMALY_WATCH",
            True,
            [f"Model 1 Isolation Forest detected multidimensional statistical anomaly (score = {m1_anomaly_score:+.4f}) despite individual parameters falling within broad envelopes."],
            f"Statistical outlier detected by Isolation Forest (score = {m1_anomaly_score:+.4f}) indicating anomalous multi-parameter signature.",
            ["anomaly_score"],
        )

    # ── 6. SAFE ───────────────────────────────────────────────────
    return (
        "SAFE",
        "SAFE",
        False,
        ["All physical, chemical, nutrient, and ML intelligence assessments confirm normal safe baseline conditions."],
        "All hydrological, chemical, nutrient, biological, and ML risk assessments confirm normal safe baseline operating conditions.",
        [],
    )


def generate_explanations(
    ph: Optional[float],
    dissolved_oxygen: Optional[float],
    turbidity: Optional[float],
    specific_conductance: Optional[float],
    fdom: Optional[float],
    nitrate: Optional[float],
    phosphate: Optional[float],
    chlorophyll: Optional[float],
    lead_risk: Optional[float],
    mercury_risk: Optional[float],
    arsenic_risk: Optional[float],
    microbial_risk: Optional[float],
    m1_anomaly_status: str,
    m1_anomaly_score: float,
    m2_risk_label: str,
    m2_confidence: float,
    final_status: str,
    safety_override_applied: bool,
    override_reasons: List[str],
    osi: float,
    csi: float,
    opi: float,
    eri: float,
) -> List[str]:
    """
    Generate comprehensive, evidence-based diagnostic explanations explaining the FINAL STATUS.
    """
    explanations = []

    # 1. Safety Override Attribution (If ML prediction was overridden)
    if safety_override_applied:
        explanations.append(
            f"🛡️ SAFETY GUARDRAIL OVERRIDE: ML Model 2 predicted {m2_risk_label} (Confidence: {m2_confidence*100:.1f}%), but Deterministic Environmental Safety Guardrails upgraded final status to {final_status}."
        )
        for reason in override_reasons:
            explanations.append(f"  • {reason}")

    # 2. Specific Parameter Attributions
    if ph is not None and not np.isnan(ph):
        if ph < THRESHOLDS["ph_critical_acid"]:
            explanations.append(f"Severe acidic condition observed (pH = {ph:.2f}, CSI = {csi:.2f}) indicating potential acid mine drainage or chemical influx risk.")
        elif ph > THRESHOLDS["ph_critical_alkaline"]:
            explanations.append(f"Severe alkaline condition observed (pH = {ph:.2f}, CSI = {csi:.2f}) indicating potential caustic discharge or photosynthetic diurnal swing.")
        elif ph < THRESHOLDS["ph_warning_acid"]:
            explanations.append(f"Moderately acidic water (pH = {ph:.2f}) observed.")
        elif ph > THRESHOLDS["ph_warning_alkaline"]:
            explanations.append(f"Elevated alkaline water (pH = {ph:.2f}) observed.")

    if dissolved_oxygen is not None and not np.isnan(dissolved_oxygen):
        if dissolved_oxygen < THRESHOLDS["do_critical_hypoxia"]:
            explanations.append(f"Lethal anoxic conditions (DO = {dissolved_oxygen:.2f} mg/L, OSI = {osi:.2f}) presents acute respiratory risk for fish and aquatic fauna.")
        elif dissolved_oxygen < THRESHOLDS["do_warning_hypoxia"]:
            explanations.append(f"Hypoxic oxygen deficit (DO = {dissolved_oxygen:.2f} mg/L, OSI = {osi:.2f}) observed.")
        elif dissolved_oxygen >= 8.0:
            explanations.append(f"Well-oxygenated water column (DO = {dissolved_oxygen:.2f} mg/L) supports healthy aquatic biota.")

    if turbidity is not None and not np.isnan(turbidity):
        if turbidity > THRESHOLDS["turbidity_critical"]:
            explanations.append(f"Severe turbidity spike ({turbidity:.1f} FNU) indicating potential storm runoff, bank erosion, or particulate influx.")
        elif turbidity > THRESHOLDS["turbidity_warning"]:
            explanations.append(f"Elevated turbidity ({turbidity:.1f} FNU) reduces light penetration and elevates particulate pollution risk.")
        else:
            explanations.append(f"Low turbidity ({turbidity:.1f} FNU) confirms clear water clarity.")

    if specific_conductance is not None and not np.isnan(specific_conductance):
        if specific_conductance > THRESHOLDS["spcond_critical"]:
            explanations.append(f"Severe ionic conductance elevation ({specific_conductance:.1f} µS/cm) indicating potential salinization or dissolved ion influx.")
        elif specific_conductance > THRESHOLDS["spcond_warning"]:
            explanations.append(f"Elevated electrical conductivity ({specific_conductance:.1f} µS/cm) indicates increased dissolved ion concentrations.")

    if fdom is not None and not np.isnan(fdom):
        if fdom > THRESHOLDS["fdom_critical"]:
            explanations.append(f"High dissolved organic matter signal (fDOM = {fdom:.1f} QSU, OPI = {opi:.2f}) indicating potential organic loading.")

    # Nutrients & Biology
    if nitrate is not None and nitrate >= 5.0:
        explanations.append(f"Elevated Nitrate level (NO3 = {nitrate:.2f} mg/L) indicating possible agricultural runoff or nutrient enrichment.")

    if phosphate is not None and phosphate >= 0.08:
        explanations.append(f"Elevated Phosphate level (PO4 = {phosphate:.3f} mg/L) indicates potential eutrophication and accelerated algal growth risk.")

    if chlorophyll is not None and chlorophyll >= 25.0:
        explanations.append(f"High Chlorophyll-a biomass ({chlorophyll:.1f} µg/L) indicates active phytoplankton / algal proliferation.")

    # Heavy Metals & Microbial
    max_m = max([m for m in [lead_risk, mercury_risk, arsenic_risk] if m is not None] or [0.0])
    if max_m >= 0.35:
        explanations.append(f"Heavy metal contamination risk inferred from proxy indicators (Max Metal Index: {max_m:.2f}).")

    if microbial_risk is not None:
        mb_pct = microbial_risk if microbial_risk > 1.0 else microbial_risk * 100.0
        if mb_pct >= 25.0:
            explanations.append(f"Elevated microbial pathogen risk inferred from water quality indicators (E. coli Probability: {mb_pct:.1f}%).")

    if eri >= 0.60:
        explanations.append(f"High eutrophication risk ({eri*100:.1f}%) driven by high organic nutrient load and oxygen deficit.")

    if not explanations:
        if final_status == "INSUFFICIENT_DATA":
            explanations.append("Insufficient sensor telemetry available to compute conclusive risk attribution.")
        else:
            explanations.append("All physical, chemical, and biological parameters remain within safe baseline operating envelopes.")

    return explanations


def compute_environmental_intelligence(
    ph: Optional[float] = None,
    dissolved_oxygen: Optional[float] = None,
    turbidity: Optional[float] = None,
    specific_conductance: Optional[float] = None,
    fdom: Optional[float] = None,
    temperature: Optional[float] = 20.0,
    chlorophyll: Optional[float] = None,
    nitrate: Optional[float] = None,
    phosphate: Optional[float] = None,
    lead_risk: Optional[float] = None,
    mercury_risk: Optional[float] = None,
    arsenic_risk: Optional[float] = None,
    microbial_risk: Optional[float] = None,
    site_id: str = "UNKNOWN",
    m1_anomaly_status: str = "Normal",
    m1_anomaly_score: float = 0.0,
    m2_risk_label: str = "SAFE",
    m2_confidence: float = 0.0,
) -> Dict[str, Any]:
    """
    Unified entry point for Hybrid Decision Engine, Guardrail Overrides, and Explainable AI.
    """
    wqi_dict = calculate_wqi(ph, dissolved_oxygen, turbidity, specific_conductance, fdom, site_id)
    osi = calculate_oxygen_stress(dissolved_oxygen, temperature)
    csi = calculate_chemical_stress(ph, specific_conductance, site_id)
    opi = calculate_organic_pollution(fdom, chlorophyll)
    eri = calculate_eutrophication_risk(osi, opi, turbidity, specific_conductance, chlorophyll)

    final_stat, env_assessment, safety_override, override_reasons, primary_reason, contributing_params = final_environmental_status(
        ph=ph,
        dissolved_oxygen=dissolved_oxygen,
        turbidity=turbidity,
        specific_conductance=specific_conductance,
        fdom=fdom,
        temperature=temperature,
        chlorophyll=chlorophyll,
        nitrate=nitrate,
        phosphate=phosphate,
        lead_risk=lead_risk,
        mercury_risk=mercury_risk,
        arsenic_risk=arsenic_risk,
        microbial_risk=microbial_risk,
        m1_anomaly_status=m1_anomaly_status,
        m1_anomaly_score=m1_anomaly_score,
        m2_risk_label=m2_risk_label,
        m2_confidence=m2_confidence,
        site_id=site_id,
    )

    explanations = generate_explanations(
        ph=ph,
        dissolved_oxygen=dissolved_oxygen,
        turbidity=turbidity,
        specific_conductance=specific_conductance,
        fdom=fdom,
        nitrate=nitrate,
        phosphate=phosphate,
        chlorophyll=chlorophyll,
        lead_risk=lead_risk,
        mercury_risk=mercury_risk,
        arsenic_risk=arsenic_risk,
        microbial_risk=microbial_risk,
        m1_anomaly_status=m1_anomaly_status,
        m1_anomaly_score=m1_anomaly_score,
        m2_risk_label=m2_risk_label,
        m2_confidence=m2_confidence,
        final_status=final_stat,
        safety_override_applied=safety_override,
        override_reasons=override_reasons,
        osi=osi,
        csi=csi,
        opi=opi,
        eri=eri,
    )

    return {
        "ml_prediction": m2_risk_label,
        "ml_confidence": round(m2_confidence, 4),
        "environmental_risk": env_assessment,
        "final_status": final_stat,
        "override_reason": primary_reason,
        "contributing_parameters": contributing_params,
        "model2_raw_prediction": m2_risk_label,
        "model2_confidence": round(m2_confidence, 4),
        "environmental_assessment": env_assessment,
        "safety_override_applied": safety_override,
        "override_reasons": override_reasons,
        "environmental_indicators": {
            "wqi": wqi_dict["wqi_score"],
            "wqi_grade": wqi_dict["wqi_grade"],
            "wqi_note": wqi_dict.get("wqi_note", ""),
            "oxygen_stress_index": osi,
            "chemical_stress_index": csi,
            "organic_pollution_indicator": opi,
            "eutrophication_risk": eri,
        },
        "explanation": explanations,
    }
