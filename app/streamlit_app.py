"""Main Streamlit app entry point with navigation."""

from pathlib import Path

import streamlit as st

# Set page config first (must be first Streamlit command)
st.set_page_config(
    page_title="Taylor-Cone Solver",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Header with institutional branding
st.title("Taylor-Cone Electrostatic-Capillary Solver")
st.caption("**A Lightweight Axisymmetric Solver for Onset Prediction**")
st.caption("ISEF 2026 | Independent Schools Foundation Academy, Hong Kong SAR")
st.caption("Ethan Yang, Elliott Dong, Curtis Lau")

# About section
with st.expander("About this solver", expanded=False):
    st.write("""
    **Project:** Reduced-order Taylor-cone solver for electrospray modeling and colloid thruster design.

    **Abstract:** Electrospray and colloid thrusters rely on the formation of a Taylor cone, an
    electrohydrodynamic interface where electric Maxwell stress balances capillary pressure. This solver
    assembles sparse finite-difference Laplace/Poisson electrostatic systems, prescribes electric fields
    via a white-exact immersed boundary stencil, evaluates Maxwell and capillary pressure on candidate
    interfaces, computes Young-Laplace-Maxwell residuals with onset voltage projection, and optionally
    includes space-charge shielding closures.

    **Citation:** Yang, E., Dong, E., & Lau, C. (2026). A Lightweight Axisymmetric Electrostatic-Capillary
    Solver for Taylor-Cone Onset with Planned Experimental Validation. ISEF 2026.

    **License:** Open source (see repository)

    **Repository:** [GitHub](https://github.com/eyang8216/isef)
    """)

st.divider()

# Navigation (using Material Symbols per best practices)
overview_page = st.Page("app_pages/01_overview.py", title="Overview", default=True)
solver_page = st.Page("app_pages/02_solver.py", title="Solver")
verification_page = st.Page("app_pages/03_verification.py", title="Verification")
documentation_page = st.Page("app_pages/07_documentation.py", title="Documentation")

pg = st.navigation([overview_page, solver_page, verification_page, documentation_page])

# Initialize session state
if 'run_history' not in st.session_state:
    st.session_state.run_history = []

if 'last_result' not in st.session_state:
    st.session_state.last_result = None

if 'last_params' not in st.session_state:
    st.session_state.last_params = None

if 'last_verification' not in st.session_state:
    st.session_state.last_verification = None

# Run selected page
pg.run()

# Footer
st.divider()
st.caption("**Tip:** Use the sidebar to adjust parameters and the tabs above to navigate between solver modes.")
st.caption("For detailed theory and methods, see the **Documentation** tab.")
