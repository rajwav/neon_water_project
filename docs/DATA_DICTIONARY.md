# Canonical Data Dictionary: NEON Water Quality Observations

Version: 2.0  
Product Code: NEON DP1.20288.001 (Water Quality In-situ Sonde Measurements)  
Sensor Suite: YSI EXO2 Multi-Parameter Sonde  
Storage Format: Columnar Apache Parquet with Snappy Compression  

---

## 1. Provenance & Dataset Information

- **Data Source**: National Ecological Observatory Network (NEON), USA.
- **Data Product**: DP1.20288.001 (Water Quality).
- **Time Resolution**: Instantaneous in-situ measurements (nominal 1-minute sampling interval).
- **Temporal Span**: January 1, 2024 to December 31, 2025 (UTC).
- **Aquatic Sites Monitored**:
  - `ARIK`: Arikaree River, Colorado, USA (Wadeable Stream, Domain 10).
  - `BARC`: Barco Lake, Florida, USA (Core Lake, Domain 03).
  - `BIGC`: Upper Big Creek, California, USA (Wadeable Stream, Domain 17).
  - `BLDE`: Blacktail Deer Creek, Wyoming, USA (Wadeable Stream, Domain 12).
  - `BLUE`: Blue River, Oklahoma, USA (Wadeable Stream, Domain 11).

---

## 2. Canonical Observation Schema

Every canonical record conforms to the following schema definition:

| Column Name | Data Type | Nullable | Unit | Description |
|---|---|---|---|---|
| `observation_id` | `string` | No | - | Deterministic SHA-256 hash (24 chars) of `site_id:sensor_position:timestamp_utc`. |
| `site_id` | `string` | No | - | NEON 4-letter site identifier (`ARIK`, `BARC`, `BIGC`, `BLDE`, `BLUE`). |
| `sensor_position` | `string` | No | - | Horizontal.Vertical.Pass index (e.g. `101.100.100`, `102.100.100`, `103.100.100`, `111.100.100`, `112.100.100`). |
| `raw_timestamp` | `string` | No | - | Original unmodified timestamp string from raw NEON CSV (`startDateTime`). |
| `timestamp_utc` | `timestamp[us, tz=UTC]` | No | UTC | Standardized ISO-8601 UTC timestamp. |
| `sensor_depth` | `float64` | Yes | `m` | Measured sensor depth beneath water surface. |
| `sensor_depth_qf` | `Int64` | Yes | - | Original NEON sensor depth quality flag (`sensorDepthFinalQF`: 0=pass, 1=fail). |
| `ph` | `float64` | Yes | `pH units` | Water acidity / alkalinity on standard pH scale. |
| `ph_qf` | `Int64` | Yes | - | Original NEON pH quality flag (`pHFinalQF`: 0=pass, 1=fail). |
| `dissolved_oxygen` | `float64` | Yes | `mg/L` | Optical dissolved oxygen concentration in water. |
| `dissolved_oxygen_qf`| `Int64` | Yes | - | Original NEON DO quality flag (`dissolvedOxygenFinalQF`: 0=pass, 1=fail). |
| `turbidity` | `float64` | Yes | `FNU` | Water clarity / suspended particulate scattering. |
| `turbidity_qf` | `Int64` | Yes | - | Original NEON turbidity quality flag (`turbidityFinalQF`: 0=pass, 1=fail). |
| `specific_conductance`| `float64` | Yes | `µS/cm` | Electrical conductivity normalized to 25°C. |
| `specific_conductance_qf`| `Int64` | Yes | - | Original NEON conductivity quality flag (`specificCondFinalQF`: 0=pass, 1=fail). |
| `chlorophyll` | `float64` | Yes | `µg/L` | Total chlorophyll-a fluorescence indicator of algae/biomass. |
| `chlorophyll_qf` | `Int64` | Yes | - | Original NEON chlorophyll quality flag (`chlorophyllFinalQF`: 0=pass, 1=fail). |
| `fdom` | `float64` | Yes | `QSU` | Fluorescent Dissolved Organic Matter (quinine sulfate units). |
| `fdom_qf` | `Int64` | Yes | - | Original NEON fDOM quality flag (`fDOMFinalQF`: 0=pass, 1=fail). |
| `ph_flag_range` | `bool` | No | - | True if `ph` is outside manufacturer operating bounds. |
| `ph_flag_qf` | `bool` | No | - | True if `ph_qf == 1`. |
| `dissolved_oxygen_flag_range` | `bool` | No | - | True if `dissolved_oxygen` is outside manufacturer operating bounds. |
| `dissolved_oxygen_flag_qf` | `bool` | No | - | True if `dissolved_oxygen_qf == 1`. |
| `turbidity_flag_range` | `bool` | No | - | True if `turbidity` is outside manufacturer operating bounds. |
| `turbidity_flag_qf` | `bool` | No | - | True if `turbidity_qf == 1`. |
| `specific_conductance_flag_range`| `bool` | No | - | True if `specific_conductance` is outside manufacturer operating bounds. |
| `specific_conductance_flag_qf` | `bool` | No | - | True if `specific_conductance_qf == 1`. |
| `chlorophyll_flag_range` | `bool` | No | - | True if `chlorophyll` is outside manufacturer operating bounds. |
| `chlorophyll_flag_qf` | `bool` | No | - | True if `chlorophyll_qf == 1`. |
| `fdom_flag_range` | `bool` | No | - | True if `fdom` is outside manufacturer operating bounds. |
| `fdom_flag_qf` | `bool` | No | - | True if `fdom_qf == 1`. |
| `sensor_depth_flag_range` | `bool` | No | - | True if `sensor_depth` is outside manufacturer operating bounds. |
| `sensor_depth_flag_qf` | `bool` | No | - | True if `sensor_depth_qf == 1`. |
| `is_duplicate` | `bool` | No | - | True if another record shares identical `site_id`, `sensor_position`, and `timestamp_utc`. |
| `source_file` | `string` | No | - | Exact raw CSV file name from which the record originated. |

---

## 3. Instrument Operating Limits

> [!IMPORTANT]
> **Scientific Notice on Operating Limits**:
> These thresholds represent hardware manufacturer specifications for the YSI EXO2 Sonde. They are strictly utilized to flag electronic clipping or sensor failure (`OUT_OF_INSTRUMENT_RANGE`). They are **NOT** ecological, regulatory, drinking water, or environmental safety thresholds.

| Parameter | Manufacturer Min | Manufacturer Max | Unit |
|---|---|---|---|
| **pH** | `0.0` | `14.0` | `pH units` |
| **Dissolved Oxygen** | `0.0` | `30.0` | `mg/L` |
| **Turbidity** | `0.0` | `4000.0` | `FNU` |
| **Specific Conductance** | `0.0` | `50000.0` | `µS/cm` |
| **Chlorophyll a** | `0.0` | `500.0` | `µg/L` |
| **fDOM** | `0.0` | `500.0` | `QSU` |
| **Sensor Depth** | `0.0` | `100.0` | `m` |

---

## 4. Quality Flag Definitions & Policies

1. **NEON QF Preservation (`*FinalQF`)**:
   - `0`: Passed automated NEON quality checks.
   - `1`: Failed automated NEON quality check (e.g. sensor drift, biofouling, step test).
   - `NaN / None`: No quality test performed.
   - **Policy**: Measurements with `FinalQF == 1` are **never deleted**. They are preserved in the dataset and flagged (`*_flag_qf = True`) so subsequent research and modelling layers can audit or filter explicitly.
2. **Instrument Range Check (`*_flag_range`)**:
   - `True`: Measurement lies outside physical sonde sensor limits (`OUT_OF_INSTRUMENT_RANGE`). Numerical value is preserved without clipping.
   - `False`: Measurement is within normal sonde hardware operating boundaries.
3. **Duplicate Record Flag (`is_duplicate`)**:
   - `True`: Multiple records exist for the same station, sensor position, and timestamp. All instances are preserved.
   - `False`: Unique observation timestamp.

---

## 5. Temporal Partitions

- **`data/canonical/temporal_2024.parquet`**: All validated records where `timestamp_utc.year == 2024`.
- **`data/canonical/temporal_2025.parquet`**: All validated records where `timestamp_utc.year == 2025`.
- **`data/validated/neon_observations.parquet`**: Full multi-year validated dataset across all 5 monitoring sites.
