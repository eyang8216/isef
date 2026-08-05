# Codebase Review and Proposed Next Steps

**Date:** 2026-08-04 (review conducted in session)
**Scope:** `solver/`, `app/`, `tests/`, `theory.tex`, `implementation_outline.md`, `IMPLEMENTATION_STATUS.md`, `paper_submission/`, `docs/`, `notes/`, `.scratch/`

---

## 1. What this project is

A **reduced-order, axisymmetric electrohydrodynamic (EHD) solver** for studying
Taylor-cone onset and space-charge shielding, built for a Hong Kong ISEF physics
project. It is deliberately *not* a full CFD/electrospray simulator — the theory
document (`theory.tex`) and paper (`paper_submission/`) frame it as:

> a reduced-order axisymmetric electrostatic-capillary onset model with effective space-charge closures

### The physics chain (all in `theory.tex`, mirrored by the code)

1. **Classical Taylor cone** — exterior Laplace solution `φ = A ρ^ν P_ν(cos θ)`;
   stress balance forces `ν = 1/2`; the equipotential cone angle comes from the
   Legendre root `P_{1/2}(cos θ₀) = 0` → **49.3°** half-angle, with the apex
   singularity `E ~ ρ^(−1/2)` [Taylor1964].
2. **Axisymmetric electrostatics** — finite-volume Laplacian
   `φ_rr + (1/r)φ_r + φ_zz` with a regularized `r = 0` stencil
   (`solver/operators.py`).
3. **Young–Laplace–Maxwell balance** — residual `R = γκ − Δp − ½ε₀Eₙ²` on a graph
   interface `r = R(z)` (`solver/residual.py`).
4. **Space-charge closures** — Gaussian prescribed cloud and threshold-activated
   `ρ_e` (Poisson), solved by under-relaxed fixed-point iteration; shielding
   metric `S_E = 1 − E_max^shielded / E_max^ref` (`solver/space_charge.py`).
5. **Shape optimization** — Powell over an analytic cone family (half-angle,
   apex radius) (`solver/optimization.py`).

### Code structure and status

- `solver/` — grid, operators, boundary conditions, electrostatics, fields,
  interface, residual, space charge, optimization, verification, app backend.
- `app/streamlit_app.py` — interactive UI over `solver/app_backend.py`.
- `tests/` — **34 tests, all passing** (verified in-session: `34 passed in 41.06s`).
- `paper_submission/` — 22-page LaTeX manuscript for HK ISEF selection.
- Status: V1 + V2 complete; V3 Track A item 1 (threshold–optimizer coupling) done.
  Remaining Track A: sharp-cone BC, leaky dielectric, current-constrained closure.
  Track B (experiments) gated on school approval.

### What is good

- **Disciplined verification**: manufactured-solution convergence (L2 error
  halves per 2× refinement — second order confirmed in
  `results/v1_numerical_report.md`), voltage scaling, residual null test, and
  the Legendre-root Taylor-angle benchmark (49.2901°).
- **Honest documentation**: limitations stated explicitly; no overclaiming.
- **Clean engineering**: frozen dataclasses, documented flattening convention,
  shared fixed-point loop, no `st.*` in the backend, ADR trail.

---

## 2. Concrete weaknesses found

### W1. The optimizer's interface never affects the field (highest-impact issue)

`solver/optimization.py` (docstring at `optimize_cone_shape`) admits the liquid
interface is *"a diagnostic surface only — it does not alter the electrode BCs…
the threshold field varies with sc_params, not with the candidate shape."* The
optimized cone is a diagnostic curve inside a **fixed** field, not the
equipotential surface that Taylor's analysis assumes.

Consequences:

- "Coupled mode" re-runs `solve_threshold_shielding` on every Powell evaluation,
  but the result is identical every time (shape-independent) — wasted CPU, and
  the shape↔field coupling the V3 feature implies is not real.
- The **43.5° vs 49.3° gap** is attributed to the staircase grid-mask, but part
  of it is this formulation: you cannot recover Taylor's angle by minimizing
  residual against a field that never sees the cone. The two explanations are
  entangled and the docs do not distinguish them.

### W2. Optimizer hit its constraint

Example 05 reports `Apex radius: 1.00e-01 m` — exactly the `apex_radius_max`
bound in `ConeShapeBounds`. The optimum sits at the box edge, so the objective
is not well-posed in that direction; the 43.5° result is partly an artifact of
the bounds.

### W3. The Gaussian "shielding" case slightly anti-shields

`results/v1_numerical_report.md` §5 shows `S_E ≈ −0.7%` (global and apex-ROI).
The docs say negative `S_E` "indicates a sign/model problem." A positive charge
cloud placed mid-domain can locally *raise* |E| depending on placement — this
needs a physical explanation or a corrected parameter regime before the paper
claims space-charge shielding.

### W4. Minor hygiene

- `SolverParams` is an empty dataclass threaded everywhere (`config.py`) — dead
  abstraction.
- `np.gradient(..., edge_order=1)` gives first-order fields at boundaries; no
  grid-convergence study exists for *interface* quantities (`E_n`, residual) —
  only interior φ.
- The threshold closure `ρ_e = ρ_max(1 − e^(−(|E|−E_c)/E_s))` is purely
  phenomenological: no connection to ion mobility or emission current, so `S_E`
  is not yet a *predictive* quantity.
- No prose ties the residual sign convention `R = γκ − Δp − ½ε₀Eₙ²` to the
  gas-side-normal choice in `solver/interface.py`.

---

## 3. Proposed next steps (with literature support)

Ranked by value-to-effort for the project's stated goals (ISEF defense + honest
physics). Every reference is either already in the repo's bibliography/research
notes or was verified against Crossref during this review (see §5 for status).

### A. Fix the free-boundary formulation (highest scientific value)

**A1. Implement the sharp immersed/ghost-cell Dirichlet BC** for the conical
conductor, replacing the staircase mask.

- Grounding: [Gibou2002] — second-order-accurate symmetric discretization of
  Poisson on irregular domains (locate the true boundary crossing, use a
  one-sided weighted stencil); [ShortleyWeller1938] — the original
  irregular-boundary truncation-error analysis; [Fedkiw1999] — ghost-fluid
  method. The repo's own `.scratch/taylor-cone-fd-bcs/research.md` already
  worked out the stencil math (including `φ_b` at the exact `P_{1/2}` root
  position).
- Payoff: turns the known O(h) staircase error into O(h²), quantifiable with a
  refinement study — directly the "close the 6° gap" Track A item.

**A2. Make the interface an actual equipotential boundary** so the field
responds to shape — the genuine free-boundary loop (iterate shape → field →
residual until both converge).

- Grounding: [Taylor1964] — the cone *is* the equipotential surface of the
  exterior problem, the premise the 49.3° benchmark rests on; [BasaranScriven1990]
  — axisymmetric EHD drop shapes with the interface as a boundary; [Higuera2004]
  — a reduced electrospray meniscus model where meniscus shape and field are
  solved self-consistently.
- This makes the 43.5° discrepancy scientifically meaningful instead of a
  bookkeeping artifact, and is the natural candidate for a *novel* claim.

### B. Make space charge physical

**B1. Replace the phenomenological closure with a drift-dominated ion model**
(the "current-constrained closure" Track A item 4): steady-state charge
transport `∇·(μρ_e E) = 0` (or a 1D/axisymmetric reduction) coupled to Poisson,
with total current tied to the emitter.

- Grounding: [FdeMLoscertales1994] — the current scaling
  `I ≈ f(ε)(γKQ/ε)^½` for highly conducting cones; [Higuera2004] — reduced
  meniscus + transport model; [GameroCastano2008] — "The structure of
  electrospray beams in vacuum," the space-charge-dominated plume regime your
  shielding narrative ultimately describes.
- Payoff: turns `S_E` from a fitting parameter into a quantity with an
  *independent* physical explanation (space-charge-limited flow between emitter
  and extractor) — exactly what an ISEF judge will probe.

**B2. Resolve the negative Gaussian `S_E`** (report §5) with a physical sign
argument or a corrected case in the cone geometry, before the paper asserts
"shielding." If a positive ion cloud between cone and extractor is what reduces
the emitter field, demonstrate that geometry; a cloud elsewhere legitimately can
increase the local field.

### C. Validation without hardware (high ISEF value, low risk)

**C1. Benchmark against Taylor's own drop experiment**: the critical field for a
conducting drop in a uniform field, `E_c ≈ 1.625 (γ/ε₀R)^½`, from [Taylor1964] —
a clean analytical target independent of the free-boundary machinery. Simulate a
spherical-cap meniscus in a uniform field and compare the onset field. *(Verify
the constant against the paper's tables/equations when implementing — not
re-derived here.)*

**C2. Compare onset-voltage trends against published cone-jet onset data**:
[CloupeauPrunetFoch1989] and [CloupeauPrunetFoch1990] give measured onset
voltages and stable-mode maps; [Hartman1999] model the cone-jet with
onset-voltage comparisons. This directly exercises the
`BoE = ε₀V₀²/γL` scaling in `theory.tex` §10.

**C3. Systematic V&V**: compute observed order of convergence with Richardson
extrapolation, and grid-converge the *interface* quantities (`E_n`, residual) —
not just interior φ.

- Grounding: [LeVeque2007]; [Roache1998]. Cheap, strengthens every numerical
  claim in the paper, and is the standard a reviewer/judge expects.

### D. Leaky-dielectric extension (Track A item 3)

Two-phase Laplace + surface-charge conservation, per the Taylor–Melcher model.

- Grounding: [Saville1997] and [MelcherTaylor1969]; [FengScott1996] — the
  standard numerical reference for exactly this model; [BasaranScriven1990] for
  axisymmetric implementation.
- Well-scoped, directly tests the "perfect conductor is a good approximation"
  assumption, and is a natural V4 claim.

### E. Code hygiene (quick wins)

1. Cache or remove the shape-independent threshold re-solve in coupled optimizer
   mode (or restructure after A2).
2. Assert the optimizer optimum is *interior* (add a test or widen the
   apex-radius bound) — the bound-active `1.00e-01 m` result undercuts the 43.5°
   claim.
3. Delete or implement `SolverParams`.
4. Add a short doc on the residual/normal sign convention tying
   `R = γκ − Δp − ½ε₀Eₙ²` to the gas-side-normal choice in `interface.py`.

---

## 4. Suggested order

1. **A1 + A2** (sharp BC + true free-boundary coupling) — fixes the central
   scientific gap and the 43.5° issue.
2. **B2 + B1** (sign fix, then drift-dominated closure) — makes the shielding
   claim defensible and predictive.
3. **C1–C3** (experiment-free validation) — best ROI for the ISEF paper before
   hardware is allowed.
4. **D** (leaky dielectric) — the natural next model level.
5. **E** hygiene items whenever convenient.

---

## 5. References

### Already in the repo's bibliography (`paper_submission/references.bib`)

- **[Taylor1964]** G. I. Taylor, "Disintegration of Water Drops in an Electric Field," *Proc. R. Soc. Lond. A* 280(1382):383–397, 1964. DOI: [10.1098/rspa.1964.0151](https://doi.org/10.1098/rspa.1964.0151)
- **[Saville1997]** D. A. Saville, "Electrohydrodynamics: The Taylor–Melcher Leaky Dielectric Model," *Annu. Rev. Fluid Mech.* 29:27–64, 1997. DOI: [10.1146/annurev.fluid.29.1.27](https://doi.org/10.1146/annurev.fluid.29.1.27)
- **[MelcherTaylor1969]** J. R. Melcher and G. I. Taylor, "Electrohydrodynamics: A Review of the Role of Interfacial Shear Stresses," *Annu. Rev. Fluid Mech.* 1:111–146, 1969. DOI: [10.1146/annurev.fl.01.010169.000551](https://doi.org/10.1146/annurev.fl.01.010169.000551)
- **[FdeMLoscertales1994]** J. Fernández de la Mora and I. G. Loscertales, "The Current Emitted by Highly Conducting Taylor Cones," *J. Fluid Mech.* 260:155–184, 1994. DOI: [10.1017/S0022112094003472](https://doi.org/10.1017/S0022112094003472)
- **[Hartman1999]** R. P. A. Hartman et al., "Electrohydrodynamic Atomization in the Cone-Jet Mode: Physical Modeling of the Liquid Cone and Jet," *J. Aerosol Sci.* 30(7):823–849, 1999. DOI: [10.1016/S0021-8502(99)00033-6](https://doi.org/10.1016/S0021-8502(99)00033-6)

### In the repo's research notes (`.scratch/taylor-cone-fd-bcs/research.md`) with DOIs

- **[Gibou2002]** F. Gibou, R. P. Fedkiw, L.-T. Cheng, M. Kang, "A Second-Order-Accurate Symmetric Discretization of the Poisson Equation on Irregular Domains," *J. Comput. Phys.* 176(1):205–227, 2002. DOI: [10.1006/jcph.2001.6977](https://doi.org/10.1006/jcph.2001.6977)
- **[ShortleyWeller1938]** G. H. Shortley and R. Weller, "The Numerical Solution of Laplace's Equation," *J. Appl. Phys.* 9(5):334–348, 1938. DOI: [10.1063/1.1710426](https://doi.org/10.1063/1.1710426)
- **[Fedkiw1999]** R. P. Fedkiw, T. Aslam, B. Merriman, S. Osher, "A Non-Oscillatory Eulerian Approach to Interfaces in Multimaterial Flows (the Ghost Fluid Method)," *J. Comput. Phys.* 152(2):457–492, 1999. DOI: [10.1006/jcph.1999.6236](https://doi.org/10.1006/jcph.1999.6236)
- **[BasaranScriven1990]** O. A. Basaran and L. E. Scriven, "Axisymmetric Shapes and Stability of Charged Drops in an External Electric Field," *J. Colloid Interface Sci.* 140(1):10–30, 1990. DOI: [10.1016/0021-9797(90)90316-G](https://doi.org/10.1016/0021-9797(90)90316-G)
- **[LeVeque2007]** R. J. LeVeque, *Finite Difference Methods for Ordinary and Partial Differential Equations*, SIAM, 2007.

### Verified against Crossref during this review (2026-08-04)

- **[Higuera2004]** F. J. Higuera, "Current/flow-rate characteristic of an electrospray with a small meniscus," *J. Fluid Mech.*, 2004. DOI: [10.1017/S0022112004000308](https://doi.org/10.1017/S0022112004000308)
- **[FengScott1996]** J. Q. Feng and T. C. Scott, "A Computational Analysis of Electrohydrodynamics of a Leaky Dielectric Drop in an Electric Field," *J. Fluid Mech.* 311, 1996. DOI: [10.1017/S0022112096002601](https://doi.org/10.1017/S0022112096002601)
- **[CloupeauPrunetFoch1989]** M. Cloupeau and B. Prunet-Foch, "Electrostatic Spraying of Liquids in Cone-Jet Mode," *J. Electrostatics* 22, 1989. DOI: [10.1016/0304-3886(89)90081-8](https://doi.org/10.1016/0304-3886(89)90081-8)
- **[CloupeauPrunetFoch1990]** M. Cloupeau and B. Prunet-Foch, "Electrostatic Spraying of Liquids: Main Functioning Modes," *J. Electrostatics* 25, 1990. DOI: [10.1016/0304-3886(90)90025-Q](https://doi.org/10.1016/0304-3886(90)90025-Q)
- **[GameroCastano2008]** M. Gamero-Castaño, "The Structure of Electrospray Beams in Vacuum," *J. Fluid Mech.* 604:339–368, 2008. DOI: [10.1017/S0022112008001316](https://doi.org/10.1017/S0022112008001316)

### Books (standard references, not DOI-verified)

- **[Roache1998]** P. J. Roache, *Verification and Validation in Computational Science and Engineering*, Hermosa Publishers, 1998.

> **Note on source status:** no reference above was invented. Papers in the first
> two groups come from this repo's own `references.bib` / research notes; papers
> in the third group were confirmed to exist with the given DOI via the Crossref
> REST API during the review session. Before relying on any specific constant or
> formula from a cited paper in code or the manuscript (e.g. the `1.625`
> critical-field constant in C1), check it against the primary source.
