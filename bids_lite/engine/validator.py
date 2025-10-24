# bids_lite/engine/validator.py
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

def read_metadata(meta_path: Path) -> pd.DataFrame:
    if meta_path.suffix.lower() == ".csv":
        df = pd.read_csv(meta_path)
    else:
        df = pd.read_csv(meta_path, sep="\t") # tsv
    return df


def validate_inputs(in_dir: Path, meta: pd.DataFrame, spec) -> List[Dict[str, Any]]:
    issues = []
    # 1) required columns
    for col in spec.required_columns:
        if col not in meta.columns:
            issues.append({"level": "ERROR", "code": "MISSING_COL", "msg": f"Missing column: {col}"})
    if issues:
        return issues

    # 2) illegal chars / simple normalization hints
    for col in ["participant_id", "session_id"]:
        bad = meta[meta[col].astype(str).str.contains(r"[^A-Za-z0-9_\-]|\s", regex=True, na=False)]
        if not bad.empty:
            issues.append({"level": "ERROR", "code": "ILLEGAL_CHAR", "msg": f"{col} contains spaces or illegal characters."})

    # 3) allowed sex values
    if not meta["sex"].astype(str).isin(spec.allowed_sex).all():
        issues.append({"level": "ERROR", "code": "BAD_SEX", "msg": f"sex must be one of {spec.allowed_sex}"})

    # 4) basic file existence check (T1w only for MVP)
    # Expect at least one file per row that contains the participant_id and session_id in name
    for _, row in meta.iterrows():
        pid = str(row["participant_id"])
        sid = str(row["session_id"])
        found = list(in_dir.rglob("*"))
        matched = [p for p in found if p.is_file() and pid in p.name and sid in p.name]
        if not matched:
            issues.append({"level": "ERROR", "code": "FILE_MISSING", "msg": f"No file found matching participant={pid}, session={sid}"})

    return issues

