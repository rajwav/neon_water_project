"""
NEON Water Intelligence Platform — Autonomous MQTT Telemetry Ingestion Client.
Manages telemetry subscriptions, packet validation, AI pipeline triggers, SQLite history persistence, and connection health.
"""

from collections import deque
from datetime import datetime, timezone
import json
import logging
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from iot.autonomous_sensor import autonomous_sensor
from iot.config import (
    ACTIVE_NODE_ID,
    DEFAULT_BASELINE_TELEMETRY,
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_TOPIC_TELEMETRY,
    OFFLINE_PACKET_THRESHOLD_SEC,
    STALE_PACKET_THRESHOLD_SEC,
    TELEMETRY_INTERVAL_SEC,
)
from iot.database import get_recent_telemetry_records, insert_telemetry_record

logger = logging.getLogger("neon.iot")


class TelemetryIngestionManager:
    """
    Central autonomous telemetry ingestion manager.
    Validates packets, tracks connection health, executes Models 1-5, and stores history in SQLite.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self.node_id = ACTIVE_NODE_ID
        self.latest_telemetry: Dict[str, Any] = dict(DEFAULT_BASELINE_TELEMETRY)
        self.latest_packet_timestamp: Optional[datetime] = None
        self.packet_history: deque = deque(maxlen=120)
        self.total_packets_received: int = 0
        self.invalid_packets_count: int = 0
        
        # Enriched AI Diagnostics cache
        self.cached_ai_result: Optional[Dict[str, Any]] = None
        self._ai_engine = None

    def set_ai_engine(self, engine: Any) -> None:
        """Set the backend AI engine for autonomous real-time inference."""
        self._ai_engine = engine

    def validate_packet(self, packet: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate telemetry packet against physical bounds."""
        if not isinstance(packet, dict):
            return False, "Packet must be a JSON object"

        req_fields = ["ph", "dissolved_oxygen", "turbidity", "temperature", "conductivity"]
        for f in req_fields:
            if f not in packet:
                return False, f"Missing required telemetry channel: {f}"
            try:
                val = float(packet[f])
            except (ValueError, TypeError):
                return False, f"Invalid numeric value for channel: {f}"

        ph = float(packet["ph"])
        if not (0.0 <= ph <= 14.0):
            return False, f"pH {ph} out of physical range [0.0, 14.0]"

        do = float(packet["dissolved_oxygen"])
        if do < 0.0 or do > 30.0:
            return False, f"Dissolved oxygen {do} out of physical range [0.0, 30.0]"

        turb = float(packet["turbidity"])
        if turb < 0.0 or turb > 2000.0:
            return False, f"Turbidity {turb} out of physical range [0.0, 2000.0]"

        cond = float(packet["conductivity"])
        if cond < 0.0 or cond > 10000.0:
            return False, f"Conductivity {cond} out of physical range [0.0, 10000.0]"

        return True, None

    def ingest_packet(self, packet: Dict[str, Any]) -> Tuple[bool, str]:
        """Ingest, validate, store, trigger AI inference, and write to SQLite."""
        is_valid, err_msg = self.validate_packet(packet)
        if not is_valid:
            with self._lock:
                self.invalid_packets_count += 1
            logger.warning(f"Rejected malformed telemetry packet: {err_msg}")
            return False, f"Validation error: {err_msg}"

        now_utc = datetime.now(timezone.utc)
        packet["server_received_at"] = now_utc.isoformat()

        # Trigger AI execution on latest telemetry
        ai_output = self._trigger_ai_inference(packet)

        with self._lock:
            self.latest_telemetry = packet
            self.latest_packet_timestamp = now_utc
            self.packet_history.append(packet)
            self.total_packets_received += 1
            if ai_output:
                self.cached_ai_result = ai_output

        # Persist to SQLite History Table
        try:
            insert_telemetry_record(packet, ai_output)
        except Exception as e:
            logger.error(f"Error persisting telemetry to SQLite: {e}")

        return True, "Packet successfully ingested"

    def _trigger_ai_inference(self, telemetry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute Models 1-5 pipeline on incoming telemetry."""
        if not self._ai_engine:
            try:
                from backend.model_loader import engine
                self._ai_engine = engine
            except Exception as e:
                logger.debug(f"AI engine not loaded: {e}")
                return None

        try:
            input_dict = {
                "ph": float(telemetry.get("ph", 7.42)),
                "dissolved_oxygen": float(telemetry.get("dissolved_oxygen", 8.65)),
                "turbidity": float(telemetry.get("turbidity", 4.5)),
                "temperature": float(telemetry.get("temperature", 21.3)),
                "specific_conductance": float(telemetry.get("conductivity", 280.0)),
                "tn_mg_l": float(telemetry.get("nitrate", 4.5)) if telemetry.get("nitrate") is not None else None,
                "tp_mg_l": float(telemetry.get("phosphate", 0.05)) if telemetry.get("phosphate") is not None else None,
                "heavy_metal_risk": float(telemetry.get("heavy_metal_risk", 0.05)) if telemetry.get("heavy_metal_risk") is not None else None,
                "microbial_risk": float(telemetry.get("microbial_risk", 3.0)) if telemetry.get("microbial_risk") is not None else None,
            }
            res = self._ai_engine.predict(**input_dict)
            return res
        except Exception as e:
            logger.error(f"Error executing AI pipeline on telemetry packet: {e}")
            return None

    def get_connection_status(self) -> Dict[str, Any]:
        """Compute connection status and age of latest telemetry packet."""
        with self._lock:
            latest_ts = self.latest_packet_timestamp
            total_rx = self.total_packets_received
            invalid_rx = self.invalid_packets_count
            latest = dict(self.latest_telemetry)
            ai_res = self.cached_ai_result

        now_utc = datetime.now(timezone.utc)
        if latest_ts is None:
            age_sec = 9999.0
            status = "🔴 SENSOR OFFLINE"
            status_color = "#EF4444"
            connected = False
            last_packet_str = "No Packets Received"
        else:
            age_sec = (now_utc - latest_ts).total_seconds()
            last_packet_str = latest_ts.strftime("%H:%M:%S UTC")
            if age_sec <= STALE_PACKET_THRESHOLD_SEC:
                status = "🟢 Connected"
                status_color = "#10B981"
                connected = True
            elif age_sec <= OFFLINE_PACKET_THRESHOLD_SEC:
                status = "🟡 SENSOR DELAY"
                status_color = "#F59E0B"
                connected = True
            else:
                status = "🔴 SENSOR OFFLINE"
                status_color = "#EF4444"
                connected = False

        return {
            "node_id": self.node_id,
            "status": status,
            "status_color": status_color,
            "connected": connected,
            "packet_age_seconds": round(age_sec, 1),
            "last_packet_time": last_packet_str,
            "total_packets_received": total_rx,
            "invalid_packets_count": invalid_rx,
            "latest_telemetry": latest,
            "ai_result": ai_res,
        }

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent telemetry records from SQLite."""
        return get_recent_telemetry_records(limit=limit)

    def start_pipeline(self) -> None:
        """Start the continuous autonomous virtual sensor pipeline."""
        # Immediately ingest one baseline packet on startup for zero-latency connection
        init_pkt = autonomous_sensor.generate_packet()
        self.ingest_packet(init_pkt)
        autonomous_sensor.start(publish_callback=lambda topic, pkt: self.ingest_packet(pkt))

    def set_sensor_scenario(self, scenario_name: str) -> None:
        """Set simulation scenario on autonomous sensor."""
        autonomous_sensor.set_scenario(scenario_name)
        # Immediately generate and ingest one packet
        pkt = autonomous_sensor.generate_packet()
        self.ingest_packet(pkt)

    def pause_sensor(self) -> None:
        """Simulate sensor failure (for delay/offline tests)."""
        autonomous_sensor.pause_sensor()

    def resume_sensor(self) -> None:
        """Resume autonomous sensor stream."""
        autonomous_sensor.resume_sensor()


# Global singleton instance
telemetry_manager = TelemetryIngestionManager()
# Start autonomous telemetry stream by default for instant live operation
telemetry_manager.start_pipeline()
