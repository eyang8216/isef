#!/usr/bin/env python3
"""Run the synthetic image-processing validation for the paper's Section 6.

Analytic Taylor-cone silhouettes are rendered by the repository's pipeline
(``solver/experimental/synthetic_validation.py``) and pushed through
preprocessing, Canny edge detection, contour extraction, and profile/half-angle
fitting.  The recovered half-angles are reported against the known ground truth
together with the pipeline's acceptance flag.

This runner only supplies the test matrix, writes the result record and draws
the figure.  No error value is synthesised here: every number below comes out
of the extraction code.

NOTE (2026-10-16): an earlier version of this script did not process the
rendered image at all.  It reported

    extracted_angle = true_angle + np.random.normal(0, 0.3)

so its published table measured a random number generator rather than the
imaging pipeline.  That fabricated path has been removed.  Rows shown as
``nan`` are cases in which the pipeline raised (for example a missing optional
imaging dependency).

NOTE (2026-10-17): the first real run of the corrected script returned angle
errors of 25--80 deg.  Those were traced to defects in the surrounding test
harness rather than in the extraction code: the renderer was asked for a
horizontal symmetry axis when it draws a vertical one, histogram equalisation
was applied to an almost-binary silhouette (turning sensor noise into ~2x10^5
spurious edge pixels), the origin was taken from a closed outline that includes
the needle, and the needle body was left in the flank regression.  The harness
now prescribes the axis from the needle centreline, skips equalisation, and
fits the flank outside the needle body.  See
``solver/experimental/synthetic_validation.py``.
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


# Nominal SNR label -> Gaussian noise standard deviation (0-255 image range).
# The label is 20*log10(150/sigma) for a 150-grey-level silhouette contrast, and
# is quoted only to keep continuity with the acceptance statement in the paper.
NOISE_CONFIGS = [("40 dB", 1.3), ("30 dB", 4.0), ("20 dB", 12.7), ("10 dB", 40.0)]
TEST_ANGLES = [45.0, 49.29, 55.0]
NOISE_SEED = 20260922

#: Prescribed calibration: the needle is mounted on the optical axis at a known
#: radius, and the image scale follows from the renderer's pixel size.
NEEDLE_RADIUS_MM = 0.4
MM_PER_PIXEL = 0.02

#: Acceptance criteria stated in Section 6.5.
ANGLE_LIMIT_DEG = 1.0
NRMSE_LIMIT_PCT = 2.0

DATA_FILE = (REPO_ROOT / "paper" / "paper_submission" / "data"
             / "synthetic_validation_results.txt")
FIGURE_FILE = (REPO_ROOT / "paper" / "paper_submission" / "figures"
               / "06_synthetic_holdout.png")


def run_synthetic_validation():
    """Process every (angle, noise) case through the real pipeline."""

    print("=" * 68)
    print("SYNTHETIC IMAGE PROCESSING VALIDATION (repository pipeline)")
    print("=" * 68)

    rows = []
    acceptance = {}
    np.random.seed(NOISE_SEED)

    for angle_true in TEST_ANGLES:
        r, z = generate_cone_profile(angle_true)
        result = validate_pipeline_accuracy(
            r, z, angle_true,
            needle_radius_mm=NEEDLE_RADIUS_MM,
            mm_per_pixel=MM_PER_PIXEL,
            noise_levels=[std for _, std in NOISE_CONFIGS],
        )
        cone_length_mm = result["cone_length_mm"]
        acceptance[angle_true] = result["acceptance_criteria_met"]

        for (label, std), err, rmse in zip(NOISE_CONFIGS,
                                           result["angle_errors_deg"],
                                           result["profile_rmse_mm"]):
            nrmse_pct = 100.0 * rmse / cone_length_mm
            rows.append({
                "true_angle": angle_true,
                "snr": label,
                "noise_std": std,
                "angle_error": err,
                "profile_rmse_mm": rmse,
                "profile_nrmse_pct": nrmse_pct,
            })
            shown = "nan (pipeline raised)" if np.isnan(err) else f"{err:.4f}"
            print(f"  alpha={angle_true:6.2f} deg  SNR {label:>5} "
                  f"(sigma={std:5.1f}): angle error {shown} deg, "
                  f"nRMSE {nrmse_pct:6.3f} %")

        if result["failure_messages"]:
            for message in result["failure_messages"]:
                print(f"    ! {message}")

        print(f"  -> acceptance flag for alpha={angle_true:.2f} deg: "
              f"{result['acceptance_criteria_met']}")

    finite = [row["angle_error"] for row in rows if np.isfinite(row["angle_error"])]
    if finite:
        print(f"\nOverall: {len(finite)}/{len(rows)} cases produced a number; "
              f"max |angle error| = {max(abs(e) for e in finite):.4f} deg, "
              f"max nRMSE = {max(row['profile_nrmse_pct'] for row in rows):.3f} %")
    else:
        print(f"\nOverall: 0/{len(rows)} cases produced a number - the pipeline "
              f"did not run (check optional imaging dependencies).")

    return rows, acceptance


def write_data_file(rows):
    """Write the measured table consumed by the paper's Section 6.5."""

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w") as fh:
        fh.write("# Synthetic image-processing validation results\n")
        fh.write("# Pipeline: solver/experimental/synthetic_validation.py "
                 "(real extraction; no simulated errors)\n")
        fh.write(f"# Noise seed: {NOISE_SEED}\n")
        fh.write(f"# Calibration: needle radius {NEEDLE_RADIUS_MM} mm, "
                 f"{MM_PER_PIXEL} mm/pixel\n")
        fh.write("# Columns: Ground_Truth_deg,SNR,Noise_Sigma,"
                 "Angle_Error_deg,Profile_RMSE_mm,Profile_nRMSE_pct\n")
        for row in rows:
            fh.write(f"{row['true_angle']:.2f},{row['snr']},"
                     f"{row['noise_std']:.1f},{row['angle_error']:.4f},"
                     f"{row['profile_rmse_mm']:.4f},"
                     f"{row['profile_nrmse_pct']:.4f}\n")
    print(f"\nResults written to: {DATA_FILE}")


def create_figure(rows):
    """Draw the two-panel accuracy figure from the measured rows."""

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import NullLocator, NullFormatter

    styles = {
        45.0: dict(marker="o", color="#7a4fa3"),
        49.29: dict(marker="s", color="#1f9b8e"),
        55.0: dict(marker="^", color="#c8801a"),
    }

    fig, (ax_angle, ax_profile) = plt.subplots(1, 2, figsize=(12.4, 5.0))

    for angle_true in TEST_ANGLES:
        subset = [row for row in rows if row["true_angle"] == angle_true]
        x = [row["noise_std"] for row in subset]
        style = styles[angle_true]
        label = f"$\\alpha_{{\\mathrm{{true}}}}$ = {angle_true:g}$^\\circ$"

        ax_angle.plot(x, [row["angle_error"] for row in subset],
                      linestyle="none", label=label, markersize=7, **style)
        ax_profile.plot(x, [row["profile_nrmse_pct"] for row in subset],
                        linestyle="none", label=label, markersize=7, **style)

    for ax, limit, ylabel, title in (
        (ax_angle, ANGLE_LIMIT_DEG, "Absolute angle error [$^\\circ$]",
         "(a) Half-angle error"),
        (ax_profile, NRMSE_LIMIT_PCT, "Profile nRMSE [\\%]",
         "(b) Profile error"),
    ):
        ax.axhline(limit, color="0.25", linestyle="--", linewidth=1.2,
                   label=f"acceptance limit {limit:g}")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Gaussian noise standard deviation [greyscale levels]")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, which="both", alpha=0.3)
        # The noise levels are named by their nominal SNR; suppress the log
        # minor ticks so those names are the only x labels.
        ax.set_xticks([std for _, std in NOISE_CONFIGS])
        ax.set_xticklabels([label for label, _ in NOISE_CONFIGS])
        ax.xaxis.set_minor_locator(NullLocator())
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.set_xlim(0.9, 55.0)

    ax_angle.set_ylim(bottom=1e-3)
    ax_profile.set_ylim(0.05, 30.0)
    ax_angle.legend(loc="upper left", fontsize=9, framealpha=0.95)

    fig.tight_layout()
    FIGURE_FILE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_FILE, dpi=250, bbox_inches="tight")
    plt.close(fig)
    print(f"Figure written to: {FIGURE_FILE}")


def main():
    rows, _acceptance = run_synthetic_validation()
    write_data_file(rows)
    create_figure(rows)
    return rows


if __name__ == "__main__":
    main()
