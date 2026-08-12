# Paper Updates for V3 Immersed Boundary Milestone

**Date:** 2026-08-12  
**Status:** LaTeX source updated, PDF compilation blocked by missing `siunitx` package in VM

---

## What Was Updated

### 1. Abstract (sections/00_abstract.tex)
**Added:**
- "cubic-exact immersed boundary stencil"
- "onset voltage projection"
- Second-order convergence verification
- Taylor amplitude identity ratio 1.009
- Grounded-box optimization: ~44° half-angle, V0* ≈ 28.9 kV
- Updated test count: "58-test automated suite"

### 2. Solver Architecture (sections/05_solver_architecture.tex)
**Added modules:**
- `geometry.py` — ImplicitCone with C1 rounded cap-flank geometry
- `immersed.py` — Fractional-distance immersed Dirichlet stencils
- `verification.py` — Immersed verification workflows

**Updated pipeline:**
- Added "immersed boundary representation" option
- Added "immersed Dirichlet stencils" 
- Added "ImplicitCone geometry" for candidate interface
- Added "immersed E_n reconstruction"
- Added "project out onset voltage V0*"

**Updated app description:**
- Now has two tabs: Classic and Immersed verification
- Demonstrates grounded-box optimization and imposed-Taylor identity

### 3. Numerical Validation (sections/06_numerical_validation.tex)
**Updated test count:**
- From "33 passed" → "58 passed in 45 seconds"

**Added entire new section: Immersed Boundary Method (V3 Milestone)**

#### Second-Order Convergence
- Richardson extrapolation on smooth manufactured problem
- Measured L2 order ≈ 2.0 over three refinement levels
- Replaces non-convergent staircase representation

#### Onset Voltage Projection
- Projects out balance voltage V0* per candidate shape
- Formula: u* = ⟨ab⟩_w / ⟨b²⟩_w, V0* = √(2u*/ε₀)
- Eliminates fixed-voltage degeneracy

#### Grounded-Box Free Boundary
- Converges to ~44° half-angle
- V0* ≈ 28.9 kV for meter-scale geometry
- Clean V-shaped landscape with interior minimum

#### Imposed-Taylor Identity Verification
- Taylor amplitude identity: ½ε₀V₀² = ∫ γκ dA
- Measured ratio: 1.009 (within 1% of unity)
- Argmin at 50.0° (~0.7° from ideal 49.29°)
- Systematic offset stable under refinement
- Attributed to cap-flank geometry and discretization floor

#### Normal-Field Reconstruction
- Cubic-exact one-sided stencil
- Formula: E_n = −(−11V_b + 18V(d) − 9V(2d) + 2V(3d))/(6d)
- Accuracy ≤ 1% on refined grids

**Removed:**
- Old "Known Optimizer Limitation" section about 43.5° angle

---

## Still Needs Compilation

The LaTeX source files are updated but the PDF cannot be compiled in this VM due to missing `texlive-latex-extra` package (specifically `siunitx.sty`).

**To compile on your Mac:**

```bash
cd /Users/a3015110/Desktop/isef/paper_submission
tectonic main.tex
```

Or if tectonic is not installed:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

The old PDF from August 6th is saved as `paper_OLD_Aug6.pdf` for comparison.

---

## Next Steps for Paper

1. **Compile the updated LaTeX** on your local machine to see the full document
2. **Add figures** showing:
   - Immersed boundary convergence plot
   - Grounded-box V-shaped landscape
   - Imposed-Taylor identity verification
   - Example cone geometry with refined grid
3. **Review experimental methodology section** for any needed updates
4. **Add author/school information** when ready for submission
5. **Generate actual result figures** from the examples (07, 08, 09)

---

## Repository Cleanup Status

The repository cleanup (frontend/backend separation) was started but paused due to git lock file. Once you review the paper, I can complete the restructuring:

- **Backend:** solver/, tests/, examples/, app/, docs/, scripts/, results/, .scratch/
- **Frontend:** paper_submission/ (papers and presentation materials)
- **Root:** Keep README.md, CONTEXT.md, pyproject.toml, requirements.txt, .gitignore
