# bids_lite/engine/checklist.py
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class MinimalSpec:
    required_columns: List[str]   # e.g., ["participant_id", "session_id", "age", "sex"]
    allowed_sex: List[str]        # e.g., ["M", "F"]

def load_minimal_spec() -> MinimalSpec:
    """Minimal specifications for subject metadata"""
    return MinimalSpec(
        required_columns=["participant_id", "session_id", "age", "sex"],
        allowed_sex=["M", "F", "Male", "Female", "f", "m", "male", "female", "NA", "na", "N/A", ""]
    )
