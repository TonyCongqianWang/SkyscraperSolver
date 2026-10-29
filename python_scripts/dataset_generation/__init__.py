"""Reproducible, resumable SPSA dataset generation and installation."""
from pathlib import Path
import sys

SCRIPTS = str(Path(__file__).resolve().parent.parent)
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
