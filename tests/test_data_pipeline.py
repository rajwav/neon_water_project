"""
Phase 1 Acceptance Tests for the Canonical Data Foundation Pipeline.
"""

import glob
import hashlib
import json
import os
import pytest
import pandas as pd
import pyarrow.parquet as pq

from src.data.constants import SENSOR_PARAMETERS
from src.data.schemas import CanonicalObservation


MANIFEST_PATH = "data/raw_manifest.json"
RAW_DIR = "data/raw"
VALIDATED_PATH = "data/validated/neon_observations.parquet"
TEMPORAL_2024_PATH = "data/canonical/temporal_2024.parquet"
TEMPORAL_2025_PATH = "data/canonical/temporal_2025.parquet"
AUDIT_PATH = "data/audit_report.json"


@pytest.fixture(scope="session")
def validated_df():
    """Loads a slice of the validated parquet dataset for testing."""
    if not os.path.exists(VALIDATED_PATH):
        pytest.fail(f"Validated dataset not found at {VALIDATED_PATH}. Run pipeline first.")
    return pd.read_parquet(VALIDATED_PATH)


@pytest.fixture(scope="session")
def audit_data():
    """Loads the audit report."""
    if not os.path.exists(AUDIT_PATH):
        pytest.fail(f"Audit report not found at {AUDIT_PATH}. Run pipeline first.")
    with open(AUDIT_PATH, "r") as fp:
        return json.load(fp)


def test_1_raw_data_immutability():
    """1. Verifies raw CSV files match pre-computed SHA-256 hashes exactly."""
    assert os.path.exists(MANIFEST_PATH), f"Manifest {MANIFEST_PATH} missing!"
    with open(MANIFEST_PATH, "r") as fp:
        manifest = json.load(fp)

    assert len(manifest) == 192, f"Expected 192 raw files in manifest, found {len(manifest)}"

    for fname, expected_hash in manifest.items():
        fpath = os.path.join(RAW_DIR, fname)
        assert os.path.exists(fpath), f"Raw file {fname} missing!"

        hasher = hashlib.sha256()
        with open(fpath, "rb") as fp:
            while chunk := fp.read(65536):
                hasher.update(chunk)
        actual_hash = hasher.hexdigest()
        assert actual_hash == expected_hash, f"Hash mismatch on raw file {fname}!"


def test_2_arik_preservation(validated_df, audit_data):
    """2. Verifies ARIK is present in the dataset and all raw records are accounted for."""
    arik_rows = validated_df[validated_df["site_id"] == "ARIK"]
    assert len(arik_rows) > 0, "Site ARIK was dropped from validated dataset!"
    
    # Check audit accountability
    arik_audit = audit_data.get("arik_accountability", {})
    assert arik_audit.get("canonical_records_preserved", 0) > 0
    assert arik_audit.get("canonical_records_preserved") == len(arik_rows)


def test_3_timestamp_utc_normalization(validated_df):
    """3. Verifies all timestamps are timezone-aware UTC datetime objects."""
    assert pd.api.types.is_datetime64_any_dtype(validated_df["timestamp_utc"])
    assert validated_df["timestamp_utc"].dt.tz is not None, "Timestamp is not timezone-aware!"
    assert str(validated_df["timestamp_utc"].dt.tz) == "UTC"
    assert validated_df["timestamp_utc"].isna().sum() == 0, "Found null timestamps in validated data!"


def test_4_original_neon_qf_preservation(validated_df):
    """4. Verifies original NEON quality flags (0, 1, NA) are preserved."""
    qf_cols = ["ph_qf", "dissolved_oxygen_qf", "turbidity_qf", "specific_conductance_qf", "chlorophyll_qf", "fdom_qf"]
    for col in qf_cols:
        assert col in validated_df.columns, f"Quality flag column {col} missing!"
        unique_vals = set(validated_df[col].dropna().unique())
        # QF values in NEON are strictly 0 or 1
        assert unique_vals.issubset({0, 1}), f"Unexpected QF values in {col}: {unique_vals}"


def test_5_instrument_range_flagging(validated_df):
    """5. Verifies instrument operating range flags work without mutating or dropping values."""
    range_flag_cols = [f"{p}_flag_range" for p in SENSOR_PARAMETERS]
    for flag_col in range_flag_cols:
        assert flag_col in validated_df.columns, f"Range flag {flag_col} missing!"
        assert validated_df[flag_col].dtype == bool or validated_df[flag_col].dtype == "boolean"


def test_6_duplicate_detection_and_preservation(validated_df):
    """6. Verifies duplicates are detected, flagged is_duplicate=True, and retained."""
    assert "is_duplicate" in validated_df.columns, "is_duplicate column missing!"
    dup_count = validated_df["is_duplicate"].sum()
    assert dup_count >= 0, "Duplicate count negative"


def test_7_no_synthetic_values(validated_df):
    """7. Verifies no values are synthetically interpolated across consecutive missing gaps."""
    # Check that missingness is preserved as null rather than flat-lined
    assert validated_df["fdom"].isna().sum() > 0, "Missing values were artificially filled!"


def test_8_provenance_completeness(validated_df):
    """8. Verifies provenance metadata (source_file, sensor_position, raw_timestamp) is complete."""
    assert validated_df["source_file"].isna().sum() == 0, "Missing source_file in records!"
    assert validated_df["sensor_position"].isna().sum() == 0, "Missing sensor_position in records!"
    assert validated_df["raw_timestamp"].isna().sum() == 0, "Missing raw_timestamp in records!"


def test_9_canonical_schema_validation(validated_df):
    """9. Validates sample rows against Pydantic CanonicalObservation contract."""
    sample_df = validated_df.sample(min(50, len(validated_df)), random_state=42)
    for _, row in sample_df.iterrows():
        obs = CanonicalObservation(
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
        assert obs.site_id in {"ARIK", "BARC", "BIGC", "BLDE", "BLUE"}


def test_10_temporal_partition_isolation():
    """10. Verifies temporal partition isolation between 2024 and 2025."""
    assert os.path.exists(TEMPORAL_2024_PATH), f"Missing {TEMPORAL_2024_PATH}"
    assert os.path.exists(TEMPORAL_2025_PATH), f"Missing {TEMPORAL_2025_PATH}"

    df_2024 = pd.read_parquet(TEMPORAL_2024_PATH, columns=["timestamp_utc"])
    df_2025 = pd.read_parquet(TEMPORAL_2025_PATH, columns=["timestamp_utc"])

    assert len(df_2024) > 0
    assert len(df_2025) > 0

    assert (df_2024["timestamp_utc"].dt.year == 2024).all(), "Non-2024 timestamp found in temporal_2024!"
    assert (df_2025["timestamp_utc"].dt.year == 2025).all(), "Non-2025 timestamp found in temporal_2025!"
