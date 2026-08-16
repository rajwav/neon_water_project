"""
NEON Water Intelligence Platform — SQLite Telemetry & AI Inference History Database.
Stores continuous time-series telemetry packets and corresponding AI model diagnostics.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_DIR = PROJECT_ROOT / "data"
DB_PATH = DB_DIR / "telemetry_history.db"


def init_db(db_path: Optional[Path] = None) -> None:
    """Initialize the SQLite schema for telemetry records."""
    target_path = db_path or DB_PATH
    os.makedirs(target_path.parent, exist_ok=True)
    
    with sqlite3.connect(target_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS telemetry_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                node_id TEXT NOT NULL,
                ph REAL NOT NULL,
                dissolved_oxygen REAL NOT NULL,
                turbidity REAL NOT NULL,
                conductivity REAL NOT NULL,
                temperature REAL NOT NULL,
                nitrate REAL,
                phosphate REAL,
                heavy_metal_risk REAL,
                microbial_risk REAL,
                anomaly_status TEXT,
                anomaly_score REAL,
                risk_label TEXT,
                risk_confidence REAL,
                eco_health_index REAL,
                final_status TEXT,
                prediction_reason TEXT,
                raw_payload_json TEXT
            )
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON telemetry_records(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_node_id ON telemetry_records(node_id)")
        conn.commit()


def insert_telemetry_record(
    telemetry: Dict[str, Any],
    ai_result: Optional[Dict[str, Any]] = None,
    db_path: Optional[Path] = None,
) -> int:
    """Insert a validated telemetry packet and its AI diagnostic results into SQLite."""
    target_path = db_path or DB_PATH
    if not target_path.exists():
        init_db(target_path)

    ai_res = ai_result or {}
    m1 = ai_res.get("anomaly_detection", {})
    m2 = ai_res.get("risk_prediction", {})
    m3 = ai_res.get("biological_health", {})
    xai = ai_res.get("xai_explanation", {})

    ts = telemetry.get("timestamp") or datetime.now(timezone.utc).isoformat()
    node_id = telemetry.get("node_id", "HIRAKUD_NODE_001")
    ph = float(telemetry.get("ph", 7.42))
    do = float(telemetry.get("dissolved_oxygen", 8.65))
    turb = float(telemetry.get("turbidity", 4.5))
    cond = float(telemetry.get("conductivity", 280.0))
    temp = float(telemetry.get("temperature", 21.3))
    no3 = float(telemetry.get("nitrate", 4.5)) if telemetry.get("nitrate") is not None else None
    po4 = float(telemetry.get("phosphate", 0.05)) if telemetry.get("phosphate") is not None else None
    hm = float(telemetry.get("heavy_metal_risk", 0.05)) if telemetry.get("heavy_metal_risk") is not None else None
    mb = float(telemetry.get("microbial_risk", 3.0)) if telemetry.get("microbial_risk") is not None else None

    anomaly_stat = m1.get("status") or ai_res.get("anomaly_status", "Normal")
    anomaly_score = float(m1.get("score") if m1.get("score") is not None else ai_res.get("anomaly_score", 0.0))
    risk_lbl = m2.get("class") or ai_res.get("ml_prediction", "SAFE")
    risk_conf = float(m2.get("probability") if m2.get("probability") is not None else ai_res.get("ml_confidence", 0.95))
    eco_idx = float(m3.get("score") if m3.get("score") is not None else 92.0)
    final_stat = ai_res.get("final_status", risk_lbl)
    reason = xai.get("prediction_reason") or ai_res.get("override_reason", "Telemetry within baseline.")

    raw_json = json.dumps({"telemetry": telemetry, "ai": ai_res})

    with sqlite3.connect(target_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO telemetry_records (
                timestamp, node_id, ph, dissolved_oxygen, turbidity, conductivity,
                temperature, nitrate, phosphate, heavy_metal_risk, microbial_risk,
                anomaly_status, anomaly_score, risk_label, risk_confidence,
                eco_health_index, final_status, prediction_reason, raw_payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts, node_id, ph, do, turb, cond, temp, no3, po4, hm, mb,
                anomaly_stat, anomaly_score, risk_lbl, risk_conf,
                eco_idx, final_stat, reason, raw_json
            )
        )
        conn.commit()
        return cursor.lastrowid


def get_recent_telemetry_records(limit: int = 50, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Retrieve the most recent telemetry history records."""
    target_path = db_path or DB_PATH
    if not target_path.exists():
        init_db(target_path)
        return []

    with sqlite3.connect(target_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, timestamp, node_id, ph, dissolved_oxygen, turbidity,
                   conductivity, temperature, nitrate, phosphate, heavy_metal_risk,
                   anomaly_status, anomaly_score, risk_label, risk_confidence,
                   eco_health_index, final_status, prediction_reason
            FROM telemetry_records
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


# Initialize on import
init_db()
