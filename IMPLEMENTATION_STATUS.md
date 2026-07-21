# Implementation Status — Version 1 Solver Core

Status: first high-quality numerical core implemented.

## Implemented modules

- `solver/config.py` — parameter dataclasses and constants.
- `solver/grid.py` — axisymmetric grid and fixed flattening convention `k = i*nz + j`.
- `solver/geometry.py` — simple rectangular and conical mask builders.
- `solver/operators.py` — sparse axisymmetric Laplace/Poisson operator with special `r=0` stencil.
- `solver/boundary_conditions.py` — Dirichlet row replacement and arbitrary-value manufactured boundary support.
- `solver/electrostatics.py` — high-level Laplace/Poisson solve entry points using SciPy sparse `spsolve`.
- `solver/fields.py` — electric field reconstruction and bilinear interpolation.
- `solver/interface.py` — graph interface `R(z)`, normals, curvature, half-angle extraction.
- `solver/residual.py` — Maxwell pressure, capillary pressure, and Young-Laplace-Maxwell residual diagnostics.
- `solver/space_charge.py` — Gaussian charge density and relaxed Poisson shielding solve scaffold.
- `solver/verification.py` — manufactured-solution verification utilities.
- `solver/plotting.py` — minimal matplotlib helpers.

## Tests

Current test command:

```bash
cd /Users/a1/ISEF_physics
/Users/a1/miniforge3/bin/python -m pytest -q
```

Current result:

```text
21 passed
```

Tests cover:

- grid indexing and flatten/unflatten convention,
- sparse axisymmetric operator including `r=0` regularized axis stencil,
- arbitrary Dirichlet row replacement,
- far-boundary Dirichlet precedence,
- classical Taylor angle benchmark from the Legendre root,
- manufactured Poisson exact quadratic sanity case,
- nontrivial quartic manufactured Poisson convergence under refinement,
- electric field derivative signs,
- bilinear interpolation,
- simple curvature and half-angle extraction,
- parallel-plate voltage scaling,
- Gaussian charge-density construction,
- Poisson RHS sign convention,
- region-of-interest shielding metric behavior.

## Examples

Runnable examples:

```bash
/Users/a1/miniforge3/bin/python examples/00_manufactured_poisson.py
/Users/a1/miniforge3/bin/python examples/01_parallel_plate_laplace.py
/Users/a1/miniforge3/bin/python examples/02_gaussian_space_charge.py
/Users/a1/miniforge3/bin/python examples/03_interface_residual_demo.py
/Users/a1/miniforge3/bin/python examples/04_taylor_angle_benchmark.py
```

## Important caveats

- The Gaussian space-charge module is currently a controlled Poisson source experiment, not a physically complete emission model.
- The global `Emax` shielding metric can be dominated by boundary/corner fields. `solver/space_charge.py`'s `shielding_metric()` now accepts an optional apex-local ROI mask to address this (see `results/v1_numerical_report.md` §5); remaining work is validating the ROI's sign/closure against measurements or a transport model, not building the ROI metric itself.
- The interface residual is diagnostic only. It does not yet optimize a free boundary.
- The conical conductor geometry is a simple grid mask for field visualization, not a sharp immersed-boundary/free-boundary method.
- Threshold-activated charge, shape optimization, and the Streamlit app remain Version 2+.
