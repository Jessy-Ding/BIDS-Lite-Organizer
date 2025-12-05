# Example 4: Derivatives Dataset with Publication Files

This example shows how to include paper-related key files (publication files) with a derivatives dataset.

## Input Structure

```
input/
├── metadata.csv
├── circuit_results.nii.gz              # Publication file
├── connectivity_matrix.csv              # Publication file
├── Insomnia_LesionTracing_Carecchio_2009_Case01.nii.gz
└── Insomnia_LesionTracing_Biran_2003_Case04.nii.gz
```

## Metadata

**File:** `input/metadata.csv`

```csv
participant_id
Carecchio
Biran
```

**Publication Files:**
- `circuit_results.nii.gz`: Key circuit analysis results
- `connectivity_matrix.csv`: Connectivity matrix data

## Command to Run

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

## Output Structure

```
output/
├── derivatives/
│   └── insomnia_lesion_tracing/
│       ├── dataset_description.json
│       ├── participants.tsv
│       ├── README.md
│       ├── logs/
│       │   └── report.md
│       ├── publications/                        # Publication files folder
│       │   └── insomnia_lesion_tracing/
│       │       ├── circuit_results.nii.gz
│       │       └── connectivity_matrix.csv
│       ├── sub-carecchio/
│       │   └── anat/                    <- No ses-XX folder!
│       │       └── sub-carecchio_lesion.nii.gz  <- No ses-XX in filename!
│       └── sub-biran/
│           └── anat/
│               └── sub-biran_lesion.nii.gz
```

## Key Points

- -  **Publication files**: Key paper-related files stored in `derivatives/publications/[pipeline_name]/`
- -  **Multiple formats**: Supports images (NIfTI, PNG, JPG), data files (CSV, TSV, MAT, JSON), PDFs
- -  **Easy access**: Other researchers can easily find and use these files for comparison
- -  **Reproducibility**: Preserves original author results for future research
- -  **No session folders**: Since metadata has no `session_id`, no `ses-XX/` folders are created (correct for derivatives)

## Why No Session Folders?

**Question:** "Why are there no `ses-XX/` folders in the output?"

**Answer:**
- **Sessions are optional for derivatives** (unlike raw data)
- Since metadata has no `session_id` column, no session folders are created
- Output structure: `derivatives/pipeline_name/sub-XXX/anat/` (no `ses-XX/`)
- Filenames: `sub-XXX_lesion.nii.gz` (no `ses-XX` in filename)
- This is correct BIDS behavior for derivatives without sessions

**Compare with raw data:** Raw data always creates `ses-01/` folders (BIDS requirement), but derivatives can omit sessions.

See [`BIDS_CONCEPTS.md`](../../BIDS_CONCEPTS.md) for explanation of what a "session" means in BIDS.

## What Happened?

1. Image files were organized into BIDS derivatives structure
2. Publication files were copied to `derivatives/publications/[pipeline_name]/` folder
3. All files preserved their original names and formats
4. BIDS metadata files were generated

## Use Cases for Publication Files

- **Key results from published papers**: Store important findings
- **Circuit/connectivity analysis**: Share analysis results
- **Comparison data**: Enable comparison with future research
- **Reproducibility**: Preserve original author results
- **Supplementary materials**: Any files related to published work

## Supported Publication File Formats

- **Image files**: `.nii`, `.nii.gz`, `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`
- **Data files**: `.csv`, `.tsv`, `.xls`, `.xlsx`, `.mat`, `.json`
- **PDF files**: `.pdf`
- **Other files**: Any file type you want to include

