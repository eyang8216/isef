# 01 — Eₙ reconstruction accuracy (P1)

**Status:** ready-for-review (implemented 2026-08-09, commit pending)

**What was built:** `solver/immersed.py::normal_field_on_interface` now uses a
one-sided **cubic-exact 4-point stencil** with samples at **full-cell
distances** (`d = max(dr, dz)`, then `2d`, `3d`):

```
Eₙ = -(-11·V_b + 18·V(d) - 9·V(2d) + 2·V(3d)) / (6·d)
```

`sample_distance` remains overridable. `solver/optimization.py`'s immersed
angle-cap clearance updated to `3·max(dr, dz)` so the new samples stay in-grid.

## Why the original premise was wrong (measured 2026-08-09)

The ticket blamed "strongly curved normal profiles break the one-sided
quadratic". Investigation found **two distinct causes**:

1. **Sub-cell sampling across the cut cell (dominant).** The old stencil
   sampled at `h = 0.5·min(dr,dz)` — half a cell from the surface — where
   bilinear interpolation straddles the cell cut by the conductor surface.
   The contaminated values, amplified by `1/h`, gave Eₙ errors that **grew
   with refinement**: box problem 61×89 → 241×353: ~0% → +30–50%; circle
   manufactured problem: +10–30% at all grids. The solved *potential* is
   accurate (converges 2nd order; fixed-point values stable to 4 digits) —
   the error is the interpolation, not the solve.
2. **Profile curvature (secondary).** Even on *exact* profile values the
   quadratic 3-point stencil is off by ~16% on the circle's boundary profile
   (strong cubic terms); the 4-point cubic-exact stencil is exact there
   (+0.0% on exact data).

Neither Richardson-of-potential (helped only where the profile is linear:
box 0–1%, circle unchanged) nor the 4-point stencil alone (worse on solved
data: interpolation contamination amplified) fixed it. **The combination that
works is full-cell samples + the cubic-exact stencil.**

## Measured results (new reconstruction vs analytic/ground truth)

| Case | Old (3-pt, half-cell) | New (4-pt, full-cell) |
|---|---|---|
| Box 45°, 61×89 / 121×177 / 241×353 (vs Richardson ground truth) | −0%/+14%/+30% | −2%/−0%/+0% |
| Circle 97×129 / 193×257 (vs 2R·e^z) | +10–22% / +0–24% | +1–3% / +0–1% |
| Linear-profile regression (`test_normal_field_one_sided`) | exact | exact |
| True-cone analytic (tiny cap) | ~1.2× | ≤ 1.04× |

Side effect: example 07/08 recovered angle moved 22.9° → 50.9° (closer to
49.29°) with 0 candidate failures — the Eₙ bias had been dragging the
optimizer to small angles. **Caveat (from code review):** 50.9° sits at the
geometric angle cap for example 07's grid (50.95°) — a boundary optimum, not
physical validation; do not cite it as such.

## Acceptance (all met)

- [x] `normal_field_on_interface` accurate on strongly curved profiles
- [x] New benchmark: `test_immersed_en_matches_analytic_on_manufactured_circle`
      asserts ≤ 5% at 97×129 and improvement at 193×257 (circle Eₙ = 2R·e^z)
- [x] `test_normal_field_one_sided` and all existing tests stay green (52 total)
- [x] Documented choice: full-cell samples + cubic-exact stencil, with the
      measured numbers above

## Comments

- (2026-08-09) The clean seam is the manufactured *circle* (exact geometry,
  independent analytic Eₙ), not the Taylor cone: the ImplicitCone flank is
  offset from the sharp Taylor cone by `R_cap·cos(2α)/cosα`, which confounds
  any Taylor-based Eₙ benchmark (this is why the spec's note forbids the
  Taylor potential for formal order tests).
- Remaining for tickets 02/03: the onset-amplitude projection (02) and the
  imposed-Taylor angle test (03) now run on bias-free Eₙ.
