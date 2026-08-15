"""
=============================================================================
SIH 2026 NEON Water Intelligence Platform
USGS Multi-Domain Water Quality Harmonization Pipeline (Phase 2)
=============================================================================

This module processes large-scale discrete Physical/Chemical and Biological
water quality datasets from the USGS Water Quality Portal (WQP):
  1. data/raw/resultphyschem.csv (445,998 rows, 81 columns)
  2. data/raw/biologicalresult.csv (445,998 rows, 156 columns)

Processing Pipeline:
  - Chunked streaming ingestion to maintain low memory footprint (<300MB RAM).
  - Robust value cleaning & below-detection-limit (BDL) 1/2 MDL imputation.
  - Long-to-wide pivoting of physical & chemical characteristics.
  - Biological & taxonomic feature extraction (taxa count, bioassay flags, trophic levels).
  - Deterministic composite merge on (MonitoringLocationIdentifier, ActivityStartDate, ActivityIdentifier).
  - Derived biogeochemical feature engineering (N:P ratios, sediment coupling, WQI).
  - Export to optimized columnar parquet: data/processed/usgs_water_quality.parquet
"""

import os
import sys
import re
import argparse
import logging
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("usgs_pipeline")

# ── Parameter Harmonization Mapping ────────────────────────────────
PHYSCHEM_PARAM_MAP = {
    # pH & Acidity
    "pH": "ph",
    "pH, lab": "ph",
    "Acidity, (H+)": "acidity_h_plus",
    "Alkalinity": "alkalinity_mg_l",
    "Alkalinity, total": "alkalinity_mg_l",
    
    # Temperature
    "Temperature, water": "temperature_c",
    "Temperature, air": "temperature_air_c",
    
    # Clarity & Particulates
    "Turbidity": "turbidity_fnu",
    "Turbidity, field": "turbidity_fnu",
    "Suspended Sediment Concentration (SSC)": "suspended_sediment_conc_mg_l",
    "Total suspended solids": "total_suspended_solids_mg_l",
    "Volatile suspended solids": "volatile_suspended_solids_mg_l",
    
    # Conductivity & Salinity
    "Specific conductance": "specific_conductance_us_cm",
    "Specific conductance, field": "specific_conductance_us_cm",
    "Total dissolved solids": "total_dissolved_solids_mg_l",
    
    # Dissolved Oxygen
    "Dissolved oxygen (DO)": "dissolved_oxygen_mg_l",
    "Dissolved oxygen": "dissolved_oxygen_mg_l",
    
    # Nitrogen Suite
    "Nitrate": "nitrate_mg_l",
    "Nitrite": "nitrite_mg_l",
    "Inorganic nitrogen (nitrate and nitrite)": "inorganic_nitrogen_mg_l",
    "Ammonia and ammonium": "ammonia_ammonium_mg_l",
    "Organic Nitrogen": "organic_nitrogen_mg_l",
    "Kjeldahl nitrogen": "kjeldahl_nitrogen_mg_l",
    "Nitrogen, mixed forms (NH3), (NH4), organic, (NO2) and (NO3)": "total_mixed_nitrogen_mg_l",
    
    # Phosphorus Suite
    "Orthophosphate": "orthophosphate_mg_l",
    "Phosphorus": "total_phosphorus_mg_l",
    "Phosphate": "total_phosphorus_mg_l",
    
    # Optical & Organic Carbon
    "UV 254": "uv_254_abs",
    "Absorption spectral slope (Sag)": "absorption_spectral_slope",
    "Absorbance at 280 nanometers": "abs_280_nm",
    "Absorbance at 370 nanometers": "abs_370_nm",
    
    # Hydrology & Physical
    "Height, gage": "gage_height_ft",
    "Stream flow, instantaneous": "stream_flow_cfs",
    "Stream flow": "stream_flow_cfs",
    "Stream width measure": "stream_width_ft",
}

KEY_MERGE_COLS = [
    "MonitoringLocationIdentifier",
    "ActivityStartDate",
    "ActivityIdentifier",
]


def clean_measure_value(val: Any, detection_limit: Any = None) -> Optional[float]:
    """
    Robust numeric measurement parser and Below-Detection-Limit (BDL) handler.
    If value is '< 0.05', returns 0.05 * 0.5 (1/2 MDL).
    """
    if pd.isna(val):
        if pd.notna(detection_limit):
            try:
                return float(detection_limit) * 0.5
            except (ValueError, TypeError):
                pass
        return None

    val_str = str(val).strip()
    
    # Censored Below Detection Limit '< X'
    if val_str.startswith("<"):
        try:
            nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", val_str)
            if nums:
                return float(nums[0]) * 0.5
        except (ValueError, IndexError):
            return None
            
    # Standard numbers or numbers with trailing qualifier asterisks
    try:
        nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", val_str)
        if nums:
            return float(nums[0])
    except (ValueError, IndexError):
        pass

    return None


def process_physchem_dataset(
    filepath: str,
    chunksize: int = 50000,
    limit_rows: Optional[int] = None,
) -> pd.DataFrame:
    """
    Stream and pivot physical/chemical observations from long format to wide observation records.
    """
    logger.info(f"Ingesting Physical/Chemical dataset: {filepath}")
    
    target_chars = set(PHYSCHEM_PARAM_MAP.keys())
    chunks = []
    rows_read = 0

    cols_to_load = [
        "MonitoringLocationIdentifier",
        "ActivityStartDate",
        "ActivityIdentifier",
        "ActivityStartTime/Time",
        "ActivityLocation/LatitudeMeasure",
        "ActivityLocation/LongitudeMeasure",
        "OrganizationFormalName",
        "HydrologicCondition",
        "HydrologicEvent",
        "CharacteristicName",
        "ResultMeasureValue",
        "DetectionQuantitationLimitMeasure/MeasureValue",
    ]

    for chunk in pd.read_csv(
        filepath,
        chunksize=chunksize,
        usecols=lambda c: c in cols_to_load,
        low_memory=False,
        nrows=limit_rows,
    ):
        rows_read += len(chunk)
        logger.info(f"  [PhysChem] Processed {rows_read:,} raw rows...")

        # Filter to target water quality parameters
        filtered = chunk[chunk["CharacteristicName"].isin(target_chars)].copy()
        if filtered.empty:
            continue

        # Standardize parameter column name
        filtered["param_col"] = filtered["CharacteristicName"].map(PHYSCHEM_PARAM_MAP)

        # Parse numeric measurement value
        det_limits = (
            filtered["DetectionQuantitationLimitMeasure/MeasureValue"]
            if "DetectionQuantitationLimitMeasure/MeasureValue" in filtered.columns
            else None
        )
        if det_limits is not None:
            filtered["clean_value"] = [
                clean_measure_value(v, dl)
                for v, dl in zip(filtered["ResultMeasureValue"], det_limits)
            ]
        else:
            filtered["clean_value"] = filtered["ResultMeasureValue"].apply(clean_measure_value)

        # Drop invalid NaN numeric rows
        filtered = filtered.dropna(subset=["clean_value"])
        if filtered.empty:
            continue

        chunks.append(filtered)

        if limit_rows and rows_read >= limit_rows:
            break

    if not chunks:
        logger.warning("No physical/chemical records matched the target criteria.")
        return pd.DataFrame()

    df_filtered = pd.concat(chunks, ignore_index=True)
    logger.info(f"Total relevant Physical/Chemical measurements: {len(df_filtered):,}")

    # Deduplicate multiple readings for same activity and parameter by taking mean
    agg_df = (
        df_filtered.groupby(KEY_MERGE_COLS + ["param_col"])["clean_value"]
        .mean()
        .reset_index()
    )

    # Pivot long format to wide features
    wide_df = agg_df.pivot(
        index=KEY_MERGE_COLS,
        columns="param_col",
        values="clean_value",
    ).reset_index()

    # Extract static activity metadata
    metadata_cols = [
        "MonitoringLocationIdentifier",
        "ActivityStartDate",
        "ActivityIdentifier",
        "ActivityStartTime/Time",
        "ActivityLocation/LatitudeMeasure",
        "ActivityLocation/LongitudeMeasure",
        "OrganizationFormalName",
        "HydrologicCondition",
        "HydrologicEvent",
    ]
    avail_meta = [c for c in metadata_cols if c in df_filtered.columns]
    meta_df = df_filtered[avail_meta].drop_duplicates(subset=KEY_MERGE_COLS)

    # Merge metadata with wide parameters
    final_pc_df = pd.merge(meta_df, wide_df, on=KEY_MERGE_COLS, how="left")
    logger.info(f"Pivoted Physical/Chemical wide events: {len(final_pc_df):,} distinct activities.")
    return final_pc_df


def process_biological_dataset(
    filepath: str,
    chunksize: int = 50000,
    limit_rows: Optional[int] = None,
) -> pd.DataFrame:
    """
    Stream and aggregate biological observations and ecotoxicity bioindicators per activity.
    """
    logger.info(f"Ingesting Biological dataset: {filepath}")
    
    chunks = []
    rows_read = 0

    cols_to_load = [
        "MonitoringLocationIdentifier",
        "ActivityStartDate",
        "ActivityIdentifier",
        "SubjectTaxonomicName",
        "TaxonomicPollutionTolerance",
        "TrophicLevelName",
        "FunctionalFeedingGroupName",
        "BiologicalIntentName",
        "CharacteristicName",
        "ResultMeasureValue",
    ]

    for chunk in pd.read_csv(
        filepath,
        chunksize=chunksize,
        usecols=lambda c: c in cols_to_load,
        low_memory=False,
        nrows=limit_rows,
    ):
        rows_read += len(chunk)
        logger.info(f"  [Biological] Processed {rows_read:,} raw rows...")

        # Keep biological rows where biological intent or taxonomy is present
        bio_mask = (
            chunk["SubjectTaxonomicName"].notna()
            | chunk["BiologicalIntentName"].notna()
            | chunk["TaxonomicPollutionTolerance"].notna()
            | chunk["TrophicLevelName"].notna()
        )
        filtered = chunk[bio_mask].copy()
        if not filtered.empty:
            chunks.append(filtered)

        if limit_rows and rows_read >= limit_rows:
            break

    if not chunks:
        logger.warning("No biological records found matching criteria.")
        return pd.DataFrame(columns=KEY_MERGE_COLS)

    df_bio = pd.concat(chunks, ignore_index=True)
    logger.info(f"Total relevant Biological observations: {len(df_bio):,}")

    # Clean pollution tolerance numeric values
    if "TaxonomicPollutionTolerance" in df_bio.columns:
        df_bio["clean_tolerance"] = df_bio["TaxonomicPollutionTolerance"].apply(clean_measure_value)
    else:
        df_bio["clean_tolerance"] = np.nan

    # Standard bioindicator species flag (Ceriodaphnia, Hyalella, Pimephales)
    STANDARD_BIOINDICATORS = {"ceriodaphnia dubia", "hyalella azteca", "pimephales promelas", "thalassiosira pseudonana"}
    df_bio["is_standard_bioassay"] = (
        df_bio["SubjectTaxonomicName"]
        .astype(str)
        .str.lower()
        .isin(STANDARD_BIOINDICATORS)
        .astype(int)
    )

    # Group by activity and construct aggregated biological health metrics
    def aggregate_bio_activity(group: pd.DataFrame) -> pd.Series:
        taxa = group["SubjectTaxonomicName"].dropna().unique()
        dominant_taxon = group["SubjectTaxonomicName"].mode()[0] if not group["SubjectTaxonomicName"].dropna().empty else "None"
        dominant_trophic = group["TrophicLevelName"].mode()[0] if ("TrophicLevelName" in group and not group["TrophicLevelName"].dropna().empty) else "Unspecified"
        dominant_ffg = group["FunctionalFeedingGroupName"].mode()[0] if ("FunctionalFeedingGroupName" in group and not group["FunctionalFeedingGroupName"].dropna().empty) else "Unspecified"
        mean_tol = group["clean_tolerance"].dropna().mean() if not group["clean_tolerance"].dropna().empty else np.nan
        has_bioassay = int(group["is_standard_bioassay"].sum() > 0)

        return pd.Series({
            "bio_taxa_richness": len(taxa),
            "bio_dominant_taxon": str(dominant_taxon),
            "bio_dominant_trophic_level": str(dominant_trophic),
            "bio_functional_feeding_group": str(dominant_ffg),
            "bio_mean_pollution_tolerance": mean_tol,
            "bio_standard_bioassay_flag": has_bioassay,
            "bio_total_observations": len(group),
            "biological_sampled_flag": 1,
        })

    bio_summary = (
        df_bio.groupby(KEY_MERGE_COLS)
        .apply(aggregate_bio_activity, include_groups=False)
        .reset_index()
    )

    logger.info(f"Aggregated Biological health features: {len(bio_summary):,} distinct sampling events.")
    return bio_summary


def compute_derived_biogeochemical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute derived stoichiometry, sediment ratios, and initial multi-domain water quality indices.
    """
    logger.info("Computing derived biogeochemical and ecotoxicity features...")

    # 1. Total Estimated Nitrogen (mg/L)
    n_components = [c for c in ["nitrate_mg_l", "nitrite_mg_l", "ammonia_ammonium_mg_l", "organic_nitrogen_mg_l"] if c in df.columns]
    if n_components:
        df["total_nitrogen_est_mg_l"] = df[n_components].sum(axis=1, min_count=1)
    else:
        df["total_nitrogen_est_mg_l"] = np.nan

    # 2. Total Estimated Phosphorus (mg/L)
    if "total_phosphorus_mg_l" in df.columns and "orthophosphate_mg_l" in df.columns:
        df["total_phosphorus_est_mg_l"] = df["total_phosphorus_mg_l"].fillna(df["orthophosphate_mg_l"])
    elif "orthophosphate_mg_l" in df.columns:
        df["total_phosphorus_est_mg_l"] = df["orthophosphate_mg_l"]
    elif "total_phosphorus_mg_l" in df.columns:
        df["total_phosphorus_est_mg_l"] = df["total_phosphorus_mg_l"]
    else:
        df["total_phosphorus_est_mg_l"] = np.nan

    # 3. Nitrogen to Phosphorus (N:P) Stoichiometric Ratio
    # Redfield ratio mass benchmark ~ 7.2:1 (N:P by weight)
    df["n_to_p_ratio"] = np.where(
        df["total_nitrogen_est_mg_l"].notna() & df["total_phosphorus_est_mg_l"].notna(),
        df["total_nitrogen_est_mg_l"] / np.clip(df["total_phosphorus_est_mg_l"], 0.001, 100.0),
        np.nan,
    )

    # 4. Sediment to Turbidity Ratio (Particulate loading signature)
    if "suspended_sediment_conc_mg_l" in df.columns and "turbidity_fnu" in df.columns:
        df["ssc_to_turbidity_ratio"] = np.where(
            df["suspended_sediment_conc_mg_l"].notna() & df["turbidity_fnu"].notna(),
            df["suspended_sediment_conc_mg_l"] / np.clip(df["turbidity_fnu"], 0.1, 1000.0),
            np.nan,
        )

    # 5. Fill biological presence flag for non-biological activities
    if "biological_sampled_flag" in df.columns:
        df["biological_sampled_flag"] = df["biological_sampled_flag"].fillna(0).astype(int)
        df["bio_standard_bioassay_flag"] = df["bio_standard_bioassay_flag"].fillna(0).astype(int)
        df["bio_taxa_richness"] = df["bio_taxa_richness"].fillna(0).astype(int)
        df["bio_total_observations"] = df["bio_total_observations"].fillna(0).astype(int)

    return df


def run_harmonization_pipeline(
    physchem_path: str,
    biological_path: str,
    output_path: str,
    limit_rows: Optional[int] = None,
) -> pd.DataFrame:
    """
    Execute complete end-to-end USGS multi-domain data harmonization pipeline.
    """
    logger.info("=" * 70)
    logger.info("STARTING USGS MULTI-DOMAIN DATA HARMONIZATION PIPELINE")
    logger.info("=" * 70)

    # 1. Ingest & Pivot Physical/Chemical Dataset
    df_physchem = process_physchem_dataset(physchem_path, limit_rows=limit_rows)

    # 2. Ingest & Aggregate Biological Dataset
    df_biological = process_biological_dataset(biological_path, limit_rows=limit_rows)

    # 3. Deterministic Composite Merge
    logger.info("Merging Physical/Chemical events with Biological indicators on composite keys:")
    logger.info(f"  Keys: {KEY_MERGE_COLS}")

    if not df_physchem.empty and not df_biological.empty:
        merged_df = pd.merge(
            df_physchem,
            df_biological,
            on=KEY_MERGE_COLS,
            how="left",
        )
    elif not df_physchem.empty:
        merged_df = df_physchem
    else:
        merged_df = df_biological

    logger.info(f"Merged Dataset Dimensions: {merged_df.shape[0]:,} events × {merged_df.shape[1]} features.")

    # 4. Feature Engineering
    fused_df = compute_derived_biogeochemical_features(merged_df)

    # 5. Save to Optimized Parquet
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    logger.info(f"Exporting harmonized dataset to: {output_path}")
    fused_df.to_parquet(output_path, engine="pyarrow", compression="snappy", index=False)
    
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    logger.info(f"Parquet Export Successful! File Size: {file_size_mb:.2f} MB")
    logger.info("=" * 70)

    return fused_df


def main():
    parser = argparse.ArgumentParser(description="USGS Water Quality Data Harmonization Pipeline")
    parser.add_argument(
        "--physchem",
        type=str,
        default="data/raw/resultphyschem.csv",
        help="Path to USGS physical/chemical CSV",
    )
    parser.add_argument(
        "--bio",
        type=str,
        default="data/raw/biologicalresult.csv",
        help="Path to USGS biological CSV",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/usgs_water_quality.parquet",
        help="Output Parquet path",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional row limit for test validation runs",
    )

    args = parser.parse_args()

    # Fallback to root files if data/raw symlinks are not available
    pc_path = args.physchem if os.path.exists(args.physchem) else "resultphyschem.csv"
    bio_path = args.bio if os.path.exists(args.bio) else "biologicalresult.csv"

    run_harmonization_pipeline(
        physchem_path=pc_path,
        biological_path=bio_path,
        output_path=args.output,
        limit_rows=args.limit,
    )


if __name__ == "__main__":
    main()
