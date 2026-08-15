"""
Site-specific threshold definitions for operational_risk_labels_v2.0.

Every threshold is classified as:
  LIT = Literature-referenced (EPA, WHO, state criteria)
  PCT = Percentile-derived from 2024 training partition

See: docs/LABEL_SPEC_v2.md for full specification and citations.
"""

from typing import Dict, Optional, Tuple

# ── Parameter state constants ──────────────────────────────────────
NORMAL = "NORMAL"
ELEVATED = "ELEVATED"
EXTREME = "EXTREME"
MISSING = "MISSING"
SENSOR_ARTIFACT = "SENSOR_ARTIFACT"
INSTRUMENT_LIMIT = "INSTRUMENT_LIMIT"

# ── Risk label constants ───────────────────────────────────────────
SAFE = "SAFE"
WARNING = "WARNING"
CRITICAL = "CRITICAL"
INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

# ── Data completeness constants ────────────────────────────────────
COMPLETENESS_FULL = "FULL"
COMPLETENESS_PARTIAL = "PARTIAL"
COMPLETENESS_DEGRADED = "DEGRADED"
COMPLETENESS_INSUFFICIENT = "INSUFFICIENT"

# ── Label confidence constants ─────────────────────────────────────
CONFIDENCE_HIGH = "HIGH"
CONFIDENCE_MODERATE = "MODERATE"
CONFIDENCE_LOW = "LOW"
CONFIDENCE_UNRELIABLE = "UNRELIABLE"

# ── Label version ─────────────────────────────────────────────────
LABEL_VERSION = "operational_risk_labels_v2.0"

# ── Installed parameters per site/position ─────────────────────────
# Maps (site_id, sensor_position) -> list of installed parameters
INSTALLED_PARAMS: Dict[Tuple[str, str], list] = {
    ("ARIK", "101.100.100"): ["ph", "dissolved_oxygen", "turbidity", "specific_conductance"],
    ("ARIK", "102.100.100"): ["ph", "dissolved_oxygen", "turbidity", "specific_conductance", "fdom"],
    ("BARC", "103.100.100"): ["ph", "dissolved_oxygen", "turbidity", "specific_conductance", "fdom", "chlorophyll"],
    ("BIGC", "111.100.100"): ["ph", "dissolved_oxygen", "turbidity", "specific_conductance"],
    ("BIGC", "112.100.100"): ["ph", "dissolved_oxygen", "turbidity", "specific_conductance", "fdom"],
    ("BLDE", "101.100.100"): ["ph", "dissolved_oxygen", "turbidity", "specific_conductance"],
    ("BLDE", "102.100.100"): ["ph", "dissolved_oxygen", "turbidity", "specific_conductance", "fdom"],
    ("BLUE", "112.100.100"): ["ph", "dissolved_oxygen", "turbidity", "specific_conductance", "fdom"],
}


def _get_installed_count(site_id: str, sensor_position: str) -> int:
    """Return number of installed parameters for a site/position."""
    key = (site_id, sensor_position)
    return len(INSTALLED_PARAMS.get(key, []))


def _get_installed_params(site_id: str, sensor_position: str) -> list:
    """Return list of installed parameters for a site/position."""
    key = (site_id, sensor_position)
    return INSTALLED_PARAMS.get(key, [])


# ── Per-parameter, per-site threshold definitions ──────────────────
# Format: { site_id: { "normal": (lo, hi), "elevated": (lo, hi), ... } }
# For asymmetric parameters (pH, SpCond), elevated and extreme are
# defined as pairs of (low_range, high_range).

# pH Thresholds — Source: LIT (EPA 440/5-88-001)
PH_THRESHOLDS: Dict[str, Dict] = {
    "ARIK": {"normal": (7.0, 8.5), "elevated_lo": (6.5, 7.0), "elevated_hi": (8.5, 9.0), "extreme_below": 6.5, "extreme_above": 9.0, "source": "LIT"},
    "BARC": {"normal": (4.5, 6.5), "elevated_lo": (4.0, 4.5), "elevated_hi": (6.5, 7.0), "extreme_below": 4.0, "extreme_above": 7.0, "source": "LIT"},
    "BIGC": {"normal": (6.5, 8.0), "elevated_lo": (6.0, 6.5), "elevated_hi": (8.0, 8.5), "extreme_below": 6.0, "extreme_above": 8.5, "source": "LIT"},
    "BLDE": {"normal": (7.0, 8.5), "elevated_lo": (6.5, 7.0), "elevated_hi": (8.5, 9.0), "extreme_below": 6.5, "extreme_above": 9.0, "source": "LIT"},
    "BLUE": {"normal": (7.5, 9.0), "elevated_lo": (7.0, 7.5), "elevated_hi": (9.0, 9.5), "extreme_below": 7.0, "extreme_above": 9.5, "source": "LIT"},
}

# Dissolved Oxygen Thresholds — Source: LIT (EPA 440/5-86-003)
DO_THRESHOLDS: Dict[str, Dict] = {
    "ARIK": {"normal": (5.0, 14.0), "elevated_lo": (3.0, 5.0), "elevated_hi": (14.0, 18.0), "extreme_below": 3.0, "extreme_above": 18.0, "source": "LIT"},
    "BARC": {"normal": (4.0, 12.0), "elevated_lo": (2.0, 4.0), "elevated_hi": (12.0, 16.0), "extreme_below": 2.0, "extreme_above": 16.0, "source": "LIT"},
    "BIGC": {"normal": (6.5, 13.0), "elevated_lo": (5.0, 6.5), "elevated_hi": (13.0, 16.0), "extreme_below": 5.0, "extreme_above": 16.0, "source": "LIT"},
    "BLDE": {"normal": (7.0, 13.0), "elevated_lo": (5.0, 7.0), "elevated_hi": (13.0, 16.0), "extreme_below": 5.0, "extreme_above": 16.0, "source": "LIT"},
    "BLUE": {"normal": (5.0, 14.0), "elevated_lo": (3.0, 5.0), "elevated_hi": (14.0, 18.0), "extreme_below": 3.0, "extreme_above": 18.0, "source": "LIT"},
}

# Turbidity Thresholds — Source: LIT+PCT
TURBIDITY_THRESHOLDS: Dict[str, Dict] = {
    "ARIK": {"normal_max": 15.0, "elevated_max": 225.0, "source": "PCT"},
    "BARC": {"normal_max": 2.0, "elevated_max": 10.0, "source": "LIT+PCT"},
    "BIGC": {"normal_max": 5.0, "elevated_max": 50.0, "source": "PCT"},
    "BLDE": {"normal_max": 6.0, "elevated_max": 50.0, "source": "PCT"},
    "BLUE": {"normal_max": 18.0, "elevated_max": 100.0, "source": "PCT"},
}

# Specific Conductance Thresholds — Source: PCT
SPCOND_THRESHOLDS: Dict[str, Dict] = {
    "ARIK": {"normal": (0.0, 750.0), "elevated_lo": (None, None), "elevated_hi": (750.0, 1000.0), "extreme_below": None, "extreme_above": 1000.0, "source": "PCT"},
    "BARC": {"normal": (20.0, 30.0), "elevated_lo": (15.0, 20.0), "elevated_hi": (30.0, 40.0), "extreme_below": 15.0, "extreme_above": 40.0, "source": "PCT"},
    "BIGC": {"normal": (50.0, 220.0), "elevated_lo": (30.0, 50.0), "elevated_hi": (220.0, 280.0), "extreme_below": 30.0, "extreme_above": 280.0, "source": "PCT"},
    "BLDE": {"normal": (50.0, 140.0), "elevated_lo": (30.0, 50.0), "elevated_hi": (140.0, 180.0), "extreme_below": 30.0, "extreme_above": 180.0, "source": "PCT"},
    "BLUE": {"normal": (450.0, 670.0), "elevated_lo": (350.0, 450.0), "elevated_hi": (670.0, 800.0), "extreme_below": 350.0, "extreme_above": 800.0, "source": "PCT"},
}

# fDOM Thresholds — Source: PCT
FDOM_THRESHOLDS: Dict[str, Dict] = {
    "ARIK": {"normal_max": 105.0, "elevated_max": 130.0, "source": "PCT"},
    "BARC": {"normal": (8.0, 20.0), "elevated_lo": (5.0, 8.0), "elevated_hi": (20.0, 30.0), "extreme_below": 5.0, "extreme_above": 30.0, "source": "PCT"},
    "BIGC": {"normal_max": 56.0, "elevated_max": 80.0, "source": "PCT"},
    "BLDE": {"normal_max": 85.0, "elevated_max": 100.0, "source": "PCT"},
    "BLUE": {"normal_max": 17.0, "elevated_max": 40.0, "source": "PCT"},
}

# Chlorophyll Thresholds — Source: LIT (WHO/EPA trophic state) — BARC only
CHLOROPHYLL_THRESHOLDS: Dict[str, Dict] = {
    "BARC": {"normal_max": 8.0, "elevated_max": 25.0, "source": "LIT"},
}

# ── Instrument operating limits (from src/data/constants.py) ───────
INSTRUMENT_RANGES: Dict[str, Tuple[float, float]] = {
    "ph": (0.0, 14.0),
    "dissolved_oxygen": (0.0, 30.0),
    "turbidity": (0.0, 4000.0),
    "specific_conductance": (0.0, 50000.0),
    "chlorophyll": (0.0, 500.0),
    "fdom": (0.0, 500.0),
}

# ── Sensor artifact detection thresholds ───────────────────────────
# These identify values that are almost certainly electronic artifacts,
# not real environmental measurements.
SENSOR_ARTIFACT_RULES: Dict[str, Dict] = {
    # Negative turbidity = optical sensor interference
    "turbidity": {"artifact_below": 0.0},
    # Negative fDOM = electronic artifact
    "fdom": {"artifact_below": 0.0},
    # Near-zero SpCond at ARIK when expected >400 = sensor exposure
    # (handled specially in the labeler for ARIK)
}
