import sys
from pathlib import Path

# Make the scripts directory importable so tests can import fetch directly
sys.path.insert(0, str(Path(__file__).resolve().parent))
