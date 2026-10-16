# Superseded paper sections

`06_numerical_validation.tex` (restored 2026-10-16) is the orphaned earlier draft of the numerical
verification section. It was never referenced by `main.tex` (which included
`06_numerical_verification.tex`) and was dropped during the 2026-10-16 repository restructure.
Restored here from commit `50da243` so the provenance chain stays intact.

`08_image_processing_comparison.tex` and `09_expected_results_placeholders.tex`
(archived 2026-10-16) were removed from the compiled paper. The first specified an
image-processing pipeline for recording and analysing the project's own cone images, and the
second summarised results already reported in Sections 6 and 7. Neither described work that
was carried out: no photographic data of our own were recorded, and no recorded images were
ever pushed through that pipeline, so both sections stated methods and results the project
could not support. The synthetic round-trip result they quoted survives in Section 6.5, which
is where it is produced; the extraction toolkit itself remains in `solver/experimental/`.
