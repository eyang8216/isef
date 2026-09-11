"""Complete experimental validation workflow example.

This script demonstrates the end-to-end pipeline:
1. Generate synthetic Taylor-cone image from solver output
2. Process through image pipeline
3. Extract profile and half-angle
4. Compare with ground truth
5. Validate pipeline accuracy

Run this before conducting real experiments to verify the methodology.
"""

from __future__ import annotations

import numpy as np
from pathlib import Path

# Import experimental modules
from experimental.synthetic_validation import (
    generate_synthetic_image,
    add_realistic_noise,
    validate_pipeline_accuracy,
    plot_synthetic_validation_results,
)
from experimental.image_processing import (
    preprocess_image,
    detect_edges_canny,
    extract_contour,
    smooth_contour,
)
from experimental.profile_extraction import extract_profile_coords
from experimental.comparison import compare_profiles
from experimental.metadata import create_metadata_template, TrialMetadata, save_metadata
from experimental.preregistration import (
    freeze_prediction_package,
    log_frozen_prediction,
    verify_prediction_integrity,
)


def generate_example_cone_profile(
    half_angle_deg: float = 49.3,
    apex_radius_mm: float = 0.05,
    cone_length_mm: float = 5.0,
    n_points: int = 100,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate a simple conical profile with rounded apex.

    Parameters
    ----------
    half_angle_deg : float
        Cone half-angle (degrees)
    apex_radius_mm : float
        Apex cap radius (mm)
    cone_length_mm : float
        Cone length from apex to base (mm)
    n_points : int
        Number of profile points

    Returns
    -------
    r, z : np.ndarray
        Radial and axial coordinates (mm)
    """
    # Generate z coordinates (apex at z=0, base at z=-cone_length)
    z = np.linspace(0, -cone_length_mm, n_points)

    # Conical profile: r = |z| * tan(alpha)
    alpha_rad = np.radians(half_angle_deg)
    r = np.abs(z) * np.tan(alpha_rad)

    # Round the apex (replace with circular cap)
    apex_mask = r < apex_radius_mm
    if np.any(apex_mask):
        # Circular cap: r^2 + (z - z0)^2 = R^2
        # At apex: z0 = R (cap tangent to cone at r=R)
        z_apex = z[apex_mask]
        r[apex_mask] = np.sqrt(apex_radius_mm**2 - (z_apex - apex_radius_mm)**2)

    return r, z


def example_1_synthetic_image_generation():
    """Example 1: Generate synthetic Taylor-cone image."""
    print("\n=== Example 1: Synthetic Image Generation ===")

    # Generate ground-truth profile
    r_true, z_true = generate_example_cone_profile(
        half_angle_deg=49.3,
        apex_radius_mm=0.05,
        cone_length_mm=5.0,
    )

    # Generate synthetic image
    img_clean = generate_synthetic_image(
        r_true, z_true,
        needle_radius_mm=0.4,
        mm_per_pixel=0.02,
    )

    print(f"Generated clean image: shape {img_clean.shape}")

    # Add noise
    img_noisy = add_realistic_noise(
        img_clean,
        gaussian_noise_std=5.0,
        blur_sigma=1.0,
    )

    print(f"Added noise: SNR ≈ {255/5:.1f} (≈{20*np.log10(255/5):.1f} dB)")

    # Save images
    output_dir = Path("backend/results/synthetic_validation")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        from PIL import Image
        Image.fromarray(img_clean).save(output_dir / "synthetic_clean.png")
        Image.fromarray(img_noisy).save(output_dir / "synthetic_noisy.png")
        print(f"Saved images to {output_dir}/")
    except ImportError:
        print("PIL not available, skipping image save")


def example_2_image_processing_pipeline():
    """Example 2: Process synthetic image through pipeline."""
    print("\n=== Example 2: Image Processing Pipeline ===")

    # Generate test image
    r_true, z_true = generate_example_cone_profile(half_angle_deg=49.3)
    img = generate_synthetic_image(r_true, z_true, needle_radius_mm=0.4)
    img_noisy = add_realistic_noise(img, gaussian_noise_std=5.0)

    # Preprocess
    img_preprocessed = preprocess_image(
        img_noisy,
        normalize=True,
        gaussian_sigma=1.0,
    )
    print(f"Preprocessed: shape {img_preprocessed.shape}")

    # Edge detection
    edges = detect_edges_canny(img_preprocessed, low_threshold=50, high_threshold=150)
    print(f"Edge detection: {np.sum(edges > 0)} edge pixels")

    # Extract contour
    try:
        contour = extract_contour(edges)
        print(f"Contour extracted: {len(contour)} points")

        # Smooth
        contour_smooth = smooth_contour(contour, method="savgol", window_length=11)
        print(f"Contour smoothed: {len(contour_smooth)} points")

    except Exception as e:
        print(f"Contour extraction failed: {e}")


def example_3_profile_extraction():
    """Example 3: Extract profile coordinates and measure angle."""
    print("\n=== Example 3: Profile Extraction and Angle Measurement ===")

    # Generate and process image
    r_true, z_true = generate_example_cone_profile(half_angle_deg=49.3)
    img = generate_synthetic_image(r_true, z_true, needle_radius_mm=0.4)
    img_noisy = add_realistic_noise(img, gaussian_noise_std=5.0)

    img_preprocessed = preprocess_image(img_noisy, normalize=True, gaussian_sigma=1.0)
    edges = detect_edges_canny(img_preprocessed)

    try:
        contour = extract_contour(edges)
        contour_smooth = smooth_contour(contour, method="savgol")

        # Extract profile
        profile = extract_profile_coords(
            contour_smooth,
            calibration_mm_per_pixel=0.02,
            axis_orientation="horizontal",
            flank_window_fraction=(0.25, 0.75),
        )

        print(f"Extracted profile: {len(profile.r)} points")
        print(f"Half-angle: {profile.half_angle_deg:.2f}° ± {profile.half_angle_uncertainty_deg:.2f}°")
        print(f"Ground truth: 49.30°")
        print(f"Error: {abs(profile.half_angle_deg - 49.3):.2f}°")
        print(f"Apex position: r={profile.apex_r:.3f} mm, z={profile.apex_z:.3f} mm")
        print(f"Line fit R²: {profile.flank_fit_params['r_squared']:.4f}")

    except Exception as e:
        print(f"Profile extraction failed: {e}")


def example_4_comparison_metrics():
    """Example 4: Compare simulation vs experimental profiles."""
    print("\n=== Example 4: Comparison Metrics ===")

    # Generate "experimental" and "simulated" profiles
    r_exp, z_exp = generate_example_cone_profile(half_angle_deg=49.5, apex_radius_mm=0.06)
    r_sim, z_sim = generate_example_cone_profile(half_angle_deg=49.0, apex_radius_mm=0.05)

    angle_exp = 49.5
    angle_sim = 49.0
    voltage_exp = 3100.0
    voltage_sim = 3000.0

    apex_exp = (0.0, 0.0)
    apex_sim = (0.0, 0.0)

    # Compare
    metrics = compare_profiles(
        r_exp, z_exp, r_sim, z_sim,
        angle_exp, angle_sim,
        voltage_exp, voltage_sim,
        apex_exp, apex_sim,
        alignment_method="apex",
        characteristic_length_mm=10.0,
    )

    print(f"Profile RMSE: {metrics.profile_rmse_mm:.4f} mm")
    print(f"Normalized RMSE: {metrics.profile_nrmse*100:.2f}%")
    print(f"Angle error: {metrics.angle_error_deg:.2f}°")
    print(f"Voltage error: {metrics.voltage_error_frac*100:.1f}%")
    print(f"Comparison points: {metrics.n_comparison_points}")
    print(f"RMSE decomposition:")
    print(f"  Total: {metrics.rmse_decomposition['rmse_total_mm']:.4f} mm")
    print(f"  Apex region: {metrics.rmse_decomposition['rmse_apex_mm']:.4f} mm")
    print(f"  Flank region: {metrics.rmse_decomposition['rmse_flank_mm']:.4f} mm")


def example_5_synthetic_validation():
    """Example 5: Validate pipeline accuracy across noise levels."""
    print("\n=== Example 5: Synthetic Validation ===")

    r_true, z_true = generate_example_cone_profile(half_angle_deg=49.3)
    angle_true = 49.3

    print("Running validation at multiple noise levels...")
    print("(This may take 30-60 seconds)")

    try:
        results = validate_pipeline_accuracy(
            r_true, z_true, angle_true,
            needle_radius_mm=0.4,
            mm_per_pixel=0.02,
            noise_levels=[0.0, 5.0, 10.0, 15.0, 20.0],
        )

        print(f"\nValidation results:")
        print(f"Acceptance criteria met: {results['acceptance_criteria_met']}")
        print(f"Cone length: {results['cone_length_mm']:.2f} mm")
        print(f"\nNoise level | Angle error | Profile RMSE | nRMSE")
        print("-" * 60)
        for i, noise in enumerate(results['noise_levels']):
            angle_err = results['angle_errors_deg'][i]
            rmse = results['profile_rmse_mm'][i]
            nrmse = rmse / results['cone_length_mm'] * 100
            print(f"{noise:11.1f} | {angle_err:11.2f}° | {rmse:12.4f} mm | {nrmse:6.2f}%")

        # Plot results
        output_dir = Path("backend/results/synthetic_validation")
        output_dir.mkdir(parents=True, exist_ok=True)
        plot_path = output_dir / "validation_results.png"

        plot_synthetic_validation_results(results, save_path=str(plot_path))
        print(f"\nValidation plot saved to {plot_path}")

    except Exception as e:
        print(f"Validation failed: {e}")
        import traceback
        traceback.print_exc()


def example_6_metadata_management():
    """Example 6: Create and validate trial metadata."""
    print("\n=== Example 6: Metadata Management ===")

    output_dir = Path("backend/results/experimental_data/metadata")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create template
    template_path = output_dir / "metadata_template.json"
    create_metadata_template(template_path)
    print(f"Created metadata template: {template_path}")

    # Create example metadata
    metadata = TrialMetadata(
        trial_id="example_001",
        date="2026-08-20",
        time_start="14:30:00",
        operator="Student",
        supervisor="Teacher",
        electrode_spacing_mm=10.0,
        needle_outer_diameter_mm=0.8,
        needle_inner_diameter_mm=0.6,
        extractor_geometry="plate",
        extractor_dimensions_mm="50x50",
        liquid_name="ethanol",
        liquid_purity="99.5%",
        liquid_supplier="Lab supplier",
        surface_tension_N_per_m=0.022,
        applied_voltage_V=3000.0,
        flow_rate_uL_per_min=1.0,
        observation_duration_s=10.0,
        camera_model="Example camera",
        resolution_pixels=(1920, 1080),
        frame_rate_fps=10.0,
        calibration_mm_per_pixel=0.02,
        calibration_method="needle_diameter",
        regime_classification="stable",
    )

    metadata_path = output_dir / "example_001_metadata.json"
    save_metadata(metadata, metadata_path)
    print(f"Saved example metadata: {metadata_path}")


def example_7_preregistration_workflow():
    """Example 7: Freeze prediction before viewing experimental data."""
    print("\n=== Example 7: Preregistration Workflow ===")

    # Simulate matched simulation results
    sim_results = {
        "onset_voltage_V": 3000.0,
        "half_angle_deg": 49.2,
        "profile_r": [0.1, 0.2, 0.3],
        "profile_z": [0.0, -1.0, -2.0],
        "residual_rms_Pa": 0.0065,
        "runtime_s": 12.5,
        "grid_used": (121, 177),
        "recovery_method": "exponent_crossing",
    }

    metadata = {"trial_id": "example_001", "electrode_spacing_mm": 10.0}

    output_dir = Path("backend/results/experimental_data/frozen_predictions")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Freeze prediction
    prediction = freeze_prediction_package(
        trial_id="example_001",
        simulation_results=sim_results,
        metadata=metadata,
        output_dir=output_dir,
        git_commit_hash="abc123def456",  # Would be actual git hash
    )

    print(f"Frozen prediction for trial: {prediction.trial_id}")
    print(f"Timestamp: {prediction.timestamp}")
    print(f"Predicted onset voltage: {prediction.predicted_onset_voltage_V:.1f} V")
    print(f"Predicted half-angle: {prediction.predicted_half_angle_deg:.2f}°")
    print(f"SHA-256 hash: {prediction.sha256_hash[:16]}...")

    # Log to audit trail
    log_path = output_dir.parent / "prediction_audit_log.txt"
    log_frozen_prediction(prediction, log_path)
    print(f"Logged to audit trail: {log_path}")

    # Verify integrity
    prediction_path = output_dir / f"{prediction.trial_id}_frozen_prediction.json"
    is_valid = verify_prediction_integrity(prediction_path)
    print(f"Integrity verification: {'PASS' if is_valid else 'FAIL'}")


def main():
    """Run all examples."""
    print("=" * 70)
    print("EXPERIMENTAL VALIDATION WORKFLOW EXAMPLES")
    print("=" * 70)

    try:
        example_1_synthetic_image_generation()
    except Exception as e:
        print(f"Example 1 failed: {e}")

    try:
        example_2_image_processing_pipeline()
    except Exception as e:
        print(f"Example 2 failed: {e}")

    try:
        example_3_profile_extraction()
    except Exception as e:
        print(f"Example 3 failed: {e}")

    try:
        example_4_comparison_metrics()
    except Exception as e:
        print(f"Example 4 failed: {e}")

    try:
        example_5_synthetic_validation()
    except Exception as e:
        print(f"Example 5 failed: {e}")

    try:
        example_6_metadata_management()
    except Exception as e:
        print(f"Example 6 failed: {e}")

    try:
        example_7_preregistration_workflow()
    except Exception as e:
        print(f"Example 7 failed: {e}")

    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
