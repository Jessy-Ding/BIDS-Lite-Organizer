# bids_lite/cli.py

import json
import sys
import click
from pathlib import Path
from .engine.checklist import load_minimal_spec
from .engine.validator import read_metadata, validate_inputs
from .engine.normalizer import normalize_ids
from .engine.planner import plan_transforms

@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli():
    """BIDS Lite Organizer (CLI) — Iteration 1: validate and plan (dry-run)."""

@cli.command()
@click.option("--in", "in_dir", type=click.Path(exists=True, file_okay=False), required=True, help="Incoming folder with messy files.")
@click.option("--meta", "meta_path", type=click.Path(exists=True, dir_okay=False), required=True, help="Metadata TSV/CSV.")
def validate(in_dir, meta_path):
    """Validate metadata + basic file existence."""
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
@click.option("--out", "out_dir", type=click.Path(file_okay=False), required=True, help="Target BIDS output.")
@click.option("--json", "json_out", type=click.Path(dir_okay=False), required=False, help="Optional path to write the dry-run plan JSON.")
def plan(in_dir, meta_path, out_dir, json_out):
    """Produce a DRY-RUN transform plan (no files are moved)."""
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
    plan_list = plan_transforms(Path(in_dir), Path(out_dir), meta_norm) # plan transforms
    click.echo(f"Planned {len(plan_list)} operation(s). Example:")
    for op in plan_list[:5]:
        click.echo(f"- {op['src']}  ->  {op['dst']}")
    if json_out:
        Path(json_out).write_text(json.dumps(plan_list, indent=2))
        click.echo(f"Wrote dry-run plan JSON to: {json_out}")

if __name__ == "__main__":
    cli()