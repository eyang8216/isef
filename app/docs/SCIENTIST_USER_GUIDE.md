# Taylor-Cone Solver: Scientist User Guide

**For Creators/Developers:** This document explains what scientists will input into the solver and what outputs they will look for, helping you understand the scientific workflow and validate the tool's behavior.

---

## Overview

The Taylor-Cone Solver is designed for researchers studying electrospray onset, colloid thruster design, and electrohydrodynamic cone formation. Users fall into three categories:

1. **Experimental researchers** designing electrospray systems who need onset voltage predictions
2. **Student researchers** learning about Taylor cone physics and numerical methods
3. **Thruster engineers** optimizing colloid propulsion systems

---

## Part 1: What Scientists Input

### 1.1 Physical Configuration (Primary Inputs)

These are the **real physical parameters** of the system being modeled:

#### Geometry
| Parameter | What It Represents | How Scientists Determine It | Typical Values |
|-----------|-------------------|----------------------------|----------------|
| **Electrode spacing** | Distance from emitter tip to grounded plate | Experimental setup dimension | 10–50 mm (benchtop), 1–5 mm (microdevices) |
| **Nozzle radius** | Radial extent of the domain; initial nozzle size | Physical emitter dimension + computational margin | Usually set equal to electrode spacing for square domain |

**Scientific Context:**
- Experimentalists measure these directly from their apparatus
- Computational domain should be large enough that outer boundaries don't affect the solution
- Rule of thumb: nozzle radius ≥ electrode spacing for minimal boundary effects

#### Material Properties
| Parameter | What It Represents | How Scientists Determine It | Typical Values |
|-----------|-------------------|----------------------------|----------------|
| **Surface tension γ** | Fluid's resistance to interface deformation | Literature value or measured (pendant drop, Wilhelmy plate) | Ethanol: 22 mN/m<br>Water: 72 mN/m<br>Formamide: 58 mN/m<br>EMI-Im ionic liquid: ~37 mN/m |

**Scientific Context:**
- This is THE critical material property for electrospray
- Temperature-dependent (typically quoted at 20°C)
- For ionic liquids (colloid thrusters), may need to measure experimentally
- Impurities can significantly affect surface tension

#### Electrical Configuration
| Parameter | What It Represents | How Scientists Determine It | Typical Values |
|-----------|-------------------|----------------------------|----------------|
| **Applied voltage V₀** | Electric potential at emitter relative to ground | Experimental control parameter OR what solver predicts | 1–5 kV (ethanol)<br>2–10 kV (water)<br>Scales with √(γ) and geometry |

**Scientific Context:**
- **Two use modes:**
  1. **Forward problem:** "What field distribution do I get at 3 kV?" → Set V₀, examine fields
  2. **Inverse problem:** "What voltage creates equilibrium?" → Examine residual, infer onset V₀*
- Experimentalists vary this to find onset empirically; solver predicts it theoretically

### 1.2 Physics Options

#### Space-Charge Model
| Option | When Scientists Use It | Physical Meaning | Parameters Needed |
|--------|------------------------|------------------|-------------------|
| **none** | Initial exploration, vacuum electrospray, low current | No ion emission; pure Laplace electrostatics | None |
| **gaussian** | Modeling localized ion cloud from apex | Phenomenological charge cloud with Gaussian spatial distribution | ρ₀ (peak charge density)<br>ℓ (cloud width)<br>(r₀, z₀) (cloud center) |
| **threshold** | Field-emission-driven space charge | Charge density activates above critical field strength | E_c (threshold field)<br>E_s (activation scale)<br>ρ_max (saturation density) |

**Scientific Context:**
- Most fundamental physics studies start with "none" (pure Laplace problem)
- Colloid thruster designers care about space charge—it shields the field and affects performance
- Parameters come from:
  - **Literature:** Lozano (2003), Gamero-Castaño (2002) for ionic liquids
  - **Fitting to experiment:** Adjust until predicted current matches measured
  - **Phenomenological:** These are simplified models, not first-principles predictions

**Typical Values (from literature):**
- **Gaussian:** ρ₀ ~ 10⁻⁹ to 10⁻⁸ C/m³, ℓ ~ 10% of electrode spacing
- **Threshold:** E_c ~ 500 V/m, E_s ~ 300 V/m, ρ_max ~ 10⁻⁸ C/m³

### 1.3 Diagnostic Interface Parameters

| Parameter | What It Represents | How Scientists Choose It | Typical Value |
|-----------|-------------------|-------------------------|---------------|
| **Interface half-angle θ** | Angle of prescribed diagnostic cone | Set to Taylor angle for equilibrium check, or sweep to find equilibrium | **49.3°** (Taylor angle)<br>Or sweep 30°–60° |

**Scientific Context:**
- This is **NOT** a solution—it's a diagnostic input
- Scientists ask: "If the interface were at this angle, what would the residual be?"
- Two workflows:
  1. **Single-angle diagnostic:** Set θ = 49.3° and check how close the residual is to zero
  2. **Angle sweep (verification mode):** Vary θ and find where power-law exponent satisfies scaling

### 1.4 Numerical Parameters (Convergence Control)

| Parameter | What It Controls | How Scientists Choose It | Typical Values |
|-----------|-----------------|-------------------------|----------------|
| **Grid resolution (nr × nz)** | Mesh density | Trade accuracy vs. speed | Coarse: exploration<br>Medium: routine work<br>Fine: publication |
| **Under-relaxation ω** | Iteration stability | Reduce if not converging | 0.5 (default)<br>0.2–0.3 (if unstable) |
| **Max iterations** | Convergence patience | Increase if nearly converging | 50 (default)<br>100+ (challenging cases) |

**Scientific Context:**
- **Grid convergence is critical** for publishable results
- Scientists should run at multiple resolutions and verify solution doesn't change significantly
- Under-relaxation is a "knob to turn" when things don't converge—not a physical parameter

---

## Part 2: What Scientists Look For (Outputs)

### 2.1 Primary Scalar Diagnostics

These are the **key numbers** scientists report in papers and use for design decisions:

#### Interface Balance Metrics

| Output | Physical Meaning | What Scientists Want to See | Red Flags |
|--------|-----------------|----------------------------|-----------|
| **RMS residual [Pa]** | How far the prescribed interface is from Young-Laplace-Maxwell equilibrium | **< 1 Pa:** Good balance<br>**< 0.1 Pa:** Excellent | **> 10 Pa:** Far from equilibrium |
| **Peak field magnitude [V/m]** | Maximum electric field in domain (usually at apex) | Compare to literature for similar geometry<br>Check it's not absurdly high (breakdown) | **> 10⁹ V/m:** Likely unphysical (air breakdown ~3×10⁶ V/m) |

**Scientific Interpretation:**
- **Residual = 0** would mean exact equilibrium (never achieved numerically, but close is good)
- Residual has units of **pressure** because it's the imbalance between capillary pressure (Pa) and Maxwell stress (also Pa)
- Scientists compare residuals across different angles to find which angle minimizes it

#### Onset Voltage Prediction

| Output | Physical Meaning | How to Interpret | Validation |
|--------|-----------------|------------------|------------|
| **Predicted onset voltage V₀* [kV]** | The voltage at which the interface would be in equilibrium | Should scale as:<br>V₀* ∝ √γ<br>V₀* ∝ (geometry length scale) | Compare to:<br>- Experimental measurements<br>- Literature (Gamero-Castaño 2008)<br>- Scaling laws |

**Scientific Context:**
- This is what **experimentalists care most about**: "What voltage do I set my power supply to?"
- Predicted V₀* from residual analysis should be close to the input V₀ used—if not, iterate
- For ethanol in typical geometry: expect 1.5–3.5 kV (literature range)

#### Convergence Indicators

| Output | What It Tells You | What Scientists Want | Troubleshooting |
|--------|------------------|---------------------|-----------------|
| **Converged (Yes/No)** | Did space-charge iteration reach steady state? | **Yes** | **No:** Reduce ω, increase iterations, check if parameters are physical |
| **Iterations** | How many fixed-point steps | < 30: good convergence<br>< 50: acceptable | = max: didn't converge (solution invalid) |
| **Runtime [s]** | Computational cost | < 1 s: fast<br>1–5 s: acceptable<br>> 10 s: may want coarser grid | — |

**Scientific Context:**
- **Convergence is mandatory** for space-charge models—non-converged solutions are meaningless
- Scientists should always report whether solutions converged in papers
- High iteration count (but converged) is acceptable but suggests near-instability

#### Space-Charge Shielding Metric

| Output | Physical Meaning | Interpretation | Typical Range |
|--------|-----------------|----------------|---------------|
| **Shielding metric S_E** | Ratio of field strength with space charge to vacuum field | < 1: field is reduced (shielded)<br>= 1: no shielding<br>> 1: field enhanced (rare) | 0.5–0.95 (typical)<br>Strong shielding: 0.3–0.5 |

**Scientific Context:**
- Only meaningful when space-charge model is active
- Colloid thruster designers use this to assess performance degradation from ion cloud
- Lower S_E → more shielding → lower thrust efficiency

### 2.2 Field Visualizations

Scientists examine these plots to understand the **physics** of their system:

#### Electric Potential φ(r, z)

**What scientists look for:**
- ✅ Smooth contours (no oscillations)
- ✅ Potential decreases monotonically from emitter (top) to ground (bottom)
- ✅ Near-apex: steep gradients (high field region)
- ❌ Red flags: Wiggles, non-monotonic behavior, asymmetries

**Scientific use:**
- Visualize voltage distribution
- Check boundary conditions are correctly enforced
- Identify field penetration depth

#### Electric Field Magnitude |E|(r, z)

**What scientists look for:**
- ✅ Peak at cone apex (expected for sharp geometry)
- ✅ Field decays away from apex following ~r^(-1/2) (Taylor scaling)
- ✅ Smooth spatial variation
- ❌ Red flags: Multiple peaks, oscillations, unrealistically high values

**Scientific use:**
- **Critical for breakdown assessment:** Is peak field below air breakdown (~3 MV/m)?
- Check field distribution matches theoretical expectations (power-law decay)
- Estimate emission current (J ∝ E² in many models)

**Comparison to Literature:**
- Fernández de la Mora (2007): Apex field should scale as E_apex ~ V₀ / r_apex
- For r_apex ~ 50 μm and V₀ ~ 3 kV: expect E_apex ~ 60 MV/m (in liquid, not air)

#### Interface Overlay on Potential

**What scientists look for:**
- ✅ Prescribed cone sits in a physically reasonable location
- ✅ Cone angle relative to field lines makes sense
- ❌ Red flags: Cone intersects boundaries, geometry doesn't match expectations

**Scientific use:**
- Sanity check that diagnostic geometry is correctly specified
- Visualize how the prescribed interface relates to the field distribution

#### Young-Laplace-Maxwell Residual Profile

**What scientists look for:**
- ✅ Small magnitude (< 1 Pa everywhere, ideally)
- ✅ Smooth variation along the interface
- ✅ Pattern: Often positive near apex (field dominates), negative on flank (if angle is wrong)
- ❌ Red flags: Huge spikes, sign changes indicating far from equilibrium

**Scientific use:**
- **Most important diagnostic plot** for assessing equilibrium
- Identify where on the interface the forces are out of balance
- If residual is uniformly small → close to equilibrium
- If residual has systematic trend → angle is wrong, or voltage is wrong

**Physical Interpretation:**
- **Positive residual:** Maxwell stress > capillary pressure → interface wants to expand outward
- **Negative residual:** Capillary pressure > Maxwell stress → interface wants to contract inward
- **Zero residual:** Perfect balance (goal)

#### Space-Charge Distribution ρ(r, z)

**What scientists look for (if using space-charge model):**
- ✅ Charge cloud localized near emission region (apex or specified location)
- ✅ Magnitude consistent with expected current density
- ✅ Smooth spatial distribution
- ❌ Red flags: Charge everywhere, unphysical negative values, oscillations

**Scientific use:**
- Visualize where ions are emitted and how they distribute
- Assess whether phenomenological model is behaving reasonably
- Check that ρ_max is not exceeded (for threshold model)

### 2.3 Verification-Specific Outputs

When scientists run the **Immersed Verification** mode, they look for different outputs:

#### Recovered Angle

| Output | Physical Meaning | What Scientists Want | Validation |
|--------|-----------------|---------------------|------------|
| **Recovered angle θ_recovered [°]** | Angle where flank field exponent crosses p = -1 (scale consistency) | **49.2°–49.3°** (within 0.5° of theoretical 49.29°) | **Must converge to 49.29° as grid refines**<br>Fast grid: ~49.1°<br>Fine grid: ~49.2°<br>Very Fine: ~49.23° |

**Scientific Context:**
- This is **code verification**—proves the solver implements the physics correctly
- NOT a prediction for a real system (it's a test case with idealized boundaries)
- Scientists should report grid convergence: show angle → 49.29° as mesh refines

**How to Report in Papers:**
> "The immersed boundary operator recovers the theoretical Taylor angle of 49.29° to within 0.1° at the Fine grid (121×177), demonstrating second-order convergence and correct implementation of the Young-Laplace-Maxwell balance."

#### Taylor Identity Ratio V₀*/A*

| Output | Physical Meaning | What Scientists Want | Validation |
|--------|-----------------|---------------------|------------|
| **Identity ratio** | Ratio of numerically projected voltage to exact analytical amplitude | **0.99–1.01** (within 1% of 1.000) | Shows onset voltage projection is accurate |

**Scientific Context:**
- Tests the **onset projection algorithm**
- Imposes exact Taylor solution → projects voltage → should get exact amplitude back
- Ratio ≠ 1.0 indicates numerical error (grid too coarse, boundary conditions wrong)

#### Minimum Residual

| Output | Physical Meaning | What Scientists Want |
|--------|-----------------|---------------------|
| **Min RMS residual [Pa]** | Smallest residual found across angle sweep | **< 0.1 Pa** (excellent)<br>**< 1.0 Pa** (acceptable) |

**Scientific Context:**
- The angle where residual is minimized should be near the recovered angle
- Very small residual → numerical solution is accurately representing equilibrium

---

## Part 3: Scientific Workflows

### Workflow 1: Onset Voltage Prediction for Experimental Design

**Goal:** An experimentalist wants to know what voltage to expect for their fluid/geometry.

**Steps:**
1. **Input:** Set γ (fluid property), electrode spacing, nozzle radius (apparatus dimensions)
2. **Input:** Set space-charge model to "none" (start simple)
3. **Input:** Set interface angle to 49.3° (Taylor angle)
4. **Input:** Guess a voltage (e.g., 3 kV based on literature)
5. **Run solver**
6. **Examine:** RMS residual
   - If residual ≈ 0: V₀ is close to onset → this is the prediction
   - If residual >> 0: V₀ is too low or too high → adjust and rerun
7. **Output:** Report predicted V₀* and compare to literature

**What to report:**
- "For ethanol (γ = 22 mN/m) in a 10 mm electrode spacing geometry, the solver predicts an onset voltage of 2.9 kV, consistent with Gamero-Castaño (2008) who measured 2.5–3.2 kV for similar conditions."

### Workflow 2: Field Distribution Analysis

**Goal:** Understand where the peak field is and whether breakdown will occur.

**Steps:**
1. **Input:** Configure realistic system (from Workflow 1)
2. **Run solver**
3. **Examine:** Field magnitude plot
   - Locate peak (should be at apex)
   - Check magnitude: Is it < 3 MV/m (air breakdown)?
4. **Examine:** Potential contours
   - Verify smooth, monotonic behavior
5. **Output:** Report peak field and location

**What to report:**
- "The peak electric field of 1.8 MV/m occurs at the cone apex (r ≈ 0, z ≈ 8.6 mm), well below the air breakdown threshold of 3 MV/m, indicating stable operation is feasible."

### Workflow 3: Space-Charge Effects (Colloid Thruster Design)

**Goal:** Assess how ion emission reduces field strength (degrades thrust).

**Steps:**
1. **Run baseline:** Set space-charge model to "none", record peak field E₀
2. **Run with space charge:** Set model to "gaussian" or "threshold" with literature parameters
3. **Examine:** Shielding metric S_E = E_shielded / E₀
4. **Examine:** Space-charge distribution plot—is it localized as expected?
5. **Output:** Report shielding percentage

**What to report:**
- "Including a Gaussian space-charge distribution (ρ₀ = 5 nC/m³, ℓ = 1 mm) reduces the apex field by 25% (S_E = 0.75), indicating moderate shielding effects consistent with Lozano (2003) for ionic liquid ion sources."

### Workflow 4: Code Verification (For Developers/Validators)

**Goal:** Prove the solver correctly implements the physics (for publication, peer review).

**Steps:**
1. **Navigate to Verification tab**
2. **Run:** Immersed verification at multiple grid resolutions (Fast, Fine, Very Fine)
3. **Record:** Recovered angle at each resolution
4. **Check:** Does angle → 49.29° as grid refines? (It should)
5. **Record:** Taylor identity ratio (should be ≈ 1.000)
6. **Output:** Create a table showing convergence

**What to report:**
```
Grid Resolution | Recovered Angle | Error from 49.29° | Identity Ratio
----------------|-----------------|-------------------|---------------
Fast (31×45)    | 49.08°          | -0.21°            | 0.998
Fine (121×177)  | 49.21°          | -0.08°            | 1.001
Very Fine       | 49.23°          | -0.06°            | 1.000
```

"The solver demonstrates second-order spatial convergence, recovering the theoretical Taylor angle to within 0.1° at the Fine grid."

---

## Part 4: Red Flags for Creators

As a developer, watch for these signs that scientists might be misusing the tool or encountering bugs:

### Input Red Flags

| Red Flag | Problem | Likely User Error |
|----------|---------|-------------------|
| Electrode spacing << nozzle radius | Nonsensical geometry | User misunderstood which parameter is which |
| γ > 100 mN/m | Unrealistic surface tension | Typo, or used wrong units (should be mN/m, not N/m) |
| V₀ > 50 kV | Absurdly high voltage for lab scale | Unit confusion or unrealistic scenario |
| Space-charge ρ₀ > 10⁻⁶ C/m³ | Unphysically high charge density | User guessing parameters without literature reference |
| Interface angle < 20° or > 70° | Outside Taylor cone range | User doesn't understand what this parameter does |

### Output Red Flags

| Red Flag | Likely Cause | Troubleshooting |
|----------|--------------|-----------------|
| RMS residual > 100 Pa | Far from equilibrium OR bug | Check if V₀ is reasonable, check if geometry makes sense |
| Peak field > 10⁹ V/m | Unphysical | Check apex radius (might be too small), check voltage |
| Recovered angle < 40° or > 55° | Grid too coarse OR boundary condition wrong | Verify using Taylor far-field BC, refine grid |
| Identity ratio < 0.9 or > 1.1 | Numerical error | Grid too coarse, or immersed boundary implementation bug |
| Converged = No (always) | Space-charge parameters unstable | Reduce ω, increase iterations, check ρ parameters |

---

## Part 5: Parameter Ranges Quick Reference

For creators validating test cases:

### Conservative (Should Always Work)

```python
# Ethanol, standard benchtop scale
gamma = 0.022               # N/m
electrode_spacing = 0.010   # m (10 mm)
nozzle_radius = 0.010       # m (10 mm)
V0 = 2500                   # V (2.5 kV)
space_charge_model = "none"
interface_half_angle_deg = 49.3
nr, nz = 31, 51             # Medium grid
```

**Expected outputs:**
- RMS residual: 0.1–1 Pa
- Peak field: 0.5–2 MV/m
- Onset voltage: 2–3.5 kV
- Converged: Yes
- Runtime: < 1 second

### Challenging (Should Still Work, But Tests Solver)

```python
# Water, large domain, fine grid
gamma = 0.072
electrode_spacing = 0.020
nozzle_radius = 0.020
V0 = 5000
space_charge_model = "gaussian"
rho0 = 1e-9
ell = 0.002
interface_half_angle_deg = 49.3
nr, nz = 61, 91
```

**Expected outputs:**
- RMS residual: 0.5–2 Pa
- Peak field: 1–3 MV/m
- Shielding metric: 0.7–0.9
- Converged: Yes (may take 20–40 iterations)
- Runtime: 2–5 seconds

### Edge Case (May Fail, But Should Fail Gracefully)

```python
# Extreme space charge (testing limits)
space_charge_model = "threshold"
rho_max = 1e-7              # Very high
E_c = 100                   # Very low threshold
E_s = 50
relaxation = 0.2            # Very slow
sc_max_iterations = 200
```

**Expected behavior:**
- May not converge (Converged = No)
- Should NOT crash
- Should NOT produce NaN or Inf
- Should display warning about non-convergence

---

## Part 6: Validation Checklist for Creators

Before releasing updates, verify these test cases:

### ✅ Basic Functionality
- [ ] Ethanol preset loads and runs without error
- [ ] Water preset loads and runs without error
- [ ] All plots render without crashing
- [ ] Results JSON writes successfully

### ✅ Numerical Correctness
- [ ] Verification recovers 49.2° ± 0.3° at Fine grid
- [ ] Taylor identity ratio is 0.99–1.01 at Fine grid
- [ ] Grid refinement reduces error (convergence)

### ✅ Physical Plausibility
- [ ] Onset voltages in literature range (1–5 kV for ethanol)
- [ ] Peak fields reasonable (0.5–5 MV/m for typical cases)
- [ ] Space charge reduces field (S_E < 1.0)

### ✅ Edge Cases
- [ ] Very coarse grid doesn't crash (may be inaccurate, but runs)
- [ ] High space charge converges or reports non-convergence gracefully
- [ ] Cache clears and reruns give identical results

### ✅ User Experience
- [ ] All parameter tooltips are accurate
- [ ] Units are clearly labeled
- [ ] Error messages are helpful (not just stack traces)
- [ ] Plots have proper axes labels and titles

---

## Conclusion

Scientists using this tool are primarily interested in:

1. **Onset voltage predictions** (V₀*) to guide experimental design
2. **Field distributions** to assess breakdown risk and understand physics
3. **Space-charge effects** (shielding metric) for thruster performance
4. **Code verification** (recovered angle, identity ratio) for publication

As creators, your role is to ensure:
- ✅ Inputs are clearly documented with physical meaning and units
- ✅ Outputs are interpretable and scientifically meaningful
- ✅ Red flags (convergence failures, unphysical results) are surfaced prominently
- ✅ Validation cases match literature and theory

This tool bridges **numerical methods** (finite differences, immersed boundaries) with **physical insight** (Taylor cones, electrospray onset). Your goal is to make that bridge robust, understandable, and trustworthy for the scientific community.

---

**Document Version:** 1.0
**Last Updated:** 2026-08-23
**Authors:** Elliott Dong (for creator reference)
