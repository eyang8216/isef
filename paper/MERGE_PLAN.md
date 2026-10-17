# Merge plan: `paper-1/` → `paper/paper_submission/`

Status: **executed**. This file records the comparison, the reasoning, and what was
actually changed. It is deliberately outside `paper_submission/` so it is never `\input`.

---

## 1. What `paper-1/` is

`paper-1/` held 52 files and a 36-page `main.pdf`. Its `sections/04_theoretical_model.tex`
was **byte-identical to commit `2bea37f`**, the commit that ported the external revision.
`paper-1` therefore forked from the repository immediately after that port and never received
`bdc0fc5`, `c50c4c4`, `2dc2700` or `097a0ed`.

That is the key fact for the merge: `paper-1` is not "a newer version of the paper". It is a
fork with a **new front half grafted onto an old body**. Its new material is confined to the
title, abstract, §1, §2, §3, two framing sentences in §5 and §6, and six references. Every
correction made during the audit is absent from it.

## 2. New in `paper-1` (merged)

| File | New material |
| --- | --- |
| `main.tex` | Title → *Reliable Taylor-Cone Angle Identification through Power-Law Exponent Crossing*; hyperref `pdftitle`/`pdfauthor` |
| `sections/00_abstract.tex` | Rewritten around diagnostic reliability rather than solver cost |
| `sections/01_introduction.tex` | Four new paragraphs — COMSOL objective selection, "observable selection" statement of the study, electrospinning process control, ST7 thruster case — plus a restructured contribution list |
| `sections/02_literature_review.tex` | Reframed closing sentence |
| `sections/03_research_question.tex` | Sharper research question and matching hypothesis and scope |
| `sections/05_solver_architecture.tex` | One sentence in §5.4 |
| `sections/06_numerical_results.tex` | One sentence in §6.4 |
| `references.bib` | Six new entries |

## 3. Old in `paper-1` (not merged)

All of the following were present in `paper-1` and are regressions already fixed on `main`:

- **§4** — unweighted `1/N` residual RMS and `Δp`; the fictional `J = R_RMS + λP` objective;
  "The first model…" though no second model exists; "used by the code"; a to-do imperative
  ("their effect should be checked by moving the boundary outward").
- **§5** — the nine non-existent campaign modules (`validation_campaign.py`, `fem_reference.py`,
  `fitted_fem.py`, `fixed_cone_validation.py`, `run_validation.py`, …); `O(N^{2.3})` and
  "13 seconds on the recorded 2020 MacBook Pro"; "The app has two tabs";
  `verification.py & Immersed verification workflows`.
- **§6** — "108 analytic cone silhouettes"; max errors `0.299°` / `1.406 %`; crossing band
  `49.067°–49.176°`; residual minimum `48.0°–50.0°`; apex radius quoted in metres;
  "$h$ is radial spacing"; the Provenance block.
- **§7** — Scope hedge deleted; "consistency check" hedge deleted; the table's Source/status
  column deleted; `|Δα| = 0.522`; "Tip radius; local cell size & 6; 4 µm";
  trailing `\addtocounter{equation}{2}`.
- **§8/§9** resurrected (the two sections that were deliberately removed) and **§10–§12 not
  renumbered**.
- **`main.tex`** — the `\todo`/`\tbd` macros, "% bm package removed due to network issues",
  `\appendix` plus the A/B inputs, `\date{October 6, 2026}`, "Elliot Dong", no `siunitx`,
  no `\emergencystretch`, `\input{references_revision}` instead of BibTeX.
- **`references_revision.tex`** — re-introduces the fabricated `wasserman2011waterethanol`
  entry and the misattributed `karimi2019curved` ("M. Karimi et al."; the real authors are
  Naderi, Shams and Ghassemi).

Figures `01`–`04` and all twelve campaign/§7 PNGs were byte-identical between the two trees.
`05_optimizer_multistart.png` and `06_synthetic_holdout.png` differed: the current files are
the ones regenerated from the solver, so they were kept.

One file was merged in addition to the text: `paper-1/figures/solver_flowchart_revised.pdf`
is the vector original of the flowchart that `paper/paper_submission/` only had as a 1960×1472
PNG. The PDF was copied across and `sections/05_solver_architecture.tex` now includes it
instead of the raster version, which shrinks `main.pdf` and sharpens the figure; the PNG was
then deleted.

## 4. Recipe

1. **Adopt the reframing as the thesis.** The observable comparison is the one headline result
   the repository fully reproduces; "lightweight solver" is the weaker claim and its title
   promised an experimental campaign that does not exist.
2. **Bibliography first**, so the build stays green throughout. Add all six keys to
   `references.bib` — three existed only in `paper-1/references.bib` and three only in
   `paper-1/references_revision.tex`, so copying §1 across with only the former would have
   produced three undefined citations. Keep BibTeX; do not adopt `\input{references_revision}`.
   Use `note = {\url{…}}` for the two COMSOL entries because `unsrt` does not print `url`.
3. **Title and metadata.** New title; `pdftitle`/`pdfauthor` with the corrected author names;
   keep `\date{\today}`, `siunitx` and `\emergencystretch`.
4. **Abstract** from `paper-1`'s, with the audit hedges re-applied and the exponent claim
   scoped to the Taylor far-field condition.
5. **§1** from `paper-1`'s structure, with four mandatory edits: the numbers `49.067°–49.176°`
   → `49.07°–49.25°` and `48.0°–50.0°` → `roughly 47.5°–50°`; verbs "Discovery" → "We show"
   and "Development of" → "We evaluate" (the `p = −1` criterion is a known scaling identity,
   not a new method); `$49.3^\circ$` → `\SI{49.3}{\degree}`; and contribution 3 hedged to
   "exercised on twelve synthetic silhouettes … applied as a consistency check".
6. **§2** — closing contribution sentence only.
7. **§3** — `paper-1`'s research question and hypothesis, merged with the existing scope
   paragraph.
8. **§5.4 and §6.4** — add `paper-1`'s two sentences verbatim; they agree with the corrected
   numbers.
9. **§10** — rewritten to the new thesis.
10. **Do not touch** §4, §5.1–5.3, §6.1–6.5, §7.

## 5. Verification performed

- `rm -f main.out && latexmk -pdf -interaction=nonstopmode main.tex` → exit 0, 0 errors,
  0 undefined references, 29 pages, 14 bibliography entries.
- PDF text swept for the retired numbers (`49.067`, `49.176`, `48.0`, `50.0`, `108`,
  `0.299`, `1.406`, `13 seconds`, `2.3`) → no matches.
- Title page confirmed: new title, `Ethan Yang, Li Ang Dong, Curtis Wai Ip Lau`,
  `Independent Schools Foundation Academy`, `\today`.
- `pytest -q` → 84 passed.

## 6. Two items still open

1. **The ST7 paragraph.** `anderson2018st7` is a real paper about the right hardware, but the
   specific claims in `paper-1`'s draft — CMNT#4 becoming inoperable after an electrical short
   attributed to a suspected propellant bridge, and the loss of rotational control authority
   about one axis — are not in the abstract reachable at
   <https://journals.aps.org/prd/abstract/10.1103/PhysRevD.98.102005>, which reports thrust
   performance and differential acceleration noise. The merged paragraph was therefore
   **softened** to what the abstract supports ("propellant reaching the extractor forced the
   thrusters to operate in a degraded configuration"). Check against the full text before
   submission if the specific detail is wanted back.
2. **Scope of the headline claim.** "The crossing is the more reliable diagnostic" holds only
   under the imposed Taylor far-field condition. With a grounded outer boundary the fitted
   exponent runs from about −0.75 to −0.63 and never reaches −1, so no crossing exists. The
   abstract, §1 and §10 now state this explicitly rather than leaving the claim unconditional.

## 7. Reference verification

All six new entries were checked against Crossref:

| Key | Verified metadata |
| --- | --- |
| `comsolglobalobjective` | COMSOL 6.3 Optimization Module documentation, HTTP 200 |
| `comsolparameterestimation` | COMSOL 6.3 Optimization Module documentation, HTTP 200 |
| `zhou2019relationships` | 10.3390/nano9060843 — Zhou, Shi, Wan, Fang, Yu, Chen, Liu, *Nanomaterials* 9:843, 2019 |
| `lunni2020monitoring` | 10.1038/s41598-020-73252-4 — Lunni et al., *Sci Rep* 10:16341, 2020 |
| `lyne2021thruster` | 10.2514/6.2021-3439 — Lyne, Rovey, Berg, AIAA 2021-3439 |
| `anderson2018st7` | 10.1103/PhysRevD.98.102005 — Anderson et al., *Phys. Rev. D* 98:102005, 2018 |
