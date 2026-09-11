# Taylor-cone model: complete proposed validation protocol
Protocol TC-VP-1.0 | 8 September 2026 | Laboratory-review issue
Ethan Yang, Elliot Dong and Curtis Lau | Independent Schools Foundation Academy, Hong Kong

## Status and authority
This is the complete proposed scientific protocol for laboratory outreach. It is not an electrical construction guide or permission to operate apparatus. Numerical criteria below are project design choices, not literature-derived safety limits or evidence that tests have passed. The students and supervisor must accept this version before calling it frozen. Execution requires a signed host-lab configuration record and approved local operating procedures. No hazardous operating values are supplied as universal defaults.

This protocol replaces the earlier lab brief as the proposed basis for discussion. It does not certify the existing software. The September audit reproduced invalid synthetic-table provenance, false-positive validation acceptance, angle and coordinate errors, and failed feature handling. The earlier synthetic table is not qualification evidence. Existing source files and historical results must be retained with a withdrawal notice, not silently overwritten. This document does not itself change those files.

## Research objective and claim boundary
The primary question is whether a reduced axisymmetric electrostatic–capillary calculation predicts a measured liquid-interface profile and fitted flank half-angle within predeclared practical tolerances at matched geometry and operating state. The target is a quasi-steady, approximately axisymmetric meniscus with no resolved jet or spray in the measurement region. Absence of a resolved jet does not prove zero emission; instrument resolution and any lab-approved current observation must be recorded. Cone-jet flow introduces physics beyond a static balance [1].

The study does not validate transient jets, breakup, emitted-current laws, plume dynamics or propulsion. Dynamic onset observations are exploratory and cannot rescue a failed primary comparison. A conical image or an angle near the classical benchmark alone is insufficient evidence. The model may fail applicability screening before any physical validation proceeds; that is a legitimate outcome.

## Deliverables and responsibilities
Students supply versioned solver and analysis code, qualification reports, frozen predictions, data schemas and the final comparison. The host principal investigator owns apparatus suitability and operating approval; qualified lab personnel own electrical, chemical, ventilation and emergency controls. A measurement lead owns calibration and image quality. An analysis custodian holds prediction files and the held-out image key until extraction is locked. One person may hold multiple roles, but separation and any limits to blinding must be disclosed.

The output package contains the signed protocol and configuration record, commissioning log, imaging qualification results, prediction manifest, all attempted-trial records, immutable raw recordings, extracted profiles, uncertainty simulations, exclusions, diagnostic overlays and a bounded conclusion. Negative and inconclusive outcomes are retained.

---PAGE---
# Scientific design and model matching
## Primary matrix
The proposed matrix has three electrode-spacing conditions, G1, G2 and G3, using the same nozzle, electrode shape, liquid batch and polarity. G2 is the lab-supported baseline; G1 and G3 are approved smaller and larger spacings. Five independently reinitialized runs are scheduled per condition, giving 15 primary attempts. Each of five blocks contains all three conditions in a randomized order generated with seed 260908. Blocks are distributed over at least two sessions. This is a pilot-scale design, not a formal power guarantee.

Only one target state per geometry is confirmatory. Commissioning identifies a feasible state using the same measurement-quality rules, without choosing conditions for favorable simulation agreement. Exact spacing, voltage, supply mode, fluid condition and reinitialization procedure are entered in the configuration record before primary acquisition. A continuous liquid feed cannot be called static merely because its nominal rate is low: the volume balance and observed shape drift must be documented. A lab-approved retained-volume configuration is preferred for the primary no-jet comparison when compatible with the solver. Otherwise the primary route requires explicit justification, or remains infeasible.

One additional approved session may replace attempts lost to documented acquisition faults, up to two attempts per condition. All attempts count in the report. Fewer than five valid independent runs at any condition prevents the full three-condition claim; exploratory summaries remain permissible. Frames are not independent runs. Safety stops never create an obligation to reach the target sample count.

## Solver readiness gate
Before primary work, document the exact physical boundary mapping: nozzle and extractor dimensions, real conductor surfaces and potentials, domain truncation, liquid attachment radius, contact-line assumption, liquid-volume or pressure closure and gravity treatment. Verify coordinate units and angle convention. State each measured, prescribed, fitted and omitted quantity. Omitted terms require a sensitivity or scale assessment; no claim of negligible flow, gravity or charge effects is accepted merely from the label “near onset.”

A solver using analytical Taylor far-field boundaries cannot be described as a matched finite-electrode prediction without a justified boundary mapping. A restricted cone-shape family cannot claim arbitrary meniscus-shape recovery. Its admissible shape domain and fit window must be declared before exposure to validation images.

For this protocol, choose and register one prediction route. Route A predicts the profile at independently measured applied voltage, with required attachment and volume/pressure constraints. Route B predicts a model-defined balance voltage and candidate profile; commissioning must establish a separately identifiable experimental state corresponding to that quantity. Route B is not relabeled a fixed-voltage response curve or dynamic onset prediction. If neither route is implemented and verified for the apparatus, physical data collection is characterization only, not model validation.

## Numerical qualification and prediction freeze
Require three successively refined grids at each geometry. Last-refinement changes must be below 0.25 degrees in fitted angle and 0.25% of reference cone length in profile RMSE; these are project budgets, not proof of an asymptotic order. Domain-size and apex-regularization sensitivities must also be quantified. Failure requires additional work, not an enlarged acceptance tolerance after data inspection.

Freeze code, environment, input distributions, shape constraints, boundary mapping and analysis rules before primary acquisition. Generate prediction distributions using independently measured apparatus inputs, never measured validation interface shapes. Save input/output hashes and timestamps with an independent custodian. A hash alone does not prove when a file existed. Permitted per-run input updates are limited to registered independently measured metadata, processed automatically before the profile-analysis key is released. Report any unavailable input as an uncertainty source.

---PAGE---
# Image-pipeline qualification
## Defect closure before qualification
Regression tests must demonstrate that all-error and all-NaN batches fail; constant valid videos select the required interval; 45-degree cones return positive 45-degree angles; translations and supported rotations preserve the result; dark objects, not image borders, are selected; and blank, clipped or uncalibratable inputs fail explicitly. Renderer and extraction axes must agree. Calibration cannot silently use arbitrary intensity peaks. Each expected failure must have a reason code; exceptions must never be converted into a successful acceptance result.

The full chain must operate on pixels: acquisition input, calibration, distortion correction where justified, interface selection, axis determination, coordinate transformation, fitting and comparison. True profile coordinates or angles cannot enter the extraction path. Separate truth files are available only to the evaluation code. Synthetic ground-truth pixel scale must not substitute for a calibration-recovery test.

## Synthetic design
Use analytic cones at 40, 45, 49.29, 55 and 60 degrees, three projected cone lengths of 100, 200 and 400 pixels, and rotations of −5, 0 and +5 degrees. The clean contrast is 150 grayscale levels on an 8-bit image. Test four degradation pairs (Gaussian blur sigma in pixels, intensity-noise standard deviation): (0,0), (0.5,1.5), (1,5), (2,15). These are test definitions, not claims about camera noise or SNR. Record clipping and noise placement.

For every angle/length/rotation/degradation cell, create ten independent subpixel offsets and noise realizations. This gives 1,800 held-out positive cases. A separate development set uses distinct seeds; the custodian retains the held-out manifest. Add 100 negative cases covering blank frames, cropped apexes, borders, two disconnected objects, asymmetric silhouettes, attached jets and inadequate calibration features. Include at least 60 additional nonconical/rounded profiles to test honest failure or “no conical flank” classification rather than forced angle output.

## Qualification thresholds
For each positive test cell in the intended operating envelope, require at least 9 of 10 successful extractions, absolute signed-mean angle bias at most 0.25 degrees, 95th-percentile absolute angle error at most 0.5 degrees, and 95th-percentile profile error at most 0.5% of true cone length. Report both successful-case errors and failure fractions; never drop failures from acceptance. Negative cases must never produce an accepted physical result. Nonconical cases must not be labeled conical simply because a line fit exists.

The intended envelope is declared before unblinding. If a stress cell outside it fails, report the restricted envelope rather than claiming universal robustness. If an in-envelope cell fails, revise on development data and create a new held-out set. Reuse of the same test set for tuning is development, not independent qualification.

## Physical optical qualification
Before energized work, image a traceably measured scale and an independently characterized cone-shaped target in the same object plane, optical path and field of view. Target uncertainty must enter the error budget. Repeat after repositioning and refocusing. Test all intended field positions; quantify distortion, axis tilt, image-depth sensitivity and motion-blur sensitivity. A calibrated-camera method may follow Zhang [2], but one printed target image does not itself establish dimensional traceability or a complete distortion model.

Require combined expanded optical angle uncertainty no greater than 0.5 degrees and profile uncertainty no greater than 0.5% of the registered reference length. Calibration drift before versus after a session must remain inside that budget. If unresolved, affected records are flagged and excluded from confirmatory analysis with their results still disclosed. Synthetic qualification alone does not establish physical measurement accuracy.

---PAGE---
# Acquisition, state classification and exclusions
## Commissioning, not validation
Commissioning establishes the attainable regime, reference cone length Lref for each condition, optical envelope, feasible recording settings, liquid supply/retention method and approved settling duration. It does not contribute primary comparison observations. A conical flank must be measurable over the declared window; if not, do not increase hazardous operating conditions merely to obtain a cone. Report infeasibility or seek a separately approved redesign.

Choose camera settings from resolution tests, not from a universal minimum frame rate. Require at least 200 pixels over the measured cone length and enough temporal resolution to resolve variations relevant to the stability decision. Compare two lab-feasible temporal sampling settings during commissioning; if unresolved rapid variation changes classification, do not classify the state as demonstrably quasi-steady. Exposure and projected motion must pass the optical error budget.

## Each primary attempt
The operator records condition and block IDs, date, supervisor, apparatus approval reference, fluid batch, calibration ID, nozzle/spacing measurements, operating metadata and raw-file destination. Lab personnel execute all energization, adjustments, de-energization and safe-access steps under the approved SOP. Students do not improvise electrical troubleshooting. Record continuously from the registered condition change through settling and the observation window.

Use the first ten seconds after the fixed commissioning-derived settling duration, not the best-looking interval. Divide the window into ten one-second bins and select the frame nearest each bin midpoint for profile extraction. Analyze the full recording for state classification. A missing selected frame is replaced only by the nearest timestamp within the same bin; record the replacement. Inability to populate every bin is an acquisition failure.

## Stability and axisymmetry rules
Within the ten-second window, require the 5th-to-95th percentile angle range to be at most 1 degree, apex axial range at most 1% of Lref, and first-half versus second-half mean apex displacement at most 0.5% of Lref. Require no resolved jet, spray, abrupt detachment or unresolved contour switching. Compare left and right profiles independently: their angle difference must be at most 1 degree and their common-grid profile RMSE at most 1% of Lref. These are registered measurement rules, not physical constants.

A failed stability window remains in the regime/failure summary. Do not wait for a later favorable interval within that attempt and replace the registered window. A run that cannot meet the primary scope may be retained as exploratory dynamic characterization. Any approved repeat follows the same reinitialization and replacement policy, not agreement-driven selection.

## State and failure codes
Record one state: undeformed/weakly deformed; nonconical stable meniscus; eligible quasi-steady conical meniscus; oscillatory/asymmetric; resolved cone-jet/spray; unclassifiable. “No resolved jet” is always qualified by spatial and temporal resolution.

Failure codes are SAFETY_STOP, CALIBRATION_FAIL, OUT_OF_ENVELOPE, FRAME_MISSING, SEGMENTATION_FAIL, AXISYMMETRY_FAIL, STABILITY_FAIL, MODEL_SCOPE_FAIL and METADATA_MISSING. Record the reason and evidence before prediction unblinding. Unexpected disagreement is never an exclusion reason. Have a second reviewer adjudicate ambiguous classifications using image data without prediction overlays.

## Optional onset record
Only if already included in the host-approved SOP, document transitions during permitted increasing/decreasing sweeps. Report the last condition without and first condition with each operationally defined state as a bracket. Keep sweep directions separate. Do not combine deformation and cone-jet thresholds, extrapolate below the voltage resolution or treat these observations as primary validation. No additional hazardous run is required by this protocol.

---PAGE---
# Locked measurement and analysis
## Coordinates and interface extraction
Use nozzle-referenced coordinates: z increases toward the extractor, the origin lies on the independently determined nozzle axis at the exit plane, and r is distance from that axis. Apply calibration and a registered rigid rotation before taking radial distances. Preserve signed lateral coordinates until left/right profiles are separated. Do not use a possibly rounded apex edge pixel as the symmetry axis. Maintain coordinates in millimetres throughout comparison; explicitly convert solver SI output.

Select the liquid component attached to the documented nozzle region; exclude nozzle metal, image borders and jet pixels. Save masks and overlays. Manual correction is not allowed for confirmatory output unless a separately preregistered blinded annotation method is selected before acquisition. Failed automated contours remain failures rather than hand-repaired successes.

## Flank convention and fitting
Let s = z_apex − z be axial distance back from the apex and L be measured nozzle-exit-to-apex length. Use s/L from 0.25 to 0.75, equivalently z in [z_apex − 0.75L, z_apex − 0.25L]. Fit each side using an errors-in-variables line fit with uncertainty derived from pixel-location tests. Half-angle is arctan(|dr/dz|), converted to degrees. Reject unresolved curvature inconsistent with the qualified conical-target residual envelope; do not let a high R-squared alone establish conical geometry.

Average side angles only after the asymmetry gate passes. Save a run-level average across the ten frames, with within-run variability reported separately. The five run means, not fifty frames or thousands of edge points, are the independent observations for condition-level repeatability. Uniform isotropic length scaling cancels from a slope angle; distortion and unequal axial/radial scale errors do not. Avoid double counting calibration in angle uncertainty.

## Profile metric
The primary comparison is over the common physical overlap of the experimental and predicted flank windows in nozzle-referenced coordinates. Register a 100-point uniform axial grid on that overlap. Require overlap at least 80% of each flank window; otherwise classify MODEL_SCOPE_FAIL or incomplete geometry rather than quietly shortening the comparison. Use shape-preserving linear interpolation without extrapolation. Preserve separately measured apex position, cone length and attachment radius; no primary radial translation or best-fit rotation may erase their discrepancy.

RMSE = sqrt(mean[(Rpred(z) − Rmeas(z))^2]); nRMSE = RMSE/Lref. Lref is fixed from commissioning, not chosen to reduce the reported error. Calculate the primary condition metric between the frozen predicted mean profile and the mean of independent run profiles, with run-level errors also reported. The same fitting convention must be applied to predicted profiles. Report apex and base diagnostic errors separately; apex alignment may be a labeled secondary shape-only diagnostic, never replace the primary comparison.

## Baseline and interpretation
The declared descriptive baseline is a straight cone of fixed 49.29-degree half-angle using the same independently registered attachment/reference convention, not fitted to validation data. Report its error beside the solver error. Better performance is descriptive unless its paired uncertainty supports the difference. Agreement with the baseline alone neither validates nor invalidates the solver, and baseline comparison does not replace the fixed practical-equivalence criteria.

---PAGE---
# Uncertainty, decisions and stopping
## Uncertainty calculation
Follow the measurement-model approach of JCGM guidance [3]. Estimate repeatability from independent runs. Include calibration, distortion, axis placement, contour bias, temporal sampling, alignment, target characterization, model-input uncertainty and numerical-discretization sensitivity. Shared calibration and fluid-property errors are shared draws across affected runs, not independently averaged away. Preserve spatial correlation along each contour.

Use 10,000 Monte Carlo draws with a saved seed and input-distribution manifest. Resample whole runs for repeatability, retaining frame grouping, and draw common systematic effects jointly. With only five runs per condition, compare the resulting angle interval with a small-sample t-based interval; use the wider interval if they disagree materially, and disclose sensitivity. Do not resample individual contour pixels as independent experimental trials. Repeat the calculation with another seed; endpoints should change by less than 10% of the stated decision margin, otherwise increase the draws.

The signed angle difference is prediction minus experimental mean. Obtain its central 95% uncertainty interval. Obtain a 95% uncertainty interval for the nonnegative condition profile nRMSE from the same joint realizations. These intervals characterize the registered propagation model, not proof of universal frequentist coverage. Qualification tests must assess interval behavior on known geometries, with coverage shortfalls disclosed and corrected before primary analysis.

## Practical-equivalence rule
The fixed project margins are 1 degree for absolute angle discrepancy and 2% of Lref for profile nRMSE. They are intended engineering-resolution targets, not literature standards. Qualification requires expanded measurement uncertainty at most 0.5 degrees and 0.5% of Lref, respectively. If the host cannot meet this budget, revise the protocol before primary data; do not widen margins after observing disagreement.

A condition is supported only when its entire 95% angle-difference interval lies within [−1,+1] degrees and the upper 95% bound of nRMSE is at most 0.02, with all qualification gates passed. A condition shows resolved discrepancy when the angle interval is entirely outside the equivalence band or the lower nRMSE bound exceeds 0.02. All other outcomes are inconclusive. A narrow interval containing zero is not required for practical equivalence; a wide interval crossing zero is not sufficient.

The overall claim requires support at all three registered conditions. This is an all-conditions decision, not selection of the best condition. Report each metric and failure rate even when the overall decision fails. Controlled-trend evidence requires the predicted and measured changes to be distinguishable from their uncertainties; if predicted differences are too small, report equivalence across tested conditions without claiming a resolved trend. Passing this pilot does not establish validity outside the tested regime.

## Amendments and stop decisions
Safety concerns stop work immediately under the lab SOP. Qualification failure stops confirmatory acquisition. Failure to obtain an eligible regime stops the primary route; it is not a reason for unapproved equipment or fluid changes. Missing run count, insufficient overlap or excessive uncertainty prevents a full support claim.

Every amendment records old/new text, rationale, date, approvers and whether any validation images or results were seen. After unblinding, corrective model or analysis changes are exploratory and require new held-out data for another confirmatory claim. There is no early stop for apparently favorable scientific results and no added sampling simply to obtain significance. Safety and lab resource limits always take precedence over completion.

---PAGE---
# Host-lab execution and safety record
## Required capabilities, not a shopping list
The proposed host provides a suitable existing electrically driven meniscus apparatus or a professionally reviewed alternative, a means of documenting actual operating voltage through approved instrumentation, controlled liquid handling, dimensional metrology, calibrated imaging and qualified supervision. The choice of voltage range, current limits, fluid identity, exposure protection and electrical instruments belongs to the host's approved risk assessment. This protocol specifies no student-built high-voltage circuitry, resistor tests or direct multimeter connections.

High voltage, stored electrical energy and hazardous liquids require separate review. Supply current limiting is not a non-lethality guarantee; stored energy and safe isolation must be addressed [4]. Ethanol is flammable [5]; its earlier inclusion is not a requirement to use it. No fluid—including a nonflammable alternative—is automatically safe or automatically compatible with the model. Current safety data sheets govern chemical-specific handling. An enclosure is not assumed to provide explosion protection.

## Signed authorization fields
Host institution: ____________________  Principal investigator: ____________________
Qualified apparatus operator: ____________________  Measurement lead: ____________________
School supervisor: ____________________  Analysis custodian: ____________________
Protocol version/hash: ____________________  Approval date: ____________________
Applicable SOP identifiers/revisions: ____________________
Applicable institutional and fair review/forms confirmed by supervisor: ____________________

Configuration ID: ____________________  Prediction route A/B: ____________________
Nozzle geometry/material and dimensional certificate: ____________________
Extractor geometry and G1/G2/G3 measured spacing with uncertainty: ____________________
Fluid identity, composition, batch, temperature and property sources: ____________________
Liquid retention/feed mode, volume/pressure constraint and reinitialization: ____________________
Approved operating setpoints and allowed envelope (SOP attachment): ____________________
Camera/lens/illumination and calibration/temporal-resolution record: ____________________
Settling duration and Lref for each geometry: ____________________
Solver/analysis/environment commit and prediction archive: ____________________

## Approval evidence and release gate
Attach signed apparatus schematics and manufacturer documentation reviewed by the lab, stored-energy and safe-access assessment, grounding/bonding assessment, interlock and emergency-stop acceptance records, chemical inventory and SDS review, ventilation/spill/waste assessment, approved operating and emergency SOPs, training records, supervision arrangements and required school/fair approvals. ISEF hazardous-activity rules require appropriate supervision and risk assessment; the supervisor must check the applicable competition-year and local requirements rather than assume this protocol supplies compliance [6].

The release decision is APPROVED FOR COMMISSIONING / APPROVED FOR PRIMARY ACQUISITION / NOT APPROVED. Primary release additionally requires imaging qualification, model-matching qualification, fixed execution settings, frozen predictions and an independent review of this record. Any blank safety-critical or scientific configuration field means NOT APPROVED. These fields capture laboratory-specific facts that cannot honestly be completed before a host is identified; they do not leave the scientific comparison undefined.

## Stop and emergency responsibility
Lab personnel apply the approved response to discharge, spill, ventilation loss, unexpected trip, damaged apparatus, missing supervision or uncertainty about safe access. Students stop participation and notify the operator; they do not approach, open, discharge or troubleshoot energized apparatus. Emergency contacts, evacuation arrangements and safe-access confirmation are those of the institution. This protocol intentionally does not substitute generic electrical handling instructions for a local SOP.

---PAGE---
# Records, review and laboratory request
## Required trial record
Each attempt records protocol/configuration/block/condition/run IDs; commissioning or primary label; timestamps; operator and supervisor; fluid and calibration IDs; measured nozzle/gap/voltage and available current metadata with uncertainty; fluid temperature and available environmental data; retention/feed state; settling and observation times; camera settings; raw filenames and hashes; state code; excluded-frame/replacement log; failures and safety events; and reviewer decision timestamp before unblinding.

The analysis record contains calibration transforms, signed contours, separate sides, axis estimate, apex/attachment positions, flank bounds, fit diagnostics, raw and processed overlays, run/condition summaries, common-grid coordinates, numerical input distributions, Monte Carlo seed, uncertainty intervals and decision. Use CSV for scalar tables, JSON for structured metadata and lossless or original camera files for raw images. Preserve original timestamps and avoid screenshots or recompressed social-media video.

## Directory and provenance convention
Store a study under experiments/validation/TC-VP-1.0/ with distinct commissioning, qualification, raw, metadata, predictions, analysis, reports and approvals subdirectories. Raw data are read-only after ingestion, with a second backed-up copy. Processed output never overwrites raw data. Every report records code commit, dependency versions, command, input hashes and output hashes. Access to student or staff contact details is restricted; public release follows lab permission. Lab ownership and publication permission are agreed before acquisition, not promised in exchange for access.

## Review sequence and realistic scheduling
The laboratory first reviews this full protocol and decides whether its apparatus can meet the target regime and measurement budget. Software defect closure and independent qualification can proceed off-site while the host reviews safety. Commissioning follows institutional approval. Primary collection follows a signed release meeting, not a calendar deadline. Analysis and reporting follow locked extraction and prediction unblinding. No fixed three-week promise is made before the host has assessed feasibility and staffing.

The immediate request is a technical review meeting, identification of a qualified host operator and an assessment of available apparatus, imaging, fluid-property measurements and supervision. The students bring the complete protocol and computational materials; they are not asking the lab to endorse previous unsupported validation claims. Any future one-page cover note must describe the pipeline as awaiting qualification until the release evidence exists.

## Independent review and publication checklist
Before primary release, a reviewer other than the main analysis author checks the failure-case tests, held-out provenance, angle sign and axis convention, trial independence, matching route, error budget and safety authorization record. Before publication, reconcile every numerical claim with a reproducible output, include all attempt counts and exclusions, disclose commissioning changes and post-hoc analyses, and remove the earlier illustrative synthetic table from evidentiary use. This protocol has been drafted and checked for internal consistency; it is not a completed independent scientific or institutional safety approval.

## References and evidence scope
[1] Fernandez de la Mora, J. (2007). The Fluid Dynamics of Taylor Cones. Annual Review of Fluid Mechanics 39, 217–243. DOI: 10.1146/annurev.fluid.39.050905.110159. Supports distinction between static geometry and cone-jet dynamics; does not prescribe this protocol's numerical margins.

[2] Zhang, Z. (2000). A flexible new technique for camera calibration. IEEE TPAMI 22, 1330–1334. DOI: 10.1109/34.888718. Microsoft Research primary publication record; supports planar-pattern camera calibration, not a universal error limit.

[3] JCGM 100:2008, Evaluation of measurement data—Guide to the expression of uncertainty in measurement; JCGM 101:2008, propagation using a Monte Carlo method. BIPM Guides in Metrology. Supports uncertainty-model principles; sample count and acceptance margins here are project choices.

[4] Lawrence Berkeley National Laboratory, Electrical Safety program and Cord and Plug guidance, accessed 8 September 2026. Institutional example concerning isolation and stored energy; host procedures remain controlling.

[5] CDC/NIOSH, Pocket Guide to Chemical Hazards: Ethyl alcohol, accessed 8 September 2026. Chemical hazard reference; obtain the actual supplier SDS for any selected fluid.

[6] Society for Science, ISEF International Rules: Hazardous Chemicals, Activities or Devices, accessed 8 September 2026. Supervisor must check the applicable year, school and affiliated-fair requirements before experimentation.

Local evidence reviewed in the preceding audit: solver/experimental/image_processing.py; profile_extraction.py; synthetic_validation.py; comparison.py; experiments/methodology/generate_synthetic_validation.py; paper/paper_submission/data/synthetic_validation_results.txt; paper Sections 7–8; experiments/design/experimental_validation_plan.tex. No new claim of repaired code or completed numerical tests is made by issuing this protocol.
