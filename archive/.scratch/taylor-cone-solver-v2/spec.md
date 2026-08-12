# Spec: Taylor-Cone Solver — Version 2

Status: completed

**Source docs:** `CONTEXT.md`, `docs/adr/0001-analytic-cone-family-for-optimizer.md`,
`docs/adr/0002-threshold-and-optimizer-decoupled-in-v2.md`,
`notes/Solver/06_Space_Charge_Shielding.md`, `notes/Solver/07_Shape_Optimization.md`,
`notes/Solver/09_Online_App_Interface.md`, `implementation_outline.md` §§5.9–5.13,
`IMPLEMENTATION_STATUS.md`.

## Problem Statement

Version 1 can diagnose a shape you hand it — it computes the Young–Laplace–Maxwell residual on a prescribed interface and reports a half-angle. But it cannot find the equilibrium interface itself, cannot model the nonlinear threshold-activated space-charge closure, and has no interactive UI. For ISEF, the solver needs to be able to claim it *predicts* cone geometry (by finding the interface that minimises the residual), demonstrate the nonlinear shielding effect (threshold closure), and be usable interactively by a judge without reading the code.

Three concrete gaps in the codebase:
1. `solver/optimization.py` — does not exist.
2. Threshold-activated branch in `solver/space_charge.py` — not implemented (stubs only in the notes).
3. `solver/app_backend.py` and `app/streamlit_app.py` — do not exist.

Additionally, two V1 tests are thin enough to miss sign bugs that the V2 optimizer would silently amplify:
- `tests/test_electrostatics.py` — one test, no convergence-order check.
- `tests/test_residual.py` — two tests, no check that residual decreases toward a better-shaped interface.

## Solution

Add three new modules (`optimization.py`, `app_backend.py`, `app/streamlit_app.py`), implement the threshold closure in the existing `space_charge.py`, and strengthen the two thin V1 tests. The resulting solver can find the equilibrium half-angle by minimising the RMS residual over an analytic cone family, model nonlinear threshold-activated charge, and expose everything interactively through a two-tier Streamlit app.

## User Stories

1. As the researcher, I want to parameterise the interface as an analytic cone family with 2–3 shape parameters (cone angle, apex radius, nozzle radius), so that the optimizer has a small, interpretable search space for the initial validation.
2. As the researcher, I want to run the Powell optimizer over the cone-family shape parameters, so that the solver finds the interface that minimises the RMS residual without requiring gradients.
3. As the researcher, I want box bounds on every shape parameter (e.g. cone angle constrained to (0°, 90°), apex radius ≥ grid spacing), so that the optimizer never evaluates a geometrically invalid interface.
4. As the researcher, I want the pressure offset Δp always eliminated analytically via mean-subtraction during optimization, so that Δp is never a degree of freedom and the search space stays minimal.
5. As the researcher, I want the optimizer to return the optimised half-angle alongside the final RMS residual, so that I can immediately compare against the 49.3° theoretical value.
6. As the researcher, I want an example script (`examples/05_shape_optimization_demo.py`) that runs the optimizer in the Laplace limit and prints the recovered half-angle, so that the optimizer result is demonstrable without the app.
7. As the researcher, I want a threshold-activated space-charge closure `ρ_e = ρ_max·(1 - exp(-(|E| - Ec)/Es))₊` implemented as a standalone `solve_threshold_shielding()` function in `space_charge.py`, so that the nonlinear charge model can be tested independently of the shape optimizer.
8. As the researcher, I want the threshold closure to reuse the existing fixed-point iteration machinery from `solve_gaussian_shielding()`, so that convergence behaviour is consistent and the threshold case doesn't introduce a parallel code path.
9. As the researcher, I want the threshold closure to correctly zero out `ρ_e` at nodes where `|E| < Ec`, so that charge only activates above the critical field.
10. As the researcher, I want a shielding sanity test confirming that `solve_threshold_shielding()` produces `S_E > 0` (field reduced) for physically sensible parameters, so that a sign bug in the Poisson source or the closure can't silently produce anti-shielding.
11. As the researcher, I want an example script (`examples/06_threshold_space_charge.py`) demonstrating the threshold closure and printing the apex-local shielding metric, so that the nonlinear shielding case is demonstrable in isolation.
12. As the researcher, I want `test_electrostatics.py` strengthened with a second test that checks convergence order (L2 error halves as grid spacing halves on a known manufactured solution), so that a regression in the operator or BC application is caught at the electrostatics level rather than only at the manufactured-Poisson integration level.
13. As the researcher, I want `test_residual.py` strengthened with a test confirming that a better-shaped interface (one closer to the equilibrium cone angle) produces a lower RMS residual than a worse-shaped one, so that the optimizer has a verified signal to follow.
14. As the researcher, I want `app_backend.py` to expose a single `run_solver(params) -> SolverResult` entry point that takes UI parameter values, calls the solver modules, and returns a structured `SolverResult` dataclass, so that the Streamlit app layer has no direct dependency on numpy arrays or solver internals.
15. As the researcher, I want `SolverResult` to carry the full field state (`phi`, `Er`, `Ez`, `E_mag`, `rho_e`), interface geometry, residual diagnostics, and scalar outputs (half-angle, peak field, RMS residual, shielding metric, runtime, convergence status), so that the app can render any combination of plots and scalars without calling back into the solver.
16. As the researcher, I want `app_backend.py` to be testable without a Streamlit session (i.e. its functions are plain Python, no `st.*` calls), so that `SolverResult` correctness can be verified in pytest.
17. As the researcher, I want `streamlit_app.py` to have a basic sidebar with 5–6 physically meaningful inputs (voltage, surface tension, electrode spacing, nozzle radius, grid resolution, space-charge model), so that a judge can run a case without being confronted by numerical tuning knobs.
18. As the researcher, I want an "Advanced" expander in the app sidebar that reveals space-charge closure parameters (`ρ₀`, `ℓ`, `Ec`, `Es`, `ρ_max`, `ω`) and BC tuning, so that I can access full control without cluttering the default view.
19. As the researcher, I want the app to run the solver on a "Run" button click and display Plotly figures (potential contour, electric field magnitude, interface overlay, residual along interface, space-charge density) and a scalar diagnostics table, so that results update interactively on each run.
20. As the researcher, I want the app to display convergence status and runtime alongside scalar outputs, so that I can tell at a glance whether the space-charge iteration converged and how long the run took.
21. As the researcher, I want the app to cover Laplace, Poisson with Gaussian closure, and Poisson with threshold closure — but not the shape optimizer — so that the app stays fast and returns in deterministic time on each button click.
22. As the researcher, I want `plotting.py` (matplotlib, CLI/examples) to remain unchanged in V2, so that existing example scripts continue to work exactly as they do in V1.
23. As the researcher, I want the app's Plotly figure builders to live in `app_backend.py` or a dedicated `app/figures.py`, not in `streamlit_app.py`, so that figure logic is testable and the Streamlit file stays thin.

## Implementation Decisions

- **New modules:** `solver/optimization.py`, `solver/app_backend.py`, `app/__init__.py`, `app/streamlit_app.py`. Optionally `app/figures.py` for Plotly builders if `app_backend.py` grows too large.
- **Modified modules:** `solver/space_charge.py` (add `solve_threshold_shielding()`), `tests/test_electrostatics.py` (add convergence-order test), `tests/test_residual.py` (add residual-decreases test).
- **New test files:** `tests/test_optimization.py`, `tests/test_app_backend.py`.
- **New example scripts:** `examples/05_shape_optimization_demo.py`, `examples/06_threshold_space_charge.py`.
- **Shape parameterization:** analytic cone family with 2–3 scalar shape parameters. Per ADR-0001, spline control points are deferred. The cone-angle parameter is the primary free variable; apex radius and nozzle radius are secondary with box bounds.
- **Optimizer:** `scipy.optimize.minimize(..., method='Powell', bounds=...)`. No smoothness penalty — the analytic family is smooth by construction. Δp is always analytically eliminated (mean-subtraction), never a free variable.
- **Threshold closure:** `solve_threshold_shielding()` reuses the fixed-point iteration loop already in `solve_gaussian_shielding()` — only the `update_rho` function differs. Nodes with `|E| < Ec` are set to exactly zero. Per ADR-0002, this function is never called from within the optimizer in V2.
- **`SolverResult` dataclass:** frozen dataclass in `app_backend.py`. Fields: `phi`, `Er`, `Ez`, `E_mag`, `rho_e`, `interface_R`, `interface_z`, `residual_profile`, `half_angle`, `peak_field`, `rms_residual`, `shielding_metric`, `runtime_s`, `converged`, `iterations`. No `st.*` imports in `app_backend.py`.
- **Plotly figures:** built from `SolverResult` fields. Contour/heatmap for field plots, scatter for interface overlay and residual profile. `streamlit_app.py` calls `st.plotly_chart()` on pre-built figures.
- **App structure:** one `streamlit_app.py` file; basic sidebar + Advanced expander pattern. "Run" button triggers `app_backend.run_solver()`. No session-state caching in V2 (add if performance is a problem).
- **Dependency additions:** `plotly` (app only), `streamlit`. Neither is required for `solver/` or `tests/` — import only inside `app/`.
- **`plotting.py`:** unchanged. No matplotlib → Plotly migration.

## Testing Decisions

- **What makes a good test here:** assert on physically/numerically observable external behavior — convergence order, sign of field, residual direction of change, shielding sign. Do not assert on matrix internals or intermediate dataclass fields that aren't load-bearing for the physics claim.
- **Test files and their seams:**
  - `tests/test_optimization.py`: (a) optimizer recovers a known half-angle on a synthetic residual landscape; (b) Powell converges to ≤ some tolerance on a simple cone-family case; (c) bounds are respected (no parameter leaves its box).
  - `tests/test_app_backend.py`: (a) `run_solver()` returns a `SolverResult` with all fields populated; (b) `SolverResult.half_angle` is finite and in (0°, 90°) for a basic Laplace case.
  - `tests/test_space_charge.py` (extend existing): add threshold closure shielding sanity test — `S_E > 0` for sensible `Ec`, `Es`, `ρ_max`.
  - `tests/test_electrostatics.py` (strengthen): add convergence-order test — L2 error at 2× resolution is ≤ 0.6× the coarse error (second-order halving).
  - `tests/test_residual.py` (strengthen): add residual-decreases test — construct two interfaces, one closer to the equilibrium angle than the other, assert the closer one has lower RMS residual.
- **Prior art:** V1 test files establish the pattern — pytest, one file per solver module, no dense-matrix assertions, physical/numerical claims only. V2 tests should follow the same structure.

## Out of Scope

- Coupling the threshold closure and shape optimizer in a single loop — deferred to V3 per ADR-0002.
- Spline control-point shape parameterization — deferred per ADR-0001.
- Shape optimizer exposed in the Streamlit app — optimizer lives in an example script only in V2; the app covers electrostatics and space-charge diagnostics only.
- Δp as a free optimization variable — always mean-subtracted in V2.
- Session-state caching or async runs in the Streamlit app — V2 app is synchronous and stateless.
- Full leaky-dielectric dynamics, surface charge conservation, current-constrained shielding, experimental image comparison — V3+, gated on hardware approval.
- Any changes to `plotting.py` — explicitly frozen in V2.

## Further Notes

- The optimizer's first validation target is reproducing the 49.3° half-angle in the Laplace limit. If it doesn't converge there, the optimization loop is broken and should be fixed before adding threshold charge or app integration.
- `streamlit` and `plotly` must be added to `requirements.txt` / `pyproject.toml` optional dev deps before the app ticket runs. Pin to specific versions.
- Per `CONTEXT.md`: "residual" always means the YLM pointwise mismatch, not optimizer convergence residual; "interface" always means the graph `R(z)`; "half-angle" is always the absolute-value arctan fit near the apex.
- `/to-tickets` should split along this dependency chain: `space_charge.py threshold` → `test_electrostatics + test_residual strengthen` → `optimization.py + test_optimization` → `app_backend.py + test_app_backend` → `streamlit_app.py + example scripts`. Each ticket blocked on the previous.
