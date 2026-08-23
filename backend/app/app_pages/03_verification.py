"""Verification page - immersed boundary verification and angle recovery."""

import sys
from pathlib import Path

import streamlit as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from solver.app_backend import (
    ImmersedVerificationParams,
    run_immersed_verification,
    verification_run_to_dict,
    write_results_json,
    figure_verification_landscape,
    figure_imposed_taylor_field,
)

# Add components directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.plot_styling import apply_academic_style
from components.theory_boxes import immersed_boundary_theory, taylor_angle_theory

# Results directory
RESULTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "backend" / "results"
RESULTS_DIR.mkdir(exist_ok=True)

st.title("✓ Immersed Boundary Verification")

st.write("""
This verification suite exercises the immersed free-boundary machinery: the cone is the powered
boundary of its own Laplace solve, and the residual projects out the onset voltage.
""")

# Theory
with st.expander("📚 Theory: Immersed Boundary Method", expanded=False):
    immersed_boundary_theory()
    taylor_angle_theory()

st.divider()

# Explanation
st.header("What This Test Does")

col_test1, col_test2 = st.columns(2)

with col_test1:
    st.subheader("🎯 Recovered Angle Test")
    st.write("""
    **Objective:** Verify that the solver correctly identifies the Taylor angle (49.29°).

    **Method:**
    1. Sweep cone half-angle from ~30° to ~60°
    2. At each angle, solve Laplace equation with the cone as a powered boundary
    3. Measure the flank field's power-law exponent: E_n² ∝ ρ^p
    4. Find where p = -1 (scale-consistency condition)

    **Expected result:** Recovered angle ≈ 49.2° (approaching 49.29° with grid refinement)
    """)

with col_test2:
    st.subheader("📐 Taylor Identity Test")
    st.write("""
    **Objective:** Verify onset voltage projection against analytical solution.

    **Method:**
    1. Impose the exact analytical Taylor potential on the cone and outer boundary
    2. Compute the Young-Laplace-Maxwell residual
    3. Project the onset voltage amplitude from the residual
    4. Compare to the known analytical amplitude A*

    **Expected result:** Ratio V₀*/A* ≈ 1.000 (exact match within discretization error)
    """)

st.divider()

# Sidebar parameters
with st.sidebar:
    st.header("Verification Configuration")

    st.write("""
    The verification uses a square domain with the electrode spacing from the **Solver** page.
    Adjust the parameters below to configure the verification run.
    """)

    st.divider()

    # Get electrode spacing from solver params or use default
    electrode_spacing = st.session_state.get("last_params")
    if electrode_spacing:
        electrode_spacing = electrode_spacing.electrode_spacing
    else:
        electrode_spacing = 0.010  # Default 10 mm

    st.metric(
        "Electrode spacing",
        f"{electrode_spacing * 1e3:.1f} mm",
        help="Inherited from Solver configuration. The verification domain is a square of this side length.",
        border=True
    )

    st.subheader("Geometry")

    verif_apex_um = st.number_input(
        "Apex radius [μm]",
        min_value=10.0,
        max_value=2000.0,
        value=electrode_spacing * 0.005 * 1e6,  # Default 0.5% of spacing
        step=10.0,
        format="%.0f",
        help="Rounding radius at the cone apex to avoid singular fields. Default 0.5% of "
             "electrode spacing (standard practice). Smaller values approach the sharp-cone limit."
    )

    st.subheader("Boundary Condition")

    st.info("""
    **Taylor far-field** boundary condition is used: the exact analytical Taylor potential
    is imposed on the outer boundary. This is the correct verification test (recovers ≈49.2° → 49.29°).
    """, icon="ℹ️")

    verif_bc_type = "taylor_farfield"  # Always use Taylor far-field

    st.caption("""
    A "grounded box" option (φ=0 at all boundaries) exists in the code as a negative control
    to demonstrate truncation artifacts, but is not exposed in this interface.
    """)

    st.subheader("Mesh")

    verif_grid = st.select_slider(
        "Grid resolution (nr × nz)",
        options=["Fast (31×45)", "Default (61×89)", "Fine (121×177)", "Very Fine (241×353)"],
        value="Fine (121×177)",
        help="Grid resolution for the angle sweep. Higher grids reduce discretization error. "
             "Fast: ≈49.1° recovered angle, Fine: ≈49.2°, Very Fine: ≈49.23° (approaching 49.29°)."
    )

    verif_grid_map = {
        "Fast (31×45)": (31, 45),
        "Default (61×89)": (61, 89),
        "Fine (121×177)": (121, 177),
        "Very Fine (241×353)": (241, 353),
    }

    verif_nr, verif_nz = verif_grid_map[verif_grid]

    # Cost warning for very fine grid
    if verif_nr * verif_nz > 30000:
        st.warning(
            f"⚠️ Very Fine grid has {verif_nr * verif_nz:,} cells. "
            "Expect 30-60 seconds runtime.",
            icon="⚠️"
        )


# Cache verification runs
@st.cache_data(max_entries=10)
def _run_verification_cached(params: ImmersedVerificationParams):
    """Cache expensive verification runs."""
    return run_immersed_verification(params)


# Build verification parameters
verif_params = ImmersedVerificationParams(
    nr=verif_nr,
    nz=verif_nz,
    electrode_spacing=electrode_spacing,
    apex_z=0.86 * electrode_spacing,  # Standard: 86% of spacing
    apex_radius=verif_apex_um * 1e-6,
    bc_type=verif_bc_type,
)

# Run button
col_run, col_clear = st.columns([3, 1])

with col_run:
    run_verif = st.button("▶️ Run Verification", type="primary")

with col_clear:
    if st.button("🗑️ Clear Cache"):
        _run_verification_cached.clear()
        st.success("Cache cleared!", icon="✅")

if run_verif:
    try:
        with st.spinner("Running immersed verification... This may take 10-60 seconds..."):
            progress_placeholder = st.empty()
            progress_placeholder.info("Sweeping cone angles and computing flank field exponents...", icon="⚙️")
            verif = _run_verification_cached(verif_params)
            progress_placeholder.empty()
    except Exception as exc:
        st.error(f"❌ Verification error: {exc}", icon="❌")
        verif = None
    else:
        st.session_state.last_verification = verif

        # Save to run history
        from datetime import datetime
        st.session_state.run_history.append({
            'timestamp': datetime.now(),
            'params': verif_params,
            'result': verif,
            'type': 'verification'
        })

        # Write results file
        try:
            results_path = write_results_json(
                RESULTS_DIR / "latest_verification_run.json",
                verification_run_to_dict(verif_params, verif),
            )
            st.success(f"✅ Verification completed successfully!", icon="✅")
            st.caption(f"Results written to `{results_path}`")
        except Exception as exc:
            st.warning(f"⚠️ Could not write results file: {exc}", icon="⚠️")

# Display results
verif = st.session_state.get("last_verification")

if verif is None:
    st.info(
        "👈 Configure verification parameters in the sidebar and click **▶️ Run Verification** to start.",
        icon="ℹ️"
    )
else:
    # Check if grid changed
    if verif.grid_r.size != verif_nr or verif.grid_z.size != verif_nz:
        st.warning(
            "⚠️ Showing results from the previous run — the grid has changed. "
            "Click **▶️ Run Verification** to recompute.",
            icon="⚠️"
        )

    st.divider()

    # Verification diagnostics
    st.header("📊 Verification Diagnostics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Recovered angle",
        f"{verif.recovered_angle_deg:.2f}°",
        delta=f"{verif.recovered_angle_deg - 49.29:+.2f}° from Taylor",
        help="Half-angle where the flank field exponent crosses p = -1 (scale-consistency condition). "
             "Should approach 49.29° with grid refinement.",
        border=True
    )

    col2.metric(
        "Method",
        verif.recovered_angle_method.replace("_", " ").title(),
        help="Algorithm used to determine the recovered angle from the exponent landscape.",
        border=True
    )

    onset_str = f"{verif.onset_voltage_V / 1e3:.2f} kV" if verif.onset_voltage_V else "—"
    col3.metric(
        "Predicted onset voltage",
        onset_str,
        help="Voltage amplitude projected from the Young-Laplace-Maxwell residual at the recovered angle.",
        border=True
    )

    col4.metric(
        "Min residual",
        f"{verif.min_rms_Pa:.3e} Pa",
        help="Minimum RMS residual across all angles tested.",
        border=True
    )

    # Taylor identity metrics (if available)
    if verif.identity_ratio is not None:
        st.subheader("Taylor Identity Verification")

        col5, col6, col7, col8 = st.columns(4)

        col5.metric(
            "Identity ratio V₀*/A*",
            f"{verif.identity_ratio:.4f}",
            delta=f"{(verif.identity_ratio - 1.0) * 100:+.2f}% from exact",
            help="Ratio of projected onset voltage to analytical amplitude. 1.000 = exact match.",
            border=True
        )

        col6.metric(
            "Exponent crossing",
            f"{verif.identity_exponent_crossing_deg:.2f}°" if verif.identity_exponent_crossing_deg else "—",
            help="Angle where flank exponent crosses p = -1 under imposed Taylor potential.",
            border=True
        )

        col7.metric(
            "Runtime",
            f"{verif.runtime_s:.1f} s",
            help="Total verification execution time.",
            border=True
        )

        col8.metric(
            "Grid cells",
            f"{verif_nr * verif_nz:,}",
            help=f"Mesh size: {verif_nr} × {verif_nz}",
            border=True
        )

        # Interpretation
        if abs(verif.identity_ratio - 1.0) < 0.01:
            st.success(
                f"✅ Excellent agreement: Identity ratio within 1% of exact (measured {verif.identity_ratio:.4f}). "
                "The immersed boundary machinery correctly implements the Taylor cone physics.",
                icon="✅"
            )
        elif abs(verif.identity_ratio - 1.0) < 0.05:
            st.info(
                f"ℹ️ Good agreement: Identity ratio within 5% of exact (measured {verif.identity_ratio:.4f}). "
                "Consider using a finer grid for better accuracy.",
                icon="ℹ️"
            )
        else:
            st.warning(
                f"⚠️ Significant deviation: Identity ratio is {abs(verif.identity_ratio - 1.0) * 100:.1f}% "
                "from exact. Check grid resolution or boundary conditions.",
                icon="⚠️"
            )

    else:
        # Just runtime and grid info
        col5, col6 = st.columns(2)

        col5.metric(
            "Runtime",
            f"{verif.runtime_s:.1f} s",
            help="Total verification execution time.",
            border=True
        )

        col6.metric(
            "Grid cells",
            f"{verif_nr * verif_nz:,}",
            help=f"Mesh size: {verif_nr} × {verif_nz}",
            border=True
        )

    # Interpretation of recovered angle
    angle_error = abs(verif.recovered_angle_deg - 49.29)
    if angle_error < 0.5:
        st.success(
            f"✅ Excellent angle recovery: {verif.recovered_angle_deg:.2f}° is within 0.5° of "
            "the theoretical Taylor angle (49.29°).",
            icon="✅"
        )
    elif angle_error < 2.0:
        st.info(
            f"ℹ️ Good angle recovery: {verif.recovered_angle_deg:.2f}° is within 2° of "
            "the theoretical Taylor angle (49.29°). Consider using Very Fine grid for better accuracy.",
            icon="ℹ️"
        )
    else:
        st.warning(
            f"⚠️ Angle recovery deviation: {verif.recovered_angle_deg:.2f}° differs by "
            f"{angle_error:.1f}° from the theoretical Taylor angle (49.29°). "
            "Check grid resolution and boundary conditions.",
            icon="⚠️"
        )

    st.divider()

    # Visualization
    st.header("🗺️ Verification Landscape")

    st.write("""
    The plots below show the angle sweep results and the imposed Taylor potential test.
    """)

    # Row 1: Verification landscape (centered, extra large)
    st.subheader("Flank Field Exponent Landscape")

    col_land_left, col_land_center, col_land_right = st.columns([1, 14, 1])

    with col_land_center:
        fig_land = figure_verification_landscape(verif)
        fig_land = apply_academic_style(fig_land, height=600)  # Extra tall for this important plot
        st.plotly_chart(fig_land)
        st.caption("""
        **Figure 1:** Flank field exponent p as a function of cone half-angle. The crossing at p = -1
        (red dashed line) identifies the angle where the far-field power law satisfies the
        scale-consistency condition. The vertical line marks the recovered angle.
        """)

    st.divider()

    # Row 2: Imposed Taylor field (centered, large)
    st.subheader("Imposed Taylor Potential Test")

    col_taylor_left, col_taylor_center, col_taylor_right = st.columns([1, 14, 1])

    with col_taylor_center:
        fig_taylor = figure_imposed_taylor_field(verif)
        fig_taylor = apply_academic_style(fig_taylor, height=600)  # Extra tall
        st.plotly_chart(fig_taylor)
        st.caption("""
        **Figure 2:** Electric potential field under the imposed analytical Taylor solution.
        This test verifies that the immersed boundary stencil correctly enforces the exact
        Taylor potential on the cone surface and outer boundary. The ratio V₀*/A* measures
        agreement with the analytical amplitude.
        """)

    st.divider()

    # Technical notes
    with st.expander("📋 Technical Notes", expanded=False):
        st.write(f"""
        **Grid resolution:** {verif_nr} × {verif_nz} = {verif_nr * verif_nz:,} cells

        **Boundary condition:** Taylor far-field (analytical potential at r = r_max, z = z_max)

        **Apex location:** z = {verif_params.apex_z * 1e3:.2f} mm ({verif_params.apex_z / electrode_spacing:.1%} of electrode spacing)

        **Apex radius:** {verif_params.apex_radius * 1e6:.1f} μm ({verif_params.apex_radius / electrode_spacing:.2%} of electrode spacing)

        **Recovered angle method:** {verif.recovered_angle_method}

        **Angle sweep range:** Approximately 30° to 60° in ~1° increments

        **Expected convergence:** The recovered angle should approach 49.29° as:
        - Grid is refined (coarse → fine → very fine)
        - Apex radius is reduced (approaching sharp cone limit)
        - Domain size increases (reducing boundary effects)

        **Discretization error:** At Fine grid (121×177), typical error is ~0.1° from the theoretical value.
        At Very Fine (241×353), error reduces to ~0.06°.
        """)

    st.divider()

    # Export
    st.header("💾 Export Results")

    export_col1, export_col2 = st.columns(2)

    with export_col1:
        st.download_button(
            label="📥 Download JSON",
            data=str(verification_run_to_dict(verif_params, verif)),
            file_name="verification_results.json",
            mime="application/json"
        )

    with export_col2:
        if st.button("📋 Copy Summary"):
            summary = f"""
Verification Summary
====================
Recovered angle: {verif.recovered_angle_deg:.3f}°
Theoretical Taylor angle: 49.29°
Error: {verif.recovered_angle_deg - 49.29:+.3f}°

Onset voltage: {onset_str}
Min residual: {verif.min_rms_Pa:.3e} Pa

Taylor identity ratio: {verif.identity_ratio:.4f} if verif.identity_ratio else "N/A"
Expected: 1.0000

Grid: {verif_nr} × {verif_nz}
Runtime: {verif.runtime_s:.1f} s
            """
            st.code(summary)

st.divider()

# Interpretation guide
with st.expander("💡 Interpreting Verification Results", expanded=False):
    st.markdown("""
    **What does "recovered angle" mean?**

    The recovered angle is the half-angle at which the computed flank field's power-law exponent
    satisfies the scale-consistency condition (p = -1). This is not an input parameter—it emerges
    from the numerical solution and tells us whether the solver correctly implements the physics.

    **Why 49.29°?**

    G.I. Taylor (1964) derived that a unique angle of 49.29° satisfies the far-field balance between
    electric stress and capillary pressure. Any correct implementation of the governing equations
    should recover this angle (within discretization error).

    **What's a "good" result?**

    - **Recovered angle:** Within 0.5° of 49.29° is excellent. Within 2° is acceptable for coarse grids.
    - **Identity ratio:** Within 1% of 1.000 (i.e., 0.990–1.010) is excellent. Within 5% is acceptable.
    - **Min residual:** Lower is better; typically < 1 Pa for good balance.

    **Grid convergence:**

    As you refine the grid (Fast → Default → Fine → Very Fine), the recovered angle should
    monotonically approach 49.29° from below. If it doesn't, check:
    - Boundary conditions (should be Taylor far-field for this test)
    - Apex radius (should be small, ~0.5% of domain size)
    - Domain size (should be large enough to avoid truncation)

    **Negative controls:**

    The "grounded box" boundary condition (not exposed in this interface) is a negative control that
    deliberately introduces truncation artifacts. It recovers angles around 43–46° instead of 49.29°,
    demonstrating that boundary conditions matter. The Taylor far-field BC is the correct choice.
    """)
