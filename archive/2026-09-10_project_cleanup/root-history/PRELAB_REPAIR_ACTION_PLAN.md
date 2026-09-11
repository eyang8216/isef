# Pre-laboratory paper and software repair plan
8 September 2026 | Proposed execution plan, not completed work

## Objective and stopping boundary
Deliver a reproducible, honestly scoped computational paper and laboratory-ready scientific package. Finish all work possible using code, mathematical analysis, synthetic data and accessible published benchmarks. Stop only at tasks requiring actual apparatus, traceable physical calibration, measured fluid/geometry inputs, approved operation or independent physical data. Do not describe pre-lab completion as physical validation or institutional safety approval.

Previous audit statements are leads to reproduce, not substitutes for a fresh equation/code/result trace. The earlier advancement probability estimates have no statistical basis and must not be used for planning. The prior protocol is a draft requiring review: its counts, uncertainty procedures, chosen margins and unresolved prediction routes are not automatically justified simply because they were written down.

## Work package A: baseline and evidence integrity
Read the full paper, bibliography, project instructions, actual solver, tests and plotting scripts. Inventory every equation and quantitative claim in a ledger: claim, assumptions, implementation location, producing command, raw output, figure/table, status. Preserve a snapshot and working branch; make no destructive cleanup or overwrite of historical data. Record interpreter and dependency versions.

Reproduce the reported synthetic-table provenance. Remove unsupported evidence and associated abstract/conclusion claims from the revised paper, retaining the original outputs with an explicit provenance notice. Correct unsafe descriptions in outreach materials and mark prior PDFs superseded. Verify authorship, test counts, timing, convergence and claimed apparatus readiness rather than copying prior summaries.

Completion gate: no retained empirical or numerical claim lacks a traceable result or a clear planned/illustrative label.

## Work package B: reproducible execution and regression protection
Repair imports, packaging, test discovery and output paths after the directory reorganization. Isolate generated results from source files. Define explicit dependencies including imaging and testing extras. Provide one documented command sequence for setup, tests, experiments and paper generation. Rerun the existing suite before algorithm changes where feasible, recording failures rather than treating an unavailable dependency as a pass.

Add regression tests for blank calibration, wrong component selection, sign/axis errors, translation, rotation, missing frames, all-NaN success, insufficient contours, nonmonotone coordinates and unsupported settings. Tests must assert intended numerical outputs and failures rather than only absence of exceptions.

Completion gate: a fresh environment reproduces the logged test results and all evidence-generating commands; known failures are fixed or their features removed from paper scope.

## Work package C: mathematically explicit model
Derive one normal-stress convention using a named outward normal, pressure jump, curvature sign and potential boundary conditions. Check a zero-field sphere and a conducting electrostatic reference. Distinguish local asymptotic Taylor balance from a globally closed finite meniscus problem. Specify pressure or volume closure, attachment/contact-line assumptions, actual versus idealized electrodes and permitted shape family.

Nondimensionalize with length L, voltage Vref and capillary pressure gamma/L. Define electric stress ratio epsilon Vref^2/(gamma L) with any factor of one-half stated explicitly, gravity ratio rho g L^2/gamma, and the pressure/volume constraints. State which input regimes could justify omitted physics, without claiming their experimental values are known.

For a fixed geometry in linear, charge-free electrostatics, derive the projected voltage-amplitude calculation as a constrained weighted least-squares problem. If residual is x a(q) minus b(q), x=V^2, positive weights W and a nonzero response, x*=max(0,(a^T W b)/(a^T W a)). Define reference-voltage units, whether b includes prescribed pressure, and behavior at bounds. Joint unknown pressure requires an explicit two-column fit and rank/conditioning analysis; projection is not automatically valid for nonlinear charge closures. Derive the reduced objective and explain that minimizing it over a restricted family is not proof of an exact free-boundary equilibrium.

Completion gate: equations, units, signs, constraints and implementation agree; the paper no longer equates a balance voltage with stability or cone-jet onset.

## Work package D: identifiability and noncircular verification
Inspect whether boundary data or the trial family encode the Taylor angle. Separate exact-solution verification from independent recovery of an unknown angle. Compute objective landscapes before and after voltage projection, curvature/sensitivity to angle and nuisance parameters, and rank/conditioning of local sensitivity matrices. Flat objectives cannot justify precise recovered angles. Do not tune fit windows to force 49.3 degrees.

Quantify angle changes under mesh refinement, domain enlargement, apex cutoff, boundary choice, sampling window and initial guess. Compare analytic versus numerical fields where possible; compare fixed versus projected amplitude. If the parameter is not identifiable, report non-identifiability or revise the estimator, rather than adding an arbitrary Taylor-angle regularizer.

Completion gate: supported accuracy claims include discretization and modeling sensitivity; otherwise replace point estimates with justified ranges or diagnostic-only conclusions.

## Work package E: hierarchical verification and benchmarks
Verify operators using manufactured solutions with axis regularity and curved boundaries. Verify field derivatives and curvature independently. Test the complete coupled residual on analytic reference geometries where valid. Use at least three, preferably four, systematically refined grids and report actual error norms and observed orders; do not assume local polynomial exactness proves global second order.

Add finite-domain and boundary-condition tests independent of the ideal Taylor condition. Benchmark the same boundary-value problem against an independent discretization or suitably reproducible published solution. Reference uncertainty and numerical convergence must be small enough for the comparison. Failure to obtain an independent reference limits claims; it cannot be hidden by comparing the solver with itself.

Build accuracy-versus-runtime curves on recorded hardware, including full solve costs, failed runs and memory where feasible. Compare against a transparent baseline at matched accuracy and conditions. Repeat timings without mixing warm starts, cache effects or different tolerances.

Completion gate: every claimed order, error and speedup comes from regenerable data and a clearly matched comparison.

## Work package F: imaging qualification without a lab
Repair the full image-to-coordinate-to-angle chain and qualification acceptance logic. Separate signed left/right contours, nozzle/axis estimation, calibration, rigid alignment, physical units and quality failure codes. Validate profile comparison and uncertainty code independently of image segmentation.

Use distinct development and held-out synthetic datasets. Ground-truth geometry is accessible to scoring, not extraction. Cover analytic cones, smooth nonconical profiles, rounded apexes, asymmetric and multi-object scenes, blank images, clipping, blur, contrast, pixel scale, camera rotation, subpixel offsets and temporal instabilities. Include calibration-target recovery, not merely a supplied true scale. Seed and version all generators. Count extraction failures in reported performance.

Review the protocol's proposed sample counts and coverage claims before declaring qualification. Cell-wise extreme-percentile assertions from ten cases are too weak for confident tail qualification; use appropriately sized tests and binomial uncertainty, or explicitly modest descriptive claims. Add synthetic recovery and coverage experiments for systematic plus random uncertainty. Passing synthetic tests cannot substitute for physical optical calibration.

Completion gate: real end-to-end held-out performance and failures are reported; no generated angle is presented as an extracted measurement.

## Work package G: novelty and contribution experiments
Build a primary-literature comparison matrix covering equilibrium solvers, boundary/finite elements, reduced models, cone-jet models and recent simplified methods. Record equations, closures, geometric restrictions, computational cost, verification and data availability. Numerical Taylor-cone modeling, reduced modeling and voltage scaling are not assumed new.

Test a focused candidate contribution: an inexpensive reduced electrostatic-capillary solver accompanied by quantified identifiability, truncation and error limits. An alternative strong result is demonstrating why an angle estimator becomes flat or biased after amplitude elimination and providing a verified diagnostic/correction. Treat both as hypotheses until experiments and prior-art checks support them.

Completion gate: one concrete contribution sentence survives the literature comparison and quantitative ablation/benchmark evidence; engineering accessibility is distinguished from a new mathematical method.

## Work package H: protocol reconciliation and paper rewrite
Choose the prediction route actually supported by the corrected model. Either freeze one primary route or explicitly separate scientifically distinct studies; do not leave a consequential A/B choice inside a supposedly final confirmatory protocol. Review profile overlap rules for selection bias, whether zero/noisy curvature is meaningfully conical, independent repetition, correlated calibration error and feasibility of no-jet quasi-steady states. Reassess proposed margins from measurement and scientific objectives before outcome inspection. Clarify all post-commissioning fields and version-control rules.

Rewrite title, abstract, model, methods, verification, results and limitations around demonstrated work. Label future experimental work as proposed. Verify each citation against the original source where accessible; remove placeholders and claims not supported by accessible evidence. Compile all plots and tables from frozen outputs. Produce a corrected paper PDF, reproducibility instructions, claim ledger, full lab-review protocol and genuine one-page outreach brief.

Completion gate: no contradiction between paper, code, data, protocol and outreach materials; no claim of experimental validation, stable operating regime or approved safety controls without evidence.

## Work package I: independent pre-lab release review
Have an independent reviewer reproduce the main results from a clean environment and inspect derivations, test independence, synthetic provenance, uncertainty, literature claims and manuscript wording. Where no independent reviewer/tool is available, label review as self-review and retain independent sign-off as pending. Visually inspect the compiled PDF and verify equations, units, axes, bibliography, layout and figure/table cross-references.

Release states are COMPLETE PRE-LAB, BLOCKED BY COMPUTATIONAL ISSUE, or WAITING FOR LAB. A failing numerical or software gate is not reclassified as waiting for a lab. Record unresolved limitations in the abstract/conclusion where material.

## What necessarily waits for the lab
Host-specific risk assessment and operational authorization; traceable physical imaging calibration; measured apparatus/fluid input distributions; feasibility of the intended regime; independent physical trials; and final model-data validation conclusions. All scaffolding, scripts, blank records and analysis dry runs can be completed beforehand. A clean negative physical result remains publishable evidence about scope; no future success is promised.

## Prior-art starting points
Publisher records checked on 8 September 2026 identify Basaran and Scriven's Axisymmetric shapes and stability of pendant and sessile drops in an electric field (1990), DOI 10.1016/0021-9797(90)90316-G, and Capillary Electrohydrostatics of Conducting Drops Hanging from a Nozzle in an Electric Field (1993), DOI 10.1006/jcis.1993.1482. These already address numerical equilibrium and stability; the latter uses hybrid boundary/finite elements for nozzle and electrode geometry. A 2026 Journal of Electric Propulsion paper titled A simplified numerical procedure for the characterization of an ionic liquid meniscus with evaporation is also directly relevant to any broad claim of a novel simplified solver (DOI 10.1007/s44205-026-00184-y). These are starting points for detailed comparison, not a completed novelty review.
