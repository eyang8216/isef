# Running the Version 1 Solver Core

This document explains how to run and interpret the current solver implementation.

## Environment

The local machine currently has the required scientific Python stack installed in Miniforge:

```bash
/Users/a1/miniforge3/bin/python
```

Run all commands from the repository root:

```bash
cd /Users/elliottdong/Desktop/isef
```

Install the solver package and dependencies (uses `.venv` if present):

```bash
python -m pip install -e ".[app,dev]"
```

`pyproject.toml` is the single source of truth for dependencies — the optional
`app` extra adds plotly and streamlit, `dev` adds pytest. For the solver core
alone, `python -m pip install -e .` is enough.

## Run tests

```bash
/Users/a1/miniforge3/bin/python -m pytest -q
```

Current expected result:

```text
21 passed
```

These tests verify:

- grid indexing convention `k = i*nz + j`,
- sparse axisymmetric Laplace operator,
- special `r=0` axis stencil,
- Poisson RHS sign convention,
- Dirichlet boundary row replacement,
- manufactured Poisson convergence,
- electric field sign and voltage scaling,
- curvature and half-angle extraction,
- residual null behavior,
- Gaussian charge-density construction,
- region-of-interest shielding metric behavior,
- classical Taylor angle from the Legendre root.

## Generate the numerical report

```bash
/Users/a1/miniforge3/bin/python scripts/generate_v1_report.py
```

This writes:

```text
results/v1_numerical_report.md
results/v1_manufactured_convergence.csv
```

The report includes:

1. classical Taylor angle benchmark,
2. quartic manufactured Poisson convergence,
3. voltage scaling sanity check,
4. residual null sanity check,
5. Gaussian space-charge scaffold diagnostics.

## Run individual examples

```bash
/Users/a1/miniforge3/bin/python examples/00_manufactured_poisson.py
/Users/a1/miniforge3/bin/python examples/01_parallel_plate_laplace.py
/Users/a1/miniforge3/bin/python examples/02_gaussian_space_charge.py
/Users/a1/miniforge3/bin/python examples/03_interface_residual_demo.py
/Users/a1/miniforge3/bin/python examples/04_taylor_angle_benchmark.py
```

## Important interpretation caveats

### This is not full CFD

The solver is a reduced-order electrostatic-capillary model. It is not a full Navier-Stokes, cone-jet breakup, plasma, or molecular emission simulator.

### The Gaussian charge model is a scaffold

The Gaussian `rho_e` model is useful for testing the Poisson source path and studying sensitivity to charge placement/sign/scale. It is not yet a physically predictive emission-current model.

### Global peak-field metrics can mislead

The global peak electric field may occur at electrode corners or artificial far boundaries, not at the cone apex. For shielding claims, use a region-of-interest mask near the apex and compare against experiments or a better transport closure.

### The residual is diagnostic

`solver.residual.compute_residual(...)` evaluates the Young-Laplace-Maxwell mismatch for a prescribed interface. It does not yet optimize the free boundary.

## Next implementation steps

High-value next steps are:

1. add a conical immersed-boundary/electrode example with field maps,
2. improve region-of-interest apex diagnostics,
3. add threshold-activated space charge as Version 2,
4. implement low-dimensional shape optimization,
5. eventually wrap the solver in a Streamlit app.
