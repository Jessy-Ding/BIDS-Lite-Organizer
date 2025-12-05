import sys
from pathlib import Path
import pandas as pd
import pytest
from click.testing import CliRunner

# Add project root to PYTHONPATH for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bids_lite.cli import cli


def test_cli_help():
    """Test that CLI help works"""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "BIDS Lite Organizer" in result.output
    assert "validate" in result.output
    assert "plan" in result.output
    assert "apply" in result.output


def test_validate_command_success(tmp_path: Path):
    """Test validate command with valid data"""
    runner = CliRunner()
    
    # Setup: create input directory and metadata
    in_dir = tmp_path / "input"
    in_dir.mkdir()
    
    # Create a file that matches the participant
    (in_dir / "patient_001" / "T1w.nii.gz").parent.mkdir()
    (in_dir / "patient_001" / "T1w.nii.gz").write_text("fake data")
    
    # Create metadata CSV
    meta_file = tmp_path / "metadata.csv"
    meta = pd.DataFrame({
        "participant_id": ["001"],
        "session_id": ["01"],
        "age": [30],
        "sex": ["F"]
    })
    meta.to_csv(meta_file, index=False)
    
    # Run validate command
    result = runner.invoke(cli, [
        "validate",
        "--in", str(in_dir),
        "--meta", str(meta_file)
    ])
    
    assert result.exit_code == 0
    assert "Validation passed" in result.output


def test_validate_command_failure_missing_column(tmp_path: Path):
    """Test validate command fails when required column is missing"""
    runner = CliRunner()
    
    in_dir = tmp_path / "input"
    in_dir.mkdir()
    
    # Create metadata without participant_id
    meta_file = tmp_path / "metadata.csv"
    meta = pd.DataFrame({
        "session_id": ["01"],
        "age": [30]
    })
    meta.to_csv(meta_file, index=False)
    
    result = runner.invoke(cli, [
        "validate",
        "--in", str(in_dir),
        "--meta", str(meta_file)
    ])
    
    assert result.exit_code == 1
    assert "issue(s)" in result.output or "MISSING_COL" in result.output


def test_validate_command_missing_paths():
    """Test validate command fails with missing input directory"""
    runner = CliRunner()
    
    result = runner.invoke(cli, [
        "validate",
        "--in", "/nonexistent/path",
        "--meta", "/nonexistent/metadata.csv"
    ])
    
    # Click should handle path validation and exit with error
    assert result.exit_code != 0


def test_plan_command_success(tmp_path: Path):
    """Test plan command with valid data"""
    runner = CliRunner()
    
    # Setup
    in_dir = tmp_path / "input"
    in_dir.mkdir()
    (in_dir / "patient_001" / "T1w.nii.gz").parent.mkdir()
    (in_dir / "patient_001" / "T1w.nii.gz").write_text("fake data")
    
    meta_file = tmp_path / "metadata.csv"
    meta = pd.DataFrame({
        "participant_id": ["001"],
        "session_id": ["01"]
    })
    meta.to_csv(meta_file, index=False)
    
    out_dir = tmp_path / "output"
    
    result = runner.invoke(cli, [
        "plan",
        "--in", str(in_dir),
        "--meta", str(meta_file),
        "--out", str(out_dir)
    ])
    
    assert result.exit_code == 0
    assert "Planned" in result.output
    assert "operation(s)" in result.output


def test_plan_command_with_json_output(tmp_path: Path):
    """Test plan command saves JSON output"""
    runner = CliRunner()
    
    in_dir = tmp_path / "input"
    in_dir.mkdir()
    (in_dir / "patient_001" / "T1w.nii.gz").parent.mkdir()
    (in_dir / "patient_001" / "T1w.nii.gz").write_text("fake data")
    
    meta_file = tmp_path / "metadata.csv"
    meta = pd.DataFrame({
        "participant_id": ["001"],
        "session_id": ["01"]
    })
    meta.to_csv(meta_file, index=False)
    
    out_dir = tmp_path / "output"
    json_file = tmp_path / "plan.json"
    
    result = runner.invoke(cli, [
        "plan",
        "--in", str(in_dir),
        "--meta", str(meta_file),
        "--out", str(out_dir),
        "--json", str(json_file)
    ])
    
    assert result.exit_code == 0
    assert json_file.exists()
    assert "Wrote dry-run plan JSON" in result.output


def test_plan_command_derivatives_requires_pipeline(tmp_path: Path):
    """Test plan command requires pipeline-name for derivatives"""
    runner = CliRunner()
    
    in_dir = tmp_path / "input"
    in_dir.mkdir()
    (in_dir / "file.nii.gz").write_text("fake data")
    
    meta_file = tmp_path / "metadata.csv"
    meta = pd.DataFrame({"participant_id": ["001"]})
    meta.to_csv(meta_file, index=False)
    
    out_dir = tmp_path / "output"
    
    result = runner.invoke(cli, [
        "plan",
        "--in", str(in_dir),
        "--meta", str(meta_file),
        "--out", str(out_dir),
        "--dataset-type", "derivatives"
    ])
    
    assert result.exit_code == 1
    assert "pipeline-name is required" in result.output


def test_plan_command_derivatives_with_pipeline(tmp_path: Path):
    """Test plan command works for derivatives with pipeline name"""
    runner = CliRunner()
    
    in_dir = tmp_path / "input"
    in_dir.mkdir()
    (in_dir / "Ahmed.nii.gz").write_text("fake data")
    
    meta_file = tmp_path / "metadata.csv"
    meta = pd.DataFrame({"participant_id": ["Ahmed"]})
    meta.to_csv(meta_file, index=False)
    
    out_dir = tmp_path / "output"
    
    result = runner.invoke(cli, [
        "plan",
        "--in", str(in_dir),
        "--meta", str(meta_file),
        "--out", str(out_dir),
        "--dataset-type", "derivatives",
        "--pipeline-name", "test_pipeline"
    ])
    
    assert result.exit_code == 0
    assert "Planned" in result.output


def test_apply_command_success(tmp_path: Path):
    """Test apply command with valid data"""
    runner = CliRunner()
    
    # Setup
    in_dir = tmp_path / "input"
    in_dir.mkdir()
    (in_dir / "patient_001" / "T1w.nii.gz").parent.mkdir()
    (in_dir / "patient_001" / "T1w.nii.gz").write_text("fake data")
    
    meta_file = tmp_path / "metadata.csv"
    meta = pd.DataFrame({
        "participant_id": ["001"],
        "session_id": ["01"],
        "age": [30],
        "sex": ["F"]
    })
    meta.to_csv(meta_file, index=False)
    
    out_dir = tmp_path / "output"
    
    result = runner.invoke(cli, [
        "apply",
        "--in", str(in_dir),
        "--meta", str(meta_file),
        "--out", str(out_dir)
    ])
    
    assert result.exit_code == 0
    assert "Apply done" in result.output
    assert "BIDS root" in result.output
    # Check that output files were created
    assert (out_dir / "dataset_description.json").exists()
    assert (out_dir / "participants.tsv").exists()
    assert (out_dir / "README.md").exists()


def test_apply_command_with_move(tmp_path: Path):
    """Test apply command accepts --move option"""
    runner = CliRunner()
    
    in_dir = tmp_path / "input"
    in_dir.mkdir()
    # Create file in folder structure that matches participant
    (in_dir / "patient_001" / "T1w.nii.gz").parent.mkdir()
    (in_dir / "patient_001" / "T1w.nii.gz").write_text("fake data")
    
    meta_file = tmp_path / "metadata.csv"
    meta = pd.DataFrame({
        "participant_id": ["001"],
        "session_id": ["01"],
        "age": [30],
        "sex": ["F"]
    })
    meta.to_csv(meta_file, index=False)
    
    out_dir = tmp_path / "output"
    
    result = runner.invoke(cli, [
        "apply",
        "--in", str(in_dir),
        "--meta", str(meta_file),
        "--out", str(out_dir),
        "--move"
    ])
    
    # Command should run successfully (move functionality is tested in writer tests)
    assert result.exit_code == 0
    assert "Apply done" in result.output


def test_apply_command_derivatives_requires_pipeline(tmp_path: Path):
    """Test apply command requires pipeline-name for derivatives"""
    runner = CliRunner()
    
    in_dir = tmp_path / "input"
    in_dir.mkdir()
    (in_dir / "file.nii.gz").write_text("fake data")
    
    meta_file = tmp_path / "metadata.csv"
    meta = pd.DataFrame({"participant_id": ["001"]})
    meta.to_csv(meta_file, index=False)
    
    out_dir = tmp_path / "output"
    
    result = runner.invoke(cli, [
        "apply",
        "--in", str(in_dir),
        "--meta", str(meta_file),
        "--out", str(out_dir),
        "--dataset-type", "derivatives"
    ])
    
    assert result.exit_code == 1
    assert "pipeline-name is required" in result.output


def test_apply_command_with_phenotype_files(tmp_path: Path):
    """Test apply command with phenotype files"""
    runner = CliRunner()
    
    in_dir = tmp_path / "input"
    in_dir.mkdir()
    (in_dir / "patient_001" / "T1w.nii.gz").parent.mkdir()
    (in_dir / "patient_001" / "T1w.nii.gz").write_text("fake data")
    
    meta_file = tmp_path / "metadata.csv"
    meta = pd.DataFrame({
        "participant_id": ["001"],
        "session_id": ["01"]
    })
    meta.to_csv(meta_file, index=False)
    
    # Create phenotype file
    phenotype_file = tmp_path / "clinical_data.csv"
    phenotype_file.write_text("col1,col2\nval1,val2")
    
    out_dir = tmp_path / "output"
    
    result = runner.invoke(cli, [
        "apply",
        "--in", str(in_dir),
        "--meta", str(meta_file),
        "--out", str(out_dir),
        "--phenotype", str(phenotype_file)
    ])
    
    assert result.exit_code == 0
    assert "phenotype file(s)" in result.output
    assert (out_dir / "phenotype" / "clinical_data.csv").exists()


def test_apply_command_validation_error_exits(tmp_path: Path):
    """Test apply command exits on validation errors (ERROR level)"""
    runner = CliRunner()
    
    in_dir = tmp_path / "input"
    in_dir.mkdir()
    
    # Create metadata without required participant_id column (this causes ERROR)
    meta_file = tmp_path / "metadata.csv"
    meta = pd.DataFrame({
        "session_id": ["01"],
        "age": [30]
    })
    meta.to_csv(meta_file, index=False)
    
    out_dir = tmp_path / "output"
    
    result = runner.invoke(cli, [
        "apply",
        "--in", str(in_dir),
        "--meta", str(meta_file),
        "--out", str(out_dir)
    ])
    
    # Should exit with error due to ERROR-level validation failure (missing required column)
    assert result.exit_code == 1
    assert "ERROR-level issues" in result.output or "Validation reported issues" in result.output

