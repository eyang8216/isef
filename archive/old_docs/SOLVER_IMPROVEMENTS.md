# Critical Solver Improvements for Experimental Validation

**Document purpose:** This document outlines three critical modifications required to make the Taylor cone solver experimentally useful and accurate.

**Status:** These improvements are REQUIRED before experimental validation.

**Priority:** All three are HIGH priority. Complete in numerical order.

**Date created:** 2026-08-12

---

## Problem Summary

The current solver has three fundamental issues preventing experimental validation:

1. **Geometry runs at meter-scale instead of millimeter-scale** (1000× too large)
2. **Boundary conditions cause 42.5° prediction instead of 49.29° Taylor angle** (finite-domain artifact)
3. **Space-charge shielding metric S_E is negative** (cannot claim "shielding" in paper)

---

## Improvement #1: Rescale Geometry to Realistic Experimental Dimensions

### Current State

```python
# Current hardcoded meter-scale geometry (WRONG):
nozzle_radius = 1.0 m          # 1000 mm diameter nozzle (!)
electrode_spacing = 1.0 m       # 1000 mm gap (!)
apex_radius = 0.05 m            # 50 mm apex (!)

# Results:
onset_voltage = 27.6 kV         # Too high to compare to literature
recovered_angle = 42.5°         # Truncation artifact exaggerated
```

### Target State

```python
# Realistic experimental scale:
nozzle_inner_diameter = 0.3 mm  # Typical capillary ID
nozzle_outer_diameter = 0.5 mm  # Typical capillary OD
electrode_spacing = 10 mm       # Typical needle-to-plate gap
apex_radius = 50 μm             # Realistic Taylor cone apex

# Expected results after rescaling:
onset_voltage = 2-5 kV          # Literature range for ethanol
recovered_angle = 42-47°        # Still truncation artifact, but at right scale
```

### Why This Matters

**Physical scaling is non-linear:**
- Onset voltage scales as `V ~ √(γL/ε₀)` where L is the characteristic length
- Grid resolution requirements change (need finer grids at smaller scales)
- Boundary layer effects become more important
- **Cannot simply "scale down" meter-scale results by a constant factor**

**Experimental comparison is impossible at wrong scale:**
- Literature shows ethanol electrospray onset at 1-3 kV for mm-scale nozzles
- Current solver predicts 27.6 kV at 1m scale
- Scaling down: 27.6 kV × √(0.3mm/1000mm) ≈ 478 V (too low!)
- The discrepancy indicates the boundary conditions/geometry are fundamentally wrong

### Implementation Plan

#### Step 1.1: Modify Streamlit App Input Parameters

**File:** `backend/app/streamlit_app.py`

**Current code (lines ~70-90):**
```python
# BEFORE:
V0 = st.number_input("Applied voltage V₀ (V)", value=1000.0, ...)
nozzle_radius = st.number_input("Nozzle radius (m)", value=1.0, ...)
electrode_spacing = st.number_input("Electrode spacing (m)", value=1.0, ...)
```

**Change to:**
```python
# AFTER - Use mm/μm units in UI, convert to meters internally:
V0 = st.number_input(
    "Applied voltage V₀ (kV)", 
    value=2.5,           # Realistic default for ethanol
    min_value=0.5, 
    max_value=10.0,
    step=0.1,
    format="%.2f",
    help="Typical ethanol electrospray: 1-5 kV"
) * 1000.0  # Convert kV → V

nozzle_id = st.number_input(
    "Nozzle inner diameter (mm)", 
    value=0.3,           # Standard capillary ID
    min_value=0.1, 
    max_value=2.0,
    step=0.05,
    format="%.2f",
    help="Inner diameter of capillary tube where liquid flows"
) * 1e-3  # Convert mm → m

nozzle_od = st.number_input(
    "Nozzle outer diameter (mm)", 
    value=0.5,           # Standard capillary OD
    min_value=0.15, 
    max_value=3.0,
    step=0.05,
    format="%.2f",
    help="Outer diameter of capillary tube"
) * 1e-3  # Convert mm → m

electrode_spacing = st.number_input(
    "Electrode spacing (mm)",
    value=10.0,          # Typical gap
    min_value=2.0,
    max_value=50.0,
    step=1.0,
    format="%.1f",
    help="Distance from nozzle tip to grounded extractor plate"
) * 1e-3  # Convert mm → m

# Update domain size to scale with electrode spacing (not hardcoded 1.0 m):
domain_r_max = electrode_spacing * 2.0
domain_z_max = electrode_spacing * 2.5
```

#### Step 1.2: Modify Immersed Verification Parameters

**File:** `backend/app/streamlit_app.py` (verification section, lines ~250-270)

**Current code:**
```python
# BEFORE:
apex_radius = 0.05  # meters (50 mm - unrealistic!)
```

**Change to:**
```python
# AFTER - Use μm units in UI:
apex_radius = st.number_input(
    "Apex radius (μm)",
    value=50.0,          # Realistic Taylor cone apex
    min_value=10.0,
    max_value=200.0,
    step=10.0,
    format="%.0f",
    help="Radius of curvature at cone apex; typical 10-100 μm"
) * 1e-6  # Convert μm → m

# Domain should scale with physical size:
verif_r_max = electrode_spacing * 1.5
verif_z_max = electrode_spacing * 2.0
```

#### Step 1.3: Update Grid Resolution for Smaller Scale

**File:** `backend/solver/app_backend.py` or wherever grid is defined

**Issue:** At mm-scale, the apex radius (50 μm) needs adequate grid resolution.

**Example calculation:**
```
Domain: 10mm × 15mm (electrode spacing × 1.5)
Apex region of interest: ~0.5mm around apex
Desired resolution at apex: ~10 μm per cell

Grid requirement: 
  - In apex region: 0.5mm / 10μm = 50 cells
  - For 10mm domain: need ~500 radial cells for uniform grid
  - OR use adaptive/stretched grid with fine resolution near axis
```

**Recommendation:** Use stretched/geometric grid spacing:
```python
# Near axis (r < 1mm): fine grid (10-20 μm spacing)
# Far field (r > 5mm): coarse grid (100-200 μm spacing)

def create_stretched_grid(r_max, n_r, stretch_factor=1.05):
    """Create geometrically stretched grid with fine resolution near axis"""
    # Implementation here
    ...
```

#### Step 1.4: Update Default Surface Tension

**Current:** `gamma = 0.022 N/m` (ethanol) - This is correct, keep it.

But add clear documentation:
```python
gamma = st.number_input(
    "Surface tension γ (mN/m)",
    value=22.0,          # Ethanol at room temp
    min_value=15.0,      # Ethanol-water mixtures
    max_value=72.0,      # Pure water
    step=1.0,
    format="%.1f",
    help="Ethanol: ~22 mN/m, Water: ~72 mN/m, Glycerol: ~63 mN/m"
) * 1e-3  # Convert mN/m → N/m
```

### Testing Procedure

After implementing changes:

1. **Sanity check dimensional analysis:**
   ```python
   # Run this test script:
   import math
   epsilon_0 = 8.854e-12
   gamma = 0.022
   L = 10e-3  # 10mm spacing
   
   V_scale = math.sqrt(gamma * L / epsilon_0)
   print(f"Expected onset voltage scale: {V_scale:.0f} V = {V_scale/1000:.1f} kV")
   # Should print: ~5 kV (matches literature)
   ```

2. **Run Mode 2 with new defaults:**
   - Check onset voltage is in 2-5 kV range (not 27 kV)
   - Check recovered angle is still 42-47° (finite-domain artifact persists)
   - Check computation completes without errors

3. **Compare to literature:**
   - Ethanol electrospray onset: 1-3 kV (literature)
   - Your solver should predict: 2-5 kV (acceptable)
   - If outside this range → investigate boundary conditions

### Success Criteria

- ✅ Streamlit app accepts inputs in mm/μm units
- ✅ Domain size scales with electrode spacing (not hardcoded 1m)
- ✅ Predicted onset voltage is 2-5 kV range for ethanol
- ✅ Grid resolution adequate at apex (>3 cells per apex radius)
- ✅ Mode 1 and Mode 2 both run without errors at new scale

### Estimated Time

- **Coding:** 2-3 hours
- **Testing:** 1-2 hours
- **Total:** Half day

---

## Improvement #2: Fix Boundary Conditions to Recover Taylor Angle (49.29°)

### Current State

**Problem:** Mode 2 (immersed verification) recovers 42.5° instead of the theoretical 49.29° Taylor angle.

**Root cause:** The computational domain uses a **finite grounded rectangular box** as the boundary condition:
```
φ = V0    at nozzle (z=0, r<R_nozzle)
φ = 0     at all outer boundaries (r=r_max, z=z_max, top, sides)
```

This truncates the ideal Taylor cone and artificially constrains the electric field, forcing the optimizer to find a shallower angle (42-45°) instead of the theoretical 49.29°.

**Evidence from code:**
- Archive document states: "Grounded-box problem **cannot recover 49.29°**"
- "Larger box → larger argmin angle (45° → 75°+)"
- "This is a **model property, not a bug**"

### Target State

**Goal:** Modify outer boundary conditions so Mode 2 recovers 49.0° ± 1.0° (within discretization error).

**Theoretical basis:**
The ideal Taylor cone exists in an infinite domain. The analytical solution is:
```
φ(r,z) = A·r^α·P_α(cos θ)
```
where `α ≈ 0.5` (from eigenvalue problem) and `P_0.5` is the half-order Legendre function.

At the Taylor angle `θ_T = 49.29°`, the cone surface is an equipotential.

### Implementation Options

#### Option A: Analytical Far-Field Boundary Condition (RECOMMENDED)

**Principle:** Apply the analytical Taylor cone potential at the outer boundaries instead of grounding them.

**Mathematical form:**
```
At r = r_max or z = z_max:
φ(r,z) = V0·(r/r_ref)^0.5·P_0.5(cos(atan2(z,r)))

where:
  - V0 = applied voltage at nozzle
  - r_ref = reference radius (e.g., nozzle radius)
  - P_0.5 = half-order Legendre function
  - atan2(z,r) = angle from axis
```

**Implementation steps:**

1. **Add analytical Taylor potential function:**

   **File:** `backend/solver/boundary_conditions.py` (or create new file `backend/solver/taylor_analytical.py`)

   ```python
   import numpy as np
   from scipy.special import lpmv  # Associated Legendre function
   
   def taylor_cone_potential(r, z, V0, r_ref, theta_taylor_deg=49.29):
       """
       Analytical Taylor cone potential for far-field boundary condition.
       
       Parameters:
       -----------
       r : array_like
           Radial coordinate(s) [m]
       z : array_like
           Axial coordinate(s) [m]
       V0 : float
           Applied voltage at nozzle [V]
       r_ref : float
           Reference radius (typically nozzle radius) [m]
       theta_taylor_deg : float
           Taylor cone half-angle [degrees], default 49.29°
       
       Returns:
       --------
       phi : array_like
           Electric potential [V]
       
       Notes:
       ------
       The analytical Taylor cone solution in spherical coordinates is:
           φ(R,θ) = A·R^α·P_α(cos θ)
       where α ≈ 0.5 and P_0.5 is the half-order Legendre function.
       
       In cylindrical coordinates:
           R = sqrt(r² + z²)
           θ = atan2(r, z)  # Angle from z-axis
       """
       R = np.sqrt(r**2 + z**2)
       theta = np.arctan2(r, z)  # Angle from z-axis (0 at top, π/2 at side)
       
       # Half-order Legendre function P_{1/2}(cos θ)
       # Using associated Legendre: lpmv(m=0, v=0.5, x=cos(theta))
       cos_theta = np.cos(theta)
       P_half = lpmv(0, 0.5, cos_theta)
       
       # Normalize: φ = V0 at some reference point
       # Choose: φ(r=r_ref, θ=0) = V0 (on axis at reference radius)
       R_ref = r_ref
       theta_ref = 0.0
       P_half_ref = lpmv(0, 0.5, np.cos(theta_ref))
       A = V0 / (R_ref**0.5 * P_half_ref)
       
       # Compute potential
       phi = A * R**0.5 * P_half
       
       return phi
   ```

2. **Modify boundary condition application:**

   **File:** `backend/solver/electrostatics.py` (or wherever BCs are applied)

   **Current code (approximately):**
   ```python
   # BEFORE:
   # Apply Dirichlet BC: φ = 0 at all outer boundaries
   phi[r_max_indices] = 0.0
   phi[z_max_indices] = 0.0
   ```

   **Change to:**
   ```python
   # AFTER:
   from solver.taylor_analytical import taylor_cone_potential
   
   # Option to use Taylor far-field BC instead of grounded box
   if use_taylor_farfield_bc:
       # Apply analytical Taylor potential at outer boundaries
       r_boundary, z_boundary = get_boundary_coordinates()
       phi_farfield = taylor_cone_potential(
           r_boundary, 
           z_boundary, 
           V0=applied_voltage,
           r_ref=nozzle_radius
       )
       phi[boundary_indices] = phi_farfield
   else:
       # Original grounded box
       phi[boundary_indices] = 0.0
   ```

3. **Add UI toggle in Streamlit app:**

   ```python
   # In backend/app/streamlit_app.py
   use_taylor_bc = st.checkbox(
       "Use analytical Taylor far-field BC",
       value=True,
       help="Apply Taylor cone potential at outer boundaries instead of grounding. "
            "Allows recovery of 49.29° theoretical angle."
   )
   ```

**Expected results:**
- Recovered angle: 48.5° - 50.0° (within ±1° of Taylor angle)
- Onset voltage: More accurate (less affected by truncation)
- Residual at Taylor angle should be very small

**Challenges:**
- Legendre function `P_0.5` has branch cuts; handle carefully near θ=0 and θ=π
- Normalization constant A must be chosen to match V0 at nozzle
- May need different BC at top (z_max) vs side (r_max) boundaries

---

#### Option B: Enlarged Domain (EASIER, less accurate)

**Principle:** Make the computational box so large that grounded boundaries are far from the cone and don't affect it.

**Rule of thumb:** Domain should be 20-50× larger than the cone region of interest.

**Implementation:**

```python
# In backend/app/streamlit_app.py or solver config:

# BEFORE:
domain_r_max = electrode_spacing * 2.0   # e.g., 20mm for 10mm spacing
domain_z_max = electrode_spacing * 2.5   # e.g., 25mm

# AFTER:
domain_r_max = electrode_spacing * 30.0  # e.g., 300mm for 10mm spacing
domain_z_max = electrode_spacing * 40.0  # e.g., 400mm

# Keep grid resolution fine only near the cone:
# Use stretched/adaptive grid with:
#   - Fine cells (10-20 μm) near axis (r < 1mm, z < 2mm)
#   - Coarse cells (500 μm - 1mm) in far field
```

**Expected results:**
- Recovered angle: 45-47° (improved from 42.5°, but not full 49.29°)
- Onset voltage: Slightly more accurate
- Much larger linear system to solve (slower computation)

**Advantages:**
- Very simple to implement (just change domain size)
- No new BC code needed

**Disadvantages:**
- Computational cost increases significantly
- Still won't fully recover 49.29° (only asymptotically as domain → ∞)
- Requires adaptive grid or you get huge memory usage

---

#### Option C: Hybrid Approach

**Combine Option A (analytical BC) with modest domain enlargement:**

```python
domain_r_max = electrode_spacing * 5.0   # Moderate size (50mm for 10mm)
domain_z_max = electrode_spacing * 7.0   # (70mm)

# Use Taylor analytical BC at these boundaries
use_taylor_farfield_bc = True
```

**Advantages:**
- More accurate than Option B
- More computationally efficient than very large domain
- Boundary is far enough that analytical approximation is valid

---

### Implementation Plan (Option A - RECOMMENDED)

#### Step 2.1: Implement Analytical Taylor Potential Function

**File:** Create `backend/solver/taylor_analytical.py`

Copy the `taylor_cone_potential()` function from above.

**Testing:**
```python
# Test script: backend/tests/test_taylor_analytical.py
import numpy as np
from solver.taylor_analytical import taylor_cone_potential

def test_taylor_potential_on_cone_surface():
    """Verify potential is constant on θ = 49.29° surface"""
    theta_taylor = np.deg2rad(49.29)
    V0 = 1000.0
    r_ref = 1e-3
    
    # Points on the Taylor cone surface at different radii
    z_vals = np.linspace(0.001, 0.01, 10)  # 1mm to 10mm
    r_vals = z_vals * np.tan(theta_taylor)
    
    phi_vals = taylor_cone_potential(r_vals, z_vals, V0, r_ref)
    
    # All values should be nearly equal (constant on equipotential)
    phi_std = np.std(phi_vals)
    phi_mean = np.mean(phi_vals)
    
    assert phi_std / phi_mean < 0.01, "Potential should be constant on cone surface"
```

#### Step 2.2: Modify Boundary Condition Application

**File:** `backend/solver/electrostatics.py` or `backend/solver/boundary_conditions.py`

Add parameter to boundary condition functions:
```python
def apply_boundary_conditions(
    phi, 
    grid, 
    V0, 
    use_taylor_farfield=False,
    nozzle_radius=None
):
    """Apply Dirichlet boundary conditions to potential field"""
    
    if use_taylor_farfield:
        # Get boundary coordinates
        r_outer = grid.r[-1]  # Last radial position
        z_outer = grid.z[-1]  # Last axial position
        
        # Right boundary (r = r_max)
        r_bc = np.full_like(grid.z, r_outer)
        z_bc = grid.z
        phi_bc = taylor_cone_potential(r_bc, z_bc, V0, nozzle_radius)
        phi[-1, :] = phi_bc
        
        # Top boundary (z = z_max)
        r_bc = grid.r
        z_bc = np.full_like(grid.r, z_outer)
        phi_bc = taylor_cone_potential(r_bc, z_bc, V0, nozzle_radius)
        phi[:, -1] = phi_bc
    else:
        # Original grounded box
        phi[-1, :] = 0.0  # r_max
        phi[:, -1] = 0.0  # z_max
    
    # Nozzle BC (always V0)
    nozzle_mask = create_nozzle_mask(grid, nozzle_radius)
    phi[nozzle_mask] = V0
    
    return phi
```

#### Step 2.3: Add UI Control in Streamlit App

```python
# In backend/app/streamlit_app.py (verification section)

with st.expander("Advanced boundary conditions"):
    bc_type = st.radio(
        "Outer boundary condition",
        options=["Grounded box", "Taylor far-field"],
        index=1,  # Default to Taylor far-field
        help="Grounded box: φ=0 at boundaries (recovers ~42-45° angle)\n"
             "Taylor far-field: analytical Taylor potential (recovers ~49° angle)"
    )
    
    use_taylor_bc = (bc_type == "Taylor far-field")
```

Pass this flag through to the solver backend.

### Testing Procedure

1. **Unit test the analytical potential:**
   ```bash
   pytest backend/tests/test_taylor_analytical.py -v
   ```

2. **Run Mode 2 with Taylor BC:**
   - Use realistic mm-scale geometry (after Improvement #1)
   - Enable "Taylor far-field" BC
   - Check recovered angle is 48-50°
   - Check identity ratio still ~1.005

3. **Compare grounded vs Taylor BC:**
   - Run Mode 2 with both BC options
   - Document angle difference in results

### Success Criteria

- ✅ Analytical Taylor potential function passes unit tests
- ✅ Mode 2 with Taylor BC recovers angle in range [48.0°, 50.5°]
- ✅ Angle difference from 49.29° is < 2° (within discretization error)
- ✅ Taylor identity ratio remains ~1.005 (electrostatic solver still accurate)
- ✅ Residual at recovered angle is small (< 0.1 Pa)

### Estimated Time

**Option A (Analytical BC):**
- **Research/derivation:** 2-3 hours (understand Legendre functions)
- **Coding:** 4-6 hours (implement function, integrate into solver)
- **Testing:** 2-3 hours
- **Total:** 1-2 days

**Option B (Enlarged domain):**
- **Coding:** 1 hour (just change domain size parameters)
- **Testing:** 2 hours (check convergence, grid resolution)
- **Total:** 3-4 hours

**Recommendation:** Start with Option B (quick test), then implement Option A if time permits.

---

## Improvement #3: Fix Negative Space-Charge Shielding Metric

### Current State

**Problem:** The computed shielding metric `S_E ≈ -0.7%` is **negative**.

**Why this is wrong:**
- Shielding means space charge *reduces* the electric field near the interface
- A negative metric implies space charge *increases* the field ("anti-shielding")
- This is physically implausible for the Gaussian/threshold closures implemented

**Current abstract claim:**
> "optionally includes effective Gaussian or threshold-activated **space-charge shielding** closures"

**You cannot claim "shielding" with a negative metric.**

### Target State

Either:
1. **Fix the computation** so S_E is positive (correct physics)
2. **Fix the space-charge model** if it's actually producing wrong fields
3. **Remove "shielding" claim** from abstract if unfixable

### Root Cause Investigation

**Location:** The S_E metric is likely computed in `backend/solver/space_charge.py` or `backend/solver/app_backend.py`

**Expected definition:**
```python
# S_E = shielding metric
# Should measure fractional field reduction due to space charge

# Without space charge:
E_n_laplace = compute_normal_field_laplace_only(...)

# With space charge:
E_n_poisson = compute_normal_field_with_space_charge(...)

# Shielding metric:
S_E = (E_n_laplace - E_n_poisson) / E_n_laplace

# Expected: S_E > 0 (field is reduced by space charge)
# Observed: S_E < 0 (field is increased ?!)
```

**Possible bugs:**

1. **Sign error in definition:**
   ```python
   # WRONG:
   S_E = (E_n_poisson - E_n_laplace) / E_n_laplace  # Flipped numerator
   
   # CORRECT:
   S_E = (E_n_laplace - E_n_poisson) / E_n_laplace
   ```

2. **Wrong charge sign:**
   ```python
   # Space charge should have SAME sign as liquid conductor
   # If liquid is at positive voltage, space charge is positive
   # This creates a cloud that SHIELDS the field
   
   # WRONG:
   rho_e = -rho_max * gaussian(...)  # Negative charge (wrong sign!)
   
   # CORRECT:
   rho_e = +rho_max * gaussian(...)  # Positive charge for V0 > 0
   ```

3. **Wrong field direction:**
   ```python
   # E_n should be the OUTWARD normal component from the interface
   # Make sure you're measuring field in gas, not in liquid
   ```

### Implementation Plan

#### Step 3.1: Locate S_E Computation

**Files to check:**
- `backend/solver/space_charge.py`
- `backend/solver/app_backend.py`
- `backend/solver/verification.py`

**Search command:**
```bash
grep -rn "S_E\|shielding_metric" backend/solver/
```

#### Step 3.2: Add Debug Logging

Before fixing, understand what's happening:

```python
# Add to computation of S_E:
import logging
logger = logging.getLogger(__name__)

# Compute fields
E_n_laplace = compute_field_laplace()
E_n_poisson = compute_field_with_space_charge()

logger.info(f"E_n (Laplace only): {E_n_laplace:.3e} V/m")
logger.info(f"E_n (with space charge): {E_n_poisson:.3e} V/m")
logger.info(f"Difference: {E_n_laplace - E_n_poisson:.3e} V/m")

S_E = (E_n_laplace - E_n_poisson) / E_n_laplace
logger.info(f"S_E = {S_E:.4f} ({S_E*100:.2f}%)")

# If S_E < 0, then E_n_poisson > E_n_laplace
# This means space charge is INCREASING the field (wrong!)
```

Run Mode 1 with Gaussian space charge and check the logs.

#### Step 3.3: Fix the Bug

**Based on typical implementations, most likely fixes:**

**Fix A: Correct the sign in S_E definition**

```python
# BEFORE (likely wrong):
S_E = (E_n_poisson - E_n_laplace) / E_n_laplace  # Wrong order

# AFTER:
S_E = (E_n_laplace - E_n_poisson) / E_n_laplace  # Correct

# Interpretation:
# S_E > 0: space charge reduces field (shielding) ✓
# S_E < 0: space charge increases field (anti-shielding) ✗
```

**Fix B: Correct the space charge sign**

```python
# BEFORE (possibly wrong):
rho_e = -rho_max * gaussian_profile(...)  # Negative charge

# AFTER:
# Space charge should have SAME sign as conductor voltage
if V0 > 0:
    rho_e = +rho_max * gaussian_profile(...)  # Positive ions
else:
    rho_e = -rho_max * gaussian_profile(...)  # Negative ions
```

**Fix C: Ensure field is measured on correct side**

```python
# Electric field normal component must be measured in the GAS
# (outside the liquid conductor, pointing away from interface)

# Check that your E_n extraction is sampling the correct region:
E_n = extract_normal_field(phi, interface, side='gas')  # Not 'liquid'
```

#### Step 3.4: Verify Fix with Test Case

Create a test where shielding is obvious:

```python
# backend/tests/test_space_charge_shielding.py

def test_gaussian_space_charge_reduces_field():
    """Verify space charge creates shielding (positive S_E)"""
    
    # Simple parallel-plate geometry
    V0 = 1000.0  # Positive voltage
    spacing = 0.01  # 10mm
    
    # Solve Laplace (no space charge)
    phi_laplace = solve_laplace(V0, spacing)
    E_laplace = compute_field(phi_laplace)
    E_n_laplace = E_laplace[interface_location]
    
    # Solve Poisson (with Gaussian space charge)
    rho_e = gaussian_space_charge(...)
    phi_poisson = solve_poisson(V0, spacing, rho_e)
    E_poisson = compute_field(phi_poisson)
    E_n_poisson = E_poisson[interface_location]
    
    # Check shielding
    S_E = (E_n_laplace - E_n_poisson) / E_n_laplace
    
    assert S_E > 0, f"Space charge should reduce field (got S_E={S_E:.4f})"
    assert 0.001 < S_E < 0.5, f"S_E should be a few percent (got {S_E*100:.1f}%)"
```

Run this test before and after your fix.

#### Step 3.5: Update Paper Claims

**After fixing:**

If `S_E` is now positive (e.g., +2.3%):
```latex
% In abstract:
The solver optionally includes effective Gaussian or threshold-activated 
space-charge shielding closures, demonstrating field reduction of ~2-5%.
```

**If unfixable in time:**

Remove "shielding" claim:
```latex
% In abstract:
The solver optionally includes effective space-charge density models 
(Gaussian or threshold-activated closures) for exploring charge effects.
```

### Testing Procedure

1. **Before fix:**
   - Run Mode 1 with Gaussian space charge
   - Record S_E value (currently ≈ -0.7%)
   - Check debug logs to understand the bug

2. **After fix:**
   - Run same case
   - Verify S_E > 0
   - Run pytest on new shielding test
   - Check S_E magnitude is reasonable (0.5% - 10%)

3. **Physical validation:**
   - S_E should increase with rho_max (more charge → more shielding)
   - S_E should be positive for any physically reasonable parameters

### Success Criteria

- ✅ S_E > 0 for all space-charge models
- ✅ Test case `test_gaussian_space_charge_reduces_field` passes
- ✅ S_E magnitude is reasonable (typically 1-10%)
- ✅ Paper abstract claim is consistent with results

### Estimated Time

- **Investigation:** 1-2 hours (find bug)
- **Fix:** 30 min - 1 hour (usually a sign error)
- **Testing:** 1-2 hours (write test, verify)
- **Total:** 3-5 hours

---

## Implementation Timeline

### Minimum Viable (1 week before experiments):

**Day 1-2: Improvement #1 (Geometry rescaling)**
- 4 hours: Modify Streamlit app inputs
- 2 hours: Test at realistic scale
- 1 hour: Update documentation

**Day 3: Improvement #3 (S_E sign fix)**
- 2 hours: Locate and diagnose bug
- 1 hour: Implement fix
- 2 hours: Test and verify

**Day 4: Improvement #2 (Option B - enlarged domain)**
- 1 hour: Increase domain size
- 2 hours: Test convergence
- 1 hour: Document tradeoffs

**Day 5: Integration testing**
- Run full workflow at new scale
- Verify all modes work
- Update paper with new results

**Result:** Solver is experimentally useful but still has truncation artifact (angle ~45-47°)

---

### Complete Solution (2-3 weeks, if time permits):

**Week 1:**
- Days 1-2: Improvement #1 (4-6 hours)
- Days 3-4: Improvement #3 (4-5 hours)
- Day 5: Initial testing

**Week 2:**
- Days 1-3: Improvement #2 Option A (analytical BC) (8-12 hours)
- Days 4-5: Testing and validation

**Week 3:**
- Integration testing
- Run experiments
- Write up results

**Result:** Solver recovers Taylor angle to within ±1° and provides accurate onset voltage predictions

---

## Success Metrics

After completing all three improvements:

| Metric | Before | After (Minimum) | After (Complete) |
|--------|--------|-----------------|------------------|
| Geometry scale | 1m (wrong) | 0.3-10mm (correct) | 0.3-10mm (correct) |
| Onset voltage | 27.6 kV | 2-5 kV | 2-4 kV |
| Recovered angle | 42.5° | 44-47° | 48.5-50° |
| S_E shielding | -0.7% ✗ | +2-5% ✓ | +2-5% ✓ |
| Experimental comparison | Impossible | Possible | Accurate |

---

## References

**Literature on boundary conditions:**
- [Cambridge J. Fluid Mech - Numerical simulation of electrospraying](https://www.cambridge.org/core/journals/journal-of-fluid-mechanics/article/numerical-simulation-of-electrospraying-in-the-conejet-mode/AE5FA95163D5FC758CB69E76CC2BE5C1): "use of the potential field generated by a semi-infinite Taylor cone as a far-field boundary condition"

**Experimental onset voltage data:**
- Ethanol: 1-3 kV (typical, mm-scale nozzles)
- Water: 2-4 kV
- [Nature Scientific Reports](https://www.nature.com/articles/srep38509.pdf): "stability margin within 1 kV for ethanol"

**Internal documentation:**
- `archive/AI_HANDOVER.md` - Documents known issues
- `archive/docs/plans/2026-08-09-next-steps.md` - S3, S4 items
- Paper Section 7: Experimental methodology

---

## Notes for Future Work

**After these three improvements, consider:**

1. **Add realistic electrode geometry** (needle + extractor plate)
2. **Implement volume/contact-line constraint** (fixes apex radius degeneracy)
3. **Add E_n convergence test** (validates second-order field claim)
4. **Compare to Hartman 1999 onset voltage data** (literature validation)
5. **Implement adaptive/stretched grids** (efficiency at mm-scale)

**Do NOT consider these future items as blocking experimental validation.**

---

**Document version:** 1.0  
**Last updated:** 2026-08-12  
**Author:** Analysis based on solver codebase review and literature comparison
