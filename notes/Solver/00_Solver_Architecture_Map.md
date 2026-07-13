# Solver Architecture Map

Tags: #solver #architecture #isef

This is the central map for the lightweight 2D axisymmetric EHD Taylor-cone solver.

## One-sentence architecture

The solver converts a physical parameter set and interface geometry into an axisymmetric electrostatic solution, reconstructs electric fields, evaluates Maxwell pressure and capillary curvature on the interface, computes the Young–Laplace–Maxwell residual, and optionally iterates a Poisson space-charge shielding model.

## Core pipeline

```mermaid
flowchart TD
    A[Input physical parameters] --> B[Build axisymmetric grid]
    B --> C[Build geometry masks]
    C --> D[Assemble Laplace/Poisson sparse matrix]
    D --> E[Solve A phi = b]
    E --> F[Compute electric field Er, Ez, |E|]
    F --> G[Sample interface]
    G --> H[Compute normals and curvature]
    F --> I[Interpolate field to interface]
    H --> J[Compute capillary pressure gamma kappa]
    I --> K[Compute Maxwell pressure eps E_n^2 / 2]
    J --> L[Young-Laplace-Maxwell residual]
    K --> L
    L --> M[Diagnostics: RMS residual, angle, peak field]
    M --> N{Space charge?}
    N -- no --> O[Return solution]
    N -- yes --> P[Update rho_e]
    P --> D
```

## Main architecture notes

- [[01_Model_Hierarchy]] defines the physics levels.
- [[02_Data_Flow]] defines how arrays and parameters move between stages.
- [[03_Module_Map]] defines planned Python modules.
- [[04_Numerical_Core]] owns the sparse electrostatic solve.
- [[05_Interface_and_Residual]] owns curvature, normals, Maxwell pressure, and residuals.
- [[06_Space_Charge_Shielding]] owns the nonlinear Poisson iteration.
- [[07_Shape_Optimization]] owns free-boundary optimization.
- [[08_Verification_and_Tests]] defines what must pass before experiments.
- [[09_Online_App_Interface]] defines the future online interface.

## Solver stages

| Stage | Name | Deliverable |
|---:|---|---|
| 0 | Analytical benchmark | Recover Taylor angle: 49.3° |
| 1 | Laplace electrostatics | Solve axisymmetric charge-free potential |
| 2 | Field reconstruction | Compute electric field and Maxwell pressure |
| 3 | Interface residual | Compute Young–Laplace–Maxwell residual |
| 4 | Poisson shielding | Add prescribed and threshold space charge |
| 5 | Shape optimization | Minimize residual over interface parameters |
| 6 | Online app | Interactive solver with plots and diagnostics |

## Design philosophy

1. **Correct limit first:** recover classical Taylor theory in the zero-space-charge perfect-conductor limit.
2. **Sparse linear algebra:** use SciPy sparse matrices, not dense matrices.
3. **Explicit assumptions:** each solver level has declared assumptions.
4. **Residual-based validation:** never just plot pretty fields; quantify physical residuals.
5. **Consumer hardware:** runtime and memory use are part of the result.
