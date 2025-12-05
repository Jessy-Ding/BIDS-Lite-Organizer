import sys, os
from pathlib import Path
import pandas as pd
import pytest
# Add project root to PYTHONPATH for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from bids_lite.engine.checklist import load_minimal_spec
from bids_lite.engine.planner import plan_transforms
from bids_lite.engine.writer import apply_transforms, write_dataset_description, write_participants_tsv, write_readme, write_report

def test_apply_pipeline_creates_core_files(tmp_path: Path):
    """Test that the apply pipeline creates the core files"""
    in_dir = tmp_path / "incoming"
    in_dir.mkdir()
    # fake NIfTI file
    f = in_dir / "sub-001_ses-01_T1w.nii.gz"
    f.write_text("fake data")

    out_dir = tmp_path / "bids_root"

    meta = pd.DataFrame({
        "participant_id": ["001"],
        "session_id": ["01"],
        "age": [30],
        "sex": ["F"],
    })

    spec = load_minimal_spec()
    plan = plan_transforms(in_dir, out_dir, meta, dataset_type="raw")

    summary = apply_transforms(plan, copy=True)

    write_dataset_description(out_dir, dataset_type="raw")
    write_participants_tsv(out_dir, meta)
    write_readme(out_dir, template=None)
    write_report(out_dir, plan, summary, issues=None)

    assert summary["n_ok"] == 1
    assert (out_dir / "dataset_description.json").exists()
    assert (out_dir / "participants.tsv").exists()
    assert (out_dir / "README.md").exists()
    assert (out_dir / "logs" / "report.md").exists()
    
    # Check that dataset_description.json has correct name
    import json
    dd = json.loads((out_dir / "dataset_description.json").read_text())
    assert dd["GeneratedBy"][0]["Name"] == "BIDS Lite"  # Updated from "BIDS Lite Organizer CLI"

def test_plan_transforms_with_modality(tmp_path: Path):
    """Test that the planner works with multiple modalities"""
    in_dir = tmp_path / "incoming"
    in_dir.mkdir()

    # T1w and T2w files for the same subject/session
    t1 = in_dir / "sub-001_ses-01_T1w.nii.gz"
    t2 = in_dir / "sub-001_ses-01_T2w.nii.gz"
    t1.write_text("t1")
    t2.write_text("t2")

    out_dir = tmp_path / "bids_root"

    meta = pd.DataFrame({
        "participant_id": ["001", "001"],
        "session_id": ["01", "01"],
        "age": [30, 30],
        "sex": ["F", "F"],
        "modality": ["T1w", "T2w"],
    })

    plan = plan_transforms(in_dir, out_dir, meta, dataset_type="raw")
    assert len(plan) == 2
    dsts = [Path(op["dst"]) for op in plan]
    endings = sorted(p.name for p in dsts)
    # Filenames are normalized to lowercase
    assert "sub-001_ses-01_t1w.nii.gz" in endings[0] or "sub-001_ses-01_t1w.nii.gz" in endings[1]
    assert "sub-001_ses-01_t2w.nii.gz" in endings[0] or "sub-001_ses-01_t2w.nii.gz" in endings[1]

def test_derivatives_dataset_description(tmp_path: Path):
    """Test that derivatives dataset_description.json is created correctly"""
    out_dir = tmp_path / "derivatives" / "test_pipeline"
    out_dir.mkdir(parents=True)
    
    write_dataset_description(out_dir, dataset_type="derivatives", pipeline_name="test_pipeline")
    
    import json
    dd = json.loads((out_dir / "dataset_description.json").read_text())
    assert dd["DatasetType"] == "derivatives"
    assert dd["PipelineDescription"]["Name"] == "test_pipeline"
    assert dd["GeneratedBy"][0]["Name"] == "BIDS Lite"
