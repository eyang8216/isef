# Spec: Sharp-Cone Immersed Boundary + Merged Free-Boundary Formulation (A1+A2)

Status: partially implemented — verification and conditioning work remain

Implementation note (2026-08-06): the shared rounded geometry, immersed
fractional-distance operator, one-sided normal field, and candidate-dependent
Laplace optimizer now exist. The original hard acceptance targets below are
retained as historical design context but are superseded where they mix a
rounded cap with the singular Taylor solution. Use a separate smooth
irregular-boundary manufactured test for formal order, and treat 49.29° as an
ideal-limit reference requiring grid/domain/cap-radius extrapolation rather
than an immediate ±0.5° pass condition.

**Source docs:** `docs/codebase_review_and_next_steps.md` (steps A1+A2),
`docs/adr/0003-merged-free-boundary-immersed-cone.md`,
`.scratch/taylor-cone-fd-bcs/research.md`, `theory.tex` §5 (Taylor cone) and
§12 (free-boundary formulation), `implementation_outline.md` §5.2/5.3,
`IMPLEMENTATION_STATUS.md` (V3 Track A item 2).

## Problem Statement

The shape optimizer recovers ~43.5° instead of the theoretical 49.29°. Two
entangled causes:

1. **Staircase electrode error.** `solver/geometry.py::conical_conductor` marks
   whole grid nodes as the powered conductor; the enforced boundary is a
   staircase displaced O(h) from the true cone, giving a first-order consistency
   error on the boundary (Shortley & Weller 1938; Gibou et al. 2002).
2. **The interface never affects the field.** `solver/optimization.py` evaluates
   the residual of a diagnostic `GraphInterface` against a *fixed* field; the
   candidate shape does not back-react on the electrostatics. Taylor's 49.29°
   equilibrium is the equipotential *cone of the exterior Laplace problem* — a
   diagnostic curve in a fixed field cannot recover it.

Additionally, once the apex is rounded (needed to regularize the
`E ~ ρ^(−1/2)` tip), the current half-angle extraction (`GraphInterface.
half_angle_deg`, which fits over the smallest-`R` samples) would fit **on the
cap**, whose slope is not the flank slope.

## Solution

Merge the interface and the conductor: the candidate liquid surface is the
Dirichlet (`V0`) boundary of the axisymmetric Laplace solve, enforced by a
Gibou-style ghost-cell / immersed Dirichlet stencil driven by an implicit cone
function with a smooth rounded cap. The Powell optimizer (half-angle, apex
radius) rebuilds the immersed operator per evaluation, so the field responds to
each candidate shape. Residual and half-angle extraction operate on the flank
only (cap excluded). Verification: manufactured Taylor-potential convergence
(order ≥ 1.8) and optimizer angle within ±0.5° of 49.29° at the finest testable
grid, with a documented refinement trend.

## User Stories

1. As the researcher, I want the cone represented as an implicit function
   (`ImplicitCone`) derived from the same cone-family parameters
   (`half_angle_deg`, `apex_radius`, `apex_z`) that build the `GraphInterface`,
   so that the operator's boundary and the residual's surface are guaranteed
   consistent (one source of truth).
2. As the researcher, I want the cone surface with a smooth rounded cap
   (tangent cap joining the flanks), so that the ghost-cell stencils see no
   geometric corner and the apex field stays finite.
3. As the researcher, I want a Gibou-style immersed Dirichlet operator
   (`solver/immersed.py`) that modifies near-boundary stencils with the
   fractional-distance weights and keeps interior conductor nodes as Dirichlet
   rows, so that the enforced boundary is second-order accurate.
4. As the researcher, I want boundary-aware electric-field reconstruction near
   the cone (one-sided stencils to the boundary crossing), so that `E_n` on the
   interface — and therefore the Maxwell pressure and YLM residual — is not
   corrupted by a plain `np.gradient` stencil crossing the surface.
5. As the researcher, I want `solve_electrostatics` to accept the immersed
   geometry as an option and to keep the `rho_e` RHS path working, so that
   `solve_poisson` and the space-charge modules are not broken by the new
   boundary treatment.
6. As the researcher, I want the Powell optimizer to solve the coupled problem
   per evaluation (candidate shape → immersed operator → solve → residual), so
   that the field genuinely responds to the interface.
7. As the researcher, I want the residual and the half-angle extraction to use
   flank-only samples (cap excluded), so that the cap's systematic YLM imbalance
   and non-flank slope do not bias the recovered angle.
8. As the researcher, I want Δp to stay analytically eliminated by
   mean-subtraction (never a free variable), preserving the V2 rule.
9. As the researcher, I want a manufactured-solution test using the exact
   Taylor potential `φ = A·ρ^½·P_{1/2}(cosθ)` as the outer Dirichlet condition
   with the sharp cone as the equipotential, asserting observed convergence
   order ≥ 1.8 under refinement, so that the ghost-cell boundary is verified
   independently of the optimizer.
10. As the researcher, I want the optimizer demo to recover a half-angle within
    ±0.5° of 49.29° at the finest testable grid with a documented refinement
    trend, so that "closing the 43.5° gap" is demonstrated quantitatively.
11. As the researcher, I want a consistency test that `GraphInterface` samples
    lie on the `ImplicitCone` zero contour, so that the one-source-of-truth
    invariant is enforced in CI.
12. As the researcher, I want all 34 existing tests to stay green and the
    legacy `conical_conductor` geometry to remain available, so that this
    milestone is a strict extension, not a breaking rewrite.

## Implementation Decisions

- **New module `solver/immersed.py`:** owns (a) near-boundary stencil
  modification with Gibou fractional-distance weights referencing the boundary
  value `V0`, (b) interior-conductor Dirichlet rows, (c) boundary-aware field
  reconstruction for `E` at interface points. Assembles into the same sparse
  `A φ = b` structure consumed by `spsolve`.
- **`ImplicitCone` in `solver/geometry.py`:** exposes a signed
  `phi(r, z)`-style implicit function (zero contour = surface), a `normal()`,
  and a `boundary_value` (`V0`). Built from the cone-family parameters shared
  with `GraphInterface`; rounded-cap construction (cone flanks + tangent
  spherical cap). Gas-side sign convention documented and tested.
- **Operator integration:** the standard axisymmetric Laplacian (including the
  `r = 0` regularity stencil) is assembled as today; `immersed.py` post-processes
  the near-boundary rows. `poisson_rhs` is unchanged — the RHS path keeps
  working (Poisson source over the gas nodes).
- **`solve_electrostatics`:** gains an optional immersed-geometry argument
  (e.g. `immersed: ImplicitCone | None = None`). When supplied, the cone nodes
  are Dirichlet at `V0` via the immersed stencils; flat/outer electrode masks
  (`GeometryMasks`) still apply as today.
- **Residual path:** `compute_residual` gains cap exclusion (flank-only sample
  window). The interface passed to the residual is the same shape used to build
  the `ImplicitCone`.
- **Half-angle extraction:** flank-window fit on `R(z)` away from the cap
  (replaces the smallest-`R`-samples fit of the current
  `GraphInterface.half_angle_deg` for capped shapes).
- **Optimizer:** keep `scipy.optimize.minimize(method="Powell")` over
  `(half_angle_deg, apex_radius)` with box bounds, Δp mean-subtracted, 1e10
  penalty for degenerate shapes. The objective performs the per-evaluation
  immersed solve. `ConeShapeBounds` unchanged except that `apex_radius` is now a
  physically meaningful regularization (recommend testing optima that are
  interior, not at the bound — see review weakness W2).
- **Benchmark path:** the Taylor-angle demo (example) uses the immersed geometry;
  the legacy `conical_conductor` remains for existing examples/tests.

## Testing Decisions

- **`tests/test_immersed.py` (new):**
  - Manufactured Taylor potential: outer boundary Dirichlet
    `φ = A·ρ^½·P_{1/2}(cosθ)`, cone equipotential at `V0`; assert L2
    convergence order ≥ 1.8 under refinement (halving error ratio
    ≤ ~0.57 per doubling).
  - Boundary-aware field: `E_n` at the cone surface matches the analytic Taylor
    field to the expected order on a manufactured case.
  - `r = 0` axis + immersed interaction: no crash, symmetric result on an
    axisymmetric cone.
  - RHS path: `solve_poisson` with an immersed geometry and a known `rho_e`
    returns a finite result and matches the manufactured source.
  - Consistency: samples of the `GraphInterface` built from the same parameters
    lie on the `ImplicitCone` zero contour within tolerance.
  - Cap exclusion: flank-only residual/angle extraction returns the flank slope
    on a synthetic capped cone.
- **`tests/test_optimization.py` (extend):** recovered angle within ±0.5° of
  49.29° at the finest testable grid; angle moves toward 49.29° as the grid
  refines (monotone trend asserted or reported); optimum is interior w.r.t.
  `apex_radius` (not at the bound).
- **Regression:** all 34 existing tests remain green.
- **Example:** `examples/07_immersed_taylor_benchmark.py` — runs the immersed
  optimizer, prints recovered angle, deviation from 49.29°, and a small
  refinement table (angle vs. grid size).

## Out of Scope

- Threshold/Gaussian space-charge coupling inside the optimizer (ADR-0002
  remains in force; only the RHS wiring is included here).
- Leaky-dielectric liquid potential, surface charge conservation,
  current-constrained closure.
- Deprecating or removing the legacy `conical_conductor` geometry.
- Spline control-point parameterization (ADR-0001).
- Asymptotic resolution of the `E ~ ρ^(−1/2)` tip singularity.

## Further Notes

- Benchmark constant: `verification.taylor_cone_half_angle_deg()` = 49.2900892921°.
- Current baseline to beat: example 05 recovers 43.5312° on a 31×51 grid with
  `apex_radius` pinned at the 0.1 m bound (review weakness W2) — the new
  benchmark must both move the angle to within ±0.5° of 49.29° and keep the
  optimum interior.
- Acceptance band rationale: the rounded cap cannot balance YLM exactly with the
  analytic family; the band absorbs that systematic offset. The refinement trend
  is the primary evidence.
- Suggested `/to-tickets` dependency chain:
  `ImplicitCone + immersed operator + tests` → `manufactured Taylor test` →
  `boundary-aware fields + cap-excluded residual/angle` → `optimizer rewiring +
  test` → `example + refinement report`.
