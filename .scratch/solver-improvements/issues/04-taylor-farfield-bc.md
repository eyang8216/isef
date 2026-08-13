# 04 — Analytical Taylor far-field boundary condition

**What to build:** The immersed-verification mode applies the analytical Taylor potential (from ticket 01) at the outer boundary instead of grounding it, so the recovered interface half-angle lands within ±1.5° of the ideal 49.3° instead of the ~42.5° truncation artifact. Exposed as a UI control defaulting to the Taylor far-field, with the grounded box retained as a selectable alternative for comparison.

**Blocked by:** 01 — Extract and test the analytical Taylor potential; 02 — Rescale geometry to realistic experimental dimensions.

**Status:** ready-for-agent

- [ ] Outer boundary uses the analytical Taylor potential when the far-field option is on; the grounded box remains a selectable alternative.
- [ ] Recovered interface half-angle is within ±1.5° of 49.3° at the new mm scale.
- [ ] Imposed-Taylor amplitude identity ratio stays ≈ 1.005 (electrostatic solver still accurate).
- [ ] Residual at the recovered half-angle is small (< 0.1 Pa).
