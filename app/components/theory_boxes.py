"""Theory boxes for in-context mathematical explanations."""

import streamlit as st


def taylor_angle_theory():
    """Display theory box for Taylor angle."""
    with st.expander("📚 Theory: Taylor Angle", expanded=False):
        st.latex(r"\theta_T = 49.29° \text{ (Taylor 1964)}")
        st.write("""
        The Taylor angle emerges from the scale-consistency condition of the
        Young-Laplace-Maxwell balance in the cone's far field. At this specific angle,
        the electric stress (Maxwell stress tensor) exactly balances the capillary
        pressure along the conical interface.

        **Mathematical basis:**
        - Electric field behaves as E ∝ r^(-1/2) in the far field
        - Capillary pressure scales as γκ where κ ∝ r^(-1) for a cone
        - Maxwell stress ∝ E² ∝ r^(-1)
        - The angle 49.29° satisfies the balance condition uniquely

        **Physical significance:**
        This angle is universal for electrohydrodynamic cone-jets, independent of
        fluid properties, flow rate, or applied voltage (within the cone-jet regime).
        """)
        st.caption("**Reference:** Taylor, G. I. (1964). Disintegration of water drops in an electric field. Proc. R. Soc. Lond. A, 280(1382), 383-397.")


def laplace_equation_theory():
    """Display theory box for Laplace equation."""
    with st.expander("📚 Theory: Laplace Equation", expanded=False):
        st.latex(r"\nabla^2 \phi = 0 \quad \text{(vacuum electrostatics)}")
        st.write("""
        The Laplace equation governs the electric potential in the absence of space charge.

        **In cylindrical coordinates (axisymmetric):**
        """)
        st.latex(r"\frac{\partial^2 \phi}{\partial r^2} + \frac{1}{r}\frac{\partial \phi}{\partial r} + \frac{\partial^2 \phi}{\partial z^2} = 0")
        st.write("""
        **Boundary conditions:**
        - Emitter surface (cone): φ = V₀ (applied voltage)
        - Grounded electrode: φ = 0
        - Radial boundary: ∂φ/∂r = 0 (symmetry)

        **Solution method:**
        Finite-difference discretization with a 5-point stencil, solved via
        successive over-relaxation (SOR) or direct sparse linear algebra.
        """)


def poisson_space_charge_theory():
    """Display theory box for Poisson equation with space charge."""
    with st.expander("📚 Theory: Space Charge (Poisson Extension)", expanded=False):
        st.latex(r"\nabla^2 \phi = -\frac{\rho}{\epsilon_0}")
        st.write("""
        When ion emission occurs, the emitted charge cloud modifies the electric field
        (space-charge shielding). The Poisson equation includes a source term ρ(r,z).

        **Phenomenological models:**

        1. **Gaussian model:** Localized charge cloud
        """)
        st.latex(r"\rho(r,z) = \rho_0 \exp\left(-\frac{(r-r_0)^2 + (z-z_0)^2}{\ell^2}\right)")
        st.write("""
        2. **Threshold model:** Field-activated emission
        """)
        st.latex(r"\rho(r,z) = \rho_{\max} \cdot H(|E| - E_c) \cdot \tanh\left(\frac{|E| - E_c}{E_s}\right)")
        st.write("""
        **Numerical solution:**
        Fixed-point iteration with under-relaxation:
        1. Solve Poisson equation for φ given ρ
        2. Compute E = -∇φ
        3. Update ρ based on E
        4. Repeat until convergence
        """)


def young_laplace_maxwell_theory():
    """Display theory box for YLM balance."""
    with st.expander("📚 Theory: Young-Laplace-Maxwell Balance", expanded=False):
        st.write("""
        The interface shape is determined by the balance between capillary pressure
        and electric stress (Maxwell stress tensor).
        """)
        st.latex(r"\gamma \kappa = \frac{\epsilon_0}{2}(E_n^2 - E_t^2)")
        st.write("""
        **Terms:**
        - **γκ**: Capillary pressure (γ = surface tension, κ = curvature)
        - **E_n**: Normal electric field component
        - **E_t**: Tangential electric field component

        **Physical interpretation:**
        - Electric field pulls the interface outward (Maxwell stress)
        - Surface tension resists deformation (capillary pressure)
        - At equilibrium, these forces balance everywhere on the interface

        **Residual diagnostic:**
        This solver evaluates the residual of this balance on a prescribed conical
        interface to assess how close the solution is to a true equilibrium shape.
        """)


def immersed_boundary_theory():
    """Display theory box for immersed boundary method."""
    with st.expander("📚 Theory: Immersed Boundary Method", expanded=False):
        st.write("""
        The immersed boundary method treats the conical interface as the powered
        boundary of its own Laplace problem, enabling:

        1. **Free-boundary mechanics:** The cone is not imposed externally but emerges
           from the Dirichlet condition φ = V₀ on the cone surface

        2. **Onset voltage projection:** The residual's amplitude reveals the voltage
           needed to achieve Young-Laplace-Maxwell balance

        3. **Angle recovery:** Sweeping the cone angle and measuring the flank field
           exponent identifies where the far-field power law satisfies scale consistency

        **Key verification tests:**
        - **Recovered angle:** Should approach 49.29° with grid refinement
        - **Taylor identity:** Imposing the exact analytical Taylor potential should
          yield onset voltage exactly matching the analytical amplitude

        **Why this matters:**
        This machinery directly verifies that the solver correctly implements the
        physics of the Taylor cone problem, independent of any empirical fitting.
        """)


def convergence_criteria_theory():
    """Display theory box for convergence criteria."""
    with st.expander("📚 Theory: Convergence Criteria", expanded=False):
        st.write("""
        **Fixed-point iteration convergence:**

        The space-charge solver uses a fixed-point iteration scheme with under-relaxation:
        """)
        st.latex(r"\phi^{(k+1)} = \omega \phi_{\text{new}} + (1-\omega)\phi^{(k)}")
        st.write("""
        where ω ∈ (0,1] is the under-relaxation factor.

        **Convergence test:**
        """)
        st.latex(r"\|\phi^{(k+1)} - \phi^{(k)}\|_2 < \text{tol}")
        st.write("""
        **Practical guidelines:**
        - **ω = 0.5**: Stable default for most problems
        - **ω < 0.5**: Use for highly nonlinear space-charge models
        - **ω > 0.5**: Can accelerate convergence if stable

        **Divergence indicators:**
        - Residual oscillates or grows
        - Solution exhibits non-physical features
        - Maximum iterations reached without convergence

        **Remedies:**
        - Reduce ω (more stable but slower)
        - Increase max iterations
        - Check space-charge parameters for physical plausibility
        - Use coarser grid for initial exploration
        """)
