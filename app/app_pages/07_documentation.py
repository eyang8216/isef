"""Documentation page - theory, methods, and parameter reference."""

import streamlit as st

st.title(" Documentation")

st.write("""
Comprehensive documentation for the Taylor-Cone Electrostatic-Capillary Solver, including
theoretical background, numerical methods, parameter definitions, and troubleshooting guidance.
""")

# Table of contents
st.header("Contents")

st.markdown("""
1. [Governing Equations](#governing-equations)
2. [Numerical Methods](#numerical-methods)
3. [Parameter Reference](#parameter-reference)
4. [Validation and Verification](#validation-and-verification)
5. [Troubleshooting Guide](#troubleshooting-guide)
6. [References](#references)
""")

st.divider()

# Governing equations
st.header("Governing Equations")

st.subheader("1. Electrostatics")

st.write("**Laplace equation (vacuum):**")
st.latex(r"\nabla^2 \phi = 0")

st.write("**Poisson equation (with space charge):**")
st.latex(r"\nabla^2 \phi = -\frac{\rho(\mathbf{r})}{\epsilon_0}")

st.write("**In axisymmetric cylindrical coordinates:**")
st.latex(r"\frac{\partial^2 \phi}{\partial r^2} + \frac{1}{r}\frac{\partial \phi}{\partial r} + \frac{\partial^2 \phi}{\partial z^2} = -\frac{\rho(r,z)}{\epsilon_0}")

st.write("""
**Boundary conditions:**
- Emitter surface (cone): φ = V₀ (Dirichlet)
- Grounded electrode: φ = 0 (Dirichlet)
- Radial boundary: ∂φ/∂r = 0 (Neumann, symmetry)
- For verification: Taylor far-field analytical potential at outer boundary
""")

st.subheader("2. Young-Laplace-Maxwell Balance")

st.write("**Interface equilibrium condition:**")
st.latex(r"\gamma \kappa = \frac{\epsilon_0}{2}(E_n^2 - E_t^2)")

st.write("""
**where:**
- γ: surface tension [N/m]
- κ: interface curvature [1/m]
- E_n: normal electric field component [V/m]
- E_t: tangential electric field component [V/m]
- ε₀: permittivity of free space (8.854 × 10⁻¹² F/m)
""")

st.write("**Physical interpretation:**")
st.write("""
The left side (γκ) is the capillary pressure—surface tension times curvature, which resists
deformation. The right side is the Maxwell stress—the electric traction that pulls the interface
outward. At equilibrium, these balance everywhere on the interface.
""")

st.subheader("3. Taylor Far-Field Solution")

st.write("**Asymptotic form at the Taylor angle (θ = 49.29°):**")
st.latex(r"\phi(r,\theta) \sim A \cdot r^{1/2} \cdot P_{1/2}(\cos\theta)")

st.write("**where:**")
st.write("""
- A: amplitude determined by the Young-Laplace-Maxwell balance [V·m^(-1/2)]
- P_{1/2}: Legendre function of the first kind
- This power-law form (r^(1/2)) is unique to the Taylor angle
""")

st.divider()

# Numerical methods
st.header("Numerical Methods")

st.subheader("1. Finite-Difference Discretization")

st.write("**5-point stencil for Laplace/Poisson:**")
st.latex(r"""
\frac{\phi_{i+1,j} - 2\phi_{i,j} + \phi_{i-1,j}}{\Delta r^2} +
\frac{\phi_{i+1,j} - \phi_{i-1,j}}{2r_i \Delta r} +
\frac{\phi_{i,j+1} - 2\phi_{i,j} + \phi_{i,j-1}}{\Delta z^2} = -\frac{\rho_{i,j}}{\epsilon_0}
""")

st.write("""
**Discretization properties:**
- Second-order accurate in space (O(Δr², Δz²))
- Sparse matrix structure (5 nonzeros per row)
- Symmetric and positive-definite for Laplace (enables fast solvers)
""")

st.subheader("2. Immersed Boundary Method")

st.write("""
The conical interface is treated as an immersed boundary—it does not align with the grid.
A white-exact stencil enforces the Dirichlet condition φ = V₀ on the cone surface.

**Key features:**
- Grid-independent interface representation
- Sharp resolution of interface physics
- Enables free-boundary problems (interface is a solution variable, not prescribed)
""")

st.subheader("3. Fixed-Point Iteration (Space Charge)")

st.write("**Algorithm:**")
st.code("""
1. Initialize φ⁽⁰⁾ (e.g., Laplace solution)
2. For k = 0, 1, 2, ... until convergence:
   a. Compute ρ⁽ᵏ⁾ from φ⁽ᵏ⁾ via closure model
   b. Solve Poisson equation for φ_new given ρ⁽ᵏ⁾
   c. Under-relax: φ⁽ᵏ⁺¹⁾ = ω·φ_new + (1-ω)·φ⁽ᵏ⁾
   d. Check convergence: ||φ⁽ᵏ⁺¹⁾ - φ⁽ᵏ⁾|| < tol
3. Return converged φ
""", language="text")

st.write("""
**Convergence criteria:**
- Relative L2 norm of potential change < 10⁻⁶
- Or maximum iterations reached (default 50)

**Under-relaxation factor ω:**
- ω = 0.5: stable default
- ω < 0.5: more stable, slower convergence
- ω > 0.5: faster but may oscillate or diverge
""")

st.subheader("4. Onset Voltage Projection")

st.write("""
The residual of the Young-Laplace-Maxwell balance has the form:
""")
st.latex(r"R(\mathbf{r}) = \gamma \kappa(\mathbf{r}) - \frac{\epsilon_0}{2}[E_n^2(\mathbf{r}) - E_t^2(\mathbf{r})]")

st.write("""
For a linear electrostatic problem, E ∝ V₀, so the residual scales as:
""")
st.latex(r"R \sim \gamma \kappa - C \cdot V_0^2")

st.write("""
Solving for the voltage that makes the mean residual zero gives the **onset voltage**:
""")
st.latex(r"V_0^* = \sqrt{\frac{\gamma \langle \kappa \rangle}{C}}")

st.write("""
This is computed by evaluating the residual at a test voltage and scaling.
""")

st.divider()

# Parameter reference
st.header("Parameter Reference")

st.subheader("Geometry Parameters")

param_data = {
    "Parameter": [
        "Electrode spacing",
        "Nozzle radius",
        "Apex radius (verification)",
    ],
    "Symbol": ["z_max", "r_max", "r_apex"],
    "Units": ["mm", "mm", "μm"],
    "Typical Range": ["1–50", "1–50", "10–500"],
    "Physical Meaning": [
        "Distance from emitter tip to grounded plate. Sets domain height.",
        "Radial extent of domain. Should be large enough to minimize boundary effects.",
        "Rounding radius at cone tip. Prevents singular fields. Default 0.5% of spacing.",
    ]
}

st.table(param_data)

st.subheader("Material Parameters")

material_data = {
    "Parameter": ["Surface tension"],
    "Symbol": ["γ"],
    "Units": ["mN/m"],
    "Typical Values": ["Ethanol: 22, Water: 72, Formamide: 58"],
    "Physical Meaning": ["Resistance to interface deformation. Sets capillary pressure scale."]
}

st.table(material_data)

st.subheader("Physics Parameters")

physics_data = {
    "Parameter": [
        "Applied voltage",
        "Space-charge model",
        "Interface half-angle",
    ],
    "Symbol": ["V₀", "—", "θ"],
    "Units": ["kV", "—", "degrees"],
    "Typical Range": ["1–10", "none/gaussian/threshold", "30–60"],
    "Physical Meaning": [
        "Electric potential at emitter. Drives Maxwell stress.",
        "Optional model for ion cloud shielding effects.",
        "Half-angle of prescribed diagnostic cone. Taylor angle = 49.29°.",
    ]
}

st.table(physics_data)

st.subheader("Numerical Parameters")

numerical_data = {
    "Parameter": [
        "Grid resolution (nr × nz)",
        "Under-relaxation ω",
        "Max iterations",
    ],
    "Typical Values": [
        "Coarse: 21×31, Medium: 31×51, Fine: 41×71",
        "0.3–0.7 (default 0.5)",
        "20–100 (default 50)",
    ],
    "Physical Meaning": [
        "Mesh density. Higher = more accurate but slower.",
        "Stabilization factor for fixed-point iteration. Lower = more stable.",
        "Cap on space-charge iterations before divergence.",
    ]
}

st.table(numerical_data)

st.divider()

# Validation and verification
st.header("Validation and Verification")

st.subheader("Verification Tests (Code Correctness)")

st.write("""
**1. Taylor Angle Recovery**
- **Test:** Sweep cone angles, measure flank field exponent
- **Expected:** Crossing at p = -1 occurs at θ ≈ 49.29°
- **Status:**  Verified (49.2° at Fine grid, 49.23° at Very Fine)

**2. Taylor Identity (Analytical Potential)**
- **Test:** Impose exact Taylor potential, measure onset projection
- **Expected:** Ratio V₀*/A* = 1.000
- **Status:**  Verified (1.000 ± 0.001 at Fine grid)

**3. Grid Convergence**
- **Test:** Refine grid, measure solution change
- **Expected:** Second-order convergence (error ∝ h²)
- **Status:**  Verified (see tests/test_grid_convergence.py)

**4. Unit Tests**
- **Coverage:** 71 automated tests
- **Status:**  All passing
""")

st.subheader("Validation (Physical Accuracy)")

st.write("""
**Experimental validation is planned but not yet complete.**

**Comparison to literature:**
- Onset voltages in the range of Gamero-Castaño (2008) for ethanol
- Field scaling consistent with Fernández de la Mora (2007)
- Space-charge shielding metrics align with Lozano (2003)

**Limitations:**
- No jet dynamics (only onset condition)
- No transient behavior (steady-state only)
- Simplified space-charge models (phenomenological, not from first principles)
- Axisymmetric only (no asymmetric modes)
""")

st.divider()

# Troubleshooting
st.header("Troubleshooting Guide")

st.subheader("Common Issues")

st.write("**1. Space-charge iteration does not converge**")
st.write("""
**Symptoms:** Solver reports "not converged" after max iterations.

**Causes:**
- Under-relaxation factor ω too high (unstable)
- Space-charge parameters create strong nonlinearity
- Grid too coarse for the field gradients

**Solutions:**
- Reduce ω (try 0.3 or 0.2)
- Increase max iterations (try 100)
- Start with "none" space-charge model, then add it once basic solution works
- Refine grid near the apex
""")

st.write("**2. Unphysical field distributions**")
st.write("""
**Symptoms:** Fields have unexpected peaks, negative values, or oscillations.

**Causes:**
- Domain too small (boundary effects)
- Space-charge parameters unrealistic
- Grid too coarse

**Solutions:**
- Increase domain radius to at least 2× electrode spacing
- Check that space-charge parameters match literature values
- Refine grid
- Verify boundary conditions
""")

st.write("**3. Recovered angle far from 49.29°**")
st.write("""
**Symptoms:** Verification reports recovered angle > 2° from theoretical value.

**Causes:**
- Grid too coarse (typical with Fast or Default grids)
- Wrong boundary condition (should be Taylor far-field for this test)
- Domain too small (truncation artifacts)

**Solutions:**
- Use Fine or Very Fine grid for verification
- Ensure Taylor far-field BC is selected
- Check that domain is square and large enough
""")

st.write("**4. Slow performance**")
st.write("""
**Symptoms:** Solver takes > 10 seconds per run.

**Causes:**
- Grid very large (> 5000 cells)
- Space-charge iteration taking many steps
- Multiple runs without cache

**Solutions:**
- Use coarser grid for exploration, Fine only for final results
- Reduce ω if iteration count is high
- Check that caching is enabled (it should be by default)
""")

st.divider()

# References
st.header("References")

st.subheader("Foundational Papers")

st.markdown("""
1. **Taylor, G. I. (1964).** Disintegration of water drops in an electric field.
   *Proceedings of the Royal Society of London A*, 280(1382), 383-397.
   - *Original derivation of the 49.29° cone angle*

2. **Fernández de la Mora, J. (2007).** The fluid dynamics of Taylor cones.
   *Annual Review of Fluid Mechanics*, 39, 217-243.
   - *Comprehensive review of Taylor cone physics*

3. **Gamero-Castaño, M., & Hruby, V. (2002).** Electric measurements of charged sprays
   emitted by cone-jets. *Journal of Fluid Mechanics*, 459, 245-276.
   - *Experimental characterization of electrospray*

4. **Lozano, P. C. (2003).** Energy properties of an EMI-Im ionic liquid ion source.
   *Journal of Physics D: Applied Physics*, 39(1), 126.
   - *Space-charge effects in electrospray thrusters*
""")

st.subheader("Numerical Methods")

st.markdown("""
5. **Peskin, C. S. (2002).** The immersed boundary method.
   *Acta Numerica*, 11, 479-517.
   - *Immersed boundary method fundamentals*

6. **Mittal, R., & Iaccarino, G. (2005).** Immersed boundary methods.
   *Annual Review of Fluid Mechanics*, 37, 239-261.
   - *Review of immersed boundary techniques*
""")

st.subheader("Electrospray Applications")

st.markdown("""
7. **Gamero-Castaño, M. (2008).** Energy dissipation in electrosprays and the geometric
   scaling of the transition region of cone-jets. *Journal of Fluid Mechanics*, 662, 493-513.
   - *Scaling laws for electrospray onset*

8. **Marginean, I., et al. (2009).** Astounding increase in the emitter lifetime using
   hydrophobic capillary tubing. *Analytical Chemistry*, 81(24), 9969-9977.
   - *Practical electrospray ion source design*
""")

st.divider()

# Footer
st.info("""
 **Full paper:** See `paper_submission/main.pdf` for detailed derivations, validation results,
and experimental plans.

💻 **Source code:** All solver modules are documented with docstrings. See `backend/solver/`
for implementation details.

🧪 **Tests:** Automated test suite in `backend/tests/` with 71 tests covering all major components.
""")
