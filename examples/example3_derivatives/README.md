# Example 3: Derivatives Dataset

This example shows how to organize processed/derivative data (e.g., lesion maps, analysis results) into BIDS derivatives format.

## Input Structure

```
input/
├── metadata.csv
├── Ahmed.nii.gz
├── Anhedonia_LesionTracing_Abdullah_2015_Case07_f.nii.gz
├── Ross1981-case2.nii.gz
└── Ross1981-case3.nii.gz
```

## Metadata

**File:** `input/metadata.csv`

```csv
participant_id
Ahmed
Abdullah
Ross1981-case2
Ross1981-case3
```

**Note:** 
- For derivatives, you can provide just author names (e.g., `Abdullah`)
- Or full IDs (e.g., `Ross1981-case2`)
- The program automatically extracts author names from complex filenames
- `session_id` is optional - if missing, no session folders are created

## Command to Run

```bash
python -m bids_lite.cli apply \
    --in examples/example3_derivatives/input \
    --meta examples/example3_derivatives/input/metadata.csv \
    --out examples/example3_derivatives/output \
    --dataset-type derivatives \
    --pipeline-name lesion_analysis
```

## Output Structure

```
output/
├── derivatives/
│   └── lesion_analysis/
│       ├── dataset_description.json
│       ├── participants.tsv
│       ├── README.md
│       ├── logs/
│       │   └── report.md
│       ├── sub-ahmed/
│       │   └── anat/                    <- No ses-XX folder!
│       │       └── sub-ahmed_lesion.nii.gz  <- No ses-XX in filename!
│       ├── sub-abdullah/
│       │   └── anat/
│       │       └── sub-abdullah_lesion.nii.gz
│       ├── sub-ross1981ucase2/
│       │   └── anat/
│       │       └── sub-ross1981ucase2_lesion.nii.gz
│       └── sub-ross1981ucase3/
│           └── anat/
│               └── sub-ross1981ucase3_lesion.nii.gz
```

**Note:** Since metadata has no `session_id` column, no `ses-XX/` folders are created. This is correct BIDS behavior for derivatives without sessions.

## Key Points

- -  **Derivatives structure**: Files stored in `derivatives/[pipeline_name]/`
- -  **Pipeline name required**: Must specify `--pipeline-name` for derivatives
- -  **Flexible IDs**: Supports simple names (`Ahmed`) and complex IDs (`Ross1981-case2`)
- -  **Auto-modality detection**: Detects lesion, connectivity, etc. from filename
- -  **participants.tsv**: Generated in `derivatives/[pipeline_name]/` directory with participant metadata
- -  **Special character handling**: `-`, `_`, spaces normalized to `u` in participant IDs
- -  **No session folders**: Since metadata has no `session_id`, no `ses-XX/` folders are created

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

1. Files with messy names were matched to participant IDs in metadata
2. Author names were extracted from complex filenames (e.g., `Abdullah` from `Anhedonia_LesionTracing_Abdullah_2015_Case07_f.nii.gz`)
3. Special characters in IDs were normalized (`Ross1981-case2` → `ross1981ucase2`)
4. Files organized into `derivatives/[pipeline_name]/sub-XXX/anat/` structure (no `ses-XX/` since no session_id)
5. Modality detected from filename (lesion, connectivity, etc.)

## Supported Derivative Filename Formats

- Simple author names: `Ahmed.nii.gz`, `Hirel.nii.gz`
- Author + year + case: `Ross1981-case2.nii.gz`, `Ross1981-case3.nii.gz`
- Complex formats: `Anhedonia_LesionTracing_Abdullah_2015_Case07_f.nii.gz`
- With update dates: `Insomnia_LesionTracing_Carecchio_2009_Case01_Updated_112523.nii.gz`

The program handles all these formats automatically!

