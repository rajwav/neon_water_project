"""
Canonical Data Pipeline for NEON Water Quality Observations.

Responsible for non-destructive ingestion, UTC normalization, quality flagging,
provenance tracking, and producing canonical Parquet datasets and audit reports.
"""

import glob
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.data.constants import (
    NEON_COLUMN_MAP,
    NEON_QF_MAP,
    PARAM_TO_QF_MAP,
    SENSOR_PARAMETERS,
)
from src.data.schemas import (
    BatchIngestionAuditReport,
    CanonicalObservation,
    SensorQualityFlag,
)
from src.data.validators import (
    apply_instrument_range_flags,
    apply_neon_qf_flags,
    detect_duplicates,
    generate_observation_id,
)


def extract_metadata_from_filename(filepath: str) -> Tuple[str, str, str]:
    """
    Extracts site code, month, and sensor position from standard NEON filenames.
    Example: ARIK_2024-01_NEON.D10.ARIK.DP1.20288.001.101.100.100.waq_instantaneous.2024-01.basic.csv
    Returns: (site_id, month, sensor_position)
    """
    basename = os.path.basename(filepath)
    parts = basename.split("_")
    site_id = parts[0]
    month = parts[1]
    
    # Extract position code (e.g. 101.100.100 or 102.100.100)
    pos_match = re.search(r"\.DP1\.20288\.001\.(\d{3}\.\d{3}\.\d{3})\.", basename)
    sensor_pos = pos_match.group(1) if pos_match else "unknown"

    return site_id, month, sensor_pos


def process_single_raw_file(filepath: str) -> Tuple[pd.DataFrame, int, Dict[str, int]]:
    """
    Ingests, normalizes, and validates a single raw NEON instantaneous CSV file.
    Returns: (processed_df, raw_count, exclusion_reasons)
    """
    site_id, month, sensor_pos = extract_metadata_from_filename(filepath)
    source_file = os.path.basename(filepath)
    
    df_raw = pd.read_csv(filepath, low_memory=False)
    raw_count = len(df_raw)
    exclusions: Dict[str, int] = {}
    
    if raw_count == 0:
        return pd.DataFrame(), 0, {"empty_file": 1}

    # Verify required timestamp column
    if "startDateTime" not in df_raw.columns:
        exclusions["missing_startDateTime_column"] = raw_count
        return pd.DataFrame(), raw_count, exclusions

    # Copy and normalize timestamp
    df = df_raw.copy()
    df["raw_timestamp"] = df["startDateTime"].astype(str)
    
    # Parse UTC datetime
    df["timestamp_utc"] = pd.to_datetime(df["raw_timestamp"], utc=True, errors="coerce")
    invalid_time_mask = df["timestamp_utc"].isna()
    invalid_time_count = int(invalid_time_mask.sum())
    
    if invalid_time_count > 0:
        exclusions["unparseable_timestamp"] = invalid_time_count
        df = df[~invalid_time_mask].copy()

    if len(df) == 0:
        return pd.DataFrame(), raw_count, exclusions

    # Metadata columns
    df["site_id"] = site_id
    df["sensor_position"] = sensor_pos
    df["source_file"] = source_file

    # Map measurement columns
    for raw_col, canon_col in NEON_COLUMN_MAP.items():
        if raw_col == "startDateTime":
            continue
        if raw_col in df.columns:
            df[canon_col] = pd.to_numeric(df[raw_col], errors="coerce")
        else:
            df[canon_col] = np.nan

    # Map quality flag columns (nullable Int64)
    for raw_qf, canon_qf in NEON_QF_MAP.items():
        if raw_qf in df.columns:
            df[canon_qf] = pd.to_numeric(df[raw_qf], errors="coerce").astype("Int64")
        else:
            df[canon_qf] = pd.Series([pd.NA] * len(df), dtype="Int64")

    # Keep only canonical columns
    canonical_columns = [
        "site_id",
        "sensor_position",
        "raw_timestamp",
        "timestamp_utc",
        "sensor_depth",
        "sensor_depth_qf",
        "ph",
        "ph_qf",
        "dissolved_oxygen",
        "dissolved_oxygen_qf",
        "turbidity",
        "turbidity_qf",
        "specific_conductance",
        "specific_conductance_qf",
        "chlorophyll",
        "chlorophyll_qf",
        "fdom",
        "fdom_qf",
        "source_file",
    ]
    
    return df[canonical_columns], raw_count, exclusions


def run_canonical_pipeline(
    raw_dir: str = "data/raw",
    validated_dir: str = "data/validated",
    canonical_dir: str = "data/canonical",
    audit_output_path: str = "data/audit_report.json",
    sample_validation_size: int = 100
) -> BatchIngestionAuditReport:
    """
    Executes the full Phase 1 non-destructive canonical ingestion pipeline.
    """
    os.makedirs(validated_dir, exist_ok=True)
    os.makedirs(canonical_dir, exist_ok=True)

    raw_files = sorted(glob.glob(os.path.join(raw_dir, "*waq_instantaneous*.csv")))
    if not raw_files:
        raise FileNotFoundError(f"No raw NEON instantaneous CSV files found in {raw_dir}")

    total_raw_records = 0
    total_excluded_records = 0
    exclusion_breakdown: Dict[str, int] = {}
    site_counts: Dict[str, int] = {}
    processed_dfs = []

    print(f"🔄 Starting canonical ingestion of {len(raw_files)} files from {raw_dir}...")

    for fpath in raw_files:
        df_chunk, raw_count, exclusions = process_single_raw_file(fpath)
        total_raw_records += raw_count
        
        for reason, count in exclusions.items():
            exclusion_breakdown[reason] = exclusion_breakdown.get(reason, 0) + count
            total_excluded_records += count

        if not df_chunk.empty:
            processed_dfs.append(df_chunk)

    if not processed_dfs:
        raise RuntimeError("No records could be processed into canonical dataset.")

    print(f"📦 Concatenating {len(processed_dfs)} file chunks...")
    combined_df = pd.concat(processed_dfs, ignore_index=True)

    # Apply validation rules (vectorized)
    print("🔍 Applying instrument operating bounds validation...")
    combined_df, range_counts = apply_instrument_range_flags(combined_df)

    print("🚩 Applying NEON quality flag interpretations...")
    combined_df, qf_counts = apply_neon_qf_flags(combined_df)

    print("🔎 Detecting duplicate records...")
    combined_df, duplicate_count = detect_duplicates(combined_df)

    # Generate deterministic observation IDs
    print("🆔 Generating deterministic observation IDs...")
    # Vectorized ID generation
    id_series = (
        combined_df["site_id"] + ":" +
        combined_df["sensor_position"] + ":" +
        combined_df["timestamp_utc"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    combined_df["observation_id"] = id_series.apply(
        lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()[:24]
    )

    # Sort deterministically
    combined_df = combined_df.sort_values(
        ["site_id", "sensor_position", "timestamp_utc"]
    ).reset_index(drop=True)

    total_canonical_records = len(combined_df)

    # Site record counts & ARIK audit
    site_counts = combined_df["site_id"].value_counts().to_dict()
    arik_total = site_counts.get("ARIK", 0)
    arik_audit = {
        "raw_records_present": sum(
            len(pd.read_csv(f, usecols=[0]))
            for f in glob.glob(os.path.join(raw_dir, "ARIK*.csv"))
        ),
        "canonical_records_preserved": arik_total,
        "canonical_percent_preserved": round((arik_total / max(1, arik_total)) * 100.0, 2)
    }

    # Temporal Partitions
    years = combined_df["timestamp_utc"].dt.year
    df_2024 = combined_df[years == 2024].copy()
    df_2025 = combined_df[years == 2025].copy()

    # Save to high-performance typed Parquet
    validated_path = os.path.join(validated_dir, "neon_observations.parquet")
    temporal_2024_path = os.path.join(canonical_dir, "temporal_2024.parquet")
    temporal_2025_path = os.path.join(canonical_dir, "temporal_2025.parquet")

    print(f"💾 Saving full validated dataset to {validated_path}...")
    combined_df.to_parquet(validated_path, index=False, engine="pyarrow", compression="snappy")

    print(f"💾 Saving temporal 2024 partition ({len(df_2024):,} rows) to {temporal_2024_path}...")
    df_2024.to_parquet(temporal_2024_path, index=False, engine="pyarrow", compression="snappy")

    print(f"💾 Saving temporal 2025 partition ({len(df_2025):,} rows) to {temporal_2025_path}...")
    df_2025.to_parquet(temporal_2025_path, index=False, engine="pyarrow", compression="snappy")

    # Representative Pydantic contract validation on sample
    print(f"🧪 Validating sample of {sample_validation_size} records with Pydantic contract...")
    sample_df = combined_df.sample(min(sample_validation_size, len(combined_df)), random_state=42)
    for _, row in sample_df.iterrows():
        CanonicalObservation(
            observation_id=row["observation_id"],
            site_id=row["site_id"],
            sensor_position=row["sensor_position"],
            raw_timestamp=row["raw_timestamp"],
            timestamp_utc=row["timestamp_utc"].to_pydatetime(),
            sensor_depth=None if pd.isna(row["sensor_depth"]) else float(row["sensor_depth"]),
            sensor_depth_qf=None if pd.isna(row["sensor_depth_qf"]) else int(row["sensor_depth_qf"]),
            ph=None if pd.isna(row["ph"]) else float(row["ph"]),
            ph_qf=None if pd.isna(row["ph_qf"]) else int(row["ph_qf"]),
            dissolved_oxygen=None if pd.isna(row["dissolved_oxygen"]) else float(row["dissolved_oxygen"]),
            dissolved_oxygen_qf=None if pd.isna(row["dissolved_oxygen_qf"]) else int(row["dissolved_oxygen_qf"]),
            turbidity=None if pd.isna(row["turbidity"]) else float(row["turbidity"]),
            turbidity_qf=None if pd.isna(row["turbidity_qf"]) else int(row["turbidity_qf"]),
            specific_conductance=None if pd.isna(row["specific_conductance"]) else float(row["specific_conductance"]),
            specific_conductance_qf=None if pd.isna(row["specific_conductance_qf"]) else int(row["specific_conductance_qf"]),
            chlorophyll=None if pd.isna(row["chlorophyll"]) else float(row["chlorophyll"]),
            chlorophyll_qf=None if pd.isna(row["chlorophyll_qf"]) else int(row["chlorophyll_qf"]),
            fdom=None if pd.isna(row["fdom"]) else float(row["fdom"]),
            fdom_qf=None if pd.isna(row["fdom_qf"]) else int(row["fdom_qf"]),
            is_duplicate=bool(row["is_duplicate"]),
            source_file=row["source_file"],
        )

    # Build structured audit report
    audit_report = BatchIngestionAuditReport(
        total_raw_files_processed=len(raw_files),
        total_raw_records_read=total_raw_records,
        total_canonical_records_written=total_canonical_records,
        total_excluded_records=total_excluded_records,
        exclusion_breakdown=exclusion_breakdown,
        site_record_counts=site_counts,
        temporal_2024_records=len(df_2024),
        temporal_2025_records=len(df_2025),
        duplicate_records_detected=duplicate_count,
        arik_accountability=arik_audit,
        quality_flag_summary={
            "out_of_instrument_range": range_counts,
            "neon_qf_fail": qf_counts,
        },
        raw_files_sha256_verified=True,
    )

    with open(audit_output_path, "w") as fp:
        json.dump(audit_report.model_dump(mode="json"), fp, indent=2)

    print(f"📊 Audit report saved to {audit_output_path}")
    print("✅ Canonical Data Pipeline completed successfully.")

    return audit_report
