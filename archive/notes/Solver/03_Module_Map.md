# Module Map

Tags: #solver #software_architecture

This is the planned Python module map. It is not code documentation yet; it is the architecture blueprint.

## Planned package layout

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
  01_laplace_cone_demo.py
  02_poisson_gaussian_shielding.py
  03_threshold_space_charge.py
  04_residual_on_prescribed_interface.py
  05_shape_optimization_demo.py
app/
  streamlit_app.py
```

## Module responsibilities

### `config.py`

Stores parameter dataclasses:

- physical parameters,
- numerical parameters,
- geometry parameters,
- shielding parameters.

### `grid.py`

Creates axisymmetric grid arrays:

- `r`, `z`,
- mesh spacing,
- node indexing,
- flatten/unflatten utilities.

### `geometry.py`

Builds masks:

- gas domain,
- liquid/conductor,
- powered electrode,
- grounded electrode,
- axis,
- far boundary.

### `boundary_conditions.py`

Applies:

- Dirichlet conditions,
- Neumann axis condition,
- far-boundary conditions.

### `operators.py`

Assembles sparse finite-volume/finite-difference operators:

- axisymmetric Laplacian,
- Poisson source insertion,
- optional variable-permittivity operator later.

### `electrostatics.py`

Main solve routines:

- solve Laplace,
- solve Poisson,
- call sparse solvers,
- return potential field.

### `fields.py`

Computes:

- \(E_r=-\partial_r\phi\),
- \(E_z=-\partial_z\phi\),
- \(|E|\),
- interpolation to interface points.

### `interface.py`

Handles interface geometry:

- graph representation \(R(z)\),
- parametric representation,
- normals,
- tangents,
- curvature,
- half-angle extraction.

### `residual.py`

Computes:

- Maxwell pressure,
- capillary pressure,
- Young–Laplace–Maxwell residual,
- RMS and max residual.

### `space_charge.py`

Implements:

- zero charge,
- Gaussian cloud,
- threshold-activated charge,
- fixed-point iteration,
- shielding metric.

### `optimization.py`

Implements:

- shape parameterization,
- residual objective,
- constraints,
- derivative-free optimization initially.

### `verification.py`

Implements tests:

- Taylor-angle benchmark,
- manufactured Poisson solutions,
- grid convergence,
- boundary condition checks.

### `plotting.py`

Produces:

- potential contours,
- field magnitude maps,
- residual plots,
- interface overlays.

### `app_backend.py`

Connects solver modules to future web app inputs/outputs.

Links: [[02_Data_Flow]], [[04_Numerical_Core]], [[08_Verification_and_Tests]]
