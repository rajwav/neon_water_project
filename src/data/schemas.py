"""
Pydantic schemas and type contracts for canonical water-quality observations and audit reports.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SensorQualityFlag(str, Enum):
    """Granular quality classification applied per sensor measurement."""
    VALID = "VALID"
    NEON_QF_FAIL = "NEON_QF_FAIL"
    OUT_OF_INSTRUMENT_RANGE = "OUT_OF_INSTRUMENT_RANGE"
    MISSING_VALUE = "MISSING_VALUE"
    DUPLICATE_RECORD = "DUPLICATE_RECORD"


class DataQualityLevel(str, Enum):
    """Aggregate data quality assessment for the observation window."""
    GOOD = "GOOD"
    SUSPECT = "SUSPECT"
    DEGRADED = "DEGRADED"
    INVALID = "INVALID"


class CanonicalObservation(BaseModel):
    """
    Canonical water-quality observation schema.
    Represents a verified, normalized, and provenance-tracked observation point.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    # Identifiers
    observation_id: str = Field(
        ...,
        description="Deterministic unique ID computed from site_id, sensor_position, and timestamp_utc"
    )
    site_id: str = Field(
        ...,
        description="NEON 4-letter site code (e.g., ARIK, BARC, BIGC, BLDE, BLUE)"
    )
    sensor_position: str = Field(
        ...,
        description="NEON horizontal.vertical.pass position code (e.g., 101.100.100)"
    )

    # Timestamps (ISO-8601 UTC)
    raw_timestamp: str = Field(
        ...,
        description="Original unmodified timestamp string from the source file"
    )
    timestamp_utc: datetime = Field(
        ...,
        description="Normalized UTC datetime"
    )

    # Core 6 Water Quality Measurements & Original NEON Quality Flags
    ph: Optional[float] = Field(default=None, description="pH (standard units)")
    ph_qf: Optional[int] = Field(default=None, description="Original pHFinalQF (0, 1, or None)")

    dissolved_oxygen: Optional[float] = Field(default=None, description="Dissolved Oxygen (mg/L)")
    dissolved_oxygen_qf: Optional[int] = Field(default=None, description="Original dissolvedOxygenFinalQF")

    turbidity: Optional[float] = Field(default=None, description="Turbidity (FNU / NTU)")
    turbidity_qf: Optional[int] = Field(default=None, description="Original turbidityFinalQF")

    specific_conductance: Optional[float] = Field(default=None, description="Specific Conductance (uS/cm)")
    specific_conductance_qf: Optional[int] = Field(default=None, description="Original specificCondFinalQF")

    chlorophyll: Optional[float] = Field(default=None, description="Chlorophyll a (ug/L)")
    chlorophyll_qf: Optional[int] = Field(default=None, description="Original chlorophyllFinalQF")

    fdom: Optional[float] = Field(default=None, description="Fluorescent DOM (QSU)")
    fdom_qf: Optional[int] = Field(default=None, description="Original fDOMFinalQF")

    # Sensor Depth & Flag
    sensor_depth: Optional[float] = Field(default=None, description="Sensor depth (m)")
    sensor_depth_qf: Optional[int] = Field(default=None, description="Original sensorDepthFinalQF")

    # Quality & Duplicate Audit Attributes
    quality_flags: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Applied sensor quality flags per parameter"
    )
    is_duplicate: bool = Field(
        default=False,
        description="True if an identical site, position, and timestamp exists"
    )

    # Lineage / Provenance
    source_file: str = Field(
        ...,
        description="Basename of the original raw NEON CSV data package file"
    )


class BatchIngestionAuditReport(BaseModel):
    """Structured audit report capturing full row accountability and provenance."""
    timestamp_generated: datetime = Field(default_factory=datetime.utcnow)
    total_raw_files_processed: int
    total_raw_records_read: int
    total_canonical_records_written: int
    total_excluded_records: int
    exclusion_breakdown: Dict[str, int]
    site_record_counts: Dict[str, int]
    temporal_2024_records: int
    temporal_2025_records: int
    duplicate_records_detected: int
    arik_accountability: Dict[str, int]
    quality_flag_summary: Dict[str, Dict[str, int]]
    raw_files_sha256_verified: bool
