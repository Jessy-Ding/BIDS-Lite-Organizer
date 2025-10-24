# bids_lite/engine/normalizer.py
import pandas as pd

def _norm_token(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.replace(" ", "").replace("/", "-")
    # If the token is purely numeric, pad it with leading zeros to ensure it has at least three digits
    if s.isdigit():
        s = s.zfill(3)
    return s

def normalize_ids(meta: pd.DataFrame) -> pd.DataFrame:
    meta = meta.copy()
    meta["participant_id"] = meta["participant_id"].astype(str).map(_norm_token)
    meta["session_id"]     = meta["session_id"].astype(str).map(_norm_token)
    return meta
