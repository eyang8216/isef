# 05 — Streamlit app and dependency pinning

**What to build:** Create `app/streamlit_app.py` with a two-tier sidebar (basic inputs + Advanced expander), a Run button, Plotly charts rendered via `st.plotly_chart()`, and a scalar diagnostics table. Pin `streamlit` to a specific version. The app covers Laplace, Poisson with Gaussian closure, and Poisson with threshold closure — not the shape optimizer.

Basic sidebar inputs: voltage, surface tension, electrode spacing, nozzle radius, grid resolution, space-charge model (none / Gaussian / threshold).

Advanced expander inputs: closure parameters (`ρ₀`, `ℓ`, `Ec`, `Es`, `ρ_max`, under-relaxation `ω`) and BC tuning knobs.

On Run button click: call `app_backend.run_solver(params)`, display the five Plotly figures from ticket 04, and show a scalar diagnostics table (half-angle, peak field, RMS residual, shielding metric, runtime, convergence status).

`streamlit_app.py` must stay thin — no figure logic, no solver calls except through `app_backend.run_solver()`. `plotting.py` is unchanged (matplotlib, CLI only).

**Blocked by:** 04 — app backend

**Status:** completed

- [ ] `app/__init__.py` created
- [ ] `app/streamlit_app.py` created with basic sidebar (6 inputs) and Advanced expander
- [ ] Run button triggers `app_backend.run_solver()` and displays results
- [ ] Five Plotly charts rendered via `st.plotly_chart()`
- [ ] Scalar diagnostics table displayed (half-angle, peak field, RMS residual, shielding metric, runtime, convergence status)
- [ ] App covers Laplace, Gaussian, and threshold cases; optimizer not exposed
- [ ] `streamlit` pinned in `requirements.txt` and `pyproject.toml`
- [ ] `plotting.py` unchanged; all existing example scripts still run
- [ ] All solver/tests pass (`streamlit` not imported in `solver/` or `tests/`)
