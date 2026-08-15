"""
Sensor constants, parameter mappings, and instrument operating limits.

CRITICAL SCIENTIFIC PRINCIPLE:
The instrument ranges defined herein represent hardware manufacturer physical 
operating bounds (e.g. YSI EXO2 Sonde specifications) used solely to detect 
sensor electrical malfunction, clipping, or unphysical artifacts.
They are EXPLICITLY NOT ecological, regulatory, or water-safety thresholds.
"""

from typing import Dict, Tuple

# Core 6 Water Quality Parameters + Environmental Metadata
SENSOR_PARAMETERS = [
    "ph",
    "dissolved_oxygen",
    "turbidity",
    "specific_conductance",
    "chlorophyll",
    "fdom",
    "sensor_depth",
]

# Raw NEON CSV Column -> Canonical Column Name
NEON_COLUMN_MAP: Dict[str, str] = {
    "startDateTime": "raw_timestamp",
    "pH": "ph",
    "dissolvedOxygen": "dissolved_oxygen",
    "turbidity": "turbidity",
    "specificConductance": "specific_conductance",
    "chlorophyll": "chlorophyll",
    "fDOM": "fdom",
    "sensorDepth": "sensor_depth",
}

# Raw NEON Quality Flag Column -> Canonical QF Column Name
NEON_QF_MAP: Dict[str, str] = {
    "pHFinalQF": "ph_qf",
    "dissolvedOxygenFinalQF": "dissolved_oxygen_qf",
    "turbidityFinalQF": "turbidity_qf",
    "specificCondFinalQF": "specific_conductance_qf",
    "chlorophyllFinalQF": "chlorophyll_qf",
    "fDOMFinalQF": "fdom_qf",
    "sensorDepthFinalQF": "sensor_depth_qf",
}

# Canonical Parameter -> Associated Canonical QF Column
PARAM_TO_QF_MAP: Dict[str, str] = {
    "ph": "ph_qf",
    "dissolved_oxygen": "dissolved_oxygen_qf",
    "turbidity": "turbidity_qf",
    "specific_conductance": "specific_conductance_qf",
    "chlorophyll": "chlorophyll_qf",
    "fdom": "fdom_qf",
    "sensor_depth": "sensor_depth_qf",
}

# Manufacturer Hardware Operating Limits: (Min, Max)
# Used ONLY to flag OUT_OF_INSTRUMENT_RANGE.
# Source: NEON WAQ In-situ Sensor Specifications / YSI EXO2 Documentation
INSTRUMENT_RANGES: Dict[str, Tuple[float, float]] = {
    "ph": (0.0, 14.0),                      # Standard pH scale
    "dissolved_oxygen": (0.0, 30.0),        # mg/L (EXO optical DO limit)
    "turbidity": (0.0, 4000.0),             # FNU (EXO turbidity sensor limit)
    "specific_conductance": (0.0, 50000.0), # uS/cm (Freshwater conductance upper limit)
    "chlorophyll": (0.0, 500.0),            # ug/L (EXO total algae chlorophyll limit)
    "fdom": (0.0, 500.0),                   # QSU (EXO fDOM optical sensor limit)
    "sensor_depth": (0.0, 100.0),           # meters
}

# Canonical Parameter Display Units
PARAMETER_UNITS: Dict[str, str] = {
    "ph": "pH units",
    "dissolved_oxygen": "mg/L",
    "turbidity": "FNU",
    "specific_conductance": "µS/cm",
    "chlorophyll": "µg/L",
    "fdom": "QSU",
    "sensor_depth": "m",
}
