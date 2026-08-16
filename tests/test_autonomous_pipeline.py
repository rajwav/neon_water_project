"""
Unit and Integration Tests for NEON Autonomous Continuous Telemetry Pipeline.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.model_loader import engine
from iot.autonomous_sensor import AutonomousSensorNode
from iot.database import get_recent_telemetry_records, init_db, insert_telemetry_record
from iot.mqtt_client import TelemetryIngestionManager


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_telemetry.db"
    init_db(db_file)
    return db_file


# ── 1. AUTONOMOUS SENSOR PACKET GENERATION ────────────────────────

def test_autonomous_sensor_packets():
    sensor = AutonomousSensorNode(node_id="HIRAKUD_NODE_001", interval_sec=5.0)
    pkt = sensor.generate_packet()

    assert pkt["node_id"] == "HIRAKUD_NODE_001"
    assert "timestamp" in pkt
    assert 6.0 <= pkt["ph"] <= 9.0
    assert 4.0 <= pkt["dissolved_oxygen"] <= 14.0
    assert 0.0 <= pkt["turbidity"] <= 30.0
    assert 10.0 <= pkt["temperature"] <= 35.0
    assert 50.0 <= pkt["conductivity"] <= 600.0


# ── 2. SQLITE HISTORY PERSISTENCE ─────────────────────────────────

def test_sqlite_insert_and_retrieve(temp_db):
    telemetry = {
        "node_id": "HIRAKUD_NODE_001",
        "ph": 7.40,
        "dissolved_oxygen": 8.60,
        "turbidity": 4.2,
        "conductivity": 280.0,
        "temperature": 21.0,
        "nitrate": 4.1,
        "phosphate": 0.04,
        "heavy_metal_risk": 0.03,
        "microbial_risk": 2.0,
    }
    ai_res = engine.predict(**{
        "ph": 7.40,
        "dissolved_oxygen": 8.60,
        "turbidity": 4.2,
        "specific_conductance": 280.0,
        "temperature": 21.0,
    })

    row_id = insert_telemetry_record(telemetry, ai_res, db_path=temp_db)
    assert row_id is not None
    assert row_id > 0

    records = get_recent_telemetry_records(limit=10, db_path=temp_db)
    assert len(records) == 1
    assert records[0]["node_id"] == "HIRAKUD_NODE_001"
    assert records[0]["final_status"] == "SAFE"
    assert records[0]["ph"] == 7.40


# ── 3. FAILURE SIMULATION & STATUS TRANSITIONS ─────────────────────

def test_failure_simulation_transitions():
    mgr = TelemetryIngestionManager()
    mgr.set_ai_engine(engine)
    
    pkt = {
        "node_id": "HIRAKUD_NODE_001",
        "ph": 7.35,
        "dissolved_oxygen": 8.50,
        "turbidity": 4.0,
        "temperature": 21.0,
        "conductivity": 275.0,
    }
    mgr.ingest_packet(pkt)

    # 1. Nominal state: < 30s
    status_nominal = mgr.get_connection_status()
    assert "Connected" in status_nominal["status"]
    assert status_nominal["connected"] is True

    # 2. Delayed state: > 30s and <= 120s
    mgr.latest_packet_timestamp = datetime.now(timezone.utc) - timedelta(seconds=45)
    status_delayed = mgr.get_connection_status()
    assert "SENSOR DELAY" in status_delayed["status"]
    assert status_delayed["status_color"] == "#F59E0B"

    # 3. Offline state: > 120s
    mgr.latest_packet_timestamp = datetime.now(timezone.utc) - timedelta(seconds=150)
    status_offline = mgr.get_connection_status()
    assert "SENSOR OFFLINE" in status_offline["status"]
    assert status_offline["status_color"] == "#EF4444"
    assert status_offline["connected"] is False


# ── 4. INCIDENT SCENARIO VERIFICATIONS ────────────────────────────

def test_scenario_normal_water_safe():
    res = engine.predict(ph=7.42, dissolved_oxygen=8.65, turbidity=4.5, specific_conductance=280.0, temperature=21.3)
    assert res["final_status"] == "SAFE"
    assert res["risk_prediction"]["class"] == "SAFE"


def test_scenario_acid_spill_critical():
    res = engine.predict(ph=3.3, dissolved_oxygen=7.2, turbidity=18.0, specific_conductance=890.0, temperature=22.0)
    assert res["final_status"] == "CRITICAL"
    assert "acid" in res["override_reason"].lower() or "ph" in str(res["contributing_parameters"]).lower()


def test_scenario_toxic_heavy_metals_critical():
    res = engine.predict(ph=5.2, dissolved_oxygen=2.1, turbidity=65.0, specific_conductance=1250.0, temperature=24.0, heavy_metal_risk=0.92)
    assert res["final_status"] == "CRITICAL"
    assert res["environmental_risk"] == "CRITICAL"


def test_scenario_eutrophication_critical():
    res = engine.predict(ph=8.9, dissolved_oxygen=2.2, turbidity=28.0, specific_conductance=520.0, temperature=26.5, chlorophyll=45.0, tn_mg_l=18.5, tp_mg_l=1.25)
    assert res["final_status"] == "CRITICAL"
    assert res["environmental_risk"] == "CRITICAL"


# ── 5. REST API TELEMETRY HISTORY ──────────────────────────────────

def test_api_telemetry_history(client):
    resp = client.get("/telemetry/history?limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_records" in data
    assert "history" in data
