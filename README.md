# ISEF Taylor-Cone Electrospray Solver

**Project:** Reduced-order axisymmetric electrostatic-capillary Taylor-cone solver for ISEF computational physics research.

---

## Repository Structure

```
isef/
├── solver/              # Core Python package and reproducible studies
│   ├── solver/          # Package modules (grid, operators, electrostatics,
│   │                    #   immersed boundary, interface, optimization)
│   ├── experimental/    # Imaging/extraction toolkit and synthetic round trip
│   ├── tests/           # 84 automated tests
│   └── examples/        # 12 demonstration scripts (00-10, 13)
├── app/                 # Streamlit interactive application
├── paper/               # ISEF paper (LaTeX)
│   └── paper_submission/
│       ├── sections/    # Paper sections
│       ├── figures/     # Generated figures
│       ├── data/        # Regenerated result tables
│       ├── main.tex     # Main LaTeX document
│       └── references.bib
├── experiments/         # Experimental design and methodology documents
│   ├── design/          # Validation plan
│   └── methodology/     # Procedure and generator scripts
├── results/             # Solver run outputs and experimental data drop-points
├── audit/               # Pre-registration and audit reports
├── archive/             # Historical drafts, superseded sections, notes
├── .scratch/            # Issue tracker (local markdown)
├── ACTIVE_FILES.md      # Index of the active submission set
├── README.md            # This file
├── CLAUDE.md            # Agent instructions
├── pyproject.toml       # Python package configuration (authoritative)
└── requirements.txt     # Pinned environment snapshot
```

---

## Quick Start

### Install Package
```bash
pip install -e ".[imaging,app]"    # optional extras: image pipeline, Streamlit app
```

The package can also be used without installing: `pyproject.toml` puts `solver/`
on the pytest path, and the app inserts it at startup. Running a script directly
needs `PYTHONPATH=solver`, as in:

```bash
PYTHONPATH=solver python solver/examples/10_quartic_poisson_convergence.py
```

### Run Tests
```bash
python -m pytest
```

### Run Example
```bash
PYTHONPATH=solver python solver/examples/07_immersed_free_boundary.py
```

### Run Streamlit App (Professional Interface)
```bash
streamlit run app/streamlit_app.py
```

**Features:**
- Multi-page architecture with Overview, Solver, Verification, Documentation
- Academic styling with professional plots (generous spacing)
- Parameter presets (Ethanol, Water, Formamide)
- Enhanced visualizations with 550-600px plot heights
- Comprehensive scientist user guide

**Legacy app** (original single-file version) preserved as:
```bash
streamlit run app/streamlit_app_legacy.py
```

See `app/README.md` for detailed app documentation.

### Compile Paper
```bash
cd paper/paper_submission
latexmk -pdf main.tex
```

---

## Current Status

**V3 Immersed Free-Boundary Milestone - Complete**

- 84 tests passing
- Immersed free-boundary cone solve, checked against a staircase baseline and a manufactured-solution convergence study
- Onset voltage projection implemented
- Taylor amplitude identity verified (ratio within 1% of unity)
- Taylor far-field BC recovers 49.14° and 49.20° at 61×89 and 121×177, versus 42.5°–46° for the grounded-box negative control
- Millimetre-scale onset voltage V0* ≈ 2.8–3.0 kV (ethanol literature range)
- Positive space-charge shielding metric (Gaussian S_E ≈ 1.3%)

**Track B (Physical Experiments)** - Gated on school approval

---

## Key Results

- **Immersed operator:** inter-level interface-potential change falls 10.33 → 4.26 → 2.55 V under refinement, where the staircase baseline does not (25.73 → 7.11 → 11.27 V)
- **Taylor identity:** amplitude balance ratio within 1% of unity (1.0005–1.0069)
- **Onset projection:** amplitude-projected residual has a minimum near the Taylor angle, but the minimising angle moves by several degrees as grid, cap radius and flank window change
- **Normal field reconstruction:** cubic-exact one-sided stencil built on fractional-distance immersed Dirichlet weights
- **Classical benchmark:** recovers the ideal 49.29° half-angle to within 0.16° across three refinement levels
- **Onset voltage:** ≈2.8–3.0 kV at millimetre scale, following V0* ∝ √(γL/ε₀)
- **Shielding:** positive apex-local S_E (~1.3%) for the Gaussian closure

---

## Documentation

- `paper/paper_submission/` - full ISEF paper with theory, numerical results and published-image validation
- `paper/paper_submission/README.md` - build instructions and figure/data provenance
- `ACTIVE_FILES.md` - index of the active submission set
- `archive/IMPLEMENTATION_STATUS.md` - detailed module status
- `archive/2026-09-10_project_cleanup/root-history/CONTEXT.md` - domain terminology and glossary
- `archive/old_docs/` - archived historical documents

---

## Citation

This is student research for ISEF. If you use this code, please cite appropriately and acknowledge the original Taylor (1964) theory.

---

## License

Open-source educational research project.
