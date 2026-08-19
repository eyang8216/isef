"""Comparison metrics for simulation vs experimental validation.

This module implements profile alignment, RMSE computation, error decomposition,
and statistical significance testing for Taylor-cone validation.

Functions:
    align_profiles: Align experimental and simulated profiles
    compute_profile_rmse: Root mean square error between profiles
    decompose_rmse_components: Separate angle-driven, apex, and base errors
    compute_angle_error: Half-angle comparison
    compute_voltage_error: Onset voltage comparison
    statistical_significance_test: Multi-trial statistical validation
"""

from __future__ import annotations

import numpy as np
from typing import Tuple, Literal, Optional
from dataclasses import dataclass
from scipy.interpolate import interp1d


@dataclass
class ComparisonMetrics:
    """Complete comparison between simulation and experiment.

    Attributes
    ----------
    profile_rmse_mm : float
        Root mean square radial error (mm)
    profile_nrmse : float
        Normalized RMSE (dimensionless, relative to characteristic length)
    angle_error_deg : float
        Absolute half-angle error (degrees)
    voltage_error_frac : float
        Fractional onset voltage error
    rmse_decomposition : dict
        Error components: angle_driven, apex_region, flank_region
    alignment_method : str
        Alignment strategy used
    n_comparison_points : int
        Number of points used in RMSE calculation
    characteristic_length_mm : float
        Normalization length for nRMSE
    """
    profile_rmse_mm: float
    profile_nrmse: float
    angle_error_deg: float
    voltage_error_frac: float
    rmse_decomposition: dict
    alignment_method: str
    n_comparison_points: int
    characteristic_length_mm: float


def align_profiles(
    r_exp: np.ndarray,
    z_exp: np.ndarray,
    r_sim: np.ndarray,
    z_sim: np.ndarray,
    method: Literal["apex", "needle_tip", "flank_lsq"] = "apex",
    apex_exp: Optional[Tuple[float, float]] = None,
    apex_sim: Optional[Tuple[float, float]] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Align experimental and simulated profiles in the same coordinate system.

    Parameters
    ----------
    r_exp, z_exp : np.ndarray
        Experimental profile coordinates (mm)
    r_sim, z_sim : np.ndarray
        Simulated profile coordinates (mm)
    method : {"apex", "needle_tip", "flank_lsq"}
        Alignment strategy
    apex_exp, apex_sim : tuple of (r, z), optional
        Apex positions if known (required for "apex" method)

    Returns
    -------
    r_exp_aligned, z_exp_aligned : np.ndarray
        Aligned experimental profile
    r_sim_aligned, z_sim_aligned : np.ndarray
        Aligned simulated profile

    Notes
    -----
    All methods translate profiles to align a reference point.
    "apex": Align apex positions to origin
    "needle_tip": Align base/detachment points to origin
    "flank_lsq": Minimize flank-region RMSE over translation
    """
    if method == "apex":
        if apex_exp is None or apex_sim is None:
            raise ValueError("apex_exp and apex_sim required for apex alignment")

        # Translate both profiles so apexes are at origin
        r_exp_aligned = r_exp - apex_exp[0]
        z_exp_aligned = z_exp - apex_exp[1]
        r_sim_aligned = r_sim - apex_sim[0]
        z_sim_aligned = z_sim - apex_sim[1]

    elif method == "needle_tip":
        # Align base points (minimum z)
        tip_z_exp = np.min(z_exp)
        tip_r_exp = r_exp[np.argmin(z_exp)]
        tip_z_sim = np.min(z_sim)
        tip_r_sim = r_sim[np.argmin(z_sim)]

        r_exp_aligned = r_exp - tip_r_exp
        z_exp_aligned = z_exp - tip_z_exp
        r_sim_aligned = r_sim - tip_r_sim
        z_sim_aligned = z_sim - tip_z_sim

    elif method == "flank_lsq":
        # Minimize flank-region RMSE over translation
        # Use middle 50% of z-range as flank
        z_min = max(np.min(z_exp), np.min(z_sim))
        z_max = min(np.max(z_exp), np.max(z_sim))
        z_mid = 0.5 * (z_min + z_max)
        z_width = 0.5 * (z_max - z_min)

        flank_mask_exp = (z_exp >= z_mid - 0.25*z_width) & (z_exp <= z_mid + 0.25*z_width)
        flank_mask_sim = (z_sim >= z_mid - 0.25*z_width) & (z_sim <= z_mid + 0.25*z_width)

        # Grid search over small translations (simplified)
        best_rmse = np.inf
        best_dr, best_dz = 0.0, 0.0

        for dr in np.linspace(-0.5, 0.5, 21):  # ±0.5 mm in 0.05 mm steps
            for dz in np.linspace(-1.0, 1.0, 41):  # ±1 mm in 0.05 mm steps
                r_exp_test = r_exp + dr
                z_exp_test = z_exp + dz

                # Interpolate sim onto exp flank z-coords
                if np.sum(flank_mask_exp) < 3 or np.sum(flank_mask_sim) < 3:
                    continue

                z_exp_flank = z_exp_test[flank_mask_exp]
                r_exp_flank = r_exp_test[flank_mask_exp]

                # Check overlap
                if np.max(z_exp_flank) < np.min(z_sim) or np.min(z_exp_flank) > np.max(z_sim):
                    continue

                try:
                    interp_sim = interp1d(z_sim, r_sim, kind='linear', fill_value='extrapolate')
                    r_sim_interp = interp_sim(z_exp_flank)
                    rmse = np.sqrt(np.mean((r_exp_flank - r_sim_interp)**2))
                    if rmse < best_rmse:
                        best_rmse = rmse
                        best_dr, best_dz = dr, dz
                except Exception:
                    continue

        r_exp_aligned = r_exp + best_dr
        z_exp_aligned = z_exp + best_dz
        r_sim_aligned = r_sim
        z_sim_aligned = z_sim

    else:
        raise ValueError(f"Unknown alignment method: {method}")

    return r_exp_aligned, z_exp_aligned, r_sim_aligned, z_sim_aligned


def compute_profile_rmse(
    r_exp: np.ndarray,
    z_exp: np.ndarray,
    r_sim: np.ndarray,
    z_sim: np.ndarray,
    characteristic_length: Optional[float] = None,
) -> Tuple[float, float, int]:
    """Compute RMSE between aligned profiles.

    Parameters
    ----------
    r_exp, z_exp : np.ndarray
        Experimental profile (aligned)
    r_sim, z_sim : np.ndarray
        Simulated profile (aligned)
    characteristic_length : float, optional
        Length scale for normalization (e.g., electrode spacing, cone length).
        If None, nRMSE is not computed.

    Returns
    -------
    rmse_mm : float
        Root mean square radial error (mm)
    nrmse : float
        Normalized RMSE (dimensionless). NaN if characteristic_length is None.
    n_points : int
        Number of comparison points

    Notes
    -----
    Interpolates simulation onto experimental z-coordinates.
    Only compares in the overlapping z-range.
    """
    # Find overlapping z-range
    z_min = max(np.min(z_exp), np.min(z_sim))
    z_max = min(np.max(z_exp), np.max(z_sim))

    if z_min >= z_max:
        raise ValueError("No overlapping z-range between profiles")

    # Select experimental points in overlap
    mask_exp = (z_exp >= z_min) & (z_exp <= z_max)
    z_exp_overlap = z_exp[mask_exp]
    r_exp_overlap = r_exp[mask_exp]

    if len(z_exp_overlap) < 2:
        raise ValueError("Insufficient experimental points in overlap region")

    # Interpolate simulation onto experimental z-coords
    interp_sim = interp1d(z_sim, r_sim, kind='linear', bounds_error=False, fill_value=np.nan)
    r_sim_interp = interp_sim(z_exp_overlap)

    # Remove any NaN from interpolation
    valid = ~np.isnan(r_sim_interp)
    r_exp_valid = r_exp_overlap[valid]
    r_sim_valid = r_sim_interp[valid]

    if len(r_exp_valid) < 2:
        raise ValueError("Insufficient valid comparison points after interpolation")

    # Compute RMSE
    rmse_mm = float(np.sqrt(np.mean((r_exp_valid - r_sim_valid)**2)))

    # Normalized RMSE
    if characteristic_length is not None and characteristic_length > 0:
        nrmse = rmse_mm / characteristic_length
    else:
        nrmse = np.nan

    return rmse_mm, nrmse, len(r_exp_valid)


def decompose_rmse_components(
    r_exp: np.ndarray,
    z_exp: np.ndarray,
    r_sim: np.ndarray,
    z_sim: np.ndarray,
    apex_z: float,
    apex_window_mm: float = 0.5,
) -> dict:
    """Decompose profile RMSE into angle-driven, apex, and flank components.

    Parameters
    ----------
    r_exp, z_exp : np.ndarray
        Experimental profile (aligned)
    r_sim, z_sim : np.ndarray
        Simulated profile (aligned)
    apex_z : float
        Apex axial position (mm)
    apex_window_mm : float
        Window size around apex for apex-region RMSE (mm)

    Returns
    -------
    dict
        RMSE components:
        - rmse_total: overall RMSE (mm)
        - rmse_apex: RMSE in apex region (mm)
        - rmse_flank: RMSE in flank region (mm)
        - n_apex: number of apex points
        - n_flank: number of flank points

    Notes
    -----
    Apex region: |z - apex_z| < apex_window_mm
    Flank region: |z - apex_z| >= apex_window_mm
    """
    # Total RMSE
    rmse_total, _, n_total = compute_profile_rmse(r_exp, z_exp, r_sim, z_sim)

    # Apex region
    apex_mask_exp = np.abs(z_exp - apex_z) < apex_window_mm
    if np.sum(apex_mask_exp) >= 2:
        r_exp_apex = r_exp[apex_mask_exp]
        z_exp_apex = z_exp[apex_mask_exp]
        try:
            rmse_apex, _, n_apex = compute_profile_rmse(r_exp_apex, z_exp_apex, r_sim, z_sim)
        except ValueError:
            rmse_apex, n_apex = np.nan, 0
    else:
        rmse_apex, n_apex = np.nan, 0

    # Flank region
    flank_mask_exp = np.abs(z_exp - apex_z) >= apex_window_mm
    if np.sum(flank_mask_exp) >= 2:
        r_exp_flank = r_exp[flank_mask_exp]
        z_exp_flank = z_exp[flank_mask_exp]
        try:
            rmse_flank, _, n_flank = compute_profile_rmse(r_exp_flank, z_exp_flank, r_sim, z_sim)
        except ValueError:
            rmse_flank, n_flank = np.nan, 0
    else:
        rmse_flank, n_flank = 0

    return {
        "rmse_total_mm": rmse_total,
        "rmse_apex_mm": rmse_apex,
        "rmse_flank_mm": rmse_flank,
        "n_total": n_total,
        "n_apex": n_apex,
        "n_flank": n_flank,
    }


def compute_angle_error(
    angle_exp_deg: float,
    angle_sim_deg: float,
) -> float:
    """Compute absolute half-angle error.

    Parameters
    ----------
    angle_exp_deg : float
        Experimental half-angle (degrees)
    angle_sim_deg : float
        Simulated half-angle (degrees)

    Returns
    -------
    float
        Absolute angle error |α_sim - α_exp| (degrees)
    """
    return abs(angle_sim_deg - angle_exp_deg)


def compute_voltage_error(
    voltage_exp_V: float,
    voltage_sim_V: float,
) -> float:
    """Compute fractional onset voltage error.

    Parameters
    ----------
    voltage_exp_V : float
        Experimental onset voltage (V)
    voltage_sim_V : float
        Simulated onset voltage (V)

    Returns
    -------
    float
        Fractional error |V_sim - V_exp| / V_exp (dimensionless)
    """
    return abs(voltage_sim_V - voltage_exp_V) / voltage_exp_V


def statistical_significance_test(
    prediction: float,
    measurements: np.ndarray,
) -> dict:
    """Test whether simulation prediction agrees with experimental distribution.

    Parameters
    ----------
    prediction : float
        Simulation prediction (angle, voltage, or other scalar)
    measurements : np.ndarray
        Array of experimental measurements from repeated trials

    Returns
    -------
    dict
        Statistical summary:
        - exp_mean: experimental mean
        - exp_std: experimental standard deviation
        - exp_sem: standard error of mean
        - deviation: prediction - mean
        - deviation_sigma: deviation in units of standard deviation
        - within_1sigma: bool, is prediction within 1σ of mean
        - within_2sigma: bool, is prediction within 2σ of mean

    Notes
    -----
    Strong agreement: deviation < 1σ
    Acceptable agreement: deviation < 2σ
    Significant discrepancy: deviation > 2σ
    """
    exp_mean = float(np.mean(measurements))
    exp_std = float(np.std(measurements, ddof=1)) if len(measurements) > 1 else 0.0
    exp_sem = exp_std / np.sqrt(len(measurements)) if len(measurements) > 0 else 0.0

    deviation = prediction - exp_mean
    deviation_sigma = abs(deviation) / exp_std if exp_std > 0 else np.inf

    return {
        "prediction": prediction,
        "exp_mean": exp_mean,
        "exp_std": exp_std,
        "exp_sem": exp_sem,
        "n_trials": len(measurements),
        "deviation": deviation,
        "deviation_sigma": deviation_sigma,
        "within_1sigma": deviation_sigma <= 1.0,
        "within_2sigma": deviation_sigma <= 2.0,
    }


def compare_profiles(
    r_exp: np.ndarray,
    z_exp: np.ndarray,
    r_sim: np.ndarray,
    z_sim: np.ndarray,
    angle_exp_deg: float,
    angle_sim_deg: float,
    voltage_exp_V: float,
    voltage_sim_V: float,
    apex_exp: Tuple[float, float],
    apex_sim: Tuple[float, float],
    alignment_method: Literal["apex", "needle_tip", "flank_lsq"] = "apex",
    characteristic_length_mm: Optional[float] = None,
) -> ComparisonMetrics:
    """Complete comparison pipeline: align profiles and compute all metrics.

    Parameters
    ----------
    r_exp, z_exp : np.ndarray
        Experimental profile (raw)
    r_sim, z_sim : np.ndarray
        Simulated profile (raw)
    angle_exp_deg, angle_sim_deg : float
        Half-angles (degrees)
    voltage_exp_V, voltage_sim_V : float
        Onset voltages (V)
    apex_exp, apex_sim : tuple of (r, z)
        Apex positions (mm)
    alignment_method : {"apex", "needle_tip", "flank_lsq"}
        Profile alignment strategy
    characteristic_length_mm : float, optional
        Length for nRMSE normalization (e.g., electrode spacing)

    Returns
    -------
    ComparisonMetrics
        Complete comparison with RMSE, angle error, voltage error, decomposition
    """
    # Align profiles
    r_exp_aligned, z_exp_aligned, r_sim_aligned, z_sim_aligned = align_profiles(
        r_exp, z_exp, r_sim, z_sim,
        method=alignment_method,
        apex_exp=apex_exp,
        apex_sim=apex_sim,
    )

    # Compute RMSE
    if characteristic_length_mm is None:
        # Use cone length as default
        characteristic_length_mm = max(np.max(z_exp_aligned) - np.min(z_exp_aligned),
                                        np.max(z_sim_aligned) - np.min(z_sim_aligned))

    rmse_mm, nrmse, n_points = compute_profile_rmse(
        r_exp_aligned, z_exp_aligned,
        r_sim_aligned, z_sim_aligned,
        characteristic_length=characteristic_length_mm,
    )

    # Decompose RMSE
    apex_z_aligned = apex_exp[1] - apex_exp[1]  # Apex at z=0 after alignment
    rmse_decomp = decompose_rmse_components(
        r_exp_aligned, z_exp_aligned,
        r_sim_aligned, z_sim_aligned,
        apex_z=apex_z_aligned,
    )

    # Angle and voltage errors
    angle_error = compute_angle_error(angle_exp_deg, angle_sim_deg)
    voltage_error = compute_voltage_error(voltage_exp_V, voltage_sim_V)

    return ComparisonMetrics(
        profile_rmse_mm=rmse_mm,
        profile_nrmse=nrmse,
        angle_error_deg=angle_error,
        voltage_error_frac=voltage_error,
        rmse_decomposition=rmse_decomp,
        alignment_method=alignment_method,
        n_comparison_points=n_points,
        characteristic_length_mm=characteristic_length_mm,
    )
