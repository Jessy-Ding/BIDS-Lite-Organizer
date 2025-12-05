# bids_lite/engine/validator.py
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

def read_metadata(meta_path: Path) -> pd.DataFrame:
    """
    Read metadata from various file formats.
    Supports: CSV, TSV, Excel (.xlsx, .xls)
    
    Args:
        meta_path: Path to metadata file
        
    Returns:
        pandas DataFrame with metadata
    """
    meta_path = Path(meta_path)
    suffix = meta_path.suffix.lower()
    
    if suffix == ".csv":
        df = pd.read_csv(meta_path)
    elif suffix in [".xlsx", ".xls"]:
        # Read Excel file (first sheet by default)
        try:
            # Try with openpyxl for .xlsx (more reliable)
            if suffix == ".xlsx":
                try:
                    df = pd.read_excel(meta_path, engine='openpyxl')
                except ImportError:
                    # Fallback if openpyxl not installed
                    df = pd.read_excel(meta_path)
            else:
                # .xls files (older format)
                df = pd.read_excel(meta_path, engine='xlrd' if suffix == ".xls" else None)
        except Exception as e:
            raise ValueError(f"Failed to read Excel file {meta_path}: {e}. "
                           f"For .xlsx files, you may need to install openpyxl: pip install openpyxl")
    elif suffix == ".tsv":
        df = pd.read_csv(meta_path, sep="\t")
    else:
        # Try CSV as default
        try:
            df = pd.read_csv(meta_path)
        except Exception:
            # If that fails, try TSV
            df = pd.read_csv(meta_path, sep="\t")
    
    return df


def validate_inputs(in_dir: Path, meta: pd.DataFrame, spec) -> List[Dict[str, Any]]:
    issues = []
    # 1) required columns (only participant_id is strictly required)
    for col in spec.required_columns:
        if col not in meta.columns:
            issues.append({"level": "ERROR", "code": "MISSING_COL", "msg": f"Missing required column: {col}"})
    if issues:
        return issues

    # 2) illegal chars / simple normalization hints (only check columns that exist)
    for col in ["participant_id", "session_id"]:
        if col in meta.columns:
            bad = meta[meta[col].astype(str).str.contains(r"[^A-Za-z0-9_\-]|\s", regex=True, na=False)]
            if not bad.empty:
                issues.append({"level": "ERROR", "code": "ILLEGAL_CHAR", "msg": f"{col} contains spaces or illegal characters."})

    # 3) allowed sex values (only check if sex column exists)
    if "sex" in meta.columns:
        sex_values = meta["sex"].astype(str)
        invalid_sex = sex_values[~sex_values.isin(spec.allowed_sex)]
        if not invalid_sex.empty:
            issues.append({"level": "WARN", "code": "BAD_SEX", "msg": f"Some sex values are not in standard format. Allowed: {spec.allowed_sex}"})

    # 4) basic file existence check
    # Use the same intelligent matching logic as planner
    # Import the matching functions from planner
    from bids_lite.engine.planner import _extract_id_from_path
    from bids_lite.engine.normalizer import _norm_token
    
    # For derivatives or when session_id is missing, only match by participant_id
    has_session = "session_id" in meta.columns
    
    # Get all files in input directory
    all_files = [p for p in in_dir.rglob("*") if p.is_file()]
    
    for _, row in meta.iterrows():
        pid_original = str(row["participant_id"])
        # Normalize participant_id for matching (same as planner does)
        pid_normalized = _norm_token(pid_original)
        
        sid_original = str(row.get("session_id", "")) if has_session else ""
        sid_normalized = _norm_token(sid_original) if sid_original else ""
        
        # Use intelligent matching (same as planner)
        matched = []
        for p in all_files:
            # Check participant_id match using intelligent extraction
            pid_match = _extract_id_from_path(p, pid_normalized)
            if not pid_match:
                continue
            
            # If session_id exists, check for session match (but be flexible)
            if has_session and sid_normalized:
                # Try to match session_id, but don't require it (many files don't have session in name)
                sid_match = _extract_id_from_path(p, sid_normalized, is_session_id=True)
                # If session pattern exists in filename but doesn't match, skip this file
                # Otherwise, allow the match (session might not be in filename)
                if sid_match or not _has_session_pattern(p.name):
                    matched.append(p)
            else:
                # No session_id, just match by participant
                matched.append(p)
        
        if not matched:
            # Show original (non-normalized) ID in warning message for user clarity
            if has_session and sid_original:
                issues.append({"level": "WARN", "code": "FILE_MISSING", "msg": f"No file found matching participant={pid_original}, session={sid_original}"})
            else:
                issues.append({"level": "WARN", "code": "FILE_MISSING", "msg": f"No file found matching participant={pid_original}"})

    return issues


def _has_session_pattern(text: str) -> bool:
    """
    Check if text contains a session pattern (e.g., ses-01, session-01, etc.)
    This helps determine if a file explicitly includes session information.
    """
    import re
    # Look for common session patterns
    patterns = [
        r'ses[-_]?\d+',  # ses-01, ses_01, ses01
        r'session[-_]?\d+',  # session-01, session_01
        r's\d+',  # s01, s1
    ]
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in patterns)

