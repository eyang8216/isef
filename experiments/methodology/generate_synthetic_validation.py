#!/usr/bin/env python3
"""Run the synthetic image-processing validation for the paper's Section 6/9.

Analytic Taylor-cone silhouettes are rendered by the repository's pipeline
(``solver/experimental/synthetic_validation.py``) and pushed through
preprocessing, Canny edge detection, contour extraction, and profile/half-angle
fitting.  The recovered half-angles are reported against the known ground truth
together with the pipeline's acceptance flag.

This runner only supplies the test matrix and writes the result record.

NOTE (2026-10-16): an earlier version of this script did not process the
rendered image at all.  It reported

    extracted_angle = true_angle + np.random.normal(0, 0.3)

so its published table measured a random number generator rather than the
imaging pipeline.  That fabricated path has been removed; the numbers below now
come from the real extraction code.  Rows shown as ``nan`` are cases in which
the pipeline raised (for example a missing optional imaging dependency).
"""

import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "solver"))

from experimental.synthetic_validation import validate_pipeline_accuracy  # noqa: E402


def generate_cone_profile(half_angle_deg, apex_radius_mm=0.05,
                          cone_length_mm=4.0, n_points=120):
    """Conical profile with a rounded apex (apex at z=0, cone opening at z<0)."""
    z = np.linspace(0.0, -cone_length_mm, n_points)
    r = np.abs(z) * np.tan(np.radians(half_angle_deg))

    apex_mask = r < apex_radius_mm
    if np.any(apex_mask):
        z_apex = z[apex_mask]
        r[apex_mask] = np.sqrt(
            np.maximum(apex_radius_mm**2 - (z_apex - apex_radius_mm) ** 2, 0.0)
        )
    return r, z


# SNR label -> Gaussian noise standard deviation (0-255 image range), matching
# the acceptance statement used in the paper.
NOISE_CONFIGS = [("40 dB", 1.3), ("30 dB", 4.0), ("20 dB", 12.7), ("10 dB", 40.0)]
TEST_ANGLES = [45.0, 49.29, 55.0]
NOISE_SEED = 20260922


def run_synthetic_validation():
    """Process every (angle, noise) case through the real pipeline."""

    print("=" * 68)
    print("SYNTHETIC IMAGE PROCESSING VALIDATION (repository pipeline)")
    print("=" * 68)

    rows = []
    np.random.seed(NOISE_SEED)

    for angle_true in TEST_ANGLES:
        r, z = generate_cone_profile(angle_true)
        result = validate_pipeline_accuracy(
            r, z, angle_true,
            needle_radius_mm=0.4,
            mm_per_pixel=0.02,
            noise_levels=[std for _, std in NOISE_CONFIGS],
        )

        for (label, _), err, rmse in zip(NOISE_CONFIGS,
                                        result["angle_errors_deg"],
                                        result["profile_rmse_mm"]):
            rows.append({
                "true_angle": angle_true,
                "snr": label,
                "angle_error": err,
                "profile_rmse_mm": rmse,
            })
            shown = "nan (pipeline raised)" if np.isnan(err) else f"{err:+.3f}"
            print(f"  alpha={angle_true:6.2f} deg  SNR {label:>5}: "
                  f"angle error {shown}")

        print(f"  -> acceptance flag for alpha={angle_true:.2f} deg: "
              f"{result['acceptance_criteria_met']}")

    finite = [row["angle_error"] for row in rows if np.isfinite(row["angle_error"])]
    if finite:
        print(f"\nOverall: {len(finite)}/{len(rows)} cases produced a number; "
              f"max |angle error| = {max(abs(e) for e in finite):.3f} deg")
    else:
        print(f"\nOverall: 0/{len(rows)} cases produced a number - the pipeline "
              f"did not run (check optional imaging dependencies).")

    output_dir = REPO_ROOT / "paper" / "paper_submission" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "synthetic_validation_results.txt"
    with output_file.open("w") as fh:
        fh.write("# Synthetic image-processing validation results\n")
        fh.write("# Pipeline: solver/experimental/synthetic_validation.py "
                 "(real extraction; no simulated errors)\n")
        fh.write(f"# Noise seed: {NOISE_SEED}\n")
        fh.write("Ground_Truth_deg,SNR,Angle_Error_deg,Profile_RMSE_mm\n")
        for row in rows:
            fh.write(f"{row['true_angle']:.2f},{row['snr']},"
                     f"{row['angle_error']:.4f},{row['profile_rmse_mm']:.4f}\n")

    print(f"\nResults written to: {output_file}")
    return rows


if __name__ == "__main__":
    run_synthetic_validation()
