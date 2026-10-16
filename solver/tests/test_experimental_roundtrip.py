"""Round-trip test for the imaging and extraction toolkit (``experimental/``).

The toolkit needs the optional imaging dependencies, so the whole module is skipped when
they are absent.  One analytic silhouette is rendered, pushed through the extraction chain,
and checked against the $1^\\circ$ acceptance limit used by
``experiments/methodology/generate_synthetic_validation.py``.
"""

import numpy as np
import pytest

pytest.importorskip("cv2", reason="opencv-python is an optional imaging dependency")
pytest.importorskip("PIL", reason="Pillow is an optional imaging dependency")

from experimental.synthetic_validation import validate_pipeline_accuracy  # noqa: E402

HALF_ANGLE_DEG = 49.29
NEEDLE_RADIUS_MM = 0.4
MM_PER_PIXEL = 0.02
ANGLE_LIMIT_DEG = 1.0


def _cone_profile(half_angle_deg, apex_radius_mm=0.05, cone_length_mm=4.0, n_points=120):
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


def test_roundtrip_recovers_analytic_half_angle():
    r_true, z_true = _cone_profile(HALF_ANGLE_DEG)
    result = validate_pipeline_accuracy(
        r_true,
        z_true,
        HALF_ANGLE_DEG,
        needle_radius_mm=NEEDLE_RADIUS_MM,
        mm_per_pixel=MM_PER_PIXEL,
        noise_levels=[1.3],
    )

    assert not result["failure_messages"], result["failure_messages"]
    angle_error = result["angle_errors_deg"][0]
    assert np.isfinite(angle_error)
    assert angle_error < ANGLE_LIMIT_DEG
    assert result["acceptance_criteria_met"]


def test_metadata_template_and_round_trip(tmp_path):
    """The metadata helpers must emit valid JSON and reload what they saved."""
    import json

    from experimental.metadata import (
        TrialMetadata,
        create_metadata_template,
        load_metadata_typed,
        save_metadata,
        validate_metadata,
    )

    template_path = tmp_path / "metadata_template.json"
    create_metadata_template(template_path)
    template = json.loads(template_path.read_text())
    assert validate_metadata(template) == (True, [])

    metadata = TrialMetadata(
        trial_id="trial_001",
        date="2026-08-20",
        time_start="14:30:00",
        operator="student",
        supervisor="teacher",
        electrode_spacing_mm=10.0,
        needle_outer_diameter_mm=0.8,
        needle_inner_diameter_mm=0.6,
        extractor_geometry="plate",
        extractor_dimensions_mm="50x50",
        liquid_name="ethanol",
        liquid_purity="99.5%",
        liquid_supplier="supplier",
        surface_tension_N_per_m=0.022,
        applied_voltage_V=3000.0,
        flow_rate_uL_per_min=1.0,
        observation_duration_s=10.0,
        camera_model="camera",
        resolution_pixels=(1920, 1080),
        frame_rate_fps=10.0,
        calibration_mm_per_pixel=0.02,
        calibration_method="needle_diameter",
        regime_classification="stable",
    )
    saved_path = tmp_path / "trial.json"
    save_metadata(metadata, saved_path)
    reloaded = load_metadata_typed(saved_path)
    assert reloaded.trial_id == "trial_001"
    assert reloaded.applied_voltage_V == 3000.0
