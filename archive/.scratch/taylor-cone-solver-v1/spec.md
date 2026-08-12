# Spec: Axisymmetric Electrostatic-Capillary Solver — Version 1

Status: ready-for-agent

**Source docs:** `theoretical_derivations.tex`/`.pdf`, `implementation_outline.md`,
`notes/Solver/*`, `notes/Theory/*`, `AI_HANDOVER.md`.

## Problem Statement

The project needs a way to check, computationally, whether the classical
Taylor-cone electrostatic-capillary balance — extended with an effective
Poisson space-charge shielding term — actually predicts sensible cone
geometry and field behavior, before any physical electrospray experiment is
attempted. Right now that check can only be done by hand on paper; there is
no runnable model. Nothing in `solver/`, `tests/`, or `examples/` exists yet
— the repository currently contains only the theory derivation and the
architecture plan.

Without a working solver, the theoretical claims (49.3° Taylor angle in the
ideal limit, shielding reducing peak field, residual behavior under voltage
scaling) remain unverified, and the ISEF project has no computational
deliverable to show or to later compare against experimental images.

## Solution

Build the numerical core of a lightweight, open-source 2D axisymmetric
electrostatic-capillary solver in Python, using sparse matrices throughout so
it runs on consumer hardware. "Version 1" (per `implementation_outline.md`
§9) is the slice where the solver can: build a grid, solve Laplace and
Poisson electrostatics, reconstruct fields, compute interface curvature and
the Young–Laplace–Maxwell residual, run one space-charge shielding closure
(Gaussian), and produce plots and scalar diagnostics — all validated by a
manufactured-solution test and per-module unit tests.

This is explicitly a reduced-order solver, not a full CFD/EHD simulator (see
Out of Scope). The novelty is mathematical transparency and accessibility,
not completeness.

## User Stories

1. As the ISEF researcher, I want to construct a 2D axisymmetric `(r, z)` grid from simple parameters (`r_max`, `z_min`, `z_max`, `nr`, `nz`), so that I can define the computational domain without hand-writing array indexing.
2. As the researcher, I want a single, consistent flattening convention between 2D `(i, j)` grid indices and the 1D linear-system index, so that every module agrees on how `phi` is laid out in memory.
3. As the researcher, I want grid utility functions to convert between `(i, j)` and the flattened index `k`, so that boundary and operator code never re-derives the indexing scheme.
4. As the researcher, I want simple named geometries (rectangular domain with flat-plate electrodes; conical conductor at `V0` with a grounded extractor plate), so that I can test the solver against recognizable configurations before attempting arbitrary shapes.
5. As the researcher, I want boolean masks identifying which grid nodes are powered, grounded, on-axis, or on the far boundary, so that boundary conditions can be applied without re-deriving geometry logic in every module.
6. As the researcher, I want a sparse assembly of the axisymmetric Laplacian operator, so that the solver can scale to fine grids without exhausting memory on consumer hardware.
7. As the researcher, I want the operator's radial term to use the correct finite-volume `1/r` cylindrical discretization, so that the physics is not silently wrong away from the axis.
8. As the researcher, I want a special-cased axis stencil at `r = 0` (the `2*phi_rr` regularized limit), so that the solver never divides by zero and axis regularity (`dphi/dr = 0`) holds automatically.
9. As the researcher, I want Dirichlet boundary conditions applied as identity rows in the sparse matrix (`A[k,:]=0; A[k,k]=1; b[k]=value`), so that powered and grounded nodes are enforced exactly regardless of the interior stencil.
10. As the researcher, I want the far-domain boundary condition to be a configurable parameter (Dirichlet `phi=0` by default) rather than hardcoded, so that I can test how far-boundary placement affects the solution near the cone.
11. As the researcher, I want boundary-condition logic kept in its own module separate from operator assembly, so that changing a boundary type doesn't require touching the finite-difference stencil code.
12. As the researcher, I want a high-level `solve_laplace(...)` entry point, so that I can solve the charge-free case with one function call.
13. As the researcher, I want a high-level `solve_poisson(...)` entry point that accepts an optional space-charge density, so that the same code path handles both the ideal and shielded cases.
14. As the researcher, I want the linear system solved via a sparse direct solver (`scipy.sparse.linalg.spsolve`) by default, so that Version 1 prioritizes correctness and simplicity over solver performance tuning.
15. As the researcher, I want the solved potential reshaped back into `(nr, nz)` form, so that downstream field/plotting code can work with grid-shaped arrays instead of flat vectors.
16. As the researcher, I want electric field components `Er = -dphi/dr` and `Ez = -dphi/dz` computed with central differences in the interior and one-sided differences at boundaries, so that field values are available everywhere on the grid, including edges.
17. As the researcher, I want `|E|` computed from `Er` and `Ez`, so that I have a single scalar field for shielding thresholds and diagnostics.
18. As the researcher, I want field values interpolated (bilinear to start) onto arbitrary interface sample points, so that Maxwell pressure can be evaluated on a candidate liquid surface that doesn't align with grid nodes.
19. As the researcher, I want to represent a candidate liquid interface as a graph `R(z)` with sampled points, so that I have a concrete, differentiable geometric object to compute curvature and normals on.
20. As the researcher, I want interface curvature computed from the axisymmetric graph-curvature formula, so that capillary pressure can be evaluated along the candidate surface.
21. As the researcher, I want a half-angle estimator that fits a line to interface points near the apex and takes `arctan(|slope|)`, so that I can report a single cone-angle number comparable to the 49.3° theoretical value.
22. As the researcher, I want the half-angle extraction to use absolute slope regardless of `z`-axis orientation, so that the estimate doesn't silently flip sign if the cone points the other way.
23. As the researcher, I want the normal electric field `E_n`, Maxwell pressure `p_E = 0.5*eps_g*E_n^2`, and capillary pressure `p_gamma = gamma*kappa` computed on the interface, so that I can form the Young–Laplace–Maxwell residual.
24. As the researcher, I want the unknown constant pressure offset `Delta_p` eliminated by mean-subtraction (`Delta_p = mean(gamma*kappa - p_E)`), so that I can evaluate the residual shape before a full pressure/volume constraint is implemented.
25. As the researcher, I want scalar diagnostics (RMS residual, max residual, mean residual, half-angle, peak field, peak Maxwell pressure) computed for any given case, so that I can compare configurations numerically rather than only visually.
26. As the researcher, I want a Gaussian space-charge closure `rho_e(r,z) = rho0 * exp(-((r-r_a)^2+(z-z_a)^2)/(2*ell^2))`, so that I can model an effective shielding cloud near the apex.
27. As the researcher, I want the Gaussian-shielding case solved via fixed-point iteration between the Poisson solve and the charge update, with under-relaxation (`rho^(k+1) = (1-omega)*rho^k + omega*rho_tilde^(k+1)`), so that the nonlinear coupling converges instead of oscillating.
28. As the researcher, I want convergence tracked via relative change in `rho_e`, `phi`, and peak `E`, plus a max-iteration cap, so that the iteration terminates predictably even if it doesn't converge cleanly.
29. As the researcher, I want a shielding metric `S_E = 1 - Emax_shielded/Emax_laplace`, so that I have one number quantifying how much the space charge reduced the peak field.
30. As the researcher, I want contour/field/interface/convergence plots produced with matplotlib, so that I can visually sanity-check a case without needing the future web app.
31. As the researcher, I want a manufactured-solution test (`phi_exact = r^2 + z^2`, analytic axisymmetric Laplacian as source), so that I have a ground-truth check that the operator, axis stencil, and boundary conditions are jointly correct.
32. As the researcher, I want the manufactured-solution error to shrink under grid refinement, so that I have quantitative evidence of correct convergence order rather than a single pass/fail check.
33. As the researcher, I want a dedicated axis-regularity test confirming `dphi/dr = 0` at `r=0` numerically, so that the axis stencil is verified independently of the manufactured-solution test.
34. As the researcher, I want a dedicated boundary-condition test confirming powered and grounded nodes match their assigned potentials exactly, so that a bug in the interior stencil can never masquerade as a boundary bug.
35. As the researcher, I want a voltage-scaling test confirming `|E|` scales linearly with `V0` and Maxwell pressure scales with `V0^2`, so that the physics of the linear Laplace solve is verified independent of any specific geometry.
36. As the researcher, I want a curvature test against simple known shapes (e.g. a straight line, a circular arc) with a known analytic curvature, so that the curvature formula is verified independent of the electrostatics.
37. As the researcher, I want a shielding sanity test confirming `Emax_shielded < Emax_laplace` for the Gaussian closure with physically sensible parameters, so that a sign error in the Poisson source can't silently produce "anti-shielding."
38. As the researcher, I want a Taylor-angle benchmark example that recovers approximately 49.3° in the ideal (zero space-charge) limit, so that the classical result is reproduced as the project's headline validation.
39. As the researcher, I want a runtime/nonzero-count scaling record across at least two grid resolutions, so that I have evidence the solver stays consumer-hardware-feasible as resolution increases.
40. As the researcher, I want one small runnable example script per completed module (per the outline's "write a tiny runnable example before moving on"), so that each milestone has a demonstrable artifact, not just passing tests.

## Implementation Decisions

- **Scope boundary ("Version 1"):** covers `implementation_outline.md` Milestones 0–6 — package skeleton through Gaussian space-charge shielding, plotting, and verification tests. Threshold-activated space charge, shape optimization, and the app/UI are Version 2+ and out of scope here (see Out of Scope).
- **Modules built in this spec's scope:** `config.py`, `grid.py`, `geometry.py`, `operators.py`, `boundary_conditions.py`, `electrostatics.py`, `fields.py`, `interface.py`, `residual.py`, `space_charge.py` (Gaussian model only), `verification.py`, `plotting.py`.
- **Modules explicitly deferred:** `optimization.py`, `app_backend.py`, `app/streamlit_app.py`, and the threshold-activated branch of `space_charge.py`.
- **Grid indexing:** flatten as `k = i * nz + j` (`i` = radial index, `j` = axial index), fixed project-wide — no module may use the alternate `k = j * nr + i` convention.
- **Parameter representation:** Python `dataclasses` — `PhysicalParams`, `GridParams`, `SolverParams`, `SpaceChargeParams` — as specified in `implementation_outline.md` §4. `SolverParams.linear_solver` stays a string field for future flexibility, but Version 1 code paths only need to support `"spsolve"`.
- **Sparse matrix construction:** assemble via `lil_matrix` or COO triplets, convert to CSR before solving. No dense matrices anywhere, including in tests — a dense-matrix code path is treated as a defect.
- **Linear solve method:** `scipy.sparse.linalg.spsolve` (direct) is the Version 1 default. Iterative solvers (`cg`, `bicgstab`) are out of scope for this spec but the `SolverParams` shape should not preclude adding them later.
- **Axis treatment:** the `r=0` stencil uses the regularized limit `2*phi_rr(0,z) ≈ 4*(phi[1,j]-phi[0,j])/dr^2`, not a direct `1/r` evaluation.
- **Far-boundary condition:** configurable, defaulting to Dirichlet `phi=0` at the outer domain edge. The far-boundary-placement sensitivity check (outline Test 4 / verification §4) is a required verification test, not optional polish.
- **Boundary-condition/operator separation:** `boundary_conditions.py` mutates the assembled `(A, b)` from `operators.py` via row replacement; it does not participate in stencil construction, and `operators.py` does not know about electrode geometry.
- **Field reconstruction:** central differences interior, one-sided at edges; bilinear interpolation to interface points for Version 1 (deferring `RegularGridInterpolator` as a possible later optimization, not a required change).
- **Interface representation:** `GraphInterface` (graph form `R(z)`) only for Version 1 — no parametric/moving-mesh representation.
- **Residual pressure offset:** eliminated via mean-subtraction (`Delta_p = mean(gamma*kappa - p_E)`) rather than a full pressure/volume constraint, consistent with the outline's explicit deferral of that machinery.
- **Space-charge iteration:** fixed-point with under-relaxation; convergence checked on relative change in `rho_e`, `phi`, and peak `E`, plus a hard iteration cap.
- **Numerical-risk-driven conventions to lock down explicitly in code/tests, per outline §8:** sign of `Er`/`Ez`, sign of the Poisson source term, sign of the interface normal, sign of curvature, and half-angle orientation (absolute value of slope). These are the specific places outline calls out as likely-to-cancel-and-hide-a-bug.

## Testing Decisions

- **Seam shape:** per-module unit seams **plus** one end-to-end integration seam — not collapsed to a single seam. This is a deliberate departure from the usual "fewest seams" default: the outline's own numerical-risk table identifies sign/convention bugs (wrong `1/r` term, wrong axis factor, wrong normal sign, wrong Poisson sign) that can cancel pairwise and still pass an end-to-end residual check. A single seam would hide exactly those bugs.
  - Unit seams (one test file per module, mirroring `solver/` layout): `test_grid.py` (indexing round-trip), `test_axis_operator.py` (axis stencil in isolation), `test_boundary_conditions.py` (Dirichlet row enforcement), `test_fields.py` (field derivative signs, voltage scaling), `test_curvature.py` (curvature against known shapes), `test_space_charge.py` (Gaussian closure + fixed-point convergence + shielding sign).
  - Integration seam: `test_manufactured_poisson.py` — exercises grid + operator + boundary conditions + solve together against a known analytic solution, at multiple resolutions, checking convergence order.
- **What makes a good test here:** assert on the *physical/numerical* external behavior (does the field scale with voltage, does curvature match a known shape, does the manufactured error shrink under refinement) rather than internal implementation details (e.g. don't assert on intermediate matrix contents). `verification.py` is explicitly meant to hold "scientific, not just software" tests per the outline.
- **Prior art:** none in-repo yet — this is the first code in the project, so these test files establish the pattern (one test file per `solver/` module, `pytest`, no dense-matrix assertions) that later modules (`optimization.py`, `app_backend.py`) should follow when their specs are written.
- **Grid-refinement test:** run the manufactured-solution case at increasing resolution (e.g. 50×50, 100×100, 200×200) and assert error decreases at roughly the expected finite-difference order — this is the project's primary quantitative correctness evidence, not just a pass/fail check.

## Out of Scope

- Threshold-activated nonlinear space-charge model (`rho_max*(1-exp(-(|E|-E_c)/E_s))`) — Version 2.
- Shape optimization (`optimization.py`, parameterized interface shapes, Nelder-Mead/Powell objective minimization) — Version 2.
- The online app (`app_backend.py`, `app/streamlit_app.py`, Streamlit UI) — Version 2.
- Full transient Navier–Stokes cone-jet dynamics, molecular ion evaporation, droplet breakup distributions, full plasma simulation, full Taylor–Melcher leaky-dielectric dynamics, 3D geometry, arbitrary CAD import, GPU acceleration — never in scope for this project's stated framing (reduced-order axisymmetric electrostatic-capillary solver), per `AI_HANDOVER.md` §2 and outline §11.
- Any physical experiment, high-voltage hardware, or ethanol/electrospray handling procedures — explicitly deferred per `AI_HANDOVER.md` §3 until school-supervised approval.
- Iterative/performance-tuned linear solvers (`cg`, `bicgstab`) — later optimization, not required for Version 1 correctness.

## Further Notes

- This spec's scope (Milestones 0–6) is intentionally larger than a single ticket. `/to-tickets` should split it along the outline's §10 coding order (`grid → operators → boundary_conditions → electrostatics + manufactured Poisson test → fields → interface → residual → space_charge (Gaussian)`), with each ticket blocked on the previous — the ordering is a hard dependency chain, not a suggestion, since e.g. `fields.py` needs a working `electrostatics.py` solve to test against.
- `plotting.py` and `verification.py` aren't a single ticket each — plotting utilities and verification tests should be attached to the ticket for whichever module they demonstrate/verify (e.g. the manufactured-Poisson test ships with the `electrostatics.py` ticket, not standalone).
- Keep the "reduced-order, not full EHD" framing discipline (`AI_HANDOVER.md` §2, §12) in any code comments, docstrings, or example output — avoid language that overclaims (e.g. don't call this a "CFD solver" or claim full leaky-dielectric dynamics).
- No `CONTEXT.md`/ADRs exist yet in this repo. If terms like "shielding metric," "residual," or "half-angle" start drifting across modules/tickets, run `/domain-modeling` to pin them down rather than letting each ticket redefine them ad hoc.
- Dependencies confirmed needed: `numpy`, `scipy`, `matplotlib`, `pytest`. Not yet confirmed installed in the local environment — check before the first implementation ticket runs.
