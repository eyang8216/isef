# Stage D — Numerical verification implementation report
Date: 2026-09-08
Status: Stage D initial implementation complete; broader convergence and independent benchmark campaigns remain pending.

## Changes made
Added `solver/tests/test_stage_d_math_contract.py` with six mathematical-contract tests covering cylinder curvature, linear-flank curvature, prescribed-pressure residual behavior, pressure-projection behavior, sample-mask pressure fitting and invalid graph-interface inputs. The full test suite now reports 80 passing tests.

The repository configuration changes from Stage B remain active: package/test paths point to `solver/`, Plotly is a direct dependency, imaging dependencies are optional, and the declared Python minimum matches the tested environment.

## Verification run
Command:
```bash
python3 -m pytest -q
```
Result:
```text
80 passed
```
Manufactured Poisson example:
```bash
PYTHONPATH=solver python3 solver/examples/00_manufactured_poisson.py
```
Observed L2 errors were approximately 2.385e-15, 5.848e-15 and 9.565e-15 on the three grids; Linf errors were approximately 4.163e-15, 8.910e-15 and 1.688e-14. These are near floating-point roundoff for the manufactured case and therefore do not support a second-order convergence claim. The existing paper convergence wording must be corrected or the underlying experiment regenerated with a nontrivial, source-generated discretization error.

## Interpretation
The new tests verify important local mathematical contracts. They do not prove that the complete immersed free-boundary calculation is convergent, physically valid or experimentally predictive. The original solver remains a reduced graph-interface residual framework. Pressure projection is explicitly tested as a diagnostic operation that removes a constant mean; prescribed pressure is tested separately.

## Remaining Stage D work
Audit optimizer degrees of freedom and objective normalization; add direct tests for axis-limit field behavior and boundary-mask precedence; regenerate nontrivial convergence data from the solver; run domain/apex-cutoff and boundary sensitivity studies; perform an independent matched benchmark where possible; and update paper claims only after those results exist.

## Stage D gate
- [x] Mathematical regression tests added.
- [x] Full suite rerun: 80 passed.
- [x] Manufactured run regenerated and interpreted honestly.
- [x] Near-roundoff result prevented from being mislabeled as second-order convergence.
- [ ] Complete solver convergence campaign.
- [ ] Independent matched benchmark.
- [ ] Manuscript rewrite.
