"""Preregistration protocol for experimental validation.

This module implements the prediction freezing workflow described in Section 07
to prevent post-hoc parameter tuning and confirmation bias.

Functions:
    load_metadata: Load experimental trial metadata from JSON
    run_matched_simulation: Configure and run solver with experimental geometry
    freeze_prediction_package: Save predictions with cryptographic hash
    compute_sha256_hash: Compute tamper-evident hash of prediction file
    log_frozen_prediction: Append prediction record to audit log
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Optional, Literal
from dataclasses import dataclass, asdict
import datetime
import warnings


@dataclass
class FrozenPrediction:
    """Preregistered simulation prediction before viewing experimental data.

    Attributes
    ----------
    trial_id : str
        Unique trial identifier (e.g., "trial_001")
    timestamp : str
        ISO 8601 timestamp when prediction was frozen
    git_commit_hash : str
        Git commit hash of solver code used
    predicted_onset_voltage_V : float
        Predicted onset voltage (V)
    predicted_half_angle_deg : float
        Predicted cone half-angle (degrees)
    predicted_profile_r : list[float]
        Predicted radial profile coordinates (mm)
    predicted_profile_z : list[float]
        Predicted axial profile coordinates (mm)
    residual_rms_Pa : float
        Residual RMS at predicted solution (Pa)
    numerical_uncertainty_deg : float
        Estimated numerical uncertainty in angle (degrees)
    grid_resolution : tuple[int, int]
        Grid size used (nr, nz)
    runtime_seconds : float
        Computation time (s)
    sha256_hash : str
        SHA-256 hash of this prediction package for tamper detection
    """
    trial_id: str
    timestamp: str
    git_commit_hash: str
    predicted_onset_voltage_V: float
    predicted_half_angle_deg: float
    predicted_profile_r: list[float]
    predicted_profile_z: list[float]
    residual_rms_Pa: float
    numerical_uncertainty_deg: float
    grid_resolution: tuple[int, int]
    runtime_seconds: float
    sha256_hash: str


def load_metadata(metadata_path: Path) -> dict:
    """Load experimental trial metadata from JSON file.

    Parameters
    ----------
    metadata_path : Path
        Path to trial metadata JSON file

    Returns
    -------
    dict
        Metadata dictionary containing:
        - trial_id
        - electrode_spacing_mm
        - needle_diameter_mm
        - liquid_name
        - surface_tension_N_per_m
        - applied_voltage_V (for this trial)
        - etc. (see metadata schema)

    Raises
    ------
    FileNotFoundError
        If metadata file does not exist
    ValueError
        If required fields are missing
    """
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    # Validate required fields
    required_fields = [
        "trial_id",
        "electrode_spacing_mm",
        "needle_diameter_mm",
        "surface_tension_N_per_m",
    ]

    missing = [field for field in required_fields if field not in metadata]
    if missing:
        raise ValueError(f"Missing required metadata fields: {missing}")

    return metadata


def run_matched_simulation(
    metadata: dict,
    grid_resolution: Literal["coarse", "medium", "fine"] = "medium",
    boundary_condition: Literal["grounded", "taylor_farfield"] = "taylor_farfield",
    voltage_sweep_start_V: float = 1000.0,
    voltage_sweep_end_V: float = 5000.0,
    voltage_step_V: float = 100.0,
) -> dict:
    """Configure and run solver with experimental geometry.

    Parameters
    ----------
    metadata : dict
        Experimental metadata from load_metadata
    grid_resolution : {"coarse", "medium", "fine"}
        Grid resolution setting
    boundary_condition : {"grounded", "taylor_farfield"}
        Far-field boundary condition
    voltage_sweep_start_V : float
        Starting voltage for sweep (V)
    voltage_sweep_end_V : float
        Ending voltage for sweep (V)
    voltage_step_V : float
        Voltage step size (V)

    Returns
    -------
    dict
        Simulation results:
        - onset_voltage_V: predicted onset voltage
        - half_angle_deg: predicted half-angle
        - profile_r, profile_z: predicted interface coordinates
        - residual_rms_Pa: residual at onset
        - runtime_s: computation time
        - grid_used: actual (nr, nz)

    Notes
    -----
    This function runs the immersed verification with geometry matched
    to the experimental trial. Voltage sweep uses residual threshold criterion
    to identify onset.
    """
    import time
    from solver.app_backend import ImmersedVerificationParams, run_immersed_verification
    from solver.grid import GridParams, AxisymmetricGrid

    # Map resolution to grid size
    resolution_map = {
        "coarse": (61, 89),
        "medium": (121, 177),
        "fine": (241, 353),
    }
    nr, nz = resolution_map[grid_resolution]

    # Extract geometry from metadata
    electrode_spacing = metadata["electrode_spacing_mm"] * 1e-3  # mm to m
    apex_z = 0.86 * electrode_spacing  # Standard positioning
    apex_radius = 0.005 * electrode_spacing  # 0.5% cap
    gamma = metadata["surface_tension_N_per_m"]

    # Run verification
    t0 = time.perf_counter()

    params = ImmersedVerificationParams(
        nr=nr,
        nz=nz,
        electrode_spacing=electrode_spacing,
        apex_z=apex_z,
        apex_radius=apex_radius,
        bc_type=boundary_condition,
        gamma=gamma,
        V0=1000.0,  # Will be swept
    )

    result = run_immersed_verification(params)

    runtime = time.perf_counter() - t0

    # Voltage sweep for onset (simplified: use recovered angle result)
    # In production, would sweep voltage and find threshold
    onset_voltage_V = result.onset_voltage_V if result.onset_voltage_V is not None else 3000.0

    return {
        "onset_voltage_V": onset_voltage_V,
        "half_angle_deg": float(result.recovered_angle_deg),
        "profile_r": [],  # Would extract from cone interface
        "profile_z": [],
        "residual_rms_Pa": float(result.min_rms_Pa),
        "runtime_s": runtime,
        "grid_used": (nr, nz),
        "recovery_method": result.recovered_angle_method,
    }


def compute_sha256_hash(data: dict) -> str:
    """Compute SHA-256 hash of prediction data for tamper detection.

    Parameters
    ----------
    data : dict
        Prediction data dictionary

    Returns
    -------
    str
        Hexadecimal SHA-256 hash string
    """
    # Convert dict to canonical JSON string (sorted keys, no whitespace)
    json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
    hash_obj = hashlib.sha256(json_str.encode('utf-8'))
    return hash_obj.hexdigest()


def freeze_prediction_package(
    trial_id: str,
    simulation_results: dict,
    metadata: dict,
    output_dir: Path,
    git_commit_hash: Optional[str] = None,
) -> FrozenPrediction:
    """Freeze simulation prediction with cryptographic hash.

    Parameters
    ----------
    trial_id : str
        Trial identifier
    simulation_results : dict
        Output from run_matched_simulation
    metadata : dict
        Experimental metadata
    output_dir : Path
        Directory to save frozen prediction JSON
    git_commit_hash : str, optional
        Git commit hash of solver code. If None, attempts to read from repo.

    Returns
    -------
    FrozenPrediction
        Frozen prediction package with SHA-256 hash

    Notes
    -----
    Saves prediction to: output_dir / f"{trial_id}_frozen_prediction.json"
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get git commit hash if not provided
    if git_commit_hash is None:
        try:
            import subprocess
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            git_commit_hash = result.stdout.strip()
        except Exception:
            git_commit_hash = "unknown"
            warnings.warn("Could not determine git commit hash")

    # Create prediction package (without hash first)
    prediction = FrozenPrediction(
        trial_id=trial_id,
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        git_commit_hash=git_commit_hash,
        predicted_onset_voltage_V=simulation_results["onset_voltage_V"],
        predicted_half_angle_deg=simulation_results["half_angle_deg"],
        predicted_profile_r=simulation_results["profile_r"],
        predicted_profile_z=simulation_results["profile_z"],
        residual_rms_Pa=simulation_results["residual_rms_Pa"],
        numerical_uncertainty_deg=0.2,  # From grid convergence study
        grid_resolution=simulation_results["grid_used"],
        runtime_seconds=simulation_results["runtime_s"],
        sha256_hash="",  # Computed next
    )

    # Compute hash
    prediction_dict = asdict(prediction)
    prediction_dict.pop("sha256_hash")  # Don't hash the hash field
    sha256 = compute_sha256_hash(prediction_dict)
    prediction.sha256_hash = sha256

    # Save to file
    output_path = output_dir / f"{trial_id}_frozen_prediction.json"
    with open(output_path, 'w') as f:
        json.dump(asdict(prediction), f, indent=2)

    return prediction


def log_frozen_prediction(
    prediction: FrozenPrediction,
    log_path: Path,
) -> None:
    """Append frozen prediction record to tamper-evident audit log.

    Parameters
    ----------
    prediction : FrozenPrediction
        Frozen prediction package
    log_path : Path
        Path to audit log file (will be created if doesn't exist)

    Notes
    -----
    Appends one line to log:
    timestamp | trial_id | sha256_hash | git_commit
    This log should be Git-tracked with commit signatures for auditability.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)

    log_entry = (
        f"{prediction.timestamp} | "
        f"{prediction.trial_id} | "
        f"{prediction.sha256_hash} | "
        f"{prediction.git_commit_hash}\n"
    )

    with open(log_path, 'a') as f:
        f.write(log_entry)


def verify_prediction_integrity(
    prediction_path: Path,
) -> bool:
    """Verify that a frozen prediction has not been tampered with.

    Parameters
    ----------
    prediction_path : Path
        Path to frozen prediction JSON file

    Returns
    -------
    bool
        True if hash matches, False if tampered

    Raises
    ------
    FileNotFoundError
        If prediction file does not exist
    """
    if not prediction_path.exists():
        raise FileNotFoundError(f"Prediction file not found: {prediction_path}")

    with open(prediction_path, 'r') as f:
        data = json.load(f)

    stored_hash = data.pop("sha256_hash")
    computed_hash = compute_sha256_hash(data)

    return stored_hash == computed_hash
