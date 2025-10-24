import sys, os
from pathlib import Path
import pandas as pd
# Add project root to PYTHONPATH for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from bids_lite.engine.planner import plan_transforms

def test_plan_transforms_basic(tmp_path: Path):
    in_dir = tmp_path / "incoming"; in_dir.mkdir()
    # create a fake file that matches pid/sid in name
    f = in_dir / "sub-001_ses-01_T1w.nii.gz"
    f.write_text("fake")  # a placeholder

    meta = pd.DataFrame({
        "participant_id": ["001"],
        "session_id": ["01"],
        "age": [30],
        "sex": ["F"]
    })
    out_dir = tmp_path / "bids"
    plan = plan_transforms(in_dir, out_dir, meta)
    assert len(plan) == 1
    assert plan[0]["src"].endswith("sub-001_ses-01_T1w.nii.gz")
    assert plan[0]["dst"].endswith("sub-001/ses-01/anat/sub-001_ses-01_T1w.nii.gz")