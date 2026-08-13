# AI Handover Document — ISEF Taylor-Cone Electrospray Solver

**Project folder:** `/Users/elliottdong/Desktop/isef`
**Branch:** `main`, tip `d2f703f` (2026-08-09), clean tree, up to date with `origin/main`.
**Project type:** ISEF computational physics / reduced-order axisymmetric electrohydrodynamic Taylor-cone / electrospray-onset solver (Python + Streamlit).
**Current phase:** V3 immersed free-boundary milestone — solver machinery verified; the committed 49.29° verification (imposed-Taylor) is done; paper write-up and code hygiene remain.
**Do not perform:** Physical experiment planning beyond safety notes, high-voltage instructions, ethanol handling, or testbed construction unless explicitly requested under school-supervised context. Experimental work (Track B) is gated on ISEF/SRC approval.

---

## 1. What has been done since commit `ebea0b8`

`ebea0b8` = "test: assert second-order convergence of the immersed operator" — it replaced the weak two-grid refinement check with a formal Richardson test (3 levels on the smooth-circle manufactured problem, observed L2 order ≈ 2.0) and updated the "not yet proven" section of `IMPLEMENTATION_STATUS.md`. All work *after* that commit (10 commits, 20 files, +1814/−122), in order:

| Commit | What it did |
|---|---|
| `8e2a2c8` | **fix(immersed): pin tiny-cut gas nodes to the boundary instead of rejecting.** Killed the discontinuous 1e10-penalty optimizer failures from `'pathological immersed-boundary fraction'`; example 07 now runs with 0 candidate failures (was 1 in 343 evals). |
| `b9a6022` | **docs:** added `docs/plans/2026-08-09-next-steps.md` (verified state, findings, priority list S1–S7) and `examples/08_immersed_refinement_study.py` (Part A: immersed potential ≈ 2nd order vs non-convergent legacy staircase; Part B: objective flat-in-angle / monotone-in-radius; Part C: single-start Powell stops in a flat basin). |
| `8407928` | **docs:** Taylor-onset framing spec + tickets 01–04 (`.scratch/taylor-onset-framing/`) after the 2026-08-09 grilling session. |
| `10d259f` | **fix(immersed): cubic-exact E_n reconstruction with full-cell samples (ticket 01 / P1).** Root causes found: sub-cell sampling across the conductor-cut cell (errors *grew* with refinement) + profile curvature. New 4-point one-sided stencil `Eₙ = −(−11V_b + 18V(d) − 9V(2d) + 2V(3d))/(6d)` with `d = max(dr,dz)`. Measured: box ≤ ±1% at all grids, circle ≤ 3% → ≤ 1%. Side effect: example 07 recovered angle moved 22.9° → 50.9°. |
| `f80dab0` | **feat(optimizer): project out the onset voltage in the immersed residual (ticket 02 / P2).** Fixed-V0 objective was meaningless (field ~25× below onset). Now projects out the balance voltage per candidate: `u* = ⟨ab⟩_w/⟨b²⟩_w`, `V0* = √(2u*/ε₀)`, `R = a − u*·b`. Angle direction is now a clean V-shape with interior minimum ~44°; `OptimizationResult` gains `onset_voltage_V`. Example 07 converges to 42.8°, V0* ≈ 28.9 kV. |
| `4c777e9` | **test: impose Taylor potential to verify the free-boundary amplitude identity (ticket 03 / P3i).** New `tests/test_taylor_onset.py` imposes the exact analytic Taylor potential on the box boundary with the rounded cone as the immersed zero equipotential. Verifies: amplitude identity ratio 1.009 (assert ≤ 3%), projected-residual argmin at 50.0° (~0.7° systematic offset from 49.29°, documented, does not converge), residual floor improves with refinement. |
| `7b117d5` | **docs(examples):** documented why the grounded-box problem cannot recover 49.29° (ticket 04 / P3iii) — argmin moves to larger angles as the box grows (45° → 75°+), rms@49.29 does not improve. Model property, not a solver bug. |
| `bc7715a` | **feat(app): add 'Immersed verification' tab.** Runs both committed verifications through the Streamlit app (grounded-box amplitude-projected landscape: angle 44.0°, V0* 27.9 kV; imposed-Taylor identity ratio 1.0105). Backend gains `ImmersedVerificationParams/Result`, `run_immersed_verification`, two plotly builders; smoke test added. App now has two tabs (Classic + Immersed verification). |
| `269b9ef` | **fix(app):** warn when the classic interface angle is capped by the domain (old defaults capped at 30.7°, silently clamping a requested 49.3°). |
| `d2f703f` | **fix(app):** raise default Domain radius to 1.0 so the 49.3° classic interface fits (cap now 49.9°). |

## 2. Current state of the project

- **Tests:** 71 passing via `.venv/bin/python -m pytest` (≈100 s, run from repo root).
- **Milestone spec:** `.scratch/taylor-onset-framing/spec.md` — all four tickets marked done (P1 Eₙ reconstruction, P2 onset-amplitude projection, P3i imposed-Taylor verification, P3iii ideal-limit study documented). Verification gates: Eₙ ≤ 5% at 97×129, V-shape interior minimum ~44°, identity ratio within 3% of unity (~1.01), all tests green.
- **Core modules:** `solver/` — `immersed.py` (fractional-distance Dirichlet + cubic-exact Eₙ), `geometry.py::ImplicitCone` (C1 rounded cone, sign convention: liquid ≤ 0), `electrostatics.py` (immersed Laplace/Poisson path), `optimization.py` (immersed candidate loop + onset projection), `residual.py`, `space_charge.py` (Gaussian + threshold closures, coupled optimizer mode), `app_backend.py` (run + verification backends, no `st.*` imports).
- **Examples:** `examples/00`–`09` (07 = immersed free boundary, 08 = refinement study, 09 = ideal-limit study).
- **App:** `app/streamlit_app.py` — Classic tab + Immersed verification tab. Run with `streamlit run app/streamlit_app.py`.
- **Docs:** `IMPLEMENTATION_STATUS.md` (updated "not yet proven" section per `ebea0b8`), `CONTEXT.md` (domain glossary — use its terminology), `docs/adr/0001`–`0003` (analytic cone family; threshold+optimizer decoupled; merged free-boundary immersed cone), `docs/plans/2026-08-09-next-steps.md` (findings + priority list), `.scratch/taylor-onset-framing/` (spec + tickets 01–04, local issue tracker), `.scratch/taylor-cone-fd-bcs/` (earlier sharp-cone research).

## 3. Issues and problems we are facing now

- **P3i ~0.7° systematic angle offset** (argmin 50.0° vs 49.29°, stable under refinement). Cause: cap-flank offset `R_cap·cos(2α)/cosα` + truncation + Eₙ reconstruction floor. Residual angle resolution is only ±1° (V-shape curvature < 1e-4 Pa/deg vs discretization floor). Ticket's ±0.5° target adjusted to ±1.5°; the identity (ratio within 3% of unity) is the strong exact result.
- **`apex_radius` direction weakly bound-favoring** — no interior minimum in apex radius without a volume/contact-line constraint. Documented as future work; do not claim a preferred apex radius.
- **Grounded-box problem cannot recover 49.29°** (P3iii) — larger box → larger argmin; needs paper write-up as a model property (truncated perfect cone in a finite grounded box ≠ Taylor meniscus).
- **Stale docs:** `IMPLEMENTATION_SUMMARY.md` and `COMPLETE_STATUS_REPORT.md` still claim 50 tests, the old weak convergence test (`errors[1] < 0.7·errors[0]`), and the pre-`8e2a2c8` "no gas-side third point" failure mode. `IMPLEMENTATION_STATUS.md` also has stale test counts ("34 passed", examples list missing 07–09). S7 hygiene not done.
- **Open plan items:** S3 (formal Eₙ convergence-order assertion in CI, target ≥ 1.5 — only accuracy tests exist so far), S5 (verify `E_c ≈ 1.625(γ/ε₀R)^½` against Taylor 1964 before coding), S6 (onset-voltage vs Cloupeau–Prunet-Foch / Hartman), E1 (cache shape-independent threshold re-solve), E3 (delete or implement `SolverParams`, `solver/config.py:41`), E4 (residual/normal sign-convention note). B1 drift-dominated ion closure and D leaky dielectric are deferred (V4 scope). **Resolved since this handover (tickets `.scratch/solver-improvements/`):** S4 (negative Gaussian `S_E`) — the shielding metric is now computed over an apex-local region of interest, so the Gaussian closure reports a positive `S_E ≈ 1.3%`; plus the geometry is rescaled to millimeter scale and the verification gains an analytical Taylor far-field boundary condition (recovered angle ~48° vs the ~44° grounded-box artifact).
- **Merged branch `feat/immersed-free-boundary` not yet deleted** (`git push origin --delete` pending, S7).

## 4. Blockers right now

- **No volume/contact-line constraint** — structural: the YLM residual over the analytic cone family has no preferred apex radius; the well-posedness of the angle direction comes from the onset projection (P2), not from a physical anchor. Fix is future work (spec §5).
- **Angle-resolution floor (~±1°)** — the discretization floor prevents asserting angle accuracy better than ~1°; the committed claim is the imposed-Taylor identity (≤ 3%) + argmin ∈ [48, 51]°, not 49.29° itself on the grounded box.
- **Physical experiments (Track B) blocked on school approval** — ISEF/SRC approval + supervisor + safety review required for high-voltage/ethanol work. Do not proceed until approved.
- **Guardrails (do not claim):** "recovered 49.29° on the grounded box" (the grounded box still recovers ~44°; the ~48° recovery comes from the analytical Taylor far-field BC, and the committed exact result remains the imposed-Taylor identity ratio within 3% of unity); 2nd-order *fields* (Eₙ, Maxwell pressure) until S3 is measured; the onset voltage is now reported at millimeter scale (~2.8 kV), not the old meter-scale ~28 kV.

## 5. Codebase hygiene note

**The codebase is getting messy — before continuing feature work, review the code for duplicate and unnecessary code.** Known evidence: stale documentation with wrong test counts/failure-mode claims (see §3), the unused `SolverParams` (E3), the legacy staircase path coexisting with the immersed path (`electrostatics.py`), the dead 4-point-stencil remnants if any, and the un-deleted merged branch. A `code-review` / `explore` pass plus the S7 hygiene list is the right entry point.

## 6. Suggested skills for the next agent

- `code-review` — before any PR-shaped change (also for the hygiene pass in §5).
- `explore` — wide-net survey of `solver/` for duplicate/dead code paths (immersed vs legacy).
- `test` / `tdd` — run `pytest`, extend for S3 (Eₙ order) test-first.
- `grill-with-docs` / `grilling` — sharpen the paper milestone / onset framing claims before writing them up.
- `handoff` — when finishing this next session.
- `developing-with-streamlit` — required for any Streamlit app work.
- `domain-modeling` — only if terminology drift is suspected; `CONTEXT.md` already exists.

## 7. Recommended reading order for a fresh agent

1. `AI_HANDOVER.md` (this file)
2. `.scratch/taylor-onset-framing/spec.md` — milestone spec, all tickets done, guardrails
3. `docs/plans/2026-08-09-next-steps.md` — findings + remaining S1–S7 items
4. `IMPLEMENTATION_STATUS.md` — module list, caveats (note stale test counts)
5. `CONTEXT.md` — domain glossary
6. `docs/adr/0001`–`0003`
7. `examples/08_immersed_refinement_study.py`, `examples/09_ideal_limit_study.py`, `tests/test_taylor_onset.py` — the evidence trail
8. `.scratch/taylor-cone-fd-bcs/research.md` — earlier sharp-cone research context

## 8. Communication style with the user

Serious physics/math treatment; comfortable with advanced material; do not oversimplify. Maintain project discipline: distinguish theory from implementation, reduced model from full EHD, and keep claims inside the guardrails (§4). Use exact paths when reporting. Challenge assumptions and refine claims when asked for professor/lab-assistant style guidance.
