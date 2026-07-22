# 04 — App backend

**What to build:** Create `solver/app_backend.py` with a single `run_solver(params) -> SolverResult` entry point and a frozen `SolverResult` dataclass, add Plotly figure builders (in `app_backend.py` or `app/figures.py`), and add `tests/test_app_backend.py`.

`run_solver()` accepts UI parameter values, calls the solver modules (grid, geometry, electrostatics, fields, interface, residual, space_charge as appropriate), and returns a `SolverResult`. The app layer must have no direct dependency on numpy arrays or solver internals — it only sees `SolverResult`.

`SolverResult` is a frozen dataclass with fields: `phi`, `Er`, `Ez`, `E_mag`, `rho_e`, `interface_R`, `interface_z`, `residual_profile`, `half_angle`, `peak_field`, `rms_residual`, `shielding_metric`, `runtime_s`, `converged`, `iterations`.

`app_backend.py` must contain no `st.*` imports — it is plain Python, testable with pytest without a Streamlit session. Plotly figure builders take a `SolverResult` and return `plotly.graph_objects.Figure` objects; `streamlit_app.py` will call `st.plotly_chart()` on them.

Pin `plotly` to a specific version in `requirements.txt` and `pyproject.toml` in this ticket (it's needed here before `streamlit` in ticket 05).

**Blocked by:** 03 — shape optimizer

**Status:** completed

- [ ] `solver/app_backend.py` created with `run_solver(params) -> SolverResult`
- [ ] `SolverResult` frozen dataclass with all specified fields
- [ ] No `st.*` imports anywhere in `app_backend.py`
- [ ] Plotly figure builders for: potential contour, field magnitude, interface overlay, residual profile, space-charge density
- [ ] `tests/test_app_backend.py`: (a) `run_solver()` returns `SolverResult` with all fields populated; (b) `half_angle` is finite and in (0°, 90°) for a basic Laplace case
- [ ] `plotly` pinned in `requirements.txt` and `pyproject.toml`
- [ ] All tests pass
