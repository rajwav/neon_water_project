# NEON Water Intelligence Platform - Site-Specific Baseline Profile

**Version:** 1.0
**Status:** Draft — Awaiting Approval
**Data Source:** 2024 Training Partition (`temporal_2024.parquet`) EXCLUSIVELY
**Governing Documents:** NEON Data Quality Protocols, Strategy C Hybrid Label Design

## Executive Summary

The purpose of this site-specific baseline profile is to document the natural ecological characteristics and parameter statistics for each monitoring site within the NEON Water Intelligence Platform. Because water quality parameters vary dramatically across different aquatic ecosystems, understanding what constitutes a "normal" baseline for a specific site is critical for accurate anomaly detection and label generation. This document establishes these localized baselines, which inform the design of site-aware thresholds and prevent the misclassification of natural ecological variations as anomalies.

## Methodology

The statistics presented in this document were computed exclusively from the 2024 training partition (`temporal_2024.parquet`). The calculations reflect all non-null observations for each parameter at each site during this period. The percentile ranges (e.g., p1, p99) and central tendencies (mean, median) are used to characterize the typical operating range and variability of the parameters, providing a robust statistical foundation for site-specific thresholds.

## Site Profiles

### ARIK — Arikaree River, Colorado
**Domain:** Domain 10
**Ecosystem Classification:** Wadeable Stream, Semi-arid Prairie
**Positions:** 101.100.100 (upstream), 102.100.100 (downstream)
**Total 2024 records:** 1,054,080

#### Key Parameter Statistics
| Parameter | Mean | Median (p50) | p1 | p99 | Std Dev | Notes |
|---|---|---|---|---|---|---|
| pH | 7.92 | 8.04 | 6.73 | 8.30 | 0.47 | |
| DO | 7.40 | 8.13 | 0.09 | 10.85 | 2.88 | High variability |
| Turbidity | 12.73 | 1.61 | - | 225.02 | 86.77 | p90=14.22, p95=32.30; highly skewed |
| SpCond | 362.14 | 519.04 | -0.16 | 737.06 | 267.11 | Bimodal |
| fDOM | 45.88 | 55.16 | -1.89 | 121.58 | 34.67 | Downstream only |
| Chlorophyll | - | - | - | - | - | NOT INSTALLED |
| Sensor Depth | - | - | - | - | - | NOT INSTALLED |

**Ecological Interpretation:** Semi-arid intermittent stream. Experiences seasonal drying. Conductance is naturally very high (>500 µS/cm). Dissolved Oxygen drops significantly during the summer due to warm water and low flow. Turbidity is highly variable, largely driven by flash storm events.
**Data Quality Notes:** SpCond shows bimodal behavior; seasonal dry periods have very high conductance, but there are sensor failures near 0. fDOM has 52.55% missing data and ~50% QF failure.

---

### BARC — Barco Lake, Florida
**Domain:** Domain 03
**Ecosystem Classification:** Core Lake, Subtropical Blackwater
**Position:** 103.100.100 (lake buoy)
**Total 2024 records:** 105,408

#### Key Parameter Statistics
| Parameter | Mean | Median (p50) | p1 | p99 | Std Dev | Notes |
|---|---|---|---|---|---|---|
| pH | 5.66 | 5.66 | 5.26 | 5.95 | 0.17 | Naturally Acidic |
| DO | 7.14 | 7.04 | 0.00 | 10.11 | 1.47 | Anoxia at depth |
| Turbidity | 0.94 | 0.94 | 0.00 | 2.83 | 0.96 | Extremely clear |
| SpCond | 27.00 | 26.91 | 25.86 | 28.84 | 1.05 | Very low, stable |
| fDOM | -20.05 | 14.38 | - | 19.72 | - | p25=11.41, p75=16.42 |
| Chlorophyll | 2.89 | 2.56 | 0.58 | 9.54 | 2.12 | Oligotrophic |
| Sensor Depth | 0.38 | 0.20 | - | 3.60 | - | |

**Ecological Interpretation:** Naturally acidic (pH 5.0-6.0) tannin-rich blackwater lake. SpCond is very low and stable. Turbidity is very low. DO drops to near zero during thermal stratification. Oligotrophic environment with low algal biomass.
**Data Quality Notes:** fDOM mean is negative due to a 25.66% QF failure rate producing large negative artifacts. Valid fDOM range is typically 11-20 QSU.

---

### BIGC — Upper Big Creek, California
**Domain:** Domain 17
**Ecosystem Classification:** Wadeable Stream, Mountain Forest
**Positions:** 111.100.100 (upstream), 112.100.100 (downstream)
**Total 2024 records:** 1,054,080

#### Key Parameter Statistics
| Parameter | Mean | Median (p50) | p1 | p99 | Std Dev | Notes |
|---|---|---|---|---|---|---|
| pH | 7.22 | 7.25 | 7.03 | 7.75 | 0.69 | Tight, slightly alkaline |
| DO | 9.31 | 9.40 | 6.83 | 11.54 | 2.67 | Well-oxygenated |
| Turbidity | 2.49 | 1.99 | 1.21 | 6.79 | 52.16 | Generally clear |
| SpCond | 145.15 | 139.38 | 67.63 | 217.56 | 48.25 | Seasonal variation |
| fDOM | 24.52 | 22.32 | 12.96 | 71.03 | 25.11 | Downstream only |
| Chlorophyll | - | - | - | - | - | NOT INSTALLED |
| Sensor Depth | - | - | - | - | - | NOT INSTALLED |

**Ecological Interpretation:** Well-oxygenated mountain stream covered by a forest canopy. Baseline turbidity is low, with rare large outliers from storm events. SpCond is moderate and varies seasonally.
**Data Quality Notes:** fDOM has 58.18% missing data.

---

### BLDE — Blacktail Deer Creek, Wyoming
**Domain:** Domain 12
**Ecosystem Classification:** Wadeable Stream, Alpine Snowmelt
**Positions:** 101.100.100 (upstream), 102.100.100 (downstream)
**Total 2024 records:** 1,054,080

#### Key Parameter Statistics
| Parameter | Mean | Median (p50) | p1 | p99 | Std Dev | Notes |
|---|---|---|---|---|---|---|
| pH | 7.75 | 7.77 | 7.35 | 8.03 | 0.44 | Slightly alkaline |
| DO | 10.20 | 10.83 | 7.51 | 11.69 | 2.47 | Cold water |
| Turbidity | 3.01 | 2.33 | 1.36 | 11.67 | 30.42 | Low baseline |
| SpCond | 106.77 | 111.64 | 56.14 | 133.95 | 19.46 | Low/moderate |
| fDOM | 46.96 | 43.78 | 27.02 | 90.17 | 24.58 | Downstream only |
| Chlorophyll | - | - | - | - | - | NOT INSTALLED |
| Sensor Depth | - | - | - | - | - | NOT INSTALLED |

**Ecological Interpretation:** Cold alpine stream fed by snowmelt, resulting in high dissolved oxygen capacity. Turbidity has a low baseline with rare storm spikes. Conductance is low to moderate due to snowmelt dilution. Seasonally ice-covered.
**Data Quality Notes:** fDOM has 51.55% missing data.

---

### BLUE — Blue River, Oklahoma
**Domain:** Domain 11
**Ecosystem Classification:** Wadeable Stream, Great Plains
**Position:** 112.100.100 (downstream only)
**Total 2024 records:** 527,040

#### Key Parameter Statistics
| Parameter | Mean | Median (p50) | p1 | p99 | Std Dev | Notes |
|---|---|---|---|---|---|---|
| pH | 8.07 | 8.04 | 7.88 | 8.88 | 0.76 | Slightly alkaline |
| DO | 10.03 | 9.81 | 7.16 | 13.07 | 3.40 | Warm-water stream |
| Turbidity | 6.65 | 3.43 | -0.77 | 31.25 | 66.11 | Moderately turbid |
| SpCond | 582.16 | 575.05 | 488.25 | 664.49 | 46.50 | High ionic content |
| fDOM | 5.61 | 4.42 | -0.37 | 32.05 | 6.02 | Low fDOM |
| Chlorophyll | - | - | - | - | - | NOT INSTALLED |
| Sensor Depth | - | - | - | - | - | NOT INSTALLED |

**Ecological Interpretation:** Great Plains warm-water stream. Conductance is naturally high. Turbidity is moderate, influenced by storm events. 
**Data Quality Notes:** High rate of data loss (~59% missing for most parameters due to seasonal sensor failures). fDOM has a 70.61% QF failure rate.

## Cross-Site Comparison Table

The following table highlights the dramatic differences in expected parameter ranges across the monitored sites:

| Site | pH (median) | SpCond (median) | DO (median) | Turbidity (p99) |
|---|---|---|---|---|
| ARIK | 8.04 | 519.04 | 8.13 | 225.02 |
| BARC | 5.66 | 26.91 | 7.04 | 2.83 |
| BIGC | 7.25 | 139.38 | 9.40 | 6.79 |
| BLDE | 7.77 | 111.64 | 10.83 | 11.67 |
| BLUE | 8.04 | 575.05 | 9.81 | 31.25 |

*(Note: Ranges vary dramatically. For example, a SpCond of 500 would be a massive anomaly at BARC, but normal at ARIK.)*

## Parameter Availability Matrix

| Parameter | ARIK | BARC | BIGC | BLDE | BLUE |
|---|---|---|---|---|---|
| pH | Yes | Yes | Yes | Yes | Yes |
| DO | Yes | Yes | Yes | Yes | Yes |
| Turbidity | Yes | Yes | Yes | Yes | Yes |
| SpCond | Yes | Yes | Yes | Yes | Yes |
| fDOM | Yes (DS only) | Yes | Yes (DS only) | Yes (DS only) | Yes |
| Chlorophyll | **No** | Yes | **No** | **No** | **No** |
| Sensor Depth| **No** | Yes | **No** | **No** | **No** |

*(DS = Downstream)*

## Implications for Label Design

1. **Site-Specific Baselines are Essential:** Ecosystems naturally differ vastly in their parameter baselines. What is a typical condition at one site (e.g., pH ~5.6 at BARC) would be a critical anomaly at another site (e.g., pH <7.0 at BLUE). Models and label thresholds must be tuned locally.
2. **Global Max Normalization Was Wrong:** Applying a single, global normalization strategy (like normalizing by global maximum) suppresses the dynamic range of data at cleaner or more dilute sites, distorting the signal and rendering anomalies mathematically undetectable at those sites.
3. **Strategy C Hybrid Thresholds:** Because baseline values vary widely and some sensors exhibit severe systemic noise (e.g., negative fDOM artifacts at BARC, bimodal SpCond at ARIK), the Strategy C approach must employ custom thresholds tailored to each site's unique statistical profile. Thresholds must account for both biological reality and site-specific sensor reliability.
4. **Handling Missing Parameters:** Due to the Parameter Availability Matrix showing significant structural differences, pipelines must handle `NOT INSTALLED` sensors gracefully per site. Missing data interpolation or imputation must respect these boundaries rather than attempting to fill values for non-existent sensors.
