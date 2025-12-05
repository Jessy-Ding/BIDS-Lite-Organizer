import sys, os
import pandas as pd
from pathlib import Path
# Add project root to PYTHONPATH for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from bids_lite.engine.checklist import load_minimal_spec
from bids_lite.engine.validator import validate_inputs

def test_missing_column(tmp_path: Path):
    """Test that missing column is detected"""
    in_dir = tmp_path / "incoming"; in_dir.mkdir()
    # metadata without 'participant_id' (required)
    meta = pd.DataFrame({"session_id": ["01"], "age": [30]})
    spec = load_minimal_spec()
    issues = validate_inputs(in_dir, meta, spec)
    assert any(it["code"] == "MISSING_COL" for it in issues)
    # metadata without 'sex' should NOT fail (sex is optional)
    meta2 = pd.DataFrame({"participant_id": ["001"], "session_id": ["01"], "age": [30]})
    issues2 = validate_inputs(in_dir, meta2, spec)
    assert not any(it["code"] == "MISSING_COL" for it in issues2)

def test_missing_session_id_ok(tmp_path: Path):
    """Test that missing session_id is OK (it's optional)"""
    in_dir = tmp_path / "incoming"; in_dir.mkdir()
    meta = pd.DataFrame({"participant_id": ["001"]})  # No session_id
    spec = load_minimal_spec()
    issues = validate_inputs(in_dir, meta, spec)
    # Should not have MISSING_COL error for session_id
    missing_col_issues = [it for it in issues if it["code"] == "MISSING_COL"]
    assert len(missing_col_issues) == 0

def test_file_missing(tmp_path: Path):
    """Test that file missing is detected"""
    in_dir = tmp_path / "incoming"; in_dir.mkdir()
    meta = pd.DataFrame({"participant_id": ["001"], "session_id": ["01"], "age": [30], "sex": ["F"]})
    spec = load_minimal_spec()
    issues = validate_inputs(in_dir, meta, spec)
    assert any(it["code"] == "FILE_MISSING" for it in issues)