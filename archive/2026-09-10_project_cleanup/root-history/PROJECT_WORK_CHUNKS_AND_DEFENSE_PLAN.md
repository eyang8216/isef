# Project Work Chunks: Current State to Presentable Paper

## Operating principle

The project remains a lightweight axisymmetric Taylor-cone solver. We will work in sequential chunks, each producing a reviewable deliverable and a defense package. No chunk is complete merely because code runs or prose exists: it must have evidence, limitations, reproducible commands, and an explanation the student team can defend.

The pre-lab endpoint is a presentable computational paper and a lab-ready validation package. Physical camera calibration, approved apparatus operation, measured fluid/electrode properties, and experimental validation remain later gates.

## Chunk 0 — Project freeze and evidence inventory

**Purpose:** Establish the current state before changing it.

**Work:** Preserve the current repository and generated outputs. Read the complete manuscript, solver, tests, image pipeline, experiment documents, figures, scripts and bibliography. Build a claim ledger recording every equation, number, figure, table and conclusion with its source, command, assumptions and status.

**Deliverables:** Baseline snapshot; repository map; claim ledger; list of unsupported or misleading claims; list of stale paths and duplicate outputs.

**Completion gate:** Every important paper claim is classified as supported, unsupported, exploratory or proposed.

**Defense preparation:** Prepare a two-minute project summary and a “what changed during the audit” explanation. Be able to distinguish a current result from a historical result.

## Chunk 1 — Reproducible environment and repository repair

**Purpose:** Make the project runnable by someone other than the author.

**Work:** Repair packaging, imports, test discovery, dependency declarations and paths after reorganization. Separate source data from generated outputs. Document the supported Python environment and exact commands. Run the baseline test suite and record actual pass/fail results.

**Deliverables:** Environment instructions; clean test command; run manifest; regression-test plan; honest baseline test report.

**Completion gate:** A clean environment can reproduce the recorded baseline, or every remaining failure has a named owner and is excluded from claims.

**Defense preparation:** Explain why reproducibility matters, what a unit test proves, what it does not prove, and why a test count is not the same as model validation.

## Chunk 2 — Mathematical problem definition

**Purpose:** State exactly what the lightweight solver solves.

**Work:** Reconcile coordinates, normals, curvature sign, pressure jump, electric boundary conditions, conductor assumptions, outer boundaries, attachment/contact-line condition, volume or pressure closure, gravity treatment and units. Separate the ideal Taylor asymptotic result from the finite-domain numerical problem. Define the admissible interface family and whether voltage is prescribed or inferred.

**Deliverables:** Equation-to-code map; corrected theory section; notation table; assumptions and omissions table; dimensionless formulation.

**Completion gate:** The equations, implementation and manuscript use the same signs, units, boundaries and unknowns.

**Defense preparation:** Practice deriving the electric field from potential, explaining Maxwell stress and curvature, explaining why the classical half-angle is approximately 49.3 degrees, and naming every important approximation.

## Chunk 3 — Solver implementation repair

**Purpose:** Ensure the code implements the defined mathematical problem.

**Work:** Fix defects found in the baseline and add regression tests for signs, axis regularity, coordinate transforms, boundary conditions, invalid inputs, optimizer failures, units and degenerate cases. Remove or quarantine features that cannot be supported scientifically, especially any feature that is only phenomenological but presented as full electrospray physics.

**Deliverables:** Corrected solver modules; regression tests; change log; failure-case report.

**Completion gate:** The solver passes intended tests and fails explicitly on unsupported or invalid cases.

**Defense preparation:** For each module, prepare one sentence answering: what goes in, what equation or operation is performed, what comes out, and how it was tested.

## Chunk 4 — Numerical verification hierarchy

**Purpose:** Verify the complete reduced calculation, not just isolated functions.

**Work:** Run manufactured-solution tests for operators and fields; independent curvature and normal tests; coupled stress-residual tests; exact Taylor-limit tests with disclosure of encoded assumptions; and optimizer tests. Use at least three systematic grid refinements. Report observed error orders rather than assumed order.

**Deliverables:** Convergence tables and plots; residual diagnostics; boundary/domain/apex-cutoff sensitivity studies; initial-guess and failure summaries.

**Completion gate:** Every accuracy statement identifies the level it supports: operator, field, geometry, coupled residual or complete solver.

**Defense preparation:** Practice answering “How do you know the solver is correct?” with the verification hierarchy. Practice explaining why reproducing a known analytical solution is verification, not experimental validation.

## Chunk 5 — Identifiability and mathematical strengthening

**Purpose:** Determine whether the solver’s reported parameters are actually constrained by the residual.

**Work:** Derive the voltage-amplitude projection under linear electrostatic assumptions. Analyze residual landscapes before and after projection, sensitivity to angle and nuisance parameters, conditioning, parameter bounds and flat minima. Test joint pressure/voltage identifiability where relevant. Do not add a regularizer that forces the Taylor angle without labeling it as a prior.

**Deliverables:** Projection derivation; dimensionless groups; objective-landscape figures; sensitivity/conditioning results; revised interpretation of angle and voltage outputs.

**Completion gate:** The paper states what is identifiable, what is weakly identified and what cannot be inferred.

**Defense preparation:** Explain why a low residual is not enough, what amplitude elimination changes, how a flat objective affects uncertainty, and how the project handles a negative identifiability result.

## Chunk 6 — Lightweight-performance evidence

**Purpose:** Prove the practical value of being lightweight.

**Work:** Measure total runtime, field-solve time, optimization time, memory and failure rate on recorded hardware. Compare with a transparent baseline solving the same problem at matched accuracy. Run focused ablations: projected versus fixed amplitude and relevant interface/shape choices. Control warm starts, tolerances, hardware and random seeds.

**Deliverables:** Accuracy-versus-cost plot; baseline comparison; ablation table; reproducible benchmark command and raw timing data.

**Completion gate:** “Lightweight” has a quantitative definition. If no superiority is shown, use the narrower claim “compact,” “transparent” or “accessible.”

**Defense preparation:** Answer “Why does lightweight matter?” and “What did you sacrifice for speed?” Explain why an unfair comparison with a looser tolerance is invalid.

## Chunk 7 — Imaging pipeline repair and synthetic qualification

**Purpose:** Establish whether the analysis can measure a known image without circularity.

**Work:** Repair stable-frame selection, angle sign, coordinate origin, segmentation, border rejection, blank calibration handling, all-NaN acceptance and renderer/extractor axis consistency. Run the actual pixel-to-calibration-to-contour-to-profile-to-angle chain. Use separate development and held-out data with hidden truth. Include blur, noise, rotation, translation, clipping, rounded apexes, asymmetry, multiple objects, blank frames and nonconical profiles. Count failures.

**Deliverables:** Corrected pipeline; regression tests; held-out qualification report; failure gallery; synthetic-data manifest; uncertainty and coverage report.

**Completion gate:** No known truth enters extraction; invalid cases are rejected; the earlier synthetic table is removed from evidentiary use unless regenerated honestly.

**Defense preparation:** Explain the difference between synthetic qualification and physical calibration. Be able to show one successful case and one correctly rejected case. Explain why the old synthetic table was not valid evidence.

## Chunk 8 — Independent benchmark and prior-art comparison

**Purpose:** Establish what is genuinely new and what is inherited.

**Work:** Read primary sources on Taylor-cone theory, finite-nozzle equilibrium, conducting menisci, reduced methods and electrospray modeling. Build a comparison matrix covering equations, closures, geometry, numerical method, validation, cost and accessibility. Run an independent matched reference or narrow the claim if none is available.

**Deliverables:** Literature matrix; contribution map; matched-reference result; novelty statement with citations.

**Completion gate:** One precise contribution sentence is supported by both literature comparison and project results.

**Defense preparation:** Practice answering “What is novel?” without claiming that Taylor-cone theory, Python, finite differences or the 49.3-degree benchmark are new. Explain what the project adds and what it does not.

## Chunk 9 — Scientific validation protocol and lab package

**Purpose:** Make the remaining physical experiment precise and reviewable.

**Work:** Reconcile the protocol with the prediction route that the solver actually supports. Fix observables, trial structure, state definitions, exclusion rules, uncertainty model, prediction freeze, raw-data policy and amendment policy. Separate commissioning from confirmatory trials. Leave apparatus-specific safety values to qualified host review.

**Deliverables:** Protocol version; configuration form; blank trial record; analysis dry-run; revised one-page lab request; superseded-document notice.

**Completion gate:** A lab can assess feasibility without inventing the scientific design, while no document implies that physical validation or safety approval has already occurred.

**Defense preparation:** Explain the primary hypothesis, independent unit of replication, controls, exclusion rules, stop criteria, and what a positive, negative or inconclusive outcome would mean.

## Chunk 10 — Paper rebuild

**Purpose:** Turn verified work into a coherent paper.

**Work:** Rewrite the title, abstract, introduction, theory, methods, verification, results, limitations, proposed experiment and conclusion from the claim ledger. Regenerate every figure and table from scripts. Separate verification, image qualification and physical validation. Remove unsupported onset claims and any invalid synthetic result. Add a reproducibility appendix and a limitations table.

**Deliverables:** Revised LaTeX source; compiled PDF; supplement; figures; tables; data/code manifest; final claim ledger.

**Completion gate:** No contradiction exists between code, data, protocol, paper and outreach material. The conclusion is no stronger than the evidence.

**Defense preparation:** Build a poster narrative with one problem, one method, three strongest results and one limitation. Avoid filling the poster with implementation detail that does not support the central claim.

## Chunk 11 — Fair defense system

**Purpose:** Ensure the team can defend the project rather than merely submit it.

**Work:** Create a defense binder with: one-page summary; 30-second, two-minute and five-minute explanations; equation sheet; code/data map; verification evidence; novelty matrix; limitations; experiment protocol; safety boundary; contribution log; and likely judge questions. Every teammate should answer core questions independently.

**Core questions to rehearse:**

- What is the research question and why does it matter?
- What does “lightweight” mean quantitatively?
- What exact equations are solved?
- What boundary conditions are used?
- Why is the Taylor angle about 49.3 degrees?
- What does the immersed-boundary treatment contribute?
- How were convergence and error measured?
- What is verification, and what would count as validation?
- What was wrong with the earlier image-validation evidence?
- What assumptions are most likely to fail experimentally?
- Why is this not a full electrospray model?
- What is genuinely innovative relative to prior work?
- What would a negative result teach us?
- What did each student do personally?

**Defense rule:** Never answer with a stronger claim than the paper. If a result is unknown, say so and explain how the protocol would test it. Judges generally reward clear scientific boundaries more than confident overclaiming.

**Deliverables:** Defense binder; question bank with recorded answers; timed practice presentations; individual contribution statements; poster outline; mock-judge feedback log.

**Completion gate:** Each student can explain the model, reproduce the headline results conceptually, identify limitations and defend the experimental plan without relying on memorized wording.

## Chunk 12 — Independent pre-lab release review

**Purpose:** Catch errors before contacting labs or submitting.

**Work:** Reproduce the main results from a clean environment. Check equations, units, axes, figure labels, bibliography, cross-references, numerical tables, image qualification provenance, uncertainty calculations and safety language. Ask an independent reviewer to inspect the paper if possible; if not, label the review self-review.

**Deliverables:** Review checklist; resolved-issues log; final PDF; final protocol; outreach package; explicit pending-lab register.

**Completion gate:** Declare one status: “Pre-lab complete,” “Computational work still blocked,” or “Scope reduced with limitations.” Pre-lab complete means all computational claims are reproducible and the lab is needed only for physical measurement and approval—not for unfinished software or theory.

## Recommended working order

Work in this order: Chunks 0–2 first; then Chunks 3–5; run Chunk 6 after the solver is stable; run Chunk 7 in parallel once the environment is fixed; complete Chunk 8 before final novelty language; complete Chunk 9 before lab outreach; then Chunks 10–12.

At the end of each chunk, record: what changed, what evidence was produced, what failed, which claims changed, what remains blocked and what the team must be able to explain. Do not advance a chunk by hiding a failure. Narrowing the scope is an acceptable completion outcome; unsupported success is not.

## Final pre-lab definition of done

The project is ready to present to labs and fairs when it has a reproducible lightweight Taylor-cone solver, a mathematically consistent problem definition, complete numerical verification appropriate to its claims, quantitative evidence for or against the lightweight advantage, a genuinely tested synthetic image pipeline, a defensible novelty statement, a coherent lab-review protocol, a corrected paper and a practiced defense.

The project is not physically validated at that point. The remaining lab-dependent questions are real physical calibration, approved apparatus operation, measured inputs, attainable regime and comparison with independent experimental observations.
