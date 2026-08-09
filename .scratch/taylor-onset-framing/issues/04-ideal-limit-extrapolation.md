# 04 — Ideal-limit extrapolation on the grounded-box problem (P3iii)

**What it asks:** Document the angle trend of the *actual* solver
configuration (grounded box, `rectangular_electrodes`) toward 49.29° as the
domain grows and the cap shrinks — or document the physical reason the finite
rounded truncated-domain problem cannot reach it.

**Why it exists:** the committed verification of 49.29° is the imposed-Taylor
test (ticket 03). This ticket is the paper's optional "on its own" story:
does the grounded-box free-boundary solve approach 49.29° in the ideal limit?

## Completed — measured finding (2026-08-09, with P1+P2 machinery)

**The grounded-box projected residual does NOT recover 49.29° at any domain
size; the argmin moves to *larger* angles as the box grows, and the
49.29° candidate does not improve with growth (rms@49.29: 2.4e-2 → 1.7e-2 →
2.1e-2 → 2.5e-2 across 1×1 → 3×3).** Reproducible table from
`examples/09_ideal_limit_study.py` (window z ∈ [0.15, 0.85], cap = 0.05):

| domain | argmin | rms@argmin | rms@49.29 |
|--------|--------|-----------|-----------|
| 1×1    | 45.0°  | 1.42e-2   | 2.44e-2   |
| 1.5×1.5| 52.5°  | 1.58e-2   | 1.66e-2   |
| 2×2    | 60.0°  | 1.69e-2   | 2.13e-2   |
| 3×3    | 75.0°  | 1.65e-2   | 2.50e-2   |

(At 3×3 the residual is still decreasing at the 75° sweep edge; caps 0.02 and
0.01 shift the argmin by ≤2.5° and do not change the direction of the trend.)

**Why — two measured facts, not a solver bug:**

1. **The grounded-box field is not the ideal conical field.** For the ideal
   cone E ~ ρ^{−1/2}, so Eₙ·√ρ is constant along the flank. Measured spread
   is 47% (1×1) and 61% (3×3) — the deviation *grows* with the box. The
   rounded cap regularizes the apex (finite E), and the finite box distorts
   the mid-flank field; there is no conical plateau in any box tried.
2. **In a large box the flattest cones balance best.** At large half-angle
   the flank curvature cos(α)/R and the field profile both become nearly
   uniform, so their *shapes* match better — the amplitude-projected residual
   (P2) is a shape-matching measure and therefore prefers flat cones as the
   box grows. This is a model property: a truncated perfect cone in a finite
   grounded box (no nozzle pinning, no extractor field structure) is not
   Taylor's meniscus problem.

**Why the solver is nevertheless correct:** the imposed-Taylor verification
(ticket 03, `tests/test_taylor_onset.py`) imposes the exact analytic Taylor
field on the box boundary and reproduces the analytic balance amplitude to
ratio 1.009, with its argmin ~1° from 49.29°. Taylor's 49.29° is a *local
asymptotic* property of the meniscus in the conical field; the correct
verification is the imposed-Taylor test, and the grounded-box sweep documents
why the "on its own" story does not produce the angle.

## Artifacts

- [x] Domain/cap sweep table for the grounded-box projected objective
  (`examples/09_ideal_limit_study.py` Part A)
- [x] Documented reason the grounded-box problem cannot reach 49.29°
  (docstring + this ticket; `examples/09_ideal_limit_study.py` Parts B–C)
- [ ] Recorded in the paper as the ideal-limit discussion, not a headline
  (paper task, outside this repo)

**Status:** done for the milestone (study + documented finding committed);
paper write-up is a separate task.
