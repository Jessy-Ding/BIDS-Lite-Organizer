import sys, os
from pathlib import Path
# Add project root to PYTHONPATH for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bids_lite.engine.checklist import load_minimal_spec

def test_load_minimal_spec():
    """Test that the minimal spec is loaded correctly"""
    spec = load_minimal_spec()
    # Only participant_id is required now (session_id, age, sex are optional)
    assert "participant_id" in spec.required_columns
    assert "session_id" not in spec.required_columns  # session_id is optional
    assert len(spec.required_columns) == 1  # Only participant_id is required
    assert set(spec.allowed_sex) == {"M", "F", "Male", "Female", "f", "m", "male", "female", "NA", "na", "N/A", ""}