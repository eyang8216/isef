# Spec: Taylor-Onset Framing & Verification (P1 + P2 + P3i)

**Status:** ready-for-agent (spec written 2026-08-09 after the grilling session;
tickets 01–03 in `issues/`, ticket 04 is deferred)

**Sources:** `docs/codebase_review_and_next_steps.md` (2026-08-04),
`.scratch/taylor-cone-fd-bcs/spec.md` (incl. its 2026-08-06 superseding note),
`docs/plans/2026-08-06-immersed-free-boundary.md`,
`docs/plans/2026-08-09-next-steps.md`, the merged v3 implementation
(eyang8216, `1ac7059`), and measurements taken 2026-08-09 during the interview.

---

## 1. Problem statement (measured, not guessed)

The immersed optimizer does not recover Taylor's 49.29° half-angle. Fresh runs
of `examples/07_immersed_free_boundary.py` land at 22.9°–47.5° depending on
start/options. This is **not a solver bug** — it is the wrong question being
asked of a correct field solver:

- The example fixes `V0 = 1000 V` and optimizes shape, but Taylor's balance is
  an **onset condition**: for a given shape the Young–Laplace–Maxwell balance
  `γκ = Δp + ½ε₀Eₙ²` determines the *voltage* (the amplitude), not the shape.
- At `V0 = 1000 V` on the meter-scale geometry (γ = 0.022 N/m), the Maxwell
  pressure on the flank is `½ε₀Eₙ² ≈ 1e-4 Pa` while the capillary pressure is
  `γκ ≈ 0.02–0.15 Pa` — **the field is ~600× too weak** (the example runs
  ~25× below the onset voltage `V0* ≈ 21–26 kV`, measured by the amplitude
  projection below). The fixed-V0 residual is therefore dominated by capillary
  curvature variation; the electric field barely enters, so the "recovered
  angle" is meaningless.
- Projecting out the onset amplitude (closed-form weighted least squares over
  `u = ½ε₀V0²`) turns the flat, meaningless landscape into a **clean V-shape
  with an identifiable minimum** (~42° in the current truncated 1×1 domain,
  vs 49.29° ideal) and predicts the onset voltage (`V0* ≈ 25 kV`). The
  remaining ~7° offset from 49.29° is the truncated-domain + rounded-cap
  effect, which the imposed-Taylor test (P3i) removes in a controlled way.

### What is verified today (do not rebuild)

| Item | Evidence |
|---|---|
| Immersed Dirichlet operator is 2nd-order on smooth curved boundaries | `test_smooth_immersed_manufactured_solution_second_order_convergence` (order ≈ 2.0) |
| Geometry/normals exact (contour δ = 0, unit normals) | 2026-08-09 measurement |
| Solved potential → analytic Taylor field as cap → 0 | error ∝ cap (2.77e-2 → 5.4e-4 as cap 0.05 → 0.001), flat in refinement |
| Tiny-cut conditioning (0 candidate failures) | `8e2a2c8` |
| Legacy staircase path intact | example 05: 43.5312° reproducible |
| 51 tests green | 2026-08-09 |

### Known weakness found during the interview (P1)

`normal_field_on_interface` uses a one-sided quadratic
`Eₙ = −(−3V_b + 4V(h) − V(2h))/(2h)`. Near the cone apex the potential profile
along the normal is far from quadratic (measured on the exact Taylor field:
`V(s) ≈ 1.39s + 515s² − 6.7e4s³`), so the reconstruction **overestimates Eₙ by
2.6× → 12.6× as h shrinks** (grid 31×45 → 241×353). This is exactly why the
spec's 2026-08-06 note forbids using the Taylor potential for the formal order
test; but it also means any residual (and any recovered angle) that uses Eₙ
near the cap carries a reconstruction bias. Fix first (P1).

---

## 2. Decisions (from the 2026-08-09 grilling session)

1. **Deadline exists; the paper needs verifiable results proving the solver
   works, with the angle near values from other studies (Taylor 49.3°).**
   `theory.tex` §1 itself states the solver "must first reproduce the classical
   Taylor cone half-angle in the charge-free conducting limit".
2. **Both framings** (onset/amplitude projection + a constraint/anchor) are
   wanted, but **minimal code change and no restructuring** take priority —
   the codebase is already complex.
3. **Verification path: (i) imposed-Taylor free-boundary test** as the
   committed deliverable. **(iii) ideal-limit extrapolation** (domain growth /
   cap shrink on the grounded-box problem) is written into this spec as later
   work, not part of the deadline milestone.

---

## 3. Solution

### P1 — Eₙ reconstruction accuracy (precondition)

Fix `normal_field_on_interface` (or add an option) so the one-sided derivative
is accurate near strongly curved potential profiles:

- Richardson-extrapolate the potential from two solves (h and h/2) before
  taking the one-sided derivative, or use a reconstruction with provably
  bounded error on the benchmark below. Contained to `solver/immersed.py` /
  `solver/fields.py`; no structural change.
- **Benchmark (the driving test):** on the *exact analytic Taylor potential*
  (imposed, with conductor values zeroed — see ticket 01), the reconstructed
  Eₙ on the flank must converge to the analytic value as h → 0 (target:
  ≤ 5% at 61×89, improving with refinement). Currently it diverges 2.6×–12.6×.
- For the *box-solve* profiles (smooth near the flank, singular only at the
  apex) the same fix removes the cap-proximity bias from the residual.

### P2 — Onset-amplitude projection in the immersed residual

In `_immersed_rms` (or a sibling used by the optimizer), project out the
balance voltage analytically per candidate shape:

- On the flank samples with weights `w`: `a = γκ − ⟨γκ⟩_w`,
  `e = Eₙ/V0`, `b = e² − ⟨e²⟩_w`, `u* = ⟨ab⟩_w/⟨b²⟩_w`,
  residual `R = a − u*·b`, RMS over the flank. Predicted onset voltage
  `V0* = √(2u*/ε₀)`.
- This makes the objective scale-invariant (the arbitrary `V0` no longer
  enters), gives a well-posed landscape (V-shape), and *predicts the onset
  voltage* — a new, verifiable, paper-worthy result.
- Reported alongside `OptimizationResult`: `onset_voltage_V` (`V0*`).
- **Acceptance:** the projected landscape has a single interior minimum in
  `half_angle_deg` over the feasible box (no more bound-chasing); `V0*` is
  finite and physically ordered (monotone in geometry scale); existing tests
  stay green (the legacy fixed-V0 path remains for regression).

### P3i — Imposed-Taylor free-boundary verification (the committed 49.29° test)

- Impose the exact analytic Taylor potential `φ = A·ρ^½·P_{1/2}(cosθ)`
  (apex-centered spherical coords, `cosθ = (z−z_apex)/ρ`) as outer Dirichlet
  on the box, with the `ImplicitCone` (49.29°) as the immersed zero
  equipotential. The interior solution then reproduces Taylor's field, and the
  potential error scales linearly with the cap radius (already demonstrated).
- Run the free-boundary solve with P1 + P2: the amplitude-projected residual
  minimum must be at 49.29° as the cap radius → 0 (cap ∈ {0.05, 0.02, 0.01,
  0.005, 0.001} trend) — the accepted "angle → 49.29° in the ideal limit"
  evidence. Assert the trend + final cap value within ±0.5° of 49.29°.
- Also assert the analytic amplitude identity: at the minimum,
  `V0* = √(2γcosα/(ε₀ P^1_{1/2}(cos(π−α))² sinα))` (derived 2026-08-09,
  verified against the solver).
- Files: `tests/test_immersed.py` (or a new `tests/test_taylor_onset.py`).

### P3iii — Ideal-limit extrapolation on the grounded-box problem (LATER, spec only)

Grow the domain / shrink the cap on the *actual* solver configuration
(grounded box, `rectangular_electrodes`) and document the angle trend toward
49.29° (or the documented reason the finite rounded truncated-domain problem
differs). Non-monotone behavior was observed in early sweeps (42° → 52°),
so the domain design must be careful. **Deferred** — do not block the deadline
milestone.

---

## 4. Verification gates

1. P1 benchmark: Eₙ reconstruction converges on the exact Taylor field
   (≤ 5% at 61×89).
2. P2: projected landscape has an interior minimum; `V0*` ≈ 21–26 kV at the
   current 1×1 domain (regression anchor); legacy path unchanged.
3. P3i: residual minimum → 49.29° as cap → 0; ±0.5° at the smallest cap;
   analytic `V0*` identity holds.
4. All existing 51 tests stay green; examples 05 and 07 still run.

## 5. Out of scope / guardrails

- No restructuring of `solver/optimization.py`'s candidate loop, no new
  parameterization (ADR-0001/0003 stay in force).
- No volume/contact-line constraint in the deadline milestone (that is the
  future work; the amplitude projection is the minimal well-posed fix).
- Do not claim "recovered 49.29° on the grounded box" — the committed claim is
  the imposed-Taylor ideal-limit verification (P3i) plus the onset-voltage
  prediction (P2).
- The `V0* ≈ 23 V` figure printed by early projection prototypes was a units
  bug (missing `1/V0²`); the correct value is `≈ 25 kV`. Do not propagate the
  wrong figure.
