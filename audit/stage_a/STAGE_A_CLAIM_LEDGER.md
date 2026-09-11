# Stage A baseline claim ledger
Date: 2026-09-08
Status: inventory complete; no scientific source files changed in Stage A.

## Executive disposition
The repository contains a substantial reduced-order solver and numerical tests, but the paper currently mixes verified numerical implementation evidence with planned physical validation and an invalid synthetic image result. The paper is not ready for submission. The immediate blocking work is computational/documentary, not laboratory work.

## Claim classifications
| Location/claim | Classification | Evidence/status | Required action |
|---|---|---|---|
| Abstract: lightweight 2-D axisymmetric Python solver | Partially supported | Code modules exist; runtime/accessibility claims need clean reproducible benchmark | Verify package/run and retain only measured wording |
| Abstract: cubic-exact immersed operator | Partially supported | Tests/source suggest local polynomial checks; complete coupled-order evidence not yet traced | Separate local exactness from global convergence |
| Abstract: second-order convergence of immersed operator | Unsupported as currently phrased | Existing convergence script contains hard-coded data; complete source-to-output reproduction not established | Re-run from solver and state exact object/norm |
| Abstract: Taylor identity ratio within 1% | Partially supported | Result appears in paper/data; independent reproduction required | Run clean command and archive output |
| Abstract: 49.29° within 0.1° | Partially supported / circularity risk | Uses analytical Taylor far-field BC and exponent observable; not independent finite-geometry prediction | Label as ideal-limit consistency benchmark |
| Abstract: 43–46° finite grounded-box artifact | Unsupported until reproduced | Quantitative source/output trace not yet established | Reproduce and explain boundary artifact |
| Abstract: 2.9 kV ethanol-literature-range onset prediction | Unsupported/overclaim | Physical input source, exact model route and output trace need audit; onset terminology exceeds static model without dynamics | Remove from headline or narrow to model-defined balance estimate |
| Abstract: positive space-charge shielding metrics | Exploratory | Phenomenological closure exists; physical validation absent | Label exploratory and state closure assumptions |
| Abstract: passing automated test suite | Unverified | Repository currently has 71 test files/tests claimed, but clean run not yet established; packaging points to backend paths while code is under solver | Run in clean environment and report actual count |
| Section 08: synthetic pipeline will recover known geometry | Proposed | Plan text, but prior generated table bypassed extraction | Rebuild actual end-to-end held-out qualification |
| Section 08: stability selection and uncertainty method | Proposed | Method described, physical data absent | Validate implementation with unit/regression tests |
| Section 09: experimental results | Correctly planned/TBD | No physical data located | Retain as future work |
| Section 10: safety/compliance | Proposed | Documents contain approval gates, but also operational wording requiring host review | Supersede unsafe student operating instructions |
| Section 12: current codebase includes app, optimizer, tests and artifacts | Partially supported | Files exist; functionality and test status unverified | Verify by commands, not inventory alone |

## Demonstrated Stage A defects/risks

1. `experiments/methodology/generate_synthetic_validation.py` creates an image but sets extracted angle using random perturbation of the known angle; its table is not a pipeline measurement.
2. `solver/experimental/synthetic_validation.py` can return acceptance true for all-NaN error arrays in a forced-failure check.
3. Stable-frame behavior, angle sign, translated-profile behavior, Otsu component selection and blank calibration require repair/regression coverage (reproduced in prior audit; rerun in Stage C/F).
4. `pyproject.toml` points package/test configuration at `backend`, while the active package and tests are under `solver`; repository state shows extensive deletes/modifications from reorganization. This must be resolved before test-count claims.
5. The convergence generator contains literal data arrays and a generic grid-spacing formula; it is a plotting/reporting script, not by itself evidence that the solver produced the values.
6. Historical paper status documents claim completion more strongly than the current evidence ledger permits.

## What Stage A does not conclude

This inventory does not conclude that the governing Taylor-cone equations are wrong, that the entire solver is unusable, or that physical validation is unnecessary. It concludes only that evidence levels and provenance are mixed and must be separated before Stage B/C claims can be made.

## Stage A release checklist

- [x] Repository and paper file inventory
- [x] Baseline source snapshot and SHA-256 manifest at `audit/stage_a/baseline_manifest.json`
- [x] Baseline source archive at `audit/stage_a/baseline_sources.tar.gz`
- [x] Claim categories assigned to headline and methodology claims
- [x] Invalid synthetic-table provenance identified
- [x] Computational blockers separated from laboratory blockers
- [ ] Full clean-environment test run (Stage B)
- [ ] Equation-to-code audit (Stage C)
- [ ] Literature novelty matrix (later stage)
