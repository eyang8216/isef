# ISEF Taylor-Cone Electrospray Solver

**Project:** Reduced-order axisymmetric electrostatic-capillary Taylor-cone solver for ISEF computational physics research.

---

## Repository Structure

```
isef/
├── backend/              # Solver implementation (Python package)
│   ├── solver/          # Core modules (grid, operators, electrostatics, immersed boundary, optimization)
│   ├── tests/           # 71 automated tests
│   ├── examples/        # 10 demonstration scripts (00-09)
│   └── app/             # Streamlit interactive application
├── paper_submission/     # ISEF paper (LaTeX)
│   ├── sections/        # Paper sections
│   ├── main.tex         # Main LaTeX document
│   └── main.pdf         # Compiled paper
├── archive/             # Historical docs and notes
├── README.md            # This file
├── CONTEXT.md           # Domain glossary
├── CLAUDE.md            # Agent instructions
├── pyproject.toml       # Python package configuration
└── requirements.txt     # Dependencies
```

---

## Quick Start

### Install Package
```bash
pip install -e .
```

### Run Tests
```bash
python -m pytest backend/tests/
```

### Run Example
```bash
python backend/examples/07_immersed_free_boundary.py
```

### Run Streamlit App (New Professional Interface)
```bash
streamlit run backend/app/streamlit_app.py
```

**New in v2.0:**
- Multi-page architecture with Overview, Solver, Verification, Documentation
- Academic styling with professional plots (generous spacing)
- Parameter presets (Ethanol, Water, Formamide)
- Enhanced visualizations with 550-600px plot heights
- Comprehensive scientist user guide

**Legacy app** (original single-file version) preserved as:
```bash
streamlit run backend/app/streamlit_app_legacy.py
```

See `backend/app/README.md` for detailed app documentation.

### Compile Paper
```bash
cd paper_submission
tectonic main.tex
```

---

## Current Status

**V3 Immersed Free-Boundary Milestone - Complete**

- 71 tests passing
- Second-order convergent immersed boundary method
- Onset voltage projection implemented
- Taylor amplitude identity verified (ratio within 3% of unity)
- Taylor far-field BC recovers ~48° half-angle (vs ~44° grounded-box artifact)
- Millimeter-scale onset voltage V0* ≈ 2.8 kV (ethanol literature range)
- Positive space-charge shielding metric (Gaussian S_E ≈ 1.3%)
- Paper updated with V4 results

**Track B (Physical Experiments)** - Gated on school approval

---

## Key Results

- **Immersed operator:** Second-order convergence proven via Richardson extrapolation
- **Taylor identity:** Amplitude balance ratio within 3% of unity
- **Onset projection:** Clean V-shaped optimization landscape
- **Normal field reconstruction:** Cubic-exact stencil, ≤1% error on refined grids
- **Classical benchmark:** Recovers Taylor's 49.29° half-angle to within ~1.3° (Taylor far-field BC)
- **Onset voltage:** ~2.8 kV at millimeter scale, following V0* ∝ √(γL/ε₀)
- **Shielding:** Positive apex-local S_E (~1.3%) for the Gaussian closure

---

## Documentation

- `CONTEXT.md` - Domain terminology and glossary
- `paper_submission/` - Full ISEF paper with theory, validation, and planned experiments
- `archive/AI_HANDOVER.md` - Complete project history and handover notes
- `archive/IMPLEMENTATION_STATUS.md` - Detailed module status

---

## Citation

This is student research for ISEF. If you use this code, please cite appropriately and acknowledge the original Taylor (1964) theory.

---

## License

Open-source educational research project.
