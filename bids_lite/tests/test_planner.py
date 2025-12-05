import sys, os
from pathlib import Path
import pandas as pd
# Add project root to PYTHONPATH for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from bids_lite.engine.planner import plan_transforms

def test_plan_transforms_basic(tmp_path: Path):
    """Test that the basic planner works"""
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
    plan = plan_transforms(in_dir, out_dir, meta, dataset_type="raw")
    assert len(plan) == 1
    assert plan[0]["src"].endswith("sub-001_ses-01_T1w.nii.gz")
    # Filename is normalized to lowercase
    assert plan[0]["dst"].endswith("sub-001/ses-01/anat/sub-001_ses-01_t1w.nii.gz")

def test_plan_transforms_raw_no_session_id(tmp_path: Path):
    """Test that raw data gets default session '01' when session_id is missing"""
    in_dir = tmp_path / "incoming"; in_dir.mkdir()
    f = in_dir / "patient_001" / "T1w.nii.gz"
    f.parent.mkdir()
    f.write_text("fake")

    meta = pd.DataFrame({
        "participant_id": ["001"],
    })
    out_dir = tmp_path / "bids"
    plan = plan_transforms(in_dir, out_dir, meta, dataset_type="raw")
    assert len(plan) == 1
    # Raw data should get default session "01"
    assert "ses-01" in plan[0]["dst"]

def test_plan_transforms_derivatives_no_session_id(tmp_path: Path):
    """Test that derivatives without session_id don't create session folders"""
    in_dir = tmp_path / "incoming"; in_dir.mkdir()
    f = in_dir / "Ahmed.nii.gz"
    f.write_text("fake")

    meta = pd.DataFrame({
        "participant_id": ["Ahmed"],
    })
    out_dir = tmp_path / "bids"
    plan = plan_transforms(in_dir, out_dir, meta, dataset_type="derivatives", pipeline_name="test_pipeline")
    assert len(plan) == 1
    # Derivatives without session_id should NOT have ses-XX in path
    assert "ses-" not in plan[0]["dst"]
    # Participant ID is normalized to lowercase
    assert "derivatives/test_pipeline/sub-ahmed" in plan[0]["dst"] or "derivatives/test_pipeline/sub-Ahmed" in plan[0]["dst"]

def test_plan_transforms_derivatives_with_session_id(tmp_path: Path):
    """Test that derivatives with session_id do create session folders"""
    in_dir = tmp_path / "incoming"; in_dir.mkdir()
    f = in_dir / "sub-001_ses-02_lesion.nii.gz"
    f.write_text("fake")

    meta = pd.DataFrame({
        "participant_id": ["001"],
        "session_id": ["02"],
    })
    out_dir = tmp_path / "bids"
    plan = plan_transforms(in_dir, out_dir, meta, dataset_type="derivatives", pipeline_name="test_pipeline")
    assert len(plan) == 1
    # Derivatives with session_id should have ses-XX in path
    assert "ses-02" in plan[0]["dst"]
    assert "derivatives/test_pipeline/sub-001/ses-02" in plan[0]["dst"]