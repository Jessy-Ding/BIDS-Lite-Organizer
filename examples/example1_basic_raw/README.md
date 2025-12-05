# Example 1: Basic Raw Dataset

This is the simplest example showing how to organize a basic raw neuroimaging dataset into BIDS format.

## Input Structure

```
input/
├── metadata.csv
├── patient_001/
│   ├── T1w_scan.nii.gz
│   ├── T2w_image.nii.gz
│   ├── bold.nii.gz              # Functional data
│   └── fMRI_rest.nii.gz         # Functional data
├── patient_002/
│   ├── FLAIR.nii.gz
│   └── functional_bold.nii.gz   # Functional data
└── patient_003/
    └── T1w.nii.gz
```

## Metadata

**File:** `input/metadata.csv`

```csv
participant_id
001
002
003
```

**Note:** Only `participant_id` is required! All other columns are optional.

## Command to Run

```bash
python -m bids_lite.cli apply \
    --in examples/example1_basic_raw/input \
    --meta examples/example1_basic_raw/input/metadata.csv \
    --out examples/example1_basic_raw/output
```

## Output Structure

After running the command, you'll get a BIDS-compliant structure:

```
output/
├── dataset_description.json
├── participants.tsv
├── README.md
├── logs/
│   └── report.md
├── sub-001/
│   └── ses-01/
│       ├── anat/                    # Anatomical data
│       │   ├── sub-001_ses-01_T1w.nii.gz
│       │   └── sub-001_ses-01_T2w.nii.gz
│       └── func/                    # Functional data
│           └── sub-001_ses-01_bold.nii.gz
├── sub-002/
│   └── ses-01/
│       ├── anat/
│       │   └── sub-002_ses-01_FLAIR.nii.gz
│       └── func/
│           └── sub-002_ses-01_bold.nii.gz
└── sub-003/
    └── ses-01/
        └── anat/
            └── sub-003_ses-01_T1w.nii.gz
```

## Key Points

- -  **Minimal metadata**: Only `participant_id` required
- -  **Flexible input**: Files can be in any folder structure
- -  **Auto-detection**: Modality (T1w, T2w, FLAIR, bold) detected from filename
- -  **Multiple data types**: Supports both anatomical (`anat/`) and functional (`func/`) data
- -  **BIDS-compliant**: Output follows BIDS standard structure
- -  **Default session**: Missing `session_id` defaults to `01` (BIDS requirement)

## Why Session Folders Are Created

**Question:** "I didn't provide `session_id` in metadata or filenames. Why are `ses-01/` folders created?"

**Answer:** 
- **BIDS standard requires sessions for raw data**
- Even if you don't provide `session_id`, the program uses default `"01"` to ensure BIDS compliance
- This is correct behavior - think of it as "one session per participant"
- For derivatives, sessions are optional (see Example 3)

See [`SESSION_HANDLING.md`](../../SESSION_HANDLING.md) for detailed explanation.

## What Happened?

1. The program found files in `patient_001/`, `patient_002/`, and `patient_003/` folders
2. It matched participant IDs (`001`, `002`, `003`) from folder names
3. It detected modalities from filenames:
   - **Anatomical**: T1w, T2w, FLAIR → organized into `anat/` folder
   - **Functional**: bold, fMRI → organized into `func/` folder
4. It organized files into BIDS structure: `sub-XXX/ses-XX/[anat|func]/`
5. It generated BIDS metadata files (`dataset_description.json`, `participants.tsv`)

## Supported Data Types

This example demonstrates:
- **Anatomical data** (`anat/`): T1w, T2w, FLAIR
- **Functional data** (`func/`): bold, fMRI

The program automatically detects the data type from the filename and organizes files into the correct BIDS folder structure.

