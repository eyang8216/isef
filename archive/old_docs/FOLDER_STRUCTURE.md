# ISEF Project Folder Structure

## Overview

The project is now organized into 4 main directories:

```
isef/
├── paper/                          # ISEF paper submission
├── solver/                         # Taylor cone solver code
├── data/                          # Generated data and results
├── experimental_methodology/      # Complete experimental procedures
├── figures/                       # Publication-quality figures
└── archive/                       # Archived materials
```

## Directory Details

### 📄 `paper/` - ISEF Paper Submission
- `paper_submission/` - Complete LaTeX project
  - `main.pdf` (311 KB) - Compiled paper
  - `main.tex` - Main LaTeX file
  - `sections/` - All paper sections
  - `figures/` - Figures included in paper
  - `data/` - Data tables
- `PAPER_COMPLETE_STATUS.md` - Comprehensive status document
- `PAPER_IMPROVEMENTS_COMPLETE.md` - Detailed improvement log

**Paper Statistics:**
- 19+ pages
- 12 main sections + 2 appendices
- 5 publication-quality figures
- Ready for Hong Kong ISEF selection submission

### 💻 `solver/` - Taylor Cone Solver
- `backend/` - Complete Python implementation
  - `solver/` - Core solver modules
  - `experimental/` - Experimental validation tools
  - `app/` - Interactive Streamlit application
  - `examples/` - Example workflows
  - `tests/` - Automated test suite (74 tests)

**Key Features:**
- O(N^2.3) computational complexity
- 130× faster than COMSOL (13s vs 30min)
- Second-order accurate (p = 2.01 ± 0.03)
- Consumer-hardware optimized

### 📊 `data/` - Generated Data
- `synthetic_validation_results.txt` - Image processing validation
- `timing_results.txt` - Performance benchmarks
- Experimental data (TBD - placeholders in paper Section 9)

**Current Data:**
- Synthetic validation: ±0.5° accuracy across 4 SNR levels
- Timing: 7 grid resolutions from 25×27 to 241×353
- Grid convergence: 3 refinement levels

### 🔬 `experimental_methodology/` - Experimental Procedures
- `experimental_procedure.pdf` (83 KB) - Compiled manual
- `experimental_procedure.tex` - LaTeX source
- `EXPERIMENTAL_APPARATUS_AND_PROCEDURE.md` (41 pages) - Markdown version
- `generate_synthetic_validation.py` - Validation data generator
- `generate_convergence_plot.py` - Convergence plot generator
- `generate_timing_data.py` - Performance benchmark tool
- `generate_figures.py` - Figure generation master script

**Documentation Includes:**
- Complete equipment list (3 budget tiers: $1.5K-$9K)
- Hong Kong supplier information
- Detailed safety protocols
- Step-by-step setup procedure
- Emergency procedures
- Pre-experiment checklist
- Troubleshooting guide

### 🎨 `figures/` - Publication Figures
All at 300 DPI in PDF + PNG formats:
- `system_schematic` - Physical setup diagram
- `solver_flowchart` - Computational pipeline
- `exponent_crossing` - **Novel observable** (key contribution)
- `poisson_convergence` - Grid convergence plot

### 🗄️ `archive/` - Archived Materials
- HTML lesson files (not part of ISEF project)
- Old documentation
- Scratch work

## Quick Navigation

### To compile the paper:
```bash
cd paper/paper_submission
tectonic main.tex
```

### To run the solver:
```bash
cd solver/backend
source ../../.venv/bin/activate
python examples/01_basic_taylor_cone.py
```

### To generate validation data:
```bash
cd experimental_methodology
source ../.venv/bin/activate
python generate_synthetic_validation.py
```

### To view experimental procedures:
```bash
open experimental_methodology/experimental_procedure.pdf
```

## File Counts

- **Paper files:** 20+ LaTeX sections
- **Solver files:** 50+ Python modules
- **Test files:** 74 automated tests
- **Documentation:** 100+ pages total
- **Figures:** 4 publication-quality + previews

## Git Status

All improvements committed and pushed to GitHub:
- Commit: `4ba20a7`
- Branch: `main`
- Remote: `github.com/eyang8216/isef`

## Next Steps

1. **For paper submission:**
   - Review `paper/paper_submission/main.pdf`
   - Fill TBD values in Section 9 after experiments
   - Submit to Hong Kong ISEF selection

2. **For experiments:**
   - Review `experimental_methodology/experimental_procedure.pdf`
   - Obtain institutional safety approval
   - Purchase equipment (budget options available)
   - Follow step-by-step protocols

3. **For solver development:**
   - Run test suite: `pytest solver/backend/tests/`
   - Explore examples: `solver/backend/examples/`
   - Modify solver: `solver/backend/solver/`

## Authors

- Ethan Yang
- Elliot Dong
- Curtis Lau

Independent Schools Foundation Academy, Hong Kong SAR

---

**Last updated:** August 21, 2026
**Total project size:** ~500 MB (including venv)
**Documentation:** Complete and submission-ready
