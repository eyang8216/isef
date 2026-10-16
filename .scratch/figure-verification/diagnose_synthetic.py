"""Diagnose why the synthetic-image pipeline returns 25-80 deg angle errors.

Renders a known 45 deg cone through the repository's own renderer, then walks
the extraction chain step by step and tests the two axes of variation that the
harness fixes in advance:

  * axis_orientation: the harness passes "horizontal", but the renderer puts
    r on the image x axis and z on the image y axis (symmetry axis vertical)
  * contour selection: the harness calls extract_contour() with no needle tip,
    which returns the longest contour in the whole edge map
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


def cone_profile(half_angle_deg, apex_radius_mm=0.05, cone_length_mm=4.0, n=120):
    z = np.linspace(0.0, -cone_length_mm, n)
    r = np.abs(z) * np.tan(np.radians(half_angle_deg))
    mask = r < apex_radius_mm
    if np.any(mask):
        r[mask] = np.sqrt(np.maximum(apex_radius_mm**2 - (z[mask] - apex_radius_mm) ** 2, 0.0))
    return r, z


ANGLE = 45.0
MM_PER_PX = 0.02
r_true, z_true = cone_profile(ANGLE)
img = generate_synthetic_image(r_true, z_true, 0.4, mm_per_pixel=MM_PER_PX)

for tag, image in (("clean", img), ("noisy", add_realistic_noise(img, gaussian_noise_std=1.3, blur_sigma=1.0))):
    cv2.imwrite(str(OUT / f"diag_{tag}.png"), np.asarray(image))

img_noisy = add_realistic_noise(img, gaussian_noise_std=1.3, blur_sigma=1.0)
pre = preprocess_image(img_noisy, normalize=True, gaussian_sigma=1.0)
edges = detect_edges_canny(pre, low_threshold=50, high_threshold=150)
cv2.imwrite(str(OUT / "diag_edges.png"), edges)

contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
big = [c for c in contours if len(c) >= 50]
print(f"contours total={len(contours)} with len>=50: {len(big)}")
for c in sorted(big, key=len, reverse=True)[:6]:
    x, y, w, h = cv2.boundingRect(c)
    print(f"  len={len(c):>6}  bbox x={x:>4} y={y:>4} w={w:>4} h={h:>4}")

apex_px = (256, 384)  # renderer's origin: x = origin_x, y = origin_y
selected = {
    "longest": extract_contour(edges),
    "needle_tip": extract_contour(edges, needle_tip_approx=apex_px),
}

print(f"\nground truth half-angle = {ANGLE:.2f} deg")
for sel_name, contour in selected.items():
    sm = smooth_contour(contour, method="savgol", window_length=11)
    for orient in ("vertical", "horizontal"):
        try:
            prof = extract_profile_coords(
                sm, calibration_mm_per_pixel=MM_PER_PX, axis_orientation=orient
            )
            print(
                f"  contour={sel_name:<10} orientation={orient:<10} "
                f"-> angle {prof.half_angle_deg:>8.3f} deg  "
                f"apex=({prof.apex_r:.3f}, {prof.apex_z:.3f}) mm  n={len(prof.r)}"
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  contour={sel_name:<10} orientation={orient:<10} -> raised {exc!r}")
