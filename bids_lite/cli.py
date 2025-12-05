# bids_lite/cli.py

import json
import sys
import click
from pathlib import Path
from .engine.checklist import load_minimal_spec
from .engine.validator import read_metadata, validate_inputs
from .engine.normalizer import normalize_ids
from .engine.planner import plan_transforms
from .engine.writer import apply_transforms, write_dataset_description, write_participants_tsv, write_report, write_readme, write_phenotype_files, write_publication_files


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli():
    """BIDS Lite Organizer - Convert messy brain imaging data to BIDS format.
    
    This tool automatically organizes neuroimaging data into BIDS (Brain Imaging Data Structure)
    format, even when your input data has messy filenames and folder structures.
    
    Quick start:
      1. Validate your data:
         bids-lite validate --in ./input_data --meta ./metadata.csv
      
      2. Preview the organization plan (dry-run):
         bids-lite plan --in ./input_data --meta ./metadata.csv --out ./bids_out
      
      3. Apply the transformations:
         bids-lite apply --in ./input_data --meta ./metadata.csv --out ./bids_out
    
    For detailed documentation, examples, and troubleshooting, see README.md
    """

@cli.command()
@click.option("--in", "in_dir", type=click.Path(exists=True, file_okay=False), required=True, help="Incoming folder with messy files.")
@click.option("--meta", "meta_path", type=click.Path(exists=True, dir_okay=False), required=True, help="Metadata file (CSV, TSV, or Excel .xlsx/.xls).")
def validate(in_dir, meta_path):
    """Validate metadata and check if files can be matched.
    
    This command checks your input data for common issues before organizing it.
    
    What it checks:
    - Required columns in metadata (only 'participant_id' is strictly required)
    - Whether files can be matched to participants in metadata
    - Data format issues (e.g., non-standard sex values)
    
    Usage:
      bids-lite validate --in ./input_data --meta ./metadata.csv
    
    Run this first to catch problems before planning or applying transformations.
    If validation passes, you can proceed with 'plan' and 'apply' commands.
    """
    spec = load_minimal_spec() ## load spec for Iter-1
    meta = read_metadata(Path(meta_path))  # read metadata file
    issues = validate_inputs(Path(in_dir), meta, spec) # validate
    if issues:
        click.echo(f"Found {len(issues)} issue(s):")
        for it in issues:
            click.echo(f"- [{it['level']}] {it['code']}: {it['msg']}")
        sys.exit(1)  # exit if issues found 
    click.echo("Validation passed. No blocking issues found.")


@cli.command()
@click.option("--in", "in_dir", type=click.Path(exists=True, file_okay=False), required=True)
@click.option("--meta", "meta_path", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--out", "out_dir", type=click.Path(file_okay=False), required=True, 
              help="Output directory where BIDS-organized data will be created.")
@click.option("--json", "json_out", type=click.Path(dir_okay=False), required=False, 
              help="Optional: Save the preview plan to a JSON file for review.")
@click.option("--dataset-type", "dataset_type", type=click.Choice(["raw", "derivatives"], case_sensitive=False), 
              default="raw", 
              help="Dataset type: 'raw' for original scans, 'derivatives' for processed data (default: raw).")
@click.option("--pipeline-name", "pipeline_name", type=str, required=False,
              help="Pipeline name for derivatives (e.g., 'lesion_analysis', 'connectivity'). Required if dataset-type is 'derivatives'.")
@click.option("--match-all-modalities/--match-specified-only", "match_all_modalities", default=True,
              help="If enabled (default), one metadata row matches all files for that participant/session. If disabled, only matches files with specified modality. Recommended: enable if one patient has multiple scan types (T1w, T2w, FLAIR, etc.).")
def plan(in_dir, meta_path, out_dir, json_out, dataset_type, pipeline_name, match_all_modalities):
    """Preview file organization plan (dry-run, no files are moved).
    
    This command shows you exactly what files will be organized and where they'll
    be placed in the BIDS structure, without actually moving or copying any files.
    
    Usage:
      bids-lite plan --in ./input_data --meta ./metadata.csv --out ./bids_out
    
    Optional:
      --json plan.json  # Save the plan to a JSON file for review
      --match-all-modalities / --match-specified-only  # Match all files per participant/session (default: enabled)
    
    Use this to verify your setup before running 'apply'. This is especially
    useful for checking that participant IDs are matched correctly.
    """
    dataset_type = dataset_type.lower()
    if dataset_type == "derivatives" and not pipeline_name:
        click.echo("Error: --pipeline-name is required when --dataset-type is 'derivatives'", err=True)
        sys.exit(1)
    
    spec = load_minimal_spec() ## load spec for Iter-1
    meta = read_metadata(Path(meta_path)) # read metadata file
    # validate first
    issues = validate_inputs(Path(in_dir), meta, spec)
    if issues:
        click.echo("Please fix validation issues before planning.")
        for it in issues:
            click.echo(f"- [{it['level']}] {it['code']}: {it['msg']}")
        sys.exit(1)
    meta_norm = normalize_ids(meta) # normalize IDs (warn only)
    plan_list = plan_transforms(Path(in_dir), Path(out_dir), meta_norm, dataset_type, pipeline_name, match_all_modalities=match_all_modalities) # plan transforms
    click.echo(f"Planned {len(plan_list)} operation(s). Example:")
    for op in plan_list[:5]:
        click.echo(f"- {op['src']}  ->  {op['dst']}")
    if json_out:
        Path(json_out).write_text(json.dumps(plan_list, indent=2))
        click.echo(f"Wrote dry-run plan JSON to: {json_out}")


@cli.command()
@click.option("--in", "in_dir", type=click.Path(exists=True, file_okay=False), required=True)
@click.option("--meta", "meta_path", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--out", "out_dir", type=click.Path(file_okay=False), required=True,
              help="Target BIDS output directory.")
@click.option("--copy/--move", "copy", default=True,
              help="Copy files instead of moving them (default: copy).")
@click.option("--readme-template", "readme_template",
              type=click.Path(exists=True, dir_okay=False),
              required=False,
              help="Optional README template to copy into the BIDS root.")
@click.option("--dataset-type", "dataset_type", type=click.Choice(["raw", "derivatives"], case_sensitive=False), 
              default="raw", help="Dataset type: 'raw' or 'derivatives' (default: raw).")
@click.option("--pipeline-name", "pipeline_name", type=str, required=False,
              help="Pipeline name for derivatives (required if dataset-type is 'derivatives').")
@click.option("--phenotype", "phenotype_files", multiple=True,
              type=click.Path(exists=True, dir_okay=False),
              help="Additional data files (CSV, TSV, XLS, PDF, etc.) to copy to phenotype/ folder (can specify multiple times, available for both raw and derivatives).")
@click.option("--publication", "publication_files", multiple=True,
              type=click.Path(exists=True, dir_okay=False),
              help="Paper-related key files (circuit/connectivity results, key images, etc.) to copy to derivatives/publications/ folder (can specify multiple times, derivatives only).")
@click.option("--match-all-modalities/--match-specified-only", "match_all_modalities", default=True,
              help="If True, one metadata row matches all files for that participant/session. If False, only match specified modality.")
def apply(in_dir, meta_path, out_dir, copy, readme_template, dataset_type, pipeline_name, phenotype_files, publication_files, match_all_modalities):
    """Organize files into BIDS format.
    
    This is the main command that actually organizes your files.
    Steps:
    1. Validates inputs
    2. Matches files to participants
    3. Organizes files into BIDS structure
    4. Generates BIDS metadata files
    
    Tip: Run 'plan' first to preview what will happen.
    """
    dataset_type = dataset_type.lower()
    if dataset_type == "derivatives" and not pipeline_name:
        click.echo("Error: --pipeline-name is required when --dataset-type is 'derivatives'", err=True)
        sys.exit(1)
    
    in_dir = Path(in_dir)
    meta_path = Path(meta_path)
    out_dir = Path(out_dir)
    template_path = Path(readme_template) if readme_template else None
    
    # Determine where to write dataset_description.json
    if dataset_type == "derivatives":
        desc_dir = out_dir / "derivatives" / pipeline_name
    else:
        desc_dir = out_dir

    spec = load_minimal_spec()
    meta = read_metadata(meta_path)

    # 1) validate
    issues = validate_inputs(in_dir, meta, spec)
    if issues:
        click.echo("Validation reported issues:")
        for it in issues:
            click.echo(f"- [{it['level']}] {it['code']}: {it['msg']}")
        # optional: allow continue if only WARN, here just exit if ERROR
        if any(it["level"] == "ERROR" for it in issues):
            click.echo("ERROR-level issues detected. Aborting apply.")
            sys.exit(1)

    # 2) normalize IDs
    meta_norm = normalize_ids(meta)

    # 3) plan transforms
    plan = plan_transforms(in_dir, out_dir, meta_norm, dataset_type, pipeline_name, match_all_modalities=match_all_modalities)

    # 4) apply transforms
    summary = apply_transforms(plan, copy=copy)

    # 5) write BIDS sidecar files
    write_dataset_description(desc_dir, dataset_type, pipeline_name)
    # participants.tsv: for raw data goes in BIDS root, for derivatives goes in derivatives/pipeline_name/
    if dataset_type == "raw":
        write_participants_tsv(out_dir, meta_norm)
    else:
        # For derivatives, write participants.tsv in the derivatives/pipeline_name/ directory
        write_participants_tsv(desc_dir, meta_norm)
    write_readme(desc_dir, template_path)
    write_report(desc_dir, plan, summary, issues)
    
    # 6) write phenotype files (available for both raw and derivatives)
    if phenotype_files:
        phenotype_paths = [Path(p) for p in phenotype_files]
        write_phenotype_files(out_dir, phenotype_paths, dataset_type, pipeline_name)
        if dataset_type == "derivatives":
            click.echo(f"Copied {len(phenotype_paths)} phenotype file(s) to {out_dir / 'derivatives' / pipeline_name / 'phenotype'}/")
        else:
            click.echo(f"Copied {len(phenotype_paths)} phenotype file(s) to {out_dir / 'phenotype'}/")
    
    # 7) write publication files (only for derivatives)
    if dataset_type == "derivatives" and publication_files:
        publication_paths = [Path(p) for p in publication_files]
        write_publication_files(out_dir, publication_paths, pipeline_name)
        click.echo(f"Copied {len(publication_paths)} publication file(s) to {out_dir / 'derivatives' / 'publications' / pipeline_name}/")

    click.echo(f"Apply done: {summary['n_ok']} ok, {summary['n_failed']} failed.")
    click.echo(f"BIDS root: {out_dir}")

if __name__ == "__main__":
    cli()