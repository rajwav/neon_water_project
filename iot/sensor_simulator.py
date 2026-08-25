"""
NEON Water Intelligence Platform — Autonomous Virtual Sensor Node Simulator.
Simulates in-situ multiparameter water quality sonde deployed at Hirakud Reservoir (HIRAKUD_NODE_001).
"""

from datetime import datetime, timezone
import json
import random
import time
from typing import Any, Callable, Dict, Optional

import numpy as np

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
        self.base_nitrate = 0.45
        self.base_phosphate = 0.015
        self.base_heavy_metal = 0.02
        self.base_microbial = 3.5

        # Active injected incident scenario (if any)
        self.active_incident: Optional[str] = None
        self.incident_step_counter = 0
        self.packet_counter = 0

    def set_incident_scenario(self, incident_type: Optional[str]) -> None:
        """Inject an intentional contamination scenario for testing."""
        if self.active_incident != incident_type:
            self.active_incident = incident_type
            self.incident_step_counter = 0

    def generate_telemetry_packet(self) -> Dict[str, Any]:
        """Generate a timestamped sensor telemetry packet with physics-informed diurnal cycles."""
        self.packet_counter += 1
        now = datetime.now(timezone.utc)
        now_utc = now.isoformat()

        # 1. Physics: Solar Diurnal Cycle based on current UTC hour
        hour_fraction = now.hour + now.minute / 60.0 + now.second / 3600.0
        # Peak thermal radiation at 15:00 local time
        temp_cycle = 2.5 * np.sin(2 * np.pi * (hour_fraction - 9.0) / 24.0)
        temp = round(self.base_temp + temp_cycle + random.gauss(0.0, 0.08), 2)

        # 2. Physics: Dissolved Oxygen saturation equilibrium (Henry's law & water temperature)
        # Saturated DO at temperature T
        do_sat = 14.652 - 0.41022 * temp + 0.007991 * (temp ** 2) - 0.000077774 * (temp ** 3)
        # Photosynthetic diurnal swing (algae produce DO during midday, net respiration deficit at dawn)
        photo_flux = 0.08 * np.sin(2 * np.pi * (hour_fraction - 8.0) / 24.0)
        base_calc_do = do_sat * (0.92 + photo_flux)
        do = round(max(0.0, base_calc_do + random.gauss(0.0, 0.06)), 2)

        # 3. Physics: Carbonic acid equilibrium & diurnal pH swing
        # (Algal CO2 uptake in daylight reduces carbonic acid H2CO3, slightly elevating pH)
        ph_cycle = 0.12 * np.sin(2 * np.pi * (hour_fraction - 8.0) / 24.0)
        ph = round(max(0.0, min(14.0, self.base_ph + ph_cycle + random.gauss(0.0, 0.02))), 2)

        # 4. Specific conductance with thermal compensation (+1.9% per degree C above 20C)
        cond_temp_factor = 1.0 + 0.019 * (temp - 20.0)
        cond = round(max(10.0, self.base_cond * cond_temp_factor + random.gauss(0.0, 1.5)), 1)

        turb = round(max(1.0, random.gauss(self.base_turbidity, 0.15)), 2)
        nitrate = round(max(0.1, random.gauss(self.base_nitrate, 0.02)), 2)
        phosphate = round(max(0.005, random.gauss(self.base_phosphate, 0.002)), 3)
        hm_risk = round(max(0.005, min(0.15, random.gauss(self.base_heavy_metal, 0.005))), 3)
        micro_risk = round(max(0.0, min(15.0, random.gauss(self.base_microbial, 0.3))), 1)

        # 5. Continuous Plume Advection & Dispersion for Injected Scenarios
        if self.active_incident:
            self.incident_step_counter += 1
            # Sigmoid plume arrival curve: alpha goes from 0.35 to 1.0 smoothly over steps
            alpha = min(1.0, 0.35 + 0.65 / (1.0 + np.exp(-0.6 * (self.incident_step_counter - 4))))

            if "acid" in self.active_incident:
                # Industrial Acid Spill: pH crashes, conductivity surges from dissociated hydronium/sulfate ions
                target_ph = 2.80 + random.gauss(0.0, 0.05)
                target_cond = 1450.0 + random.gauss(0.0, 25.0)
                target_turb = 28.0 + random.gauss(0.0, 1.5)
                target_do = max(3.0, do - 3.5)
                target_hm = 0.65

                ph = round(ph * (1.0 - alpha) + target_ph * alpha, 2)
                cond = round(cond * (1.0 - alpha) + target_cond * alpha, 1)
                turb = round(turb * (1.0 - alpha) + target_turb * alpha, 2)
                do = round(do * (1.0 - alpha) + target_do * alpha, 2)
                hm_risk = round(hm_risk * (1.0 - alpha) + target_hm * alpha, 3)

            elif "eutro" in self.active_incident:
                # Eutrophication: Nitrogen/Phosphorus spike, severe nocturnal/secondary anoxia
                target_nitrate = 14.5 + random.gauss(0.0, 0.8)
                target_phosphate = 0.22 + random.gauss(0.0, 0.02)
                target_do = 1.80 + random.gauss(0.0, 0.15)
                target_turb = 35.0 + random.gauss(0.0, 2.0)
                target_ph = 8.85 + random.gauss(0.0, 0.08)

                nitrate = round(nitrate * (1.0 - alpha) + target_nitrate * alpha, 2)
                phosphate = round(phosphate * (1.0 - alpha) + target_phosphate * alpha, 3)
                do = round(do * (1.0 - alpha) + target_do * alpha, 2)
                turb = round(turb * (1.0 - alpha) + target_turb * alpha, 2)
                ph = round(ph * (1.0 - alpha) + target_ph * alpha, 2)

            elif "toxic" in self.active_incident:
                # Toxic Heavy Metal & Industrial Chemical Contamination
                target_hm = 0.88 + random.gauss(0.0, 0.02)
                target_cond = 1180.0 + random.gauss(0.0, 30.0)
                target_ph = 5.60 + random.gauss(0.0, 0.1)
                target_do = 2.20 + random.gauss(0.0, 0.15)
                target_turb = 65.0 + random.gauss(0.0, 3.0)

                hm_risk = round(hm_risk * (1.0 - alpha) + target_hm * alpha, 3)
                cond = round(cond * (1.0 - alpha) + target_cond * alpha, 1)
                ph = round(ph * (1.0 - alpha) + target_ph * alpha, 2)
                do = round(do * (1.0 - alpha) + target_do * alpha, 2)
                turb = round(turb * (1.0 - alpha) + target_turb * alpha, 2)

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
