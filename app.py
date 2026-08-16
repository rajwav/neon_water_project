"""
AQUA NEON — National Environmental Water Intelligence Platform.
Main Entrypoint Launcher: Executes the canonical Command Center in dashboard/app.py.
"""

from pathlib import Path
import runpy
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Execute canonical dashboard/app.py
dashboard_app_path = PROJECT_ROOT / "dashboard" / "app.py"
runpy.run_path(str(dashboard_app_path), run_name="__main__")