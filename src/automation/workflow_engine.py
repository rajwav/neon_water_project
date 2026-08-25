"""
AquaNeon SCADA-Compatible Industrial Automation Workflow Engine & Notification Router.
Full operational simulation dashboard backing:
1. Live Incident Command Header
2. 7-Step Real-Time Event Execution Timeline
3. Digital Twin 5-Equipment Actuation State
4. SCADA Simulation Console & Commands
5. n8n Visual Workflow Execution States
6. Authority Emergency Notification Dispatch
7. Terminal-Style Console Event Logs
8. Recipient Acknowledgement Tracking
"""

from datetime import datetime, timezone, timedelta
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("neon.automation")


class AuthorityNotificationRouter:
    """
    📡 Authority Notification Router (Simulation Layer).
    """

    def __init__(self):
        self.acknowledgement_ledger: List[Dict[str, Any]] = [
            {
                "Recipient": "Dr. P. Mohanty",
                "Role": "SPCB Regional Officer (Pollution Control)",
                "Channel": "Email + SMS Simulation",
                "Status": "Action Taken",
                "Timestamp": "10:33:04",
            },
            {
                "Recipient": "Er. A. K. Nayak",
                "Role": "Municipal Water Authority",
                "Channel": "Webhook + SMS Simulation",
                "Status": "Received",
                "Timestamp": "10:33:18",
            },
            {
                "Recipient": "S. Jena",
                "Role": "Treatment Plant Operator",
                "Channel": "SCADA Advisory",
                "Status": "Action Required",
                "Timestamp": "10:32:45",
            },
            {
                "Recipient": "HazMat Quick Response Unit",
                "Role": "Emergency Response Team",
                "Channel": "Dispatch Simulation",
                "Status": "Pending",
                "Timestamp": "10:34:02",
            },
        ]

    def route_notification(
        self,
        final_status: str,
        ai_result: Dict[str, Any],
        control_mode: str,
        detected_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        now = datetime.now()
        now_str = now.strftime("%H:%M:%S")
        now_iso = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        decision_support = ai_result.get("decision_support", {})
        incident_name = decision_support.get("incident", "Water Quality Assessment")
        m2_block = ai_result.get("risk_prediction", ai_result.get("risk_classification", {}))

        m5_conf = float(decision_support.get("confidence", 95.0))
        m2_conf = float(m2_block.get("confidence", 0.95)) * 100.0
        ai_conf = round(max(m5_conf, m2_conf), 1)

        stat_upper = final_status.upper()
        incident_id = f"INC-2026-{now.strftime('%m%d')}-01"
        location_str = "Hirakud Dam Raw Water Intake (Digital Twin Node #001)"

        params = detected_params or {
            "pH": 7.42,
            "dissolved_oxygen_mg_l": 8.65,
            "turbidity_ntu": 4.5,
            "specific_conductance_us_cm": 280.0,
            "temperature_c": 21.3,
        }

        if stat_upper == "CRITICAL":
            wf_id = "WF-NOTIFY-001"
            wf_name = "🚨 Critical Emergency Response Protocol"
            severity_label = "CRITICAL"
            severity_color = "#EF4444"
            status_text = "🔴 CRITICAL RESPONSE ACTIVE" if control_mode != "Advisory Mode" else "QUEUED (Awaiting Operator Sign-Off)"

            stakeholders = [
                {
                    "name": "Dr. P. Mohanty (SPCB)",
                    "role": "SPCB Regional Pollution Officer",
                    "reason": "Regulatory contamination event",
                    "channel": "Email + SMS Simulation",
                    "status": "✓ Notification Generated",
                    "ack": "Action Taken",
                    "icon": "🏢",
                },
                {
                    "name": "Er. A. K. Nayak (Muni)",
                    "role": "Municipal Water Authority",
                    "reason": "Public water safety & reservoir switch",
                    "channel": "Webhook + SMS Simulation",
                    "status": "✓ Received",
                    "ack": "Received",
                    "icon": "🏛️",
                },
                {
                    "name": "S. Jena (Plant Operator)",
                    "role": "Treatment Plant Operator",
                    "reason": "Operational adjustment (Intake closure)",
                    "channel": "SCADA Advisory",
                    "status": "✓ Action Required",
                    "ack": "Action Taken (Valve Closed)",
                    "icon": "🏭",
                },
                {
                    "name": "HazMat Emergency Team",
                    "role": "Emergency Response Team",
                    "reason": "In-situ field verification & containment",
                    "channel": "Dispatch Simulation",
                    "status": "Pending",
                    "ack": "Pending (En Route)",
                    "icon": "🚨",
                },
            ]

            rec_action = "Immediate raw water intake valve shutoff (VALVE_CLOSE_REQUEST), dispatch emergency HazMat sampling team, and switch municipal supply to auxiliary reservoir."
            manifest_hash = hashlib.sha256(f"{incident_id}-{now_iso}-{stat_upper}-CPCB33A".encode()).hexdigest()

        elif stat_upper in ["WARNING", "HIGH", "MEDIUM"]:
            wf_id = "WF-NOTIFY-002"
            wf_name = "🟡 Early-Intervention & Adaptive Monitoring Protocol"
            severity_label = "WARNING"
            severity_color = "#F59E0B"
            status_text = "🟡 WARNING INTERVENTION ACTIVE" if control_mode != "Advisory Mode" else "QUEUED (Awaiting Operator Sign-Off)"

            stakeholders = [
                {
                    "name": "Watershed Field Cell",
                    "role": "Municipal Water Authority",
                    "reason": "Elevated runoff advisory",
                    "channel": "Webhook + SMS Simulation",
                    "status": "✓ Received",
                    "ack": "Received",
                    "icon": "🏛️",
                },
                {
                    "name": "SPCB Zonal Desk",
                    "role": "SPCB Regional Pollution Officer",
                    "reason": "Catchment parameter drift",
                    "channel": "Email + SMS Simulation",
                    "status": "✓ Notification Generated",
                    "ack": "Received",
                    "icon": "🏢",
                },
                {
                    "name": "Dosing Control Operator",
                    "role": "Treatment Plant Operator",
                    "reason": "Chemical coagulant dosage adjustment",
                    "channel": "SCADA Advisory",
                    "status": "✓ Action Required",
                    "ack": "Action Taken (+15% Coagulant)",
                    "icon": "🧪",
                },
            ]

            rec_action = "Increase in-situ telemetry sampling frequency from 15s to 2s, verify coagulant chemical dosing rate (+15% Alum), and inspect upstream agricultural drainage channels."
            manifest_hash = hashlib.sha256(f"{incident_id}-{now_iso}-{stat_upper}-ADVISORY".encode()).hexdigest()

        else:
            wf_id = "WF-NOTIFY-003"
            wf_name = "🟢 Safe Baseline & Continuous Archival Protocol"
            severity_label = "SAFE"
            severity_color = "#10B981"
            status_text = "🟢 NOMINAL SURVEILLANCE ACTIVE"

            stakeholders = [
                {
                    "name": "Surveillance Duty Desk",
                    "role": "Internal Monitoring Team",
                    "reason": "Daily hydrological compliance report",
                    "channel": "Email Digest Simulation",
                    "status": "✓ Generated",
                    "ack": "Closed",
                    "icon": "📊",
                },
                {
                    "name": "Central Cloud Ledger",
                    "role": "SPCB Cloud Heartbeat",
                    "reason": "Continuous baseline telemetry commit",
                    "channel": "MQTT QoS 1 Simulation",
                    "status": "✓ Committed",
                    "ack": "Closed",
                    "icon": "💾",
                },
            ]

            rec_action = "Maintain continuous standard baseline telemetry monitoring at nominal 5-second sampling intervals."
            manifest_hash = hashlib.sha256(f"{incident_id}-{now_iso}-{stat_upper}-NOMINAL".encode()).hexdigest()

        alert_payload = {
            "incident_id": incident_id,
            "location": location_str,
            "detected_event": incident_name,
            "severity": f"{severity_label} (Level {'4' if stat_upper == 'CRITICAL' else ('2' if stat_upper in ['WARNING', 'HIGH', 'MEDIUM'] else '0')})",
            "ai_confidence": f"{ai_conf:.1f}%",
            "parameters": params,
            "recommended_action": rec_action,
            "timestamp": now_iso,
            "verification_signature_sha256": f"{manifest_hash[:16]}...{manifest_hash[-8:]}",
        }

        # n8n Visual Nodes with Execution States
        flow_nodes = [
            {"name": "AI Trigger Node", "type": "ai_trigger", "icon": "🧠", "state": "COMPLETED", "details": f"Evaluated: {severity_label} ({ai_conf}% Conf)"},
            {"name": "Severity Router", "type": "router", "icon": "🔀", "state": "COMPLETED", "details": f"{severity_label} PATH SELECTED"},
            {"name": "Email Node", "type": "email", "icon": "📧", "state": "COMPLETED", "details": "PAYLOAD CREATED"},
            {"name": "SMS Node", "type": "sms", "icon": "📲", "state": "COMPLETED" if stat_upper == "CRITICAL" else "STANDBY", "details": "PRIORITY ALERT GENERATED" if stat_upper == "CRITICAL" else "Standing by"},
            {"name": "Webhook Node", "type": "webhook", "icon": "🌐", "state": "COMPLETED", "details": "MUNICIPAL API PAYLOAD GENERATED"},
            {"name": "Audit Node", "type": "audit", "icon": "📑", "state": "COMPLETED", "details": "INCIDENT HASH STORED"},
        ]

        ack_rows = [
            {
                "Recipient": s["name"],
                "Role": s["role"],
                "Reason": s.get("reason", "Water Quality Surveillance"),
                "Channel": s["channel"],
                "Status": s["status"],
                "Ack State": s["ack"],
                "Timestamp": now_str,
            }
            for s in stakeholders
        ]

        return {
            "workflow_id": wf_id,
            "workflow_name": wf_name,
            "notification_status": status_text,
            "severity": severity_label,
            "severity_color": severity_color,
            "incident_id": incident_id,
            "location": location_str,
            "detected_event": incident_name,
            "ai_confidence": f"{ai_conf:.1f}%",
            "recommended_action": rec_action,
            "message_preview": f"{severity_label}: {incident_name} at {location_str}. Recommended action: {rec_action}",
            "stakeholders": stakeholders,
            "target_groups": [s["role"] for s in stakeholders],
            "alert_payload": alert_payload,
            "flow_nodes": flow_nodes,
            "acknowledgements": ack_rows,
            "history": self.acknowledgement_ledger,
        }


class AutomationWorkflowEngine:
    """
    Industrial Event-Driven Automation Workflow Engine (Simulation).
    """

    def __init__(self):
        self.control_mode: str = "Autonomous Simulation Mode"
        self.notification_router = AuthorityNotificationRouter()
        self.execution_logs: List[Dict[str, Any]] = [
            {
                "Time": "10:32:15",
                "Status": "SAFE",
                "Workflow": "WF-003",
                "Action": "Data archival & SPCB pulse",
                "Latency": "11ms",
            },
            {
                "Time": "10:45:00",
                "Status": "WARNING",
                "Workflow": "WF-002",
                "Action": "Sampling rate shift (2s) & advisory",
                "Latency": "22ms",
            },
        ]

    def set_control_mode(self, mode: str) -> None:
        """Set Human-In-The-Loop Control Mode."""
        if mode in ["Autonomous Simulation Mode", "Assisted Mode", "Advisory Mode"]:
            self.control_mode = mode

    def evaluate_and_trigger(
        self,
        ai_result: Dict[str, Any],
        control_mode: Optional[str] = None,
        raw_params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        if control_mode:
            self.set_control_mode(control_mode)

        now = datetime.now()
        now_str = now.strftime("%H:%M:%S")
        final_status = ai_result.get("final_status", "SAFE").upper()
        stat_upper = final_status
        decision_support = ai_result.get("decision_support", {})
        incident_name = decision_support.get("incident", "Water Quality Assessment")
        m2_block = ai_result.get("risk_prediction", ai_result.get("risk_classification", {}))

        m5_conf = float(decision_support.get("confidence", 95.0))
        m2_conf = float(m2_block.get("confidence", 0.95)) * 100.0
        ai_conf = round(max(m5_conf, m2_conf), 1)

        s_agreement = 97.5 if final_status == "SAFE" else (94.2 if final_status == "WARNING" else 98.8)

        # ── 5 Equipment Components Digital Twin State Modeling ──
        if final_status == "CRITICAL":
            digital_twin_equipment = {
                "valve": {
                    "name": "1. Raw Water Intake Valve",
                    "before": "OPEN",
                    "before_color": "#10B981",
                    "command": "VALVE_CLOSE_REQUEST(HIRAKUD_ACT_01)",
                    "after": "CLOSED",
                    "after_color": "#EF4444",
                    "status": "🔴 TRIP EXECUTED",
                },
                "pump": {
                    "name": "2. Intake Pumping Station",
                    "before": "ACTIVE (100% Flow)",
                    "before_color": "#10B981",
                    "command": "EMERGENCY_PUMP_TRIP",
                    "after": "STOPPED / STANDBY",
                    "after_color": "#EF4444",
                    "status": "🔴 CAVITATION SAFEGUARD ACTIVE",
                },
                "aeration": {
                    "name": "3. Aeration Injection System",
                    "before": "STANDBY",
                    "before_color": "#94A3B8",
                    "command": "AERATION_STAGE_MAX",
                    "after": "ACTIVATED (Max DO Injection)",
                    "after_color": "#EF4444",
                    "status": "⚡ HIGH PRESSURE OXYGEN STREAM",
                },
                "sampling": {
                    "name": "4. Telemetry Sampling Sonde",
                    "before": "15-Second Interval",
                    "before_color": "#94A3B8",
                    "command": "SHIFT_RATE_1S",
                    "after": "1-Second Critical Burst",
                    "after_color": "#38BDF8",
                    "status": "⏱️ HIGH DENSITY PLUME TELEMETRY",
                },
                "chemical": {
                    "name": "5. Chemical Dosing System",
                    "before": "Normal Base Feed",
                    "before_color": "#10B981",
                    "command": "COAGULANT_ISOLATION",
                    "after": "ISOLATED (Neutralizer Ready)",
                    "after_color": "#F59E0B",
                    "status": "🧪 RAW WATER INTAKE ISOLATED",
                },
            }
            scada_console = {
                "command_generated": "VALVE_CLOSE_REQUEST(HIRAKUD_ACT_01)",
                "status": "✓ ACCEPTED",
                "execution": "SIMULATED (Modbus-TCP / IEC-60870)",
                "response": "ACTUATOR STATE UPDATED (0 errors, 18ms latency)",
                "history": [
                    {"time": (now - timedelta(seconds=2)).strftime("%H:%M:%S"), "event": "Raw water intake valve isolation command generated"},
                    {"time": (now - timedelta(seconds=1)).strftime("%H:%M:%S"), "event": "Digital twin actuator state updated: Valve CLOSED, Pump STOPPED"},
                    {"time": now.strftime("%H:%M:%S"), "event": "Confirmation received from Node HIRAKUD_ACT_01 (Status: 200 OK)"},
                ],
            }
            primary_wf_id = "WF-001"
            primary_action = "SCADA Valve Close & HazMat Webhook"
            wf_latency = "38 ms"
            actions_completed = "7/7 COMPLETED"

        elif final_status in ["WARNING", "HIGH", "MEDIUM"]:
            digital_twin_equipment = {
                "valve": {
                    "name": "1. Raw Water Intake Valve",
                    "before": "OPEN",
                    "before_color": "#10B981",
                    "command": "MAINTAIN_OPEN",
                    "after": "OPEN",
                    "after_color": "#10B981",
                    "status": "🟢 NOMINAL INTAKE ACTIVE",
                },
                "pump": {
                    "name": "2. Intake Pumping Station",
                    "before": "ACTIVE (100% Flow)",
                    "before_color": "#10B981",
                    "command": "THROTTLE_80PCT",
                    "after": "ACTIVE (80% Flow)",
                    "after_color": "#F59E0B",
                    "status": "🟡 SLOW FLOW HEADSPACE",
                },
                "aeration": {
                    "name": "3. Aeration Injection System",
                    "before": "STANDBY",
                    "before_color": "#94A3B8",
                    "command": "AERATION_STAGE_1",
                    "after": "ACTIVATED (Stage 1 Boost)",
                    "after_color": "#F59E0B",
                    "status": "🟡 PREVENTATIVE DO BOOST",
                },
                "sampling": {
                    "name": "4. Telemetry Sampling Sonde",
                    "before": "15-Second Interval",
                    "before_color": "#94A3B8",
                    "command": "SHIFT_RATE_2S",
                    "after": "2-Second Adaptive Rate",
                    "after_color": "#38BDF8",
                    "status": "⏱️ PLUME TRACKING ACCELERATION",
                },
                "chemical": {
                    "name": "5. Chemical Dosing System",
                    "before": "Normal Base Feed",
                    "before_color": "#10B981",
                    "command": "COAGULANT_BOOST_15PCT",
                    "after": "+15% COAGULANT FEED",
                    "after_color": "#F59E0B",
                    "status": "🧪 TURBIDITY FLOCCULATION ACTIVE",
                },
            }
            scada_console = {
                "command_generated": "ACCELERATE_SAMPLING_2S(HIRAKUD_SONDE_01)",
                "status": "✓ ACCEPTED",
                "execution": "SIMULATED (MQTT Telemetry Rate Config)",
                "response": "SONDE SAMPLING SHIFTED 15s -> 2s (Latency: 22ms)",
                "history": [
                    {"time": (now - timedelta(seconds=2)).strftime("%H:%M:%S"), "event": "Adaptive sampling acceleration command generated"},
                    {"time": (now - timedelta(seconds=1)).strftime("%H:%M:%S"), "event": "Coagulant dosing rate adjusted (+15% Alum)"},
                    {"time": now.strftime("%H:%M:%S"), "event": "Watershed telemetry heartbeat synchronized"},
                ],
            }
            primary_wf_id = "WF-002"
            primary_action = "Adaptive Sampling & Coagulant Advisory"
            wf_latency = "22 ms"
            actions_completed = "6/6 COMPLETED"

        else:
            digital_twin_equipment = {
                "valve": {
                    "name": "1. Raw Water Intake Valve",
                    "before": "OPEN",
                    "before_color": "#10B981",
                    "command": "NONE",
                    "after": "OPEN",
                    "after_color": "#10B981",
                    "status": "🟢 NOMINAL INTAKE ACTIVE",
                },
                "pump": {
                    "name": "2. Intake Pumping Station",
                    "before": "ACTIVE (100% Flow)",
                    "before_color": "#10B981",
                    "command": "NONE",
                    "after": "ACTIVE (100% Flow)",
                    "after_color": "#10B981",
                    "status": "🟢 NOMINAL BASEFLOW OPERATION",
                },
                "aeration": {
                    "name": "3. Aeration Injection System",
                    "before": "STANDBY",
                    "before_color": "#94A3B8",
                    "command": "NONE",
                    "after": "STANDBY (Passive)",
                    "after_color": "#94A3B8",
                    "status": "🟢 BASELINE NATURAL DISSOLVED O2",
                },
                "sampling": {
                    "name": "4. Telemetry Sampling Sonde",
                    "before": "15-Second Interval",
                    "before_color": "#94A3B8",
                    "command": "NONE",
                    "after": "15-Second Interval",
                    "after_color": "#10B981",
                    "status": "🟢 CONTINUOUS STANDARD SURVEILLANCE",
                },
                "chemical": {
                    "name": "5. Chemical Dosing System",
                    "before": "Normal Base Feed",
                    "before_color": "#10B981",
                    "command": "NONE",
                    "after": "Normal Dosing (10 mg/L)",
                    "after_color": "#10B981",
                    "status": "🟢 NOMINAL WATER CLARIFICATION",
                },
            }
            scada_console = {
                "command_generated": "SYNC_TIMESCALE_LEDGER(HIRAKUD_HYPERTABLE)",
                "status": "✓ ACCEPTED",
                "execution": "SIMULATED (Database Micro-Batch Commit)",
                "response": "HYPERTABLE BATCH COMMITTED (Latency: 11ms)",
                "history": [
                    {"time": (now - timedelta(seconds=2)).strftime("%H:%M:%S"), "event": "Pristine baseline telemetry validated"},
                    {"time": (now - timedelta(seconds=1)).strftime("%H:%M:%S"), "event": "Telemetry packet committed to TimescaleDB ledger"},
                    {"time": now.strftime("%H:%M:%S"), "event": "SPCB central cloud heartbeat pulse published (QoS 1)"},
                ],
            }
            primary_wf_id = "WF-003"
            primary_action = "Data Archival & Health Heartbeat"
            wf_latency = "11 ms"
            actions_completed = "5/5 COMPLETED"

        # ── 7-Step Real-Time Event Execution Timeline ──
        p = raw_params or {
            "pH": 7.42,
            "dissolved_oxygen_mg_l": 8.65,
            "turbidity_ntu": 4.5,
            "specific_conductance_us_cm": 280.0,
            "temperature_c": 21.3,
        }
        do_val = p.get("dissolved_oxygen_mg_l", 8.65)
        turb_val = p.get("turbidity_ntu", 4.5)
        cond_val = p.get("specific_conductance_us_cm", 280.0)

        t0 = now - timedelta(milliseconds=54)
        t1 = now - timedelta(milliseconds=42)
        t2 = now - timedelta(milliseconds=30)
        t3 = now - timedelta(milliseconds=20)
        t4 = now - timedelta(milliseconds=12)
        t5 = now - timedelta(milliseconds=6)
        t6 = now

        seven_step_timeline = [
            {
                "step_num": "STEP 1",
                "title": "📡 SENSOR TELEMETRY INGESTION",
                "time": t0.strftime("%H:%M:%S.%f")[:-3],
                "status": "✓ COMPLETED",
                "status_color": "#10B981",
                "input": f"DO: {do_val:.2f} mg/L • Turbidity: {turb_val:.1f} NTU • Conductance: {cond_val:.0f} µS/cm",
                "output": "Telemetry packet validated & calibrated in 4ms",
            },
            {
                "step_num": "STEP 2",
                "title": "🧠 AI MODEL ANALYSIS",
                "time": t1.strftime("%H:%M:%S.%f")[:-3],
                "status": "✓ COMPLETED",
                "status_color": "#10B981",
                "input": "M1 (Anomaly), M2 (Risk), M3 (Bio), M4 (Forecast), M5 (Decision)",
                "output": f"Ensemble Evaluated -> Fused Conf: {ai_conf}%, Severity: {final_status}",
            },
            {
                "step_num": "STEP 3",
                "title": "⚖️ SAFETY RULE ENGINE",
                "time": t2.strftime("%H:%M:%S.%f")[:-3],
                "status": "✓ COMPLETED",
                "status_color": "#10B981",
                "input": "CPCB Class A-E Guardrails & Cross-Sensor Agreement",
                "output": "DO below critical threshold (Rule Breach Confirmed)" if stat_upper == "CRITICAL" else ("Hydrological parameter drift detected" if stat_upper in ["WARNING", "HIGH", "MEDIUM"] else "All parameters within pristine baseline limits"),
            },
            {
                "step_num": "STEP 4",
                "title": "⚡ AUTOMATION WORKFLOW TRIGGER",
                "time": t3.strftime("%H:%M:%S.%f")[:-3],
                "status": "✓ EXECUTED",
                "status_color": "#10B981",
                "input": f"Trigger Gate == {final_status} (Mode: {self.control_mode})",
                "output": f"{primary_wf_id} Activated ({primary_action})",
            },
            {
                "step_num": "STEP 5",
                "title": "🏭 DIGITAL TWIN ACTUATION",
                "time": t4.strftime("%H:%M:%S.%f")[:-3],
                "status": "✓ SIMULATION EXECUTED",
                "status_color": "#10B981",
                "input": digital_twin_equipment["valve"]["command"],
                "output": f"Virtual Valve: {digital_twin_equipment['valve']['after']} • Pump: {digital_twin_equipment['pump']['after']}",
            },
            {
                "step_num": "STEP 6",
                "title": "📧 AUTHORITY NOTIFICATION",
                "time": t5.strftime("%H:%M:%S.%f")[:-3],
                "status": "✓ GENERATED",
                "status_color": "#10B981",
                "input": "Multi-Agency Stakeholder Routing Table",
                "output": "Emergency Payloads Created for SPCB, Muni, Plant, HazMat",
            },
            {
                "step_num": "STEP 7",
                "title": "📑 AUDIT RECORD",
                "time": t6.strftime("%H:%M:%S.%f")[:-3],
                "status": "✓ STORED",
                "status_color": "#10B981",
                "input": "Full Incident JSON Payload + Timestamp Vector",
                "output": f"SHA-256 Manifest Signed & Committed ({wf_latency} total latency)",
            },
        ]

        # ── Terminal Event Log Stream ──
        terminal_logs = [
            f"[{t0.strftime('%H:%M:%S')}] 📡 In-situ telemetry ingested (DO={do_val:.2f} mg/L, Cond={cond_val:.0f} µS/cm)",
            f"[{t1.strftime('%H:%M:%S')}] 🧠 AI ensemble evaluated: M1-M5 Fused Confidence={ai_conf}%, issue={incident_name}",
            f"[{t2.strftime('%H:%M:%S')}] ⚖️ Safety rule engine evaluated: {seven_step_timeline[2]['output']}",
            f"[{t3.strftime('%H:%M:%S')}] ⚡ Emergency workflow {primary_wf_id} activated (Latency: {wf_latency})",
            f"[{t4.strftime('%H:%M:%S')}] 🏭 Digital twin actuation: {digital_twin_equipment['valve']['command']} -> State: {digital_twin_equipment['valve']['after']}",
            f"[{t5.strftime('%H:%M:%S')}] 📡 Authority notification payloads generated & queued for 4 stakeholder agencies",
            f"[{t6.strftime('%H:%M:%S')}] 📑 Incident manifest committed to TimescaleDB audit ledger (Tamper-proof signature verified)",
        ]

        # Stakeholder Notification Routing
        notification_data = self.notification_router.route_notification(
            final_status, ai_result, self.control_mode, raw_params
        )

        workflows = {
            "critical_emergency_response": {
                "id": "WF-001",
                "name": "Critical Emergency Workflow (WF-001)",
                "trigger_condition": "Final Status == CRITICAL",
                "is_active": final_status == "CRITICAL",
                "primary_action": "SCADA Valve Close & HazMat Webhook",
                "latency": "38ms",
                "nodes": [
                    {
                        "name": "Trigger: Critical Gate",
                        "type": "trigger",
                        "status": "executed" if final_status == "CRITICAL" else "idle",
                        "details": f"Condition Met: Final Status == {final_status}",
                        "icon": "⚡",
                    },
                    {
                        "name": "SCADA Actuator Simulation",
                        "type": "scada_actuator",
                        "status": "executed" if final_status == "CRITICAL" else "idle",
                        "details": "Simulated command: RAW_WATER_VALVE_CLOSE(HIRAKUD_001)",
                        "icon": "🛑",
                    },
                    {
                        "name": "Alert Webhook Simulation",
                        "type": "webhook",
                        "status": "executed" if final_status == "CRITICAL" else "idle",
                        "details": "Webhook payload simulation: POST /v1/hazmat/alerts (200 OK)",
                        "icon": "🌐",
                    },
                    {
                        "name": "Notification Broadcast",
                        "type": "broadcast",
                        "status": "executed" if final_status == "CRITICAL" else "idle",
                        "details": "Simulated dispatch: 14 On-Duty Operators & Regional Collector",
                        "icon": "📲",
                    },
                    {
                        "name": "Audit Log Generation",
                        "type": "audit_ledger",
                        "status": "executed" if final_status == "CRITICAL" else "idle",
                        "details": "SHA-256 Tamper-Proof Incident Record Appended to Ledger",
                        "icon": "📑",
                    },
                ],
                "execution_summary": "5 Emergency Response Nodes Executed in 38ms." if final_status == "CRITICAL" else "Standing By — Awaiting Critical Trigger.",
            },
            "warning_early_intervention": {
                "id": "WF-002",
                "name": "Warning Intervention Workflow (WF-002)",
                "trigger_condition": "Final Status == WARNING",
                "is_active": final_status in ["WARNING", "HIGH", "MEDIUM"] and final_status != "CRITICAL",
                "primary_action": "Adaptive Sampling & Coagulant Advisory",
                "latency": "22ms",
                "nodes": [
                    {
                        "name": "Trigger: Warning Gate",
                        "type": "trigger",
                        "status": "executed" if (final_status in ["WARNING", "HIGH", "MEDIUM"] and final_status != "CRITICAL") else "idle",
                        "details": f"Condition Met: Final Status == {final_status}",
                        "icon": "⚡",
                    },
                    {
                        "name": "Increased Monitoring Frequency",
                        "type": "iot_config",
                        "status": "executed" if (final_status in ["WARNING", "HIGH", "MEDIUM"] and final_status != "CRITICAL") else "idle",
                        "details": "Simulated telemetry rate shifted: 15s -> 2s for plume tracking",
                        "icon": "⏱️",
                    },
                    {
                        "name": "Advisory Generation",
                        "type": "advisory",
                        "status": "executed" if (final_status in ["WARNING", "HIGH", "MEDIUM"] and final_status != "CRITICAL") else "idle",
                        "details": "Simulated SCADA advisory: +15% Alum/Coagulant feed rate",
                        "icon": "🧪",
                    },
                    {
                        "name": "Operator Notification",
                        "type": "email_alert",
                        "status": "executed" if (final_status in ["WARNING", "HIGH", "MEDIUM"] and final_status != "CRITICAL") else "idle",
                        "details": "Simulated advisory notice sent to Watershed Field Engineers",
                        "icon": "📧",
                    },
                ],
                "execution_summary": "4 Warning Intervention Nodes Executed in 22ms." if (final_status in ["WARNING", "HIGH", "MEDIUM"] and final_status != "CRITICAL") else "Standing By — Awaiting Warning Trigger.",
            },
            "nominal_data_archival": {
                "id": "WF-003",
                "name": "Safe Baseline Workflow (WF-003)",
                "trigger_condition": "Final Status == SAFE",
                "is_active": final_status == "SAFE",
                "primary_action": "Data Archival & Health Heartbeat",
                "latency": "11ms",
                "nodes": [
                    {
                        "name": "Trigger: Baseline Stream",
                        "type": "trigger",
                        "status": "executed" if final_status == "SAFE" else "idle",
                        "details": "Condition Met: Pristine Telemetry Baseline Validated",
                        "icon": "⚡",
                    },
                    {
                        "name": "Data Archival",
                        "type": "database",
                        "status": "executed" if final_status == "SAFE" else "idle",
                        "details": "Simulated batch commit to TimescaleDB hypertable (6ms)",
                        "icon": "💾",
                    },
                    {
                        "name": "Health Heartbeat",
                        "type": "cloud_pulse",
                        "status": "executed" if final_status == "SAFE" else "idle",
                        "details": "Simulated MQTT Heartbeat sent to spcb/hirakud/health (QoS 1)",
                        "icon": "💚",
                    },
                    {
                        "name": "Continuous Monitoring",
                        "type": "monitor",
                        "status": "executed" if final_status == "SAFE" else "idle",
                        "details": "Nominal 5-second sampling active on Node HIRAKUD_001",
                        "icon": "🔄",
                    },
                ],
                "execution_summary": "4 Nominal Monitoring Nodes Active & Synced in 11ms." if final_status == "SAFE" else "Standing By — Inactive in current state.",
            },
        }

        active_wf_key = (
            "critical_emergency_response"
            if final_status == "CRITICAL"
            else ("warning_early_intervention" if final_status in ["WARNING", "HIGH", "MEDIUM"] else "nominal_data_archival")
        )
        active_wf = workflows[active_wf_key]

        log_entry = {
            "Time": now_str,
            "Status": final_status,
            "Workflow": active_wf["id"],
            "Action": active_wf["primary_action"],
            "Latency": active_wf["latency"],
        }

        if not self.execution_logs or self.execution_logs[0].get("Status") != final_status:
            self.execution_logs.insert(0, log_entry)
            if len(self.execution_logs) > 15:
                self.execution_logs.pop()

        executed_count = len([n for n in active_wf["nodes"] if n["status"] == "executed"])

        return {
            "active_workflow_id": primary_wf_id,
            "active_workflow_name": active_wf["name"],
            "active_trigger_condition": active_wf["trigger_condition"],
            "active_executed_nodes_count": executed_count,
            "active_total_nodes_count": len(active_wf["nodes"]),
            "active_latency": wf_latency,
            "actions_completed": actions_completed,
            "control_mode": self.control_mode,
            "safety_gate": {
                "ai_confidence": f"{ai_conf:.1f}%",
                "sensor_agreement": f"{s_agreement:.1f}%",
                "regulatory_rules": "PASSED (CPCB / BIS 10500 Compliant)",
                "gate_decision": "AUTHORIZED" if ai_conf >= 85.0 else "PENDING_REVIEW",
            },
            "digital_twin_equipment": digital_twin_equipment,
            "scada_console": scada_console,
            "seven_step_timeline": seven_step_timeline,
            "terminal_logs": terminal_logs,
            "notification_routing": notification_data,
            "workflows": workflows,
            "recent_logs": self.execution_logs,
            "total_executions": len(self.execution_logs),
        }


workflow_engine = AutomationWorkflowEngine()
