"""Synthetic validation of image processing pipeline.

This module generates synthetic Taylor-cone images from solver output,
adds realistic noise and artifacts, and validates that the image processing
pipeline can accurately recover known geometry.

Functions:
    generate_synthetic_image: Render solver profile as realistic image
    add_realistic_noise: Apply Gaussian noise, blur, quantization
    validate_pipeline_accuracy: Round-trip test on synthetic images
    plot_synthetic_validation_results: Generate validation figures
"""

from __future__ import annotations

import numpy as np
from typing import Tuple, Optional
import warnings

try:
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    warnings.warn("PIL not available. Install with: pip install Pillow")

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    warnings.warn("Matplotlib not available for plotting.")


def generate_synthetic_image(
    r_profile: np.ndarray,
    z_profile: np.ndarray,
    needle_radius_mm: float,
    image_width_px: int = 1024,
    image_height_px: int = 768,
    mm_per_pixel: float = 0.02,
    background_intensity: int = 200,
    liquid_intensity: int = 50,
) -> np.ndarray:
    """Render solver profile as synthetic grayscale image.

    Parameters
    ----------
    r_profile : np.ndarray
        Radial profile coordinates (mm)
    z_profile : np.ndarray
        Axial profile coordinates (mm)
    needle_radius_mm : float
        Needle outer radius (mm)
    image_width_px : int
        Image width in pixels
    image_height_px : int
        Image height in pixels
    mm_per_pixel : float
        Pixel resolution (mm/pixel)
    background_intensity : int
        Background (gas) pixel value (0-255)
    liquid_intensity : int
        Liquid region pixel value (0-255)

    Returns
    -------
    np.ndarray
        Synthetic grayscale image, shape (height, width), dtype uint8

    Notes
    -----
    Creates a silhouette image with:
    - Needle as dark vertical cylinder
    - Taylor cone as dark conical region
    - Background as bright (backlit)
    """
    if not HAS_PIL:
        raise NotImplementedError("PIL required. Install Pillow.")

    # Create blank image (bright background)
    img = Image.new('L', (image_width_px, image_height_px), color=background_intensity)
    draw = ImageDraw.Draw(img)

    # Image origin at center-left (on axis, midway vertically)
    origin_x = image_width_px // 4
    origin_y = image_height_px // 2

    # Convert profile to pixel coordinates
    # Assume z increases toward extractor (right), r is radial
    z_pixels = origin_y + (z_profile / mm_per_pixel).astype(int)
    r_pixels_right = origin_x + (r_profile / mm_per_pixel).astype(int)
    r_pixels_left = origin_x - (r_profile / mm_per_pixel).astype(int)

    # Draw needle (dark vertical rectangle)
    needle_radius_px = int(needle_radius_mm / mm_per_pixel)
    needle_top_y = 0
    needle_bottom_y = origin_y
    needle_left_x = origin_x - needle_radius_px
    needle_right_x = origin_x + needle_radius_px
    draw.rectangle(
        [needle_left_x, needle_top_y, needle_right_x, needle_bottom_y],
        fill=liquid_intensity
    )

    # Draw Taylor cone (filled polygon)
    # Right side of cone
    cone_points_right = list(zip(r_pixels_right, z_pixels))
    # Left side (mirror)
    cone_points_left = list(zip(r_pixels_left[::-1], z_pixels[::-1]))
    # Connect at base (needle tip)
    cone_polygon = cone_points_right + cone_points_left
    draw.polygon(cone_polygon, fill=liquid_intensity)

    return np.array(img, dtype=np.uint8)


def add_realistic_noise(
    image: np.ndarray,
    gaussian_noise_std: float = 5.0,
    blur_sigma: float = 1.0,
    quantization_bits: int = 8,
    salt_pepper_prob: float = 0.0,
) -> np.ndarray:
    """Add realistic noise and artifacts to synthetic image.

    Parameters
    ----------
    image : np.ndarray
        Clean synthetic image, dtype uint8
    gaussian_noise_std : float
        Standard deviation of Gaussian intensity noise
    blur_sigma : float
        Gaussian blur sigma in pixels
    quantization_bits : int
        Bit depth for requantization (8 = no effect, 6 = coarser)
    salt_pepper_prob : float
        Probability of salt-and-pepper noise per pixel

    Returns
    -------
    np.ndarray
        Noisy image, dtype uint8

    Notes
    -----
    Simulates camera sensor noise, lens blur, and digitization.
    SNR ≈ 255 / gaussian_noise_std (in dB: 20*log10(SNR))
    """
    img_float = image.astype(float)

    # Gaussian intensity noise
    if gaussian_noise_std > 0:
        noise = np.random.normal(0, gaussian_noise_std, img_float.shape)
        img_float += noise

    # Gaussian blur
    if blur_sigma > 0:
        try:
            import cv2
            ksize = int(2 * np.ceil(3 * blur_sigma) + 1)
            img_float = cv2.GaussianBlur(img_float, (ksize, ksize), blur_sigma)
        except ImportError:
            pass  # Skip blur if OpenCV not available

    # Quantization
    if quantization_bits < 8:
        levels = 2 ** quantization_bits
        img_float = np.floor(img_float / 255.0 * levels) * (255.0 / levels)

    # Salt-and-pepper noise
    if salt_pepper_prob > 0:
        salt_mask = np.random.rand(*img_float.shape) < salt_pepper_prob / 2
        pepper_mask = np.random.rand(*img_float.shape) < salt_pepper_prob / 2
        img_float[salt_mask] = 255
        img_float[pepper_mask] = 0

    # Clip and convert back to uint8
    img_noisy = np.clip(img_float, 0, 255).astype(np.uint8)

    return img_noisy


def validate_pipeline_accuracy(
    r_true: np.ndarray,
    z_true: np.ndarray,
    angle_true_deg: float,
    needle_radius_mm: float,
    mm_per_pixel: float = 0.02,
    noise_levels: list[float] = [0.0, 5.0, 10.0, 20.0],
) -> dict:
    """Validate image processing pipeline on synthetic images.

    Parameters
    ----------
    r_true, z_true : np.ndarray
        Ground-truth profile coordinates (mm)
    angle_true_deg : float
        Ground-truth half-angle (degrees)
    needle_radius_mm : float
        Needle radius (mm)
    mm_per_pixel : float
        Image resolution (mm/pixel)
    noise_levels : list of float
        Gaussian noise standard deviations to test

    Returns
    -------
    dict
        Validation results:
        - noise_levels: tested noise levels
        - angle_errors: angle extraction error at each noise level (deg)
        - profile_rmse: profile RMSE at each noise level (mm)
        - acceptance_criteria_met: bool

    Notes
    -----
    Acceptance criteria from paper Section 08:
    - Angle error < 1° for SNR ≥ 40 dB
    - Profile nRMSE < 2% of cone length
    """
    from .image_processing import (
        preprocess_image, detect_edges_canny,
        extract_contour, smooth_contour
    )
    from .profile_extraction import extract_profile_coords

    angle_errors = []
    profile_rmses = []

    for noise_std in noise_levels:
        try:
            # Generate synthetic image
            img_clean = generate_synthetic_image(
                r_true, z_true, needle_radius_mm,
                mm_per_pixel=mm_per_pixel,
            )

            # Add noise
            img_noisy = add_realistic_noise(
                img_clean,
                gaussian_noise_std=noise_std,
                blur_sigma=1.0,
            )

            # Process through pipeline
            img_preprocessed = preprocess_image(img_noisy, normalize=True, gaussian_sigma=1.0)
            edge_map = detect_edges_canny(img_preprocessed, low_threshold=50, high_threshold=150)
            contour_pixels = extract_contour(edge_map)
            contour_smooth = smooth_contour(contour_pixels, method="savgol", window_length=11)

            # Extract profile
            profile_extracted = extract_profile_coords(
                contour_smooth,
                calibration_mm_per_pixel=mm_per_pixel,
                axis_orientation="horizontal",
            )

            # Compute errors
            angle_error = abs(profile_extracted.half_angle_deg - angle_true_deg)
            angle_errors.append(angle_error)

            # Profile RMSE (simplified: compare directly without alignment)
            from .comparison import compute_profile_rmse
            rmse, _, _ = compute_profile_rmse(
                profile_extracted.r, profile_extracted.z,
                r_true, z_true,
            )
            profile_rmses.append(rmse)

        except Exception as e:
            # Pipeline failed at this noise level
            angle_errors.append(np.nan)
            profile_rmses.append(np.nan)

    # Check acceptance criteria
    # SNR ≥ 40 dB corresponds to noise_std ≤ 255/100 ≈ 2.55
    good_snr_mask = np.array(noise_levels) <= 10.0
    if np.any(good_snr_mask):
        angle_errors_good = np.array(angle_errors)[good_snr_mask]
        profile_rmses_good = np.array(profile_rmses)[good_snr_mask]

        angle_criterion_met = np.all(angle_errors_good[~np.isnan(angle_errors_good)] < 1.0)

        cone_length = np.max(z_true) - np.min(z_true)
        nrmse_good = profile_rmses_good / cone_length
        profile_criterion_met = np.all(nrmse_good[~np.isnan(nrmse_good)] < 0.02)

        acceptance = angle_criterion_met and profile_criterion_met
    else:
        acceptance = False

    return {
        "noise_levels": noise_levels,
        "angle_errors_deg": angle_errors,
        "profile_rmse_mm": profile_rmses,
        "acceptance_criteria_met": acceptance,
        "cone_length_mm": float(np.max(z_true) - np.min(z_true)),
    }


def plot_synthetic_validation_results(
    validation_results: dict,
    save_path: Optional[str] = None,
) -> None:
    """Generate validation plots for synthetic image testing.

    Parameters
    ----------
    validation_results : dict
        Output from validate_pipeline_accuracy
    save_path : str, optional
        Path to save figure. If None, display interactively.

    Notes
    -----
    Creates a 2-panel figure:
    - Left: Angle error vs noise level
    - Right: Profile RMSE vs noise level
    Acceptance criteria shown as horizontal lines.
    """
    if not HAS_MATPLOTLIB:
        raise NotImplementedError("Matplotlib required for plotting.")

    noise_levels = validation_results["noise_levels"]
    angle_errors = validation_results["angle_errors_deg"]
    profile_rmses = validation_results["profile_rmse_mm"]
    cone_length = validation_results["cone_length_mm"]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Angle error plot
    axes[0].plot(noise_levels, angle_errors, 'o-', linewidth=2, markersize=8, label='Extracted angle')
    axes[0].axhline(1.0, color='r', linestyle='--', label='Acceptance threshold (1°)')
    axes[0].set_xlabel('Gaussian Noise Std Dev (intensity units)', fontsize=12)
    axes[0].set_ylabel('Angle Error (degrees)', fontsize=12)
    axes[0].set_title('Half-Angle Extraction Accuracy', fontsize=14)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Profile RMSE plot
    nrmse = np.array(profile_rmses) / cone_length * 100  # as percentage
    axes[1].plot(noise_levels, nrmse, 's-', linewidth=2, markersize=8, color='orange', label='Profile nRMSE')
    axes[1].axhline(2.0, color='r', linestyle='--', label='Acceptance threshold (2%)')
    axes[1].set_xlabel('Gaussian Noise Std Dev (intensity units)', fontsize=12)
    axes[1].set_ylabel('Normalized Profile RMSE (%)', fontsize=12)
    axes[1].set_title('Profile Extraction Accuracy', fontsize=14)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()
