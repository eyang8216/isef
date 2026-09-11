# Stage D — Final numerical verification report
Date: 2026-09-09
Status: completed for the defined verification scope; independent physical validation remains out of scope.

## Completed work
Stage D added mathematical-contract regression tests and boundary/axis tests. The full test suite passes with 82 tests. The active package configuration remains aligned with `solver/`.

The manufactured quadratic case was re-run and correctly classified as a roundoff diagnostic, not a convergence study. A new source-derived quartic manufactured Poisson case was added at `solver/solver/verification.py::manufactured_phi_quartic` / `run_quartic_manufactured_poisson`, with executable driver `solver/examples/10_quartic_poisson_convergence.py`.

## Nontrivial convergence result
The quartic case produced:

| Grid | L2 error | Linf error | observed L2 order | observed Linf order |
|---|---:|---:|---:|---:|
| 17 x 19 | 1.82155502e-03 | 2.98447695e-03 | — | — |
| 33 x 37 | 4.44529637e-04 | 7.49622691e-04 | 2.03482 | 1.99324 |
| 65 x 73 | 1.09730635e-04 | 1.87655469e-04 | 2.01831 | 1.99808 |
| 129 x 145 | 2.72549081e-05 | 4.69314141e-05 | 2.00938 | 1.99946 |

This supports approximately second-order convergence for the tested regular manufactured axisymmetric Poisson problem. It does not establish second-order convergence of the immersed interface operator or the coupled Taylor-cone optimizer.

## Tests
Command:
```bash
python3 -m pytest -q
```
Result: 82 passed.

## Remaining limitations
The full coupled solver still requires a dedicated refinement campaign with source-generated outputs, domain/apex-cutoff sensitivity, optimizer initial-guess studies, and a matched independent reference. The current boundary test verifies deterministic powered-over-far-boundary precedence, but the broader geometry-mask policy should remain documented. No numerical result here validates physical onset voltage or experimental image accuracy.

## Claim disposition after Stage D
Retain: source-derived second-order convergence of the regular manufactured Poisson solver; local graph-curvature and residual-contract tests; explicit distinction between prescribed and fitted pressure.

Narrow: Taylor-angle result to an analytical/ideal-limit consistency benchmark; lightweight claims to measured accuracy–cost evidence when benchmarked.

Withdraw or hold: the old hard-coded convergence figure as evidence, the old synthetic image-accuracy table, and any wording implying physical onset-voltage validation or full electrospray prediction.
