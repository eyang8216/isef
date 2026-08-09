# 03 — Imposed-Taylor free-boundary verification (P3i)

**What to build:** The committed verification that the free-boundary solver
recovers Taylor's 49.29° half-angle. Impose the exact analytic Taylor
potential on the box boundary with the `ImplicitCone` as the immersed zero
equipotential, run the free-boundary solve with P1 + P2, and show the
amplitude-projected residual minimum is at 49.29° as the cap radius → 0.

**Why (decision from the 2026-08-09 grilling session):** the paper needs a
verifiable "solver reproduces Taylor's 49.3°" result. On the *grounded box*
the angle is shifted by the truncated domain and rounded cap (measured ~42°,
non-monotone under domain growth), so the controlled test imposes Taylor's
field directly and removes those effects by the cap → 0 limit. This is the
spec's accepted evidence path ("angle → 49.29° in the ideal limit").

**Setup (validated 2026-08-09):**

- Spherical coords about the apex at (0, z_apex=0.86): `ρ = √(r²+(z−z_apex)²)`,
  `cosθ = (z−z_apex)/ρ`. The cone (half-angle α = 49.290089°) is the zero
  equipotential because `P_{1/2}(cos(π−α)) = 0` (repo's
  `taylor_cone_half_angle_deg`; root at cosθ = −0.6522).
- Outer Dirichlet on the box ring = `φ = A·ρ^½·P_{1/2}(cosθ)` (`A = 1` for the
  trend; any amplitude, the projection absorbs it), `NaN` at the apex → 0
  (the ρ→0 limit). Conductor nodes zeroed (they are Dirichlet via the
  immersed pass).
- Verified: the solved potential matches the analytic field with error ∝ cap
  radius (2.77e-2 → 5.4e-4 as cap 0.05 → 0.001), flat in grid refinement —
  i.e., the machinery is correct and the only discrepancy is the cap model.

**The test (new `tests/test_taylor_onset.py`):**

1. For cap radius ∈ {0.05, 0.02, 0.01, 0.005, 0.001}: solve the imposed-Taylor
   problem, evaluate the P1-fixed Eₙ on the flank, compute the P2-projected
   residual over a half-angle sweep, record the argmin angle.
2. Assert: argmin → 49.29° as cap → 0, and ≤ ±0.5° at the smallest cap.
3. Assert the analytic amplitude identity at the smallest cap:
   `V0* = √(2γcosα / (ε₀·P^1_{1/2}(cos(π−α))²·sinα))`
   (derived and verified against the solver 2026-08-09; `P^1 = −0.9747`).

**Blocked by:** tickets 01 (Eₙ accuracy) and 02 (amplitude projection)

**Status:** needs-triage

- [ ] Imposed-Taylor setup helper (potential, boundary mask, apex-NaN handling)
- [ ] Sweep: projected-residual argmin angle vs cap radius
- [ ] Assert argmin → 49.29° with cap → 0; ≤ ±0.5° at smallest cap
- [ ] Analytic `V0*` identity asserted
- [ ] All 51 existing tests stay green

## Comments

- (2026-08-09, spec session) The user chose (i) as the committed deliverable;
  (iii) grounded-box extrapolation is ticket 04 (deferred).
- Do not use the raw analytic potential as the formal order test — the spec's
  2026-08-06 note forbids it (cap/singularity mix). This test verifies the
  free-boundary *angle*, not the discretization order.
