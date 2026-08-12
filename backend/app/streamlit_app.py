"""Streamlit app for the Taylor-cone electrostatic-capillary solver.

Two-tier sidebar: basic physical inputs visible by default, advanced
closure/tuning inputs in an expander. Run button triggers run_solver()
via app_backend. Plotting via Plotly — no matplotlib in this file.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

from solver.app_backend import (
    ImmersedVerificationParams,
    RunParams,
    SolverResult,
    figure_field_magnitude,
    figure_imposed_taylor_field,
    figure_interface_overlay,
    figure_potential,
    figure_residual_profile,
    figure_space_charge,
    figure_verification_landscape,
    run_immersed_verification,
    run_solver,
    solver_run_to_dict,
    verification_run_to_dict,
    write_results_json,
)

# Directory for agent-facing results files (repo-root/results, same convention
# as scripts/generate_v1_report.py).
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"

st.set_page_config(
    page_title="Taylor-Cone Solver",
    page_icon=":material/science:",
    layout="wide",
)
st.title("Axisymmetric Electrostatic-Capillary Solver")
st.caption(
    "Reduced-order Taylor-cone solver — Laplace / Poisson with space-charge shielding. "
    "The Immersed verification tab exercises the immersed free-boundary machinery "
    "(recovered angle, onset voltage, and the imposed-Taylor amplitude identity)."
)

# ---------------------------------------------------------------------------
# Session state — keep the last run around so results survive sidebar tweaks
# ---------------------------------------------------------------------------
st.session_state.setdefault("last_result", None)
st.session_state.setdefault("last_params", None)
st.session_state.setdefault("last_verification", None)


@st.cache_data(max_entries=20)
def _run_solver_cached(params: RunParams) -> SolverResult:
    """Cache the expensive solver run keyed by the full parameter set."""
    return run_solver(params)


@st.cache_data(max_entries=10)
def _run_verification_cached(params: ImmersedVerificationParams) -> "ImmersedVerificationResult":
    """Cache the immersed verification run keyed by the parameter set."""
    return run_immersed_verification(params)


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
                                     value=1.0, format="%.3f")
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

tab_classic, tab_verif = st.tabs(["Classic diagnostics", "Immersed verification"])

# ---------------------------------------------------------------------------
# Tab 1 — classic diagnostics (legacy fixed-V0 residual on a prescribed cone)
# ---------------------------------------------------------------------------
with tab_classic:
    run = st.button("Run solver", type="primary", icon=":material/play_arrow:")

    if run:
        try:
            with st.spinner("Running solver…"):
                result = _run_solver_cached(params)
        except Exception as exc:
            st.error(f"Solver error: {exc}", icon=":material/error:")
            result = None
        else:
            st.session_state.last_result = result
            st.session_state.last_params = params
            try:
                results_path = write_results_json(
                    RESULTS_DIR / "latest_solver_run.json",
                    solver_run_to_dict(params, result),
                )
            except Exception as exc:
                st.warning(f"Could not write results file: {exc}", icon=":material/warning:")
            else:
                st.caption(f"Results written to `{results_path}` — full input parameters "
                           "and output summaries in JSON for agent consumption.")

    result = st.session_state.get("last_result")

    if result is None:
        st.info("Set parameters in the sidebar and click **Run solver** to start.",
                icon=":material/info:")
    else:
        if st.session_state.last_params != params:
            st.caption("Showing results from the previous run — some parameters have changed. "
                       "Click **Run solver** to recompute.")

        if result.half_angle < params.interface_half_angle_deg - 0.01:
            st.warning(
                f"The requested interface angle {params.interface_half_angle_deg:.1f}° exceeds "
                f"what this domain can fit, so the diagnostic ran at the capped angle "
                f"{result.half_angle:.1f}°. Increase **Domain radius** (or reduce the angle) "
                f"to fit steeper cones.",
                icon=":material/warning:",
            )

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

        st.subheader("Field plots")
        col_left, col_right = st.columns(2)
        with col_left:
            st.plotly_chart(figure_potential(result))
            st.plotly_chart(figure_interface_overlay(result))
            st.plotly_chart(figure_space_charge(result))
        with col_right:
            st.plotly_chart(figure_field_magnitude(result))
            st.plotly_chart(figure_residual_profile(result))

# ---------------------------------------------------------------------------
# Tab 2 — immersed verification (P2 onset projection + P3i Taylor identity)
# ---------------------------------------------------------------------------
with tab_verif:
    st.caption(
        "Exercises the immersed free-boundary machinery: the cone is the powered boundary "
        "of its own Laplace solve and the residual projects out the onset voltage. "
        "**Recovered angle** is the half-angle minimising the amplitude-projected residual "
        "on the grounded box; the **Taylor identity** imposes the exact analytic Taylor "
        "potential and checks the projected onset voltage against the analytic balance "
        "amplitude (ratio ~1.0 = exact match)."
    )

    verif_grid = st.select_slider(
        "Grid resolution (nr × nz)",
        options=["Fast (31×45)", "Default (61×89)", "Fine (121×177)"],
        value="Default (61×89)",
    )
    _verif_grid_map = {
        "Fast (31×45)": (31, 45),
        "Default (61×89)": (61, 89),
        "Fine (121×177)": (121, 177),
    }
    verif_nr, verif_nz = _verif_grid_map[verif_grid]

    run_verif = st.button("Run immersed verification", type="primary",
                          icon=":material/experiment:")

    if run_verif:
        verif_params = ImmersedVerificationParams(nr=verif_nr, nz=verif_nz)
        try:
            with st.spinner("Running immersed verification…"):
                verif = _run_verification_cached(verif_params)
        except Exception as exc:
            st.error(f"Verification error: {exc}", icon=":material/error:")
            verif = None
        else:
            st.session_state.last_verification = verif
            try:
                results_path = write_results_json(
                    RESULTS_DIR / "latest_verification_run.json",
                    verification_run_to_dict(verif_params, verif),
                )
            except Exception as exc:
                st.warning(f"Could not write results file: {exc}", icon=":material/warning:")
            else:
                st.caption(f"Results written to `{results_path}` — full input parameters "
                           "and output summaries in JSON for agent consumption.")

    verif = st.session_state.get("last_verification")

    if verif is None:
        st.info("Click **Run immersed verification** to compute the recovered angle, "
                "onset voltage, and the imposed-Taylor amplitude identity.",
                icon=":material/info:")
    else:
        if verif.grid_r.size != verif_nr or verif.grid_z.size != verif_nz:
            st.caption("Showing results from the previous run — the grid has changed. "
                       "Click **Run immersed verification** to recompute.")

        st.subheader("Verification diagnostics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Recovered angle (grounded box)", f"{verif.recovered_angle_deg:.2f}°",
                    help="Half-angle minimising the amplitude-projected residual "
                         "(Taylor reference value 49.29° — see caption below).",
                    border=True)
        onset_str = f"{verif.onset_voltage_V / 1e3:.2f} kV" if verif.onset_voltage_V else "—"
        col2.metric("Predicted onset voltage V0*", onset_str,
                    help="Amplitude projected out of the residual, reported as a voltage.",
                    border=True)
        col3.metric("Min residual", f"{verif.min_rms_Pa:.3e} Pa", border=True)

        col4, col5 = st.columns(2)
        col4.metric("Taylor identity ratio V0*/A*", f"{verif.identity_ratio:.4f}" if verif.identity_ratio else "—",
                    help="Ratio of the projected onset voltage to the analytic balance amplitude at the Taylor angle. 1.0 = exact match (measured ~1.01).",
                    border=True)
        col5.metric("Identity residual argmin", f"{verif.identity_argmin_deg:.1f}°" if verif.identity_argmin_deg else "—",
                    help="Half-angle of minimum projected residual under the imposed Taylor potential.",
                    border=True)

        col_land, col_field = st.columns(2)
        with col_land:
            st.plotly_chart(figure_verification_landscape(verif))
        with col_field:
            st.plotly_chart(figure_imposed_taylor_field(verif))

        st.caption(f"Runtime: {verif.runtime_s:.1f} s. "
                   "The grounded-box angle is the answer of the truncated-cone-in-a-box "
                   "problem (not Taylor's meniscus limit — see examples/09_ideal_limit_study.py); "
                   "the imposed-Taylor identity is the committed verification of the machinery "
                   "against 49.29° (tests/test_taylor_onset.py).")
