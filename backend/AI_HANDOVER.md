# AI Handover Document

## ✅ RESOLVED (2026-08-16) — Verified root cause and committed fix

**The 1.3° bias is fixed. With the new defaults (121×177 grid, 0.5% apex cap,
window [0.30, 0.60]), the recovered angle is 49.203° (error −0.087°), identity
ratio 1.0005, identity exponent crossing 49.254°.**

### What the investigation actually found (all claims below verified by experiment)

1. **The projected-residual argmin is an ill-conditioned observable — this is
   the root cause, not the apex radius or the window.**
   The amplitude projection absorbs the dominant `1/ρ` term of the balance, so
   the remaining landscape is flat to within its discretization floor over
   ±2° around the minimum (depth `rms(49.29°)/min` measured 1.0–4.4×) and is
   dominated by near-apex `E_n` reconstruction noise. The argmin wanders with
   grid/cap/window: measured 47.6°–52° across the parameter matrix (e.g.
   cap=10μm → 51.0°, cap=200μm → 49.29° *by coincidence*, cap=500μm → 48.0°,
   window [0.35,0.70] → 44.25°, [0.40,0.75] → 51.7°). The old "48.00°" was
   **noise, not physics** — it did not converge with refinement (48.0° at
   both 121×177 and 241×353) and the identity-case argmin was biased the
   *opposite* way (50–51°).

2. **Hypothesis A (apex radius) — REFUTED as stated.** Smaller caps do NOT
   monotonically recover 49.29°: cap 500→200→100→50→10μm gave argmins
   48.0→49.29→50.5→51.0→51.0 at 61×89. The cap does shift the physics, but
   only ~0.4° (measured via the exponent observable: 48.83° at 500μm vs
   49.22° at 50μm), and it is NOT the 1.29° error.

3. **Hypothesis B (sampling window) — REFUTED as stated.** Widening the
   window to [0.15, 0.85] makes things *worse* (argmin 46.0°, identity ratio
   1.085) because the base samples are distorted by the bottom wall. The
   correct move is *narrowing* away from the apex: [0.30, 0.60] lowers the
   residual floor ~10× and removes cap sensitivity.

4. **The machinery is accurate.** The solve reproduces the analytic Taylor
   field (reconstructed `E_n` within 0.4% of `A·ρ^{-1/2}|P₁|`), and the
   identity ratio is 1.0005–1.0032 at the new window. The identity ratio
   1.063/argmin 52.0° in the old JSON was an artifact of n_interface=121 +
   window [0.15, 0.85] (both now known-bad choices).

### The fix (committed)

- **New primary observable**: the flank field power-law exponent
  `E_n² ~ ρ^p`. The YLM balance is scale-consistent iff `p = −1` (capillary
  `γκ ~ cotα/ρ` on the flank). The crossing of `p(α)+1 = 0` is monotone in
  α, grid-convergent (49.13 → 49.22 → 49.23° at 61×89 → 121×177 → 241×353,
  cap=50μm), and robust to window (±0.05°). Implemented as
  `optimization.flank_field_exponent()` + `_exponent_crossing_deg()` in
  `app_backend.py`.
- **Defaults changed**: `apex_radius` 0.5mm → 0.05mm (0.5% of spacing);
  Taylor window [0.30, 0.75] → [0.30, 0.60]; default grid 61×89 → 121×177.
  UI: apex slider default 5% → 0.5%, grid slider gains "Very Fine (241×353)".
- **Grounded BC unchanged in meaning**: the exponent never crosses −1 there
  (field decays more slowly than ρ^{-1}), so the argmin fallback keeps the
  ~43° truncation-artifact behavior and the 2.8–3.0 kV onset voltage.
- `identity_argmin_deg` (noisy, reported 52.0°) replaced by
  `identity_exponent_crossing_deg` (~49.25°); JSON schema bumped to v2.
- Tests: `test_taylor_onset.py` rewritten around the exponent crossing
  (asserts |crossing − 49.29| ≤ 0.1–0.2° by grid); new
  `test_free_boundary_recovers_taylor_angle` guards |recovered − 49.29| ≤
  0.2° at the default grid.

### Verified results at the new defaults

| Grid | Recovered (exponent) | Identity ratio | Identity crossing |
|---|---|---|---|
| 61×89  | 49.134° | 1.0069 | 49.18° |
| 121×177 (default) | 49.203° | 1.0005 | 49.254° |
| 241×353 | 49.23° | 1.0024 | 49.26° |

Success criteria met: **49.29° ± 0.2° at the default grid; oscillation ratio
no longer applies to the recovered-angle observable** (the exponent curve is
monotone; the residual landscape is still plotted for diagnostics).

---

## Historical record (original problem statement — superseded findings below)

## Critical Issues: Taylor Angle Verification

### Problem Summary

The immersed boundary verification (`backend/solver/app_backend.py::run_immersed_verification`) is **consistently recovering 48.0°** instead of the theoretical **Taylor angle of 49.29°**, with a **highly noisy landscape** showing multiple spurious local minima.

### Symptoms

From `backend/results/latest_verification_run.json`:
- **Recovered angle**: 48.00° (should be 49.29°)
- **Error**: 1.29° (~2.6% relative error)
- **Oscillation ratio**: 47% (landscape oscillates wildly)
- **Local minima**: 4 distinct local minima instead of 1 smooth minimum
- **Grid resolution tested**: Both 121×177 and 241×353 show the same behavior
- **RMS at Taylor angle**: 0.0307 Pa (2.4× worse than the 48° minimum of 0.0127 Pa)

**Key observation**: Even with Very Fine grid (241×353), the problem persists. This rules out simple grid discretization as the sole cause.

### What Was Investigated

#### 1. Grid Resolution (RULED OUT as sole cause)
- Tested: 121×177 → 241×353 (4× more points)
- Result: Still recovers 48.0°, noise actually increased (32% → 47% oscillation)
- Conclusion: Grid resolution alone does not fix the issue

#### 2. Interface Sampling Parameter `n_interface`
- Tested: Increasing from 41 → 61 → 101 points on interface
- Result: **Made things WORSE**
  - n_interface=101 recovered 42.9° (7° error!)
  - n_interface=61 showed 47% oscillation
  - Original n_interface=41 was actually the best
- Conclusion: **Do not increase n_interface** - it's a red herring

### Root Cause Hypotheses (UNVERIFIED)

Based on detailed investigation, the most likely causes are:

#### A. Apex Radius Too Large (HIGHLY LIKELY)
**Current**: `apex_radius = 0.5mm = 5% of 10mm domain`
- The theoretical Taylor cone has a **perfect point apex**
- A 0.5mm rounded spherical cap is NOT a small perturbation
- This breaks the ideal Taylor geometry and could shift equilibrium angle
- **Recommended test**: Reduce to 50-100 μm (<1% of domain)

#### B. Sampling Window Too Narrow (LIKELY)
**Current**: Residual computed over `z ∈ [30%, 75%]` of domain = [3.0mm, 7.5mm]
- Apex is at 8.6mm, so sampling stops 1.1mm below apex
- Misses the near-apex region where Taylor physics is strongest
- **Grounded BC uses wider window**: [15%, 85%]
- **Recommended test**: Expand to [15%, 85%] like grounded BC

#### C. Combination of A + B
- Most likely scenario: both contribute to the error
- Apex radius shifts equilibrium, narrow window reinforces the bias

### Why This Matters

1. **Scientific validity**: Cannot publish results claiming Taylor cone physics if we're 1.3° off
2. **Landscape noise**: 47% oscillation suggests the residual metric is unreliable
3. **Verification failure**: The identity check at 49.29° should minimize, but it's 2.4× worse than 48°

### What Needs to Be Done

> **SUPERSEDED 2026-08-16**: the systematic parameter study was executed and
> the root cause turned out to be the *observable* (projected-residual argmin),
> not the parameters. See the RESOLVED section at the top. The parameter
> studies that refuted the original hypotheses are preserved in the "What Was
> Investigated" section below.

#### Option 1: Systematic Parameter Study (RECOMMENDED)
Test combinations of:
- Apex radius: [50, 100, 200, 500] μm
- Sampling window: [15-85%, 20-80%, 30-75%]
- Grid resolution: Fine (121×177), Very Fine (241×353)
- n_interface: Keep at 41 (do NOT increase)

**Expected outcome**: If apex radius is the issue, smaller values should recover angles closer to 49.29°

> **Result (2026-08-16)**: executed. Argmins did NOT converge to 49.29° with
> smaller caps (48.0 → 51.0°); wider windows made things worse. The argmin
> was noise. The exponent observable (see RESOLVED) does converge.

#### Option 2: Code Changes Required
If parameter tuning doesn't work, may need to:
1. Reduce field sampling distance (currently `d = max(dr, dz)`, try `0.5 * max(dr, dz)`)
2. Investigate the amplitude projection math in `_immersed_projected_stats`
3. Validate the `taylor_potential` analytical solution implementation
4. Check if the flank mask is being applied correctly

> **Result (2026-08-16)**: none of these were the cause. The solve, E_n
> reconstruction (0.4% vs analytic), amplitude projection, and `taylor_potential`
> are all verified accurate. The implemented fix is a new observable, not a
> code fix in these components.

### Key Files and Functions

**Verification entry point:**
- `backend/solver/app_backend.py::run_immersed_verification(params)` (line 382)

**Residual calculation:**
- `backend/solver/optimization.py::_immersed_projected_stats()` (line 83)
  - This computes the amplitude-projected YLM residual
  - Uses interface sampling window `z_min`, `z_max`
  - Calls `cone.sample_graph(z_min, z_max, n_interface)`

**Sampling window definition:**
- Line 404: `taylor_z_min, taylor_z_max = 0.30 * z_max, 0.75 * z_max` ← HARDCODED
- Line 403: `z_min_w, z_max_w = 0.15 * z_max, 0.85 * z_max` (for grounded BC)

**Apex radius:**
- Line 261 in streamlit_app: `value=verif_spacing * 0.05 * 1e6` = 5% of domain
- Passed to `ImmersedVerificationParams(apex_radius=...)` at line 299

### Code Changes Attempted and Reverted

During this session, attempted to:
1. Add UI controls for `n_interface`, `z_min_frac`, `z_max_frac`
2. Add dataclass fields to `ImmersedVerificationParams`
3. Created comprehensive documentation

**Why reverted**: Implementation complexity vs. benefit. Better to:
- First validate the hypothesis with manual parameter edits
- Then add UI controls if successful
- Avoid adding complexity before understanding the problem

### How to Test Manually

To test the apex radius hypothesis:

1. **Edit `backend/app/streamlit_app.py` line 261:**
   ```python
   # Current:
   value=verif_spacing * 0.05 * 1e6,  # 500 μm
   
   # Change to:
   value=100.0,  # 100 μm test
   ```

2. **Edit `backend/solver/app_backend.py` line 404:**
   ```python
   # Current:
   taylor_z_min, taylor_z_max = 0.30 * z_max, 0.75 * z_max
   
   # Change to:
   taylor_z_min, taylor_z_max = 0.15 * z_max, 0.85 * z_max
   ```

3. **Run verification** with Very Fine (241×353) grid

4. **Check results**:
   - If recovered angle moves toward 49.29°: confirms apex radius hypothesis
   - If landscape smooths out: confirms sampling window hypothesis
   - If both improve: confirms both contribute

### Success Criteria

**Target**: Recover 49.29° ± 0.2° with oscillation ratio <10%

**Current**: 48.00° with 47% oscillation

**Gap**: 1.29° error and 37% excess noise

### Additional Notes

- The code comments in `run_immersed_verification` say "recovering ~48 deg" is expected, but this was likely written to match observed behavior, not justified from first principles
- The identity check (`identity_ratio ≈ 1.005`) validates the solver works correctly at 49.29°, which makes the 48° recovery even more suspicious
- The consistent recovery at 48° across different grid resolutions suggests it's a **geometric bias**, not numerical noise
- Do NOT attempt to add smoothing/filtering to the landscape - this masks the problem rather than fixing it

### References

- Latest verification run: `backend/results/latest_verification_run.json`
- Solver run: `backend/results/latest_solver_run.json`
- Taylor angle calculation: `backend/solver/verification.py::taylor_cone_half_angle_deg()` (line 104)
- Analytical Taylor potential: `backend/solver/taylor_analytical.py::taylor_potential()` (line 19)

---

**Status**: ~~Investigation complete, root causes identified, manual testing
needed to validate hypotheses before implementing UI changes.~~
**RESOLVED 2026-08-16**: root cause verified (ill-conditioned residual-argmin
observable), fix implemented and committed (flank exponent crossing + default
cap/window/grid changes), tests updated and passing. See the top of this
document.
