# bids_lite/engine/normalizer.py
import pandas as pd

def _norm_token(s: str) -> str:
    """
    Normalize participant/session ID for BIDS format.
    User-defined participant IDs should only contain letters and numbers.
    Special characters (spaces, -, _, /, etc.) are replaced with 'u'.
    BIDS format separators (- and _) are only used in BIDS structure (sub-XXX_ses-XX), not in participant_id itself.
    """
    s = (s or "").strip()
    # Convert to lowercase for consistency
    s = s.lower()
    
    # Replace all special characters with 'u'
    # This includes: spaces, hyphens, underscores, slashes, and any other non-alphanumeric characters
    import re
    # Replace any non-alphanumeric character with 'u'
    s = re.sub(r'[^a-z0-9]', 'u', s)
    
    # If the token is purely numeric, pad it with leading zeros to ensure it has at least three digits
    if s.isdigit():
        s = s.zfill(3)
    
    return s

def normalize_ids(meta: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize participant and session IDs.
    Handles missing columns gracefully (e.g., derivatives may not have session_id).
    """
    meta = meta.copy()
    meta["participant_id"] = meta["participant_id"].astype(str).map(_norm_token)
    
    # session_id is optional (derivatives may not have sessions)
    # Only normalize if the column exists - don't add it automatically
    # This allows the planner to decide whether to create session folders
    if "session_id" in meta.columns:
        meta["session_id"] = meta["session_id"].astype(str).map(_norm_token)
    # If session_id column doesn't exist, leave it out
    # The planner will handle this appropriately:
    # - For raw data: use default "01" (BIDS standard requires session for raw)
    # - For derivatives: omit session folders if no session_id
    
    return meta
