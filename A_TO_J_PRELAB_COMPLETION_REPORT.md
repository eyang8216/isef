# A–J pre-lab completion report
Date: 2026-09-10

## Executive status
**Scope reduced with limitations.** The repository is computationally organized and the regular Poisson component is verified, but the full Taylor-cone solver is not physically validated and the existing synthetic image routine does not meet its stated acceptance criteria. The project should not be labeled PRE-LAB COMPLETE until the manuscript is rewritten around this narrower scope and a qualified host reviews the physical protocol.

## Gate outcomes

### A — Provenance: partial, retained evidence only
Baseline archive, manifest and claim ledger exist under `audit/stage_a/`. Stage B–D reports and generated convergence logs are recorded. Historical unsupported synthetic-image and convergence claims are explicitly disqualified in the Stage D report. The old paper and outreach artifacts remain in the repository as provenance; they must be marked superseded before submission.

### B — Reproducibility: local gate passes, clean-environment gate pending
`pyproject.toml` now targets the active `solver/` package and `solver/tests`, and declares Plotly as a direct dependency. The active suite passes 82 tests in the available environment. A fresh Python-environment reproduction and immutable dependency lock/manifest were not performed; therefore the stronger clean-environment gate is pending.

### C — Mathematical contract: narrowed scope
The implementation is a reduced axisymmetric electrostatic–capillary residual framework for single-valued graph/cone-family interfaces. Curvature, normal orientation, Poisson sign, pressure projection and boundary precedence are tested locally. The fitted pressure mode is a diagnostic projection, not independent equilibrium closure. Space-charge modes are phenomenological exploratory closures. The model is not an unrestricted free-boundary electrospray predictor.

### D — Numerical verification: component gate passes; coupled gate pending
The quartic manufactured Poisson case gives observed orders near 2 on four systematically refined grids. This supports second-order convergence only for the regular manufactured Poisson component. It does not verify immersed-interface/coupled optimizer convergence. The existing coupled refinement, domain/apex/window sensitivity, independent matched reference and optimizer robustness studies remain incomplete.

### E — Lightweight performance: not established
No matched-accuracy baseline and no final reproducible accuracy–cost frontier were completed. “Lightweight” is retained as a design description, not an experimentally demonstrated superiority claim.

### F — Identifiability: not established
No final objective-landscape/conditioning/controlled-perturbation study was completed. Angle and projected voltage should be described as restricted diagnostic outputs, not uniquely precise physical estimates.

### G — Synthetic imaging: fails current acceptance criteria
The executable synthetic pipeline was rerun. For a nominal 49.29-degree cone with a 4 mm profile, the current round-trip routine returned angle errors of approximately 49.32 degrees at zero noise, 40.58 degrees at noise level 5, 43.39 degrees at noise level 10 and 66.81 degrees at noise level 20; profile RMSEs were approximately 1.89, 2.90, 3.94 and 6.17 mm. Its acceptance flag was false in each tested case. This is measurement-pipeline failure evidence, not solver validation. The manuscript must not retain the stated `<1 degree` / `<2%` qualification claim.

### H — Novelty: provisional only
No completed primary-source contribution matrix was verified during this execution. Novelty claims must remain provisional. A Python interface, classical Taylor angle and unit tests are not sufficient novelty evidence by themselves.

### I — Manuscript: not release-ready
The paper contains stale test counts and unsupported image-qualification language. It needs a claim-ledger-driven rewrite, generated tables/figures, updated references, and a clean compilation after the numerical and imaging status is reflected accurately.

### J — Lab package: physical review package can be prepared; physical gate pending
The proposed validation protocol can be framed as a host-review request. Actual apparatus safety approval, optical calibration, measured fluid/electrode properties, stable operating state, physical trials and model–data comparison cannot be completed in this environment and must remain pending.

## Retained claims
The repository supports these claims: a reduced axisymmetric solver exists; the active automated suite passes 82 tests in the recorded local environment; the regular manufactured Poisson component shows approximately second-order convergence; local geometry and residual contracts have regression coverage; and the code is suitable for further controlled computational and laboratory review.

## Withdrawn or narrowed claims
Do not claim that the current code is experimentally validated, predicts physical onset voltage, resolves full cone–jet dynamics, is an unrestricted free-boundary solver, demonstrates superior speed at matched accuracy, or has a qualified synthetic image-measurement pipeline. Do not retain the old 74-test count in the manuscript. Do not use the roundoff-level quadratic manufactured case as convergence evidence.

## Required before submission
Complete a clean environment run and manifest; complete coupled D campaigns and E/F studies; repair G or explicitly remove image-accuracy claims; perform H with primary sources; rewrite and compile I; mark superseded documents; and obtain qualified host review for J. The exact stopping boundary is physical metrology and approved apparatus operation—not broken code or unfinished documentation.

## Reproduction commands
```bash
cd isef
python3 -m pytest -q
PYTHONPATH=solver python3 solver/examples/10_quartic_poisson_convergence.py
PYTHONPATH=solver python3 solver/examples/00_manufactured_poisson.py
```
