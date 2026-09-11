"""Profile extraction and half-angle measurement for Taylor-cone validation.

This module transforms pixel contours into physical (r, z) coordinates and
extracts quantitative geometric properties like half-angle and apex position.

Functions:
    transform_to_axisymmetric: Convert pixel coordinates to (r, z)
    identify_apex: Locate the cone apex from contour
    identify_needle_tip: Locate needle detachment point
    measure_half_angle: Extract cone half-angle via flank line fit
    extract_profile_coords: Complete pipeline from pixels to physical coords
"""

from __future__ import annotations

import numpy as np
from typing import Tuple, Optional, Literal
from dataclasses import dataclass


@dataclass
class ProfileData:
    """Extracted Taylor-cone profile in physical coordinates.

    Attributes
    ----------
    r : np.ndarray
        Radial coordinates (mm), shape (n_points,)
    z : np.ndarray
        Axial coordinates (mm), shape (n_points,)
    half_angle_deg : float
        Cone half-angle (degrees)
    half_angle_uncertainty_deg : float
        Standard error of half-angle from line fit
    apex_r : float
        Apex radial position (mm)
    apex_z : float
        Apex axial position (mm)
    flank_fit_params : dict
        Line fit parameters: slope, intercept, r_squared, flank_window
    """
    r: np.ndarray
    z: np.ndarray
    half_angle_deg: float
    half_angle_uncertainty_deg: float
    apex_r: float
    apex_z: float
    flank_fit_params: dict


def transform_to_axisymmetric(
    contour_pixels: np.ndarray,
    calibration_mm_per_pixel: float,
    axis_orientation: Literal["vertical", "horizontal"] = "vertical",
    origin_pixel: Optional[Tuple[float, float]] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Transform pixel contour to axisymmetric (r, z) coordinates.

    Parameters
    ----------
    contour_pixels : np.ndarray
        Contour in pixel coordinates, shape (n_points, 2) as (x, y)
    calibration_mm_per_pixel : float
        Calibration scale (mm/pixel)
    axis_orientation : {"vertical", "horizontal"}
        Direction of the symmetry axis. "vertical" means z is y-direction.
    origin_pixel : tuple of (x0, y0), optional
        Origin location in pixel coords. If None, will be determined from apex.

    Returns
    -------
    r : np.ndarray
        Radial coordinates (mm), shape (n_points,)
    z : np.ndarray
        Axial coordinates (mm), shape (n_points,)

    Notes
    -----
    Assumes the contour represents one side of an axisymmetric interface.
    The origin is typically at the apex or needle tip.
    """
    x_pixels = contour_pixels[:, 0]
    y_pixels = contour_pixels[:, 1]

    # Determine origin if not provided
    if origin_pixel is None:
        # Default: use apex (maximum penetration point)
        if axis_orientation == "vertical":
            # Apex is at maximum y (assuming y increases downward toward extractor)
            apex_idx = np.argmax(y_pixels)
        else:
            # Apex is at maximum x
            apex_idx = np.argmax(x_pixels)
        origin_pixel = (float(x_pixels[apex_idx]), float(y_pixels[apex_idx]))

    x0, y0 = origin_pixel

    # Transform to physical coordinates
    x_mm = (x_pixels - x0) * calibration_mm_per_pixel
    y_mm = (y_pixels - y0) * calibration_mm_per_pixel

    # Map to (r, z) based on orientation
    if axis_orientation == "vertical":
        r = np.abs(x_mm)  # Radial distance from axis
        z = y_mm          # Axial position (positive toward extractor)
    else:
        r = np.abs(y_mm)
        z = x_mm

    return r, z


def identify_apex(
    r: np.ndarray,
    z: np.ndarray,
    method: Literal["max_z", "min_r"] = "max_z",
) -> Tuple[float, float]:
    """Identify apex position from profile coordinates.

    Parameters
    ----------
    r : np.ndarray
        Radial coordinates (mm)
    z : np.ndarray
        Axial coordinates (mm)
    method : {"max_z", "min_r"}
        Method for apex identification.
        "max_z": point with maximum axial penetration
        "min_r": point with minimum radius

    Returns
    -------
    apex_r : float
        Apex radial coordinate (mm)
    apex_z : float
        Apex axial coordinate (mm)
    """
    if method == "max_z":
        apex_idx = np.argmax(z)
    elif method == "min_r":
        apex_idx = np.argmin(r)
    else:
        raise ValueError(f"Unknown apex identification method: {method}")

    return float(r[apex_idx]), float(z[apex_idx])


def identify_needle_tip(
    r: np.ndarray,
    z: np.ndarray,
    needle_radius_mm: Optional[float] = None,
) -> Tuple[float, float]:
    """Identify needle tip (detachment point) from profile.

    Parameters
    ----------
    r : np.ndarray
        Radial coordinates (mm)
    z : np.ndarray
        Axial coordinates (mm)
    needle_radius_mm : float, optional
        Known needle outer radius. If provided, finds the point closest to this radius.

    Returns
    -------
    tip_r : float
        Needle tip radial coordinate (mm)
    tip_z : float
        Needle tip axial coordinate (mm)

    Notes
    -----
    The needle tip is typically where the interface detaches from the needle,
    identified as a sharp curvature change or the point nearest to the needle radius.
    """
    if needle_radius_mm is not None:
        # Find point closest to known needle radius
        tip_idx = np.argmin(np.abs(r - needle_radius_mm))
    else:
        # Use point with minimum z (closest to needle base)
        tip_idx = np.argmin(z)

    return float(r[tip_idx]), float(z[tip_idx])


def measure_half_angle(
    r: np.ndarray,
    z: np.ndarray,
    flank_window_fraction: Tuple[float, float] = (0.25, 0.75),
    apex_z: Optional[float] = None,
) -> Tuple[float, float, dict]:
    """Extract cone half-angle via least-squares line fit to flank.

    Parameters
    ----------
    r : np.ndarray
        Radial coordinates (mm)
    z : np.ndarray
        Axial coordinates (mm)
    flank_window_fraction : tuple of (z_min_frac, z_max_frac)
        Flank region as fraction of cone length from apex.
        E.g., (0.25, 0.75) uses middle 50% of visible cone.
    apex_z : float, optional
        Apex axial position. If None, determined automatically.

    Returns
    -------
    half_angle_deg : float
        Cone half-angle in degrees
    uncertainty_deg : float
        Standard error of half-angle from line fit
    fit_params : dict
        Line fit parameters: slope, intercept, r_squared, flank_indices

    Notes
    -----
    Fits r = m*z + b to the flank region via weighted least squares.
    Half-angle α = arctan(m).
    """
    if apex_z is None:
        apex_z, _ = identify_apex(r, z, method="max_z")

    # Define flank region
    z_min_cone = np.min(z)
    z_max_cone = np.max(z)
    cone_length = z_max_cone - z_min_cone

    z_min_flank = apex_z - flank_window_fraction[1] * cone_length
    z_max_flank = apex_z - flank_window_fraction[0] * cone_length

    flank_mask = (z >= z_min_flank) & (z <= z_max_flank)
    flank_indices = np.where(flank_mask)[0]

    if np.sum(flank_mask) < 3:
        raise ValueError(f"Insufficient flank points ({np.sum(flank_mask)} < 3) for line fit")

    r_flank = r[flank_mask]
    z_flank = z[flank_mask]

    # Least-squares line fit: r = m*z + b
    n = len(r_flank)
    z_mean = np.mean(z_flank)
    r_mean = np.mean(r_flank)

    numerator = np.sum((z_flank - z_mean) * (r_flank - r_mean))
    denominator = np.sum((z_flank - z_mean)**2)

    if denominator < 1e-12:
        raise ValueError("Flank z-coordinates are degenerate (constant z)")

    slope = numerator / denominator
    intercept = r_mean - slope * z_mean

    # Compute R-squared
    r_pred = slope * z_flank + intercept
    ss_res = np.sum((r_flank - r_pred)**2)
    ss_tot = np.sum((r_flank - r_mean)**2)
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    # Standard error of slope
    residuals = r_flank - r_pred
    s_residual = np.sqrt(np.sum(residuals**2) / (n - 2))
    s_slope = s_residual / np.sqrt(denominator)

    # Convert slope to half-angle
    half_angle_rad = np.arctan(slope)
    half_angle_deg = float(np.degrees(half_angle_rad))

    # Propagate uncertainty: δα = δm / (1 + m²)
    uncertainty_rad = s_slope / (1.0 + slope**2)
    uncertainty_deg = float(np.degrees(uncertainty_rad))

    fit_params = {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r_squared),
        "flank_indices": flank_indices.tolist(),
        "flank_window_z": (float(z_min_flank), float(z_max_flank)),
        "n_points": int(n),
    }

    return half_angle_deg, uncertainty_deg, fit_params


def extract_profile_coords(
    contour_pixels: np.ndarray,
    calibration_mm_per_pixel: float,
    axis_orientation: Literal["vertical", "horizontal"] = "vertical",
    flank_window_fraction: Tuple[float, float] = (0.25, 0.75),
    needle_radius_mm: Optional[float] = None,
) -> ProfileData:
    """Complete pipeline: pixel contour → physical profile with half-angle.

    Parameters
    ----------
    contour_pixels : np.ndarray
        Raw contour from image processing, shape (n_points, 2)
    calibration_mm_per_pixel : float
        Calibration scale (mm/pixel)
    axis_orientation : {"vertical", "horizontal"}
        Symmetry axis direction
    flank_window_fraction : tuple of (z_min_frac, z_max_frac)
        Flank region for angle measurement
    needle_radius_mm : float, optional
        Known needle radius for origin/tip identification

    Returns
    -------
    ProfileData
        Complete profile with coordinates, half-angle, apex position, fit parameters

    Notes
    -----
    This is the main entry point for converting image contours to physical profiles.
    """
    # Transform to (r, z)
    r, z = transform_to_axisymmetric(
        contour_pixels,
        calibration_mm_per_pixel,
        axis_orientation=axis_orientation,
        origin_pixel=None,  # Will use apex as origin
    )

    # Identify apex
    apex_r, apex_z = identify_apex(r, z, method="max_z")

    # Measure half-angle
    half_angle_deg, uncertainty_deg, fit_params = measure_half_angle(
        r, z,
        flank_window_fraction=flank_window_fraction,
        apex_z=apex_z,
    )

    return ProfileData(
        r=r,
        z=z,
        half_angle_deg=half_angle_deg,
        half_angle_uncertainty_deg=uncertainty_deg,
        apex_r=apex_r,
        apex_z=apex_z,
        flank_fit_params=fit_params,
    )
