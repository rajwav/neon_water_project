"""
Test Automation Workflow Engine (n8n-Style Orchestrator).
"""
import pytest
from src.automation.workflow_engine import AutomationWorkflowEngine


def test_automation_workflow_trigger_critical():
    engine = AutomationWorkflowEngine()
    ai_result = {
        "final_status": "CRITICAL",
        "decision_support": {"incident": "Acid Spill Emergency", "severity": "CRITICAL"},
    }
    res = engine.evaluate_and_trigger(ai_result)
    assert res["active_workflow_id"] == "WF-001"
    assert "Critical" in res["active_workflow_name"] or "CRITICAL" in res["active_workflow_name"]
    wf = res["workflows"]["critical_emergency_response"]
    assert wf["is_active"] is True
    executed_nodes = [n for n in wf["nodes"] if n["status"] == "executed"]
    assert len(executed_nodes) >= 3


def test_automation_workflow_trigger_warning():
    engine = AutomationWorkflowEngine()
    ai_result = {
        "final_status": "WARNING",
        "decision_support": {"incident": "Hypoxia Warning", "severity": "HIGH"},
    }
    res = engine.evaluate_and_trigger(ai_result)
    assert res["active_workflow_id"] == "WF-002"
    assert "Warning" in res["active_workflow_name"] or "WARNING" in res["active_workflow_name"]
    wf = res["workflows"]["warning_early_intervention"]
    assert wf["is_active"] is True


def test_automation_workflow_trigger_safe():
    engine = AutomationWorkflowEngine()
    ai_result = {
        "final_status": "SAFE",
        "decision_support": {"incident": "Pristine River Baseline", "severity": "LOW"},
    }
    res = engine.evaluate_and_trigger(ai_result)
    assert res["active_workflow_id"] == "WF-003"
    assert "Safe" in res["active_workflow_name"] or "SAFE" in res["active_workflow_name"] or "Nominal" in res["active_workflow_name"]
    wf = res["workflows"]["nominal_data_archival"]
    assert wf["is_active"] is True


def test_authority_notification_routing_layers():
    engine = AutomationWorkflowEngine()

    # 1. Critical Scenario
    res_crit = engine.evaluate_and_trigger({"final_status": "CRITICAL", "decision_support": {"incident": "Industrial Acid Spill"}})
    notif_crit = res_crit["notification_routing"]
    assert notif_crit["workflow_id"] == "WF-NOTIFY-001"
    assert notif_crit["severity"] == "CRITICAL"
    assert any("SPCB" in tg or "Pollution" in tg for tg in notif_crit["target_groups"])
    assert "CRITICAL" in notif_crit["message_preview"]

    # 2. Warning Scenario
    res_warn = engine.evaluate_and_trigger({"final_status": "WARNING", "decision_support": {"incident": "Elevated Runoff"}})
    notif_warn = res_warn["notification_routing"]
    assert notif_warn["workflow_id"] == "WF-NOTIFY-002"
    assert notif_warn["severity"] == "WARNING"
    assert any("Municipal" in tg or "Water" in tg for tg in notif_warn["target_groups"])

    # 3. Safe Scenario
    res_safe = engine.evaluate_and_trigger({"final_status": "SAFE", "decision_support": {"incident": "Pristine Baseline"}})
    notif_safe = res_safe["notification_routing"]
    assert notif_safe["workflow_id"] == "WF-NOTIFY-003"
    assert notif_safe["severity"] == "SAFE"
    assert any("Monitoring" in tg or "SPCB" in tg for tg in notif_safe["target_groups"])
    assert len(notif_safe["history"]) >= 1
