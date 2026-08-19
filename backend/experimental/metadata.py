"""Metadata management for experimental trials.

This module defines the trial metadata schema and provides validation utilities.

Classes:
    TrialMetadata: Complete trial metadata dataclass

Functions:
    create_metadata_template: Generate blank metadata JSON template
    validate_metadata: Check metadata completeness and consistency
    save_metadata: Write metadata to JSON file
"""

from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Literal
import datetime


@dataclass
class TrialMetadata:
    """Complete experimental trial metadata.

    All fields documented in Section 07 of the paper.
    """
    # Trial identification
    trial_id: str
    date: str  # ISO 8601 date
    time_start: str  # ISO 8601 time
    operator: str
    supervisor: str
    session_notes: str = ""

    # Geometric parameters
    electrode_spacing_mm: float
    needle_outer_diameter_mm: float
    needle_inner_diameter_mm: float
    extractor_geometry: str  # "plate", "ring", or "aperture"
    extractor_dimensions_mm: str  # Free-form description

    # Fluid properties
    liquid_name: str
    liquid_purity: str
    liquid_supplier: str
    surface_tension_N_per_m: float
    conductivity_S_per_m: Optional[float] = None
    dopant_identity: Optional[str] = None
    dopant_concentration: Optional[str] = None
    liquid_temperature_C: Optional[float] = None

    # Operational settings
    applied_voltage_V: float
    flow_rate_uL_per_min: float
    observation_duration_s: float
    voltage_step_V: Optional[float] = None
    voltage_ramp_rate_V_per_s: Optional[float] = None

    # Imaging parameters
    camera_model: str
    resolution_pixels: tuple[int, int]  # (width, height)
    frame_rate_fps: float
    calibration_mm_per_pixel: float
    calibration_method: Literal["target", "needle_diameter"]
    lens_focal_length_mm: Optional[float] = None
    working_distance_mm: Optional[float] = None
    exposure_time_ms: Optional[float] = None

    # Environmental
    ambient_temperature_C: Optional[float] = None
    ambient_humidity_percent: Optional[float] = None

    # Qualitative observations
    regime_classification: Literal["no_cone", "unstable", "stable", "spray"]
    anomalies: str = ""

    # File references
    video_filename: Optional[str] = None
    image_directory: Optional[str] = None


def create_metadata_template(output_path: Path) -> None:
    """Generate blank metadata JSON template for manual completion.

    Parameters
    ----------
    output_path : Path
        Path where template JSON will be saved

    Notes
    -----
    Creates a template with placeholder values and explanatory comments.
    """
    template = {
        "_comment": "Trial metadata template. Fill all required fields before data collection.",
        "trial_id": "trial_001",
        "date": datetime.date.today().isoformat(),
        "time_start": "HH:MM:SS",
        "operator": "operator_name",
        "supervisor": "supervisor_name",
        "session_notes": "Any relevant notes about this trial",

        "electrode_spacing_mm": 10.0,
        "needle_outer_diameter_mm": 0.8,
        "needle_inner_diameter_mm": 0.6,
        "extractor_geometry": "plate",
        "extractor_dimensions_mm": "50x50 plate",

        "liquid_name": "ethanol",
        "liquid_purity": "99.5%",
        "liquid_supplier": "Supplier name",
        "surface_tension_N_per_m": 0.022,
        "conductivity_S_per_m": null,
        "dopant_identity": null,
        "dopant_concentration": null,
        "liquid_temperature_C": 22.0,

        "applied_voltage_V": 3000.0,
        "flow_rate_uL_per_min": 1.0,
        "observation_duration_s": 10.0,
        "voltage_step_V": 100.0,
        "voltage_ramp_rate_V_per_s": null,

        "camera_model": "Camera model name",
        "resolution_pixels": [1920, 1080],
        "frame_rate_fps": 10.0,
        "calibration_mm_per_pixel": 0.02,
        "calibration_method": "needle_diameter",
        "lens_focal_length_mm": 50.0,
        "working_distance_mm": 100.0,
        "exposure_time_ms": 10.0,

        "ambient_temperature_C": 22.0,
        "ambient_humidity_percent": 50.0,

        "regime_classification": "stable",
        "anomalies": "None observed",

        "video_filename": "trial_001_video.mp4",
        "image_directory": "trial_001/images/",
    }

    with open(output_path, 'w') as f:
        json.dump(template, f, indent=2)


def validate_metadata(metadata: dict) -> tuple[bool, list[str]]:
    """Check metadata completeness and consistency.

    Parameters
    ----------
    metadata : dict
        Metadata dictionary to validate

    Returns
    -------
    is_valid : bool
        True if all validation checks pass
    errors : list of str
        List of validation error messages (empty if valid)

    Notes
    -----
    Checks for:
    - Required fields present
    - Physical constraints (positive values, reasonable ranges)
    - Consistency between related fields
    """
    errors = []

    # Required fields
    required = [
        "trial_id", "date", "operator", "supervisor",
        "electrode_spacing_mm", "needle_outer_diameter_mm",
        "liquid_name", "surface_tension_N_per_m",
        "applied_voltage_V", "flow_rate_uL_per_min",
        "camera_model", "resolution_pixels", "calibration_mm_per_pixel",
        "regime_classification",
    ]

    for field in required:
        if field not in metadata or metadata[field] is None:
            errors.append(f"Missing required field: {field}")

    # Physical constraints
    if "electrode_spacing_mm" in metadata:
        if metadata["electrode_spacing_mm"] <= 0:
            errors.append("electrode_spacing_mm must be positive")
        if metadata["electrode_spacing_mm"] > 100:
            errors.append("electrode_spacing_mm > 100 mm seems unrealistic (check units)")

    if "surface_tension_N_per_m" in metadata:
        if not (0.001 < metadata["surface_tension_N_per_m"] < 0.1):
            errors.append("surface_tension outside typical range (0.001-0.1 N/m)")

    if "applied_voltage_V" in metadata:
        if metadata["applied_voltage_V"] < 0:
            errors.append("applied_voltage_V must be non-negative")
        if metadata["applied_voltage_V"] > 20000:
            errors.append("applied_voltage_V > 20 kV may be dangerous (verify)")

    if "flow_rate_uL_per_min" in metadata:
        if metadata["flow_rate_uL_per_min"] < 0:
            errors.append("flow_rate_uL_per_min must be non-negative")

    # Consistency checks
    if "needle_outer_diameter_mm" in metadata and "needle_inner_diameter_mm" in metadata:
        if metadata["needle_inner_diameter_mm"] >= metadata["needle_outer_diameter_mm"]:
            errors.append("needle_inner_diameter must be less than outer_diameter")

    if "regime_classification" in metadata:
        valid_regimes = ["no_cone", "unstable", "stable", "spray"]
        if metadata["regime_classification"] not in valid_regimes:
            errors.append(f"regime_classification must be one of {valid_regimes}")

    return len(errors) == 0, errors


def save_metadata(metadata: TrialMetadata, output_path: Path) -> None:
    """Write metadata to JSON file.

    Parameters
    ----------
    metadata : TrialMetadata
        Metadata object to save
    output_path : Path
        Output file path

    Notes
    -----
    Saves as formatted JSON with 2-space indentation.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(asdict(metadata), f, indent=2)


def load_metadata_typed(metadata_path: Path) -> TrialMetadata:
    """Load metadata from JSON and convert to typed dataclass.

    Parameters
    ----------
    metadata_path : Path
        Path to metadata JSON file

    Returns
    -------
    TrialMetadata
        Typed metadata object

    Raises
    ------
    FileNotFoundError
        If metadata file does not exist
    ValueError
        If metadata validation fails
    """
    with open(metadata_path, 'r') as f:
        data = json.load(f)

    # Validate
    is_valid, errors = validate_metadata(data)
    if not is_valid:
        raise ValueError(f"Metadata validation failed:\n" + "\n".join(errors))

    # Convert to dataclass
    return TrialMetadata(**data)
