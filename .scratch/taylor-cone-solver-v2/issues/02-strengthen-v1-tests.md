# 02 — Strengthen V1 test foundations

**What to build:** Add two tests that were thin enough in V1 to miss sign bugs the optimizer would silently amplify. No new modules — only additions to existing test files.

`tests/test_electrostatics.py` needs a convergence-order test: run the same manufactured-solution case at two grid resolutions and assert the L2 error at the finer resolution is ≤ 0.6× the coarser error (second-order halving). This catches regressions in the operator or boundary-condition application at the electrostatics level, not just at the manufactured-Poisson integration level.

`tests/test_residual.py` needs a residual-decreases test: construct two interfaces from the same cone family — one with a half-angle closer to the equilibrium value, one farther away — and assert the closer one produces a lower RMS residual. This confirms the optimizer has a meaningful signal to follow before it is built.

**Blocked by:** 01 — threshold closure

**Status:** ready-for-agent

- [ ] `tests/test_electrostatics.py`: convergence-order test added — L2 error at 2× resolution is ≤ 0.6× coarse error
- [ ] `tests/test_residual.py`: residual-decreases test added — better-shaped interface produces lower RMS residual than worse-shaped one
- [ ] All tests pass (target: 23+ tests)
