# Taylor-Cone Electrospray Validation: Lab Support Request

**Students:** Ethan Yang, Elliot Dong, Curtis Lau  
**Institution:** Independent Schools Foundation Academy, Hong Kong SAR  
**Project:** ISEF Computational Physics Research  
**Date:** September 2026

---

## Executive Summary

We have developed a validated computational solver that predicts the shape of electrically charged liquid surfaces (Taylor cones) using fundamental physics equations. To complete our ISEF research project, we need supervised lab access to perform a controlled experimental validation comparing our predictions against real optical measurements of electrospray cone formation.

**What we need:** High-voltage power supply (0-5 kV), optical imaging setup, liquid handling equipment, and qualified supervision for a 3-week experimental validation campaign.

---

## What We Built

### The Solver
We created a specialized computational tool that solves the coupled electrostatics and surface-tension problem for axisymmetric Taylor cones. The solver:

- Implements second-order accurate finite-difference methods on adaptive grids
- Uses immersed boundary techniques to represent moving liquid-gas interfaces
- Predicts interface shapes, cone angles, and onset voltages from first principles
- Has been verified against theoretical benchmarks (Taylor's 49.3° analytical result)
- Passes 71 automated unit and integration tests
- Runs in ~1 second per solve on standard hardware

### Current Status
**Computational verification: Complete**
- Numerical convergence proven (second-order accurate)
- Taylor amplitude identity satisfied within 3%
- Classical benchmark reproduced within ~1.3°
- Grid resolution studies show consistent behavior
- Code is documented, version-controlled, and reproducible

**Physical validation: Not yet performed**  
This is what we need lab support for.

---

## Why Experimental Validation Matters

A computational model without experimental comparison is incomplete science. We need to demonstrate that our solver predicts real physical behavior, not just mathematical consistency. The validation will:

1. **Test predictive accuracy:** Does the solver predict the correct cone angle and shape for a real liquid meniscus under high voltage?

2. **Establish regime validity:** Under what conditions (voltage, geometry, flow rate) does the static electrostatic-capillary model remain accurate?

3. **Quantify model limitations:** Where does the reduced-order approximation break down (dynamic jets, charge transport, space charge effects)?

4. **Meet scientific standards:** ISEF and peer-reviewed research require evidence that computational predictions match physical reality.

---

## Experimental Design Summary

### Overview
We will image a charged liquid meniscus under controlled voltage, extract its profile using computer vision, and compare the measured cone angle and shape against frozen solver predictions. The validation uses a **preregistered protocol** to prevent post-hoc parameter fitting.

### Key Design Features

**1. Controlled Variables**
- Fixed nozzle geometry (inner/outer diameter, material, length)
- Fixed electrode spacing and configuration
- Documented fluid properties (surface tension, density, permittivity, conductivity)
- Applied voltage with calibrated measurement
- Flow rate control and stability criteria

**2. Measured Observables**
- Interface profile R(z) via optical imaging
- Cone half-angle α from fitted flank region
- Onset voltage (deformation threshold and cone-jet transition)
- Repeatability across multiple trials
- Frame-to-frame stability metrics

**3. Validation Protocol**
- **Step 1:** Calibrate optical system (pixel scale, distortion, alignment)
- **Step 2:** Commission apparatus (stable operating window, safety verification)
- **Step 3:** Freeze solver prediction (no tuning after this point)
- **Step 4:** Collect experimental data (voltage sweeps, repeated trials)
- **Step 5:** Process images with blinded pipeline (validated on synthetic data)
- **Step 6:** Compare frozen prediction against measured profiles

**4. Scientific Rigor**
- Preregistered hypotheses (documented before data collection)
- Frozen prediction package (commit hash, tamper-evident record)
- Blinded image processing (pipeline validated on synthetic images first)
- Declared acceptance criteria (uncertainty-based, not arbitrary thresholds)
- Full metadata recording (geometry, fluid, voltage, imaging, environment)
- Raw data preservation (never overwritten)

### Realistic Validation Scope

**What the experiment CAN validate:**
- Static interface geometry under near-onset conditions
- Cone flank angle prediction for matched geometry and voltage
- Trends under controlled geometry or voltage changes
- Qualitative Taylor-cone formation

**What it CANNOT validate (model limitations):**
- Transient jet dynamics (outside static model scope)
- Charge transport and space charge effects (not included in solver)
- Droplet breakup and spray (requires full electrohydrodynamics)
- High-conductivity or high-flow regimes (dynamic behavior dominates)

The realistic outcome is a **tiered validation statement**: image-analysis validity → static interface-shape comparison → controlled trend comparison → limited onset-voltage comparison.

---

## Equipment and Resources Required

### Essential Equipment
1. **High-voltage power supply**
   - Range: 0-5 kV DC, adjustable
   - Current limiting: <1 mA for safety
   - Voltage accuracy: ±1% or calibrated measurement
   - Remote control/monitoring capability (preferred)

2. **Optical imaging system**
   - High-speed or standard video camera (≥30 fps, ≥1024×768 resolution)
   - Macro lens or microscope objective (field of view ~5-20 mm)
   - Backlighting or shadowgraphy setup
   - Stable mount and optical table

3. **Liquid handling**
   - Precision syringe pump (0.1-10 mL/hr, adjustable)
   - Stainless steel or glass capillary nozzles (21-27 gauge)
   - Working fluid: ethanol, water, or formamide (documented properties)
   - Clean glassware and fluid preparation area

4. **Safety and enclosure**
   - Grounded Faraday cage or enclosure with viewing window
   - Interlock system (door switches, emergency stop)
   - Current-limiting resistor in HV circuit
   - Proper grounding and discharge procedure
   - Fume extraction (for volatile fluids)
   - PPE: insulated gloves, safety glasses, lab coat

5. **Calibration and measurement**
   - Digital calipers or microscope for nozzle diameter
   - Calibration target (printed checkerboard or machined scale)
   - Multimeter for voltage verification (if accessible)
   - Temperature and humidity logging (if available)

### Consumables
- Working fluids (ethanol, DI water, formamide): ~100-500 mL total
- Disposable pipettes and beakers
- Cleaning solvents (isopropanol, acetone)
- Paper towels, Kim wipes

### Software (We Provide)
- Image-processing pipeline (Python: OpenCV, NumPy, SciPy, matplotlib)
- Solver codebase (fully documented, version-controlled)
- Analysis scripts for profile extraction and validation metrics
- All code is open-source and runs on standard computers

---

## Timeline and Commitment

### Estimated Duration: 3 weeks (flexible)

**Week 1: Setup and Commissioning**
- Apparatus assembly and safety review
- Optical calibration and alignment
- Synthetic image validation (test pipeline on simulated data)
- Initial fluid characterization and low-voltage tests
- Establish stable operating window

**Week 2: Data Collection**
- Baseline geometry: voltage sweeps, repeated trials
- Document onset conditions and stability regimes
- Capture video sequences at multiple voltage steps
- Monitor repeatability and system stability
- Adjust protocol if needed (with supervisor approval)

**Week 3: Validation and Analysis**
- Process experimental images with frozen pipeline
- Extract profiles, angles, and onset voltages
- Compare against frozen solver predictions
- Quantify agreement, uncertainty, and limitations
- Document results and archive raw data

**Lab Access Requirements:**
- 2-4 hour sessions, 2-3 times per week
- Supervised by qualified teacher or lab manager
- Flexible scheduling around school/lab availability
- Data analysis and writing performed off-site

---

## Safety Plan

### Risk Assessment
**Primary hazards:**
- High voltage (electric shock)
- Flammable liquids (ethanol)
- Sharp needles (puncture)
- Liquid spills (slip hazard, contamination)

### Mitigation Measures
1. **High-voltage safety**
   - All HV components inside grounded enclosure
   - Interlock prevents access during energized operation
   - Current limiting to <1 mA (painful but non-lethal)
   - Discharge procedure before any access
   - No solo operation (supervisor or partner always present)

2. **Chemical safety**
   - Material Safety Data Sheets (MSDS) reviewed for all fluids
   - Fume extraction for volatile liquids
   - Spill kit and cleanup procedure
   - No open flames or ignition sources
   - Proper waste disposal

3. **Mechanical safety**
   - Needles handled with forceps, never bare hands
   - Sharps container for disposal
   - Stable mounting (no loose cables or hanging equipment)
   - Clear workspace, no clutter

4. **Training and supervision**
   - Safety briefing before first session
   - Supervised by qualified teacher or lab manager
   - Emergency contact and first aid kit accessible
   - School safety protocols followed

### Institutional Approval
**This experiment will not proceed without:**
- Supervisor review and written approval
- School safety office or risk assessment review
- Parental consent (if required for minors)
- Compliance with all school and institutional policies

---

## Why Support This Project

### Educational Value
- Bridges computational and experimental physics
- Teaches rigorous scientific methodology (preregistration, blinding, uncertainty quantification)
- Develops practical lab skills (optics, high-voltage, data analysis)
- Demonstrates iterative model validation process
- Prepares students for university-level research

### Scientific Merit
- Addresses a real gap: most Taylor-cone studies use commercial codes or simplified models
- Lightweight, transparent solver suitable for student research and education
- Validation data will inform model limitations and future extensions
- Results publishable in student research journals and ISEF competition

### Institutional Benefits
- Showcases school's lab capabilities and research support
- Potential for co-authorship or acknowledgment in ISEF paper
- Demonstrates commitment to student-led experimental work
- Low cost, low risk, high educational impact

---

## Expected Outcomes

### Best-Case Scenario
- Solver predicts cone angle within experimental uncertainty (±1-2°)
- Profile RMSE within image-processing noise floor
- Onset voltage trend matches simulation qualitatively
- Result supports static electrostatic-capillary model within its regime
- **Conclusion:** Model validated for geometry predictions under controlled conditions

### Realistic Scenario
- Cone angle agreement at baseline geometry
- Some profile mismatch near apex or base (expected due to finite-radius effects)
- Onset voltage shows trend but quantitative mismatch (due to missing dynamics)
- **Conclusion:** Tiered validation - geometry supported, full onset requires extended model

### Worst-Case Scenario
- Large angle discrepancy or profile mismatch
- Onset voltage completely wrong
- **Conclusion:** Model limitations identified, solver requires correction or extended physics

**All outcomes are scientifically valuable.** A negative result identifies where the model fails and guides future improvements. A positive result establishes the solver's predictive capability.

---

## Student Background and Preparedness

**Computational Experience:**
- Python programming (NumPy, SciPy, matplotlib, OpenCV)
- Numerical methods (finite differences, optimization, linear algebra)
- Version control (Git), testing (pytest), documentation
- 71 automated tests written and passing

**Theoretical Background:**
- Electrostatics (Laplace equation, boundary conditions)
- Surface tension and capillarity (Young-Laplace equation)
- Taylor cone theory and electrohydrodynamics literature
- Numerical verification and validation concepts

**What We Still Need to Learn:**
- Hands-on high-voltage safety procedures
- Optical imaging calibration and alignment
- Experimental data collection and repeatability
- Real-world troubleshooting (bubbles, contamination, instabilities)

**This is exactly why we need lab access and supervision.**

---

## Contact and Next Steps

We are ready to schedule an initial meeting to:
1. Present our computational results and validation plan in detail
2. Tour the lab facility and assess available equipment
3. Discuss timeline, safety requirements, and institutional approval process
4. Refine the experimental protocol based on available resources
5. Prepare formal safety documentation and approval requests

**Contact Information:**  
[Student email addresses]  
[Supervising teacher contact]  
[School name and address]

**Supporting Materials Available:**
- Full ISEF paper (LaTeX, with theory and validation sections)
- Solver codebase (GitHub repository with documentation)
- Verification test results (71 passing tests, convergence studies)
- Example simulation outputs (cone profiles, voltage landscapes)
- Preliminary image-processing pipeline (tested on synthetic data)

---

## References

Key literature supporting our validation approach:

1. **Taylor (1964)** - Original theoretical framework for electrostatic cones
2. **Fernández de la Mora (2007)** - Comprehensive review of Taylor cone fluid dynamics
3. **Cloupeau & Prunet-Foch (1989, 1994)** - Electrospray operating modes and stability regimes
4. **Hartman et al. (1999)** - Experimental cone-jet characterization with geometry effects
5. **Zhang (2000)** - Camera calibration method for optical measurements
6. **Karimi et al. (2019)** - Counter-electrode geometry effects on onset

All citations properly documented in our bibliography with DOIs.

---

## Appendix: Validation Methodology Audit

**Experimental design review (completed September 2026):**

✅ **Scientific rigor verified:**
- Preregistration protocol prevents post-hoc fitting
- Blinded image processing (validated on synthetic data first)
- Frozen prediction package (tamper-evident)
- Declared acceptance criteria (uncertainty-based)

✅ **Literature support confirmed:**
- All major claims cited with DOIs verified
- Geometry and fluid property effects documented (Hartman, Karimi)
- Operating regime variations recognized (Cloupeau)
- Calibration method standard (Zhang)

✅ **Realistic scope defined:**
- Model limitations clearly stated
- Static vs. dynamic physics distinguished
- Tiered validation outcome specified
- No overclaims about full electrospray dynamics

✅ **Safety and ethics integrated:**
- Institutional approval required before operation
- Comprehensive safety controls specified
- Supervisor involvement mandatory
- Emergency procedures defined

✅ **Reproducibility ensured:**
- Full metadata recording protocol
- Raw data preservation requirements
- Software and commit tracking
- Uncertainty propagation methodology

**Conclusion:** The validation methodology is scientifically sound, properly scoped, and ready for implementation with qualified supervision.
