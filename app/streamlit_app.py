"""Streamlit app for the Taylor-cone electrostatic-capillary solver.

Two-tier sidebar: basic physical inputs visible by default, advanced
closure/tuning inputs in an expander. Run button triggers run_solver()
via app_backend. Plotting via Plotly — no matplotlib in this file.
"""

import pandas as pd
import streamlit as st

from solver.app_backend import (
    RunParams,
    SolverResult,
    figure_field_magnitude,
    figure_interface_overlay,
    figure_potential,
    figure_residual_profile,
    figure_space_charge,
    run_solver,
)

st.set_page_config(
    page_title="Taylor-Cone Solver",
    page_icon=":material/science:",
    layout="wide",
)
st.title("Axisymmetric Electrostatic-Capillary Solver")
st.caption(
    "Reduced-order Taylor-cone solver — Laplace / Poisson with space-charge shielding. "
    "Shape optimisation is available via the CLI example scripts."
)

# ---------------------------------------------------------------------------
# Session state — keep the last run around so results survive sidebar tweaks
# ---------------------------------------------------------------------------
st.session_state.setdefault("last_result", None)
st.session_state.setdefault("last_params", None)


@st.cache_data(max_entries=20)
def _run_solver_cached(params: RunParams) -> SolverResult:
    """Cache the expensive solver run keyed by the full parameter set."""
    return run_solver(params)


# ---------------------------------------------------------------------------
# Sidebar — basic inputs
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Basic parameters")

    V0 = st.number_input("Voltage V₀ [V]", min_value=1.0, max_value=1e6, value=1000.0, step=100.0)
    gamma = st.number_input("Surface tension γ [N/m]", min_value=1e-4, max_value=1.0,
                             value=0.022, format="%.4f")
    electrode_spacing = st.number_input("Electrode spacing [m]", min_value=0.01, max_value=10.0,
                                         value=1.0, format="%.3f")
    nozzle_radius = st.number_input("Domain radius [m]", min_value=0.01, max_value=10.0,
                                     value=0.5, format="%.3f")
    grid_res = st.select_slider("Grid resolution (nr × nz)",
                                 options=["Coarse (21×31)", "Medium (31×51)", "Fine (41×71)"],
                                 value="Medium (31×51)")
    _grid_map = {
        "Coarse (21×31)": (21, 31),
        "Medium (31×51)": (31, 51),
        "Fine (41×71)": (41, 71),
    }
    nr, nz = _grid_map[grid_res]

    space_charge_model = st.selectbox(
        "Space-charge model",
        options=["none", "gaussian", "threshold"],
        index=0,
    )

    # ---------------------------------------------------------------------------
    # Advanced expander
    # ---------------------------------------------------------------------------
    with st.expander("Advanced", expanded=False):
        st.subheader("Space-charge closure parameters")

        if space_charge_model == "gaussian":
            rho0 = st.number_input("ρ₀ [C/m³]", value=1e-9, format="%.2e")
            ell = st.number_input("ℓ (cloud width) [m]", value=0.1, format="%.3f")
            apex_r = st.number_input("Apex r [m]", value=0.0, format="%.3f")
            apex_z = st.number_input("Apex z [m]", value=electrode_spacing * 0.8, format="%.3f")
        else:
            rho0 = ell = apex_r = apex_z = None

        if space_charge_model == "threshold":
            E_c = st.number_input("E_c (critical field) [V/m]", value=500.0, format="%.1f")
            E_s = st.number_input("E_s (scale field) [V/m]", value=300.0, format="%.1f")
            rho_max = st.number_input("ρ_max [C/m³]", value=1e-8, format="%.2e")
        else:
            E_c = E_s = rho_max = None

        st.subheader("Iteration controls")
        relaxation = st.slider("Under-relaxation ω", min_value=0.1, max_value=1.0, value=0.5, step=0.05)
        sc_max_iterations = st.number_input("Max iterations", min_value=5, max_value=500, value=50)

        st.subheader("Interface for residual diagnostics")
        interface_half_angle_deg = st.slider("Cone half-angle [°]", min_value=1.0, max_value=89.0,
                                              value=49.3, step=0.1)

# ---------------------------------------------------------------------------
# Run button
# ---------------------------------------------------------------------------
params = RunParams(
    V0=V0,
    gamma=gamma,
    electrode_spacing=electrode_spacing,
    nozzle_radius=nozzle_radius,
    nr=nr,
    nz=nz,
    space_charge_model=space_charge_model,
    rho0=rho0,
    ell=ell,
    apex_r=apex_r,
    apex_z=apex_z,
    E_c=E_c,
    E_s=E_s,
    rho_max=rho_max,
    relaxation=relaxation,
    sc_max_iterations=sc_max_iterations,
    interface_half_angle_deg=interface_half_angle_deg,
)

run = st.button("Run solver", type="primary", icon=":material/play_arrow:")

if run:
    try:
        with st.spinner("Running solver…"):
            result = _run_solver_cached(params)
    except Exception as exc:
        st.error(f"Solver error: {exc}", icon=":material/error:")
        st.stop()
    st.session_state.last_result = result
    st.session_state.last_params = params

result = st.session_state.get("last_result")

if result is None:
    st.info("Set parameters in the sidebar and click **Run solver** to start.",
            icon=":material/info:")
    st.stop()

# ---------------------------------------------------------------------------
# Scalar diagnostics
# ---------------------------------------------------------------------------
if st.session_state.last_params != params:
    st.caption("Showing results from the previous run — some parameters have changed. "
               "Click **Run solver** to recompute.")

st.subheader("Scalar diagnostics")
col1, col2, col3 = st.columns(3)
col1.metric("Interface half-angle (input)", f"{result.half_angle:.2f}°",
            help="Angle of the prescribed interface used for residual diagnostics — not a predicted value. Change via the Advanced slider.",
            border=True)
col2.metric("Peak |E|", f"{result.peak_field:.3g} V/m", border=True)
col3.metric("RMS residual", f"{result.rms_residual:.3e} Pa", border=True)

col4, col5, col6 = st.columns(3)
shield_str = f"{result.shielding_metric:.4f}" if result.shielding_metric is not None else "—"
col4.metric("Shielding metric S_E", shield_str, border=True)
col5.metric("Runtime", f"{result.runtime_s:.3f} s", border=True)
col6.metric("Converged", "Yes" if result.converged else "No", border=True)

# Full diagnostics table (copyable/readable)
diag_table = {
    "Quantity": ["Interface half-angle (input)", "Peak |E|", "RMS residual", "Shielding metric S_E",
                 "Runtime", "Converged", "Iterations"],
    "Value": [
        f"{result.half_angle:.4f} °",
        f"{result.peak_field:.4g} V/m",
        f"{result.rms_residual:.4e} Pa",
        shield_str,
        f"{result.runtime_s:.4f} s",
        "Yes" if result.converged else "No",
        str(result.iterations),
    ],
}
st.dataframe(pd.DataFrame(diag_table), hide_index=True)

if not result.converged:
    st.warning(f"Space-charge iteration did not converge ({result.iterations} iterations). "
                "Try reducing ω or increasing max iterations.")

# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------
st.subheader("Field plots")
col_left, col_right = st.columns(2)
with col_left:
    st.plotly_chart(figure_potential(result))
    st.plotly_chart(figure_interface_overlay(result))
    st.plotly_chart(figure_space_charge(result))
with col_right:
    st.plotly_chart(figure_field_magnitude(result))
    st.plotly_chart(figure_residual_profile(result))
