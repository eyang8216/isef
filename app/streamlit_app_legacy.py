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

    gamma = st.number_input("Surface tension γ [mN/m]", min_value=15.0, max_value=72.0,
                            value=22.0, step=1.0, format="%.1f",
                            help="Surface tension of the working fluid. Determines the capillary "
                                 "pressure scale γκ. Common values: Ethanol ≈ 22 mN/m, Water ≈ "
                                 "72 mN/m, Formamide ≈ 58 mN/m. This affects the balance between "
                                 "electrostatic and capillary forces.") * 1e-3
    electrode_spacing = st.number_input("Electrode spacing [mm]", min_value=0.5, max_value=50.0,
                                        value=10.0, step=1.0, format="%.1f",
                                        help="Distance from emitter tip to grounded counter-electrode. "
                                             "Sets the domain height (z_max). Typical experimental "
                                             "values: 10–50 mm for benchtop electrospray, 1–5 mm for "
                                             "microdevices. NOTE: this is a model geometry parameter, "
                                             "not a prescription for optimal experimental spacing.") * 1e-3
    nozzle_radius = st.number_input("Nozzle / domain radius [mm]", min_value=0.5, max_value=50.0,
                                    value=10.0, step=1.0, format="%.1f",
                                    help="Radial extent of the computational domain (r_max) and "
                                         "initial nozzle outer radius. Should be large enough to "
                                         "minimize radial boundary effects on the solution. For a "
                                         "square domain, set equal to the electrode spacing.") * 1e-3

    space_charge_model = st.selectbox(
        "Space-charge model",
        options=["none", "gaussian", "threshold"],
        index=0,
        help="Optional phenomenological space-charge shielding model to account for ion emission. "
             "'none': vacuum electrostatics (Laplace equation). 'gaussian': Gaussian charge "
             "distribution with exponential decay. 'threshold': field-threshold activation model.",
    )

    # ---------------------------------------------------------------------------
    # Advanced expander
    # ---------------------------------------------------------------------------
    with st.expander("Advanced", expanded=False):
        st.subheader("Space-charge closure parameters")

        if space_charge_model == "gaussian":
            rho0 = st.number_input("ρ₀ [C/m³]", value=1e-9, format="%.2e")
            ell = st.number_input("ℓ (cloud width) [mm]", value=electrode_spacing * 0.1 * 1e3, format="%.1f") * 1e-3
            apex_r = st.number_input("Apex r [mm]", value=0.0, format="%.2f") * 1e-3
            apex_z = st.number_input("Apex z [mm]", value=electrode_spacing * 0.8 * 1e3, format="%.2f") * 1e-3
        else:
            rho0 = ell = apex_r = apex_z = None

        if space_charge_model == "threshold":
            E_c = st.number_input("E_c (critical field) [V/m]", value=500.0, format="%.1f")
            E_s = st.number_input("E_s (scale field) [V/m]", value=300.0, format="%.1f")
            rho_max = st.number_input("ρ_max [C/m³]", value=1e-8, format="%.2e")
        else:
            E_c = E_s = rho_max = None

        st.subheader("Iteration controls")
        relaxation = st.slider("Under-relaxation ω", min_value=0.1, max_value=1.0, value=0.5, step=0.05,
                               help="Under-relaxation factor for the fixed-point iteration. Lower "
                                    "values are more stable but slower; raise only if the iteration "
                                    "fails to move.")
        sc_max_iterations = st.number_input("Max iterations", min_value=5, max_value=500, value=50,
                                            help="Cap on space-charge fixed-point iterations before "
                                                 "reporting divergence.")

        st.subheader("Interface for residual diagnostics")
        interface_half_angle_deg = st.slider("Cone half-angle [°]", min_value=1.0, max_value=89.0,
                                             value=49.3, step=0.1,
                                             help="Half-angle of the prescribed conical interface used "
                                                  "for residual diagnostics. The theoretical Taylor "
                                                  "angle is 49.29°. This is an INPUT parameter for "
                                                  "diagnostics, not a prediction from the solver.")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_classic, tab_verif = st.tabs(["Classic diagnostics", "Immersed verification"])

# ---------------------------------------------------------------------------
# Tab 1 — classic diagnostics (legacy fixed-V0 residual on a prescribed cone)
# ---------------------------------------------------------------------------
with tab_classic:
    st.subheader("Classic solver parameters")

    V0 = st.number_input("Voltage V₀ [kV]", min_value=0.5, max_value=100.0, value=2.5, step=0.1,
                         format="%.2f",
                         help="Applied potential at the emitter relative to the grounded plate. "
                              "Typical experimental onset voltages: 1–5 kV for ethanol, 2–10 kV for water. "
                              "Higher voltages increase electric field strength and Maxwell stress. "
                              "Only used by the Classic diagnostics tab.") * 1000.0
    grid_res = st.select_slider("Grid resolution (nr × nz)",
                                options=["Coarse (21×31)", "Medium (31×51)", "Fine (41×71)"],
                                value="Medium (31×51)",
                                help="Finite-difference grid resolution (radial × axial). Higher "
                                     "resolution improves accuracy but increases computation time. "
                                     "Coarse: quick tests, Medium: routine work, Fine: "
                                     "publication quality. Independent from the verification grid.",
                                key="classic_grid")
    _grid_map = {
        "Coarse (21×31)": (21, 31),
        "Medium (31×51)": (31, 51),
        "Fine (41×71)": (41, 71),
    }
    nr, nz = _grid_map[grid_res]

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
        "**Recovered angle** is the half-angle at which the flank field's power-law exponent "
        "crosses the balance condition (Taylor far-field recovers ≈49.2° at the Fine grid; "
        "the grounded box falls back to the ~43–46° truncation artifact). The **Taylor identity** "
        "imposes the exact analytic Taylor potential and checks the projected onset voltage "
        "against the analytic balance amplitude (ratio ≈1.000 = exact match)."
    )

    # Electrode spacing is shared from the sidebar (single source of truth for both
    # tabs). The verification domain is a square of side = electrode_spacing, apex at
    # 0.86×spacing, and the default apex radius is 0.5% of spacing — all derived here.
    verif_apex_um = st.number_input("Apex radius [μm]", min_value=10.0, max_value=2000.0,
                                    value=electrode_spacing * 0.005 * 1e6, step=10.0, format="%.0f",
                                    help="Rounding radius at the cone apex to avoid singular "
                                         "fields. Default 50 μm = 0.5% of the electrode spacing "
                                         "(standard practice). Smaller values approach the "
                                         "sharp-cone limit but require finer grids near the apex.")

    # COMMENTED OUT: Grounded BC option (negative control, kept for easy reversion).
    # The grounded box (φ=0 at all outer boundaries) is a negative control that demonstrates
    # the finite-box truncation artifact (recovers ~43–46° instead of the Taylor 49.29°).
    # It is educational only and not needed for routine verification. To restore the option,
    # uncomment the radio below and delete the fixed assignment.
    # verif_bc = st.radio(
    #     "Outer boundary condition",
    #     options=["Taylor far-field", "Grounded box"],
    #     index=0,
    #     help="Taylor far-field: analytical Taylor potential at the boundary (recovers ≈49.2°). "
    #          "Grounded box: φ=0 at the boundary (recovers the ~43° truncation artifact).",
    # )
    # verif_bc_type = "taylor_farfield" if verif_bc == "Taylor far-field" else "grounded"
    verif_bc_type = "taylor_farfield"  # Always use the primary test (Taylor far-field BC)

    st.caption(
        "The verification uses the **Taylor far-field** boundary condition: the exact analytical "
        "Taylor potential is imposed on the outer boundary. This is the correct verification test "
        "(recovers ≈49.2° → 49.29°). A \"grounded\" option (all boundaries at φ=0) exists in the "
        "code as a negative control to demonstrate truncation artifacts but is commented out for "
        "clarity."
    )

    verif_grid = st.select_slider(
        "Grid resolution (nr × nz)",
        options=["Fast (31×45)", "Default (61×89)", "Fine (121×177)", "Very Fine (241×353)"],
        value="Fine (121×177)",
        help="Grid resolution for the angle sweep. Higher grids reduce discretization error. "
             "Fast: ≈49.1° recovered angle, Fine: ≈49.2°, Very Fine: ≈49.23° (approaching "
             "theoretical 49.29°). Use Fine (121×177) for standard verification, Very Fine for "
             "convergence studies.",
    )
    _verif_grid_map = {
        "Fast (31×45)": (31, 45),
        "Default (61×89)": (61, 89),
        "Fine (121×177)": (121, 177),
        "Very Fine (241×353)": (241, 353),
    }
    verif_nr, verif_nz = _verif_grid_map[verif_grid]

    run_verif = st.button("Run immersed verification", type="primary",
                          icon=":material/experiment:")

    if run_verif:
        verif_params = ImmersedVerificationParams(
            nr=verif_nr, nz=verif_nz,
            electrode_spacing=electrode_spacing,
            apex_z=0.86 * electrode_spacing,
            apex_radius=verif_apex_um * 1e-6,
            bc_type=verif_bc_type,
        )
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
        col1.metric("Recovered angle", f"{verif.recovered_angle_deg:.2f}°",
                    help="Half-angle where the flank field exponent E_n² ~ ρ^p crosses p = -1, "
                         "the scale-consistency condition of the Young-Laplace-Maxwell balance "
                         "under the selected outer boundary condition (Taylor reference 49.29°).",
                    border=True)
        st.caption(f"Recovered-angle method: {verif.recovered_angle_method}")
        onset_str = f"{verif.onset_voltage_V / 1e3:.2f} kV" if verif.onset_voltage_V else "—"
        col2.metric("Predicted onset voltage V0*", onset_str,
                    help="Amplitude projected out of the residual, reported as a voltage.",
                    border=True)
        col3.metric("Min residual", f"{verif.min_rms_Pa:.3e} Pa", border=True)

        col4, col5 = st.columns(2)
        col4.metric("Taylor identity ratio V0*/A*", f"{verif.identity_ratio:.4f}" if verif.identity_ratio else "—",
                    help="Ratio of the projected onset voltage to the analytic balance amplitude at the Taylor angle. 1.0 = exact match (measured ~1.000 at Fine grid).",
                    border=True)
        col5.metric("Identity exponent crossing", f"{verif.identity_exponent_crossing_deg:.2f}°" if verif.identity_exponent_crossing_deg else "—",
                    help="Half-angle where the flank exponent crosses p = -1 under the imposed Taylor potential (~49.2°).",
                    border=True)

        col_land, col_field = st.columns(2)
        with col_land:
            st.plotly_chart(figure_verification_landscape(verif))
        with col_field:
            st.plotly_chart(figure_imposed_taylor_field(verif))

        st.caption(f"Runtime: {verif.runtime_s:.1f} s. "
                   "Taylor far-field removes the finite-box truncation artifact: the flank "
                   "exponent crossing recovers ≈49.2° at the Fine grid (49.29° ideal). "
                   "The grounded box falls back to the truncated-cone-in-a-box angle (~43–46°). "
                   "The imposed-Taylor identity is the committed verification of the machinery "
                   "against 49.29° (tests/test_taylor_onset.py).")
