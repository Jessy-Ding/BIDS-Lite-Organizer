# BIDS(Brain Imaging Data Structure)-Lite-Organizer-CLI
Lightweight desktop app to automatically organize brain imaging data into BIDS format (Idea proposed by Dr. Michael Fox, MD, PhD, Brigham and Women's Hospital). Also, part of this project serves as a semester-long project for the course CS5001 at Khoury College of Computer Sciences, Northeastern University, Oakland, CA.

## Abstract
BIDS Lite Organizer (CLI) is a Python program that helps brain-imaging researchers convert messy MRI data (mixed nii.gz/nii files + a small metadata table) into a minimal Brain Imaging Data Structure (BIDS) layout. The Iteration-1 MVP focuses on structural T1-weighted data only, performing input validation, ID normalization, and a dry-run reorganization plan before applying safe file moves. The tool outputs a minimal BIDS tree plus `dataset_description.json`, `participants.tsv`, and a human-readable report—without requiring any coding background or GUI. Future iterations will extend modality coverage and error handling.

## Problem & Motivation
### Problem. 
Labs often receive heterogeneous MRI data collected over years across sites. File names, subject/session IDs, and metadata are inconsistent, which blocks analysis, sharing, and reproducibility.
### Motivation. 
A simple, offline CLI that enforces a small, opinionated subset of BIDS for T1w(T1-weighted (structural MRI)) can dramatically lower the barrier for non-programmers: validate a short checklist, normalize IDs, preview a reorganization plan (dry-run), then apply safely to produce a clean, minimal BIDS dataset ready for downstream tools.

## Reduced Scope for Iteration-1
Planned functionalities (6):
	1.	load_minimal_spec() – Load a hard-coded minimal T1w spec (no external schema files).
	2.	read_metadata(path) – Read TSV/CSV with required columns (participant_id, session_id, age, sex).
	3.	validate_inputs(in_dir, meta) – Check required columns, illegal characters, and file existence. Iter-1
	4.	normalize_ids(meta) – Normalize subject/session IDs (lowercase, zero-pad, strip spaces). Iter-1
	5.	plan_transforms(in_dir, meta) – Produce a dry-run plan: source → target BIDS paths (JSON/print). Iter-1
	6.	apply_transforms(plan, out_dir) – Execute safe copies/moves; write dataset_description.json, participants.tsv, and report.md.  Iter-2

# Program
## `requirements.txt` (minimum)


