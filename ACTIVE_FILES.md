# Active ISEF project set

This folder contains the files intended for current work and professor review. The `archive/` directory contains historical drafts, superseded reports, intermediate build files, legacy code, and cleanup artifacts; it is retained for provenance and is not part of the active submission set.

## Start here

- `README.md` — project orientation and reproduction guidance.
- `教授评审与项目执行计划_轻量化Taylor锥求解器.pdf` — Chinese professor-review document.
- `教授评审与项目执行计划_轻量化Taylor锥求解器.docx` — editable version of the same document.
- `paper/paper_submission/build/isef_taylor_cone_updated_draft.pdf` — current paper draft.
- `A_TO_J_PRELAB_COMPLETION_REPORT.md` — evidence status and release limitations.

## Active technical material

- `solver/` — active solver package and tests.
- `experiments/` — current validation protocols and generation scripts.
- `paper/paper_submission/` — current manuscript source, figures, data and build files.
- `audit/` — provenance, reproducibility, mathematical and numerical audit evidence.
- `results/` — current machine-generated result records.
- `app/` — current demonstration interface.
- `pyproject.toml` and `requirements.txt` — environment declarations.

## Reproduction

From this directory:

```bash
python3 -m pytest -q
PYTHONPATH=solver python3 solver/examples/10_quartic_poisson_convergence.py
PYTHONPATH=solver python3 solver/examples/00_manufactured_poisson.py
```

The active status is a reduced, computationally verified framework with limitations. It is not yet experimentally validated.
