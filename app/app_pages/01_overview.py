"""Overview page - landing page with theory and quick start."""

import streamlit as st

st.title("Overview")

st.write("""
Welcome to the Taylor-Cone Electrostatic-Capillary Solver, a computational tool for modeling
electrospray onset and Taylor cone formation.
""")

# Quick start guide
st.header("Quick Start")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 1. Configure
    - Choose a preset or custom configuration
    - Set geometry and material properties
    - Select mesh resolution
    """)

with col2:
    st.markdown("""
    ### 2️⃣ Solve
    - Run the electrostatic solver
    - View field distributions
    - Analyze residuals and metrics
    """)

with col3:
    st.markdown("""
    ### 3️⃣ Verify
    - Run immersed verification tests
    - Check recovered angle (≈49.29°)
    - Validate onset voltage prediction
    """)

st.divider()

# Physical background
st.header("Physical Background")

st.write("""
**Electrospray** is a process where an electric field deforms a liquid meniscus into a sharp cone
(the **Taylor cone**), from which a fine jet of charged droplets is emitted. This phenomenon is
fundamental to:

- **Mass spectrometry** (electrospray ionization, ESI)
- **Colloid thrusters** for spacecraft propulsion
- **Electrospinning** for nanofiber production
- **Focused ion beam** systems

The Taylor cone forms when electric stress (Maxwell stress) exactly balances capillary pressure
along the interface.
""")

col_theory1, col_theory2 = st.columns(2)

with col_theory1:
    st.subheader("The Taylor Angle")
    st.latex(r"\theta_T = 49.29°")
    st.write("""
    G.I. Taylor (1964) showed that a unique half-angle of **49.29°** satisfies the scale-consistency
    condition of the Young-Laplace-Maxwell balance. This angle is universal—independent of fluid
    properties, flow rate, or voltage.
    """)

with col_theory2:
    st.subheader("Governing Physics")
    st.write("**Young-Laplace-Maxwell Balance:**")
    st.latex(r"\gamma \kappa = \frac{\epsilon_0}{2}(E_n^2 - E_t^2)")
    st.write("""
    - **γκ**: Capillary pressure
    - **E_n, E_t**: Normal and tangential electric fields
    - Balance determines interface shape
    """)

st.divider()

# What this solver does
st.header("What This Solver Does")

st.write("""
This solver implements a **reduced-order model** for Taylor cone onset, designed to be:

- **Lightweight**: Runs on consumer hardware (no HPC required)
- **Fast**: Seconds per solve, not hours
- **Accurate**: Verified against analytical solutions
- **Accessible**: Python-based, open source, well-documented

**Not intended as:**
- Full CFD simulation with jet breakup
- Complete thruster performance predictor
- Replacement for experimental validation
""")

st.info("""
**Scope:** This solver focuses on the **onset condition**—the voltage and field distribution at
which the Taylor cone forms. It does not model jet dynamics, droplet formation, or transient
behavior.
""")

st.divider()

# COMSOL alternative section
st.header("🔬 Alternative to COMSOL Multiphysics")

st.markdown("""
<div style="background-color: #e8f4f8; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;">
<h3 style="color: #1f77b4; margin-top: 0;">Specific Capabilities for Scientists</h3>
<p>This solver provides a <strong>lightweight, open-source alternative to COMSOL</strong> for specific Taylor cone applications:</p>

<h4 style="color: #1f77b4;">✓ What You CAN Use This For (Instead of COMSOL):</h4>
<ul>
    <li><strong>Taylor Cone Onset Voltage Prediction</strong> — Fast prediction of critical voltage for electrospray initiation</li>
    <li><strong>Axisymmetric Electrostatic Field Simulation</strong> — 2D cylindrical coordinates (r, z) for rotationally symmetric problems</li>
    <li><strong>Immersed Boundary Free-Surface Handling</strong> — Complex cone geometries with automated interface tracking</li>
    <li><strong>Grid Convergence Studies</strong> — Automated mesh refinement analysis for accuracy verification</li>
    <li><strong>Novel Exponent Crossing Observable</strong> — Unique verification method (p = -1 crossing) not available in COMSOL</li>
</ul>

<h4 style="color: #d9534f;">✗ Limitations (Use COMSOL For These):</h4>
<ul>
    <li>Full 3D geometries with no rotational symmetry</li>
    <li>Fluid dynamics, jet breakup, droplet formation</li>
    <li>Coupled multiphysics beyond electrostatics + capillary</li>
</ul>

<h4 style="color: #1f77b4;">🎯 Ideal Scientific Use Cases:</h4>
<p><strong>Electrospray ionization (ESI-MS)</strong>, <strong>liquid metal ion sources (LMIS)</strong>, <strong>electrospinning</strong>,
<strong>colloid thrusters</strong>, and <strong>cone-jet formation research</strong> where fast onset predictions for axisymmetric
geometries are needed without commercial FEM overhead.</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# Key features
st.header("Key Features")

feature_col1, feature_col2 = st.columns(2)

with feature_col1:
    st.subheader("Solver Capabilities")
    st.markdown("""
    - Axisymmetric Laplace/Poisson electrostatics
    - ✓ Immersed boundary method for free interfaces
    - Space-charge shielding models (optional)
    - Young-Laplace-Maxwell residual analysis
    - Onset voltage projection
    - ✓ Grid convergence tools
    """)

with feature_col2:
    st.subheader("Verification Suite")
    st.markdown("""
    - Taylor angle recovery (→ 49.29°)
    - Analytical Taylor potential identity
    - Flank field exponent measurement
    - Grid refinement convergence tests
    - 71 automated unit tests
    - Documented validation cases
    """)

st.divider()

# Navigation guide
st.header("Navigation Guide")

st.write("""
Use the tabs at the top to navigate:

- **Overview** (this page): Background and getting started
- **Solver**: Main solver interface with field visualization
- **Verification**: Immersed boundary verification and angle recovery
- **Documentation**: Theory, methods, and parameter reference
""")

st.divider()

# Getting help
st.header("Getting Help")

help_col1, help_col2, help_col3 = st.columns(3)

with help_col1:
    st.markdown("""
    ### Documentation
    Read the **Documentation** tab for:
    - Theory and governing equations
    - Numerical methods
    - Parameter definitions
    - Troubleshooting guide
    """)

with help_col2:
    st.markdown("""
    ### Tooltips
    Hover over information icons throughout the app for:
    - Parameter explanations
    - Typical value ranges
    - Physical interpretation
    - Computational cost hints
    """)

with help_col3:
    st.markdown("""
    ### Paper
    See the full ISEF paper for:
    - Literature review
    - Mathematical derivations
    - Validation results
    - Experimental plans
    """)

st.divider()

# Citation
st.header("Citation")

st.code("""
@article{yang2026taylor,
  title={A Lightweight Axisymmetric Electrostatic-Capillary Solver for
         Taylor-Cone Onset with Planned Experimental Validation},
  author={Yang, Ethan and Dong, Elliott and Lau, Curtis},
  journal={ISEF 2026},
  year={2026},
  institution={Independent Schools Foundation Academy, Hong Kong SAR}
}
""", language="bibtex")

st.success("Ready to start? Navigate to the **Solver** tab to begin!")
