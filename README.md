[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)]()

# BIDS (Brain Imaging Data Structure) Lite Organizer

A lightweight Python tool to automatically organize messy brain imaging data into the Brain Imaging Data Structure (BIDS) format. Supports both Command-Line Interface (CLI) and Graphical User Interface (GUI) for maximum flexibility.

**Idea proposed by:** Dr. Michael Fox, MD, PhD, Brigham and Women's Hospital  
**Project for:** CS5001, Khoury College of Computer Sciences, Northeastern University, Oakland, CA

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Input Requirements](#input-requirements)
- [CLI Usage](#cli-usage)
- [GUI Usage](#gui-usage)
- [Advanced Features](#advanced-features)
- [Output Structure](#output-structure)
- [Examples](#examples)
- [Common Questions & Troubleshooting](#common-questions--troubleshooting)
- [Troubleshooting](#troubleshooting)
- [Testing and Validation](#testing-and-validation)
- [Challenges and Lessons Learned](#challenges-and-lessons-learned)
- [Future Work](#future-work)
- [Project Context](#project-context)
- [Code Repository](#code-repository)
- [Demo Videos](#demo-videos)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

BIDS Lite Organizer is designed to help researchers and clinicians organize neuroimaging data into BIDS format without requiring BIDS-compliant input data. The tool automatically:

- **Validates** metadata and file structure
- **Normalizes** participant/session IDs (handles messy formats)
- **Matches** files to participants intelligently
- **Detects** modalities from filenames
- **Organizes** files into proper BIDS structure
- **Generates** BIDS-compliant metadata files

### Why BIDS Lite Organizer?

Many neuroimaging datasets are collected across different labs and years, resulting in:
- Inconsistent filenames (`patient_001`, `patient-001`, `patient 001`, `Smith2023A`)
- Missing or incomplete metadata
- Non-standard folder structures
- Poor reproducibility

This tool bridges the gap between messy real-world data and the BIDS standard, making it accessible to non-programmers while maintaining full BIDS compliance.

---

## Key Features

-  **Flexible Input**: Accepts any file organization and naming convention  
-  **Automatic BIDS Conversion**: Converts messy data to standard BIDS format  
-  **Smart ID Matching**: Handles numeric (`001`, `01`, `1`) and alphanumeric (`Smith2023A`) IDs  
-  **Intelligent File Matching**: Finds files by participant ID even with different formats  
-  **Modality Detection**: Auto-detects T1w, T2w, FLAIR, bold, lesion, connectivity from filenames  
-  **Missing Data Handling**: Works with incomplete metadata (only `participant_id` required)  
-  **One-Patient-Per-Folder**: Supports common organization where each patient has their own folder  
-  **Derivatives Support**: Handles processed data (lesion maps, connectivity matrices, etc.)  
-  **Phenotype Files**: Supports additional data files for raw datasets  
-  **Publication Files**: Stores paper-related key files for derivatives datasets  
-  **Dual Interface**: Both CLI and GUI available

---

## Installation

### Requirements

- Python 3.9 or higher
- Dependencies listed in `requirements.txt`

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd Project_BIDS-Lite

# Install dependencies
pip install -r requirements.txt
```

---

## Quick Start

###  Try the Examples First!

**We've prepared 4 complete, runnable examples** with full input and output. Start here:

 **[See All Examples →](examples/EXAMPLES.md)**

Each example includes:
- Complete input data
- Ready-to-run commands
- Full output results
- Detailed explanations

**Quick links:**
- [Example 1: Basic Raw Dataset](examples/example1_basic_raw/) - Simplest example
- [Example 2: Raw with Phenotype Files](examples/example2_raw_with_phenotype/) - Additional data files
- [Example 3: Derivatives Dataset](examples/example3_derivatives/) - Processed data
- [Example 4: Derivatives with Publications](examples/example4_derivatives_with_publications/) - Paper-related files

### CLI - Basic Example

```bash
# 1. Validate your data
python -m bids_lite.cli validate --in ./input_data --meta ./metadata.csv

# 2. Plan transformations (dry-run)
python -m bids_lite.cli plan --in ./input_data --meta ./metadata.csv --out ./bids_out

# 3. Apply transformations
python -m bids_lite.cli apply --in ./input_data --meta ./metadata.csv --out ./bids_out
```

### GUI - Basic Example

```bash
# Launch the GUI
python ui/app.py
```

Then use the graphical interface to:
1. Select input directory and metadata file
2. Choose output directory
3. Click "Validate" to check your data
4. Click "Plan" to preview transformations
5. Click "Apply" to execute

---

## Input Requirements

### Simple Rule: **You don't need to organize your data in BIDS format!**

The program automatically converts messy data to BIDS format.

### 1. Input Data Organization (Any Format Works!)

Your input data can be organized in **any way you want**:

**Option A: One patient per folder** (recommended)
```
input_data/
  patient_001/
    T1w scan.nii.gz
    T2w image.nii.gz
  patient_002/
    FLAIR.nii.gz
```

**Option B: All files in one folder**
```
input_data/
  patient_001_T1w.nii.gz
  patient_002_FLAIR.nii.gz
```

**Option C: Mixed organization** - any structure works!

### 2. Metadata File Requirements (Minimal!)

**Supported formats:** CSV, TSV, or Excel (.xlsx, .xls)

Your metadata file only needs **one required column**:

- **`participant_id`** (required): Patient/participant identifier

**Supported ID formats:**
- **Numeric**: `001`, `01`, `1`, `patient_001`, `patient-001`, `patient 001`
- **Alphanumeric** (for derivatives/case reports): 
  - `Smith2023A`, `Smith-2023-B`, `Jones2022EE`
  - `Abdullah`, `Ross1981-case2`, `Erburu-Iriarte`
  - Supports author names + year + case ID format
  - Case-insensitive matching
  - Handles separators: `-`, `_`, spaces (automatically normalized)

**Optional columns** (include if available):
- `session_id`: Session identifier (visit/timepoint, NOT modality/sequence)
  - **What is a session?** A scanning session or visit (e.g., baseline, 6-month follow-up)
  - **NOT the same as modality**: Modality is the scan type (T1w, T2w, FLAIR, bold)
  - **For raw data**: Optional (defaults to `"01"` if missing - BIDS requires sessions)
  - **For derivatives**: Optional (if missing, no session folders created)
- `age`: Age in years
- `sex`: M/F/Male/Female (or leave empty)
- `modality`: Specific modality (usually auto-detected from filename)
- Any other columns you want to include

**Important: Session vs. Modality**
- **Session** = Visit/Timepoint (when: baseline, follow-up, etc.)
- **Modality** = Sequence Type (what: T1w, T2w, FLAIR, bold, etc.)
- One session can have multiple modalities (T1w, T2w, FLAIR all in same visit)

**Session handling:**
- **Raw data**: BIDS requires sessions, so `ses-01/` folders are always created (defaults to `"01"` if `session_id` is missing)
- **Derivatives**: Sessions are optional - no `ses-XX/` folders created if `session_id` is missing
- See [`BIDS_CONCEPTS.md`](BIDS_CONCEPTS.md) and [`SESSION_HANDLING.md`](SESSION_HANDLING.md) for details

**Example minimal metadata** (`metadata.csv`):
```csv
participant_id
001
002
003
```

**Example with alphanumeric IDs** (derivatives/case reports):
```csv
participant_id
Smith2023A
Smith2023B
Jones2022EE
Abdullah
Ross1981-case2
```

**Example with optional columns**:
```csv
participant_id,session_id,age,sex
001,01,30,M
002,01,25,F
003,02,40,M
```

### 3. File Naming (Any Format Works!)

Your image files can have **any names** - the program will automatically:
- Extract participant IDs from filenames or folder names
- Detect modality (T1w, T2w, FLAIR, bold, lesion, connectivity, etc.) from filename
- Convert special characters (`-`, `_`, spaces) to BIDS format
- Organize files into proper BIDS structure

**Supported filename formats** (examples):
- Numeric IDs: `patient_001_T1w.nii.gz`, `patient-001-T1w scan.nii.gz`, `001_T1w.nii.gz`
- Alphanumeric IDs: 
  - `Smith2023A_lesion.nii.gz`
  - `Anhedonia_LesionTracing_Abdullah_2015_Case07_f.nii.gz`
  - `Insomnia_LesionTracing_Carecchio_2009_Case01_Updated_112523.nii.gz`
- BIDS format: `sub-001_ses-01_T1w.nii.gz`
- Any other format with participant ID somewhere in the name or folder!

**Supported file extensions:**
- `.nii`, `.nii.gz` (NIfTI format)

---

## CLI Usage

### Command Overview

BIDS Lite Organizer provides three main commands:

1. **`validate`** - Validate metadata and file structure
2. **`plan`** - Generate a dry-run transformation plan
3. **`apply`** - Execute transformations and create BIDS structure

### 1. Validate Command

Validates metadata and checks if files can be matched to participants.

**What it checks:**
- Required columns in metadata (only `participant_id` is strictly required)
- Whether files can be matched to participants in metadata
- Data format issues (e.g., non-standard sex values)

```bash
python -m bids_lite.cli validate --in <input_directory> --meta <metadata_file>
```

**Options:**
- `--in, --in_dir`: Input directory containing your image files (required)
- `--meta, --meta_path`: Path to metadata file - CSV, TSV, or Excel format (required)

**Example:**
```bash
python -m bids_lite.cli validate --in ./input_data --meta ./metadata.csv
```

**Output:**
- Lists validation issues (errors or warnings)
- Exits with code 1 if errors found, 0 if validation passes
- **Tip**: Run this first to catch problems before planning or applying transformations

### 2. Plan Command

Generates a dry-run transformation plan without moving any files. This shows you exactly what files will be organized and where they'll be placed in the BIDS structure.

```bash
python -m bids_lite.cli plan --in <input_directory> --meta <metadata_file> --out <output_directory> [OPTIONS]
```

**Required Options:**
- `--in, --in_dir`: Input directory containing your image files
- `--meta, --meta_path`: Path to metadata file (CSV, TSV, or Excel)
- `--out, --out_dir`: Target BIDS output directory (will be created if it doesn't exist)

**Optional Options:**
- `--json, --json_out`: Path to save the plan as JSON file (e.g., `--json plan.json`)
- `--dataset-type`: Dataset type - `raw` (original scans) or `derivatives` (processed data). Default: `raw`
- `--pipeline-name`: Pipeline name for derivatives (e.g., `lesion_analysis`, `connectivity`). Required if `--dataset-type` is `derivatives`
- `--match-all-modalities / --match-specified-only`: 
  - `--match-all-modalities` (default): One metadata row matches all files for that participant/session. **Recommended** if one patient has multiple scan types (T1w, T2w, FLAIR, etc.)
  - `--match-specified-only`: Only match files with specified modality in metadata

**Example:**
```bash
# Raw dataset
python -m bids_lite.cli plan --in ./input_data --meta ./metadata.csv --out ./bids_out --json ./plan.json

# Derivatives dataset
python -m bids_lite.cli plan --in ./derivative_data --meta ./metadata.csv --out ./bids_out \
    --dataset-type derivatives --pipeline-name lesion_analysis
```

**Output:**
- Prints first 5 planned operations to console
- Optionally saves full plan to JSON file for detailed review
- **Tip**: Use this to verify your setup before running `apply`, especially to check participant ID matching

### 3. Apply Command

Executes transformations and creates BIDS-compliant structure. This is the main command that performs the complete BIDS organization process.

**What it does:**
1. Validates input data
2. Creates transformation plan
3. Executes plan (copies or moves files)
4. Generates BIDS-compliant metadata files
5. Creates summary report

```bash
python -m bids_lite.cli apply --in <input_directory> --meta <metadata_file> --out <output_directory> [OPTIONS]
```

**Required Options:**
- `--in, --in_dir`: Input directory containing your image files
- `--meta, --meta_path`: Path to metadata file (CSV, TSV, or Excel)
- `--out, --out_dir`: Target BIDS output directory (will be created if it doesn't exist)

**Optional Options:**
- `--copy / --move`: Copy files (default, keeps originals) or move files. Default: `--copy` (safer)
- `--readme-template`: Optional custom README template file (.md or .txt) to use. If not provided, a default template will be used
- `--dataset-type`: Dataset type - `raw` (original scans) or `derivatives` (processed data). Default: `raw`
- `--pipeline-name`: Pipeline name for derivatives (e.g., `lesion_analysis`, `connectivity`). **Required** if `--dataset-type` is `derivatives`
- `--phenotype`: Additional data files (can specify multiple times, both raw and derivatives). Supports CSV, TSV, Excel, PDF, and other formats. Files copied to `phenotype/` (raw) or `derivatives/[pipeline]/phenotype/` (derivatives)
- `--publication`: Paper-related key files for derivatives (can specify multiple times, derivatives only). Supports images (NIfTI, PNG, JPG), data files (CSV, TSV, MAT, JSON), PDFs, and other formats. Files copied to `derivatives/publications/[pipeline_name]/`
- `--match-all-modalities / --match-specified-only`: 
  - `--match-all-modalities` (default): One metadata row matches all files for that participant/session. **Recommended** if one patient has multiple scan types (T1w, T2w, FLAIR, etc.)
  - `--match-specified-only`: Only match files with specified modality in metadata

**Examples:**

**Basic raw dataset:**
```bash
python -m bids_lite.cli apply --in ./input_data --meta ./metadata.csv --out ./bids_out
```

**Raw dataset with phenotype files:**
```bash
python -m bids_lite.cli apply --in ./input_data --meta ./metadata.csv --out ./bids_out \
    --phenotype ./additional_data1.csv \
    --phenotype ./additional_data2.xls \
    --phenotype ./supplementary_data.pdf
```

**Derivatives dataset:**
```bash
python -m bids_lite.cli apply --in ./derivative_data --meta ./metadata.csv --out ./bids_out \
    --dataset-type derivatives \
    --pipeline-name lesion_analysis
```

**Derivatives dataset with publication files:**
```bash
python -m bids_lite.cli apply --in ./derivative_data --meta ./metadata.csv --out ./bids_out \
    --dataset-type derivatives \
    --pipeline-name lesion_analysis \
    --publication ./circuit_results.nii.gz \
    --publication ./connectivity_matrix.csv \
    --publication ./key_figure.pdf
```

**Move files instead of copying:**
```bash
python -m bids_lite.cli apply --in ./input_data --meta ./metadata.csv --out ./bids_out --move
```

**Output:**
- Creates BIDS-compliant directory structure
- Copies/moves files to proper locations
- Generates `dataset_description.json`, `participants.tsv` (raw datasets), `README.md`, and `logs/report.md`
- Copies phenotype files to `phenotype/` (raw) or `derivatives/[pipeline]/phenotype/` (derivatives)
- Copies publication files to `derivatives/publications/[pipeline_name]/` (derivatives only)

---

## GUI Usage

### Platform Support

**Note on Platform Compatibility:**
- GUI tested on **macOS**; should work on **Windows** and **Linux** (tkinter is cross-platform)
- If you encounter GUI issues on Windows/Linux, use the **CLI** instead (fully cross-platform and feature-complete)
- We welcome feedback from Windows/Linux users!

### Launching the GUI

```bash
python ui/app.py
```

**Alternative (if the above doesn't work):**
```bash
python -m ui.app
```

### GUI Workflow

1. **Input Selection**
   - Click "Browse..." to select input directory
   - Click "Browse..." to select metadata file (CSV/TSV)
   - Click "Browse..." to select output directory

2. **Options Configuration**
   - **Dataset Type**: Choose `raw` or `derivatives`
   - **Pipeline Name**: Required for derivatives (e.g., `freesurfer`, `lesion_analysis`)
   - **Match All Modalities**: Check to match all files per participant/session
   - **Copy Files**: Check to copy (uncheck to move files)

3. **Additional Files** (Optional)
   - **Phenotype Files** (both raw and derivatives): Click "Add Phenotype File..." or drag and drop. Supports CSV, TSV, Excel, PDF, and other formats. Files copied to `phenotype/` (raw) or `derivatives/[pipeline]/phenotype/` (derivatives).
   - **Publication Files** (derivatives only): Available when dataset type is "derivatives". Click "Add Publication File..." or drag and drop. Supports images (NIfTI, PNG, JPG), data files (CSV, TSV, MAT, JSON), PDFs, and other formats. Files copied to `derivatives/publications/[pipeline_name]/`.

4. **Validation**
   - Click "Validate" button
   - Review validation issues in the text area
   - Fix any errors before proceeding

5. **Planning** (Dry-Run)
   - Click "Plan (Dry Run)" button
   - Review planned operations
   - Optionally save plan as JSON file

6. **Application**
   - Click "Apply" button to execute transformations
   - Review completion message with summary

### GUI Features

- Scrollable interface with scrollbar support
- Real-time validation with clear error/warning messages
- Visual file management with drag-and-drop support for phenotype and publication files
- Status updates showing current operation
- User-friendly error messages with troubleshooting tips
- Plan preview (dry-run mode) before applying transformations
- Supports various file formats for metadata, phenotype, and publication files

---

## Advanced Features

### 1. Derivatives Support

For processed/derivative data (e.g., lesion maps, connectivity matrices, analysis results):

**Key Differences from Raw Data:**
- `session_id` is optional (no default session folders if missing)
- One metadata row per participant (non-longitudinal)
- Modality auto-detected from filename (lesion, connectivity, etc.)
- Files stored in `derivatives/[pipeline_name]/` structure
- No `participants.tsv` file (derivatives typically don't have it)

**CLI Example:**
```bash
python -m bids_lite.cli apply --in ./derivative_data \
    --meta ./metadata.csv \
    --out ./bids_out \
    --dataset-type derivatives \
    --pipeline-name freesurfer
```

**Supported Derivative Filename Formats:**
- Simple author names: `Ahmed.nii.gz`, `Hirel.nii.gz`
- Author + year + case: `Ross1981-case2.nii.gz`, `Ross1981-case3.nii.gz`
- Complex formats: `Anhedonia_LesionTracing_Abdullah_2015_Case07_f.nii.gz`
- With update dates: `Insomnia_LesionTracing_Carecchio_2009_Case01_Updated_112523.nii.gz`

**Metadata for Derivatives:**
- Can provide just author name: `Abdullah`, `Biran`
- Or full ID: `Ross1981-case2`, `Abdullah2015Case07`
- Program automatically extracts author from complex filenames

### 2. Phenotype Files (Available for Both Raw and Derivatives)

Additional data files that don't match the main `participants.tsv` format (e.g., clinical data, demographics, questionnaires, or any supplementary information).

**Supported Formats:** CSV, TSV, Excel (.xls, .xlsx), PDF, and other file types

**CLI Example:**
```bash
# Raw dataset with phenotype files
python -m bids_lite.cli apply --in ./input_data \
    --meta ./metadata.csv \
    --out ./bids_out \
    --phenotype ./additional_data1.csv \
    --phenotype ./additional_data2.xls \
    --phenotype ./supplementary_data.pdf

# Derivatives dataset with phenotype files
python -m bids_lite.cli apply --in ./derivative_data \
    --meta ./metadata.csv \
    --out ./bids_out \
    --dataset-type derivatives \
    --pipeline-name lesion_analysis \
    --phenotype ./clinical_scores.csv
```

**Output Location:**
- Raw datasets: Files copied to `bids_out/phenotype/` folder
- Derivatives datasets: Files copied to `bids_out/derivatives/[pipeline_name]/phenotype/` folder

### 3. Publication Files (Derivatives Only)

Key files from published or to-be-published papers using the dataset (e.g., key results, circuit/connectivity analysis files, for reproducibility and comparison with future research).

**Supported Formats:** Images (`.nii`, `.nii.gz`, `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`), data files (`.csv`, `.tsv`, `.xls`, `.xlsx`, `.mat`, `.json`), PDFs, and other file types

**CLI Example:**
```bash
python -m bids_lite.cli apply --in ./derivative_data \
    --meta ./metadata.csv \
    --out ./bids_out \
    --dataset-type derivatives \
    --pipeline-name lesion_analysis \
    --publication ./circuit_results.nii.gz \
    --publication ./connectivity_matrix.csv \
    --publication ./key_figure.pdf
```

**Output Location:**
- Files copied to `bids_out/derivatives/publications/[pipeline_name]/` folder

### 4. Match All Modalities

By default, one metadata row matches all files for that participant/session.

**Example:**
If metadata has:
```csv
participant_id,session_id
001,01
```

And input directory has:
```
patient_001/
  T1w.nii.gz
  T2w.nii.gz
  FLAIR.nii.gz
```

All three files will be matched to participant `001` session `01`.

**To match only specified modality:**
```bash
python -m bids_lite.cli apply --in ./input_data --meta ./metadata.csv --out ./bids_out \
    --match-specified-only
```

Then include `modality` column in metadata:
```csv
participant_id,session_id,modality
001,01,T1w
001,01,T2w
```

---

## Output Structure

### Raw Dataset Structure

```
bids_out/
├── README.md
├── dataset_description.json
├── participants.tsv
├── phenotype/                    # Optional: additional data files
│   ├── additional_data1.csv
│   └── supplementary_data.pdf
└── sub-001/
    └── ses-01/
        └── anat/
            ├── sub-001_ses-01_T1w.nii.gz
            └── sub-001_ses-01_T2w.nii.gz
└── sub-002/
    └── ses-01/
        └── anat/
            └── sub-002_ses-01_FLAIR.nii.gz
└── logs/
    └── report.md
```

### Derivatives Dataset Structure

```
bids_out/
├── README.md
├── derivatives/
│   ├── [pipeline_name]/
│   │   ├── dataset_description.json
│   │   ├── README.md
│   │   ├── logs/
│   │   │   └── report.md
│   │   ├── sub-[participant_id]/
│   │   │   └── ses-01/              # Optional if no sessions
│   │   │       └── anat/            # or other modality folders
│   │   │           └── sub-[pid]_ses-01_lesion.nii.gz
│   │   └── publications/             # Optional: paper-related files
│   │       └── [pipeline_name]/
│   │           ├── circuit_results.nii.gz
│   │           ├── connectivity_matrix.csv
│   │           └── key_figure.pdf
```

---

## Examples

** Complete examples with full input and output are available in the [`examples/`](examples/) directory.**

### Quick Overview

| Example | Description | Location |
|---------|-------------|----------|
| **Example 1** | Basic Raw Dataset | [`examples/example1_basic_raw/`](examples/example1_basic_raw/) |
| **Example 2** | Raw with Phenotype Files | [`examples/example2_raw_with_phenotype/`](examples/example2_raw_with_phenotype/) |
| **Example 3** | Derivatives Dataset | [`examples/example3_derivatives/`](examples/example3_derivatives/) |
| **Example 4** | Derivatives with Publications | [`examples/example4_derivatives_with_publications/`](examples/example4_derivatives_with_publications/) |

 **[See All Examples →](examples/EXAMPLES.md)**

Each example includes:
- **Input data**: Sample files and metadata ready to use
- **Output results**: Complete BIDS-compliant output (already generated!)
- **README**: Detailed step-by-step explanation
- **Commands**: Copy-paste ready CLI commands

### Example 1: Basic Raw Dataset

**Location:** [`examples/example1_basic_raw/`](examples/example1_basic_raw/)

**Run it:**
```bash
python -m bids_lite.cli apply \
    --in examples/example1_basic_raw/input \
    --meta examples/example1_basic_raw/input/metadata.csv \
    --out examples/example1_basic_raw/output
```

**See complete results:** `examples/example1_basic_raw/output/`

### Example 2: Raw Dataset with Phenotype Files

**Location:** [`examples/example2_raw_with_phenotype/`](examples/example2_raw_with_phenotype/)

**Run it:**
```bash
python -m bids_lite.cli apply \
    --in examples/example2_raw_with_phenotype/input \
    --meta examples/example2_raw_with_phenotype/input/metadata.csv \
    --out examples/example2_raw_with_phenotype/output \
    --phenotype examples/example2_raw_with_phenotype/input/clinical_data.csv \
    --phenotype examples/example2_raw_with_phenotype/input/demographics.tsv
```

**See complete results:** `examples/example2_raw_with_phenotype/output/`

### Example 3: Derivatives Dataset

**Location:** [`examples/example3_derivatives/`](examples/example3_derivatives/)

**Run it:**
```bash
python -m bids_lite.cli apply \
    --in examples/example3_derivatives/input \
    --meta examples/example3_derivatives/input/metadata.csv \
    --out examples/example3_derivatives/output \
    --dataset-type derivatives \
    --pipeline-name lesion_analysis
```

**See complete results:** `examples/example3_derivatives/output/`

### Example 4: Derivatives with Publication Files

**Location:** [`examples/example4_derivatives_with_publications/`](examples/example4_derivatives_with_publications/)

**Run it:**
```bash
python -m bids_lite.cli apply \
    --in examples/example4_derivatives_with_publications/input \
    --meta examples/example4_derivatives_with_publications/input/metadata.csv \
    --out examples/example4_derivatives_with_publications/output \
    --dataset-type derivatives \
    --pipeline-name insomnia_lesion_tracing \
    --publication examples/example4_derivatives_with_publications/input/circuit_results.nii.gz \
    --publication examples/example4_derivatives_with_publications/input/connectivity_matrix.csv
```

**See complete results:** `examples/example4_derivatives_with_publications/output/`

---

## Common Questions & Troubleshooting

### Quick FAQ

**Q: What's the difference between "raw" and "derivatives" dataset types?**
- **Raw data**: Original imaging scans (T1w, T2w, FLAIR, bold, etc.) from scanners
- **Derivatives**: Processed/analyzed data (lesion maps, connectivity matrices, statistical maps, etc.)

**Q: Do I need to organize my input files in BIDS format?**
- **No!** The program accepts any file organization (one folder per patient, all files in one folder, mixed organization, any naming convention).

**Q: What if my participant IDs have special characters (spaces, dashes, underscores)?**
- The program automatically normalizes IDs (e.g., `Smith_2023-A` → `smithu2023ua`) - no need to change your filenames or metadata.

**Q: Why are `ses-01/` folders created even when I didn't provide `session_id`?**
- **For raw data**: BIDS requires sessions, so default `ses-01/` is used
- **For derivatives**: Sessions are optional - no `ses-XX/` folders if `session_id` is missing

**Q: My files aren't being matched. What should I check?**
1. Verify participant IDs in metadata match file/folder names (even with different formats)
2. Ensure files are in NIfTI format (`.nii` or `.nii.gz`)
3. Check that input directory path is correct
4. Run "Validate" first to see warnings

**Q: Can I use Excel files for metadata?**
- Yes! Supports `.xlsx` and `.xls` files (requires `openpyxl`: `pip install openpyxl`)

**Q: What happens if I have multiple CSV files?**
- Use the main CSV for `participants.tsv` (via `--meta`); use additional CSVs as phenotype files (via `--phenotype` multiple times) - they'll be copied to `phenotype/` folder

---

## Troubleshooting

### Common Issues

**1. Validation Errors**
- **Issue**: Missing `participant_id` column
- **Solution**: Ensure your metadata CSV has a `participant_id` column

**2. No Files Matched**
- **Issue**: Files not being matched to participants
- **Solution**: Verify participant IDs in metadata match those in filenames/folders, use `--match-all-modalities` flag (default), and ensure file extensions are `.nii` or `.nii.gz`

**3. Pipeline Name Required**
- **Issue**: Error when using derivatives without pipeline name
- **Solution**: Always specify `--pipeline-name` when using `--dataset-type derivatives`

**4. Special Characters in IDs**
- **Issue**: IDs with spaces, hyphens, or underscores
- **Solution**: Program automatically normalizes these (special chars → `u`) - no action needed

**5. Multiple Files Per Participant**
- **Issue**: Only one file per participant being processed
- **Solution**: Use `--match-all-modalities` flag (default) to match all files

### Getting Help

- Check validation output for specific error messages
- Review the `logs/report.md` file in output directory
- Use `--help` flag for command-specific help:
  ```bash
  python -m bids_lite.cli --help
  python -m bids_lite.cli apply --help
  ```

---

## Testing and Validation

We use a combination of automated tests, example-driven end-to-end runs, and cross-platform checks to validate the behavior of BIDS Lite Organizer.

- **Automated unit tests (CLI core)**
  - Core components (`checklist`, `normalizer`, `planner`, `validator`, `writer`) are covered by `pytest` tests in `bids_lite/tests/`.
  - Tests exercise both **raw** and **derivatives** workflows, including:
    - ID normalization and matching from messy filenames and folders
    - Session handling (default `ses-01` for raw vs. optional sessions for derivatives)
    - Correct BIDS paths in generated plans and write operations
  - Run locally with:
    ```bash
    pytest -q
    ```

- **End-to-end example runs**
  - The four example datasets in `examples/` are used as **regression tests**:
    - Example 1: basic raw data
    - Example 2: raw data + phenotype files
    - Example 3: derivatives dataset
    - Example 4: derivatives + publication files
  - For each example, we:
    - Run the `apply` command as documented in this README
    - Compare the produced BIDS structure (including logs and metadata) to the checked-in expected output
  - This validates that real-world-like datasets remain stable across code changes.

- **Cross-platform GUI and CLI checks**
  - A dedicated script (`scripts/test_gui_crossplatform.py`) verifies that the GUI module and Tkinter can be imported and initialized.
  - GitHub Actions workflows run these checks on **Windows**, **Linux**, and **macOS**, ensuring that:
    - The CLI entry points import and run without errors
    - The GUI root window can be created on all three platforms
  - Manual GUI testing has been performed on macOS; on Windows/Linux, the **CLI is the primary, fully tested interface**, while the GUI is expected to work and is further validated by CI.

**Summary of current status**

- Automated unit tests pass on supported Python versions (3.9+).
- All documented examples run end-to-end and reproduce the committed BIDS outputs.
- Cross-platform CI confirms that the CLI and GUI initialization work on macOS, Windows, and Linux for typical configurations.

---

## Challenges and Lessons Learned

During development, several non-trivial design and engineering challenges arose; addressing them shaped the current architecture.

- **Robust ID and filename normalization**
  - Real datasets include IDs such as `001`, `patient-001`, `Smith2023A`, and long lesion-tracing filenames.
  - We resolved this by centralizing normalization logic in the engine, writing tests for corner cases (e.g., author/year/case combinations), and ensuring consistent handling across validator, planner, and writer.

- **Session semantics for raw vs. derivatives**
  - BIDS requires sessions for raw data but treats them as optional for derivatives.
  - Early versions conflated these behaviors; tests now explicitly cover:
    - Automatically adding `ses-01` for raw datasets when `session_id` is missing
    - Avoiding session folders for derivatives when no `session_id` is provided
  - This is reflected in the planner tests and has significantly reduced user confusion.

- **Cross-platform GUI behavior**
  - GUI behavior differed across macOS, Windows, and Linux (Tkinter versions, drag-and-drop support, file dialog quirks).
  - We mitigated this by:
    - Keeping path handling and OS-sensitive logic minimal and centralized
    - Using Tkinter and `tkinterdnd2` in a conservative, cross-platform style
    - Adding automated cross-platform import/initialization tests and documenting known platform-specific considerations.

- **Reproducible testing without real PHI**
  - Because clinical neuroimaging data is sensitive, all tests and examples use **synthetic or de-identified toy data**.
  - File and metadata generators are designed to mimic real clinical workflows (raw scans, lesion maps, phenotype tables) while remaining fully shareable and reproducible.

These lessons directly informed the separation of concerns between validation, planning, and writing, and motivated the focus on example-driven documentation.

---

## Future Work

Several extensions are planned or under consideration to make BIDS Lite Organizer more powerful and easier to integrate into research pipelines:

- **Deeper BIDS validation**
  - Integrate with the official BIDS Validator or compatible tools for additional schema checks.
  - Provide structured validation reports (JSON/HTML) that can be archived with datasets.

- **Richer metadata and modality support**
  - Support more imaging modalities and derivative types out of the box.
  - Add smarter inference of modality and acquisition parameters from filenames and headers.

- **Enhanced provenance and logging**
  - Record transformation provenance (command-line arguments, versions, environment) in machine-readable form.
  - Offer optional, exportable reports for inclusion in methods sections of papers.

- **Packaging and deployment**
  - Publish as a Python package on PyPI and/or provide a Docker image for easier installation.
  - Explore a lightweight web-based interface for environments where installing a desktop GUI is difficult.

- **Broader neuromodulation datasets**
  - Generalize the organizer so that large TMS/DBS repositories and related hospital databases map cleanly into BIDS Lite.
  - Add richer phenotype and longitudinal data-cleaning utilities to handle complex clinical covariates.


Community feedback and real-world use cases—especially in clinical and translational settings—will guide which of these items are prioritized.

---

## Project Context

This repository was originally developed as part of **CS5001 (Intensive Foundations of Computer Science)** in the **MSCS Align program at Northeastern University**, with the core idea proposed and supported by **Dr. Michael Fox (Brigham and Women's Hospital, Center for Brain Circuit Therapeutics)**, supervised by **Dr. Michael Ferguson (Brigham and Women's Hospital, Center for Brain Circuit Therapeutics)**.

While it has an academic origin, the goal from the outset has been to create a **practical, research-grade tool** that can be used and extended by the broader neuroimaging and brain-circuit research communities. The project continues to evolve beyond the initial course, with attention to reproducibility, cross-platform support, and alignment with emerging BIDS practices.

---

## Code Repository

[GitHub Repository](https://github.com/Jessy-Ding/BIDS-Lite-Organizer)

## Testing Demo Videos

- [Testing Demo Recording](https://drive.google.com/file/d/1ZsIGa5PVcbSG2MzlgkI2EL5cr7LsVtJL/view?usp=drive_link)

---

## License

MIT License - see LICENSE file for details

---

## Acknowledgments

- **Idea and support**: Dr. Michael Fox, MD, PhD, Center for Brain Circuit Therapeutics (CBCT), Brigham and Women's Hospital (BWH)
- **Supervision**: Dr. Michael Ferguson, PhD, Neurospirituality Lab, CBCT, BWH
- **Course**: CS5001, Khoury College of Computer Sciences, Northeastern University, Oakland, CA
- **Course Faculty**: Prof. Almudena Konrad, PhD, Khoury College of Computer Sciences, Northeastern University, Oakland, CA
