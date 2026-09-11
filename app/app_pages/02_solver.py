"""Solver page - main solver interface with field visualization."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from solver.app_backend import (
    RunParams,
    run_solver,
    solver_run_to_dict,
    write_results_json,
    figure_field_magnitude,
    figure_imposed_taylor_field,
    figure_interface_overlay,
    figure_potential,
    figure_residual_profile,
    figure_space_charge,
)

# Add components directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.parameter_panel import (
    preset_selector,
    geometry_parameters,
    material_parameters,
    grid_parameters,
)
from components.plot_styling import apply_academic_style
from components.theory_boxes import (
    taylor_angle_theory,
    laplace_equation_theory,
    young_laplace_maxwell_theory,
    poisson_space_charge_theory,
    convergence_criteria_theory,
)

# Results directory
RESULTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "backend" / "results"
RESULTS_DIR.mkdir(exist_ok=True)

st.title(" Electrostatic-Capillary Solver")

st.write("""
Configure the solver parameters in the sidebar, then click **Run Solver** to compute the
electrostatic field distribution and evaluate the Young-Laplace-Maxwell residual on a
prescribed conical interface.
""")

# Theory boxes
with st.expander(" Theory and Methods", expanded=False):
    theory_col1, theory_col2 = st.columns(2)
    with theory_col1:
        laplace_equation_theory()
        young_laplace_maxwell_theory()
    with theory_col2:
        poisson_space_charge_theory()
        convergence_criteria_theory()

st.divider()

# Sidebar parameters
with st.sidebar:
    st.header("Solver Configuration")

    # Preset selector
    preset = preset_selector()

    st.divider()

    # Geometry parameters
    with st.expander(" Geometry", expanded=True):
        geom_params = geometry_parameters(preset)

    # Material parameters
    with st.expander("🧪 Materials", expanded=True):
        mat_params = material_parameters(preset)

    # Physics settings
    with st.expander(" Physics", expanded=True):
        st.subheader("Electrostatics")

        V0 = st.number_input(
            "Applied voltage V₀ [kV]",
            min_value=0.5,
            max_value=100.0,
            value=preset["parameters"].get("V0", 2500.0) / 1000.0 if preset else 2.5,
            step=0.1,
            format="%.2f",
            help="Applied potential at the emitter relative to the grounded plate. "
                 "Typical experimental onset voltages: 1–5 kV for ethanol, 2–10 kV for water."
        ) * 1000.0

        st.subheader("Space charge (optional)")

        space_charge_model = st.selectbox(
            "Space-charge model",
            options=["none", "gaussian", "threshold"],
            index=0,
            help="Optional phenomenological space-charge shielding model. "
                 "'none': vacuum electrostatics (Laplace). 'gaussian': Gaussian charge cloud. "
                 "'threshold': field-activated emission model."
        )

        # Space-charge parameters (shown only if model selected)
        if space_charge_model == "gaussian":
            with st.expander("Gaussian model parameters", expanded=True):
                rho0 = st.number_input("ρ₀ [C/m³]", value=1e-9, format="%.2e")
                ell = st.number_input(
                    "ℓ (cloud width) [mm]",
                    value=geom_params["electrode_spacing"] * 0.1 * 1e3,
                    format="%.1f"
                ) * 1e-3
                apex_r = st.number_input("Apex r [mm]", value=0.0, format="%.2f") * 1e-3
                apex_z = st.number_input(
                    "Apex z [mm]",
                    value=geom_params["electrode_spacing"] * 0.8 * 1e3,
                    format="%.2f"
                ) * 1e-3
        else:
            rho0 = ell = apex_r = apex_z = None

        if space_charge_model == "threshold":
            with st.expander("Threshold model parameters", expanded=True):
                E_c = st.number_input("E_c (critical field) [V/m]", value=500.0, format="%.1f")
                E_s = st.number_input("E_s (scale field) [V/m]", value=300.0, format="%.1f")
                rho_max = st.number_input("ρ_max [C/m³]", value=1e-8, format="%.2e")
        else:
            E_c = E_s = rho_max = None

    # Grid parameters
    with st.expander("🔲 Mesh", expanded=True):
        grid_params = grid_parameters(preset, key_prefix="solver")

    # Solver settings
    with st.expander(" Solver Settings", expanded=False):
        st.subheader("Iteration controls")

        relaxation = st.slider(
            "Under-relaxation ω",
            min_value=0.1,
            max_value=1.0,
            value=0.5,
            step=0.05,
            help="Under-relaxation factor for fixed-point iteration. Lower values are "
                 "more stable but slower."
        )

        sc_max_iterations = st.number_input(
            "Max iterations",
            min_value=5,
            max_value=500,
            value=50,
            help="Maximum space-charge fixed-point iterations before reporting divergence."
        )

        st.subheader("Interface for diagnostics")

        interface_half_angle_deg = st.slider(
            "Cone half-angle [°]",
            min_value=1.0,
            max_value=89.0,
            value=preset["parameters"].get("interface_half_angle_deg", 49.3) if preset else 49.3,
            step=0.1,
            help="Half-angle of the prescribed conical interface for residual diagnostics. "
                 "The theoretical Taylor angle is 49.29°."
        )

        taylor_angle_theory()

# Build parameters object
@st.cache_data(max_entries=20)
def _run_solver_cached(params: RunParams):
    """Cache expensive solver runs."""
    return run_solver(params)


params = RunParams(
    V0=V0,
    gamma=mat_params["gamma"],
    electrode_spacing=geom_params["electrode_spacing"],
    nozzle_radius=geom_params["nozzle_radius"],
    nr=grid_params["nr"],
    nz=grid_params["nz"],
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

# Run button
col_run, col_clear = st.columns([3, 1])

with col_run:
    run = st.button(" Run Solver", type="primary")

with col_clear:
    if st.button(" Clear Cache"):
        _run_solver_cached.clear()
        st.success("Cache cleared!", icon="✅")

if run:
    try:
        with st.spinner("Running solver... Computing electrostatic field distribution..."):
            result = _run_solver_cached(params)
    except Exception as exc:
        st.error(f" Solver error: {exc}", icon="❌")
        result = None
    else:
        st.session_state.last_result = result
        st.session_state.last_params = params

        # Save to run history
        from datetime import datetime
        st.session_state.run_history.append({
            'timestamp': datetime.now(),
            'params': params,
            'result': result,
            'type': 'solver'
        })

        # Write results file
        try:
            results_path = write_results_json(
                RESULTS_DIR / "latest_solver_run.json",
                solver_run_to_dict(params, result),
            )
            st.success(f" Solver completed successfully!", icon="✅")
            st.caption(f"Results written to `{results_path}`")
        except Exception as exc:
            st.warning(f" Could not write results file: {exc}", icon="⚠️")

# Display results
result = st.session_state.get("last_result")

if result is None:
    st.info(
        " Configure parameters in the sidebar and click ** Run Solver** to start."
    , icon="ℹ️")
else:
    # Check if parameters changed
    if st.session_state.last_params != params:
        st.warning(
            " Showing results from the previous run — some parameters have changed. "
            "Click ** Run Solver** to recompute."
        , icon="⚠️")

    # Warning for capped angle
    if result.half_angle < params.interface_half_angle_deg - 0.01:
        st.warning(
            f" The requested interface angle {params.interface_half_angle_deg:.1f}° exceeds "
            f"what this domain can fit. Diagnostic ran at capped angle {result.half_angle:.1f}°. "
            f"Increase **Domain radius** to fit steeper cones."
        , icon="⚠️")

    st.divider()

    # CSS for highlighting COMSOL-alternative metrics
    st.markdown("""
    <style>
    .comsol-alternative {
        background: linear-gradient(135deg, #e8f4f8 0%, #d4e9f2 100%);
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 10px;
    }
    .comsol-alternative h4 {
        color: #1f77b4;
        margin-top: 0;
        font-size: 0.9em;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    # Scalar diagnostics
    st.header(" Scalar Diagnostics")

    st.markdown("""
    <div class="comsol-alternative">
    <h4>🔬 COMSOL Alternative Metrics — Key datapoints for scientists using this as a substitute for commercial FEM software</h4>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Interface half-angle",
        f"{result.half_angle:.2f}°",
        help="Prescribed interface angle (input parameter, not a prediction)",
        border=True
    )

    col2.metric(
        "Peak |E|",
        f"{result.peak_field:.3g} V/m",
        help="Maximum electric field magnitude in the domain",
        border=True
    )

    col3.metric(
        "RMS residual",
        f"{result.rms_residual:.3e} Pa",
        help="Root-mean-square Young-Laplace-Maxwell residual on the interface",
        border=True
    )

    shield_str = f"{result.shielding_metric:.4f}" if result.shielding_metric is not None else "—"
    col4.metric(
        "Shielding metric S_E",
        shield_str,
        help="Space-charge shielding metric (ratio of perturbed to vacuum field)",
        border=True
    )

    col5, col6, col7, col8 = st.columns(4)

    col5.metric(
        "Runtime",
        f"{result.runtime_s:.3f} s",
        help="Total solver execution time",
        border=True
    )

    col6.metric(
        "Converged",
        " Yes" if result.converged else "✗ No",
        help="Whether the space-charge iteration converged",
        border=True
    )

    col7.metric(
        "Iterations",
        str(result.iterations),
        help="Number of space-charge fixed-point iterations",
        border=True
    )

    col8.metric(
        "Grid cells",
        f"{params.nr * params.nz:,}",
        help=f"Total mesh size: {params.nr} × {params.nz}",
        border=True
    )

    # Convergence warning
    if not result.converged:
        st.error(
            f" Space-charge iteration did not converge after {result.iterations} iterations. "
            "Try reducing ω or increasing max iterations."
        , icon="❌")

    # Full diagnostics table (copyable)
    with st.expander("📋 Full Diagnostics Table", expanded=False):
        diag_table = {
            "Quantity": [
                "Interface half-angle (input)",
                "Peak |E|",
                "RMS residual",
                "Shielding metric S_E",
                "Runtime",
                "Converged",
                "Iterations",
                "Grid size (nr × nz)",
            ],
            "Value": [
                f"{result.half_angle:.4f} °",
                f"{result.peak_field:.4g} V/m",
                f"{result.rms_residual:.4e} Pa",
                shield_str,
                f"{result.runtime_s:.4f} s",
                "Yes" if result.converged else "No",
                str(result.iterations),
                f"{params.nr} × {params.nz}",
            ],
        }
        st.dataframe(pd.DataFrame(diag_table), hide_index=True)

    st.divider()

    # Field visualizations
    st.header("🗺️ Field Visualizations")

    st.write("""
    The plots below show the computed electrostatic field distribution and diagnostic quantities.
    All figures are interactive—hover for values, zoom, pan, and download using the toolbar.
    """)

    # Row 1: Potential and Field Magnitude (side by side with generous spacing)
    st.subheader("Electric Potential and Field Magnitude")

    col_left, col_spacer1, col_right = st.columns([10, 1, 10])

    with col_left:
        fig_pot = figure_potential(result)
        fig_pot = apply_academic_style(fig_pot, height=550)  # Increased height
        st.plotly_chart(fig_pot)
        st.caption("**Figure 1:** Electric potential φ(r,z). Emitter at top (φ = V₀), ground at bottom (φ = 0).")

    with col_right:
        fig_field = figure_field_magnitude(result)
        fig_field = apply_academic_style(fig_field, height=550)  # Increased height
        st.plotly_chart(fig_field)
        st.caption("**Figure 2:** Electric field magnitude |E| = |∇φ|. Peak field typically at the cone apex.")

    st.divider()

    # Row 2: Interface Overlay and Residual Profile
    st.subheader("Interface Diagnostics")

    col_left2, col_spacer2, col_right2 = st.columns([10, 1, 10])

    with col_left2:
        fig_interface = figure_interface_overlay(result)
        fig_interface = apply_academic_style(fig_interface, height=550)  # Increased height
        st.plotly_chart(fig_interface)
        st.caption("**Figure 3:** Prescribed conical interface overlaid on the potential field.")

    with col_right2:
        fig_residual = figure_residual_profile(result)
        fig_residual = apply_academic_style(fig_residual, height=550)  # Increased height
        st.plotly_chart(fig_residual)
        st.caption("**Figure 4:** Young-Laplace-Maxwell residual along the interface. Small residuals indicate near-equilibrium.")

    st.divider()

    # Row 3: Space Charge (if applicable)
    if space_charge_model != "none":
        st.subheader("Space-Charge Distribution")

        # Center this plot with extra spacing
        col_sc_left, col_sc_center, col_sc_right = st.columns([2, 10, 2])

        with col_sc_center:
            fig_sc = figure_space_charge(result)
            fig_sc = apply_academic_style(fig_sc, height=550)  # Increased height
            st.plotly_chart(fig_sc)
            st.caption("**Figure 5:** Space-charge density ρ(r,z). Shows ion cloud distribution that shields the electric field.")

    st.divider()

    # Export section
    st.header("💾 Export Results")

    export_col1, export_col2, export_col3 = st.columns(3)

    with export_col1:
        st.download_button(
            label="📥 Download JSON",
            data=str(solver_run_to_dict(params, result)),
            file_name="solver_results.json",
            mime="application/json"
        )

    with export_col2:
        if st.button("📋 Copy Parameters"):
            st.code(f"""
V0 = {V0/1000:.2f} kV
gamma = {mat_params['gamma']*1e3:.1f} mN/m
electrode_spacing = {geom_params['electrode_spacing']*1e3:.1f} mm
nozzle_radius = {geom_params['nozzle_radius']*1e3:.1f} mm
grid = {params.nr} × {params.nz}
angle = {interface_half_angle_deg:.2f}°
            """)

    with export_col3:
        st.caption(" More export formats coming soon: HDF5, VTK, LaTeX tables")

st.divider()

# Tips
with st.expander(" Tips and Best Practices", expanded=False):
    st.markdown("""
    **Getting good results:**
    - Start with a preset configuration for typical fluids
    - Use Medium grid for exploration, Fine for publication-quality results
    - Keep the domain roughly square (electrode spacing ≈ nozzle radius)
    - The prescribed angle should be near 49.3° for Taylor cone diagnostics

    **Interpreting results:**
    - **Low RMS residual** (< 1 Pa): Good balance between electric and capillary forces
    - **Peak field** location: Should be near the cone apex
    - **Convergence**: Essential for space-charge models; divergence indicates unstable parameters

    **Troubleshooting:**
    - If solver doesn't converge: reduce ω (try 0.3), increase max iterations
    - If results look unphysical: check that space-charge parameters are reasonable
    - If computation is slow: reduce grid resolution for initial exploration
    """)
