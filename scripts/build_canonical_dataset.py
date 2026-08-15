#!/usr/bin/env python3
"""
CLI entry point to execute the Phase 1 Canonical Data Pipeline.

Verifies raw file immutability (SHA-256), processes all raw files,
exports validated & temporal Parquet datasets, and generates the audit report.
"""

import hashlib
import json
import os
import sys

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.pipeline import run_canonical_pipeline


def verify_raw_manifest(manifest_path: str = "data/raw_manifest.json", raw_dir: str = "data/raw") -> bool:
    """Verifies that all raw files match their pre-computed SHA-256 hashes."""
    if not os.path.exists(manifest_path):
        print(f"⚠️ Warning: Manifest file {manifest_path} not found.")
        return False

    with open(manifest_path, "r") as fp:
        manifest = json.load(fp)

    mismatches = []
    missing = []

    for fname, expected_hash in manifest.items():
        fpath = os.path.join(raw_dir, fname)
        if not os.path.exists(fpath):
            missing.append(fname)
            continue

        hasher = hashlib.sha256()
        with open(fpath, "rb") as fp:
            while chunk := fp.read(65536):
                hasher.update(chunk)
        actual_hash = hasher.hexdigest()

        if actual_hash != expected_hash:
            mismatches.append((fname, expected_hash, actual_hash))

    if missing:
        print(f"❌ Verification failed: {len(missing)} raw files missing!")
        return False
    if mismatches:
        print(f"❌ Verification failed: {len(mismatches)} raw files modified!")
        return False

    print(f"🔒 SHA-256 Immutability Check PASSED for all {len(manifest)} raw files.")
    return True


def main():
    print("=" * 60)
    print("SIH Water Intelligence Platform — Phase 1 Canonical Pipeline")
    print("=" * 60)

    # 1. Pre-execution SHA-256 check
    print("\n[Step 1/3] Verifying pre-execution raw data integrity...")
    if not verify_raw_manifest():
        print("❌ Pre-execution raw data verification failed. Aborting.")
        sys.exit(1)

    # 2. Run Pipeline
    print("\n[Step 2/3] Running canonical data pipeline...")
    report = run_canonical_pipeline()

    # 3. Post-execution SHA-256 check
    print("\n[Step 3/3] Verifying post-execution raw data immutability...")
    if not verify_raw_manifest():
        print("❌ Post-execution raw data check failed: raw files were modified!")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("PIPELINE AUDIT SUMMARY")
    print("=" * 60)
    print(f"Raw Records Read:         {report.total_raw_records_read:,}")
    print(f"Canonical Records Written:{report.total_canonical_records_written:,}")
    print(f"Excluded Records:         {report.total_excluded_records:,}")
    print(f"Temporal 2024 Records:    {report.temporal_2024_records:,}")
    print(f"Temporal 2025 Records:    {report.temporal_2025_records:,}")
    print(f"Duplicate Records:        {report.duplicate_records_detected:,}")
    print(f"ARIK Raw vs Canonical:    {report.arik_accountability['canonical_records_preserved']:,} preserved")
    print("\nSite Breakdown:")
    for site, count in report.site_record_counts.items():
        print(f" - {site:5s}: {count:,} records")
    print("=" * 60)


if __name__ == "__main__":
    main()
