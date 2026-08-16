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


class AutonomousSensorNode:
    """
    Autonomous in-situ multiparameter sonde for Hirakud Reservoir.
    Generates continuous live telemetry packets every 5 seconds.
    """

    def __init__(self, node_id: str = ACTIVE_NODE_ID, interval_sec: float = DEFAULT_INTERVAL_SEC):
        self.node_id = node_id
        self.interval_sec = interval_sec
        self.active_scenario: Optional[str] = "normal"
        self._is_active: bool = True
        self._packet_count: int = 0
        self._thread: Optional[threading.Thread] = None
        self._publish_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None

    def set_scenario(self, scenario_name: str) -> None:
        """Set active simulation scenario: 'normal', 'acid_spill', 'toxic_waste', 'eutrophication'."""
        self.active_scenario = scenario_name.lower().strip()
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
        now_utc = datetime.now(timezone.utc).isoformat()
        sc = self.active_scenario or "normal"

        if "acid" in sc:
            # Lethal acidification scenario
            ph = round(random.uniform(3.2, 3.6), 2)
            do = round(random.uniform(7.0, 7.8), 2)
            turb = round(random.uniform(16.0, 22.0), 2)
            cond = round(random.uniform(850.0, 920.0), 1)
            temp = round(random.uniform(21.8, 22.8), 2)
            nitrate = round(random.uniform(5.5, 7.0), 2)
            phosphate = round(random.uniform(0.08, 0.15), 3)
            heavy_metal = round(random.uniform(0.65, 0.85), 3)
        elif "toxic" in sc:
            # Toxic chemical & heavy metal contamination
            ph = round(random.uniform(5.0, 5.5), 2)
            do = round(random.uniform(1.5, 2.5), 2)
            turb = round(random.uniform(55.0, 75.0), 2)
            cond = round(random.uniform(1150.0, 1350.0), 1)
            temp = round(random.uniform(23.5, 24.8), 2)
            nitrate = round(random.uniform(18.0, 24.0), 2)
            phosphate = round(random.uniform(1.8, 2.4), 3)
            heavy_metal = round(random.uniform(0.85, 0.98), 3)
        elif "eutro" in sc:
            # Eutrophication & algal bloom
            ph = round(random.uniform(8.7, 9.2), 2)
            do = round(random.uniform(1.8, 2.6), 2)
            turb = round(random.uniform(24.0, 32.0), 2)
            cond = round(random.uniform(500.0, 560.0), 1)
            temp = round(random.uniform(26.0, 27.5), 2)
            nitrate = round(random.uniform(16.0, 21.0), 2)
            phosphate = round(random.uniform(1.1, 1.5), 3)
            heavy_metal = round(random.uniform(0.10, 0.20), 3)
        else:
            # Normal pristine baseline with natural micro-fluctuations
            ph = round(random.gauss(7.42, 0.05), 2)
            do = round(random.gauss(8.65, 0.12), 2)
            turb = round(max(1.0, random.gauss(4.5, 0.2)), 2)
            cond = round(random.gauss(280.0, 4.0), 1)
            temp = round(random.gauss(21.3, 0.15), 2)
            nitrate = round(random.gauss(4.2, 0.15), 2)
            phosphate = round(max(0.01, random.gauss(0.05, 0.005)), 3)
            heavy_metal = round(max(0.01, random.gauss(0.05, 0.01)), 3)

        packet = {
            "node_id": self.node_id,
            "packet_id": self._packet_count,
            "timestamp": now_utc,
            "ph": ph,
            "dissolved_oxygen": do,
            "turbidity": turb,
            "conductivity": cond,
            "temperature": temp,
            "nitrate": nitrate,
            "phosphate": phosphate,
            "heavy_metal_risk": heavy_metal,
            "microbial_risk": 3.2 if "toxic" not in sc else 85.0,
            "location": "Hirakud Reservoir Inflow Reach, Odisha",
        }
        return packet

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
