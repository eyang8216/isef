# `experimental/` — imaging and extraction toolkit

This package is the image-side half of the project. It renders synthetic silhouettes of
Taylor cones, pushes them (or recorded frames) through a contour-extraction chain, converts
pixels to axisymmetric $(r, z)$ profiles, and compares those profiles against solver output.

It is a **separate top-level package** from `solver/` — `solver/solver/` is the importable
package `solver`; this directory is the sibling package `experimental`, declared in
`pyproject.toml` under `[tool.setuptools] packages`. It is not needed to run the electrostatic
solver, and it requires the optional imaging dependencies:

```bash
pip install -e ".[imaging]"   # Pillow + opencv-python
```

## Modules

| Module | Responsibility |
| --- | --- |
| `image_processing.py` | Frame selection, pixel/mm calibration, preprocessing (`preprocess_image`), Canny/Otsu/Sobel edge detection, contour extraction and smoothing |
| `profile_extraction.py` | `transform_to_axisymmetric`, apex and needle-tip identification, flank least-squares half-angle (`measure_half_angle`, `extract_profile_coords`), `ProfileData` |
| `comparison.py` | Profile alignment, RMSE and its decomposition, angle/voltage error, significance tests (`compare_profiles`) |
| `synthetic_validation.py` | Synthetic silhouette rendering, noise models, axis-origin estimation, and the end-to-end round-trip harness `validate_pipeline_accuracy` |
| `metadata.py` | `TrialMetadata` records plus JSON validation, save and typed load |
| `preregistration.py` | Freezing predictions before experimental data are viewed, with SHA-256 integrity checks |

## Reproducing the synthetic round-trip results

The results reported in the paper (largest half-angle error $0.027^\circ$, largest profile
nRMSE $0.62\%$ over the accepted noise levels) are produced by:

```bash
python experiments/methodology/generate_synthetic_validation.py
```

That script runs a $3 \times 4$ matrix of three half-angles ($45^\circ$, $49.29^\circ$,
$55^\circ$) against four Gaussian noise levels, and writes both

- `paper/paper_submission/data/synthetic_validation_results.txt`, and
- `paper/paper_submission/figures/06_synthetic_holdout.png`.

The noise realisation is fixed by seed `20260922`, and the symmetry axis is taken from the
needle centreline, which the renderer places on the optical axis. Both are prescribed
calibration data rather than measured quantities.

## Scope

The round trip validates the software chain — rendering, thresholding, contour tracking and
least-squares flank fitting — against analytic silhouettes. It does not calibrate the chain
against recorded images: illumination variation, contact-line pinning, optical distortion and
finite camera resolution are all outside its scope.
