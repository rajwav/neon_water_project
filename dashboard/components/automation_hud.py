"""
AquaNeon Industrial SCADA & NASA Mission Control Room HUD Visual Components.
High-impact, CSS-animated HUD, Cause-Effect Pipeline, Emergency GIS Map,
Digital Twin Actuator Transitions, and Animated SCADA Terminal.
"""

from datetime import datetime
from typing import Any, Dict, List


def render_mission_control_hud_html(
    incident_id: str,
    incident_name: str,
    severity: str,
    ai_conf: float,
    active_command: str,
    current_step: str,
    latency: str,
) -> str:
    """
    Render NASA / SCADA Mission Control Header HUD with real-time clocks and status beacons.
    """
    now_str = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    sev_upper = severity.upper()
    sev_color = "#EF4444" if sev_upper == "CRITICAL" else ("#F59E0B" if sev_upper in ["WARNING", "HIGH", "MEDIUM"] else "#10B981")
    glow = "rgba(239, 68, 68, 0.45)" if sev_upper == "CRITICAL" else ("rgba(245, 158, 11, 0.45)" if sev_upper in ["WARNING", "HIGH", "MEDIUM"] else "rgba(16, 185, 129, 0.45)")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <link rel="preconnect" href="https://fonts.googleapis.com">
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700;800&family=Orbitron:wght@700;900&display=swap" rel="stylesheet">
      <style>
        body {{
          margin: 0;
          padding: 8px 4px;
          background: transparent;
          font-family: 'Inter', sans-serif;
          color: #F8FAFC;
        }}
        .hud-banner {{
          background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.90) 100%);
          border: 1.5px solid {sev_color};
          box-shadow: 0 0 20px {glow};
          border-radius: 12px;
          padding: 14px 18px;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }}
        .hud-top {{
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 10px;
          border-bottom: 1px solid rgba(148, 163, 184, 0.2);
          padding-bottom: 10px;
        }}
        .hud-brand {{
          display: flex;
          align-items: center;
          gap: 10px;
        }}
        .hud-title {{
          font-family: 'Orbitron', sans-serif;
          font-size: 14px;
          font-weight: 900;
          letter-spacing: 1.5px;
          color: #F8FAFC;
          text-shadow: 0 0 10px {sev_color};
        }}
        .hud-beacons {{
          display: flex;
          align-items: center;
          gap: 10px;
        }}
        .beacon {{
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 3px 8px;
          border-radius: 16px;
          font-family: 'JetBrains Mono', monospace;
          font-size: 10px;
          font-weight: 700;
        }}
        .beacon-pulse {{
          width: 7px;
          height: 7px;
          border-radius: 50%;
          animation: pulse 1.2s infinite;
        }}
        @keyframes pulse {{
          0%, 100% {{ transform: scale(1); opacity: 1; }}
          50% {{ transform: scale(1.4); opacity: 0.4; }}
        }}
        .hud-grid {{
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
          gap: 10px;
        }}
        .hud-cell {{
          background: rgba(0, 0, 0, 0.35);
          border: 1px solid rgba(148, 163, 184, 0.2);
          border-radius: 8px;
          padding: 8px 10px;
        }}
        .cell-label {{
          font-family: 'JetBrains Mono', monospace;
          font-size: 9px;
          color: #94A3B8;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 3px;
        }}
        .cell-val {{
          font-family: 'Orbitron', sans-serif;
          font-size: 13px;
          font-weight: 800;
          color: #F8FAFC;
        }}
        .cell-val.alert {{
          color: {sev_color};
          text-shadow: 0 0 8px {glow};
        }}
      </style>
    </head>
    <body>
      <div class="hud-banner">
        <div class="hud-top">
          <div class="hud-brand">
            <span style="font-size: 18px;">🚨</span>
            <span class="hud-title">AQUANEON MISSION CONTROL HUD</span>
            <span style="background: {sev_color}25; border: 1px solid {sev_color}; color: {sev_color}; padding: 2px 8px; border-radius: 4px; font-family: 'JetBrains Mono'; font-size: 10px; font-weight: 800;">{sev_upper}</span>
          </div>
          <div class="hud-beacons">
            <span class="beacon" style="background: rgba(56, 189, 248, 0.15); border: 1px solid #38BDF8; color: #38BDF8;">
              <span class="beacon-pulse" style="background: #38BDF8; box-shadow: 0 0 6px #38BDF8;"></span> LIVE AI ENGINE
            </span>
            <span class="beacon" style="background: rgba(239, 68, 68, 0.15); border: 1px solid #EF4444; color: #EF4444;">
              <span class="beacon-pulse" style="background: #EF4444; box-shadow: 0 0 6px #EF4444;"></span> SCADA LINK
            </span>
            <span class="beacon" style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; color: #10B981;">
              <span class="beacon-pulse" style="background: #10B981; box-shadow: 0 0 6px #10B981;"></span> SPCB DISPATCH
            </span>
          </div>
        </div>
        <div class="hud-grid">
          <div class="hud-cell">
            <div class="cell-label">INCIDENT ID</div>
            <div class="cell-val" style="font-size: 11px;">{incident_id}</div>
          </div>
          <div class="hud-cell">
            <div class="cell-label">DETECTED EVENT</div>
            <div class="cell-val" style="font-size: 11px; color: #38BDF8;">{incident_name[:20]}</div>
          </div>
          <div class="hud-cell">
            <div class="cell-label">SIM CLOCK</div>
            <div class="cell-val" style="font-size: 11px; color: #10B981;">{now_str} UTC</div>
          </div>
          <div class="hud-cell">
            <div class="cell-label">AI CONFIDENCE</div>
            <div class="cell-val alert">{ai_conf:.1f}%</div>
          </div>
          <div class="hud-cell">
            <div class="cell-label">CURRENT EXECUTION</div>
            <div class="cell-val" style="font-size: 10px; color: #F59E0B;">{current_step}</div>
          </div>
          <div class="hud-cell">
            <div class="cell-label">SCADA COMMAND</div>
            <div class="cell-val" style="font-size: 10px; color: {sev_color};">{active_command}</div>
          </div>
          <div class="hud-cell">
            <div class="cell-label">TOTAL LATENCY</div>
            <div class="cell-val" style="font-size: 11px;">{latency}</div>
          </div>
        </div>
      </div>
    </body>
    </html>
    """


def render_cause_effect_chain_html(severity: str, incident_name: str) -> str:
    """
    Render the 6-Node Visual Cause-and-Effect Chain:
    CONTAMINATION ➔ AI DETECTION ➔ DECISION ➔ AUTOMATION ➔ ACTUATOR RESPONSE ➔ PUBLIC SAFETY ACTION
    """
    sev_upper = severity.upper()
    sev_color = "#EF4444" if sev_upper == "CRITICAL" else ("#F59E0B" if sev_upper in ["WARNING", "HIGH", "MEDIUM"] else "#10B981")

    steps = [
        {"num": "1", "title": "CONTAMINATION", "icon": "⚠️", "desc": incident_name[:22]},
        {"num": "2", "title": "AI DETECTION", "icon": "🧠", "desc": f"Models M1–M5 Evaluated ({sev_upper})"},
        {"num": "3", "title": "DECISION", "icon": "⚖️", "desc": "CPCB Safety Guardrail Breach" if sev_upper == "CRITICAL" else "Baseline Validated"},
        {"num": "4", "title": "AUTOMATION", "icon": "⚡", "desc": f"WF-001 Protocol Triggered" if sev_upper == "CRITICAL" else "WF-003 Baseline Archival"},
        {"num": "5", "title": "ACTUATOR RESPONSE", "icon": "🏭", "desc": "Intake Valve CLOSED • Pump TRIP" if sev_upper == "CRITICAL" else "Intake OPEN (Nominal Flow)"},
        {"num": "6", "title": "PUBLIC SAFETY", "icon": "🛡️", "desc": "4 Authorities Alerted • Water Guarded"},
    ]

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <link rel="preconnect" href="https://fonts.googleapis.com">
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@600;700;800&family=JetBrains+Mono:wght@700&family=Orbitron:wght@700;900&display=swap" rel="stylesheet">
      <style>
        body {{
          margin: 0;
          padding: 6px;
          background: transparent;
          font-family: 'Inter', sans-serif;
          color: #F8FAFC;
          overflow-x: auto;
        }}
        .chain-container {{
          display: flex;
          align-items: center;
          gap: 8px;
          min-width: 820px;
        }}
        .chain-node {{
          background: rgba(15, 23, 42, 0.90);
          border: 1.5px solid {sev_color};
          box-shadow: 0 0 12px {sev_color}35;
          border-radius: 8px;
          padding: 8px 10px;
          flex: 1;
          min-width: 120px;
        }}
        .node-top {{
          display: flex;
          align-items: center;
          gap: 6px;
          margin-bottom: 4px;
        }}
        .node-num {{
          background: {sev_color};
          color: #0F172A;
          font-family: 'Orbitron', sans-serif;
          font-size: 9px;
          font-weight: 900;
          width: 15px;
          height: 15px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
        }}
        .node-title {{
          font-family: 'Orbitron', sans-serif;
          font-size: 9.5px;
          font-weight: 800;
          color: #F8FAFC;
          letter-spacing: 0.5px;
        }}
        .node-desc {{
          font-family: 'JetBrains Mono', monospace;
          font-size: 8.5px;
          color: #94A3B8;
          line-height: 1.25;
        }}
        .connector {{
          color: {sev_color};
          font-size: 14px;
          font-weight: 900;
          animation: flow 1.5s infinite;
        }}
        @keyframes flow {{
          0%, 100% {{ opacity: 0.6; transform: translateX(0); }}
          50% {{ opacity: 1; transform: translateX(2px); }}
        }}
      </style>
    </head>
    <body>
      <div class="chain-container">
    """

    for i, s in enumerate(steps):
        html += f"""
        <div class="chain-node">
          <div class="node-top">
            <div class="node-num">{s['num']}</div>
            <span>{s['icon']}</span>
            <span class="node-title">{s['title']}</span>
          </div>
          <div class="node-desc">{s['desc']}</div>
        </div>
        """
        if i < len(steps) - 1:
            html += f"""<div class="connector">➔</div>"""

    html += """
      </div>
    </body>
    </html>
    """
    return html


def render_emergency_response_map_html(severity: str, incident_name: str) -> str:
    """
    Render Interactive GIS Emergency Response Map HUD showing Hirakud reservoir,
    plume direction, intake node #001 isolation barrier, and municipal treatment bypass.
    """
    sev_upper = severity.upper()
    sev_color = "#EF4444" if sev_upper == "CRITICAL" else ("#F59E0B" if sev_upper in ["WARNING", "HIGH", "MEDIUM"] else "#10B981")
    valve_state = "🔴 CLOSED (ISOLATED)" if sev_upper == "CRITICAL" else "🟢 OPEN (FLOW ACTIVE)"
    plume_anim = "pulsePlume 1.5s infinite" if sev_upper == "CRITICAL" else "none"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <link rel="preconnect" href="https://fonts.googleapis.com">
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@600;700&family=JetBrains+Mono:wght@600;800&family=Orbitron:wght@700;900&display=swap" rel="stylesheet">
      <style>
        body {{
          margin: 0;
          padding: 4px;
          background: transparent;
          font-family: 'Inter', sans-serif;
          color: #F8FAFC;
        }}
        .map-box {{
          background: rgba(15, 23, 42, 0.92);
          border: 1.5px solid {sev_color};
          box-shadow: 0 0 16px {sev_color}30;
          border-radius: 10px;
          padding: 10px;
          position: relative;
        }}
        .map-header {{
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
          border-bottom: 1px solid rgba(148, 163, 184, 0.2);
          padding-bottom: 6px;
        }}
        .map-title {{
          font-family: 'Orbitron', sans-serif;
          font-size: 11px;
          font-weight: 800;
          letter-spacing: 0.8px;
          color: #38BDF8;
          display: flex;
          align-items: center;
          gap: 6px;
        }}
        .map-svg-wrap {{
          width: 100%;
          height: 120px;
        }}
        @keyframes pulsePlume {{
          0%, 100% {{ opacity: 0.4; r: 18px; }}
          50% {{ opacity: 0.85; r: 24px; }}
        }}
      </style>
    </head>
    <body>
      <div class="map-box">
        <div class="map-header">
          <div class="map-title"><span>🗺️</span> HIRAKUD RESERVOIR INDUSTRIAL GIS HUD (NODE #001)</div>
          <span style="font-family: 'JetBrains Mono'; font-size: 10px; color: {sev_color}; font-weight: 800;">{valve_state}</span>
        </div>
        <div class="map-svg-wrap">
          <svg viewBox="0 0 600 110" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
            <!-- River Baseflow -->
            <path d="M 10 55 Q 150 20, 300 55 T 590 55" fill="none" stroke="#1E3A8A" stroke-width="16" stroke-linecap="round" opacity="0.6"/>
            <path d="M 10 55 Q 150 20, 300 55 T 590 55" fill="none" stroke="#38BDF8" stroke-width="4" stroke-linecap="round" stroke-dasharray="6 6"/>

            <!-- Plume / Contamination Source -->
            <circle cx="120" cy="42" r="20" fill="{sev_color}" opacity="0.35" style="animation: {plume_anim};"/>
            <circle cx="120" cy="42" r="8" fill="{sev_color}"/>
            <text x="120" y="22" fill="#F8FAFC" font-family="Orbitron" font-size="8.5" font-weight="bold" text-anchor="middle">⚠️ CONTAMINATION SOURCE</text>
            <text x="120" y="75" fill="#94A3B8" font-family="JetBrains Mono" font-size="7.5" text-anchor="middle">{incident_name[:18]}</text>

            <!-- Flow Vector Arrow -->
            <path d="M 200 48 L 260 52" stroke="{sev_color}" stroke-width="2.5" marker-end="url(#arrow)"/>
            <text x="230" y="42" fill="{sev_color}" font-family="JetBrains Mono" font-size="8" font-weight="bold" text-anchor="middle">PLUME FLOW ➔</text>

            <!-- Digital Twin Node 001 Intake -->
            <rect x="350" y="32" width="100" height="44" rx="6" fill="#0F172A" stroke="{sev_color}" stroke-width="2"/>
            <text x="400" y="48" fill="#F8FAFC" font-family="Orbitron" font-size="8" font-weight="bold" text-anchor="middle">RAW INTAKE #001</text>
            <text x="400" y="64" fill="{sev_color}" font-family="JetBrains Mono" font-size="8" font-weight="bold" text-anchor="middle">VALVE: {('CLOSED' if sev_upper == 'CRITICAL' else 'OPEN')}</text>

            <!-- Municipal Bypass Barrier -->
            <line x1="460" y1="30" x2="460" y2="80" stroke="{sev_color}" stroke-width="3" stroke-dasharray="4 2"/>
            <rect x="475" y="36" width="110" height="36" rx="6" fill="#1E293B" stroke="#10B981" stroke-width="1.5"/>
            <text x="530" y="50" fill="#10B981" font-family="Orbitron" font-size="7.5" font-weight="bold" text-anchor="middle">🏛️ MUNICIPAL RESERVE</text>
            <text x="530" y="64" fill="#38BDF8" font-family="JetBrains Mono" font-size="7.5" text-anchor="middle">BYPASS ACTIVE (100%)</text>
          </svg>
        </div>
      </div>
    </body>
    </html>
    """


def render_n8n_execution_flow_html(notif_data: Dict[str, Any]) -> str:
    """
    Render n8n-style visual node flow with animated connector lines and execution states:
    COMPLETED (🟢), PROCESSING (🟡), WAITING (⚪).
    """
    flow_nodes = notif_data.get("flow_nodes", [])
    sev = notif_data.get("severity", "SAFE").upper()
    sev_color = "#EF4444" if sev == "CRITICAL" else ("#F59E0B" if sev in ["WARNING", "HIGH", "MEDIUM"] else "#10B981")
    glow = "rgba(239, 68, 68, 0.45)" if sev == "CRITICAL" else ("rgba(245, 158, 11, 0.45)" if sev in ["WARNING", "HIGH", "MEDIUM"] else "rgba(16, 185, 129, 0.45)")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <link rel="preconnect" href="https://fonts.googleapis.com">
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;700&family=Orbitron:wght@700;900&display=swap" rel="stylesheet">
      <style>
        body {{
          margin: 0;
          padding: 8px 4px;
          background: transparent;
          font-family: 'Inter', sans-serif;
          color: #F8FAFC;
          overflow-x: auto;
          overflow-y: hidden;
        }}
        .flow-container {{
          display: flex;
          align-items: center;
          gap: 12px;
          min-width: 860px;
        }}
        .flow-card {{
          background: rgba(15, 23, 42, 0.90);
          border: 1.5px solid {sev_color};
          box-shadow: 0 0 14px {glow};
          border-radius: 10px;
          padding: 10px 12px;
          flex: 1;
          min-width: 130px;
          max-width: 175px;
          position: relative;
        }}
        .flow-card.standby {{
          border: 1px solid rgba(148, 163, 184, 0.25);
          box-shadow: none;
          background: rgba(15, 23, 42, 0.45);
          opacity: 0.70;
        }}
        .flow-header {{
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 4px;
        }}
        .flow-title {{
          font-size: 11px;
          font-weight: 700;
          color: #F8FAFC;
          display: flex;
          align-items: center;
          gap: 5px;
        }}
        .status-badge {{
          font-family: 'JetBrains Mono', monospace;
          font-size: 8.5px;
          font-weight: 700;
          padding: 2px 6px;
          border-radius: 4px;
          background: rgba(16, 185, 129, 0.2);
          color: #10B981;
          border: 1px solid #10B981;
        }}
        .status-badge.standby {{
          background: rgba(148, 163, 184, 0.15);
          color: #94A3B8;
          border: 1px solid #64748B;
        }}
        .flow-details {{
          font-family: 'JetBrains Mono', monospace;
          font-size: 9.5px;
          color: #94A3B8;
          line-height: 1.25;
        }}
        .connector {{
          display: flex;
          align-items: center;
          justify-content: center;
          color: {sev_color};
          font-size: 14px;
          font-weight: 900;
          animation: pulseArrow 1.5s infinite;
        }}
        @keyframes pulseArrow {{
          0%, 100% {{ transform: translateX(0); opacity: 0.7; }}
          50% {{ transform: translateX(3px); opacity: 1; }}
        }}
      </style>
    </head>
    <body>
      <div class="flow-container">
    """

    for i, node in enumerate(flow_nodes):
        state = node.get("state", "COMPLETED").upper()
        is_completed = state == "COMPLETED"
        card_class = "flow-card" if is_completed else "flow-card standby"
        badge_class = "status-badge" if is_completed else "status-badge standby"
        icon = node.get("icon", "📦")
        n_name = node.get("name", "Node")
        n_details = node.get("details", "")

        html += f"""
        <div class="{card_class}">
          <div class="flow-header">
            <div class="flow-title"><span>{icon}</span> <span>{n_name}</span></div>
            <span class="{badge_class}">{state}</span>
          </div>
          <div class="flow-details">{n_details}</div>
        </div>
        """

        if i < len(flow_nodes) - 1:
            html += f"""<div class="connector">➔</div>"""

    html += """
      </div>
    </body>
    </html>
    """
    return html


def render_single_workflow_canvas_html(wf: Dict[str, Any]) -> str:
    return render_n8n_execution_flow_html({"flow_nodes": wf.get("nodes", []), "severity": wf.get("name", "")})


render_notification_flow_canvas_html = render_n8n_execution_flow_html

