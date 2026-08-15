"""
=============================================================================
SIH 2026 NEON Water Intelligence Platform
Model 3: Biological Ecosystem Health Assessment Engine (Phase 4)
=============================================================================

This module implements a multi-metric Biological & Ecotoxicity Health Engine
fusing physical-chemical water chemistry with biological bioassay indicators:
  1. Biodiversity Score (0-100)
  2. Pollution Tolerance Score (0-100)
  3. Trophic Balance Score (0-100)
  4. Bioassay Stress Score (0-100)
  5. Composite Biological Health Score (0-100)
  6. NEON Eco Health Index (0-100) [Chemical + Biological Fusion with Anti-Eclipsing]

Artifact: models/v3/ecological_health_engine.joblib
Documentation: docs/MODEL3_BIOLOGICAL_INTELLIGENCE.md
"""

import os
import sys
import argparse
import logging
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("biological_health")

# EPA & Standard Ecotoxicity Bioassay Species Tolerance Profiles
# Lower sensitivity index = more sensitive / lower pollution tolerance (1-10 scale)
TAXA_ECOTOX_PROFILES = {
    "ceriodaphnia dubia": {
        "common_name": "Water Flea (Cladoceran)",
        "trophic_role": "Primary Consumer / Filterer",
        "sensitivity_level": "High (Acute Heavy Metal & Pesticide Sensitive)",
        "tolerance_index": 2.5, # Sensitive
        "optimal_ph_range": (6.5, 8.5),
        "min_do_mg_l": 5.0,
        "max_ammonia_mg_l": 0.5,
    },
    "hyalella azteca": {
        "common_name": "Scud / Amphipod Crustacean",
        "trophic_role": "Benthic Detritivore / Epibenthic Consumer",
        "sensitivity_level": "High (Sediment Toxicity & Hypoxia Sensitive)",
        "tolerance_index": 3.0, # Sensitive
        "optimal_ph_range": (6.0, 8.8),
        "min_do_mg_l": 4.0,
        "max_ssc_mg_l": 150.0,
    },
    "pimephales promelas": {
        "common_name": "Fathead Minnow (Vertebrate)",
        "trophic_role": "Secondary Consumer / Planktivore",
        "sensitivity_level": "Moderate (Organic Waste & Industrial Effluent)",
        "tolerance_index": 5.5, # Moderately Tolerant
        "optimal_ph_range": (6.0, 9.0),
        "min_do_mg_l": 4.5,
        "max_ammonia_mg_l": 1.2,
    },
    "thalassiosira pseudonana": {
        "common_name": "Marine / Estuarine Diatom",
        "trophic_role": "Primary Producer",
        "sensitivity_level": "High (Herbicide & Heavy Metal Sensitive)",
        "tolerance_index": 2.0,
        "optimal_ph_range": (7.0, 8.8),
        "min_do_mg_l": 5.5,
        "max_ammonia_mg_l": 0.3,
    },
}


class BiologicalHealthEngine:
    """
    Biological Ecosystem Intelligence & Multi-Domain Ecotoxicity Engine.
    """

    def __init__(self):
        self.version = "3.0.0-eco-intelligence"

    def compute_biodiversity_score(
        self,
        taxa_richness: int,
        biological_sampled: int,
        do_val: Optional[float] = None,
        turb_val: Optional[float] = None,
    ) -> float:
        """
        Evaluate community biodiversity and taxa richness on a 0-100 scale.
        """
        if biological_sampled == 1 and taxa_richness > 0:
            # Score scaled with richness: 1 taxon = 75, 2 taxa = 90, >=3 taxa = 100
            base = min(100.0, 60.0 + (taxa_richness * 15.0))
            return float(np.clip(base, 0.0, 100.0))
        
        # When biological sampling is absent, infer potential habitat biodiversity capacity from DO and turbidity
        score = 80.0
        if do_val is not None:
            if do_val < 3.0:
                score -= 40.0
            elif do_val < 5.0:
                score -= 20.0
            elif do_val >= 7.5:
                score += 10.0

        if turb_val is not None:
            if turb_val > 50.0:
                score -= 25.0
            elif turb_val > 20.0:
                score -= 10.0

        return float(np.clip(score, 10.0, 100.0))

    def compute_pollution_tolerance_score(
        self,
        dominant_taxon: str,
        ph_val: Optional[float] = None,
        do_val: Optional[float] = None,
        cond_val: Optional[float] = None,
        ammonia_val: Optional[float] = None,
    ) -> float:
        """
        Calculate pollution tolerance health score (0-100).
        High score = sensitive clean-water organisms thriving in unpolluted water.
        """
        taxon_key = str(dominant_taxon).lower().strip()
        profile = TAXA_ECOTOX_PROFILES.get(taxon_key)

        if profile is not None:
            base_score = 90.0 # Base clean bioassay score
            penalty = 0.0

            # pH envelope stress
            if ph_val is not None:
                min_ph, max_ph = profile["optimal_ph_range"]
                if ph_val < min_ph or ph_val > max_ph:
                    penalty += 25.0

            # Dissolved oxygen stress
            if do_val is not None and do_val < profile["min_do_mg_l"]:
                deficit = profile["min_do_mg_l"] - do_val
                penalty += min(45.0, deficit * 15.0)

            # Ammonia toxicity stress
            if ammonia_val is not None and ammonia_val > profile.get("max_ammonia_mg_l", 1.0):
                excess = ammonia_val - profile["max_ammonia_mg_l"]
                penalty += min(35.0, excess * 25.0)

            # Salinity shock stress
            if cond_val is not None and cond_val > 1000.0:
                penalty += 20.0

            return float(np.clip(base_score - penalty, 5.0, 100.0))

        # Baseline chemical inference for unclassified taxa
        base = 85.0
        penalty = 0.0
        if do_val is not None and do_val < 5.0:
            penalty += (5.0 - do_val) * 12.0
        if ph_val is not None and (ph_val < 6.5 or ph_val > 8.5):
            penalty += abs(ph_val - 7.5) * 10.0
        if cond_val is not None and cond_val > 800.0:
            penalty += min(30.0, (cond_val - 800.0) / 30.0)

        return float(np.clip(base - penalty, 10.0, 100.0))

    def compute_trophic_balance_score(
        self,
        tn_val: Optional[float] = None,
        tp_val: Optional[float] = None,
        n_p_ratio: Optional[float] = None,
        do_val: Optional[float] = None,
        ssc_val: Optional[float] = None,
    ) -> float:
        """
        Evaluate trophic stability, nutrient equilibrium, and autotroph-heterotroph balance.
        """
        score = 95.0
        penalty = 0.0

        # Eutrophic nutrient loading penalties
        if tp_val is not None and tp_val > 0.05:
            penalty += min(30.0, (tp_val - 0.05) / 0.01 * 4.0)

        if tn_val is not None and tn_val > 3.0:
            penalty += min(25.0, (tn_val - 3.0) * 3.0)

        # Stoichiometric imbalance (Algal bloom or Nitrogen limitation)
        if n_p_ratio is not None:
            if n_p_ratio > 30.0 or n_p_ratio < 4.0:
                penalty += 15.0

        # Hypoxia / Eutrophication collapse coupling
        if do_val is not None and do_val < 4.0:
            penalty += (4.0 - do_val) * 10.0

        # Sediment blanket smothering benthic trophic web
        if ssc_val is not None and ssc_val > 150.0:
            penalty += min(20.0, (ssc_val - 150.0) / 20.0)

        return float(np.clip(score - penalty, 10.0, 100.0))

    def compute_bioassay_stress_score(
        self,
        dominant_taxon: str,
        ph_val: Optional[float] = None,
        do_val: Optional[float] = None,
        cond_val: Optional[float] = None,
        ammonia_val: Optional[float] = None,
        ssc_val: Optional[float] = None,
    ) -> float:
        """
        Calculate bioassay stress index (0 = lethal toxicity shock, 100 = optimal organism survival).
        """
        stress = 0.0 # Cumulative toxic stress index (0 - 100)

        if ph_val is not None:
            if ph_val < 4.0 or ph_val > 10.0:
                stress += 80.0 # Acute lethal acid/alkali shock
            elif ph_val < 6.0 or ph_val > 9.0:
                stress += 30.0

        if do_val is not None:
            if do_val < 2.0:
                stress += 75.0 # Acute asphyxiation
            elif do_val < 4.0:
                stress += 35.0
            elif do_val < 6.0:
                stress += 15.0

        if cond_val is not None and cond_val > 1500.0:
            stress += 40.0 # Osmotic / heavy metal complexation shock

        if ammonia_val is not None and ammonia_val > 1.0:
            stress += min(50.0, ammonia_val * 25.0)

        if ssc_val is not None and ssc_val > 500.0:
            stress += 40.0 # Severe abrasive gill clogging

        survival_score = 100.0 - min(100.0, stress)
        return float(np.clip(survival_score, 0.0, 100.0))

    def compute_biological_health_score(
        self,
        bio_diversity: float,
        pollution_tolerance: float,
        trophic_balance: float,
        bioassay_stress: float,
    ) -> float:
        """
        Weighted aggregate biological health score (0-100).
        """
        score = (
            0.30 * bio_diversity
            + 0.30 * pollution_tolerance
            + 0.20 * trophic_balance
            + 0.20 * bioassay_stress
        )
        return float(np.clip(score, 0.0, 100.0))

    def compute_chemical_health_score(
        self,
        ph_val: Optional[float] = None,
        do_val: Optional[float] = None,
        turb_val: Optional[float] = None,
        cond_val: Optional[float] = None,
        tn_val: Optional[float] = None,
        tp_val: Optional[float] = None,
        ssc_val: Optional[float] = None,
    ) -> float:
        """
        Compute integrated physical-chemical water quality score (0-100).
        """
        score = 100.0
        penalty = 0.0

        if ph_val is not None:
            if ph_val < 4.0 or ph_val > 10.0:
                penalty += 60.0
            elif ph_val < 6.5 or ph_val > 8.5:
                penalty += abs(ph_val - 7.5) * 12.0

        if do_val is not None:
            if do_val < 2.0:
                penalty += 65.0
            elif do_val < 5.0:
                penalty += (5.0 - do_val) * 12.0

        if turb_val is not None:
            if turb_val > 100.0:
                penalty += 45.0
            elif turb_val > 25.0:
                penalty += min(25.0, (turb_val - 25.0) * 0.4)

        if cond_val is not None:
            if cond_val > 1500.0:
                penalty += 40.0
            elif cond_val > 800.0:
                penalty += min(20.0, (cond_val - 800.0) / 35.0)

        if ssc_val is not None and ssc_val > 200.0:
            penalty += min(30.0, (ssc_val - 200.0) / 20.0)

        if tp_val is not None and tp_val > 0.10:
            penalty += min(25.0, (tp_val - 0.10) * 80.0)

        return float(np.clip(score - penalty, 0.0, 100.0))

    def evaluate_sample(
        self,
        ph: Optional[float] = None,
        dissolved_oxygen: Optional[float] = None,
        turbidity: Optional[float] = None,
        specific_conductance: Optional[float] = None,
        temperature: Optional[float] = None,
        total_nitrogen: Optional[float] = None,
        total_phosphorus: Optional[float] = None,
        n_p_ratio: Optional[float] = None,
        suspended_sediment: Optional[float] = None,
        ammonia: Optional[float] = None,
        bio_dominant_taxon: str = "None",
        bio_taxa_richness: int = 0,
        biological_sampled: int = 0,
    ) -> Dict[str, Any]:
        """
        Execute comprehensive biological and chemical ecosystem health assessment.
        """
        # 1. Compute Sub-Indicators
        s_biodiv = self.compute_biodiversity_score(
            taxa_richness=bio_taxa_richness,
            biological_sampled=biological_sampled,
            do_val=dissolved_oxygen,
            turb_val=turbidity,
        )

        s_tolerance = self.compute_pollution_tolerance_score(
            dominant_taxon=bio_dominant_taxon,
            ph_val=ph,
            do_val=dissolved_oxygen,
            cond_val=specific_conductance,
            ammonia_val=ammonia,
        )

        s_trophic = self.compute_trophic_balance_score(
            tn_val=total_nitrogen,
            tp_val=total_phosphorus,
            n_p_ratio=n_p_ratio,
            do_val=dissolved_oxygen,
            ssc_val=suspended_sediment,
        )

        s_bioassay = self.compute_bioassay_stress_score(
            dominant_taxon=bio_dominant_taxon,
            ph_val=ph,
            do_val=dissolved_oxygen,
            cond_val=specific_conductance,
            ammonia_val=ammonia,
            ssc_val=suspended_sediment,
        )

        # 2. Composite Biological Health Score (0-100)
        bio_health = self.compute_biological_health_score(
            bio_diversity=s_biodiv,
            pollution_tolerance=s_tolerance,
            trophic_balance=s_trophic,
            bioassay_stress=s_bioassay,
        )

        # 3. Chemical Health Score (0-100)
        chem_health = self.compute_chemical_health_score(
            ph_val=ph,
            do_val=dissolved_oxygen,
            turb_val=turbidity,
            cond_val=specific_conductance,
            tn_val=total_nitrogen,
            tp_val=total_phosphorus,
            ssc_val=suspended_sediment,
        )

        # 4. NEON Eco Health Index (Chemical + Biological Fusion with Anti-Eclipsing)
        raw_fusion = (0.50 * bio_health) + (0.50 * chem_health)

        # Anti-Eclipsing Ecological Guardrail: If either domain suffers acute collapse, cap overall index
        is_chemical_collapse = (chem_health < 30.0) or (ph is not None and (ph < 4.0 or ph > 10.0)) or (dissolved_oxygen is not None and dissolved_oxygen < 2.0)
        is_biological_collapse = s_bioassay < 25.0

        if is_chemical_collapse or is_biological_collapse:
            eco_health_index = min(raw_fusion, 28.0) # Force into Ecotoxic Collapse tier
        else:
            eco_health_index = raw_fusion

        # 5. Qualitative Ecological Tier
        if eco_health_index >= 85.0:
            eco_tier = "Excellent (Pristine Ecosystem)"
            status_code = "SAFE"
        elif eco_health_index >= 70.0:
            eco_tier = "Good (Minor Stress)"
            status_code = "SAFE"
        elif eco_health_index >= 50.0:
            eco_tier = "Moderate (Impaired Community)"
            status_code = "WARNING"
        elif eco_health_index >= 30.0:
            eco_tier = "Poor (Severe Stress)"
            status_code = "WARNING"
        else:
            eco_tier = "Ecotoxic Collapse (Acute Mortality / Lethal Envelope)"
            status_code = "CRITICAL"

        return {
            "biodiversity_score": round(s_biodiv, 1),
            "pollution_tolerance_score": round(s_tolerance, 1),
            "trophic_balance_score": round(s_trophic, 1),
            "bioassay_stress_score": round(s_bioassay, 1),
            "biological_health_score": round(bio_health, 1),
            "chemical_health_score": round(chem_health, 1),
            "neon_eco_health_index": round(eco_health_index, 1),
            "ecological_tier": eco_tier,
            "operational_status": status_code,
            "bio_dominant_taxon": str(bio_dominant_taxon),
            "biological_sampled": int(biological_sampled),
        }


def process_dataset_and_generate_artifacts(
    data_path: str,
    model_output_path: str,
    reports_dir: str,
):
    """
    Score the full USGS dataset, serialize the engine, and export validation charts.
    """
    logger.info("=" * 70)
    logger.info("INITIALIZING BIOLOGICAL ECOSYSTEM HEALTH ENGINE (MODEL 3)")
    logger.info("=" * 70)

    engine = BiologicalHealthEngine()

    logger.info(f"Loading harmonized dataset: {data_path}")
    df = pd.read_parquet(data_path)
    logger.info(f"Assessing {len(df):,} sampling events...")

    results = []
    for _, row in df.iterrows():
        diag = engine.evaluate_sample(
            ph=row.get("ph") if pd.notna(row.get("ph")) else None,
            dissolved_oxygen=row.get("dissolved_oxygen_mg_l") if pd.notna(row.get("dissolved_oxygen_mg_l")) else None,
            turbidity=row.get("turbidity_fnu") if pd.notna(row.get("turbidity_fnu")) else None,
            specific_conductance=row.get("specific_conductance_us_cm") if pd.notna(row.get("specific_conductance_us_cm")) else None,
            temperature=row.get("temperature_c") if pd.notna(row.get("temperature_c")) else None,
            total_nitrogen=row.get("total_nitrogen_est_mg_l") if pd.notna(row.get("total_nitrogen_est_mg_l")) else None,
            total_phosphorus=row.get("total_phosphorus_est_mg_l") if pd.notna(row.get("total_phosphorus_est_mg_l")) else None,
            n_p_ratio=row.get("n_to_p_ratio") if pd.notna(row.get("n_to_p_ratio")) else None,
            suspended_sediment=row.get("suspended_sediment_conc_mg_l") if pd.notna(row.get("suspended_sediment_conc_mg_l")) else None,
            ammonia=row.get("ammonia_ammonium_mg_l") if pd.notna(row.get("ammonia_ammonium_mg_l")) else None,
            bio_dominant_taxon=row.get("bio_dominant_taxon") if pd.notna(row.get("bio_dominant_taxon")) else "None",
            bio_taxa_richness=int(row.get("bio_taxa_richness", 0)),
            biological_sampled=int(row.get("biological_sampled_flag", 0)),
        )
        results.append(diag)

    res_df = pd.DataFrame(results)
    
    logger.info("\n=== NEON ECO HEALTH INDEX EVALUATION SUMMARY ===")
    logger.info(f"Mean Biological Health Score : {res_df['biological_health_score'].mean():.2f}/100")
    logger.info(f"Mean Chemical Health Score   : {res_df['chemical_health_score'].mean():.2f}/100")
    logger.info(f"Mean NEON Eco Health Index   : {res_df['neon_eco_health_index'].mean():.2f}/100")
    
    logger.info("\nEcological Tier Distribution:")
    for tier, cnt in res_df["ecological_tier"].value_counts().items():
        logger.info(f"  {tier:<50}: {cnt:>6} ({cnt/len(res_df)*100:.1f}%)")

    # Serialize Engine Artifact
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(engine, model_output_path)
    logger.info(f"\nSerialized Biological Health Engine to: {model_output_path}")

    # Generate Evaluation Visualizations
    os.makedirs(reports_dir, exist_ok=True)

    # 1. Eco Health Index Distribution Plot
    plt.figure(figsize=(9, 5))
    sns.histplot(res_df["neon_eco_health_index"], bins=30, kde=True, color="#1b9e77")
    plt.axvline(85, color="green", linestyle="--", label="Pristine (>=85)")
    plt.axvline(70, color="blue", linestyle="--", label="Good (>=70)")
    plt.axvline(50, color="orange", linestyle="--", label="Moderate (>=50)")
    plt.axvline(30, color="red", linestyle="--", label="Ecotoxic Collapse (<30)")
    plt.title("NEON Eco Health Index Distribution (USGS Harmonized Catchments)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("NEON Eco Health Index (0-100)", fontweight="bold")
    plt.ylabel("Frequency", fontweight="bold")
    plt.legend()
    plt.tight_layout()
    dist_plot_path = os.path.join(reports_dir, "usgs_eco_health_distribution.png")
    plt.savefig(dist_plot_path, dpi=200)
    plt.close()
    logger.info(f"Saved Eco Health distribution plot to: {dist_plot_path}")

    # 2. Biological vs Chemical Score Scatter / Density Plot
    plt.figure(figsize=(8, 6))
    sns.scatterplot(
        data=res_df.sample(min(5000, len(res_df)), random_state=42),
        x="chemical_health_score",
        y="biological_health_score",
        hue="operational_status",
        palette={"SAFE": "#2ca02c", "WARNING": "#ff7f0e", "CRITICAL": "#d62728"},
        alpha=0.6,
    )
    plt.title("Biological Health vs. Chemical Health Score Coupling", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Chemical Health Score (0-100)", fontweight="bold")
    plt.ylabel("Biological Health Score (0-100)", fontweight="bold")
    plt.tight_layout()
    corr_plot_path = os.path.join(reports_dir, "usgs_bio_vs_chem_correlation.png")
    plt.savefig(corr_plot_path, dpi=200)
    plt.close()
    logger.info(f"Saved Bio-vs-Chem correlation plot to: {corr_plot_path}")
    logger.info("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Model 3 Biological Health Assessment Engine")
    parser.add_argument(
        "--data",
        type=str,
        default="data/processed/usgs_water_quality.parquet",
        help="Harmonized parquet input path",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="models/v3/ecological_health_engine.joblib",
        help="Serialized engine destination path",
    )
    parser.add_argument(
        "--reports-dir",
        type=str,
        default="reports",
        help="Directory to save evaluation figures",
    )

    args = parser.parse_args()
    process_dataset_and_generate_artifacts(args.data, args.output, args.reports_dir)


if __name__ == "__main__":
    main()
