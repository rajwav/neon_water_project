#!/usr/bin/env python3
"""
Generate operational risk labels v2.0.

Reads canonical observations, applies site-specific ecological thresholds
per LABEL_SPEC_v2.md, and writes labeled dataset.

Usage:
    python scripts/generate_operational_labels.py

Output:
    data/labeled/operational_risk_labels_v2.parquet
    docs/LABEL_GENERATION_REPORT.md

STRICT RULES:
    - Does NOT modify any legacy datasets, models, or artifacts.
    - Does NOT use anomaly_status or any Model 1 output.
    - Uses only canonical observations as input.
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.labels import LABEL_VERSION
from src.labels.labeler import generate_labels, ALL_RISK_PARAMS

# ── Paths ──────────────────────────────────────────────────────────
INPUT_2024 = PROJECT_ROOT / "data" / "canonical" / "temporal_2024.parquet"
INPUT_2025 = PROJECT_ROOT / "data" / "canonical" / "temporal_2025.parquet"
OUTPUT_DIR = PROJECT_ROOT / "data" / "labeled"
OUTPUT_FILE = OUTPUT_DIR / "operational_risk_labels_v2.parquet"
REPORT_FILE = PROJECT_ROOT / "docs" / "LABEL_GENERATION_REPORT.md"

# Columns to preserve from canonical dataset
PRESERVE_COLS = [
    "observation_id", "site_id", "sensor_position",
    "raw_timestamp", "timestamp_utc",
    "ph", "dissolved_oxygen", "turbidity",
    "specific_conductance", "fdom", "chlorophyll", "sensor_depth",
    "ph_qf", "dissolved_oxygen_qf", "turbidity_qf",
    "specific_conductance_qf", "fdom_qf", "chlorophyll_qf", "sensor_depth_qf",
    "ph_flag_qf", "dissolved_oxygen_flag_qf", "turbidity_flag_qf",
    "specific_conductance_flag_qf", "fdom_flag_qf", "chlorophyll_flag_qf",
    "ph_flag_range", "dissolved_oxygen_flag_range", "turbidity_flag_range",
    "specific_conductance_flag_range", "fdom_flag_range", "chlorophyll_flag_range",
    "is_duplicate", "source_file",
]

# New columns added by label generation
LABEL_COLS = [
    "risk_label_v2", "elevated_count", "extreme_count", "assessable_count",
    "data_completeness", "label_confidence", "per_param_state",
    "label_version", "threshold_source", "generated_at",
]

# State columns (intermediate, kept for auditability)
STATE_COLS = [f"{p}_state" for p in ALL_RISK_PARAMS]


def verify_legacy_untouched():
    """Verify that legacy files have not been modified."""
    legacy_files = [
        PROJECT_ROOT / "results" / "final_water_quality_prediction.csv",
        PROJECT_ROOT / "results" / "neon_anomaly_results.csv",
        PROJECT_ROOT / "models" / "saved_models" / "risk_model.pkl",
        PROJECT_ROOT / "models" / "saved_models" / "anomaly_model.pkl",
        PROJECT_ROOT / "models" / "saved_models" / "anomaly_scaler.pkl",
        PROJECT_ROOT / "models" / "saved_models" / "status_encoder.pkl",
        PROJECT_ROOT / "models" / "saved_models" / "model_metadata.pkl",
        PROJECT_ROOT / "models" / "saved_models" / "anomaly_features.pkl",
    ]
    checksums = {}
    for f in legacy_files:
        if f.exists():
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            checksums[str(f.relative_to(PROJECT_ROOT))] = h
    return checksums


def generate_report(
    df: pd.DataFrame,
    processing_time_s: float,
    pre_checksums: dict,
    post_checksums: dict,
):
    """Generate LABEL_GENERATION_REPORT.md."""

    total = len(df)

    # Class distribution
    class_dist = df["risk_label_v2"].value_counts()
    class_pct = df["risk_label_v2"].value_counts(normalize=True) * 100

    # Site-wise distribution
    site_class = pd.crosstab(df["site_id"], df["risk_label_v2"], margins=True)

    # Confidence distribution
    conf_dist = df["label_confidence"].value_counts()
    conf_pct = df["label_confidence"].value_counts(normalize=True) * 100

    # Completeness distribution
    comp_dist = df["data_completeness"].value_counts()
    comp_pct = df["data_completeness"].value_counts(normalize=True) * 100

    # Per-parameter state distribution
    param_state_counts = {}
    for param in ALL_RISK_PARAMS:
        col = f"{param}_state"
        if col in df.columns:
            param_state_counts[param] = df[col].value_counts().to_dict()

    # Temporal partition counts
    df_ts = pd.to_datetime(df["timestamp_utc"])
    count_2024 = (df_ts.dt.year == 2024).sum()
    count_2025 = (df_ts.dt.year == 2025).sum()

    # Verify legacy integrity
    legacy_ok = pre_checksums == post_checksums

    lines = []
    lines.append("# Label Generation Report: `operational_risk_labels_v2.0`")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append(f"**Label Version**: `{LABEL_VERSION}`")
    lines.append(f"**Specification**: `docs/LABEL_SPEC_v2.md`")
    lines.append(f"**Processing Time**: {processing_time_s:.1f} seconds")
    lines.append(f"**Output**: `data/labeled/operational_risk_labels_v2.parquet`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 1. Total records
    lines.append("## 1. Records Processed")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|---|---:|")
    lines.append(f"| **Total Records** | **{total:,}** |")
    lines.append(f"| 2024 Partition | {count_2024:,} |")
    lines.append(f"| 2025 Partition | {count_2025:,} |")
    lines.append("")

    # 2. Class distribution
    lines.append("## 2. Risk Label Distribution")
    lines.append("")
    lines.append("| Label | Count | Percentage |")
    lines.append("|---|---:|---:|")
    for label in ["SAFE", "WARNING", "CRITICAL", "INSUFFICIENT_DATA"]:
        c = class_dist.get(label, 0)
        p = class_pct.get(label, 0.0)
        lines.append(f"| **{label}** | {c:,} | {p:.2f}% |")
    lines.append("")

    # 3. Site-wise distribution
    lines.append("## 3. Site-Wise Label Distribution")
    lines.append("")

    # Format site_class as markdown table
    headers = ["Site"] + [str(col) for col in site_class.columns]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---:"] * len(headers)) + " |")
    for idx, row in site_class.iterrows():
        row_vals = [f"**{idx}**"] + [f"{int(val):,}" if pd.notna(val) else "0" for val in row]
        lines.append("| " + " | ".join(row_vals) + " |")
    lines.append("")

    # 4. Confidence distribution
    lines.append("## 4. Label Confidence Distribution")
    lines.append("")
    lines.append("| Confidence | Count | Percentage |")
    lines.append("|---|---:|---:|")
    for level in ["HIGH", "MODERATE", "LOW", "UNRELIABLE"]:
        c = conf_dist.get(level, 0)
        p = conf_pct.get(level, 0.0)
        lines.append(f"| **{level}** | {c:,} | {p:.2f}% |")
    lines.append("")

    # 5. Data completeness
    lines.append("## 5. Data Completeness Distribution")
    lines.append("")
    lines.append("| Completeness | Count | Percentage |")
    lines.append("|---|---:|---:|")
    for level in ["FULL", "PARTIAL", "DEGRADED", "INSUFFICIENT"]:
        c = comp_dist.get(level, 0)
        p = comp_pct.get(level, 0.0)
        lines.append(f"| **{level}** | {c:,} | {p:.2f}% |")
    lines.append("")

    # 6. Parameter state distribution
    lines.append("## 6. Per-Parameter State Distribution")
    lines.append("")
    for param, states in param_state_counts.items():
        lines.append(f"### {param}")
        lines.append("")
        lines.append("| State | Count | Percentage |")
        lines.append("|---|---:|---:|")
        for state_name in ["NORMAL", "ELEVATED", "EXTREME", "MISSING", "SENSOR_ARTIFACT", "INSTRUMENT_LIMIT"]:
            c = states.get(state_name, 0)
            p = c / total * 100
            lines.append(f"| {state_name} | {c:,} | {p:.2f}% |")
        lines.append("")

    # 7. Legacy integrity
    lines.append("## 7. Legacy Artifact Integrity")
    lines.append("")
    if legacy_ok:
        lines.append("> [!NOTE]")
        lines.append("> All legacy files verified unchanged. Pre- and post-generation SHA-256 checksums match.")
    else:
        lines.append("> [!CAUTION]")
        lines.append("> **INTEGRITY VIOLATION**: Legacy file checksums changed during generation!")
    lines.append("")
    lines.append("| File | Status |")
    lines.append("|---|---|")
    for f in pre_checksums:
        status = "✅ Unchanged" if pre_checksums[f] == post_checksums.get(f) else "❌ MODIFIED"
        lines.append(f"| `{f}` | {status} |")
    lines.append("")

    # 8. Anomaly independence verification
    lines.append("## 8. Anomaly Independence Verification")
    lines.append("")
    lines.append("The label generation pipeline does **not** read, reference, or depend on:")
    lines.append("- `anomaly_status` (legacy Model 1 output)")
    lines.append("- `water_risk_score` (legacy heuristic score)")
    lines.append("- `final_status` (legacy pseudo-label)")
    lines.append("- `final_risk_score` (legacy coupled score)")
    lines.append("")
    lines.append("Labels are derived exclusively from sensor observations and site-specific ecological thresholds.")
    lines.append("")

    report_text = "\n".join(lines)
    REPORT_FILE.write_text(report_text)
    print(f"  Report saved: {REPORT_FILE}")


def main():
    print("=" * 70)
    print("  OPERATIONAL RISK LABELS v2.0 — Label Generation Pipeline")
    print("=" * 70)
    print(f"  Label Version: {LABEL_VERSION}")
    print(f"  Specification: docs/LABEL_SPEC_v2.md")
    print()

    # 1. Verify legacy files before processing
    print("Step 1: Checksumming legacy artifacts (pre-generation)...")
    pre_checksums = verify_legacy_untouched()
    print(f"  Tracked {len(pre_checksums)} legacy files")

    # 2. Load canonical datasets
    print("\nStep 2: Loading canonical datasets...")
    t_start = time.time()

    df_2024 = pd.read_parquet(INPUT_2024)
    print(f"  2024: {len(df_2024):,} records")

    df_2025 = pd.read_parquet(INPUT_2025)
    print(f"  2025: {len(df_2025):,} records")

    # Combine
    df = pd.concat([df_2024, df_2025], ignore_index=True)
    print(f"  Combined: {len(df):,} records")
    del df_2024, df_2025  # free memory

    # Keep only needed columns
    available_preserve = [c for c in PRESERVE_COLS if c in df.columns]
    df = df[available_preserve].copy()

    # 3. Generate labels
    print("\nStep 3: Generating labels...")
    df = generate_labels(df)

    # 4. Select output columns
    output_cols = available_preserve + STATE_COLS + LABEL_COLS
    output_cols = [c for c in output_cols if c in df.columns]
    df_output = df[output_cols]

    # 5. Write output
    print("\nStep 4: Writing labeled dataset...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df_output.to_parquet(OUTPUT_FILE, engine="pyarrow", compression="snappy", index=False)
    file_size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    print(f"  Output: {OUTPUT_FILE}")
    print(f"  Size: {file_size_mb:.1f} MB")
    print(f"  Records: {len(df_output):,}")

    t_end = time.time()
    processing_time = t_end - t_start

    # 6. Verify legacy files after processing
    print("\nStep 5: Checksumming legacy artifacts (post-generation)...")
    post_checksums = verify_legacy_untouched()
    if pre_checksums == post_checksums:
        print("  ✅ All legacy files unchanged")
    else:
        print("  ❌ WARNING: Legacy files were modified!")

    # 7. Generate report
    print("\nStep 6: Generating label generation report...")
    generate_report(df_output, processing_time, pre_checksums, post_checksums)

    # 8. Summary
    print("\n" + "=" * 70)
    print("  GENERATION COMPLETE")
    print("=" * 70)

    class_dist = df_output["risk_label_v2"].value_counts()
    for label in ["SAFE", "WARNING", "CRITICAL", "INSUFFICIENT_DATA"]:
        c = class_dist.get(label, 0)
        p = c / len(df_output) * 100
        print(f"  {label:20s}: {c:>10,} ({p:5.2f}%)")

    print(f"\n  Processing time: {processing_time:.1f}s")
    print(f"  Label version: {LABEL_VERSION}")
    print()


if __name__ == "__main__":
    main()
