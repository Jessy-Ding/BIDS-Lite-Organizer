# BIDS Lite Organizer - Examples

This directory contains complete, runnable examples demonstrating all features of BIDS Lite Organizer.

## Quick Start

Each example includes:
- -  **Input data**: Sample files and metadata
- -  **Output results**: Complete BIDS-compliant output
- -  **README**: Detailed explanation
- -  **Commands**: Ready-to-run CLI commands

## Example Overview

### [Example 1: Basic Raw Dataset](example1_basic_raw/)
**The simplest example** - Organize a basic raw neuroimaging dataset.

- Minimal metadata (only `participant_id` required)
- Flexible input structure
- Auto-detection of modalities
- Perfect for beginners

**Run it:**
```bash
python -m bids_lite.cli apply \
    --in examples/example1_basic_raw/input \
    --meta examples/example1_basic_raw/input/metadata.csv \
    --out examples/example1_basic_raw/output
```

**See results:** `examples/example1_basic_raw/output/`

---

### [Example 2: Raw Dataset with Phenotype Files](example2_raw_with_phenotype/)
**Include additional data files** with your raw dataset.

- Phenotype files (CSV, TSV, XLS, PDF)
- Additional clinical/demographic data
- BIDS-compliant `phenotype/` folder

**Run it:**
```bash
python -m bids_lite.cli apply \
    --in examples/example2_raw_with_phenotype/input \
    --meta examples/example2_raw_with_phenotype/input/metadata.csv \
    --out examples/example2_raw_with_phenotype/output \
    --phenotype examples/example2_raw_with_phenotype/input/clinical_data.csv \
    --phenotype examples/example2_raw_with_phenotype/input/demographics.tsv
```

**See results:** `examples/example2_raw_with_phenotype/output/`

---

### [Example 3: Derivatives Dataset](example3_derivatives/)
**Organize processed/derivative data** (lesion maps, analysis results).

- Derivatives structure (`derivatives/[pipeline_name]/`)
- Flexible participant IDs (author names, case IDs)
- Auto-extraction from complex filenames
- Handles messy real-world filenames

**Run it:**
```bash
python -m bids_lite.cli apply \
    --in examples/example3_derivatives/input \
    --meta examples/example3_derivatives/input/metadata.csv \
    --out examples/example3_derivatives/output \
    --dataset-type derivatives \
    --pipeline-name lesion_analysis
```

**See results:** `examples/example3_derivatives/output/`

---

### [Example 4: Derivatives with Publication Files](example4_derivatives_with_publications/)
**Include paper-related key files** with derivatives dataset.

- Publication files (circuit results, connectivity data, key figures)
- Stored in `derivatives/publications/[pipeline_name]/`
- Easy access for other researchers
- Supports multiple file formats

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

**See results:** `examples/example4_derivatives_with_publications/output/`

---

## How to Use These Examples

### 1. Explore the Input

Each example has an `input/` directory showing:
- How to organize your data (any format works!)
- What metadata looks like (minimal requirements)
- Example filenames and structures

### 2. Run the Example

Copy the command from the example's README and run it in your terminal.

### 3. Check the Output

Each example has an `output/` directory with complete BIDS-compliant results:
- BIDS directory structure
- Generated metadata files
- Organized image files
- Logs and reports

### 4. Compare with Your Data

Use these examples as templates for your own data organization.

---

## Example Comparison

| Feature | Example 1 | Example 2 | Example 3 | Example 4 |
|---------|-----------|-----------|-----------|-----------|
| Dataset Type | Raw | Raw | Derivatives | Derivatives |
| Metadata | Minimal | With optional columns | Author names | Author names |
| Phenotype Files | No | -  | No | No |
| Publication Files | No | No | No | -  |
| Complexity |  Simple |  Medium |  Advanced |  Advanced |

---

## Next Steps

1. **Start with Example 1** if you're new to BIDS Lite Organizer
2. **Try Example 2** if you have additional data files
3. **Use Example 3** if you're working with processed/derivative data
4. **Check Example 4** if you want to include publication files

Each example is self-contained and can be run independently!

---

## Need Help?

- See the main [README.md](../README.md) for detailed documentation
- Check each example's README for specific details
- Review the output structure to understand BIDS organization

