# Immersed Free-Boundary Implementation Plan

> **For implementation:** execute task-by-task with tests before integration.

**Goal:** Make each candidate cone the powered equipotential boundary of the axisymmetric Laplace/Poisson solve, while preserving the structured gas grid and legacy solver paths.

**Architecture:** Add one shared rounded-cone geometry (`ImplicitCone`) that produces both the implicit conductor and sampled graph interface. Add a ghost-value immersed Dirichlet correction to gas rows adjacent to the conductor, plus one-sided normal-field reconstruction from the gas. Integrate this optional path into electrostatics and the optimizer; retain the legacy staircase path for regression and app compatibility.

**Tech stack:** Python 3.11+, NumPy, SciPy sparse matrices/optimization, pytest.

---

## Scientific conventions

- `ImplicitCone.signed_function(r,z) <= 0` is conducting liquid; `> 0` is gas.
- The physical apex is on the axis at `z=apex_z`; liquid extends toward decreasing `z`.
- `apex_radius` is the spherical cap curvature radius.
- A tangent spherical cap joins a straight cone flank with C1 continuity.
- The gas-side normal points toward increasing signed function.
- The exact Taylor potential benchmark and the smooth immersed-boundary order test are separate; no hard optimizer requirement of 49.29° is imposed until a converged ideal-limit study supports it.

## Task 1: Shared geometry

**Files:** modify `solver/geometry.py`, `solver/interface.py`; create `tests/test_implicit_cone.py`.

- Implement tangent cap/flank equations, signed function, normal, masks, exact segment boundary crossing, flank mask, and graph sampling.
- Test cap/flank continuity, sign convention, normals, and graph/zero-contour consistency.

## Task 2: Immersed operator and surface field

**Files:** create `solver/immersed.py`, `tests/test_immersed.py`.

- For each gas row whose axis-aligned neighbor is conductor, eliminate the ghost-node value using the exact fractional boundary distance and powered boundary value.
- Keep conductor nodes as Dirichlet rows and preserve arbitrary Poisson RHS on gas nodes.
- Reconstruct normal field using second-order one-sided samples into gas, with a first-order fallback near outer boundaries.
- Verify a smooth manufactured harmonic/Poisson problem independently of the singular Taylor solution.

## Task 3: Solver integration

**Files:** modify `solver/electrostatics.py`, `solver/residual.py`, `solver/__init__.py`; extend relevant tests.

- Add optional `immersed: ImplicitCone | None` to electrostatic entry points.
- Use immersed masks/operator only when requested; preserve all old signatures and behavior.
- Permit residual evaluation from a supplied boundary-normal field and a flank-only sample mask.

## Task 4: True shape-dependent optimizer

**Files:** modify `solver/optimization.py`, `tests/test_optimization.py`.

- Add an immersed mode in which every Powell candidate constructs its own cone, operator, potential, and normal field.
- Keep mean elimination of `delta_p` and report cap radius/base radius accurately.
- Catch only expected geometry/numerical failures and retain actionable diagnostics.
- Test that changing shape changes the field and that optimization lowers its own initial immersed objective; do not assert a predetermined Taylor angle.

## Task 5: Poisson correctness

**Files:** modify `solver/space_charge.py`, `solver/config.py`, `tests/test_space_charge.py`.

- Mask closure charge to gas nodes.
- Ensure returned `rho_e`, potential, and field are from the same accepted fixed-point state via a final solve.
- Validate tolerance/model parameters and add a discrete returned-state consistency test.
- Keep nonlinear immersed threshold optimization out of the first verified Laplace milestone unless integration is demonstrably stable.

## Task 6: Physics benchmarks and documentation

**Files:** create `examples/07_immersed_taylor_benchmark.py`; update `IMPLEMENTATION_STATUS.md`, ADR/spec/current run docs.

- Compare staircase and immersed boundary errors for a prescribed Taylor cone away from the singular apex.
- Report grid/domain sensitivity and field scaling without claiming the rounded finite-domain optimizer must equal 49.29°.
- Document limitations, exact conventions, and test count from a fresh run.

## Verification gates

1. All legacy tests pass.
2. New geometry invariants pass.
3. Smooth immersed manufactured test converges under refinement in a declared norm/region.
4. Poisson returned-state residual is consistent with returned charge.
5. Candidate shape demonstrably changes the solved potential/field.
6. Optimizer lowers the initial immersed residual without a bound-forced scientific claim.
7. Example and full test suite run from a clean editable install.
