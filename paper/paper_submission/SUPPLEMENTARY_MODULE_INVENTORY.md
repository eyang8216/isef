# Supplementary solver module inventory

This uncompiled inventory preserves the implementation map removed from the main manuscript's workflow-focused Solver Architecture section (Section 4 in the revised manuscript).

| Module | Responsibility |
| --- | --- |
| `config.py` | Parameter dataclasses for physical, grid, solver, and space-charge settings |
| `grid.py` | Axisymmetric grid and indexing convention |
| `operators.py` | Sparse Laplace/Poisson finite-difference operator |
| `boundary_conditions.py` | Dirichlet boundary insertion |
| `electrostatics.py` | Laplace/Poisson solve entry points |
| `taylor_analytical.py` | Analytical Taylor-cone potential for far-field boundary conditions |
| `fields.py` | Electric-field reconstruction and interpolation |
| `geometry.py` | Rounded cap--flank cone geometry |
| `immersed.py` | Fractional-distance immersed Dirichlet stencils |
| `interface.py` | Interface geometry, curvature, and half-angle extraction |
| `residual.py` | Young--Laplace--Maxwell residual diagnostics |
| `space_charge.py` | Gaussian and threshold space-charge closures |
| `optimization.py` | Cone-family shape optimization with amplitude projection |
| `verification.py` | Manufactured-solution and Taylor-angle verification helpers |
| `app_backend.py` | Streamlit-independent backend for the interactive app |
| `experimental/image_processing.py` | Image preprocessing and contour extraction |
| `experimental/profile_extraction.py` | Pixel-to-profile conversion and half-angle fitting |
| `experimental/synthetic_validation.py` | Synthetic image rendering and extraction tests |
| `experimental/comparison.py` | Profile alignment and geometric error metrics |
