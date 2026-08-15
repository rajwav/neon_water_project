"""
Vectorized label generation engine for operational_risk_labels_v2.0.

Processes millions of rows using pandas vectorization — no per-row
Pydantic instantiation. Implements the complete labeling logic from
docs/LABEL_SPEC_v2.md.
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from src.labels import (
    NORMAL, ELEVATED, EXTREME, MISSING, SENSOR_ARTIFACT, INSTRUMENT_LIMIT,
    SAFE, WARNING, CRITICAL, INSUFFICIENT_DATA,
    COMPLETENESS_FULL, COMPLETENESS_PARTIAL, COMPLETENESS_DEGRADED, COMPLETENESS_INSUFFICIENT,
    CONFIDENCE_HIGH, CONFIDENCE_MODERATE, CONFIDENCE_LOW, CONFIDENCE_UNRELIABLE,
    LABEL_VERSION,
    PH_THRESHOLDS, DO_THRESHOLDS, TURBIDITY_THRESHOLDS,
    SPCOND_THRESHOLDS, FDOM_THRESHOLDS, CHLOROPHYLL_THRESHOLDS,
    INSTRUMENT_RANGES, INSTALLED_PARAMS,
)

# All assessable parameters (sensor_depth excluded from risk assessment)
ALL_RISK_PARAMS = ["ph", "dissolved_oxygen", "turbidity", "specific_conductance", "fdom", "chlorophyll"]

# QF flag column mapping
PARAM_QF_COL = {
    "ph": "ph_flag_qf",
    "dissolved_oxygen": "dissolved_oxygen_flag_qf",
    "turbidity": "turbidity_flag_qf",
    "specific_conductance": "specific_conductance_flag_qf",
    "fdom": "fdom_flag_qf",
    "chlorophyll": "chlorophyll_flag_qf",
}

# Range flag column mapping
PARAM_RANGE_COL = {
    "ph": "ph_flag_range",
    "dissolved_oxygen": "dissolved_oxygen_flag_range",
    "turbidity": "turbidity_flag_range",
    "specific_conductance": "specific_conductance_flag_range",
    "fdom": "fdom_flag_range",
    "chlorophyll": "chlorophyll_flag_range",
}


def _classify_asymmetric_param(
    values: pd.Series,
    thresholds: Dict,
) -> pd.Series:
    """
    Classify values for parameters with asymmetric normal ranges
    (pH, DO, SpCond at most sites, fDOM at BARC).
    """
    states = pd.Series(NORMAL, index=values.index, dtype=object)

    normal_lo, normal_hi = thresholds["normal"]

    # NORMAL: within [normal_lo, normal_hi]
    is_normal = (values >= normal_lo) & (values <= normal_hi)

    # ELEVATED ranges
    elev_lo = thresholds.get("elevated_lo")
    elev_hi = thresholds.get("elevated_hi")
    extreme_below = thresholds.get("extreme_below")
    extreme_above = thresholds.get("extreme_above")

    is_elevated = pd.Series(False, index=values.index)

    if elev_lo and elev_lo[0] is not None:
        is_elevated = is_elevated | ((values >= elev_lo[0]) & (values < elev_lo[1]))
    if elev_hi and elev_hi[0] is not None:
        is_elevated = is_elevated | ((values > elev_hi[0]) & (values <= elev_hi[1]))

    is_extreme = pd.Series(False, index=values.index)
    if extreme_below is not None:
        is_extreme = is_extreme | (values < extreme_below)
    if extreme_above is not None:
        is_extreme = is_extreme | (values > extreme_above)

    states[is_elevated & ~is_normal] = ELEVATED
    states[is_extreme] = EXTREME

    return states


def _classify_upper_only_param(
    values: pd.Series,
    normal_max: float,
    elevated_max: float,
) -> pd.Series:
    """
    Classify values for parameters where only high values indicate concern
    (turbidity, fDOM at non-BARC sites, chlorophyll).
    Normal: [0, normal_max]. Elevated: (normal_max, elevated_max]. Extreme: >elevated_max.
    """
    states = pd.Series(NORMAL, index=values.index, dtype=object)
    states[(values > normal_max) & (values <= elevated_max)] = ELEVATED
    states[values > elevated_max] = EXTREME
    return states


def classify_parameter_states(df: pd.DataFrame) -> pd.DataFrame:
    """
    Vectorized classification of each parameter into NORMAL/ELEVATED/EXTREME/
    MISSING/SENSOR_ARTIFACT/INSTRUMENT_LIMIT for every observation.

    Adds columns: ph_state, dissolved_oxygen_state, turbidity_state,
    specific_conductance_state, fdom_state, chlorophyll_state
    """
    sites = df["site_id"].unique()

    for param in ALL_RISK_PARAMS:
        state_col = f"{param}_state"
        df[state_col] = MISSING  # default for all

        for site in sites:
            site_mask = df["site_id"] == site
            site_idx = df.index[site_mask]

            if len(site_idx) == 0:
                continue

            values = df.loc[site_idx, param] if param in df.columns else pd.Series(np.nan, index=site_idx)

            # 1. Check if parameter is installed at any position for this site
            site_positions = [k for k in INSTALLED_PARAMS if k[0] == site]
            installed_at_site = any(param in INSTALLED_PARAMS[k] for k in site_positions)

            if not installed_at_site:
                # Structurally absent — remains MISSING
                continue

            # 2. Check per-position installation
            for pos_key in site_positions:
                pos_mask = site_mask & (df["sensor_position"] == pos_key[1])
                pos_idx = df.index[pos_mask]
                if len(pos_idx) == 0:
                    continue

                if param not in INSTALLED_PARAMS[pos_key]:
                    # Not installed at this specific position
                    continue

                pos_values = df.loc[pos_idx, param]

                # Start with MISSING for NaN
                pos_states = pd.Series(MISSING, index=pos_idx, dtype=object)
                has_value = pos_values.notna()

                if has_value.sum() == 0:
                    df.loc[pos_idx, state_col] = pos_states
                    continue

                valid_idx = pos_idx[has_value]
                valid_values = pos_values[has_value]

                # 3. Check sensor artifacts (e.g. negative turbidity/fDOM, dry-bed SpCond)
                if param == "turbidity":
                    artifact_mask = valid_values < 0.0
                    pos_states.loc[valid_idx[artifact_mask]] = SENSOR_ARTIFACT
                    valid_idx = valid_idx[~artifact_mask]
                    valid_values = valid_values[~artifact_mask]

                elif param == "fdom":
                    artifact_mask = valid_values < 0.0
                    pos_states.loc[valid_idx[artifact_mask]] = SENSOR_ARTIFACT
                    valid_idx = valid_idx[~artifact_mask]
                    valid_values = valid_values[~artifact_mask]

                elif param == "specific_conductance" and site == "ARIK":
                    # Near-zero SpCond at ARIK is sensor exposure during dry periods
                    # ARIK valid SpCond should be >100; values <5 are artifacts
                    artifact_mask = valid_values < 5.0
                    pos_states.loc[valid_idx[artifact_mask]] = SENSOR_ARTIFACT
                    valid_idx = valid_idx[~artifact_mask]
                    valid_values = valid_values[~artifact_mask]

                if len(valid_idx) == 0:
                    df.loc[pos_idx, state_col] = pos_states
                    continue

                # 4. Check instrument limits
                if param in INSTRUMENT_RANGES:
                    inst_lo, inst_hi = INSTRUMENT_RANGES[param]
                    oor_mask = (valid_values < inst_lo) | (valid_values > inst_hi)
                    # Also check the _flag_range column if available
                    range_col = PARAM_RANGE_COL.get(param)
                    if range_col and range_col in df.columns:
                        oor_mask = oor_mask | df.loc[valid_idx, range_col].fillna(False).astype(bool)
                    pos_states.loc[valid_idx[oor_mask]] = INSTRUMENT_LIMIT
                    # Remove OOR from further classification
                    valid_idx = valid_idx[~oor_mask]
                    valid_values = valid_values[~oor_mask]

                if len(valid_idx) == 0:
                    df.loc[pos_idx, state_col] = pos_states
                    continue

                # 5. Apply site-specific thresholds
                if param == "ph" and site in PH_THRESHOLDS:
                    classified = _classify_asymmetric_param(valid_values, PH_THRESHOLDS[site])
                    pos_states.loc[valid_idx] = classified

                elif param == "dissolved_oxygen" and site in DO_THRESHOLDS:
                    classified = _classify_asymmetric_param(valid_values, DO_THRESHOLDS[site])
                    pos_states.loc[valid_idx] = classified

                elif param == "turbidity" and site in TURBIDITY_THRESHOLDS:
                    t = TURBIDITY_THRESHOLDS[site]
                    classified = _classify_upper_only_param(valid_values, t["normal_max"], t["elevated_max"])
                    pos_states.loc[valid_idx] = classified

                elif param == "specific_conductance" and site in SPCOND_THRESHOLDS:
                    classified = _classify_asymmetric_param(valid_values, SPCOND_THRESHOLDS[site])
                    pos_states.loc[valid_idx] = classified

                elif param == "fdom" and site in FDOM_THRESHOLDS:
                    t = FDOM_THRESHOLDS[site]
                    if "normal" in t:
                        # BARC has asymmetric fDOM thresholds
                        classified = _classify_asymmetric_param(valid_values, t)
                    else:
                        # Other sites use upper-only
                        classified = _classify_upper_only_param(valid_values, t["normal_max"], t["elevated_max"])
                    pos_states.loc[valid_idx] = classified

                elif param == "chlorophyll" and site in CHLOROPHYLL_THRESHOLDS:
                    t = CHLOROPHYLL_THRESHOLDS[site]
                    classified = _classify_upper_only_param(valid_values, t["normal_max"], t["elevated_max"])
                    pos_states.loc[valid_idx] = classified

                df.loc[pos_idx, state_col] = pos_states

    return df


def compute_aggregated_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply multi-parameter aggregation rule from LABEL_SPEC_v2.md Section 7.
    Computes: risk_label_v2, elevated_count, extreme_count, assessable_count.
    """
    state_cols = [f"{p}_state" for p in ALL_RISK_PARAMS]
    assessable_states = {NORMAL, ELEVATED, EXTREME}

    # Vectorized counts using numpy
    state_matrix = df[state_cols].values

    assessable_count = np.sum(np.isin(state_matrix, list(assessable_states)), axis=1)
    elevated_count = np.sum(state_matrix == ELEVATED, axis=1)
    extreme_count = np.sum(state_matrix == EXTREME, axis=1)

    df["assessable_count"] = assessable_count.astype(np.int8)
    df["elevated_count"] = elevated_count.astype(np.int8)
    df["extreme_count"] = extreme_count.astype(np.int8)

    # Apply aggregation rule (vectorized)
    labels = np.full(len(df), SAFE, dtype=object)

    # INSUFFICIENT_DATA: assessable < 2
    labels[assessable_count < 2] = INSUFFICIENT_DATA

    # WARNING: elevated >= 1
    labels[(assessable_count >= 2) & (elevated_count >= 1)] = WARNING

    # WARNING: exactly 1 extreme, 0 elevated
    labels[(assessable_count >= 2) & (extreme_count == 1) & (elevated_count == 0)] = WARNING

    # CRITICAL: elevated >= 3
    labels[(assessable_count >= 2) & (elevated_count >= 3)] = CRITICAL

    # CRITICAL: extreme >= 1 and elevated >= 1
    labels[(assessable_count >= 2) & (extreme_count >= 1) & (elevated_count >= 1)] = CRITICAL

    # CRITICAL: extreme >= 2
    labels[(assessable_count >= 2) & (extreme_count >= 2)] = CRITICAL

    df["risk_label_v2"] = labels

    return df


def compute_data_completeness(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute data completeness and label confidence per LABEL_SPEC_v2.md Sections 8-9.
    """
    state_cols = [f"{p}_state" for p in ALL_RISK_PARAMS]
    state_matrix = df[state_cols].values

    # Compute installed count per row
    installed_counts = np.zeros(len(df), dtype=np.int8)
    for (site, pos), params in INSTALLED_PARAMS.items():
        mask = (df["site_id"].values == site) & (df["sensor_position"].values == pos)
        installed_counts[mask] = len(params)

    # Available = not MISSING and not SENSOR_ARTIFACT and not INSTRUMENT_LIMIT
    available_states = {NORMAL, ELEVATED, EXTREME}
    available_count = np.sum(np.isin(state_matrix, list(available_states)), axis=1)

    # QF clean = available AND not QF flagged
    qf_clean_count = np.zeros(len(df), dtype=np.int8)
    for param in ALL_RISK_PARAMS:
        state_col = f"{param}_state"
        qf_col = PARAM_QF_COL.get(param)
        if qf_col and qf_col in df.columns and state_col in df.columns:
            is_available = np.isin(df[state_col].values, list(available_states))
            is_qf_clean = ~df[qf_col].fillna(False).astype(bool).values
            qf_clean_count += (is_available & is_qf_clean).astype(np.int8)

    # Ratios (avoid division by zero)
    with np.errstate(divide='ignore', invalid='ignore'):
        completeness_ratio = np.where(installed_counts > 0,
                                       available_count / installed_counts, 0.0)
        quality_ratio = np.where(installed_counts > 0,
                                  qf_clean_count / installed_counts, 0.0)

    # Classify completeness
    completeness = np.full(len(df), COMPLETENESS_INSUFFICIENT, dtype=object)
    completeness[(completeness_ratio >= 0.25) | (df["assessable_count"].values >= 2)] = COMPLETENESS_DEGRADED
    completeness[(completeness_ratio >= 0.50) & (quality_ratio >= 0.30)] = COMPLETENESS_PARTIAL
    completeness[(completeness_ratio >= 0.80) & (quality_ratio >= 0.60)] = COMPLETENESS_FULL

    df["data_completeness"] = completeness

    # Label confidence
    confidence = np.full(len(df), CONFIDENCE_UNRELIABLE, dtype=object)

    is_full = completeness == COMPLETENESS_FULL
    is_partial = completeness == COMPLETENESS_PARTIAL
    is_degraded = completeness == COMPLETENESS_DEGRADED
    is_insuff = df["risk_label_v2"].values == INSUFFICIENT_DATA

    confidence[is_degraded] = CONFIDENCE_LOW
    confidence[is_partial] = CONFIDENCE_MODERATE
    confidence[is_full] = CONFIDENCE_HIGH
    confidence[is_insuff] = CONFIDENCE_UNRELIABLE

    df["label_confidence"] = confidence

    return df


def build_per_param_state(df: pd.DataFrame) -> pd.Series:
    """
    Build compact JSON string of per-parameter states.
    Done in bulk using vectorized string operations for efficiency.
    """
    state_cols = {p: f"{p}_state" for p in ALL_RISK_PARAMS}

    def _row_to_json(row):
        d = {}
        for param, col in state_cols.items():
            val = row.get(col)
            if val and val != MISSING:
                d[param] = val
            elif val == MISSING:
                d[param] = MISSING
        return json.dumps(d, separators=(",", ":"))

    # Process in chunks for memory efficiency
    chunk_size = 100_000
    results = []
    for start in range(0, len(df), chunk_size):
        chunk = df.iloc[start:start + chunk_size]
        chunk_result = chunk.apply(_row_to_json, axis=1)
        results.append(chunk_result)

    return pd.concat(results)


def generate_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main entry point: apply the complete v2.0 labeling pipeline.
    Returns the dataframe with all new label columns added.
    """
    print(f"  Classifying parameter states for {len(df):,} observations...")
    df = classify_parameter_states(df)

    print("  Computing aggregated risk labels...")
    df = compute_aggregated_labels(df)

    print("  Computing data completeness and confidence...")
    df = compute_data_completeness(df)

    print("  Building per-parameter state JSON...")
    df["per_param_state"] = build_per_param_state(df)

    # Add provenance columns
    df["label_version"] = LABEL_VERSION
    df["threshold_source"] = "LIT+PCT"
    df["generated_at"] = datetime.now(timezone.utc).isoformat()

    return df
