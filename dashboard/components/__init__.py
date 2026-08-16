"""
Dashboard components package.
"""

from .alerts import water_alert
from .futuristic_hud import (
    FUTURISTIC_CSS,
    render_digital_twin_svg,
    render_pipeline_html,
    create_gauge_figure,
    create_shap_waterfall_chart,
    create_forecast_timeline_chart,
)
from .geospatial_map import (
    build_national_deployment_deck,
    build_hirakud_basin_deck,
    COLOR_ACTIVE_OPERATIONAL,
    COLOR_PROPOSED_EXPANSION,
)

__all__ = [
    "water_alert",
    "FUTURISTIC_CSS",
    "render_digital_twin_svg",
    "render_pipeline_html",
    "create_gauge_figure",
    "create_shap_waterfall_chart",
    "create_forecast_timeline_chart",
    "build_national_deployment_deck",
    "build_hirakud_basin_deck",
    "COLOR_ACTIVE_OPERATIONAL",
    "COLOR_PROPOSED_EXPANSION",
]
