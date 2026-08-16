"""
NEON Water Intelligence Platform — Autonomous Virtual Sensor Node Simulator.
Simulates in-situ multiparameter water quality sonde deployed at Hirakud Reservoir (HIRAKUD_NODE_001).
"""

from datetime import datetime, timezone
import json
import random
import time
from typing import Any, Callable, Dict, Optional

from iot.config import (
    ACTIVE_NODE_ID,
    MQTT_TOPIC_TELEMETRY,
    TELEMETRY_INTERVAL_SEC,
)


class HirakudVirtualSensorNode:
    """
    Autonomous multi-parameter water sensor node simulator for Hirakud Reservoir.
    Simulates optical DO, glass pH electrode, nephelometric turbidity, 4-electrode conductivity cell,
    and thermistor with physical stochastic variance.
    """

    def __init__(self, node_id: str = ACTIVE_NODE_ID):
        self.node_id = node_id
        # Baseline physical state
        self.base_ph = 7.42
        self.base_do = 8.65
        self.base_turbidity = 4.50
        self.base_temp = 21.30
        self.base_cond = 280.0
        self.base_nitrate = 4.20
        self.base_phosphate = 0.05
        self.base_heavy_metal = 0.06
        self.base_microbial = 3.5

        # Active injected incident scenario (if any)
        self.active_incident: Optional[str] = None
        self.packet_counter = 0

    def set_incident_scenario(self, incident_type: Optional[str]) -> None:
        """Inject an intentional contamination scenario for testing."""
        self.active_incident = incident_type

    def generate_telemetry_packet(self) -> Dict[str, Any]:
        """Generate a single timestamped sensor telemetry packet with natural physical variance."""
        self.packet_counter += 1
        now_utc = datetime.now(timezone.utc).isoformat()

        if self.active_incident == "acid_spill":
            ph = round(max(2.0, min(14.0, random.gauss(3.8, 0.2))), 2)
            do = round(max(0.1, min(15.0, random.gauss(7.2, 0.4))), 2)
            turb = round(max(0.1, random.gauss(18.5, 2.0)), 2)
            temp = round(random.gauss(22.8, 0.5), 2)
            cond = round(max(50.0, random.gauss(840.0, 30.0)), 1)
            nitrate = round(max(0.1, random.gauss(6.5, 0.5)), 2)
            phosphate = round(max(0.01, random.gauss(0.12, 0.02)), 3)
            hm_risk = round(min(1.0, random.gauss(0.75, 0.05)), 3)
            micro_risk = round(random.gauss(12.0, 2.0), 1)
        elif self.active_incident == "eutrophication":
            ph = round(max(2.0, min(14.0, random.gauss(8.9, 0.2))), 2)
            do = round(max(0.1, min(15.0, random.gauss(2.4, 0.3))), 2)
            turb = round(max(0.1, random.gauss(28.0, 3.0)), 2)
            temp = round(random.gauss(26.5, 0.4), 2)
            cond = round(max(50.0, random.gauss(520.0, 20.0)), 1)
            nitrate = round(max(0.1, random.gauss(18.5, 1.5)), 2)
            phosphate = round(max(0.01, random.gauss(1.25, 0.1)), 3)
            hm_risk = round(min(1.0, random.gauss(0.15, 0.03)), 3)
            micro_risk = round(random.gauss(45.0, 5.0), 1)
        elif self.active_incident == "toxic_waste":
            ph = round(max(2.0, min(14.0, random.gauss(5.2, 0.3))), 2)
            do = round(max(0.1, min(15.0, random.gauss(1.8, 0.3))), 2)
            turb = round(max(0.1, random.gauss(65.0, 5.0)), 2)
            temp = round(random.gauss(24.0, 0.6), 2)
            cond = round(max(50.0, random.gauss(1250.0, 50.0)), 1)
            nitrate = round(max(0.1, random.gauss(22.0, 2.0)), 2)
            phosphate = round(max(0.01, random.gauss(2.1, 0.2)), 3)
            hm_risk = round(min(1.0, random.gauss(0.92, 0.03)), 3)
            micro_risk = round(random.gauss(88.0, 6.0), 1)
        else:
            # Baseline natural fluctuations
            ph = round(max(6.5, min(8.5, random.gauss(self.base_ph, 0.06))), 2)
            do = round(max(5.0, min(12.0, random.gauss(self.base_do, 0.15))), 2)
            turb = round(max(1.0, min(15.0, random.gauss(self.base_turbidity, 0.25))), 2)
            temp = round(max(15.0, min(28.0, random.gauss(self.base_temp, 0.20))), 2)
            cond = round(max(100.0, min(450.0, random.gauss(self.base_cond, 5.0))), 1)
            nitrate = round(max(0.5, min(10.0, random.gauss(self.base_nitrate, 0.20))), 2)
            phosphate = round(max(0.01, min(0.20, random.gauss(self.base_phosphate, 0.005))), 3)
            hm_risk = round(max(0.01, min(0.30, random.gauss(self.base_heavy_metal, 0.01))), 3)
            micro_risk = round(max(0.0, min(10.0, random.gauss(self.base_microbial, 0.5))), 1)

        packet = {
            "node_id": self.node_id,
            "packet_id": self.packet_counter,
            "timestamp": now_utc,
            "ph": ph,
            "dissolved_oxygen": do,
            "turbidity": turb,
            "temperature": temp,
            "conductivity": cond,
            "nitrate": nitrate,
            "phosphate": phosphate,
            "heavy_metal_risk": hm_risk,
            "microbial_risk": micro_risk,
            "location": "Hirakud Reservoir Inflow, Odisha",
            "battery_pct": 98.5,
            "signal_rssi_dbm": -68,
        }
        return packet

    def run_publisher_loop(
        self,
        publish_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        interval_sec: float = TELEMETRY_INTERVAL_SEC,
        max_packets: Optional[int] = None,
    ) -> None:
        """Run continuous autonomous telemetry publication."""
        count = 0
        while True:
            packet = self.generate_telemetry_packet()
            if publish_callback:
                publish_callback(MQTT_TOPIC_TELEMETRY, packet)
            count += 1
            if max_packets and count >= max_packets:
                break
            time.sleep(interval_sec)


# Standalone runner
if __name__ == "__main__":
    node = HirakudVirtualSensorNode()
    print(f"Starting autonomous sensor stream for {node.node_id} (Topic: {MQTT_TOPIC_TELEMETRY})...")
    for _ in range(5):
        pkt = node.generate_telemetry_packet()
        print(f"[{pkt['timestamp']}] Published: pH={pkt['ph']}, DO={pkt['dissolved_oxygen']} mg/L, Turb={pkt['turbidity']} FNU, Cond={pkt['conductivity']} uS/cm")
        time.sleep(1.0)
