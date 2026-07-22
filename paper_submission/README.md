# Paper Submission Draft

This folder contains a competition-facing LaTeX paper draft for the Taylor-cone solver project.

## Contents

- `main.tex` — main LaTeX document
- `sections/` — modular paper sections
- `references.bib` — bibliography
- `figures/` — placeholder for final figures
- `tables/` — placeholder for exported result tables
- `build/` — placeholder for compiled output

## Compile locally

This computer has `tectonic` available, so the draft can be compiled with:

```bash
cd /Users/a1/Desktop/isef/paper_submission
tectonic main.tex
```

If a full LaTeX distribution is installed, either of these also works:

```bash
cd paper_submission
latexmk -pdf main.tex
```

or:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Compile using Overleaf

If LaTeX is not installed locally, upload the contents of `paper_submission/` to Overleaf and compile `main.tex`.

## Current status

This draft intentionally includes placeholders for experimental data because physical validation has not yet been performed. Current completed results include theory, solver architecture, numerical validation, and planned experimental methodology.
