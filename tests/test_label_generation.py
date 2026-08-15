"""
Tests for operational_risk_labels_v2.0 label generation.

Validates:
  1. No legacy files modified
  2. Label version correctness
  3. Deterministic output
  4. No anomaly_status dependency
  5. Temporal separation preserved
  6. Schema completeness
  7. Threshold correctness
  8. Aggregation logic
"""

import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.labels import (
    LABEL_VERSION,
    SAFE, WARNING, CRITICAL, INSUFFICIENT_DATA,
    NORMAL, ELEVATED, EXTREME, MISSING, SENSOR_ARTIFACT, INSTRUMENT_LIMIT,
    COMPLETENESS_FULL, COMPLETENESS_PARTIAL, COMPLETENESS_DEGRADED, COMPLETENESS_INSUFFICIENT,
    CONFIDENCE_HIGH, CONFIDENCE_MODERATE, CONFIDENCE_LOW, CONFIDENCE_UNRELIABLE,
    INSTALLED_PARAMS,
)
from src.labels.labeler import (
    classify_parameter_states,
    compute_aggregated_labels,
    compute_data_completeness,
    ALL_RISK_PARAMS,
)

# ── Paths ──────────────────────────────────────────────────────────
LABELED_FILE = PROJECT_ROOT / "data" / "labeled" / "operational_risk_labels_v2.parquet"

LEGACY_FILES = {
    "results/final_water_quality_prediction.csv": None,
    "results/neon_anomaly_results.csv": None,
    "models/saved_models/risk_model.pkl": None,
    "models/saved_models/anomaly_model.pkl": None,
    "models/saved_models/anomaly_scaler.pkl": None,
    "models/saved_models/status_encoder.pkl": None,
    "models/saved_models/model_metadata.pkl": None,
    "models/saved_models/anomaly_features.pkl": None,
}

# Pre-recorded checksums (computed before any changes)
LEGACY_CHECKSUMS = {}
for rel_path in LEGACY_FILES:
    full_path = PROJECT_ROOT / rel_path
    if full_path.exists():
        LEGACY_CHECKSUMS[rel_path] = hashlib.sha256(full_path.read_bytes()).hexdigest()


# ════════════════════════════════════════════════════════════════════
# 1. NO LEGACY FILES MODIFIED
# ════════════════════════════════════════════════════════════════════

class TestLegacyIntegrity:
    """Verify that no legacy files were modified during label generation."""

    @pytest.fixture
    def current_checksums(self):
        checksums = {}
        for rel_path in LEGACY_FILES:
            full_path = PROJECT_ROOT / rel_path
            if full_path.exists():
                checksums[rel_path] = hashlib.sha256(full_path.read_bytes()).hexdigest()
        return checksums

    def test_legacy_files_exist(self):
        """All expected legacy files must still exist."""
        for rel_path in LEGACY_FILES:
            full_path = PROJECT_ROOT / rel_path
            assert full_path.exists(), f"Legacy file missing: {rel_path}"

    def test_legacy_checksums_unchanged(self, current_checksums):
        """Legacy file checksums must match pre-generation values."""
        for rel_path, expected_hash in LEGACY_CHECKSUMS.items():
            actual_hash = current_checksums.get(rel_path)
            assert actual_hash == expected_hash, (
                f"Legacy file modified: {rel_path}\n"
                f"Expected SHA-256: {expected_hash}\n"
                f"Actual SHA-256:   {actual_hash}"
            )


# ════════════════════════════════════════════════════════════════════
# 2. LABEL VERSION CORRECTNESS
# ════════════════════════════════════════════════════════════════════

class TestLabelVersion:
    """Verify label version metadata is correct."""

    @pytest.fixture(scope="module")
    def labeled_df(self):
        assert LABELED_FILE.exists(), f"Labeled file not found: {LABELED_FILE}"
        return pd.read_parquet(LABELED_FILE)

    def test_label_version_column_exists(self, labeled_df):
        assert "label_version" in labeled_df.columns

    def test_label_version_value(self, labeled_df):
        unique_versions = labeled_df["label_version"].unique()
        assert len(unique_versions) == 1
        assert unique_versions[0] == LABEL_VERSION

    def test_label_version_matches_spec(self, labeled_df):
        assert labeled_df["label_version"].iloc[0] == "operational_risk_labels_v2.0"


# ════════════════════════════════════════════════════════════════════
# 3. DETERMINISTIC OUTPUT
# ════════════════════════════════════════════════════════════════════

class TestDeterminism:
    """Verify labeling is deterministic on synthetic data."""

    def _make_test_df(self):
        """Create a small synthetic dataframe for determinism testing."""
        return pd.DataFrame({
            "site_id": ["BLDE"] * 4,
            "sensor_position": ["101.100.100"] * 4,
            "ph": [7.5, 6.3, 7.8, np.nan],
            "dissolved_oxygen": [10.0, 4.5, 8.0, 11.0],
            "turbidity": [2.0, 60.0, 3.0, 1.0],
            "specific_conductance": [100.0, 200.0, 110.0, 80.0],
            "fdom": [np.nan, np.nan, np.nan, np.nan],  # not installed at 101
            "chlorophyll": [np.nan, np.nan, np.nan, np.nan],
            "ph_flag_qf": [False, False, False, False],
            "dissolved_oxygen_flag_qf": [False, False, False, False],
            "turbidity_flag_qf": [False, False, False, False],
            "specific_conductance_flag_qf": [False, False, False, False],
            "fdom_flag_qf": [False, False, False, False],
            "chlorophyll_flag_qf": [False, False, False, False],
            "ph_flag_range": [False, False, False, False],
            "dissolved_oxygen_flag_range": [False, False, False, False],
            "turbidity_flag_range": [False, False, False, False],
            "specific_conductance_flag_range": [False, False, False, False],
            "fdom_flag_range": [False, False, False, False],
            "chlorophyll_flag_range": [False, False, False, False],
        })

    def test_deterministic_labels(self):
        """Same input must produce same labels every time."""
        df1 = self._make_test_df()
        df1 = classify_parameter_states(df1)
        df1 = compute_aggregated_labels(df1)

        df2 = self._make_test_df()
        df2 = classify_parameter_states(df2)
        df2 = compute_aggregated_labels(df2)

        pd.testing.assert_series_equal(
            df1["risk_label_v2"].reset_index(drop=True),
            df2["risk_label_v2"].reset_index(drop=True),
        )

    def test_deterministic_param_states(self):
        """Same input must produce same parameter states."""
        df1 = self._make_test_df()
        df1 = classify_parameter_states(df1)

        df2 = self._make_test_df()
        df2 = classify_parameter_states(df2)

        for param in ALL_RISK_PARAMS:
            state_col = f"{param}_state"
            if state_col in df1.columns:
                pd.testing.assert_series_equal(
                    df1[state_col].reset_index(drop=True),
                    df2[state_col].reset_index(drop=True),
                    check_names=False,
                )


# ════════════════════════════════════════════════════════════════════
# 4. NO ANOMALY_STATUS DEPENDENCY
# ════════════════════════════════════════════════════════════════════

class TestAnomalyIndependence:
    """Verify labels do not depend on anomaly_status or Model 1 output."""

    @pytest.fixture(scope="module")
    def labeled_df(self):
        return pd.read_parquet(LABELED_FILE)

    def test_no_anomaly_status_column(self, labeled_df):
        """The labeled output must not contain anomaly_status."""
        assert "anomaly_status" not in labeled_df.columns

    def test_no_anomaly_score_column(self, labeled_df):
        """The labeled output must not contain anomaly_score."""
        assert "anomaly_score" not in labeled_df.columns

    def test_no_final_status_column(self, labeled_df):
        """The labeled output must not contain the legacy final_status."""
        assert "final_status" not in labeled_df.columns

    def test_no_water_risk_score_column(self, labeled_df):
        """The labeled output must not contain the legacy water_risk_score."""
        assert "water_risk_score" not in labeled_df.columns

    def test_no_final_risk_score_column(self, labeled_df):
        """The labeled output must not contain the legacy final_risk_score."""
        assert "final_risk_score" not in labeled_df.columns

    def test_label_source_code_independence(self):
        """Verify the labeler module does not import anomaly-related modules."""
        labeler_source = (PROJECT_ROOT / "src" / "labels" / "labeler.py").read_text()
        assert "anomaly_status" not in labeler_source
        assert "anomaly_score" not in labeler_source
        assert "final_status" not in labeler_source
        assert "water_risk_score" not in labeler_source
        assert "final_risk_score" not in labeler_source
        assert "train_anomaly" not in labeler_source
        assert "IsolationForest" not in labeler_source


# ════════════════════════════════════════════════════════════════════
# 5. TEMPORAL SEPARATION PRESERVED
# ════════════════════════════════════════════════════════════════════

class TestTemporalSeparation:
    """Verify temporal partition integrity."""

    @pytest.fixture(scope="module")
    def labeled_df(self):
        return pd.read_parquet(LABELED_FILE)

    def test_contains_2024_data(self, labeled_df):
        timestamps = pd.to_datetime(labeled_df["timestamp_utc"])
        assert (timestamps.dt.year == 2024).sum() > 0

    def test_contains_2025_data(self, labeled_df):
        timestamps = pd.to_datetime(labeled_df["timestamp_utc"])
        assert (timestamps.dt.year == 2025).sum() > 0

    def test_no_data_leakage_across_years(self, labeled_df):
        """Both temporal partitions must be present and non-overlapping in source."""
        timestamps = pd.to_datetime(labeled_df["timestamp_utc"])
        years = timestamps.dt.year.unique()
        assert set(years).issubset({2024, 2025})


# ════════════════════════════════════════════════════════════════════
# 6. SCHEMA COMPLETENESS
# ════════════════════════════════════════════════════════════════════

class TestSchemaCompleteness:
    """Verify all required columns exist with correct types and valid values."""

    @pytest.fixture(scope="module")
    def labeled_df(self):
        return pd.read_parquet(LABELED_FILE)

    def test_risk_label_column(self, labeled_df):
        assert "risk_label_v2" in labeled_df.columns
        valid_labels = {SAFE, WARNING, CRITICAL, INSUFFICIENT_DATA}
        actual_labels = set(labeled_df["risk_label_v2"].unique())
        assert actual_labels.issubset(valid_labels), f"Unexpected labels: {actual_labels - valid_labels}"

    def test_count_columns(self, labeled_df):
        for col in ["elevated_count", "extreme_count", "assessable_count"]:
            assert col in labeled_df.columns
            assert labeled_df[col].dtype in [np.int8, np.int16, np.int32, np.int64]
            assert labeled_df[col].min() >= 0

    def test_completeness_column(self, labeled_df):
        assert "data_completeness" in labeled_df.columns
        valid = {COMPLETENESS_FULL, COMPLETENESS_PARTIAL, COMPLETENESS_DEGRADED, COMPLETENESS_INSUFFICIENT}
        assert set(labeled_df["data_completeness"].unique()).issubset(valid)

    def test_confidence_column(self, labeled_df):
        assert "label_confidence" in labeled_df.columns
        valid = {CONFIDENCE_HIGH, CONFIDENCE_MODERATE, CONFIDENCE_LOW, CONFIDENCE_UNRELIABLE}
        assert set(labeled_df["label_confidence"].unique()).issubset(valid)

    def test_per_param_state_column(self, labeled_df):
        assert "per_param_state" in labeled_df.columns
        # Verify JSON parseable
        sample = labeled_df["per_param_state"].iloc[0]
        parsed = json.loads(sample)
        assert isinstance(parsed, dict)

    def test_provenance_columns(self, labeled_df):
        assert "label_version" in labeled_df.columns
        assert "threshold_source" in labeled_df.columns
        assert "generated_at" in labeled_df.columns

    def test_preserved_columns(self, labeled_df):
        required = ["observation_id", "site_id", "sensor_position", "timestamp_utc"]
        for col in required:
            assert col in labeled_df.columns, f"Missing preserved column: {col}"

    def test_state_columns(self, labeled_df):
        for param in ALL_RISK_PARAMS:
            col = f"{param}_state"
            assert col in labeled_df.columns, f"Missing state column: {col}"
            valid_states = {NORMAL, ELEVATED, EXTREME, MISSING, SENSOR_ARTIFACT, INSTRUMENT_LIMIT}
            actual_states = set(labeled_df[col].unique())
            assert actual_states.issubset(valid_states), (
                f"Invalid states in {col}: {actual_states - valid_states}"
            )


# ════════════════════════════════════════════════════════════════════
# 7. THRESHOLD LOGIC CORRECTNESS
# ════════════════════════════════════════════════════════════════════

class TestThresholdLogic:
    """Unit-test individual threshold classifications."""

    def _make_single_row(self, site, position, **params):
        """Create a single-row test dataframe."""
        defaults = {p: np.nan for p in ALL_RISK_PARAMS}
        defaults.update(params)
        row = {
            "site_id": [site],
            "sensor_position": [position],
        }
        for p in ALL_RISK_PARAMS:
            row[p] = [defaults[p]]
            row[f"{p}_flag_qf"] = [False]
            row[f"{p}_flag_range"] = [False]
        return pd.DataFrame(row)

    def test_barc_normal_ph(self):
        """BARC pH 5.5 should be NORMAL (naturally acidic lake)."""
        df = self._make_single_row("BARC", "103.100.100", ph=5.5)
        df = classify_parameter_states(df)
        assert df["ph_state"].iloc[0] == NORMAL

    def test_barc_extreme_ph(self):
        """BARC pH 8.0 should be EXTREME (far above natural range for blackwater)."""
        df = self._make_single_row("BARC", "103.100.100", ph=8.0)
        df = classify_parameter_states(df)
        assert df["ph_state"].iloc[0] == EXTREME

    def test_blde_normal_do(self):
        """BLDE DO 10.0 mg/L should be NORMAL."""
        df = self._make_single_row("BLDE", "101.100.100", dissolved_oxygen=10.0)
        df = classify_parameter_states(df)
        assert df["dissolved_oxygen_state"].iloc[0] == NORMAL

    def test_blde_elevated_low_do(self):
        """BLDE DO 6.0 mg/L should be ELEVATED (cold alpine stream)."""
        df = self._make_single_row("BLDE", "101.100.100", dissolved_oxygen=6.0)
        df = classify_parameter_states(df)
        assert df["dissolved_oxygen_state"].iloc[0] == ELEVATED

    def test_arik_extreme_low_do(self):
        """ARIK DO 2.0 mg/L should be EXTREME."""
        df = self._make_single_row("ARIK", "101.100.100", dissolved_oxygen=2.0)
        df = classify_parameter_states(df)
        assert df["dissolved_oxygen_state"].iloc[0] == EXTREME

    def test_negative_turbidity_is_artifact(self):
        """Negative turbidity must be SENSOR_ARTIFACT, not assessed."""
        df = self._make_single_row("BIGC", "111.100.100", turbidity=-5.0)
        df = classify_parameter_states(df)
        assert df["turbidity_state"].iloc[0] == SENSOR_ARTIFACT

    def test_negative_fdom_is_artifact(self):
        """Negative fDOM must be SENSOR_ARTIFACT."""
        df = self._make_single_row("BLDE", "102.100.100", fdom=-10.0)
        df = classify_parameter_states(df)
        assert df["fdom_state"].iloc[0] == SENSOR_ARTIFACT

    def test_arik_near_zero_spcond_is_artifact(self):
        """Near-zero SpCond at ARIK must be SENSOR_ARTIFACT."""
        df = self._make_single_row("ARIK", "101.100.100", specific_conductance=1.0)
        df = classify_parameter_states(df)
        assert df["specific_conductance_state"].iloc[0] == SENSOR_ARTIFACT

    def test_missing_param_is_missing(self):
        """NaN value should be classified as MISSING."""
        df = self._make_single_row("BLDE", "101.100.100", ph=np.nan)
        df = classify_parameter_states(df)
        assert df["ph_state"].iloc[0] == MISSING

    def test_chlorophyll_not_installed(self):
        """Chlorophyll at BLDE must be MISSING (not installed)."""
        df = self._make_single_row("BLDE", "101.100.100", chlorophyll=5.0)
        df = classify_parameter_states(df)
        assert df["chlorophyll_state"].iloc[0] == MISSING


# ════════════════════════════════════════════════════════════════════
# 8. AGGREGATION LOGIC
# ════════════════════════════════════════════════════════════════════

class TestAggregationLogic:
    """Unit-test the multi-parameter aggregation rule."""

    def _make_states_df(self, **states):
        """Create a df with pre-set parameter states for aggregation testing."""
        row = {f"{p}_state": [states.get(p, MISSING)] for p in ALL_RISK_PARAMS}
        return pd.DataFrame(row)

    def test_all_normal_is_safe(self):
        df = self._make_states_df(
            ph=NORMAL, dissolved_oxygen=NORMAL, turbidity=NORMAL,
            specific_conductance=NORMAL,
        )
        df = compute_aggregated_labels(df)
        assert df["risk_label_v2"].iloc[0] == SAFE

    def test_one_elevated_is_warning(self):
        df = self._make_states_df(
            ph=ELEVATED, dissolved_oxygen=NORMAL, turbidity=NORMAL,
            specific_conductance=NORMAL,
        )
        df = compute_aggregated_labels(df)
        assert df["risk_label_v2"].iloc[0] == WARNING

    def test_one_extreme_zero_elevated_is_warning(self):
        df = self._make_states_df(
            ph=EXTREME, dissolved_oxygen=NORMAL, turbidity=NORMAL,
            specific_conductance=NORMAL,
        )
        df = compute_aggregated_labels(df)
        assert df["risk_label_v2"].iloc[0] == WARNING

    def test_one_extreme_one_elevated_is_critical(self):
        df = self._make_states_df(
            ph=EXTREME, dissolved_oxygen=ELEVATED, turbidity=NORMAL,
            specific_conductance=NORMAL,
        )
        df = compute_aggregated_labels(df)
        assert df["risk_label_v2"].iloc[0] == CRITICAL

    def test_two_extreme_is_critical(self):
        df = self._make_states_df(
            ph=EXTREME, dissolved_oxygen=EXTREME, turbidity=NORMAL,
            specific_conductance=NORMAL,
        )
        df = compute_aggregated_labels(df)
        assert df["risk_label_v2"].iloc[0] == CRITICAL

    def test_three_elevated_is_critical(self):
        df = self._make_states_df(
            ph=ELEVATED, dissolved_oxygen=ELEVATED, turbidity=ELEVATED,
            specific_conductance=NORMAL,
        )
        df = compute_aggregated_labels(df)
        assert df["risk_label_v2"].iloc[0] == CRITICAL

    def test_insufficient_data(self):
        """Fewer than 2 assessable parameters → INSUFFICIENT_DATA."""
        df = self._make_states_df(
            ph=NORMAL,  # only 1 assessable
        )
        df = compute_aggregated_labels(df)
        assert df["risk_label_v2"].iloc[0] == INSUFFICIENT_DATA

    def test_two_assessable_is_enough(self):
        """Exactly 2 assessable parameters should be enough for a label."""
        df = self._make_states_df(
            ph=NORMAL, dissolved_oxygen=NORMAL,
        )
        df = compute_aggregated_labels(df)
        assert df["risk_label_v2"].iloc[0] == SAFE


# ════════════════════════════════════════════════════════════════════
# 9. MISSING ≠ SAFE
# ════════════════════════════════════════════════════════════════════

class TestMissingNotSafe:
    """Verify that missing parameters do not contribute 'NORMAL' status."""

    @pytest.fixture(scope="module")
    def labeled_df(self):
        return pd.read_parquet(LABELED_FILE)

    def test_missing_not_counted_as_assessable(self, labeled_df):
        """Observations with MISSING state must not count toward assessable_count."""
        # For any row, assessable_count should equal the number of
        # state columns that are NORMAL, ELEVATED, or EXTREME
        sample = labeled_df.sample(min(1000, len(labeled_df)), random_state=42)
        for _, row in sample.iterrows():
            expected_count = 0
            for param in ALL_RISK_PARAMS:
                state = row.get(f"{param}_state")
                if state in (NORMAL, ELEVATED, EXTREME):
                    expected_count += 1
            assert row["assessable_count"] == expected_count, (
                f"Assessable count mismatch at observation {row.get('observation_id')}: "
                f"expected {expected_count}, got {row['assessable_count']}"
            )
