# Project Structure

This document explains the organization of the BIDS Lite Organizer project.

## Directory Structure

```
Project_BIDS-Lite/
├── bids_lite/                    # Main package
│   ├── cli.py                    # Command-line interface
│   ├── engine/                   # Core engine modules
│   │   ├── checklist.py         # BIDS specification
│   │   ├── normalizer.py        # ID normalization
│   │   ├── planner.py           # Transformation planning
│   │   ├── validator.py         # Input validation
│   │   └── writer.py            # BIDS file writing
│   └── tests/                  # Unit tests
│
├── ui/                          # GUI application (cross-platform)
│   └── app.py                   # Tkinter GUI
│
├── scripts/                      # Development and testing scripts
│   └── test_all_platforms.py     # Cross-platform test for GUI and CLI (used by CI)
│
├── examples/                     # Complete examples (START HERE!)
│   ├── EXAMPLES.md              # Examples overview
│   ├── example1_basic_raw/      # Example 1: Basic raw dataset
│   │   ├── README.md            # Example documentation
│   │   ├── input/               # Input data
│   │   │   ├── metadata.csv
│   │   │   └── patient_XXX/
│   │   └── output/              # Complete BIDS output (already generated!)
│   │       ├── dataset_description.json
│   │       ├── participants.tsv
│   │       └── sub-XXX/
│   │
│   ├── example2_raw_with_phenotype/  # Example 2: Raw + phenotype files
│   │   ├── README.md
│   │   ├── input/
│   │   └── output/
│   │
│   ├── example3_derivatives/    # Example 3: Derivatives dataset
│   │   ├── README.md
│   │   ├── input/
│   │   └── output/
│   │
│   └── example4_derivatives_with_publications/  # Example 4: Derivatives + publications
│       ├── README.md
│       ├── input/
│       └── output/
│
├── README.md                     # Main documentation (START HERE!)
├── PROJECT_STRUCTURE.md          # This file
├── requirements.txt              # Python dependencies
├── run_gui.py                    # GUI launcher (cross-platform)
└── LICENSE                       # MIT License
```

## Key Directories

### `bids_lite/`
The core package containing all the BIDS organization logic.

- **`cli.py`**: Command-line interface using Click
- **`engine/`**: Core processing modules
  - `checklist.py`: BIDS specification definitions
  - `normalizer.py`: Participant/session ID normalization
  - `planner.py`: File matching and transformation planning
  - `validator.py`: Input validation
  - `writer.py`: BIDS file writing and organization

### `ui/`
Cross-platform graphical user interface built with tkinter. Works on Windows, macOS, and Linux.

- **`app.py`**: Tkinter-based GUI application

### Root Directory Files

- **`run_gui.py`**: Cross-platform GUI launcher script. Run with `python run_gui.py` or `python3 run_gui.py`
- **`README.md`**: Main documentation and user guide
- **`requirements.txt`**: Python package dependencies
- **`LICENSE`**: MIT License

### `examples/`
**This is where you should start!** Complete, runnable examples with:
- Input data (sample files and metadata)
- Output results (complete BIDS structure, already generated)
- README documentation for each example
- Ready-to-run commands

Each example demonstrates different features:
1. **example1_basic_raw**: Simplest case - basic raw dataset
2. **example2_raw_with_phenotype**: Raw dataset with additional data files
3. **example3_derivatives**: Processed/derivative data
4. **example4_derivatives_with_publications**: Derivatives with paper-related files

## Getting Started

1. **Read the main README**: [`README.md`](README.md)
2. **Try the examples**: [`examples/EXAMPLES.md`](examples/EXAMPLES.md)
3. **Run an example**: Pick any example and follow its README
4. **Use with your data**: Adapt the examples to your own data

## File Organization Philosophy

- **Clear separation**: Code, examples, and documentation are clearly separated
- **Self-contained examples**: Each example has everything needed to run
- **Complete outputs**: All examples include pre-generated output so you can see results immediately
- **Documentation first**: Each example has detailed README explaining what happens

## For Contributors

- **Code**: `bids_lite/` and `ui/`
- **Tests**: `bids_lite/tests/`
- **Examples**: `examples/` (keep these updated when adding features)
- **Documentation**: `README.md`, `PROJECT_STRUCTURE.md`, and example READMEs

## For Users

- **Start here**: [`examples/EXAMPLES.md`](examples/EXAMPLES.md)
- **Pick an example**: Choose the one closest to your use case
- **Run it**: Follow the commands in the example's README
- **Check output**: See the complete BIDS structure in `output/` directory
- **Adapt**: Use the example as a template for your data

