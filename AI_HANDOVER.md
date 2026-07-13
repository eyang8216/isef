# AI Handover Document — ISEF Physics Taylor-Cone Solver

**Project folder:** `/Users/a1/ISEF_physics`  
**Project type:** ISEF physics / computational physics / aerospace electrospray modeling  
**Current phase:** Theory + computational solver planning only  
**Do not perform:** Physical experiment planning beyond safety notes, high-voltage instructions, ethanol handling procedures, or testbed construction steps unless explicitly asked later under school-supervised context.

---

## 1. Project summary

This project is an ISEF-oriented computational physics project focused on **Taylor cone formation and electrospray onset** for microfluidic / colloid thruster systems.

The core idea is to build a **lightweight, open-source, consumer-hardware 2D axisymmetric solver** that models the electrostatic-capillary balance of a Taylor cone and extends the ideal charge-free model using a **Poisson space-charge shielding term**.

The long-term scientific goal is to compare simulation predictions against physical electrospray images later, but the current 1.5-month focus is strictly:

1. theory,
2. derivations,
3. numerical formulation,
4. software architecture,
5. eventually a Python/online solver.

The working research question is approximately:

> To what extent can a lightweight 2D axisymmetric Python solver, coupling electrostatic Maxwell stress, capillary pressure, and an effective Poisson space-charge shielding model, predict Taylor-cone geometry and onset-voltage trends for electrospray emitters on consumer-grade hardware?

---

## 2. Important project framing

The project should **not** be framed as a full industrial CFD or complete electrospray emission simulator.

Correct framing:

> A reduced-order axisymmetric electrostatic-capillary solver with effective space-charge shielding.

Avoid overclaiming:

- full transient Navier–Stokes cone-jet dynamics,
- molecular ion evaporation,
- droplet breakup distributions,
- full plasma simulation,
- full Taylor–Melcher leaky-dielectric dynamics unless actually implemented,
- replacement for COMSOL/ANSYS.

The novelty is accessibility + mathematical transparency:

- sparse Python solver,
- open formulation,
- classical Taylor-angle benchmark,
- Poisson shielding extension,
- consumer-hardware runtime.

---

## 3. Current safety / experiment status

The physical experiment is **deferred** until school resumes and approvals/supervision are available.

Do not help build or operate high-voltage hardware in the current phase. The planned experiment may later involve electrospray, ethanol, and high voltage, but for now all work should remain computational.

Safety notes already established:

- ISEF/SRC approval likely required before construction.
- Project may fall under hazardous devices/chemicals due to high voltage and ethanol.
- Current folder focus is theory and solver only.

---

## 4. Key files currently in the folder

### Main deliverables requested by user

#### `theoretical_derivations.pdf`

The main theory PDF. It contains the physics/math derivations needed before coding.

Source:

```text
theoretical_derivations.tex
```

It covers:

- classical Taylor cone derivation,
- 49.3° Taylor angle,
- apex singularity,
- axisymmetric Laplace equation,
- axisymmetric Poisson equation,
- Maxwell stress,
- capillary curvature,
- Young–Laplace–Maxwell residual,
- space-charge shielding closures,
- nondimensionalization,
- theoretical success criteria.

#### `implementation_outline.md`

The CS/coding implementation outline. It explains how to make the model work in code.

It covers:

- product goal,
- computational pipeline,
- proposed repository structure,
- data structures,
- module responsibilities,
- sparse matrix assembly,
- boundary conditions,
- electric field reconstruction,
- interface representation,
- residual computation,
- space-charge iteration,
- shape optimization,
- tests,
- numerical risks,
- milestone plan.

### Earlier combined theory document

#### `theory.pdf`
#### `theory.tex`

Earlier combined theory + implementation-plan PDF. It is still useful but has now been superseded as the main deliverable by:

- `theoretical_derivations.pdf`
- `implementation_outline.md`

### Obsidian vault files

This folder can be opened directly as an Obsidian vault.

Important files:

```text
00_Index.md
Solver_Architecture_Map.canvas
notes/Solver/00_Solver_Architecture_Map.md
notes/Solver/01_Model_Hierarchy.md
notes/Solver/02_Data_Flow.md
notes/Solver/03_Module_Map.md
notes/Solver/04_Numerical_Core.md
notes/Solver/05_Interface_and_Residual.md
notes/Solver/06_Space_Charge_Shielding.md
notes/Solver/07_Shape_Optimization.md
notes/Solver/08_Verification_and_Tests.md
notes/Solver/09_Online_App_Interface.md
notes/Theory/Taylor Cone Theory.md
notes/Theory/Axisymmetric Electrostatics.md
notes/Theory/Young-Laplace-Maxwell Balance.md
notes/Theory/Space Charge Theory.md
notes/Implementation/Implementation_Roadmap.md
notes/Experiment_Later/Experiment_Later.md
```

The Obsidian map is useful for architecture navigation but the user recently requested two clearer separate deliverables. Do not delete the Obsidian vault unless asked.

---

## 5. Current theoretical model

### 5.1 Classical Taylor cone

The analytical benchmark is the classical Taylor cone.

Exterior charge-free potential satisfies:

```math
\nabla^2 \phi = 0
```

Near a conical apex:

```math
\phi(\rho,\vartheta)=A\rho^\nu P_\nu(\cos\vartheta)
```

Stress scaling gives:

```math
\nu=\frac12
```

Conducting cone boundary gives:

```math
P_{1/2}(\cos\vartheta_0)=0
```

Relevant root:

```math
\vartheta_0\approx130.7^\circ
```

Physical semi-vertical angle:

```math
\alpha_T\approx49.3^\circ
```

This must be recovered in the ideal zero-space-charge limit.

### 5.2 Apex singularity

The ideal Taylor solution has:

```math
E\sim\rho^{-1/2}
```

so the field diverges near the apex. The project models regularization through finite numerical resolution and Poisson space-charge shielding.

### 5.3 Axisymmetric electrostatics

Axisymmetric operator:

```math
\nabla^2\phi = \frac{1}{r}\frac{\partial}{\partial r}\left(r\frac{\partial\phi}{\partial r}\right)+\frac{\partial^2\phi}{\partial z^2}
```

Laplace model:

```math
\nabla^2\phi=0
```

Poisson model:

```math
\nabla^2\phi=-\frac{\rho_e}{\varepsilon_0}
```

Boundary conditions:

- powered conductor/liquid: `phi = V0`,
- grounded extractor: `phi = 0`,
- axis: `dphi/dr = 0`,
- far boundary: Dirichlet or Neumann, to be tested.

### 5.4 Maxwell stress and capillary stress

For conducting liquid:

```math
p_E = \frac{\varepsilon_0}{2}E_n^2
```

Axisymmetric graph interface `r = R(z)` curvature:

```math
\kappa = \frac{1}{R\sqrt{1+R_z^2}} - \frac{R_{zz}}{(1+R_z^2)^{3/2}}
```

Young–Laplace–Maxwell residual:

```math
\mathcal R = \gamma\kappa - \Delta p - \frac{\varepsilon_0}{2}E_n^2
```

The solver should quantify residual RMS and use it as the main physical diagnostic.

### 5.5 Space charge closures

First supported closures:

#### Gaussian shielding cloud

```math
\rho_e(r,z)=\rho_0\exp\left[-\frac{(r-r_a)^2+(z-z_a)^2}{2\ell^2}\right]
```

#### Threshold-activated effective charge

```math
\rho_e=\rho_{\max}\left[1-\exp\left(-\frac{|E|-E_c}{E_s}\right)\right]_+
```

Use fixed-point iteration with under-relaxation:

```math
\rho_e^{k+1}=(1-\omega)\rho_e^k+\omega\widetilde\rho_e^{k+1}
```

---

## 6. Intended software architecture

The intended Python structure is described in `implementation_outline.md`.

Recommended package layout:

```text
solver/
  __init__.py
  config.py
  grid.py
  geometry.py
  boundary_conditions.py
  operators.py
  electrostatics.py
  fields.py
  interface.py
  residual.py
  space_charge.py
  optimization.py
  verification.py
  plotting.py
  app_backend.py

examples/
  00_taylor_angle_benchmark.py
  01_laplace_basic_electrodes.py
  02_laplace_cone_field.py
  03_poisson_gaussian_shielding.py
  04_threshold_space_charge.py
  05_interface_residual_demo.py
  06_shape_optimization_demo.py

tests/
  test_grid.py
  test_axis_operator.py
  test_boundary_conditions.py
  test_manufactured_poisson.py
  test_fields.py
  test_curvature.py
  test_space_charge.py

app/
  streamlit_app.py
```

Do not start with the app. Start with numerical core.

Recommended coding order:

```text
1. grid.py
2. operators.py
3. boundary_conditions.py
4. electrostatics.py
5. verification.py manufactured Poisson test
6. fields.py
7. interface.py
8. residual.py
9. space_charge.py Gaussian model
10. space_charge.py threshold model
11. plotting.py
12. optimization.py
13. app_backend.py
14. streamlit_app.py
```

---

## 7. Numerical implementation details to preserve

### 7.1 Sparse matrices only

Use SciPy sparse matrices. Avoid dense matrices.

Matrix system:

```math
A\phi=b
```

Matrix size:

```text
(nr * nz) by (nr * nz)
```

Nonzeros should scale like:

```text
O(nr * nz)
```

not:

```text
O((nr * nz)^2)
```

### 7.2 Grid indexing

Use a consistent flattening convention. Recommended in outline:

```text
k = i * nz + j
```

where:

- `i` = radial index,
- `j` = axial index.

### 7.3 Axis stencil

At `r = 0`, do not divide by `r`. Use:

```math
\lim_{r\to0}\left(\phi_{rr}+\frac{1}{r}\phi_r\right)=2\phi_{rr}(0,z)
```

Discrete radial part:

```math
2\phi_{rr}(0,z_j)\approx\frac{4(\phi_{1,j}-\phi_{0,j})}{\Delta r^2}
```

### 7.4 Dirichlet boundary implementation

For node `k`:

```python
A[k, :] = 0
A[k, k] = 1
b[k] = value
```

### 7.5 Electric field reconstruction

```text
Er = -dphi/dr
Ez = -dphi/dz
E_mag = sqrt(Er^2 + Ez^2)
```

Use central differences inside and one-sided differences at boundaries.

### 7.6 Residual pressure offset

The pressure constant `Delta_p` can initially be eliminated with:

```math
\Delta p = \mathrm{mean}(\gamma\kappa-p_E)
```

Then:

```math
\mathcal R = (\gamma\kappa-p_E)-\mathrm{mean}(\gamma\kappa-p_E)
```

This is useful before full pressure/volume constraints are implemented.

---

## 8. Verification targets

Before claiming the solver works, verify:

1. **Manufactured Poisson solution** — choose known `phi_exact`, compute source, verify convergence.
2. **Axis regularity** — confirm `dphi/dr = 0` at `r=0`.
3. **Dirichlet boundary enforcement** — powered and grounded nodes match assigned potentials.
4. **Voltage scaling** — field scales like `V0`; Maxwell pressure scales like `V0^2`.
5. **Curvature tests** — known simple shapes give correct curvature.
6. **Taylor angle benchmark** — ideal limit approaches `49.3°`.
7. **Shielding sanity test** — Poisson space charge changes/reduces peak field in intended cases.
8. **Runtime scaling** — record runtime and nonzero counts versus grid size.

---

## 9. Current dependencies / tools

LaTeX compiler available:

```text
/Users/a1/miniforge3/bin/tectonic
```

To compile theory PDF:

```bash
cd /Users/a1/ISEF_physics
/Users/a1/miniforge3/bin/tectonic theoretical_derivations.tex
```

Python environment likely has Miniforge. Use:

```bash
python3
```

or Miniforge Python if needed:

```bash
/Users/a1/miniforge3/bin/python
```

When coding starts, likely dependencies:

```text
numpy
scipy
matplotlib
pytest
streamlit  # later
```

Do not assume all are installed. Check first.

---

## 10. What has already been done

Completed:

- Created `/Users/a1/ISEF_physics`.
- Created theory LaTeX and PDF documents.
- Created separated theoretical derivations PDF.
- Created separated implementation outline Markdown file.
- Built Obsidian vault and architecture map.
- Installed/used `tectonic` via Miniforge for LaTeX compilation.

Important files produced:

```text
theoretical_derivations.pdf
theoretical_derivations.tex
implementation_outline.md
theory.pdf
theory.tex
00_Index.md
Solver_Architecture_Map.canvas
AI_HANDOVER.md
```

---

## 11. Recommended next task

The next best task is:

> Start implementing the numerical solver skeleton, beginning with `solver/grid.py`, `solver/operators.py`, `solver/boundary_conditions.py`, and a manufactured Poisson verification test.

Before coding, inspect `implementation_outline.md` and follow its module order.

Suggested first concrete deliverable:

```text
solver/grid.py
solver/operators.py
solver/boundary_conditions.py
solver/electrostatics.py
tests/test_manufactured_poisson.py
examples/01_laplace_basic_electrodes.py
```

Acceptance criteria for first coding milestone:

- Can create a grid.
- Can assemble sparse axisymmetric operator.
- Can apply simple Dirichlet boundaries.
- Can solve a simple Laplace/Poisson case.
- Can pass at least one manufactured solution test.

---

## 12. Communication style with user

The user wants serious physics/math treatment and is comfortable with advanced material. Do not oversimplify unnecessarily.

However, maintain project discipline:

- distinguish theory from implementation,
- distinguish reduced model from full EHD,
- avoid unsafe experiment instructions,
- keep deliverables organized in files,
- use exact paths when reporting work.

The user may ask for professor/lab-assistant style guidance. It is appropriate to challenge assumptions and refine claims.

---

## 13. If another AI continues

Start by reading these files in order:

1. `AI_HANDOVER.md`
2. `implementation_outline.md`
3. `theoretical_derivations.tex` or `theoretical_derivations.pdf`
4. `notes/Solver/03_Module_Map.md`
5. `notes/Solver/04_Numerical_Core.md`
6. `notes/Solver/08_Verification_and_Tests.md`

Then ask the user whether they want to begin solver code implementation or further refine the theory.
