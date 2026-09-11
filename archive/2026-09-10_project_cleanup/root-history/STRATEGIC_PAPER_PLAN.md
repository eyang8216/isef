# Strategic paper plan: a lightweight Taylor-cone solver
## Execution roadmap through the pre-experiment stopping point
8 September 2026 | Planning document | No new implementation or validation is claimed

## 1. Project direction
The project remains a lightweight axisymmetric Taylor-cone solver. The purpose of this plan is to turn the existing implementation into a credible research contribution through mathematical clarity, reproducible numerical evidence and a precisely matched future experiment. It is not a plan to build a complete electrospray simulator.

The working research question is: How accurately and efficiently can a reduced electrostatic–capillary solver recover the quantities it actually represents, and how do geometry, numerical resolution and model assumptions limit those predictions?

The intended paper argument is that a simpler solver can be useful when its cost, accuracy and restrictions are quantified. This is a hypothesis to test, not a conclusion to impose. If the method does not outperform a baseline or cannot uniquely recover a parameter, we report that result and revise the contribution accordingly.

The primary success condition before experiments is a reproducible computational paper whose retained claims are supported. Physical validation, physical camera calibration and permission to operate apparatus remain explicitly pending. No speculative finalist probability or promise of an award is part of the strategy.

## 2. Research positioning and scope control
### Minimum defensible contribution
The minimum target is a verified implementation of a clearly defined reduced problem, with transparent accuracy–cost measurements and quantified limitations. Merely reproducing a known Taylor angle or having many unit tests is insufficient to establish a new research contribution. We must determine what the implementation enables or reveals beyond that benchmark.

### Preferred contribution
The preferred contribution is a useful combination of reduced computation and demonstrated reliability: a precise amplitude-reduction method, a transparent treatment of the interface, and evidence identifying where the resulting prediction is robust. Each component must be compared with prior work before being called novel.

A stronger mathematical result about parameter identifiability is worth pursuing only if it explains actual solver behavior. It should support the lightweight-solver paper, not displace it with an unrelated mathematical project.

### Excluded expansion
Full fluid dynamics, transient breakup, a general leaky-dielectric formulation and a predictive space-charge transport model are outside the core repair effort. An optional unfinished feature may be disabled, separated as exploratory or removed from manuscript claims rather than expanded into a second project. A polished interface is secondary to correct numerical results.

We will not call a restricted shape-family optimizer an unrestricted free-boundary solver. We will not call a projected stress-balance voltage an experimentally established cone-jet onset voltage. Exact terminology will follow the equations and code once reviewed.

## 3. Stage A — establish truth and repair provenance
### Work
Read the complete manuscript, bibliography, relevant solver modules, imaging modules, tests, example scripts and data-generation paths. The previous audit is a list of issues to reproduce; it is not a substitute for a new source-to-result check. Preserve the starting state and avoid destructive cleanup.

Create a claim ledger covering every substantive statement: the exact claim, manuscript location, producing equation or command, code version, raw output, uncertainty or sensitivity, and permitted wording. Use four states: supported, unsupported, exploratory and proposed. Verify test counts and execution status rather than repeating historical numbers.

Reproduce the synthetic-table provenance issue and replace unsupported image-accuracy claims in the revised paper with an explicit statement of incomplete qualification. Retain historical files in a clearly labeled provenance archive. Correct the unsafe assurances in the previous outreach brief and mark superseded PDFs as such; creating a new document alone does not withdraw an old one.

### Deliverables and release gate
Deliver a baseline audit, claim ledger and clean list of retained results. The gate passes when all current figures and numerical claims have known provenance, even if many are still classified as unsupported. No unsupported result is silently carried into the new manuscript.

## 4. Stage B — restore a reproducible computational baseline
### Work
Repair packaging, module imports, dependency declarations, test discovery and stale paths caused by repository moves. Establish one supported interpreter/environment and separate required solver dependencies from optional imaging and interface dependencies. Preserve existing tests before changing algorithms.

Run the available tests and record their actual outcomes. Classify failures as dependency/setup failures, incorrect tests, implementation defects or numerical-method limitations. Add regression coverage before fixing reproducible defects. Store logs and commands, not just a count of passing tests.

Provide commands for setup, tests, benchmark execution, figure generation and paper compilation. Use deterministic seeds where randomness is involved. Store generated outputs separately and give results a manifest containing code revision, settings and dependencies.

### Deliverables and release gate
Deliver an executable environment specification, regression suite and run manifest. The gate passes when a fresh environment can reproduce the baseline and all claimed functionality has an executable test. Unsupported features must be removed from claims or explicitly disabled; a failing numerical result is not a laboratory dependency.

## 5. Stage C — give the lightweight solver a mathematical contract
### Work
Write the actual problem before improving its presentation. Define the unknown interface representation, electric potential problem, conductor and outer boundaries, normal direction, curvature convention, pressure jump, attachment condition, and volume or pressure closure. State whether voltage is an input or an inferred balance quantity. Document all units and conversions.

Check the formulation on simple analytic cases that expose sign and normalization errors, including a zero-field capillary reference where applicable and a conducting electrostatic reference with known field. Distinguish the ideal Taylor asymptotic problem from a finite-nozzle problem. Boundary data encoding the analytical cone must not be used as independent evidence of physical angle prediction.

Nondimensionalize the governing equations using clearly defined length, potential and pressure scales. Identify the dimensionless input groups and the quantities the model omits. Scale estimates will describe hypothetical ranges until actual apparatus/fluid measurements exist; they will not be written as measured experimental justification.

Derive voltage-amplitude elimination only under its valid linear-electrostatics assumptions. For a weighted residual xa(q) − b(q), with x = V², derive the nonnegative least-squares solution, its dimensional interpretation and degeneracies. Explain how an unknown pressure alters the fit and its rank. Confirm that the implementation uses the derived objective. Do not extend linear scaling automatically to nonlinear charge closures.

### Deliverables and release gate
Deliver a theory section plus derivation appendix and equation-to-code map. The gate passes when the problem is closed within its declared approximation, implementation and notation agree, and terms such as equilibrium, onset and prediction have operational definitions. If closure is missing, resolve it or narrow the model before proceeding to physical claims.

## 6. Stage D — verify the complete reduced calculation
### Verification hierarchy
Operator tests establish individual derivative and stencil behavior. Field tests establish the solution and gradient accuracy on fixed geometry. Geometry tests establish normals and curvature. Coupled tests establish the assembled stress residual. Optimization tests establish the reported shape or amplitude. Each level needs evidence; passing the first level cannot stand in for the last.

### Computational campaigns
Campaign D1 tests smooth manufactured fields, axis regularity and curved-boundary behavior. Use at least three systematically refined meshes, preferably four where cost allows. Report measured error norms and observed rates, not a presumed second-order label.

Campaign D2 tests the exact Taylor limit as a consistency benchmark. Explicitly disclose analytical boundary information and shape assumptions. Distinguish evaluating the correct field on a known cone from independently determining an unknown angle.

Campaign D3 changes outer-domain size, apex cutoff and sampling window independently. Show whether reported angle, voltage and residual stabilize. If the singular apex prevents a claimed order, explain the restricted norm or regularization rather than concealing it.

Campaign D4 tests a matched finite-domain problem using an independent implementation or an accessible, reproducible reference. Agree boundary conditions, geometry, normalization and error budgets before comparing values. Merely running the same algorithm at a finer grid is a refinement reference, not a fully independent verification.

Campaign D5 tests repeated initial guesses and parameter bounds. Identify convergence failures, boundary minima, flat objectives and dependence on optimizer settings. Save failures as well as successful cases.

### Deliverables and release gate
Deliver verification tables, convergence plots, diagnostic residual fields and a failure summary. The gate passes when each retained claim is supported at its actual level and sensitivity is smaller than the stated precision. If evidence supports only a restricted idealized problem, that becomes the scope of the computational paper.

## 7. Stage E — demonstrate why “lightweight” matters
### Work
Define lightweight quantitatively rather than rhetorically: runtime, memory or implementation burden at a stated accuracy, on recorded hardware. Separate field-solve time, optimization time and total workflow cost. Record problem size, tolerances, warm starts, thread configuration and repeated-run variability.

Choose a transparent baseline solving the same mathematical problem. Compare at matched error or report the full accuracy–cost frontier. A faster run with a looser tolerance is not a demonstrated algorithmic advantage. If a high-fidelity code is inaccessible, use an available matched baseline and narrow the comparison rather than inventing a speedup claim.

Run ablations that isolate contribution: fixed versus projected amplitude, relevant interface-treatment alternatives, and coarse versus richer shape representation where already implementable. Do not expand to many methods just to make the paper appear broad. Prioritize comparisons that answer why the chosen simplification is useful.

### Deliverables and release gate
Deliver an accuracy–cost figure, an ablation table and a precise lightweight claim. If no advantage is demonstrated, describe the code as compact or accessible and present the actual performance without asserting superiority. The project may remain valuable, but its research claim must reflect that outcome.

## 8. Stage F — strengthen the math where the data justify it
### Identifiability study
Evaluate the shape objective before and after amplitude projection. Plot its dependence on the candidate angle and any active shape parameters. Calculate local sensitivities and check conditioning with respect to pressure, voltage and boundary parameters. Perturb the inputs within controlled synthetic uncertainty and observe whether the recovered solution changes materially.

A sharp optimizer output is not automatically a precise physical estimate. If the objective is flat, investigate whether this is an expected property of the ideal problem, a consequence of projection, an implementation defect or insufficient observables. Do not force the Taylor angle with a prior and then call it independently recovered.

### Priority boundary
Required mathematics comprises consistent derivations, nondimensionalization, projection assumptions and sensitivity analysis. Optional work comprises an analytic conditioning result or reduced-objective derivative if it directly improves the solver. A full existence/uniqueness theorem, general stability theory or broad nonlinear transport extension is not required for this paper.

### Deliverables and release gate
Deliver a mathematically supported interpretation of what the estimator can determine. A negative identifiability result can become a contribution if independently checked and clearly distinguished from a coding failure. The final paper should present either a robust estimator with demonstrated limits or an honest restricted diagnostic—not a falsely precise predictor.

## 9. Stage G — qualify image analysis without physical experiments
### Work
Repair the previously reported failures with regression tests: all-error success, stable-frame selection, angle sign, coordinate-origin sensitivity, background/border segmentation and blank calibration. Confirm the full coordinate convention between rendering, extraction and solver comparison.

Use the real chain from image pixels to calibration, mask, component, axis, separate signed contours, physical profile and fitted angle. Truth coordinates must never enter the extraction path. Keep development and held-out sets separate, with versioned generators and seed manifests.

Test noise, blur, subpixel shifts, rotations, finite resolution, clipped apexes, multiple components, asymmetric and nonconical interfaces, blank calibration targets and temporal variation. Count invalid extraction attempts and test explicit rejection. Test comparison and uncertainty routines on known profiles independently of image segmentation.

Review the protocol’s numerical qualification margins and sample counts before treating them as final. Use suitable sample sizes or explicitly modest uncertainty statements for tail errors and failure rates. Validate uncertainty propagation with simulated correlated systematic errors; do not treat edge pixels or adjacent frames as independent trials.

### Deliverables and release gate
Deliver actual held-out image-to-measurement results, code, failure galleries and uncertainty diagnostics. The gate passes when the declared synthetic operating envelope is supported. Physical optical qualification remains pending; synthetic accuracy never becomes a claim of calibrated experimental accuracy.

## 10. Stage H — establish novelty with a focused literature review
### Work
Read primary sources on static conducting menisci, finite-nozzle equilibria, reduced numerical methods and related amplitude/shape reductions. Compare equations, closures, admissible geometry, computational methods, numerical evidence, cost and physical validation. Separate unavailable source content from verified facts.

Create a contribution matrix identifying what is inherited, implemented independently, modified and newly demonstrated. Test the prospective contribution against the strongest relevant prior work, not only broad review articles. Numerical cone modeling, a Python interface and the classical angle are not automatically innovations.

### Deliverables and release gate
Deliver a literature comparison table and one evidence-backed contribution paragraph. If novelty is incremental, say so and make the empirical contribution precise. Do not reposition every limitation as a breakthrough. A full prior-art judgment remains provisional until this review is performed.

## 11. Stage I — rewrite the paper around the evidence
### Working title and narrative
Use a provisional title such as “A lightweight axisymmetric Taylor-cone solver: numerical verification, efficiency and limits.” Do not put experimentally validated or predictive onset in the title without the corresponding evidence.

The introduction should define a narrow practical/computational need and explain why reduced complexity is worth testing. The model section should define the mathematical contract and omissions. The methods should explain the solver and amplitude reduction. The results should lead with verification and then show efficiency, sensitivity and failure cases. Synthetic measurement qualification belongs in a clearly separate section. The proposed experiment should not appear as completed results.

The discussion should answer what the method does well, where it fails, what remains unidentifiable and what physical observation would challenge it. The conclusion must be no stronger than the supported results. The abstract should be written last from the final claim ledger.

### Proposed figure set
The main paper should prioritize a geometry/boundary schematic, hierarchical convergence results, an objective/identifiability plot, a matched accuracy–cost plot, a sensitivity summary and an independent-reference comparison. A synthetic image-to-profile example and failure summary can move to the supplement if they interrupt the solver narrative. Every figure should answer a research question, not merely display a simulation.

### Supplement
Place longer derivations, exact experiment configurations, additional convergence plots, complete failure counts, environment details and synthetic qualification evidence in the supplement. Do not hide a limitation essential to interpreting the headline result there.

### Deliverables and release gate
Deliver the revised source and compiled PDF, supplementary material and machine-generated tables/figures. Check references against primary sources, units, uncertainty notation, figure labels and claim consistency. No manually typed numerical table should diverge from its raw data source.

## 12. Stage J — finalize the laboratory-facing package
### Work
Reconcile the full proposed validation protocol with the solver that actually survives verification. Select a coherent primary prediction route; do not leave a fundamental scientific choice unresolved under the label “frozen.” Exact host-specific equipment and operating details may remain approval fields, but their effect on model matching must be explicit.

Dry-run the proposed analysis on synthetic trial records with independent runs, shared calibration effects, missing metadata and exclusions. Confirm that the planned observable can discriminate the model from the baseline at the anticipated measurement budget. If not, redesign the comparison before approaching physical collection.

Prepare the final protocol, a one-page lab request, a concise capability/constraint sheet and blank trial/configuration records. Request a supervised feasibility and execution review, not endorsement of a supposedly validated apparatus. Safety-critical operating procedures remain controlled by qualified host personnel.

### Deliverables and release gate
The outreach package describes what is completed, what is untested and exactly what the lab is needed for. It contains no universal high-voltage safety assurance, invented apparatus performance or guaranteed project timeline. The lab should not need to infer the research question or invent the analysis method.

## 13. Execution order and decision points
The critical path is baseline integrity, reproducible execution, mathematical contract, complete numerical verification, evidence-backed contribution and manuscript rewrite. Imaging qualification can proceed in parallel after environment repair, but its results must not be used to substitute for solver verification. Literature review can proceed alongside the mathematical work and must inform the final novelty language.

After the contract review, decide whether the current code supports finite-geometry predictions or only the idealized cone family. After verification, decide whether claimed accuracy and efficiency survive. After identifiability analysis, decide whether an angle/voltage estimate is defensible or must be narrowed. After synthetic qualification, decide which measurement envelope is realistically supportable. Each decision can reduce scope; none automatically requires expanding the physics.

If repeated tuning cannot rescue a central result without changing the research question, pause and present a decision memo rather than silently rewriting the project. Bound exploratory work by relevance to the contribution and available computational resources. Do not promise completion dates until the baseline reveals the actual failure burden.

## 14. Working method and checkpoints
At each checkpoint, report what changed, which command or derivation supports it, what failed, what conclusions changed and what remains. Keep tests and result manifests with code revisions. Separate algorithm changes from manuscript changes so results can be traced. Preserve prior outputs without letting stale figures enter the final build.

The assistant can implement, test, derive, compare, draft and automate within available tools. The students must review the research direction and understand each change. They must not claim personal experimental or analytical work they did not perform. Qualified mentors review physical assumptions where appropriate, and the host alone approves hazardous operation.

Independent reproduction is desirable before final release. If an independent reviewer is unavailable, disclose self-review rather than labeling it independent. A successful build is not a scientific audit, and a self-review is not institutional safety approval.

## 15. The exact stopping boundary
We stop because a laboratory is required only when the remaining question depends on physical metrology or an actual approved apparatus. These dependencies are host safety approval, optical calibration in the real imaging geometry, measured liquid and electrode properties, establishment of a stable eligible state, independent physical trials and model-data validation.

We do not stop for broken imports, incomplete synthetic tests, unsupported math, missing numerical convergence, unverified citations, inconsistent definitions, unreliable uncertainty code or unfinished documentation. Those remain our responsibility before declaring the pre-experiment phase complete.

The final release state must be explicit: PRE-LAB COMPLETE; COMPUTATIONAL WORK STILL BLOCKED; or SCOPE REDUCED WITH LIMITATIONS. PRE-LAB COMPLETE means every retained computational claim is reproducible, all historical unsupported evidence is withdrawn from use, the contribution is honestly positioned and the physical study is ready for host review. It does not mean the solver has been physically validated.

## 16. Strategic end product
The strongest desired pre-lab paper tells a concise story: this is the reduced problem; this is why the implementation is inexpensive; this is the evidence that it solves that problem correctly; these are its numerical and modeling limits; and this is the independent physical test that remains.

If the evidence supports that story, retain the original lightweight-solver identity and present it confidently within those limits. If it supports only a narrower result, publish that narrower result honestly. The strategy is to earn a strong claim through evidence, not to decide the claim first and make the experiments fit it.

## Basis of this plan
This roadmap synthesizes the stated project goal and issues discussed in this conversation. It is not a new code audit, literature review, mathematical proof or competition assessment. Previously reported defects must be reproduced during Stage A. Detailed safety, scientific and novelty judgments must be checked against the actual implementation and primary sources during execution.
