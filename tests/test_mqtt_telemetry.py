"""
Unit and Integration Tests for NEON Autonomous MQTT IoT Telemetry Pipeline.
"""

from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from iot.config import ACTIVE_NODE_ID, MQTT_TOPIC_TELEMETRY
from iot.mqtt_client import TelemetryIngestionManager
from iot.sensor_simulator import HirakudVirtualSensorNode


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def clean_manager():
    mgr = TelemetryIngestionManager()
    mgr.stop_autonomous_sensor_stream()
    return mgr


# ── 1. SENSOR SIMULATOR TESTS ──────────────────────────────────────

def test_sensor_simulator_baseline_generation():
    node = HirakudVirtualSensorNode(node_id="HIRAKUD_NODE_001")
    pkt = node.generate_telemetry_packet()

    assert pkt["node_id"] == "HIRAKUD_NODE_001"
    assert "timestamp" in pkt
    assert 6.0 <= pkt["ph"] <= 9.0
    assert 4.0 <= pkt["dissolved_oxygen"] <= 14.0
    assert 0.0 <= pkt["turbidity"] <= 30.0
    assert 10.0 <= pkt["temperature"] <= 35.0
    assert 50.0 <= pkt["conductivity"] <= 600.0


def test_sensor_simulator_incident_injection():
    node = HirakudVirtualSensorNode(node_id="HIRAKUD_NODE_001")

    # Acid Spill
    node.set_incident_scenario("acid_spill")
    acid_pkt = node.generate_telemetry_packet()
    assert acid_pkt["ph"] < 5.5
    assert acid_pkt["heavy_metal_risk"] > 0.5

    # Eutrophication
    node.set_incident_scenario("eutrophication")
    eutro_pkt = node.generate_telemetry_packet()
    assert eutro_pkt["ph"] > 8.0
    assert eutro_pkt["dissolved_oxygen"] < 4.0
    assert eutro_pkt["nitrate"] > 10.0

    # Toxic Waste
    node.set_incident_scenario("toxic_waste")
    toxic_pkt = node.generate_telemetry_packet()
    assert toxic_pkt["turbidity"] > 40.0
    assert toxic_pkt["heavy_metal_risk"] > 0.8


# ── 2. TELEMETRY VALIDATION TESTS ──────────────────────────────────

def test_telemetry_validation_success(clean_manager):
    valid_pkt = {
        "node_id": "HIRAKUD_NODE_001",
        "ph": 7.42,
        "dissolved_oxygen": 8.65,
        "turbidity": 4.5,
        "temperature": 21.3,
        "conductivity": 280.0,
        "nitrate": 4.5,
        "phosphate": 0.05,
    }
    is_valid, err = clean_manager.validate_packet(valid_pkt)
    assert is_valid is True
    assert err is None


def test_telemetry_validation_out_of_bounds(clean_manager):
    # Invalid pH
    bad_ph_pkt = {"ph": 15.5, "dissolved_oxygen": 8.0, "turbidity": 5.0, "temperature": 20.0, "conductivity": 300.0}
    is_valid, err = clean_manager.validate_packet(bad_ph_pkt)
    assert is_valid is False
    assert "pH" in err

    # Negative DO
    bad_do_pkt = {"ph": 7.0, "dissolved_oxygen": -2.0, "turbidity": 5.0, "temperature": 20.0, "conductivity": 300.0}
    is_valid, err = clean_manager.validate_packet(bad_do_pkt)
    assert is_valid is False
    assert "Dissolved oxygen" in err


# ── 3. INGESTION & STATUS TRACKING ─────────────────────────────────

def test_telemetry_ingestion_and_health_tracking(clean_manager):
    pkt = {
        "node_id": "HIRAKUD_NODE_001",
        "ph": 7.35,
        "dissolved_oxygen": 8.40,
        "turbidity": 3.8,
        "temperature": 21.0,
        "conductivity": 275.0,
    }
    ok, msg = clean_manager.ingest_packet(pkt)
    assert ok is True

    status = clean_manager.get_connection_status()
    assert status["connected"] is True
    assert "Connected" in status["status"]
    assert status["total_packets_received"] == 1
    assert status["latest_telemetry"]["ph"] == 7.35


def test_telemetry_stale_and_offline_transitions(clean_manager):
    pkt = {"node_id": "HIRAKUD_NODE_001", "ph": 7.0, "dissolved_oxygen": 8.0, "turbidity": 5.0, "temperature": 20.0, "conductivity": 300.0}
    clean_manager.ingest_packet(pkt)

    # Simulate 40s delay
    clean_manager.latest_packet_timestamp = datetime.now(timezone.utc) - timedelta(seconds=45)
    stale_status = clean_manager.get_connection_status()
    assert "SENSOR DELAY" in stale_status["status"]

    # Simulate 150s offline
    clean_manager.latest_packet_timestamp = datetime.now(timezone.utc) - timedelta(seconds=150)
    offline_status = clean_manager.get_connection_status()
    assert "SENSOR OFFLINE" in offline_status["status"]
    assert offline_status["connected"] is False


# ── 4. FASTAPI TELEMETRY ENDPOINTS ─────────────────────────────────

def test_fastapi_telemetry_live_endpoint(client):
    resp = client.get("/telemetry/live")
    assert resp.status_code == 200
    data = resp.json()
    assert "node_id" in data
    assert "status" in data
    assert "latest_telemetry" in data
    assert "ph" in data["latest_telemetry"]


def test_fastapi_telemetry_status_endpoint(client):
    resp = client.get("/telemetry/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["node_id"] == ACTIVE_NODE_ID
    assert "connected" in data


def test_fastapi_telemetry_publish_endpoint(client):
    test_pkt = {
        "node_id": "HIRAKUD_NODE_001",
        "ph": 7.45,
        "dissolved_oxygen": 8.70,
        "turbidity": 4.1,
        "temperature": 21.1,
        "conductivity": 282.0,
        "nitrate": 3.8,
        "phosphate": 0.04,
        "heavy_metal_risk": 0.04,
        "microbial_risk": 2.5,
    }
    resp = client.post("/telemetry/publish", json=test_pkt)
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["status"] == "success"

    # Verify live endpoint reflects the published values
    live_resp = client.get("/telemetry/live")
    assert live_resp.status_code == 200
    live_data = live_resp.json()
    assert live_data["latest_telemetry"]["ph"] == 7.45
