# bids_lite/engine/planner.py
from pathlib import Path
from typing import List, Dict
import pandas as pd

def _anat_dst(out_dir: Path, pid: str, sid: str) -> Path:
    return out_dir / f"sub-{pid}" / f"ses-{sid}" / "anat" / f"sub-{pid}_ses-{sid}_T1w.nii.gz"

def plan_transforms(in_dir: Path, out_dir: Path, meta: pd.DataFrame) -> List[Dict]:
    ops: List[Dict] = []
    all_files = [p for p in in_dir.rglob("*") if p.name.endswith((".nii", ".nii.gz"))]
    for _, row in meta.iterrows():
        pid, sid = str(row["participant_id"]), str(row["session_id"])
        # naive: pick the first file that contains pid&sid
        candidates = [p for p in all_files if pid in p.name and sid in p.name]
        if not candidates:
            continue # no file found; should be caught by validator
        src = candidates[0]
        dst = _anat_dst(Path(out_dir), pid, sid)
        ops.append({"src": str(src), "dst": str(dst), "action": "copy"})
    return ops

