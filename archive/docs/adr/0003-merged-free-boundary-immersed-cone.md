# Merged free-boundary formulation with an immersed-boundary cone (A1+A2)

**Implementation status (2026-08-06): partially implemented and under verification.**
`ImplicitCone`, immersed fractional-distance stencils, one-sided normal fields,
and candidate-dependent Laplace optimization now exist. Smooth irregular-domain
convergence, small-cut conditioning, ideal-limit extrapolation, and physical
free-boundary constraints remain open. The implementation does not claim SPD or
49.29° recovery solely from this milestone.

## Decision

Replace the current split — a fixed staircase `conical_conductor` electrode plus a
diagnostic interface that never affects the field — with a **merged free-boundary
formulation**: the candidate liquid interface *is* the equipotential conductor
(Dirichlet at `V0`) of the axisymmetric Laplace solve.

- The cone is represented **implicitly** (`ImplicitCone` in `solver/geometry.py`),
  built from the same cone-family parameters (`half_angle_deg`, `apex_radius`,
  `apex_z`) that define the `GraphInterface` used for residual evaluation — one
  source of truth.
- The boundary is enforced with a **fractional-distance immersed Dirichlet
  stencil** on the existing structured grid (`solver/immersed.py`). The current
  matrix is not claimed to be symmetric positive definite: the axisymmetric
  operator is weighted-self-adjoint and legacy row-only Dirichlet insertion is
  not symmetric elimination. Accuracy and conditioning must be established by
  refinement tests.
- The cone tip is **rounded with a smooth cap** whose radius is a free shape
  parameter; the cap region is excluded from the residual and the half-angle fit.
- The Powell optimizer rebuilds the immersed operator for every candidate shape,
  so the field genuinely responds to the interface (per-evaluation coupled solve).

This supersedes the V2/V3 optimizer behavior documented in `solver/optimization.py`,
where the interface was a diagnostic surface only and the field "varies with
sc_params, not with the candidate shape".

## Rationale

1. **Taylor's equilibrium is the equipotential cone.** In Taylor (1964), the
   conducting liquid surface is the equipotential boundary of the exterior
   Laplace problem; the 49.3° half-angle follows from the stress balance on that
   boundary. A diagnostic curve floating in a *fixed* field cannot recover this —
   the current ~43.5° result is partly an artifact of that split, not purely of
   the staircase mask.
2. **The staircase mask is first-order.** Flagging grid nodes along a curved
   boundary displaces the enforced boundary by O(h) (Shortley & Weller 1938),
   degrading the global solution to first order. The ghost-cell / immersed
   Dirichlet approach locates the true boundary crossing and restores second
   order (Gibou, Fedkiw, Cheng & Kang 2002).
3. **The volume grid must survive.** The space-charge (Poisson) work depends on
   the structured volume grid; a boundary-element formulation would discard it.
4. **The singularity is regularized physically.** The ideal tip has
   `E ~ ρ^(−1/2)`; a rounded apex of finite radius makes the field finite and
   keeps the apex radius as an interpretable shape parameter.

## Why ghost-cell rather than alternatives

- **Boundary element method:** elegant for exterior Laplace, but abandons the
  volume grid the Poisson space-charge extension needs — largest rewrite.
- **Analytic per-row cut stencil (straight cone only):** least code, but a dead
  end once the apex is rounded or a nozzle is added.
- **Conforming mesh / FEM library:** heavy dependency change, out of proportion.

## Trade-offs

- Each optimizer evaluation now rebuilds the operator and re-solves; grids are
  small (≈10³–10⁴ unknowns) so this remains cheap with `spsolve`.
- The rounded cap cannot satisfy the Young–Laplace–Maxwell balance exactly with
  the analytic cone family, so the family optimum carries a small systematic
  offset from 49.3°. The acceptance band (±0.5°) accounts for this; the
  refinement trend, not a single-point value, is the primary evidence.
- Space-charge coupling inside the optimizer is deferred (ADR-0002 stays in
  force): the immersed operator is wired with an RHS path so `solve_poisson`
  keeps working, but threshold-optimizer coupling is out of scope for this
  milestone.

## References

- G. I. Taylor, "Disintegration of water drops in an electric field," *Proc. R.
  Soc. Lond. A* 280(1382):383–397, 1964. DOI: 10.1098/rspa.1964.0151
- G. H. Shortley and R. Weller, "The numerical solution of Laplace's equation,"
  *J. Appl. Phys.* 9(5):334–348, 1938. DOI: 10.1063/1.1710426
- F. Gibou, R. P. Fedkiw, L.-T. Cheng, M. Kang, "A second-order-accurate
  symmetric discretization of the Poisson equation on irregular domains,"
  *J. Comput. Phys.* 176(1):205–227, 2002. DOI: 10.1006/jcph.2001.6977
- See also: `.scratch/taylor-cone-fd-bcs/research.md` (staircase-error and
  ghost-cell derivation specific to the Taylor cone).
