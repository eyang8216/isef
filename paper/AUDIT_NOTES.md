# Paper audit notes — open items

Date: 2026-10-16
Scope: `paper/paper_submission/` (the compiled submission), the figures and data it cites,
and the solver code it describes. This file records what is **still to change**. It is a
working note for the project, not part of the submission: it lives in `paper/` and is not
`\input` by `paper/paper_submission/main.tex`.

Everything listed under *Verified* has been re-run against the code in this repository.
Everything under *Open* could not be reproduced from the repository, or is a presentational
decision that has not been taken yet.

---

## 1. Claims the repository cannot reproduce

These are the only places where the paper states numbers that no code or data in this
repository can produce. They are internally consistent and figure-consistent, but an
examiner who tries to regenerate them will not be able to.

### 1.1 The body-fitted finite-element comparison — decision needed

Affected locations:

| Location | Claim |
| --- | --- |
| `sections/06_numerical_results.tex` §6.3 | cross-method differences 0.024 % (potential), 0.226 % (vector field), 0.381 % (normal field), 0.817 % (Maxwell pressure), 1.071 %, 2.518 % |
| `figures/01_regular_poisson_fem.png` panel (a) | Q1 FEM convergence curve and its fitted orders ≈ 2.05 / 2.03 / 2.01 |
| `figures/03_fixed_cone_fd_fem.png` panels (a), (b) | FEM overlays and the percentage-difference curves |
| `sections/01_introduction.tex` | "compared against an independent body-fitted finite-element reference" |
| `sections/03_research_question.tex` | "within <1 % for interface pressures" |
| `sections/10_conclusion_future_work.tex` | same comparison described as verification |

Evidence that it is unregenerable here:

- No finite-element code exists anywhere in the repository. Searches for
  `finite element`, `finite-element`, `fenics`, `scikit-fem`, `Galerkin`, `basis function`,
  `P1 element` across `*.py`, `*.md`, `*.tex` return only the paper sections themselves and
  archived planning documents. The only `*.py` occurrences of `FEM` are prose inside
  `app/app_pages/01_overview.py` and `app/app_pages/02_solver.py`.
- The intended driver names (`fem_reference.py`, `fitted_fem.py`, `fixed_cone_validation.py`,
  `validation_campaign.py`) do not exist anywhere in the tree or in git history.
- `03_fixed_cone_fd_fem.png` was committed as a binary with no producing script.

What *is* reproducible is the immersed finite-difference side of §6.3 (the panel (b)
normal-field curve, 242 → 316 V/mm, and panel (c) Maxwell pressure, 0.26 → 0.44 Pa); a
probe script under `.scratch/figure-verification/` regenerates those.

Options: (a) leave as is — the text never claims the comparison was run in this repository;
(b) state explicitly in §6.3 that the FEM reference was produced by the external analysis
campaign and is reproduced here as a figure only; (c) obtain and commit the FEM source and
mesh so the comparison becomes reproducible.

### 1.2 Section 7 in full — decision needed

`sections/07_public_validation.tex` (lines 7–75), plus `figures/geometry.png`,
`experimental_photos.png`, `profiles_and_height.png`, `angle_comparison.png`,
`extraction_sensitivity.png`, `field_and_balance.png`.

The section digitises published ethanol cone-jet photographs from Yang et al. (2025) and
reports angle differences (mean 1.337°, RMS 1.468°), calibration (1.57068 µm/pixel) and a
sensitivity study. None of it is reproducible here:

- `results/experimental_data/{images,profiles,metadata,frozen_predictions}/` contain no data
  (only `.gitkeep` placeholders).
- No image files of any kind exist in the repository outside `.venv`.
- Every number quoted in §7 returns zero hits in `*.py`, `*.txt`, `*.md`, `*.json`, `*.csv`.
- There is no `run_validation.py` or equivalent driver.

The section already carries a *Scope* statement saying the images come from the published
literature. Options: (a) keep §7 as a literature consistency check and accept that it is not
regenerable; (b) commit the extracted contours and the reduced source images so that the
fitted numbers can be re-derived; (c) drop §7.

### 1.3 Figure 4's two window series and the 1.50× domain series

`figures/04_sensitivity_landscapes.png` plots ten series. Eight of them are expressible
through `solver/solver/app_backend.py`'s `ImmersedVerificationParams` and reproduce
(recovered angles 49.066°–49.251°). Two are not:

- the "25–55 % window" and "35–65 % window" entries — `ImmersedVerificationParams` hard-codes
  the flank window at 0.30–0.60 of the domain (`app_backend.py`);
- the "1.50× domain" entry — every reachable spelling of it raises
  `RuntimeError: immersed verification: all landscape candidates failed`.

The panel's plotted minima still span roughly 48–50°, which is what §6.4 quotes, so the
figure is not contradicted; it is simply not fully regenerable. Options: (a) leave the figure
and its caption as a campaign product; (b) extend `ImmersedVerificationParams` with a flank
window parameter and a working large-domain mode, then regenerate.

---

## 2. Presentational and imprecision items still in the text

1. **The synthetic noise labels are nominal.** `paper/paper_submission/data/synthetic_validation_results.txt`
   labels its rows 40/30/20/10 dB, but the generator's own
   `20 · log10(150 / σ)` gives 41.2 / 31.5 / 21.4 / 11.5 dB. Either relabel the figure and
   table with the computed values or state in the caption that the labels are nominal.
2. **`figures/01_regular_poisson_fem.png` and `03_fixed_cone_fd_fem.png` have no in-repo
   generator** (see §1.1). Every other campaign figure except `02`, `03` and `04` now does:
   `05_optimizer_multistart.png` is produced by
   `experiments/methodology/generate_multistart_figure.py`, and `06_synthetic_holdout.png` by
   `experiments/methodology/generate_synthetic_validation.py`. Consider writing generators for
   the remaining three so the whole figure set is reproducible from the repository.
3. **`figures/02_curved_boundary_refinement.png`** is reproducible via
   `solver/examples/08_immersed_refinement_study.py` but has no dedicated plotting script.
4. **`experiments/methodology/generate_figures.py`** regenerates `system_schematic` and
   `solver_flowchart` but writes `system_schematic.pdf|png`, `solver_flowchart.pdf|png` and
   `exponent_crossing.pdf|png`, none of which are cited. The cited flowchart is
   `solver_flowchart_revised.pdf`, which has no generator. Consolidate.

---

## 3. Submission-readiness decisions

1. **The blue tracked-changes markup still prints.** `paper/paper_submission/revision_style.tex`
   defines the `\rev{}` command, the `revision` environment and `\revisionfigure{}`, all of
   which render in `RevisionBlue` (RGB 0,70,190); `sections/05_solver_architecture.tex` also
   sets `\captionsetup{labelfont={color=RevisionBlue}, textfont={color=RevisionBlue}}`. The
   abstract, all of §6 and §7, and the conclusion currently print in blue. This was authorised
   deliberately ("keep the blue markup as-is"), but it is the one thing a reader will notice
   first. To finalise: replace `\rev{...}` with its argument, the `revision` environment with
   its body, `\revisionfigure` with `\includegraphics` + `\caption` + `\label`, and delete the
   `\captionsetup` and the `\input{revision_style}` line.
2. **The title's "…with Planned Experimental Validation" suffix — RESOLVED.** The merge from
   `paper-1` (see `paper/MERGE_PLAN.md`) retitled the paper *"Reliable Taylor-Cone Angle
   Identification through Power-Law Exponent Crossing"* and added hyperref `pdftitle`/`pdfauthor`
   metadata. The promised-but-absent experimental campaign is no longer implied by the title.
3. **No `LICENSE` file exists** even though the project has been described as open source.
   Either add a licence (the `LICENSE` question is unresolved) or avoid the phrase — the word
   "open-source" was already removed from `sections/01_introduction.tex`.
4. **Named hardware.** §5.3 states an Apple M4 with 16 GB. This is accurate for the machine
   that produced `data/timing_results.txt`, and the table's header records it, but naming
   consumer hardware in a paper is sometimes considered unnecessary. Consider moving it to
   the data file only.

---

## 4. Repository hygiene leftovers

1. **Four uncompiled section files still contain stale text** (they are not `\input` by
   `main.tex`, so they do not reach the PDF):
   - `sections/06_numerical_verification.tex` — says the local suite passes 82 tests (now 84)
     and that the synthetic table is withdrawn and its rerun failed at zero noise. That
     statement predates the harness repair and directly contradicts the now-correct §6.5.
     Either delete the file or rewrite it as an archive note.
   - `sections/07_experimental_methodology.tex` — re-declares
     `\label{sec:experimental-procedure}`, which `sections/07_public_validation.tex` already
     owns. If it is ever compiled again this becomes a duplicate-label error.
   - `sections/A_submission_checklist.tex` — a pre-submission to-do list.
   - `sections/B_reproducibility.tex` — stale local-environment notes including absolute paths
     (`/Users/a1/...`) from another machine.
   Consider moving all four to `archive/superseded_sections/`.
2. **Six unreferenced figures** remain in `paper/paper_submission/figures/`:
   `exponent_crossing.pdf`, `exponent_crossing.png`, `poisson_convergence.pdf`,
   `poisson_convergence.png`, `solver_flowchart.pdf`, `solver_flowchart.png`,
   `system_schematic.png`. All are products of `experiments/methodology/generate_figures.py`
   or `generate_convergence_plot.py`. Delete them or keep them as generator output and say so
   in `figures/README.md`.
3. **`requirements.txt`** is a `pip freeze` dump whose first non-comment line is
   `-e git+https://github.com/eyang8216/isef@1116b274…#egg=isef_taylor_cone_solver`, i.e. it
   pins the project to an unrelated fork/commit. The real dependency declaration is
   `pyproject.toml`. Replace with a short direct-dependency list or delete.
4. **Four stale app build logs**: `app/COMPLETE_SUMMARY.md`,
   `app/IMPLEMENTATION_SUMMARY.md`, `app/TESTING_CHECKLIST.md`, `app/VISUAL_COMPARISON.md`.
   They contain numerous `backend/…` paths from the pre-restructure layout and describe work
   as pending that is now done. Move to `archive/` or update.
5. **`CLAUDE.md` points at `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`,
   `docs/agents/domain.md` and `docs/adr/`**, none of which exist (the `docs/` directory was
   removed as a stale empty shell). The real agent skills live in `.agents/skills/`.
6. **`Taylor_Cone_Poster_Revised.pptx`** (7.2 MB) is superseded by
   `Taylor_Cone_Poster_Final.pptx` (9.3 MB).
7. **`solver/INVESTIGATION_LOG.md`** is a development log living inside the distributed
   package; move it to `archive/` or the repository root.
8. **Dated documents that still quote 82 tests**: `A_TO_J_PRELAB_COMPLETION_REPORT.md`,
   `audit/stage_d_final_report.md`, `paper/paper_submission/sections/06_numerical_verification.tex`.
   These are historical records; either leave them explicitly marked as dated or update the
   count.
9. **Two figures were previously never cited** from the text (`\label{fig:system-schematic}`,
   `\label{fig:solver-flowchart}`). Both now are.

---

## 5. Verified — reproduction index

Use these to re-confirm the numbers the paper reports.

| Paper claim | How to reproduce |
| --- | --- |
| Quartic manufactured Poisson: RMS `1.82e-3 → 4.45e-4 → 1.10e-4 → 2.73e-5`, orders `2.035 / 2.018 / 2.009` | `.venv/bin/python solver/examples/10_quartic_poisson_convergence.py` |
| Curved-boundary refinement: inter-level changes `10.334 / 4.264 / 2.549 V` (immersed) vs `25.731 / 7.107 / 11.267 V` (staircase) | `.venv/bin/python solver/examples/08_immersed_refinement_study.py` |
| Taylor half-angle `49.2900892921°` | `solver/solver/verification.py: taylor_cone_half_angle_deg()` |
| Exponent crossing `p = −1` within `49.07°–49.25°` across grid/cap/domain variants | `.scratch/figure-verification/check_crossing_band.py` |
| Refinement levels `49.14 / 49.20 / 49.23°` | `.scratch/figure-verification/check_monotone_taylor.py` |
| Multistart endpoints `40.199°–42.791°`, radii `0.0704–0.0887` model units, residual `0.01257–0.01333 Pa` | `experiments/methodology/generate_multistart_figure.py --rerun`, or `data/multistart_results.txt` |
| Synthetic round trip: max angle error `0.027°`, max nRMSE `0.62 %` over σ ≤ 4.0; `10.5 %` at 55°/10 dB | `experiments/methodology/generate_synthetic_validation.py`, or recompute from `data/synthetic_validation_results.txt` |
| Timing `O(N^0.99)`, `0.46 s` at 121×177 | `experiments/methodology/generate_timing_data.py`, or `data/timing_results.txt` |
| §7 arithmetic: mean `1.337°`, RMS `1.468°` | recomputed from the three quoted differences (1.970, 1.520, 0.520) |
| Table 1 module list | all 19 named modules exist (15 in `solver/solver/`, 4 in `solver/experimental/`) |
| §5 app description | `app/streamlit_app.py` four `st.Page` entries; `app/app_pages/03_verification.py` uses the Taylor far-field condition only |

Build and test:

```bash
cd paper/paper_submission && rm -f main.out && latexmk -pdf -interaction=nonstopmode main.tex
.venv/bin/python -m pytest -q          # 84 tests
```

`rm -f main.out` matters: a stale `main.out` makes `latexmk` abort with a runaway
bookmark argument. A single bare `pdflatex` pass also produces a broken PDF (empty contents,
`??` references, no bibliography) — always use `latexmk` (or run `pdflatex` enough times).
