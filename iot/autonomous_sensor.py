"""
NEON Water Intelligence Platform — Autonomous Virtual Sensor Node (HIRAKUD_NODE_001).
Continuously generates and publishes multi-parameter water quality telemetry packets every 5 seconds.
"""

from datetime import datetime, timezone
import json
import logging
import random
import threading
import time
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("neon.sensor")

MQTT_TOPIC_TELEMETRY = "neon/water/hirakud/telemetry"
ACTIVE_NODE_ID = "HIRAKUD_NODE_001"
DEFAULT_INTERVAL_SEC = 5.0


from iot.sensor_simulator import HirakudVirtualSensorNode


class AutonomousSensorNode:
    """
    Autonomous in-situ multiparameter sonde for Hirakud Reservoir.
    Generates continuous live telemetry packets every 5 seconds using
    physics-informed diurnal solar, DO solubility, and plume advection modeling.
    """

    def __init__(self, node_id: str = ACTIVE_NODE_ID, interval_sec: float = DEFAULT_INTERVAL_SEC):
        self.node_id = node_id
        self.interval_sec = interval_sec
        self.active_scenario: Optional[str] = "normal"
        self._is_active: bool = True
        self._packet_count: int = 0
        self._thread: Optional[threading.Thread] = None
        self._publish_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
        self._engine = HirakudVirtualSensorNode(node_id=node_id)

    def set_scenario(self, scenario_name: str) -> None:
        """Set active simulation scenario: 'normal', 'acid_spill', 'toxic_waste', 'eutrophication'."""
        self.active_scenario = scenario_name.lower().strip()
        self._engine.set_incident_scenario(self.active_scenario)
        logger.info(f"Sensor scenario set to: {self.active_scenario}")

    def pause_sensor(self) -> None:
        """Pause packet generation to simulate network or sensor hardware failure."""
        self._is_active = False
        logger.warning(f"Sensor {self.node_id} paused (simulating failure)")

    def resume_sensor(self) -> None:
        """Resume packet generation."""
        self._is_active = True
        logger.info(f"Sensor {self.node_id} resumed")

    def generate_packet(self) -> Dict[str, Any]:
        """Generate a validated physical telemetry packet."""
        self._packet_count += 1
        return self._engine.generate_telemetry_packet()

    def start(self, publish_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None) -> None:
        """Start the background autonomous 5-second publisher loop."""
        if self._thread and self._thread.is_alive():
            return
        self._publish_callback = publish_callback

        def _run_loop():
            logger.info(f"Autonomous sensor loop started for {self.node_id} (Interval: {self.interval_sec}s)")
            while True:
                if self._is_active:
                    pkt = self.generate_packet()
                    if self._publish_callback:
                        try:
                            self._publish_callback(MQTT_TOPIC_TELEMETRY, pkt)
                        except Exception as e:
                            logger.error(f"Error in publish callback: {e}")
                time.sleep(self.interval_sec)

        self._thread = threading.Thread(target=_run_loop, daemon=True, name="AutonomousSensorThread")
        self._thread.start()


# Standalone autonomous sensor instance
autonomous_sensor = AutonomousSensorNode(node_id=ACTIVE_NODE_ID, interval_sec=5.0)
