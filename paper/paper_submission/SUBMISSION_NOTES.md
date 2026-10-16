# Submission Notes

This manuscript is written for Hong Kong ISEF selection and reports work done
before any physical experiment.

## Contents

- Abstract
- Introduction and motivation
- Literature review
- Research question and hypothesis
- Theoretical model
- Solver architecture
- Numerical results (Section 6), including the synthetic round trip of the extraction pipeline
- Comparison against published ethanol cone-jet photographs (Section 7)
- Safety, ethics and compliance
- Limitations
- Conclusion and future work
- Bibliography

## Experimental placeholders

None. No physical experiments were performed for this manuscript, so it reports
no measured data of its own and contains no `TBD` cells. Section 7 re-uses
photographs from the cited literature.

## Compiled files

```text
paper/paper_submission/main.pdf
paper/paper_submission/build/isef_taylor_cone_submission_draft.pdf   # archived earlier draft
```

## Compile command used

```bash
cd paper/paper_submission
rm -f main.out
latexmk -pdf main.tex
```

## Important final checks before official submission

1. Replace placeholder author/school information.
2. Confirm Hong Kong selection formatting and page limits.
3. Confirm all safety and approval language with the teacher/supervisor.
4. Recompile and inspect the final PDF visually.
