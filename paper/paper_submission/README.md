# Paper Submission Draft

Competition-facing LaTeX manuscript for the Taylor-cone solver project.

## Contents

- `main.tex` — main LaTeX document
- `sections/` — modular paper sections; `revision_style.tex` defines the tracked-change markup
- `references.bib` — bibliography
- `figures/` — generated figures
- `data/` — regenerated result tables quoted in the text
- `tables/` — exported table sources
- `build/` — archived earlier submission draft
- `main.pdf` — compiled output

## Compile locally

A full LaTeX distribution is required (`latexmk`, `pdflatex`, `bibtex`):

```bash
cd paper/paper_submission
rm -f main.out          # a truncated main.out makes latexmk fail on bookmarks
latexmk -pdf main.tex
```

`pdflatex` plus `bibtex` also works, with three `pdflatex` passes.

## Compile using Overleaf

Upload the contents of `paper_submission/` to Overleaf and compile `main.tex`.

## Regenerating figures and result tables

Figures and the `data/` tables are produced by the scripts in
`experiments/methodology/` (`generate_figures.py`,
`generate_synthetic_validation.py`, `generate_timing_data.py`,
`generate_convergence_plot.py`). See `figures/README.md` for the figure list.

## Current status

Theory, solver architecture, the numerical results in Section 6, and the
published-image comparison in Section 7 are complete. No physical experiments
were carried out for this manuscript, so it reports no measured data of its own.
