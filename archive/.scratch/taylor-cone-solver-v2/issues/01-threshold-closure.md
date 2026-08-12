# 01 — Threshold space-charge closure

**What to build:** Add the nonlinear threshold-activated closure to `solver/space_charge.py` as a standalone `solve_threshold_shielding()` function, extend `tests/test_space_charge.py` with a shielding sanity test, and add `examples/06_threshold_space_charge.py` as a runnable demonstration.

The closure is `ρ_e = ρ_max·(1 - exp(-(|E| - Ec)/Es))₊` — nodes where `|E| < Ec` are exactly zero. The function must reuse the existing fixed-point iteration loop from `solve_gaussian_shielding()`; only the charge-update step differs. Per ADR-0002, this function is never called from within the shape optimizer.

The example script should run end-to-end, converge the fixed-point iteration, and print the apex-local shielding metric `S_E`. The shielding metric must be positive for physically sensible parameters (`S_E > 0` means field was reduced).

**Blocked by:** None — can start immediately

**Status:** completed

- [ ] `solve_threshold_shielding()` implemented in `solver/space_charge.py`, reusing the fixed-point loop
- [ ] Nodes with `|E| < Ec` produce exactly zero charge density
- [ ] `tests/test_space_charge.py` extended: shielding sanity test confirms `S_E > 0` for sensible `Ec`, `Es`, `ρ_max`
- [ ] `examples/06_threshold_space_charge.py` runs without error and prints a positive apex-local shielding metric
- [ ] All existing 21 tests still pass
