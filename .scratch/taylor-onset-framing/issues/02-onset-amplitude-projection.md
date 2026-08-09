# 02 — Onset-amplitude projection in the immersed residual (P2)

**Status:** ready-for-review (implemented 2026-08-09, commit pending)

**What was built:** the immersed optimizer objective is now scale-invariant.
`solver/optimization.py::_immersed_rms` computes the amplitude-projected YLM
residual (new `_immersed_projected_stats` returns `(rms, onset_voltage_V)`; the
objective keeps the scalar rms). `OptimizationResult` gains `onset_voltage_V`.
Example 07 prints it.

**Math (flank samples, weights `w`):**

```
a  = γκ − ⟨γκ⟩_w
e  = Eₙ / V0                     # field per volt (NOT Eₙ — units bug alert)
b  = e² − ⟨e²⟩_w
u* = ⟨a·b⟩_w / ⟨b²⟩_w           # u = ½ε₀V0²; weighted least-squares amplitude
R  = a − u*·b                    # amplitude-projected residual
V0* = √(2u*/ε₀)
```

The old fixed-V0 residual is the special case `u = ½ε₀V0²` — the projection
replaces the arbitrary voltage with the per-shape balance voltage. A
degenerate guard raises when the flank field is constant (`⟨b²⟩ ≈ 0`).

## Measured (with the P1-fixed Eₙ, 61×89, 1×1 domain, γ = 0.022)

| angle | 30° | 35° | 40° | 44° | 45° | 48° | 49.29° | 52° |
|---|---|---|---|---|---|---|---|---|
| proj RMS (Pa) | 2.08e-2 | 1.75e-2 | 1.44e-2 | **1.39e-2** | 1.42e-2 | 1.88e-2 | 2.43e-2 | 4.53e-2 |
| V0* (kV) | 28.5 | 28.4 | 28.3 | 28.2 | 27.7 | 26.8 | 25.8 | 13.4 |

- Clean V-shape, interior minimum at **44°** — the pre-P1 noise at 44°+ is
  gone (the ticket's prediction was correct).
- The `apex_radius` direction remains weakly bound-favoring at the optimum
  angles (projected RMS 40°: 2.48e-2 → 1.28e-2 from r=0.025 → 0.10). The
  projection makes the **angle** identifiable; the model still has no
  preferred apex radius without a volume/contact-line constraint (documented
  in the spec; future work). The test asserts the angle direction only.
- Example 07 with the projected objective converges to **42.8°** (near the
  interior minimum) instead of the flat-landscape 22.9°/50.9°, and reports
  `V0* ≈ 28.9 kV`.

## Acceptance (all met)

- [x] Amplitude projection implemented in the immersed residual path
- [x] Landscape test `test_immersed_projected_residual_has_interior_angle_minimum`:
      single interior minimum in the angle direction (~44°), monotone rise
      both sides
- [x] `onset_voltage_V` reported; `test_immersed_projected_onset_voltage_anchor`
      pins V0* ≈ 28 kV at 45°, 1×1 (band 20–35 kV — the 23 V units bug is
      guarded against)
- [x] Legacy fixed-V0 path and all existing tests unchanged (54 total green)
- [x] Example 07 prints the onset voltage + converged angle

## Comments

- (2026-08-09) The V0* regression anchor was updated from the ticket's
  pre-P1 range (21–26 kV) to the measured post-P1 value (≈ 28 kV at 45°) —
  the P1 Eₙ fix shifted the numbers ~10%.
- The radius-direction bound-chasing is a documented limitation, not a
  regression: it matches the spec's "no volume/contact-line constraint" gap
  and is addressed by ticket 04 / future work, not this ticket.
