# Implementation Status — Version 2 Solver (Complete)

Status: Version 1 and Version 2 both complete.

## Version 2 — new modules

- `solver/space_charge.py` — extended with threshold-activated closure `solve_threshold_shielding()`. Nonlinear fixed-point iteration reusing the Gaussian loop; nodes with `|E| < E_c` produce exactly zero charge.
- `solver/optimization.py` — analytic cone-family shape optimizer (Powell, gradient-free). Free variables: cone half-angle and apex radius. Δp always mean-subtracted; never a free variable. Geometry-constrained angle bound prevents off-grid interfaces. Per ADR-0001: no splines.
- `solver/app_backend.py` — `RunParams` + `SolverResult` frozen dataclasses. Single `run_solver()` entry point covering Laplace, Gaussian, and threshold cases. Five Plotly figure builders. No `st.*` imports.
- `app/streamlit_app.py` — two-tier sidebar (6 basic inputs + Advanced expander), Run button, KPI metrics + `st.dataframe()` diagnostics table, five Plotly charts.

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
- `solver/plotting.py` — minimal matplotlib helpers (CLI/examples only; unchanged in V2).

## Tests

Test command (from repo root):

```bash
.venv/bin/python -m pytest -q
```

Current result:

```text
33 passed
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

## Important caveats

- The Gaussian and threshold space-charge closures are effective (phenomenological) models, not physically complete emission transport models.
- The shape optimizer recovers ~43.5° vs the theoretical 49.3° Taylor angle. The ~6° deviation is caused by the grid-mask `conical_conductor` geometry (see `solver/geometry.py`), which is not a sharp immersed-boundary method. A proper sharp-cone representation would close this gap — deferred to V3.
- The `shielding_metric()` function in `space_charge.py` accepts an optional apex-local ROI mask. Always use the mask for physically meaningful shielding claims — the global Emax is dominated by Dirichlet boundary corners.
- The interface residual in the app is diagnostic only — it evaluates the YLM balance on a *prescribed* interface shape. The half-angle shown is the input angle, not a predicted equilibrium value. To get a predicted angle, run `examples/05_shape_optimization_demo.py`.
- Threshold charge and shape optimizer are intentionally decoupled in V2 (ADR-0002). Coupling them in a single loop is V3 work.

## Version 3 (not started — gated on hardware approval)

1. Couple threshold closure inside the optimizer loop (ADR-0002 deferred).
2. Leaky-dielectric liquid potential and surface charge conservation.
3. Current-constrained shielding closure.
4. Experimental computer-vision comparison against electrospray images.
