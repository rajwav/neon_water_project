"""
NEON Water Intelligence Platform — Futuristic Command Center HUD Components.

Contains:
  - Custom NASA / Cyberpunk CSS & Glassmorphism Design System
  - Real-Time Digital Twin Dynamic SVG & Particle Flow Visualizer
  - 5-Stage AI Model Pipeline Visualizer HUD
  - Plotly Futuristic Circular & Arc Sensor Telemetry Gauges
  - SHAP Feature Attribution Waterfall & Diverging Visualizer
  - 24-Hour Predictive Trajectory Forecast Visualizer
"""

from typing import Any, Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px

# ── Futuristic Command Center CSS Design System ────────────────────
FUTURISTIC_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&family=Orbitron:wght@600;800;900&display=swap');

:root {
    --bg-deep: #070B14;
    --bg-card: rgba(15, 23, 42, 0.75);
    --border-glow: rgba(0, 240, 255, 0.25);
    --neon-cyan: #00F0FF;
    --neon-blue: #38BDF8;
    --neon-green: #10B981;
    --neon-amber: #F59E0B;
    --neon-red: #EF4444;
    --neon-purple: #8B5CF6;
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
}

/* Global Dark Command Center Background */
.stApp {
    background: radial-gradient(circle at 50% 0%, #0d1b2a 0%, #070B14 70%, #030712 100%);
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
}

/* Top Command Header */
.command-header {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.7) 100%);
    border: 1px solid rgba(0, 240, 255, 0.35);
    border-radius: 12px;
    padding: 16px 22px;
    margin-bottom: 18px;
    box-shadow: 0 8px 32px rgba(0, 240, 255, 0.1), inset 0 0 16px rgba(0, 240, 255, 0.05);
    backdrop-filter: blur(16px);
}

.command-title {
    font-family: 'Orbitron', 'Inter', sans-serif;
    font-size: 24px;
    font-weight: 800;
    letter-spacing: 2px;
    background: linear-gradient(90deg, #FFFFFF 0%, #00F0FF 50%, #38BDF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-transform: uppercase;
}

.system-beacon {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 9999px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
}

.beacon-online {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid #10B981;
    color: #34D399;
    box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
}

.beacon-warning {
    background: rgba(245, 158, 11, 0.15);
    border: 1px solid #F59E0B;
    color: #FBBF24;
    box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
}

.beacon-critical {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid #EF4444;
    color: #F87171;
    box-shadow: 0 0 16px rgba(239, 68, 68, 0.6);
    animation: pulse-danger 1.5s infinite;
}

@keyframes pulse-danger {
    0% { box-shadow: 0 0 8px rgba(239, 68, 68, 0.4); }
    50% { box-shadow: 0 0 24px rgba(239, 68, 68, 0.85); }
    100% { box-shadow: 0 0 8px rgba(239, 68, 68, 0.4); }
}

/* Glassmorphism Futuristic Cards */
.hud-card {
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(0, 240, 255, 0.2);
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(12px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 12px;
}

.hud-card:hover {
    border-color: rgba(0, 240, 255, 0.5);
    box-shadow: 0 8px 30px rgba(0, 240, 255, 0.15);
}

/* Pipeline Horizontal Flow */
.pipeline-container {
    display: flex;
    justify-content: space-between;
    align-items: stretch;
    gap: 8px;
    margin: 16px 0;
    overflow-x: auto;
    padding-bottom: 8px;
}

.pipeline-node {
    flex: 1;
    min-width: 135px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 10px;
    padding: 12px 8px;
    text-align: center;
    position: relative;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(8px);
}

.pipeline-node-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 10px;
    font-weight: 700;
    color: var(--neon-cyan);
    letter-spacing: 1px;
    margin-bottom: 4px;
}

.pipeline-node-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    margin: 4px 0;
}

.pipeline-node-meta {
    font-size: 10px;
    color: var(--text-secondary);
}

/* Tiered Action Cards */
.action-card-imm {
    background: linear-gradient(180deg, rgba(239, 68, 68, 0.12) 0%, rgba(15, 23, 42, 0.8) 100%);
    border-left: 4px solid #EF4444;
    border-radius: 8px;
    padding: 14px;
    margin-bottom: 10px;
}

.action-card-short {
    background: linear-gradient(180deg, rgba(245, 158, 11, 0.12) 0%, rgba(15, 23, 42, 0.8) 100%);
    border-left: 4px solid #F59E0B;
    border-radius: 8px;
    padding: 14px;
    margin-bottom: 10px;
}

.action-card-long {
    background: linear-gradient(180deg, rgba(56, 189, 248, 0.12) 0%, rgba(15, 23, 42, 0.8) 100%);
    border-left: 4px solid #38BDF8;
    border-radius: 8px;
    padding: 14px;
    margin-bottom: 10px;
}
</style>
"""


# ── 1. Digital Twin Real-Time Dynamic Visualizer ───────────────────
def render_digital_twin_svg(
    site_id: str = "Hirakud Reservoir",
    ph: Optional[float] = 7.42,
    do: Optional[float] = 8.65,
    turb: Optional[float] = 4.5,
    cond: Optional[float] = 280.0,
    temp: Optional[float] = 21.3,
    final_status: str = "SAFE",
    incident_type: str = "NOMINAL_BASELINE",
) -> str:
    """
    Generate a dynamic, realistic sub-surface physical digital twin of the water column tank.
    Includes:
      - Water surface sinusoidal animation
      - Calibrated depth scale (0m to 5m)
      - Submerged IoT multi-parameter sonde with depth tether (4.2m)
      - Thermal stratification gradient layers (Epilimnion -> Thermocline -> Hypolimnion)
      - Dynamic pH gradient and contaminant plume simulation
      - Turbidity particulate cloud animation
      - Telemetry overlay HUD
    """
    # Safe float extraction
    try:
        ph_v = float(ph) if ph is not None else 7.42
    except (ValueError, TypeError):
        ph_v = 7.42

    try:
        do_v = float(do) if do is not None else 8.65
    except (ValueError, TypeError):
        do_v = 8.65

    try:
        turb_v = float(turb) if turb is not None else 4.5
    except (ValueError, TypeError):
        turb_v = 4.5

    try:
        cond_v = float(cond) if cond is not None else 280.0
    except (ValueError, TypeError):
        cond_v = 280.0

    try:
        temp_v = float(temp) if temp is not None else 21.3
    except (ValueError, TypeError):
        temp_v = 21.3

    status_str = str(final_status).upper()

    # Dynamic color palettes based on environmental chemistry
    if status_str == "CRITICAL":
        if ph_v <= 5.0 or "ACID" in str(incident_type).upper():
            water_top, water_mid, water_bot = "#7F1D1D", "#B91C1C", "#450A0A"
            plume_color = "rgba(239, 68, 68, 0.75)"
            beacon_color = "#EF4444"
            status_desc = "ACUTE ACID CONTAMINATION INFLUX"
            particle_count = 18
        elif do_v <= 2.5 or "HYPOXIA" in str(incident_type).upper():
            water_top, water_mid, water_bot = "#1E293B", "#334155", "#0F172A"
            plume_color = "rgba(100, 116, 139, 0.70)"
            beacon_color = "#EF4444"
            status_desc = "SEVERE ANOXIC STRATIFICATION"
            particle_count = 12
        else:
            water_top, water_mid, water_bot = "#581C87", "#7E22CE", "#3B0764"
            plume_color = "rgba(168, 85, 247, 0.75)"
            beacon_color = "#EF4444"
            status_desc = "TOXIC CONTAMINATION PULSE ACTIVE"
            particle_count = 20
    elif status_str in ["WARNING", "HIGH", "MEDIUM"]:
        water_top, water_mid, water_bot = "#78350F", "#B45309", "#451A03"
        plume_color = "rgba(245, 158, 11, 0.65)"
        beacon_color = "#F59E0B"
        status_desc = "ELEVATED TURBIDITY & SEDIMENT LOADING"
        particle_count = 14
    else:  # SAFE / NOMINAL
        water_top, water_mid, water_bot = "#0369A1", "#0284C7", "#0F766E"
        plume_color = "rgba(56, 189, 248, 0.40)"
        beacon_color = "#10B981"
        status_desc = "NOMINAL BASELINE WATER QUALITY"
        particle_count = 8

    # Particle clouds based on turbidity
    particles_svg = ""
    for i in range(particle_count):
        cx = 160 + (i * 37) % 600
        cy = 130 + (i * 23) % 180
        r = 2 + (i % 3)
        dur = 3.5 + (i % 4)
        delay = (i * 0.3) % 2.5
        particles_svg += f"""
        <circle cx="{cx}" cy="{cy}" r="{r}" fill="{beacon_color}" opacity="0.55">
            <animate attributeName="cy" values="{cy};{cy - 16};{cy}" dur="{dur}s" begin="{delay}s" repeatCount="indefinite" />
            <animate attributeName="cx" values="{cx};{cx + 20};{cx}" dur="{dur * 1.5}s" begin="{delay}s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.2;0.8;0.2" dur="{dur}s" begin="{delay}s" repeatCount="indefinite" />
        </circle>
        """

    html_payload = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{
          margin: 0;
          padding: 0;
          background: transparent;
          font-family: 'JetBrains Mono', -apple-system, sans-serif;
          color: #F8FAFC;
          overflow: hidden;
        }}
        .tank-container {{
          background: rgba(11, 19, 43, 0.95);
          border: 1px solid rgba(56, 189, 248, 0.3);
          border-radius: 12px;
          padding: 12px;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7);
        }}
        @keyframes pulse-led {{
          0% {{ opacity: 0.4; filter: drop-shadow(0 0 2px {beacon_color}); }}
          50% {{ opacity: 1.0; filter: drop-shadow(0 0 10px {beacon_color}); }}
          100% {{ opacity: 0.4; filter: drop-shadow(0 0 2px {beacon_color}); }}
        }}
        .led-active {{
          animation: pulse-led 1.4s infinite;
        }}
      </style>
    </head>
    <body>
      <div class="tank-container">
        <svg viewBox="0 0 840 370" width="100%" height="360" xmlns="http://www.w3.org/2000/svg" style="border-radius: 8px; background: #040814;">
          <defs>
            <linearGradient id="waterTankGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="{water_top}" stop-opacity="0.90" />
              <stop offset="45%" stop-color="{water_mid}" stop-opacity="0.85" />
              <stop offset="100%" stop-color="{water_bot}" stop-opacity="0.98" />
            </linearGradient>

            <linearGradient id="plumeStream" x1="100%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="{plume_color}" stop-opacity="0.8" />
              <stop offset="60%" stop-color="{plume_color}" stop-opacity="0.3" />
              <stop offset="100%" stop-color="{plume_color}" stop-opacity="0.0" />
            </linearGradient>

            <filter id="glowEffect" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          <!-- Sky & Atmospheric Interface -->
          <rect x="0" y="0" width="840" height="75" fill="#0A0F1D" />

          <!-- Water Tank Column Body -->
          <rect x="90" y="75" width="730" height="280" fill="url(#waterTankGrad)" rx="4" />

          <!-- Depth Stratification Bands -->
          <!-- Epilimnion (0 - 1.8m) -->
          <rect x="90" y="75" width="730" height="90" fill="rgba(255,255,255,0.03)" />
          <text x="800" y="95" text-anchor="end" font-size="9" fill="#94A3B8" font-family="'JetBrains Mono'">Epilimnion (Warm Surface: {temp_v:.1f}°C)</text>

          <!-- Thermocline (1.8m - 3.4m) -->
          <rect x="90" y="165" width="730" height="85" fill="rgba(0,0,0,0.06)" />
          <text x="800" y="185" text-anchor="end" font-size="9" fill="#94A3B8" font-family="'JetBrains Mono'">Thermocline Gradient</text>

          <!-- Hypolimnion (3.4m - 5.0m) -->
          <rect x="90" y="250" width="730" height="105" fill="rgba(0,0,0,0.15)" />
          <text x="800" y="270" text-anchor="end" font-size="9" fill="#94A3B8" font-family="'JetBrains Mono'">Hypolimnion (Benthic Bottom: 17.2°C)</text>

          <!-- Dynamic Water Surface Wave -->
          <path d="M90,75 Q270,68 455,75 T820,72 L820,95 L90,95 Z" fill="url(#waterTankGrad)" opacity="0.8">
            <animate attributeName="d" 
              values="M90,75 Q270,68 455,75 T820,72 L820,95 L90,95 Z;
                      M90,72 Q270,82 455,70 T820,76 L820,95 L90,95 Z;
                      M90,75 Q270,68 455,75 T820,72 L820,95 L90,95 Z" 
              dur="4s" repeatCount="indefinite" />
          </path>

          <!-- Surface Shimmer Line -->
          <path d="M90,75 Q270,68 455,75 T820,72" stroke="rgba(255,255,255,0.4)" stroke-width="2" fill="none">
            <animate attributeName="d" 
              values="M90,75 Q270,68 455,75 T820,72;
                      M90,72 Q270,82 455,70 T820,76;
                      M90,75 Q270,68 455,75 T820,72" 
              dur="4s" repeatCount="indefinite" />
          </path>

          <!-- Contaminant Plume Streamer -->
          <path d="M820,220 C680,240 520,290 380,295 C260,300 160,320 90,330 L90,355 L820,355 Z" fill="url(#plumeStream)" opacity="0.75" />

          <!-- Dynamic Turbidity Particles -->
          {particles_svg}

          <!-- Calibrated Depth Scale Rail (Left Margin) -->
          <line x1="75" y1="75" x2="75" y2="355" stroke="#38BDF8" stroke-width="2" />
          <!-- Ticks -->
          <line x1="68" y1="75" x2="75" y2="75" stroke="#38BDF8" stroke-width="2" />
          <text x="62" y="79" text-anchor="end" font-size="10" fill="#38BDF8" font-weight="700">0.0m</text>

          <line x1="68" y1="131" x2="75" y2="131" stroke="#38BDF8" stroke-width="1.5" />
          <text x="62" y="135" text-anchor="end" font-size="9" fill="#94A3B8">1.0m</text>

          <line x1="68" y1="187" x2="75" y2="187" stroke="#38BDF8" stroke-width="1.5" />
          <text x="62" y="191" text-anchor="end" font-size="9" fill="#94A3B8">2.0m</text>

          <line x1="68" y1="243" x2="75" y2="243" stroke="#38BDF8" stroke-width="1.5" />
          <text x="62" y="247" text-anchor="end" font-size="9" fill="#94A3B8">3.0m</text>

          <line x1="68" y1="299" x2="75" y2="299" stroke="#EF4444" stroke-width="2" />
          <text x="62" y="303" text-anchor="end" font-size="10" fill="#EF4444" font-weight="700">4.2m*</text>

          <line x1="68" y1="355" x2="75" y2="355" stroke="#38BDF8" stroke-width="2" />
          <text x="62" y="359" text-anchor="end" font-size="9" fill="#94A3B8">5.0m</text>

          <!-- ── SUBMERGED MULTI-PARAMETER IOT SONDE RIG ── -->
          <!-- Surface Buoy -->
          <g transform="translate(420, 68)">
            <!-- Buoy Body -->
            <ellipse cx="0" cy="0" rx="22" ry="9" fill="#F59E0B" stroke="#F8FAFC" stroke-width="1.5" />
            <rect x="-6" y="-12" width="12" height="12" fill="#D97706" rx="2" />
            <!-- Solar Cap / Antenna -->
            <line x1="0" y1="-12" x2="0" y2="-26" stroke="#38BDF8" stroke-width="2" />
            <circle cx="0" cy="-26" r="3" fill="#38BDF8" class="led-active" />
          </g>

          <!-- Tether Cable (Descends to 4.2m -> y=299) -->
          <line x1="420" y1="75" x2="420" y2="280" stroke="#64748B" stroke-width="2.5" stroke-dasharray="6,3" />

          <!-- Submerged Sonde Housing at 4.2m Depth -->
          <g transform="translate(420, 299)">
            <!-- Titanium Housing Body -->
            <rect x="-14" y="-22" width="28" height="44" rx="6" fill="#1E293B" stroke="#38BDF8" stroke-width="2" filter="url(#glowEffect)" />
            <!-- Sensor Guard Cage -->
            <rect x="-11" y="14" width="22" height="16" rx="2" fill="none" stroke="#64748B" stroke-width="1.5" />
            <!-- Optical DO Window -->
            <circle cx="-5" cy="20" r="3" fill="#38BDF8" />
            <!-- Glass pH Bulb -->
            <circle cx="5" cy="20" r="3" fill="#F59E0B" />
            <!-- Telemetry LED Beacon -->
            <circle cx="0" cy="-8" r="4" fill="{beacon_color}" class="led-active" />
            
            <!-- Sensor Data Tag -->
            <rect x="22" y="-16" width="155" height="32" rx="4" fill="rgba(15,23,42,0.9)" stroke="{beacon_color}" stroke-width="1.5" />
            <text x="30" y="-3" font-size="10" fill="#F8FAFC" font-weight="700">IN-SITU SONDE #001</text>
            <text x="30" y="9" font-size="9" fill="#94A3B8">Depth: 4.2m • {status_desc}</text>
          </g>

          <!-- ── TOP-LEFT TELEMETRY OVERLAY CARD ── -->
          <g transform="translate(105, 14)">
            <rect x="0" y="0" width="715" height="48" rx="8" fill="rgba(15,23,42,0.92)" stroke="rgba(56,189,248,0.4)" stroke-width="1.2" />
            
            <!-- Header Row -->
            <circle cx="16" cy="18" r="5" fill="#10B981" class="led-active" />
            <text x="28" y="22" font-size="12" fill="#38BDF8" font-weight="700">LIVE NODE: {site_id.upper()}</text>
            <text x="280" y="22" font-size="11" fill="#10B981">● Sensor: Connected</text>
            <text x="440" y="22" font-size="11" fill="#94A3B8">Depth: <b style="color:#F8FAFC;">4.2 m</b></text>
            <text x="560" y="22" font-size="11" fill="#94A3B8">Sampling: <b style="color:#F8FAFC;">15 sec</b></text>

            <!-- Metrics Row -->
            <text x="16" y="40" font-size="11" fill="#F8FAFC">
              pH: <b style="color:#38BDF8;">{ph_v:.2f}</b> &nbsp;|&nbsp; 
              DO: <b style="color:#38BDF8;">{do_v:.2f} mg/L</b> &nbsp;|&nbsp; 
              Turbidity: <b style="color:#38BDF8;">{turb_v:.1f} FNU</b> &nbsp;|&nbsp; 
              Cond: <b style="color:#38BDF8;">{cond_v:.0f} µS/cm</b> &nbsp;|&nbsp; 
              Temp: <b style="color:#38BDF8;">{temp_v:.1f} °C</b>
            </text>
          </g>
        </svg>
      </div>
    </body>
    </html>
    """
    return html_payload



# ── 2. AI Model Pipeline 5-Stage Visualizer ────────────────────────
def render_pipeline_html(result: Dict[str, Any]) -> str:
    """
    Render 5-stage AI Model pipeline HUD with glowing connector wires and real-time status.
    """
    m1 = result.get("anomaly_detection", {})
    m2 = result.get("risk_prediction", {})
    m3 = result.get("biological_health", {})
    m4 = result.get("early_warning_forecast", {})
    m5 = result.get("decision_support", {})

    m1_stat = m1.get("status", "Normal")
    m1_score = m1.get("score", -0.15)
    m1_color = "#EF4444" if m1_stat == "Anomaly" else "#10B981"

    m2_class = m2.get("class", "SAFE")
    m2_prob = m2.get("probability", 0.95)
    m2_color = "#EF4444" if m2_class == "CRITICAL" else ("#F59E0B" if m2_class == "WARNING" else "#10B981")

    m3_score = m3.get("score", 92.0)
    m3_tier = m3.get("classification", "Excellent").split("(")[0].strip()
    m3_color = "#10B981" if m3_score >= 70 else ("#F59E0B" if m3_score >= 50 else "#EF4444")

    m4_stat = m4.get("future_projected_status", "SAFE")
    m4_do = m4.get("predicted_dissolved_oxygen_24h", 8.4)
    m4_color = "#EF4444" if m4_stat in ["CRITICAL", "EMERGENCY_OVERRIDE"] else ("#F59E0B" if m4_stat == "WARNING" else "#00F0FF")

    m5_inc = m5.get("incident", "Nominal Baseline")
    m5_sev = m5.get("severity", "LOW")
    m5_color = "#EF4444" if m5_sev in ["CRITICAL", "HIGH"] else ("#F59E0B" if m5_sev == "MEDIUM" else "#10B981")

    html = f"""
    <div class="pipeline-container">
      <!-- Input Stream -->
      <div class="pipeline-node" style="border-color: rgba(0, 240, 255, 0.4);">
        <div class="pipeline-node-title">📡 TELEMETRY</div>
        <div class="pipeline-node-status" style="color: #00F0FF;">STREAM ACTIVE</div>
        <div class="pipeline-node-meta">12 Channels • 15s</div>
      </div>

      <div style="display: flex; align-items: center; color: rgba(0,240,255,0.6); font-size: 16px;">➔</div>

      <!-- Model 1 -->
      <div class="pipeline-node" style="border-color: {m1_color};">
        <div class="pipeline-node-title">MODEL 1: ANOMALY</div>
        <div class="pipeline-node-status" style="color: {m1_color};">{m1_stat.upper()}</div>
        <div class="pipeline-node-meta">Score: {m1_score:+.3f}</div>
      </div>

      <div style="display: flex; align-items: center; color: rgba(0,240,255,0.6); font-size: 16px;">➔</div>

      <!-- Model 2 -->
      <div class="pipeline-node" style="border-color: {m2_color};">
        <div class="pipeline-node-title">MODEL 2: RISK AI</div>
        <div class="pipeline-node-status" style="color: {m2_color};">{m2_class}</div>
        <div class="pipeline-node-meta">Conf: {m2_prob*100:.1f}%</div>
      </div>

      <div style="display: flex; align-items: center; color: rgba(0,240,255,0.6); font-size: 16px;">➔</div>

      <!-- Model 3 -->
      <div class="pipeline-node" style="border-color: {m3_color};">
        <div class="pipeline-node-title">MODEL 3: ECOSYSTEM</div>
        <div class="pipeline-node-status" style="color: {m3_color};">{m3_score:.0f}/100</div>
        <div class="pipeline-node-meta">{m3_tier}</div>
      </div>

      <div style="display: flex; align-items: center; color: rgba(0,240,255,0.6); font-size: 16px;">➔</div>

      <!-- Model 4 -->
      <div class="pipeline-node" style="border-color: {m4_color};">
        <div class="pipeline-node-title">MODEL 4: FORECAST</div>
        <div class="pipeline-node-status" style="color: {m4_color};">{m4_stat[:10]}</div>
        <div class="pipeline-node-meta">DO 24h: {m4_do:.1f} mg/L</div>
      </div>

      <div style="display: flex; align-items: center; color: rgba(0,240,255,0.6); font-size: 16px;">➔</div>

      <!-- Model 5 -->
      <div class="pipeline-node" style="border-color: {m5_color};">
        <div class="pipeline-node-title">MODEL 5: DECISION</div>
        <div class="pipeline-node-status" style="color: {m5_color};">{m5_sev}</div>
        <div class="pipeline-node-meta">{m5_inc[:12]}..</div>
      </div>
    </div>
    """
    return html


# ── 3. Futuristic Plotly Dark Sensor Gauges ────────────────────────
def create_gauge_figure(
    value: float,
    title: str,
    min_val: float,
    max_val: float,
    safe_min: float,
    safe_max: float,
    unit: str,
    color_scheme: str = "cyan",
) -> go.Figure:
    """Create a high-tech dark telemetry gauge meter using Plotly."""
    val = float(value) if value is not None else safe_min

    # Color logic
    if val < safe_min or val > safe_max:
        bar_color = "#EF4444" if (val < safe_min * 0.7 or val > safe_max * 1.3) else "#F59E0B"
    else:
        bar_color = "#00F0FF" if color_scheme == "cyan" else "#10B981"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=val,
            number={"suffix": f" {unit}", "font": {"family": "JetBrains Mono", "size": 17, "color": "#F8FAFC"}},
            title={"text": title, "font": {"family": "Orbitron", "size": 11, "color": "#94A3B8"}},
            gauge={
                "axis": {"range": [min_val, max_val], "tickwidth": 1, "tickcolor": "#334155"},
                "bar": {"color": bar_color, "thickness": 0.3},
                "bgcolor": "#0F172A",
                "borderwidth": 1,
                "bordercolor": "rgba(0, 240, 255, 0.2)",
                "steps": [
                    {"range": [min_val, safe_min], "color": "rgba(239, 68, 68, 0.15)"},
                    {"range": [safe_min, safe_max], "color": "rgba(16, 185, 129, 0.15)"},
                    {"range": [safe_max, max_val], "color": "rgba(239, 68, 68, 0.15)"},
                ],
                "threshold": {
                    "line": {"color": "#FFFFFF", "width": 2},
                    "thickness": 0.75,
                    "value": val,
                },
            },
        )
    )

    fig.update_layout(
        height=135,
        margin=dict(l=10, r=10, t=25, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#F8FAFC"},
    )
    return fig


# ── 4. SHAP Feature Attribution Waterfall / Bar Chart ───────────────
def create_shap_waterfall_chart(contribs: Any, status: Optional[str] = None) -> go.Figure:
    """
    Build Plotly diverging horizontal bar chart for SHAP feature contributions.
    Accepts either a dict containing 'feature_contributions' or a list of contribution dicts directly.
    """
    if isinstance(contribs, dict):
        feature_contribs = contribs.get("feature_contributions", [])
    elif isinstance(contribs, list):
        feature_contribs = contribs
    else:
        feature_contribs = []

    if not feature_contribs:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(text="No SHAP contribution generated", showarrow=False, font=dict(color="#94A3B8", size=13))],
            height=280,
        )
        return fig


    top_fc = sorted(feature_contribs, key=lambda x: abs(float(x.get("shap_value", x.get("impact", 0.0)))), reverse=True)[:8]
    top_fc.reverse()

    labels = []
    hover_texts = []
    impacts = []
    colors = []

    for fc in top_fc:
        fname = fc.get("label") or fc.get("feature", "Feature")
        fval = str(fc.get("value", ""))
        imp = float(fc.get("shap_value", fc.get("impact", 0.0)))
        direction_raw = str(fc.get("direction", "")).lower()

        if "increase" in direction_raw or imp > 0.005:
            direction_str = "Risk Increasing"
            color = "#EF4444"
        elif "decrease" in direction_raw or "protect" in direction_raw or imp < -0.005:
            direction_str = "Protective / Risk Decreasing"
            color = "#10B981"
        else:
            direction_str = "Neutral"
            color = "#64748B"

        label_display = f"{fname} ({fval})" if fval and fval != "None" else fname
        labels.append(label_display)
        impacts.append(imp)
        colors.append(color)
        hover_texts.append(
            f"<b>{fname}</b><br>Observed Value: <b>{fval}</b><br>SHAP Contribution: <b>{imp:+.4f}</b><br>Direction: <b>{direction_str}</b>"
        )

    fig = go.Figure(
        go.Bar(
            x=impacts,
            y=labels,
            orientation="h",
            marker=dict(color=colors, line=dict(color="rgba(255,255,255,0.2)", width=1)),
            text=[f"{imp:+.4f}" for imp in impacts],
            textposition="auto",
            textfont=dict(family="JetBrains Mono", size=11, color="#FFFFFF"),
            hovertext=hover_texts,
            hoverinfo="text",
        )
    )

    title_text = f"TreeSHAP Local Feature Attribution {f'[{status}]' if status else ''}"
    fig.update_layout(
        title={"text": title_text, "font": {"family": "Orbitron", "size": 13, "color": "#00F0FF"}},
        xaxis=dict(title="SHAP Value (Probability Shift / Risk Contribution)", zeroline=True, zerolinecolor="#38BDF8", zerolinewidth=2, gridcolor="#1E293B"),
        yaxis=dict(gridcolor="#1E293B"),
        height=320,
        margin=dict(l=10, r=10, t=40, b=30),
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        font={"color": "#F8FAFC", "family": "Inter"},
    )
    return fig



# ── 5. Predictive 24-Hour Trajectory Forecast Chart ────────────────
def create_forecast_timeline_chart(
    current_do: float,
    pred_do: float,
    current_turb: float = 5.0,
    pred_turb: float = 10.0,
    future_prob: float = 0.05,
    is_suspended: bool = False,
) -> go.Figure:
    """
    Build Plotly multi-timeline projection chart (Current, +6h, +12h, +24h).
    """
    time_labels = ["Current (t=0)", "Projected +6h", "Projected +12h", "Projected +24h"]

    if is_suspended:
        do_trajectory = [current_do, current_do, current_do, current_do]
        turb_trajectory = [current_turb, current_turb, current_turb, current_turb]
    else:
        do_trajectory = [
            current_do,
            current_do + (pred_do - current_do) * 0.25,
            current_do + (pred_do - current_do) * 0.55,
            pred_do,
        ]
        turb_trajectory = [
            current_turb,
            current_turb + (pred_turb - current_turb) * 0.30,
            current_turb + (pred_turb - current_turb) * 0.65,
            pred_turb,
        ]

    fig = go.Figure()

    # DO Series
    fig.add_trace(
        go.Scatter(
            x=time_labels,
            y=do_trajectory,
            mode="lines+markers+text",
            name="Dissolved Oxygen (mg/L)",
            line=dict(color="#00F0FF", width=3, dash="solid" if not is_suspended else "dash"),
            marker=dict(size=8, color="#00F0FF", symbol="diamond"),
            text=[f"{v:.2f}" for v in do_trajectory],
            textposition="top center",
            textfont=dict(family="JetBrains Mono", size=10, color="#00F0FF"),
        )
    )

    # Hypoxia Safety Baseline Reference (4.0 mg/L)
    fig.add_hline(
        y=4.0,
        line_dash="dot",
        line_color="#EF4444",
        annotation_text="Hypoxia Danger Floor (4.0 mg/L)",
        annotation_position="bottom right",
        annotation_font_color="#EF4444",
        annotation_font_size=10,
    )

    fig.update_layout(
        title={"text": "24-Hour Dissolved Oxygen Trajectory Forecast (Model 4.1)", "font": {"family": "Orbitron", "size": 13, "color": "#00F0FF"}},
        xaxis=dict(gridcolor="#1E293B"),
        yaxis=dict(title="DO (mg/L)", gridcolor="#1E293B", range=[0, max(14, max(do_trajectory) + 2)]),
        height=280,
        margin=dict(l=10, r=10, t=40, b=20),
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        font={"color": "#F8FAFC", "family": "Inter"},
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig

