import sys, os
from pathlib import Path
# Add project root to PYTHONPATH for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bids_lite.engine.checklist import load_minimal_spec

def test_load_minimal_spec():
    spec = load_minimal_spec()
    assert "participant_id" in spec.required_columns
    assert "session_id" in spec.required_columns
    assert set(spec.allowed_sex) == {"M", "F", "Male", "Female", "f", "m", "male", "female", "NA", "na", "N/A", ""}