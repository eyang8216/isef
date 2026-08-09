# Next Steps — Post-Merge V3 (2026-08-09)

**Status tracker for what remains after the `feat/immersed-free-boundary` merge.**
Sources: `docs/codebase_review_and_next_steps.md` (2026-08-04), the V3 spec
`.scratch/taylor-cone-fd-bcs/spec.md` (incl. its 2026-08-06 superseding note),
`docs/plans/2026-08-06-immersed-free-boundary.md`, the merged branch
(eyang8216, tip `1ac7059`), and measurements taken 2026-08-09.

---

## 1. Current verified state

| Fact | Evidence |
|---|---|
| V3 immersed free-boundary core merged on `main` | merge `3bf4d1f` (2026-08-09) |
| W1 fixed: candidate cone is the Dirichlet boundary of its own solve in `immersed_mode` | `solver/optimization.py:197-217`; test asserts `field_variation > 0`; example 07 prints `field_variation = 1.000e+03 V` |
| Immersed operator is second-order on a smooth curved boundary | `test_smooth_immersed_manufactured_solution_second_order_convergence` (`ebea0b8`), measured order ≈ 2.0 |
| Tiny-cut conditioning fixed; example 07 runs with 0 candidate failures | `8e2a2c8`; wrapped run: 0 failures / 343 evals |
| Full test suite green | 51 passed (2026-08-09, 41s) |
| Legacy staircase path intact | example 05 reproduces exactly 43.5312°, apex_radius = 1.00e-01 m (bound-active, W2) |
| Optimizer result is start/option-dependent | example 07: fresh run 22.9° (rms 0.0586 Pa); friend's run ≈ 47.5° |

## 2. New findings (2026-08-09) — read before planning work

1. **The immersed YLM objective is not well-posed in `apex_radius` and nearly
   flat in `half_angle`.** A full sweep of the feasible box plus an extended
   scan shows the residual *decreases monotonically with `apex_radius` at every
   angle* (e.g. 10°, r = 0.10 → 0.40 m: 0.0345 → 0.0040 Pa) with no interior
   minimum, and the angle direction is flat/noisy (all angles within ~2× RMS at
   fixed radius). This is W2 elevated from "hit the bound" to a modeling
   degeneracy: the YLM residual over the analytic cone family has no preferred
   apex radius without a volume / contact-line constraint (spec's "not yet
   proven" list item).
2. **The 22.9° vs 47.5° spread is a flat-landscape artifact, not
   multi-modality.** A fine scan (19–28°, r = 0.055–0.095) shows a smooth,
   monotone landscape; Powell stops anywhere in a shallow basin depending on
   start/options. **No angle-vs-grid refinement trend can be extracted from
   this objective as-is** — the honest outcome the spec permits ("document why
   the finite rounded case differs").
3. **Potential in the gas converges ~2nd order (immersed) while the legacy
   staircase path does not converge cleanly** (inter-level L2 differences
   non-monotone; orders 2.31/1.66 vs 3.36/−1.49 on a 31×45→87×129 series) —
   the A1 payoff, measured directly (details in `examples/08_immersed_refinement_study.py`).
4. **E_n at fixed interface points does not converge cleanly** with the current
   one-sided quadratic reconstruction: the O(h²) potential error enters the
   derivative as O(h), with oscillating interpolation sign. Interface-field
   convergence needs Richardson-extrapolated potentials (item S3 below).

## 3. Review-doc items → status

| Review item | Status | Where |
|---|---|---|
| A1 sharp immersed/ghost-cell BC | ✅ Done | `solver/immersed.py`, `solver/geometry.py::ImplicitCone` (eyang `1ac7059`); order proven (`ebea0b8`) |
| A2 interface as equipotential (field↔shape) | ✅ Done | `solver/optimization.py` immersed mode |
| B1 drift-dominated ion closure | ⬜ Not started | Track A item 4 |
| B2 negative Gaussian `S_E ≈ −0.7%` | ⬜ Open | `results/v1_numerical_report.md` §5 |
| C1 Taylor drop critical field `E_c ≈ 1.625(γ/ε₀R)^½` | ⬜ Not started | verify constant against Taylor (1964) first |
| C2 onset-voltage vs published data | ⬜ Not started | Cloupeau–Prunet-Foch / Hartman |
| C3 systematic V&V (Richardson + interface quantities) | ◐ Partial | potential order done; interface E_n open (S3) |
| D leaky dielectric | ⬜ Not started | V4 scope |
| E1 cache/remove shape-independent threshold re-solve | ⬜ Open | legacy coupled mode unchanged |
| E2 assert interior optimum / W2 | ⬜ Open — now characterized | monotone-in-radius degeneracy (finding 1) |
| E3 delete/implement `SolverParams` | ⬜ Open | `solver/config.py:41` |
| E4 residual/normal sign-convention note | ⬜ Open | tie `R = γκ − Δp − ½ε₀Eₙ²` to gas-side normal |

Also stale: `IMPLEMENTATION_SUMMARY.md` and `COMPLETE_STATUS_REPORT.md`
(friend's docs) still claim 50 tests, a weak convergence test
(`errors[1] < 0.7·errors[0]`), and a "no gas-side third point" failure mode
that the 2026-08-09 conditioning fix removed.

## 4. Next steps (priority order)

### S1 — Regularize the `apex_radius` direction (gating, ~1–2 days)
The optimizer cannot produce a meaningful angle until the residual is well-posed
in `apex_radius`. Options, in order of preference:
1. Add a volume / contact-line constraint (spec lists "unique physical
   free-boundary solution with volume/contact-line constraints" as not yet
   proven — this is the honest fix).
2. Freeze `apex_radius` at a physically justified value (e.g. from a capillary
   length or nozzle geometry) and optimize angle only — the flat-in-angle
   landscape must then be reported as weak identifiability, with the residual
   floor rather than a claim of angle recovery.
3. Widen/remove the bound and document the monotone degeneracy as the study
   result (cheapest; acceptable only if the paper does not claim an angle).

**Acceptance:** either an interior optimum with documented 49.29° trend, or a
documented, data-backed statement of why the finite rounded truncated-domain
model cannot recover 49.29° (spec's accepted alternative).

### S2 — Refinement study example (this turn) — `examples/08_immersed_refinement_study.py`
- Part A: potential self-convergence, immersed vs legacy staircase, fixed gas
  sub-region, 4 grid levels → observed orders (immersed ≈ 2, staircase
  non-convergent).
- Part B: optimizer landscape sweep at 2 grid levels → shows flat-in-angle /
  monotone-in-radius persists under refinement (model issue, not discretization).
- **Acceptance:** runs in < 2 min, prints both tables + honest interpretation.

### S3 — Interface-quantity convergence in CI (~2–3 h)
Extend `tests/test_immersed.py`: Richardson-extrapolate the potential from
successive levels, then evaluate `E_n` on the extrapolated field; assert
observed E_n order (target ≥ 1.5, decide from measurement). Closes W4/C3.

### S4 — B2: resolve the negative Gaussian `S_E` (~half day)
Physical sign argument (charge-cloud placement) or corrected case, then update
`results/v1_numerical_report.md` §5 and the paper claim.

### S5 — C1: Taylor drop critical-field benchmark (~half day)
`E_c ≈ 1.625(γ/ε₀R)^½` — **verify the constant against Taylor (1964) before
coding** (review doc warning). Spherical-cap meniscus in a uniform field.

### S6 — C2: onset-voltage trend vs published data (~1 day)
Cloupeau–Prunet-Foch (1989, 1990); Hartman (1999). Exercises the
`BoE = ε₀V₀²/γL` scaling (theory.tex §10).

### S7 — Hygiene (~1 h)
E3 delete `SolverParams`; E4 sign-convention note; refresh
`IMPLEMENTATION_SUMMARY.md` / `COMPLETE_STATUS_REPORT.md`; delete merged branch
`git push origin --delete feat/immersed-free-boundary`.

### Deferred
B1 drift-dominated ion transport, D leaky dielectric (V4-sized new models).

## 5. Guardrails (do not claim)

- No "recovered half-angle" for the immersed optimizer until S1 is done — the
  current number is bound/start-dependent.
- Do not assert 2nd-order *fields* (E_n, Maxwell pressure) until S3 is measured.
- Do not assert "shielding" while `S_E < 0` (S4).
- Do not use the 1.625 constant (S5) without checking Taylor (1964).
