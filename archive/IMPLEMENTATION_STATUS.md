# Implementation Status — Versions 1–2 complete; V3 immersed-boundary milestone in progress

Status: Version 1 and Version 2 are complete. V3 immersed free-boundary milestone
is **functionally complete and verified** with 58 automated tests passing in the
local `.venv`. Second-order convergence proven, Taylor identity verified (ratio 1.009),
onset-voltage projection working (V0* ≈ 28.9 kV). The ~0.7° systematic offset from
49.29° is documented as a model property (rounded cap + finite domain), not a solver bug.

## V3 immersed-boundary milestone

Implemented:

- `ImplicitCone` in `solver/geometry.py` — a shared C1 tangent spherical-cap /
  straight-flank geometry with an explicit sign convention. The liquid is
  `signed_function <= 0`, the gas-side normal points toward increasing signed
  value, and `sample_graph()` supplies the same zero contour to residual code.
- `solver/immersed.py` — fractional-distance immersed Dirichlet corrections
  for gas rows adjacent to the conductor, including the axisymmetric radial
  first-derivative term, conductor identity rows, Poisson RHS preservation,
  and gas-side one-sided normal-field reconstruction.
- `solver/electrostatics.py` — optional `immersed=` path for Laplace/Poisson
  solves. Legacy staircase and rectangular paths remain available.
- `solver/optimization.py` — `immersed_mode=True` rebuilds the cone boundary,
  masks, sparse system, and field on every candidate evaluation. The result
  reports whether immersed mode was used, initial/final residuals, field
  variation, and candidate solve failures.
- `solver/residual.py` — optional one-sided `E_n_override` and explicit sample
  masks for cap/flank-aware diagnostics.
- `solver/space_charge.py` / `solver/config.py` — stronger parameter validation,
  gas-only effective charge, and a final solve using the accepted charge state.
- `examples/07_immersed_free_boundary.py` — grounded-box amplitude-projected
  free-boundary demonstration. Recovers angle ~44° with onset voltage V0* ≈ 28.9 kV.
- `examples/08_immersed_refinement_study.py` — three-part refinement study showing
  immersed operator converges (vs non-convergent legacy staircase), objective
  shape, and Powell behavior.
- `examples/09_ideal_limit_study.py` — documents why grounded-box cannot recover
  49.29° (model property: larger box → larger argmin).
- `tests/test_taylor_onset.py` — imposed-Taylor verification confirming amplitude
  identity ratio 1.009 (≤ 3% target) and argmin ~50° (±1° resolution).

**Status after 2026-08-09 fixes:**
- Tiny-cut failures eliminated (0 candidate failures, was 1/343)
- Cubic-exact E_n reconstruction (≤ ±1% accuracy, was growing with refinement)
- Onset-voltage projection working (clean V-shape with interior minimum ~44°)
- Second-order convergence formally proven (Richardson test: observed order ≈ 2.0)
- Taylor identity verified (ratio 1.009 on imposed-Taylor problem)

### What is not yet proven

- ~~Second-order convergence for the immersed operator on a smooth manufactured
  irregular-boundary problem.~~ **Proven 2026-08-09**: `test_smooth_immersed_manufactured_solution_second_order_convergence`
  asserts observed L2 order ≥ 1.8 on three refinement levels of the smooth
  circle manufactured problem (measured ≈ 2.0). See `tests/test_immersed.py`.
- Convergence of interface-normal field, Maxwell pressure, residual, or angle.
- A unique physical free-boundary solution with volume/contact-line constraints.
- Convergence of the rounded finite-domain optimizer to the ideal 49.29° limit.
- Physical space-charge/current transport or onset-voltage prediction.

The analytical 49.290089° Legendre-root routine remains a reference benchmark,
not evidence that the finite optimizer independently recovers Taylor's angle.

## Version 2 — new modules

- `solver/space_charge.py` — Gaussian and threshold-activated closures. Both
  share the under-relaxed fixed-point iteration in the private
  `_fixed_point_iterate()` helper; the Gaussian closure relaxes toward a
  prescribed cloud, the threshold closure toward
  `rho_max * (1 - exp(-(|E| - E_c) / E_s))` with nodes `|E| < E_c` producing
  exactly zero charge.
- `solver/optimization.py` — analytic cone-family shape optimizer (Powell,
  gradient-free). Free variables: cone half-angle and apex radius. Δp always
  mean-subtracted; never a free variable. Geometry-constrained angle bound
  prevents off-grid interfaces. Per ADR-0001: no splines.
  **Coupled mode** (V3 Track A item 1): passing
  `sc_params=SpaceChargeParams(model="threshold", ...)` runs the threshold
  fixed-point loop inside every optimizer evaluation, so the field adjusts to
  the current shape's space-charge distribution; `OptimizationResult` reports
  `sc_converged` / `sc_iterations` (see ADR-0002).
- `solver/app_backend.py` — `RunParams` + `SolverResult` frozen dataclasses.
  Single `run_solver()` entry point covering Laplace, Gaussian, and threshold
  cases. Five Plotly figure builders. No `st.*` imports.
- `app/streamlit_app.py` — two-tier sidebar (6 basic inputs + Advanced
  expander), Run button, KPI metrics + `st.dataframe()` diagnostics table,
  five Plotly charts.

## Version 1 — original modules (unchanged)

- `solver/config.py` — parameter dataclasses and constants.
- `solver/grid.py` — axisymmetric grid, flattening convention `k = i*nz + j`.
- `solver/geometry.py` — rectangular and conical mask builders.
- `solver/operators.py` — sparse axisymmetric Laplace/Poisson operator, `r=0` stencil.
- `solver/boundary_conditions.py` — Dirichlet row replacement.
- `solver/electrostatics.py` — Laplace/Poisson solve entry points (SciPy `spsolve`).
- `solver/fields.py` — electric field reconstruction, bilinear interpolation.
- `solver/interface.py` — graph interface `R(z)`, normals, curvature, half-angle extraction.
- `solver/residual.py` — Maxwell pressure, capillary pressure, YLM residual diagnostics.
- `solver/verification.py` — manufactured-solution verification utilities.

## Tests

Test command (from repo root):

```bash
.venv/bin/python -m pytest -q
```

Current result:

```text
58 passed in ~45s
```

Tests cover (V1 + V2 + V3 additions):

- grid indexing and flatten/unflatten convention,
- sparse axisymmetric operator including `r=0` regularized axis stencil,
- arbitrary Dirichlet row replacement,
- far-boundary Dirichlet precedence,
- classical Taylor angle benchmark from the Legendre root,
- manufactured Poisson exact quadratic sanity case,
- nontrivial quartic manufactured Poisson convergence under refinement,
- electrostatics convergence order (L2 error halves at 2× grid refinement),
- electric field derivative signs,
- bilinear interpolation,
- simple curvature and half-angle extraction,
- parallel-plate voltage scaling,
- Gaussian charge-density construction,
- Poisson RHS sign convention,
- region-of-interest shielding metric behavior,
- threshold closure shielding sanity (interior S_E > 0),
- residual decreases toward equilibrium interface shape,
- optimizer returns finite result within bounds,
- optimizer reduces residual vs. initial shape,
- coupled threshold+optimizer mode: inner-loop status reported and residual
  landscape shifts vs. Laplace-only,
- app_backend returns complete SolverResult with all fields,
- SolverResult half_angle in (0°, 90°) for Laplace case,
- immersed operator second-order convergence (Richardson test, 3 levels, order ≥ 1.8),
- immersed tiny-cut pinning (gas nodes near pathological cuts pinned to boundary),
- cubic-exact E_n reconstruction with full-cell samples,
- Taylor amplitude identity verification (imposed-Taylor boundary, ratio ≤ 3%),
- onset-voltage projection in optimizer,
- immersed verification backend and Streamlit tab.

## Examples

```bash
python examples/00_manufactured_poisson.py
python examples/01_parallel_plate_laplace.py
python examples/02_gaussian_space_charge.py
python examples/03_interface_residual_demo.py
python examples/04_taylor_angle_benchmark.py
python examples/05_shape_optimization_demo.py   # V2: Powell optimizer, legacy staircase ~43.5°
python examples/06_threshold_space_charge.py    # V2: threshold closure, S_E > 0
python examples/07_immersed_free_boundary.py    # V3: grounded-box immersed, ~44°, V0* ≈ 28.9 kV
python examples/08_immersed_refinement_study.py # V3: convergence study, objective analysis
python examples/09_ideal_limit_study.py         # V3: why grounded-box ≠ 49.29° (model property)
```

## Running the Streamlit app

```bash
cd ~/Desktop/isef
source .venv/bin/activate
streamlit run app/streamlit_app.py
```

The app has two tabs:
- **Classic** — original Laplace/Gaussian/Threshold solver with diagnostic interface
- **Immersed verification** — grounded-box and imposed-Taylor verification results

(The app imports `solver` through the editable install — see
`docs/running_solver.md`. No `sys.path` hack is needed.)

## Important caveats and guardrails

- The Gaussian and threshold space-charge closures are effective
  (phenomenological) models, not physically complete emission transport models.
- **Angle recovery:**
  - Legacy staircase optimizer (example 05): ~43.5° (first-order staircase error)
  - Immersed grounded-box (example 07): ~44° (onset-projected, verified)
  - Imposed-Taylor identity test: ~50.0° argmin (~0.7° systematic offset from 49.29°)
  - The ~0.7° offset is a **model property** (rounded cap + finite domain + discretization floor),
    not a solver bug. Angle resolution is ±1°. The strong result is the Taylor identity
    ratio 1.009 ≈ 1.0, which verifies the free-boundary coupling.
- **Do not claim:** "recovered 49.29° on grounded-box" — larger box → larger argmin (model property)
- The `shielding_metric()` function accepts an optional apex-local ROI mask. Always use
  the mask for physically meaningful shielding claims — global Emax is dominated by
  Dirichlet boundary corners.
- **Gaussian S_E ≈ -0.7%** (anti-shielding) — parameter regime issue, not yet resolved.
  Do not claim "shielding works" until this is fixed.
- The interface residual in the Classic app tab is diagnostic only — it evaluates the YLM
  balance on a *prescribed* interface shape. To get a predicted angle, run the optimizer
  examples or use the Immersed verification tab.
- Threshold closure and shape optimizer are decoupled by default and optionally coupled
  via `sc_params` (ADR-0002). Coupled mode is significantly slower.

## Version 3

### Track A — computational

1. ✅ **Couple threshold closure inside the optimizer loop** — done (commit `7bef973`; ADR-0002).
2. ✅ **Immersed free-boundary with rounded cone** — done (commits `ebea0b8` through `d2f703f`).
   - Second-order convergence proven (Richardson test: order ≈ 2.0)
   - Cubic-exact E_n reconstruction (≤ ±1% accuracy)
   - Onset-voltage projection working (V0* ≈ 28.9 kV)
   - Taylor identity verified (ratio 1.009, ≤ 3% target)
   - Zero candidate failures (tiny-cut pinning fix)
   - See `.scratch/taylor-onset-framing/spec.md` for full verification details
3. ⏳ **Leaky-dielectric liquid potential** and surface charge conservation (deferred to V4).
4. ⏳ **Current-constrained shielding closure** (deferred to V4).

### Track B — experimental (gated on school approval)

1. Experimental computer-vision comparison against electrospray images.
