import sys, os
from pathlib import Path
import pandas as pd
# Add project root to PYTHONPATH for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from bids_lite.engine.normalizer import normalize_ids

def test_normalize_ids_spaces_case():
    """Test that spaces and case are handled correctly"""
    meta = pd.DataFrame({
        "participant_id": ["  Ab 1 "],
        "session_id": ["  S  02 "],
        "age": [28],
        "sex": ["M"]
    })
    out = normalize_ids(meta)
    # Special characters (spaces, etc.) are now replaced with 'u'
    assert out.iloc[0]["participant_id"] == "abu1"  # "Ab 1" -> "abu1" (space -> u)
    assert out.iloc[0]["session_id"] == "suu02"  # "S  02" -> "suu02" (two spaces -> uu)

def test_normalize_ids_special_chars():
    """Test that special characters are replaced with 'u'"""
    meta = pd.DataFrame({
        "participant_id": ["Smith-2023_A", "patient_001", "Ross1981-case2"],
    })
    out = normalize_ids(meta)
    assert out.iloc[0]["participant_id"] == "smithu2023ua"  # - and _ -> u
    assert out.iloc[1]["participant_id"] == "patientu001"  # _ -> u
    assert out.iloc[2]["participant_id"] == "ross1981ucase2"  # - -> u

def test_normalize_ids_numeric_padding():
    """Test that numeric IDs are zero-padded"""
    meta = pd.DataFrame({
        "participant_id": ["1", "01", "001", "12"],
    })
    out = normalize_ids(meta)
    assert out.iloc[0]["participant_id"] == "001"  # "1" -> "001"
    assert out.iloc[1]["participant_id"] == "001"  # "01" -> "001"
    assert out.iloc[2]["participant_id"] == "001"  # "001" -> "001"
    assert out.iloc[3]["participant_id"] == "012"  # "12" -> "012"

def test_normalize_ids_missing_session():
    """Test that missing session_id column is handled gracefully"""
    meta = pd.DataFrame({
        "participant_id": ["001", "002"],
    })
    out = normalize_ids(meta)
    assert "session_id" not in out.columns  # Should not add session_id if missing
    assert len(out) == 2