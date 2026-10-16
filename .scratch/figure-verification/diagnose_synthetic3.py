"""Third pass: does the pipeline recover the true angle once the harness stops
fighting it?

Candidate corrections, all harness-level:
  1. axis_orientation="vertical" (the renderer puts the symmetry axis on the
     image's vertical axis; the harness asks for "horizontal")
  2. do not equalizeHist a near-binary silhouette that carries additive noise
  3. give transform_to_axisymmetric an explicit origin: x = needle midline,
     y = deepest contour row (the cone apex)
  4. drop contour points inside the needle body (r <= needle radius) from the
     flank regression
  5. compare magnitudes, since the renderer's z axis runs negative toward the
     cone opening
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


def recover(image, normalize: bool):
    pre = preprocess_image(image, normalize=normalize, gaussian_sigma=1.0)
    edges = detect_edges_canny(pre, low_threshold=50, high_threshold=150)
    contour = extract_contour(edges, needle_tip_approx=None)
    contour = smooth_contour(contour, method="savgol", window_length=11)

    xs, ys = contour[:, 0].astype(float), contour[:, 1].astype(float)
    top = ys.min()
    axis_x = 0.5 * (xs[ys <= top + 1.0].min() + xs[ys <= top + 1.0].max())
    apex_y = ys.max()

    r, z = transform_to_axisymmetric(
        contour, MM_PER_PX, axis_orientation="vertical", origin_pixel=(axis_x, apex_y)
    )
    _apex_r, apex_z = identify_apex(r, z, method="max_z")
    outside = r > NEEDLE_RADIUS_MM
    angle, unc, fit = measure_half_angle(r[outside], z[outside], apex_z=apex_z)
    return abs(angle), unc, int(outside.sum()), fit["r_squared"]


np.random.seed(20260922)
for normalize in (True, False):
    print(f"\n===== preprocess_image(normalize={normalize}) =====")
    print(f"{'truth':>7} {'SNR':>6} {'error(deg)':>11} {'+/-':>7} {'nflank':>7} {'R2':>7}")
    for angle_true in ANGLES:
        r_true, z_true = cone_profile(angle_true)
        clean = generate_synthetic_image(r_true, z_true, NEEDLE_RADIUS_MM, mm_per_pixel=MM_PER_PX)
        for label, std in NOISE:
            noisy = add_realistic_noise(clean, gaussian_noise_std=std, blur_sigma=1.0)
            try:
                got, unc, n, r2 = recover(noisy, normalize)
                print(f"{angle_true:>7.2f} {label:>6} {abs(got - angle_true):>11.3f} "
                      f"{unc:>7.3f} {n:>7} {r2:>7.4f}")
            except Exception as exc:  # noqa: BLE001
                print(f"{angle_true:>7.2f} {label:>6}   raised {exc!r}")
