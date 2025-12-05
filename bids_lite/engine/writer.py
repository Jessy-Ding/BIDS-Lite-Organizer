from pathlib import Path
from typing import List, Dict, Any, Optional
import shutil
import json
import pandas as pd
from datetime import date

def _ensure_parent_dir(path: Path) -> None:
    """Ensure the parent directory of the path exists"""
    path.parent.mkdir(parents=True, exist_ok=True)

def apply_transforms(plan: List[Dict[str, Any]], copy: bool = True) -> Dict[str, Any]:
    """
    Execute copy/move operations from `plan` produced by plan_transforms().
    Returns a summary dict with counts and any errors.
    """
    summary = {"n_ops": 0, "n_ok": 0, "n_failed": 0, "errors": []}

    for op in plan:
        src = Path(op["src"])
        dst = Path(op["dst"])
        action = op.get("action", "copy")

        summary["n_ops"] += 1

        if not src.exists():
            summary["n_failed"] += 1
            summary["errors"].append(
                f"Source missing: {src}"
            )
            continue

        try:
            _ensure_parent_dir(dst)
            if copy or action == "copy":
                shutil.copy2(src, dst)  # copy2 keeps timestamps
            else:
                shutil.move(src, dst)
            summary["n_ok"] += 1
        except Exception as e:
            summary["n_failed"] += 1
            summary["errors"].append(f"Failed {action} {src} -> {dst}: {e}")

    return summary


def write_dataset_description(out_dir: Path, dataset_type: str = "raw", 
                              pipeline_name: Optional[str] = None) -> None:
    """
    Write a minimal BIDS-compliant dataset_description.json.
    
    Args:
        out_dir: Output directory (for raw) or derivatives/pipeline_name (for derivatives)
        dataset_type: "raw" or "derivatives"
        pipeline_name: Pipeline name for derivatives (required if dataset_type is "derivatives")
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dd_path = out_dir / "dataset_description.json"

    # Build payload based on dataset type
    if dataset_type == "derivatives":
        if pipeline_name is None:
            raise ValueError("pipeline_name is required for derivatives dataset type")
        payload = {
            "Name": f"BIDS Lite Derivatives - {pipeline_name}",
            "BIDSVersion": "1.9.0",
            "DatasetType": "derivatives",
            "PipelineDescription": {
                "Name": pipeline_name,
                "Version": "0.1.0"
            },
            "GeneratedBy": [
                {
                    "Name": "BIDS Lite",
                    "Version": "0.1.0"
                }
            ],
            "Date": str(date.today())
        }
    else:
        payload = {
            "Name": "BIDS Lite Dataset",
            "BIDSVersion": "1.9.0",
            "DatasetType": "raw",
            "Authors": ["Mengyuan (Jessy) Ding"],
            "GeneratedBy": [
                {
                    "Name": "BIDS Lite",
                    "Version": "0.1.0"
                }
            ],
            "Date": str(date.today())
        }
    
    dd_path.write_text(json.dumps(payload, indent=2))


def write_participants_tsv(out_dir: Path, meta: pd.DataFrame) -> None:
    """
    Write participants.tsv into BIDS root. Assumes `meta` is already normalized.
    Handles missing columns gracefully (age, sex, session_id may be missing).
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    p_path = out_dir / "participants.tsv"

    # BIDS requires a column called participant_id, prefixed with "sub-"
    df = meta.copy()
    df["participant_id"] = df["participant_id"].apply(lambda x: f"sub-{x}")
    
    # Keep available columns (age, sex, session_id are optional)
    # Include all columns that exist, prioritizing core BIDS columns
    core_cols = ["participant_id"]
    optional_cols = ["session_id", "age", "sex"]
    
    # Add core column first
    cols = [core_cols[0]]
    # Add optional columns if they exist
    for col in optional_cols:
        if col in df.columns:
            cols.append(col)
    
    # Also include any other columns that might be useful
    other_cols = [c for c in df.columns if c not in cols and c != "modality"]
    cols.extend(other_cols)
    
    df[cols].to_csv(p_path, sep="\t", index=False)


def write_phenotype_files(out_dir: Path, phenotype_files: List[Path], 
                         dataset_type: str = "raw", pipeline_name: Optional[str] = None) -> None:
    """
    Copy additional data files to phenotype/ folder in BIDS structure.
    These are typically supplementary data files that don't match the main participants.tsv format.
    Supports various file formats: CSV, TSV, XLS, XLSX, PDF, and others.
    
    For raw data: phenotype/ folder goes in BIDS root
    For derivatives: phenotype/ folder goes in derivatives/pipeline_name/
    
    Args:
        out_dir: BIDS output directory (root for raw, or base for derivatives)
        phenotype_files: List of paths to files to copy to phenotype/ (CSV, TSV, XLS, PDF, etc.)
        dataset_type: "raw" or "derivatives"
        pipeline_name: Pipeline name for derivatives (required if dataset_type is "derivatives")
    """
    if not phenotype_files:
        return
    
    out_dir = Path(out_dir)
    
    # Determine where to place phenotype folder
    if dataset_type == "derivatives":
        if pipeline_name is None:
            raise ValueError("pipeline_name is required for derivatives dataset type")
        # For derivatives: phenotype/ goes in derivatives/pipeline_name/
        phenotype_dir = out_dir / "derivatives" / pipeline_name / "phenotype"
    else:
        # For raw data: phenotype/ goes in BIDS root
        phenotype_dir = out_dir / "phenotype"
    
    phenotype_dir.mkdir(parents=True, exist_ok=True)
    
    for phenotype_file in phenotype_files:
        if not phenotype_file.exists():
            continue
        
        # Copy file to phenotype directory, preserving name and extension
        dest_path = phenotype_dir / phenotype_file.name
        shutil.copy2(phenotype_file, dest_path)

def write_publication_files(out_dir: Path, publication_files: List[Path], pipeline_name: Optional[str] = None) -> None:
    """
    Copy publication-related files (paper key files) to derivatives/publications/ folder.
    
    These files are typically key results from published or to-be-published papers,
    such as circuit/connectivity results, key images, etc. They are stored separately
    for easy access by other researchers for comparison purposes.
    
    Args:
        out_dir: BIDS output directory root
        publication_files: List of paths to publication files to copy
        pipeline_name: Pipeline name (for derivatives structure)
    """
    if not publication_files:
        return
    
    out_dir = Path(out_dir)
    
    # Create publications directory
    # For derivatives: derivatives/publications/
    # For raw data: publications/ (at root level, though typically only derivatives have publications)
    publications_dir = out_dir / "derivatives" / "publications"
    if pipeline_name:
        # Optionally organize by pipeline: derivatives/publications/pipeline_name/
        publications_dir = out_dir / "derivatives" / "publications" / pipeline_name
    
    publications_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy each publication file
    for pub_file in publication_files:
        pub_file = Path(pub_file)
        if not pub_file.exists():
            continue
        
        # Copy file to publications directory, preserving name and extension
        dest_path = publications_dir / pub_file.name
        shutil.copy2(pub_file, dest_path)

def write_readme(out_dir: Path, template: Optional[Path] = None) -> None:
    """
    Write a minimal README.md if not already present.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    readme_path = out_dir / "README.md"
    if readme_path.exists():
        return
    if template is not None:
        text = Path(template).read_text()
    else:
        lines = [
            "# BIDS Lite Dataset\n",
            "This dataset was organized using BIDS Lite.\n",
            "You can edit this README to add study-specific information.\n"
        ]
        text = "".join(lines)
    readme_path.write_text(text)


def write_report(out_dir: Path,
                 plan: List[Dict[str, Any]],
                 summary: Dict[str, Any],
                 issues: Optional[List[Dict[str, Any]]] = None) -> None:
    """
    Write a simple Markdown report summarizing validation issues and operations.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    r_path = out_dir / "logs" / "report.md"
    r_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# BIDS Lite Organizer Report\n")
    if issues:
        lines.append("## Validation Issues\n")
        if not issues:
            lines.append("- None\n")
        else:
            for it in issues:
                lines.append(f"- **{it.get('level', 'INFO')} {it.get('code', '')}**: {it.get('msg', '')}\n")
    else:
        lines.append("## Validation Issues\n- None (not provided to report)\n")

    lines.append("\n## Operations Summary\n")
    lines.append(f"- Planned operations: {summary.get('n_ops', 0)}\n")
    lines.append(f"- Successful: {summary.get('n_ok', 0)}\n")
    lines.append(f"- Failed: {summary.get('n_failed', 0)}\n")

    if summary.get("errors"):
        lines.append("\n### Operation Errors\n")
        for e in summary["errors"]:
            lines.append(f"- {e}\n")

    lines.append("\n## Planned Operations (first 20)\n")
    for op in plan[:20]:
        lines.append(f"- {op['src']}  →  {op['dst']}\n")

    r_path.write_text("".join(lines))
