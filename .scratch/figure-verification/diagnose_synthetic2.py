"""Second pass: which preprocessing/contour configuration actually recovers the cone?

The harness feeds a near-binary rendered silhouette (200 background / 50 liquid)
through cv2.equalizeHist before Canny, which amplifies sensor noise into
thousands of spurious edges.  Test the alternatives on the same rendered image.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "solver"))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from experimental.image_processing import (  # noqa: E402
    detect_edges_canny,
    extract_contour,
    preprocess_image,
    smooth_contour,
)
from experimental.profile_extraction import extract_profile_coords  # noqa: E402
from experimental.synthetic_validation import (  # noqa: E402
    add_realistic_noise,
    generate_synthetic_image,
)

OUT = Path(__file__).parent
ANGLE, MM_PER_PX = 45.0, 0.02


def cone_profile(half_angle_deg, apex_radius_mm=0.05, cone_length_mm=4.0, n=120):
    z = np.linspace(0.0, -cone_length_mm, n)
    r = np.abs(z) * np.tan(np.radians(half_angle_deg))
    mask = r < apex_radius_mm
    if np.any(mask):
        r[mask] = np.sqrt(np.maximum(apex_radius_mm**2 - (z[mask] - apex_radius_mm) ** 2, 0.0))
    return r, z


r_true, z_true = cone_profile(ANGLE)
img_clean = generate_synthetic_image(r_true, z_true, 0.4, mm_per_pixel=MM_PER_PX)
img_noisy = add_realistic_noise(img_clean, gaussian_noise_std=1.3, blur_sigma=1.0)
cv2.imwrite(str(OUT / "diag_clean.png"), np.asarray(img_clean))

apex_px = (256, 384)
variants = [
    ("noisy  normalize=1 blur=1.0 (harness)", img_noisy, dict(normalize=True, gaussian_sigma=1.0)),
    ("noisy  normalize=0 blur=1.0", img_noisy, dict(normalize=False, gaussian_sigma=1.0)),
    ("noisy  normalize=0 blur=3.0", img_noisy, dict(normalize=False, gaussian_sigma=3.0)),
    ("clean  normalize=1 blur=1.0", img_clean, dict(normalize=True, gaussian_sigma=1.0)),
    ("clean  normalize=0 blur=1.0", img_clean, dict(normalize=False, gaussian_sigma=1.0)),
]
for name, image, kw in variants:
    pre = preprocess_image(image, **kw)
    edges = detect_edges_canny(pre, low_threshold=50, high_threshold=150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    big = [c for c in contours if len(c) >= 50]
    tag = name.split()[0] + "_" + ("norm%d" % kw["normalize"]) + ("_blur%.1f" % kw["gaussian_sigma"])
    cv2.imwrite(str(OUT / f"diag_edges_{tag}.png"), edges)
    line = f"{name:<42} edges={int(edges.sum() // 255):>7}px  contours>=50: {len(big):>4}"
    try:
        contour = extract_contour(edges, needle_tip_approx=apex_px)
        sm = smooth_contour(contour, method="savgol", window_length=11)
        prof = extract_profile_coords(sm, calibration_mm_per_pixel=MM_PER_PX, axis_orientation="vertical")
        line += f"  n={len(contour):>6}  angle={prof.half_angle_deg:>7.3f} deg  (true {ANGLE})"
    except Exception as exc:  # noqa: BLE001
        line += f"  -> raised {exc!r}"
    print(line)
