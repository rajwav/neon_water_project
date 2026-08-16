"""
NEON Water Intelligence Platform — IoT & MQTT Configuration.
"""

import os
from typing import Dict, Any

MQTT_BROKER_HOST: str = os.getenv("MQTT_BROKER_HOST", "127.0.0.1")
MQTT_BROKER_PORT: int = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_KEEPALIVE_SEC: int = int(os.getenv("MQTT_KEEPALIVE_SEC", "60"))

# Topics
MQTT_TOPIC_TELEMETRY: str = "neon/water/hirakud/telemetry"
MQTT_TOPIC_CONTROL: str = "neon/water/hirakud/control"
MQTT_TOPIC_ALERTS: str = "neon/water/hirakud/alerts"

# Active Node Identification
ACTIVE_NODE_ID: str = "HIRAKUD_NODE_001"
ACTIVE_NODE_LOCATION: str = "Hirakud Reservoir, Mahanadi Basin, Odisha"
ACTIVE_NODE_COORDINATES = [83.872, 21.534]

# Sampling & Latency Thresholds (Seconds)
TELEMETRY_INTERVAL_SEC: float = 10.0
STALE_PACKET_THRESHOLD_SEC: float = 30.0    # 🟡 SENSOR DELAY
OFFLINE_PACKET_THRESHOLD_SEC: float = 120.0  # 🔴 SENSOR OFFLINE

# Default Baseline Sensor Calibration
DEFAULT_BASELINE_TELEMETRY: Dict[str, Any] = {
    "node_id": ACTIVE_NODE_ID,
    "ph": 7.42,
    "dissolved_oxygen": 8.65,
    "turbidity": 4.5,
    "temperature": 21.3,
    "conductivity": 280.0,
    "nitrate": 4.5,
    "phosphate": 0.05,
    "heavy_metal_risk": 0.05,
    "microbial_risk": 3.0,
}
