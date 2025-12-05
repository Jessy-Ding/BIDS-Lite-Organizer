# Example 2: Raw Dataset with Phenotype Files

This example shows how to include additional data files (phenotype files) with a raw dataset.

## Input Structure

```
input/
├── metadata.csv
├── clinical_data.csv          # Additional phenotype file
├── demographics.tsv            # Additional phenotype file
├── patient_001/
│   └── T1w.nii.gz
└── patient_002/
    └── T1w.nii.gz
```

## Metadata

**File:** `input/metadata.csv`

```csv
participant_id,session_id,age,sex
001,01,30,M
002,01,25,F
```

**Phenotype Files:**
- `clinical_data.csv`: Additional clinical information
- `demographics.tsv`: Demographics data

## Command to Run

```bash
python -m bids_lite.cli apply \
    --in examples/example2_raw_with_phenotype/input \
    --meta examples/example2_raw_with_phenotype/input/metadata.csv \
    --out examples/example2_raw_with_phenotype/output \
    --phenotype examples/example2_raw_with_phenotype/input/clinical_data.csv \
    --phenotype examples/example2_raw_with_phenotype/input/demographics.tsv
```

## Output Structure

```
output/
├── dataset_description.json
├── participants.tsv
├── README.md
├── logs/
│   └── report.md
├── phenotype/                          # Phenotype files folder
│   ├── clinical_data.csv
│   └── demographics.tsv
├── sub-001/
│   └── ses-01/
│       └── anat/
│           └── sub-001_ses-01_T1w.nii.gz
└── sub-002/
    └── ses-01/
        └── anat/
            └── sub-002_ses-01_T1w.nii.gz
```

## Key Points

- -  **Phenotype files**: Additional data files stored in `phenotype/` folder
- -  **Multiple formats**: Supports CSV, TSV, XLS, XLSX, PDF, and more
- -  **Optional columns**: `session_id`, `age`, `sex` are optional
- -  **BIDS standard**: Phenotype folder is part of BIDS specification

## What Happened?

1. Image files were organized into BIDS structure
2. Phenotype files were copied to `phenotype/` folder
3. All files preserved their original names and formats
4. BIDS metadata files were generated

## Use Cases for Phenotype Files

- Clinical data that doesn't fit `participants.tsv` format
- Supplementary demographic information
- Additional behavioral or cognitive data
- Any other data files you want to include with your dataset

