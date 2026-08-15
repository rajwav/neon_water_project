#!/usr/bin/env python3
"""
Model 1: Water Quality Anomaly Detector (v2.0).

Trains an Isolation Forest anomaly detector on canonical water quality data.
Evaluates using a strict temporal split (2024 train -> 2025 test).

Features:
  - ph
  - dissolved_oxygen
  - turbidity
  - specific_conductance
  - fdom

Outputs:
  - models/v2/anomaly_detector_v2.joblib
  - models/v2/anomaly_metadata.json
  - reports/model1_results.md
  - reports/anomaly_distribution_v2.png
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Set matplotlib config dir to local workspace directory for headless execution
os.environ["MPLCONFIGDIR"] = str(PROJECT_ROOT / ".matplotlib_cache")
import matplotlib.pyplot as plt
import seaborn as sns

DATA_PATH = PROJECT_ROOT / "data" / "labeled" / "operational_risk_labels_v2.parquet"
MODEL_DIR = PROJECT_ROOT / "models" / "v2"
REPORT_DIR = PROJECT_ROOT / "reports"

ANOMALY_FEATURES = [
    "ph",
    "dissolved_oxygen",
    "turbidity",
    "specific_conductance",
    "fdom",
]


def load_and_sample_data(sample_train: int = 80_000, sample_test: int = 20_000, random_state: int = 42):
    """
    Load data and perform temporal train/test sampling:
      - 2024 -> Train partition (80,000 records)
      - 2025 -> Test partition (20,000 records)
    """
    print(f"Loading {DATA_PATH}...")
    cols_to_load = ANOMALY_FEATURES + ["site_id", "sensor_position", "risk_label_v2", "timestamp_utc"]
    df = pd.read_parquet(DATA_PATH, columns=cols_to_load)
    print(f"Total dataset: {len(df):,} records")

    # Temporal split
    df_ts = pd.to_datetime(df["timestamp_utc"])
    df_2024 = df[df_ts.dt.year == 2024]
    df_2025 = df[df_ts.dt.year == 2025]

    print(f"2024 pool: {len(df_2024):,} records | 2025 pool: {len(df_2025):,} records")

    train_sample = df_2024.sample(n=min(len(df_2024), sample_train), random_state=random_state).reset_index(drop=True)
    test_sample = df_2025.sample(n=min(len(df_2025), sample_test), random_state=random_state).reset_index(drop=True)

    print(f"Sampled train set: {len(train_sample):,} records")
    print(f"Sampled test set:  {len(test_sample):,} records")

    return train_sample, test_sample


def build_and_train_model(X_train: pd.DataFrame, contamination: float = 0.05):
    """
    Build pipeline: SimpleImputer (median) -> RobustScaler -> IsolationForest.
    """
    print("Building and training Isolation Forest pipeline...")
    pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", RobustScaler()),
        ("model", IsolationForest(
            n_estimators=120,
            contamination=contamination,
            max_samples="auto",
            random_state=42,
            n_jobs=-1,
        )),
    ])

    t0 = time.time()
    pipeline.fit(X_train)
    t1 = time.time()
    print(f"Isolation Forest trained in {t1 - t0:.2f}s")

    return pipeline


def score_anomalies(pipeline: Pipeline, df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute anomaly_score and anomaly_status for observations.
      - raw decision_function: lower means more anomalous
      - anomaly_score: inverted and scaled so higher means more anomalous
      - anomaly_status: 'Anomaly' (-1) vs 'Normal' (1)
    """
    X = df[ANOMALY_FEATURES]
    preds = pipeline.predict(X)
    raw_scores = pipeline.decision_function(X)

    # Invert decision function: higher raw score was normal -> higher anomaly_score is now anomalous
    df_scored = df.copy()
    df_scored["anomaly_raw_score"] = raw_scores
    df_scored["anomaly_score"] = -raw_scores  # higher = more anomalous
    df_scored["anomaly_status"] = np.where(preds == -1, "Anomaly", "Normal")

    return df_scored


def save_artifacts_and_reports(pipeline, train_scored, test_scored, train_count, test_count, contamination):
    """Save model pipeline, metadata, evaluation plot, and markdown report."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Save model artifact
    model_path = MODEL_DIR / "anomaly_detector_v2.joblib"
    joblib.dump(pipeline, model_path)
    print(f"Saved anomaly detector: {model_path} ({model_path.stat().st_size / (1024*1024):.2f} MB)")

    # Compute statistics
    train_anomaly_count = (train_scored["anomaly_status"] == "Anomaly").sum()
    train_anomaly_pct = (train_anomaly_count / train_count) * 100

    test_anomaly_count = (test_scored["anomaly_status"] == "Anomaly").sum()
    test_anomaly_pct = (test_anomaly_count / test_count) * 100

    site_dist = test_scored.groupby(["site_id", "anomaly_status"]).size().unstack(fill_value=0)
    risk_cross = test_scored.groupby(["risk_label_v2", "anomaly_status"]).size().unstack(fill_value=0)

    # Save metadata
    metadata = {
        "model_name": "Model 1 Water Quality Anomaly Detector",
        "model_version": "v2.0",
        "algorithm": "IsolationForest",
        "contamination": contamination,
        "features": ANOMALY_FEATURES,
        "train_records": train_count,
        "test_records": test_count,
        "train_anomaly_percentage": round(train_anomaly_pct, 2),
        "test_anomaly_percentage": round(test_anomaly_pct, 2),
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    meta_path = MODEL_DIR / "anomaly_metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2))
    print(f"Saved metadata: {meta_path}")

    # Generate Visualization Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Plot 1: Anomaly Score Distribution
    sns.histplot(
        data=test_scored,
        x="anomaly_score",
        hue="anomaly_status",
        bins=50,
        palette={"Normal": "#2b5c8f", "Anomaly": "#d9534f"},
        ax=axes[0],
        kde=True,
    )
    axes[0].set_title("Anomaly Score Distribution (2025 Test Partition)", fontsize=11, fontweight="bold")
    axes[0].set_xlabel("Anomaly Score (Higher = More Anomalous)", fontsize=10)
    axes[0].set_ylabel("Observation Count", fontsize=10)

    # Plot 2: Site-wise Anomaly Breakdown
    site_pcts = (site_dist["Anomaly"] / site_dist.sum(axis=1) * 100).sort_values(ascending=False)
    sns.barplot(x=site_pcts.index, y=site_pcts.values, color="#e67e22", ax=axes[1])
    axes[1].set_title("Anomaly Rate by Monitoring Site (%)", fontsize=11, fontweight="bold")
    axes[1].set_xlabel("Site ID", fontsize=10)
    axes[1].set_ylabel("Anomaly Percentage (%)", fontsize=10)
    for p in axes[1].patches:
        axes[1].annotate(f"{p.get_height():.1f}%", (p.get_x() + p.get_width() / 2., p.get_height()),
                         ha='center', va='center', xytext=(0, 5), textcoords='offset points', fontsize=9)

    plt.tight_layout()
    viz_path = REPORT_DIR / "anomaly_distribution_v2.png"
    plt.savefig(viz_path, dpi=200)
    plt.close()
    print(f"Saved evaluation visualization: {viz_path}")

    # Generate Markdown Report
    lines = []
    lines.append("# Model 1 Anomaly Detection (v2.0) Evaluation Report")
    lines.append("")
    lines.append(f"**Model**: Isolation Forest (`v2.0`)")
    lines.append(f"**Dataset**: `data/labeled/operational_risk_labels_v2.parquet`")
    lines.append(f"**Validation Strategy**: Strict Temporal Hold-Out (2024 Train $\\rightarrow$ 2025 Test)")
    lines.append(f"**Features Evaluated**: `{', '.join(ANOMALY_FEATURES)}`")
    lines.append(f"**Train Records**: {train_count:,} (2024)")
    lines.append(f"**Test Records**: {test_count:,} (2025)")
    lines.append(f"**Evaluation Date**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Anomaly Detection Summary")
    lines.append("")
    lines.append(f"| Metric | 2024 Train Partition | 2025 Test Partition |")
    lines.append(f"|---|---:|---:|")
    lines.append(f"| **Total Sampled Records** | {train_count:,} | {test_count:,} |")
    lines.append(f"| **Normal Observations** | {train_count - train_anomaly_count:,} ({(100-train_anomaly_pct):.2f}%) | {test_count - test_anomaly_count:,} ({(100-test_anomaly_pct):.2f}%) |")
    lines.append(f"| **Detected Anomalies** | {train_anomaly_count:,} (**{train_anomaly_pct:.2f}%**) | {test_anomaly_count:,} (**{test_anomaly_pct:.2f}%**) |")
    lines.append("")
    lines.append("## 2. Site-Wise Anomaly Distribution (2025 Test Set)")
    lines.append("")
    lines.append("| Site | Normal | Anomaly | Total | Anomaly Rate |")
    lines.append("|---|---:|---:|---:|---:|")
    for site, row in site_dist.iterrows():
        n = row.get("Normal", 0)
        a = row.get("Anomaly", 0)
        tot = n + a
        pct = (a / tot * 100) if tot > 0 else 0.0
        lines.append(f"| **{site}** | {n:,} | {a:,} | {tot:,} | **{pct:.2f}%** |")
    lines.append("")
    lines.append("## 3. Anomaly vs. Operational Risk Cross-Tabulation")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append("> Per `Rules.md` 2.3, Anomaly detection is independent of contamination confirmation. Below demonstrates the empirical relationship on unseen 2025 data:")
    lines.append("")
    lines.append("| Risk State (v2.0) | Normal | Anomaly | Total | Anomaly Rate |")
    lines.append("|---|---:|---:|---:|---:|")
    for risk_lbl, row in risk_cross.iterrows():
        n = row.get("Normal", 0)
        a = row.get("Anomaly", 0)
        tot = n + a
        pct = (a / tot * 100) if tot > 0 else 0.0
        lines.append(f"| **{risk_lbl}** | {n:,} | {a:,} | {tot:,} | **{pct:.2f}%** |")
    lines.append("")
    lines.append("## 4. Sample Predictions on Unseen 2025 Records")
    lines.append("")
    sample_rows = test_scored[test_scored["anomaly_status"] == "Anomaly"].head(5)
    lines.append("| Observation ID | Site | pH | DO (mg/L) | Turbidity (FNU) | SpCond (µS/cm) | fDOM (QSU) | Anomaly Score | Status |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---|")
    for idx, r in sample_rows.iterrows():
        lines.append(
            f"| Row {idx} | {r['site_id']} | {r['ph']:.2f} | {r['dissolved_oxygen']:.2f} | {r['turbidity']:.2f} | {r['specific_conductance']:.1f} | {r['fdom']:.1f} | **{r['anomaly_score']:.4f}** | `{r['anomaly_status']}` |"
        )
    lines.append("")
    lines.append("## 5. Architectural Improvements over Legacy Model 1")
    lines.append("")
    lines.append("1. **Full Temporal Separation**: Trained on 2024 and validated on 2025; no data leakage.")
    lines.append("2. **Robust Multi-Parameter Scaling**: Utilizes `RobustScaler` to prevent extreme flash turbidity/SpCond spikes from skewing the spatial tree partitioning.")
    lines.append("3. **Continuous Anomaly Scoring**: Produces both calibrated continuous `anomaly_score` and discrete `anomaly_status`.")
    lines.append("4. **Decoupled Architecture**: Zero leakage into or from risk classification labels.")
    lines.append("")

    report_path = REPORT_DIR / "model1_results.md"
    report_path.write_text("\n".join(lines))
    print(f"Saved evaluation report: {report_path}")


def main():
    print("=" * 70)
    print("  MODEL 1 WATER QUALITY ANOMALY DETECTOR (v2.0) TRAINING")
    print("=" * 70)

    train_df, test_df = load_and_sample_data(sample_train=80_000, sample_test=20_000)

    X_train = train_df[ANOMALY_FEATURES]
    pipeline = build_and_train_model(X_train, contamination=0.05)

    print("Scoring train and test partitions...")
    train_scored = score_anomalies(pipeline, train_df)
    test_scored = score_anomalies(pipeline, test_df)

    save_artifacts_and_reports(
        pipeline=pipeline,
        train_scored=train_scored,
        test_scored=test_scored,
        train_count=len(train_df),
        test_count=len(test_df),
        contamination=0.05,
    )

    print("\n" + "=" * 70)
    print(f"  MODEL 1 TRAINING & EVALUATION COMPLETE: Test Anomaly Rate = {(test_scored['anomaly_status'] == 'Anomaly').mean()*100:.2f}%")
    print("=" * 70)


if __name__ == "__main__":
    main()
