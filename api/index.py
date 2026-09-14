import os
import sys

# Ensure repository root is on sys.path so modules (agents, orchestrator, model) can be imported
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from api.main import app
