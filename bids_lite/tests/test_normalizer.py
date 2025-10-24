import sys, os
from pathlib import Path
import pandas as pd
# Add project root to PYTHONPATH for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from bids_lite.engine.normalizer import normalize_ids

def test_normalize_ids_spaces_case():
    meta = pd.DataFrame({
        "participant_id": ["  Ab 1 "],
        "session_id": ["  S  02 "],
        "age": [28],
        "sex": ["M"]
    })
    out = normalize_ids(meta)
    assert out.iloc[0]["participant_id"] == "ab1"
    assert out.iloc[0]["session_id"] == "s02"