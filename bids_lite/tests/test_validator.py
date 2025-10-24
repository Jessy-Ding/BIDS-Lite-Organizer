import sys, os
import pandas as pd
from pathlib import Path
# Add project root to PYTHONPATH for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from bids_lite.engine.checklist import load_minimal_spec
from bids_lite.engine.validator import validate_inputs

def test_missing_column(tmp_path: Path):
    in_dir = tmp_path / "incoming"; in_dir.mkdir()
    # metadata without 'sex'
    meta = pd.DataFrame({"participant_id": ["001"], "session_id": ["01"], "age": [30]})
    spec = load_minimal_spec()
    issues = validate_inputs(in_dir, meta, spec)
    assert any(it["code"] == "MISSING_COL" for it in issues)

def test_file_missing(tmp_path: Path):
    in_dir = tmp_path / "incoming"; in_dir.mkdir()
    meta = pd.DataFrame({"participant_id": ["001"], "session_id": ["01"], "age": [30], "sex": ["F"]})
    spec = load_minimal_spec()
    issues = validate_inputs(in_dir, meta, spec)
    assert any(it["code"] == "FILE_MISSING" for it in issues)