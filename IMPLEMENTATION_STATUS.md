# Implementation Status — Versions 1–2 Complete, V3 Track A Started

Status: Version 1 and Version 2 both complete. Version 3 Track A item 1
(threshold–optimizer coupling) is also complete as of `7bef973`.

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
34 passed
```

Tests cover (V1 + V2 additions):

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
- SolverResult half_angle in (0°, 90°) for Laplace case.

## Examples

```bash
python examples/00_manufactured_poisson.py
python examples/01_parallel_plate_laplace.py
python examples/02_gaussian_space_charge.py
python examples/03_interface_residual_demo.py
python examples/04_taylor_angle_benchmark.py
python examples/05_shape_optimization_demo.py   # V2: Powell optimizer, recovers ~43.5°
python examples/06_threshold_space_charge.py    # V2: threshold closure, S_E > 0
```

## Running the Streamlit app

```bash
streamlit run app/streamlit_app.py
```

(The app imports `solver` through the editable install — see
`docs/running_solver.md`. No `sys.path` hack is needed.)

## Important caveats

- The Gaussian and threshold space-charge closures are effective
  (phenomenological) models, not physically complete emission transport models.
- The shape optimizer recovers ~43.5° vs the theoretical 49.3° Taylor angle.
  The ~6° deviation is caused by the grid-mask `conical_conductor` geometry
  (see `solver/geometry.py`), which is not a sharp immersed-boundary method.
  A proper sharp-cone representation would close this gap — the staircase /
  ghost-cell research is tracked in `.scratch/taylor-cone-fd-bcs/`.
- The `shielding_metric()` function in `space_charge.py` accepts an optional
  apex-local ROI mask. Always use the mask for physically meaningful shielding
  claims — the global Emax is dominated by Dirichlet boundary corners.
- The interface residual in the app is diagnostic only — it evaluates the YLM
  balance on a *prescribed* interface shape. The half-angle shown is the input
  angle, not a predicted equilibrium value. To get a predicted angle, run
  `examples/05_shape_optimization_demo.py`.
- Threshold closure and shape optimizer are decoupled by default and
  optionally coupled via `sc_params` (ADR-0002). Coupled mode is significantly
  slower: each Powell evaluation runs the full Poisson fixed-point iteration
  (typically 20–80 iterations). Tune `sc_params.max_iterations` and
  `sc_params.tolerance` to control the inner-loop cost.
- `solver/plotting.py` (unused matplotlib helpers) was removed in the V2.1
  cleanup — it had no callers; examples rely on their own inline plotting.

## Version 3

### Track A — computational (in progress)

1. ✅ Couple threshold closure inside the optimizer loop — done (commit
   `7bef973`; ADR-0002 updated in the same commit).
2. Improve the conical-conductor geometry to close the ~6° optimizer angle
   error. Literature research on staircase error and ghost-cell /
   immersed-boundary Dirichlet corrections is in
   `.scratch/taylor-cone-fd-bcs/research.md`.
3. Leaky-dielectric liquid potential and surface charge conservation.
4. Current-constrained shielding closure.

### Track B — experimental (gated on school approval)

1. Experimental computer-vision comparison against electrospray images.
