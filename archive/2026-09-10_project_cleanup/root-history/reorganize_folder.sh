#!/bin/bash

# Create main organizational directories
mkdir -p paper
mkdir -p solver
mkdir -p data
mkdir -p experimental_methodology
mkdir -p figures
mkdir -p archive

# Move paper-related files
echo "Organizing paper files..."
mv paper_submission paper/

# Move solver/backend code
echo "Organizing solver code..."
if [ -d "backend" ]; then
    mv backend solver/
fi

# Move data files and results
echo "Organizing data files..."
mv paper_submission/data/* data/ 2>/dev/null || true
mv paper_submission/figures/* figures/ 2>/dev/null || true
if [ -d "backend/results" ]; then
    mv solver/backend/results/* data/ 2>/dev/null || true
fi

# Move experimental methodology
echo "Organizing experimental methodology..."
mv experimental_procedure.tex experimental_methodology/
mv experimental_procedure.pdf experimental_methodology/
mv EXPERIMENTAL_APPARATUS_AND_PROCEDURE.md experimental_methodology/

# Move generation scripts
echo "Moving generation scripts..."
mv generate_*.py experimental_methodology/

# Move documentation
echo "Organizing documentation..."
mv PAPER_COMPLETE_STATUS.md paper/
mv PAPER_IMPROVEMENTS_COMPLETE.md paper/

# Archive HTML lesson files (not part of ISEF project)
echo "Archiving lesson files..."
mv *.html archive/ 2>/dev/null || true
mv lessons archive/ 2>/dev/null || true

# Create README in each directory
cat > paper/README.md << 'PAPER_README'
# Paper Directory

Contains the complete ISEF paper submission:
- `paper_submission/` - LaTeX source files and compiled PDF
- `PAPER_COMPLETE_STATUS.md` - Status of all improvements
- `PAPER_IMPROVEMENTS_COMPLETE.md` - Detailed improvement log
PAPER_README

cat > solver/README.md << 'SOLVER_README'
# Solver Directory

Contains the Taylor cone solver implementation:
- `backend/` - Python solver package
  - `solver/` - Core solver modules
  - `experimental/` - Experimental validation code
  - `app/` - Streamlit application
  - `examples/` - Example scripts
  - `tests/` - Automated test suite
SOLVER_README

cat > data/README.md << 'DATA_README'
# Data Directory

Contains all generated data and results:
- `synthetic_validation_results.txt` - Synthetic image validation
- `timing_results.txt` - Performance benchmarks
- Experimental data (TBD)
DATA_README

cat > experimental_methodology/README.md << 'EXP_README'
# Experimental Methodology Directory

Contains complete experimental procedure documentation:
- `experimental_procedure.pdf` - Compiled procedure manual (83 pages)
- `experimental_procedure.tex` - LaTeX source
- `EXPERIMENTAL_APPARATUS_AND_PROCEDURE.md` - Markdown version (41 pages)
- `generate_*.py` - Scripts for generating validation data and figures
EXP_README

cat > figures/README.md << 'FIG_README'
# Figures Directory

Contains all publication-quality figures:
- `system_schematic.pdf/.png` - Physical setup diagram
- `solver_flowchart.pdf/.png` - Computational pipeline
- `exponent_crossing.pdf/.png` - Novel observable (key contribution)
- `poisson_convergence.pdf/.png` - Grid convergence plot

All figures at 300 DPI for publication.
FIG_README

echo "Folder reorganization complete!"
echo ""
echo "New structure:"
tree -L 2 -d . 2>/dev/null || find . -maxdepth 2 -type d | head -20
