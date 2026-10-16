"""Fourth pass: sweep the needle-exclusion threshold.

The extracted contour is a closed outline: needle stem + cone top rim + two
cone flanks.  measure_half_angle assumes a one-sided monotone profile, so the
stem (constant r ~ needle radius) must be dropped or it dominates the
regression.  The rim sits at the most negative z and falls outside the
25-75% flank window, so it needs no special handling.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "solver"))

import numpy as np  # noqa: E402

from experimental.image_processing import (  # noqa: E402
    detect_edges_canny,
    extract_contour,
    preprocess_image,
    smooth_contour,
)
from experimental.profile_extraction import (  # noqa: E402
    identify_apex,
    measure_half_angle,
    transform_to_axisymmetric,
)
from experimental.synthetic_validation import (  # noqa: E402
    add_realistic_noise,
    generate_synthetic_image,
)

MM_PER_PX = 0.02
NEEDLE_RADIUS_MM = 0.4
NOISE = [("40 dB", 1.3), ("30 dB", 4.0), ("20 dB", 12.7), ("10 dB", 40.0)]
ANGLES = [45.0, 49.29, 55.0]


def cone_profile(half_angle_deg, apex_radius_mm=0.05, cone_length_mm=4.0, n=120):
    z = np.linspace(0.0, -cone_length_mm, n)
    r = np.abs(z) * np.tan(np.radians(half_angle_deg))
    mask = r < apex_radius_mm
    if np.any(mask):
        r[mask] = np.sqrt(np.maximum(apex_radius_mm**2 - (z[mask] - apex_radius_mm) ** 2, 0.0))
    return r, z


def recover(image, margin_factor: float):
    pre = preprocess_image(image, normalize=False, gaussian_sigma=1.0)
    edges = detect_edges_canny(pre, low_threshold=50, high_threshold=150)
    contour = smooth_contour(extract_contour(edges), method="savgol", window_length=11)

    xs, ys = contour[:, 0].astype(float), contour[:, 1].astype(float)
    top = ys.min()
    axis_x = 0.5 * (xs[ys <= top + 1.0].min() + xs[ys <= top + 1.0].max())
    apex_y = ys.max()

    r, z = transform_to_axisymmetric(
        contour, MM_PER_PX, axis_orientation="vertical", origin_pixel=(axis_x, apex_y)
    )
    _apex_r, apex_z = identify_apex(r, z, method="max_z")
    keep = r > NEEDLE_RADIUS_MM * margin_factor
    angle, unc, fit = measure_half_angle(r[keep], z[keep], apex_z=apex_z)
    return abs(angle), unc, int(keep.sum()), fit["r_squared"]


np.random.seed(20260922)
for factor in (1.0, 1.5, 2.0, 2.5, 3.0):
    errs = []
    print(f"\n===== needle-exclusion threshold = {factor} x needle radius =====")
    for angle_true in ANGLES:
        r_true, z_true = cone_profile(angle_true)
        clean = generate_synthetic_image(r_true, z_true, NEEDLE_RADIUS_MM, mm_per_pixel=MM_PER_PX)
        for label, std in NOISE:
            noisy = add_realistic_noise(clean, gaussian_noise_std=std, blur_sigma=1.0)
            try:
                got, unc, n, r2 = recover(noisy, factor)
                errs.append(abs(got - angle_true))
                print(f"  {angle_true:>6.2f} {label:>6}  err={abs(got - angle_true):>7.3f}  "
                      f"n={n:>5}  R2={r2:>7.4f}")
            except Exception as exc:  # noqa: BLE001
                print(f"  {angle_true:>6.2f} {label:>6}  raised {exc!r}")
    if errs:
        print(f"  --> max |error| = {max(errs):.3f} deg")
