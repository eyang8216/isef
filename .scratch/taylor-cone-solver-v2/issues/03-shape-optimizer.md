# 03 — Shape optimizer

**What to build:** Create `solver/optimization.py` with an analytic cone-family parameterization and a Powell optimizer that minimises the RMS residual, add `tests/test_optimization.py`, and add `examples/05_shape_optimization_demo.py`.

The shape family is parameterized by 2–3 scalars (cone angle as the primary free variable; apex radius and nozzle radius as secondary). All parameters have box bounds — cone angle in (0°, 90°), apex radius ≥ grid spacing. The pressure offset Δp is always eliminated analytically via mean-subtraction and is never a free variable. Per ADR-0001, spline control points are out of scope.

The optimizer uses `scipy.optimize.minimize(..., method='Powell', bounds=...)`. It returns the optimised half-angle and final RMS residual. The primary validation: the example script runs in the Laplace limit and prints a recovered half-angle near 49.3°. If it doesn't converge there, the optimization loop is broken.

Per ADR-0002, the optimizer always runs with the Laplace solve in V2 — it never calls the threshold or Gaussian shielding closures internally.

**Blocked by:** 02 — strengthen V1 test foundations

**Status:** ready-for-agent

- [ ] `solver/optimization.py` created with analytic cone-family parameterization (cone angle, apex radius, nozzle radius)
- [ ] Box bounds enforced on all shape parameters
- [ ] Δp eliminated via mean-subtraction; never a free variable
- [ ] Powell optimizer returns optimised half-angle and final RMS residual
- [ ] `tests/test_optimization.py`: (a) optimizer recovers a known angle on a simple cone case; (b) Powell converges within tolerance; (c) no parameter leaves its box bounds
- [ ] `examples/05_shape_optimization_demo.py` runs in the Laplace limit and prints a recovered half-angle near 49.3°
- [ ] All tests pass
