# Implementation Outline: Lightweight Axisymmetric Taylor-Cone Electrospray Solver

**Project:** ISEF Physics — electrospray / Taylor cone computational solver  
**File purpose:** CS/coding plan only. This document explains how to turn the theory into a working Python model. It intentionally avoids experimental hardware.

---

## 1. Product goal

Build a lightweight Python solver that can:

1. solve 2D axisymmetric Laplace/Poisson electrostatics on an `(r, z)` grid,
2. compute electric field components,
3. evaluate Maxwell pressure on a candidate liquid interface,
4. compute capillary curvature of the interface,
5. compute the Young–Laplace–Maxwell residual,
6. optionally iterate a space-charge shielding model,
7. display fields, interface shape, residuals, and convergence metrics,
8. run on consumer hardware using sparse matrices.

The first product is not a full CFD simulator. It is a reduced-order electrostatic-capillary solver with optional Poisson shielding.

---

## 2. High-level computational pipeline

```text
Physical parameters
    ↓
Grid generation
    ↓
Geometry and boundary masks
    ↓
Sparse matrix assembly for axisymmetric Laplace/Poisson operator
    ↓
Boundary condition insertion
    ↓
Solve A phi = b
    ↓
Compute electric field Er, Ez, |E|
    ↓
Sample candidate interface
    ↓
Compute normals and curvature
    ↓
Interpolate electric field to interface
    ↓
Compute Maxwell pressure and capillary pressure
    ↓
Compute Young-Laplace-Maxwell residual
    ↓
Diagnostics, plots, optional optimization
    ↓
Optional space-charge update loop
```

For space charge, the pipeline becomes iterative:

```text
initialize rho_e
repeat:
    solve Poisson equation
    compute electric field
    update rho_e from shielding closure
    under-relax rho_e
until convergence
```

---

## 3. Proposed repository structure

```text
ISEF_physics/
  theoretical_derivations.pdf
  implementation_outline.md

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

---

## 4. Core data structures

Use Python `dataclasses` for parameters and state.

### 4.1 `PhysicalParams`

Stores physical constants and experiment-like inputs.

```python
@dataclass
class PhysicalParams:
    V0: float                 # applied voltage [V]
    gamma: float              # surface tension [N/m]
    eps_g: float              # gas permittivity [F/m]
    eps_l: float | None       # liquid permittivity, optional
    sigma_l: float | None     # liquid conductivity, optional
    length_scale: float       # characteristic L [m]
```

### 4.2 `GridParams`

```python
@dataclass
class GridParams:
    r_max: float
    z_min: float
    z_max: float
    nr: int
    nz: int
```

### 4.3 `SolverParams`

```python
@dataclass
class SolverParams:
    linear_solver: str        # "spsolve", "cg", "bicgstab", etc.
    tolerance: float
    max_iterations: int
    use_dimensionless: bool
```

### 4.4 `SpaceChargeParams`

```python
@dataclass
class SpaceChargeParams:
    model: str                # "none", "gaussian", "threshold"
    rho0: float | None
    ell: float | None
    apex_r: float | None
    apex_z: float | None
    E_c: float | None
    E_s: float | None
    rho_max: float | None
    relaxation: float         # omega
```

### 4.5 Runtime objects

Important runtime objects:

```text
Grid
  r: array[nr]
  z: array[nz]
  R, Z: meshgrid arrays
  dr, dz
  flatten/unflatten utilities

GeometryMask
  gas: bool[nr, nz]
  powered: bool[nr, nz]
  grounded: bool[nr, nz]
  axis: bool[nr, nz]
  far_boundary: bool[nr, nz]
  conductor: bool[nr, nz]

FieldState
  phi: float[nr, nz]
  Er: float[nr, nz]
  Ez: float[nr, nz]
  E_mag: float[nr, nz]
  rho_e: float[nr, nz]
```

---

## 5. Module responsibilities

### 5.1 `grid.py`

Responsibilities:

- create 1D arrays `r`, `z`,
- create meshgrid arrays `R`, `Z`,
- store `dr`, `dz`,
- define array flattening convention,
- provide `idx(i, j)` and `unidx(k)`.

Important decision:

```text
k = i * nz + j
```

or

```text
k = j * nr + i
```

Pick one and use it everywhere. Recommended:

```text
k = i * nz + j
```

because `i` is radial index and `j` is axial index.

---

### 5.2 `geometry.py`

Responsibilities:

- construct masks for powered boundary, grounded boundary, axis, far boundary, gas, and conductor,
- support simple initial geometries:
  - flat plate electrode,
  - conical conducting boundary,
  - rounded cone,
  - nozzle + meniscus approximation.

Initial geometry should be simple. Do not start with arbitrary CAD.

First supported cases:

1. rectangular domain with top/bottom electrodes,
2. conical conductor held at `V0`,
3. grounded extractor plate.

---

### 5.3 `operators.py`

Responsibilities:

- build sparse axisymmetric Laplacian matrix,
- correctly handle the `1/r` cylindrical term,
- correctly handle `r=0` axis condition,
- return matrix `A` and base RHS vector `b`.

Interior stencil for radial part:

```text
(1 / (r_i dr)) * [
  r_{i+1/2} (phi[i+1,j] - phi[i,j]) / dr
  - r_{i-1/2} (phi[i,j] - phi[i-1,j]) / dr
]
```

Axial part:

```text
(phi[i,j+1] - 2 phi[i,j] + phi[i,j-1]) / dz^2
```

Axis stencil at `i = 0`:

```text
radial_part ≈ 4 * (phi[1,j] - phi[0,j]) / dr^2
```

Implementation detail:

- assemble using `scipy.sparse.lil_matrix` or COO triplets,
- convert to CSR before solving.

---

### 5.4 `boundary_conditions.py`

Responsibilities:

- apply Dirichlet rows,
- apply Neumann rows/ghost approximations,
- keep boundary condition logic separate from operator construction.

Dirichlet implementation:

```python
A[k, :] = 0
A[k, k] = 1
b[k] = value
```

Boundary categories:

```text
powered conductor: phi = V0
grounded electrode: phi = 0
axis: dphi/dr = 0
far boundary: either phi = chosen value or dphi/dn = 0
```

---

### 5.5 `electrostatics.py`

Responsibilities:

- high-level `solve_laplace(...)`,
- high-level `solve_poisson(...)`,
- call operator builder,
- call boundary condition applier,
- call sparse solver,
- reshape solution into `(nr, nz)`.

Main function sketch:

```python
def solve_electrostatics(grid, masks, physical, rho_e=None):
    A, b = build_axisymmetric_operator(grid)
    if rho_e is not None:
        b += build_poisson_rhs(grid, rho_e, physical.eps_g)
    A, b = apply_boundary_conditions(A, b, masks, physical)
    phi_flat = sparse_solve(A.tocsr(), b)
    return phi_flat.reshape((grid.nr, grid.nz))
```

---

### 5.6 `fields.py`

Responsibilities:

- compute gradients of potential,
- compute electric field,
- interpolate fields to interface points.

Field components:

```text
Er = -dphi/dr
Ez = -dphi/dz
E_mag = sqrt(Er^2 + Ez^2)
```

Use central differences in the interior and one-sided differences at boundaries.

Interpolation:

- start with bilinear interpolation,
- later use `scipy.interpolate.RegularGridInterpolator`.

---

### 5.7 `interface.py`

Responsibilities:

- represent candidate liquid surface,
- compute derivatives,
- compute normals,
- compute curvature,
- estimate cone half-angle.

First representation:

```python
class GraphInterface:
    z_samples: ndarray
    R_samples: ndarray
```

Curvature:

```text
kappa = 1 / (R * sqrt(1 + R_z^2)) - R_zz / (1 + R_z^2)^(3/2)
```

Half-angle extraction:

1. choose a near-apex fitting window,
2. fit `R ≈ m z + c`,
3. compute `alpha = arctan(|m|)`.

Need to be careful with coordinate orientation. If the cone points in the opposite `z` direction, use the absolute slope.

---

### 5.8 `residual.py`

Responsibilities:

- compute normal electric field,
- compute Maxwell pressure,
- compute capillary pressure,
- compute residual,
- compute scalar diagnostics.

Definitions:

```text
E_n = Er * n_r + Ez * n_z
p_E = 0.5 * eps_g * E_n^2
p_gamma = gamma * kappa
R = p_gamma - Delta_p - p_E
```

Pressure offset handling:

The pressure offset `Delta_p` can initially be chosen to minimize RMS residual analytically:

```text
Delta_p = mean(gamma*kappa - p_E)
```

Then residual becomes:

```text
R = (gamma*kappa - p_E) - mean(gamma*kappa - p_E)
```

This removes the unknown constant pressure offset from the first residual tests.

Diagnostics:

```text
rms_residual
max_abs_residual
mean_residual
half_angle
peak_field
peak_maxwell_pressure
```

---

### 5.9 `space_charge.py`

Responsibilities:

- define `rho_e` models,
- implement fixed-point Poisson iteration,
- track convergence,
- compute shielding metric.

Models:

#### Zero charge

```python
rho_e = zeros_like(phi)
```

#### Gaussian charge cloud

```python
rho_e = rho0 * exp(-((R-apex_r)**2 + (Z-apex_z)**2) / (2*ell**2))
```

#### Threshold charge

```python
rho_new = rho_max * (1 - exp(-(E_mag - E_c)/E_s))
rho_new[E_mag < E_c] = 0
```

Fixed-point iteration:

```python
rho = initial_rho()
for k in range(max_iter):
    phi = solve_poisson(rho)
    Er, Ez, E_mag = compute_fields(phi)
    rho_candidate = update_rho(E_mag)
    rho_next = (1 - omega) * rho + omega * rho_candidate
    if converged(rho_next, rho, phi):
        break
    rho = rho_next
```

Convergence checks:

```text
relative change in rho_e
relative change in phi
relative change in peak E
max iteration count
```

Shielding metric:

```text
S_E = 1 - Emax_shielded / Emax_laplace
```

---

### 5.10 `optimization.py`

Responsibilities:

- define parameterized interface shapes,
- evaluate residual objective,
- enforce smoothness/geometric constraints,
- run low-dimensional optimization.

Initial approach:

- do **not** use moving meshes at first,
- do **not** optimize hundreds of boundary points,
- use 2–6 shape parameters only.

Candidate shape:

```text
R(z; a) = R_base(z) + sum_k a_k B_k(z)
```

Objective:

```text
J(a) = RMS_residual(a)^2 + lambda * smoothness_penalty(a)
```

Recommended first optimizers:

- `scipy.optimize.minimize(..., method="Nelder-Mead")`,
- `Powell`,
- later finite-difference gradients.

---

### 5.11 `verification.py`

Responsibilities:

- keep tests scientific, not just software-based,
- generate reproducible numerical evidence.

Verification cases:

1. manufactured Poisson solution,
2. axis regularity test,
3. Dirichlet boundary test,
4. voltage scaling test,
5. curvature test on known curves,
6. Taylor angle benchmark,
7. shielding sanity test,
8. runtime scaling test.

---

### 5.12 `plotting.py`

Responsibilities:

- potential contour plots,
- electric field magnitude plots,
- space-charge density plots,
- interface overlay,
- residual along interface,
- convergence history.

Use `matplotlib` first. Avoid fancy visual dependencies until the core solver works.

---

### 5.13 `app_backend.py` and `app/streamlit_app.py`

Responsibilities:

- connect solver components to a future UI,
- expose physical parameters,
- run simulations on button click,
- display plots and scalar diagnostics.

UI inputs:

```text
voltage
surface tension
electrode spacing
nozzle radius
grid resolution
space-charge model
space-charge parameters
```

UI outputs:

```text
potential contour
electric field magnitude
space-charge density
interface residual plot
half-angle estimate
peak field
shielding metric
runtime
```

---

## 6. Development milestones

## Milestone 0 — Setup

Deliverables:

- package skeleton,
- dependency list,
- example runner,
- basic plotting utilities.

Dependencies:

```text
numpy
scipy
matplotlib
pytest
streamlit   # later, for app
```

---

## Milestone 1 — Grid and operator

Deliverables:

- grid generation,
- sparse axisymmetric Laplace operator,
- correct axis treatment,
- simple Dirichlet boundary solve.

Acceptance criteria:

- solves without dense matrices,
- matrix shape is `(nr*nz, nr*nz)`,
- number of nonzeros scales like `O(nr*nz)`, not `O((nr*nz)^2)`.

---

## Milestone 2 — Manufactured Poisson test

Use an exact function, for example:

```text
phi_exact(r,z) = r^2 + z^2
```

Compute:

```text
axisymmetric_laplacian(phi_exact)
```

and set the Poisson RHS accordingly.

Acceptance criteria:

- numerical solution converges under grid refinement,
- error decreases at approximately expected finite-difference order away from boundary/mask complications.

---

## Milestone 3 — Field reconstruction

Deliverables:

- `Er`, `Ez`, `E_mag`,
- voltage scaling test.

Acceptance criteria:

- if voltage doubles, field approximately doubles,
- Maxwell pressure approximately quadruples.

---

## Milestone 4 — Interface geometry

Deliverables:

- graph interface class,
- normals,
- curvature,
- half-angle extraction.

Acceptance criteria:

- curvature is correct for simple test shapes,
- line/cone angle extraction works on synthetic data.

---

## Milestone 5 — Residual evaluation

Deliverables:

- Maxwell pressure on interface,
- capillary pressure on interface,
- residual profile and RMS residual.

Acceptance criteria:

- residual changes sensibly with voltage,
- pressure offset can be eliminated by mean subtraction,
- bad shapes have larger residual than optimized/better shapes.

---

## Milestone 6 — Space-charge shielding

Deliverables:

- Gaussian charge model,
- threshold charge model,
- fixed-point iteration,
- shielding metric.

Acceptance criteria:

- Poisson solution changes relative to Laplace solution,
- shielding metric is stable under moderate grid refinement,
- iteration converges for reasonable relaxation values.

---

## Milestone 7 — Shape optimization

Deliverables:

- low-dimensional interface parameterization,
- objective function,
- first optimizer run.

Acceptance criteria:

- objective decreases during optimization,
- optimized shape has a meaningful half-angle,
- ideal limit approaches Taylor-like angle behavior.

---

## Milestone 8 — Online prototype

Deliverables:

- Streamlit app,
- interactive inputs,
- plots,
- diagnostics table.

Acceptance criteria:

- user can run Laplace and Poisson cases,
- app returns plots and metrics,
- app reports runtime and grid size.

---

## 7. Testing strategy

Use `pytest` for software tests and example scripts for scientific demonstrations.

Test categories:

```text
unit tests:
  grid indexing
  boundary masks
  operator dimensions
  field differences
  curvature calculation

numerical tests:
  manufactured solution error
  grid convergence
  voltage scaling
  Poisson source sign

physics sanity tests:
  Taylor angle benchmark
  shielding reduces intended peak field
  residual behaves with voltage and geometry
```

Every bug-prone physics convention should have a test:

- sign of electric field,
- sign of Poisson source,
- sign of normal vector,
- sign of curvature,
- interpretation of cone angle.

---

## 8. Numerical risks and mitigation

| Risk | Why it matters | Mitigation |
|---|---|---|
| Wrong `1/r` term | Breaks axisymmetric physics | finite-volume radial operator + manufactured tests |
| Axis singularity | `r=0` division error | special axis stencil |
| Dense matrix usage | impossible at high grid size | SciPy sparse CSR matrices |
| Boundary mask errors | wrong physical geometry | plot masks before solving |
| Noisy curvature | residual becomes meaningless | smooth interface basis, not raw noisy points |
| Wrong normal sign | Maxwell residual sign error | test on known geometries |
| Wrong Poisson sign | shielding becomes anti-shielding | sign test with known charge distribution |
| Unstable fixed-point iteration | nonlinear model oscillates | under-relaxation and convergence logging |
| Overclaiming physics | weakens ISEF defense | explicitly label reduced-order assumptions |

---

## 9. Definition of a working first version

Version 1 is working when it can do all of this:

1. build a 2D axisymmetric grid,
2. solve Laplace with sparse matrices,
3. solve Poisson with a known source,
4. reconstruct electric fields,
5. compute interface curvature and normals,
6. compute Maxwell pressure and residual,
7. run a Gaussian shielding case,
8. output plots and scalar diagnostics,
9. pass manufactured-solution and grid-refinement tests.

Version 2 adds:

1. threshold-activated nonlinear charge,
2. shape optimization,
3. Streamlit interface.

Version 3, later, may add:

1. leaky-dielectric liquid potential,
2. surface charge conservation,
3. current-constrained shielding,
4. experimental computer-vision comparison.

---

## 10. Suggested first coding order

Do not start with the app. Build the numerical engine first.

Recommended order:

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

At each step, write a tiny runnable example before moving on.

---

## 11. What not to implement first

Avoid these until the core solver is correct:

- full Navier–Stokes,
- arbitrary moving meshes,
- 3D geometry,
- droplet breakup,
- molecular ion evaporation,
- complex CAD import,
- GPU acceleration,
- fancy web UI,
- experimental camera pipeline.

These are distractions before the Laplace/Poisson + residual engine works.

---

## 12. Final architecture summary

The code should be built around one central idea:

```text
Given a geometry and physical parameters,
solve electrostatics,
compute electric stress,
compare it to capillary stress,
and quantify the mismatch.
```

Everything else — space charge, shape optimization, app interface, and later experiment comparison — should plug into that core loop.
