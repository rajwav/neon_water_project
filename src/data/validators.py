"""
Validation rules and high-performance vectorized checks for water quality observations.
"""

import hashlib
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from src.data.constants import (
    INSTRUMENT_RANGES,
    PARAM_TO_QF_MAP,
    SENSOR_PARAMETERS,
)
from src.data.schemas import SensorQualityFlag


def generate_observation_id(site_id: str, sensor_pos: str, timestamp_utc_iso: str) -> str:
    """Generate a deterministic, reproducible observation ID from coordinates."""
    raw_key = f"{site_id}:{sensor_pos}:{timestamp_utc_iso}".encode("utf-8")
    return hashlib.sha256(raw_key).hexdigest()[:24]


def apply_instrument_range_flags(
    df: pd.DataFrame
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Vectorized evaluation of instrument physical operating boundaries.
    Does NOT mutate, clip, or drop values; assigns OUT_OF_INSTRUMENT_RANGE flag.
    """
    out_of_range_counts = {}

    for param in SENSOR_PARAMETERS:
        if param not in df.columns:
            continue

        min_val, max_val = INSTRUMENT_RANGES[param]
        series = df[param]
        
        # Valid numerical values outside instrument bounds
        invalid_mask = series.notna() & ((series < min_val) | (series > max_val))
        count = int(invalid_mask.sum())
        out_of_range_counts[param] = count
        
        flag_col = f"{param}_flag_range"
        df[flag_col] = invalid_mask

    return df, out_of_range_counts


def apply_neon_qf_flags(
    df: pd.DataFrame
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Vectorized evaluation of NEON Final Quality Flags.
    Preserves original QF columns and flags failures without dropping rows.
    """
    qf_fail_counts = {}

    for param, qf_col in PARAM_TO_QF_MAP.items():
        if qf_col not in df.columns:
            continue

        # NEON FinalQF == 1 indicates failed quality check
        fail_mask = df[qf_col] == 1
        count = int(fail_mask.sum())
        qf_fail_counts[param] = count
        
        flag_col = f"{param}_flag_qf"
        df[flag_col] = fail_mask

    return df, qf_fail_counts


def detect_duplicates(
    df: pd.DataFrame
) -> Tuple[pd.DataFrame, int]:
    """
    Identifies duplicate records matching (site_id, sensor_position, timestamp_utc).
    Preserves all duplicate instances and marks is_duplicate=True without silent deletion.
    """
    dup_mask = df.duplicated(
        subset=["site_id", "sensor_position", "timestamp_utc"],
        keep=False
    )
    df["is_duplicate"] = dup_mask
    total_duplicates = int(dup_mask.sum())
    return df, total_duplicates


def build_compact_quality_flags(df: pd.DataFrame) -> pd.Series:
    """
    Constructs a structured JSON-compatible string/list per row summarizing
    all active quality flags per parameter for efficient downstream querying.
    """
    def row_flags(row):
        flags = {}
        for param in SENSOR_PARAMETERS:
            param_flags = []
            if pd.isna(row.get(param)):
                param_flags.append(SensorQualityFlag.MISSING_VALUE.value)
            else:
                if row.get(f"{param}_flag_range", False):
                    param_flags.append(SensorQualityFlag.OUT_OF_INSTRUMENT_RANGE.value)
                if row.get(f"{param}_flag_qf", False):
                    param_flags.append(SensorQualityFlag.NEON_QF_FAIL.value)
            
            if row.get("is_duplicate", False):
                param_flags.append(SensorQualityFlag.DUPLICATE_RECORD.value)
                
            if not param_flags:
                param_flags.append(SensorQualityFlag.VALID.value)
            flags[param] = param_flags
        return flags

    return df.apply(row_flags, axis=1)
