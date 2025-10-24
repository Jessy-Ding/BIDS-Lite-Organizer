# BIDS(Brain Imaging Data Structure)-Lite-Organizer-CLI
A CLI to automatically organize brain imaging data into BIDS format (Idea proposed by Dr. Michael Fox, MD, PhD, Brigham and Women's Hospital). Also, part of this project serves as a semester-long project for the course CS5001 at Khoury College of Computer Sciences, Northeastern University, Oakland, CA.


## Project Description and Motivation 
BIDS Lite Organizer is a lightweight Python command-line application designed to help researchers and clinicians organize messy brain imaging data into the Brain Imaging Data Structure (BIDS) format. Many neuroimaging datasets are collected across different labs and years, resulting in inconsistent filenames, missing metadata, and poor reproducibility. This tool provides a simple, automated way to validate metadata, normalize participant/session identifiers, and plan safe file transformations (dry-run) before reorganizing data into a clean, standardized structure. The goal is to lower the technical barrier for non-programmers and improve research reproducibility.


## Functionalities 
Planned functionalities (7):

	1.	load_minimal_spec() – Load a hard-coded minimal T1w spec. Iter-1

	2.	read_metadata(path) – Read TSV/CSV with required columns (participant_id, session_id, age, sex). Iter-1

	3.	validate_inputs(in_dir, meta) – Check required columns, illegal characters, and file existence. Iter-1

	4.	normalize_ids(meta) – Normalize subject/session IDs (lowercase, zero-pad, strip spaces). Iter-1

	5.	plan_transforms(in_dir, meta) – Produce a dry-run plan: source → target BIDS paths (JSON/print). Iter-1
    
	6.	apply_transforms(plan, out_dir) – Execute safe copies/moves; write dataset_description.json, participants.tsv, and report.md.  Iter-2

	7.  expand to more MRI modalities and wrap up into off-line desktop softwares. Iter-2


## Iter-1 Challenges and Solutions 
•	Challenge 1: Metadata files from different labs/researchers have inconsistent column names or missing fields.
	- Implemented a strict validation function that detects missing columns and illegal characters early.
•	Challenge 2: Subject/session IDs often contain spaces or special characters.
	- Added a normalization layer with regex filtering and zero-padding.
•	Challenge 3: Testing relative imports during development caused ModuleNotFoundError.
	- Fixed by adding the project root to sys.path and setting up consistent test import paths.


## Steps to run the program
Step1: env set up
	install the py environment requested by `requirements.txt`
Step2: CLI usage examples
locate(`cd`) to your installed parent project root, then run the following command in your terminal:
```bash
	python -m bids_lite.cli validate --in ./use_case_example/T1w --meta ./use_case_example/metadata/metadata.csv
	python -m bids_lite.cli plan --in ./use_case_example/T1w --meta ./use_case_example/metadata/metadata.csv --out ./bids_out --json ./plan.json
```

## Code Repository on GitHub
[BIDS-Lite-Organizer-CLI](https://github.com/Jessy-Ding/BIDS-Lite-Organizer-CLI)

## Demo Recording

