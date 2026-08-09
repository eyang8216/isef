# 02 — Onset-amplitude projection in the immersed residual (P2)

**What to build:** Make the immersed optimizer objective scale-invariant by
projecting out the balance (onset) voltage analytically per candidate shape,
in `solver/optimization.py::_immersed_rms` (or a sibling used only by the
immersed path). Report the predicted onset voltage on `OptimizationResult`.

**Why:** Measured 2026-08-09 — at `V0 = 1000 V` on the meter-scale geometry
(γ = 0.022 N/m), the flank Maxwell pressure is `½ε₀Eₙ² ≈ 1e-4 Pa` vs capillary
`γκ ≈ 0.02–0.15 Pa` (~600× too weak; the example runs ~25× below the onset
voltage `V0* ≈ 21–26 kV`). The fixed-V0 residual is dominated by capillary
curvature variation, so the recovered angle is start-dependent and meaningless
(22.9°–47.5°). Projecting out the amplitude:

- makes the landscape a clean, well-posed V-shape with an interior minimum
  (~42° in the current 1×1 domain vs 49.29° ideal; the offset is the
  truncated-domain/cap effect, handled by ticket 03),
- removes the arbitrary `V0` from the objective,
- **predicts the onset voltage** — a new, verifiable, paper-worthy result.

**Math (flank samples, weights `w` from `arclength_weights`):**

```
a  = γκ − ⟨γκ⟩_w
e  = Eₙ / V0                      # field per volt (NOT Eₙ itself — units bug alert)
b  = e² − ⟨e²⟩_w
u* = ⟨a·b⟩_w / ⟨b²⟩_w            # u = ½ε₀V0²
R  = a − u*·b                     # amplitude-projected residual
V0* = √(2u*/ε₀)                   # predicted onset voltage
rms = √⟨R²⟩_w
```

**Acceptance (add tests in `tests/test_optimization.py` / `tests/test_immersed.py`):**

- The projected objective has a single interior minimum in `half_angle_deg`
  over the feasible box (no bound-chasing; the legacy fixed-V0 residual is
  retained and tested unchanged).
- `V0* ≈ 21–26 kV` at the current 1×1 domain, 45° cone (regression anchor;
  the early prototype's 23 V figure was a units bug — do not propagate it).
- `OptimizationResult` gains `onset_voltage_V` (finite, positive).
- Example 07 (or a small addition) prints the onset voltage and the projected
  landscape minimum.

**Blocked by:** ticket 01 (Eₙ bias pollutes the residual near the cap; P2's
numbers are only trustworthy once P1 lands)

**Status:** needs-triage

- [ ] Amplitude projection implemented in the immersed residual path
- [ ] Landscape test: single interior minimum over the feasible box
- [ ] `onset_voltage_V` reported; ≈ 21–26 kV regression anchor at 45°, 1×1
- [ ] Legacy fixed-V0 path and all 51 tests unchanged/green
- [ ] Example 07 prints onset voltage + projected minimum

## Comments

- (2026-08-09, spec session) Prototype (uncommitted) showed the V-shape with a
  minimum at 42°; the numbers at 44°+ are noisy, consistent with the P1 bias —
  re-measure after 01.
