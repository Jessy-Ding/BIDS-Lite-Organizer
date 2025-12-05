# bids_lite/engine/checklist.py
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class MinimalSpec:
    required_columns: List[str]   # e.g., ["participant_id", "session_id", "age", "sex"]
    allowed_sex: List[str]        # e.g., ["M", "F"]

def load_minimal_spec() -> MinimalSpec:
    """
    Minimal specifications for subject metadata.
    
    Note: Only participant_id is strictly required. Other columns (session_id, age, sex) 
    are optional and may be missing in real-world datasets, especially for derivatives.
    """
    return MinimalSpec(
        required_columns=["participant_id"],  # Only participant_id is required
        allowed_sex=["M", "F", "Male", "Female", "f", "m", "male", "female", "NA", "na", "N/A", ""]
    )

