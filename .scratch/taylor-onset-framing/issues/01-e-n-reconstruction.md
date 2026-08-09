# 01 — Eₙ reconstruction accuracy (P1)

**What to build:** Make `solver/immersed.py::normal_field_on_interface` accurate
when the potential profile along the surface normal is strongly curved, which
currently breaks the one-sided quadratic `Eₙ = −(−3V_b + 4V(h) − V(2h))/(2h)`.

**Why:** Measured 2026-08-09 — on the exact analytic Taylor potential (imposed
as the box boundary condition, conductor values zeroed), the reconstructed Eₙ
overestimates the analytic field by 2.6× → 4.0× → 5.3× → 12.6× as the grid
refines 31×45 → 61×89 → 121×177 → 241×353. The Taylor profile along the normal
is `V(s) ≈ 1.39s + 515s² − 6.7e4s³` at the flank — far from quadratic at
practical `h`, so the 4-1 formula diverges. Any residual (and any recovered
angle) using Eₙ near the apex carries this bias. This is the precondition for
tickets 02 and 03.

**Approach (contained, no restructuring):**

- Richardson-extrapolate the potential before the one-sided derivative: solve
  on `h` and `h/2` (or use two solves inside the evaluation), extrapolate
  `φ ≈ φ_h + (φ_h − φ_{2h})/3`, then apply the one-sided formula. Acceptable
  cost inside the *verification* and *imposed-Taylor* paths; the optimizer's
  per-candidate cost is unchanged if the reconstruction defaults are kept.
- Alternatively: a higher-order one-sided stencil with more normal samples
  (4-point), if it passes the benchmark below; prefer the simplest change that
  passes.
- The change must not alter behavior for smooth profiles (existing
  `test_normal_field_one_sided` and the circle tests must stay green).

**Driving benchmark (add to `tests/test_immersed.py`):**

- Analytic Taylor potential `φ = A·ρ^½·P_{1/2}(cosθ)` about the apex
  (apex-centered, `cosθ = (z−z_apex)/ρ`), evaluated on grid nodes, conductor
  values zeroed; reconstructed `|Eₙ|` on flank points vs analytic
  `|Eₙ| = |A·ρ^−½·P^1_{1/2}(cos(π−α))|` with `α = 49.290089°`.
- Acceptance: ≤ 5% error at 61×89 and monotonically improving with
  refinement. Currently 300%+ and diverging.

**Blocked by:** None — can start immediately

**Status:** needs-triage

- [ ] `normal_field_on_interface` (or an option on it) returns accurate Eₙ on
      strongly curved profiles
- [ ] New benchmark test asserts ≤ 5% at 61×89, improving with refinement
- [ ] `test_normal_field_one_sided` and all existing immersed tests stay green
- [ ] Documented choice: Richardson vs higher-order stencil, with the
      measured numbers

## Comments

- (2026-08-09, spec session) The analytic-Taylor benchmark is the driving test;
  the box-solve profiles are smoother but share the cap-proximity bias, so the
  fix benefits the residual everywhere.
