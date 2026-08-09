import numpy as np
import pytest

from solver.config import GridParams, PhysicalParams, SpaceChargeParams
from solver.electrostatics import solve_laplace
from solver.fields import compute_electric_field
from solver.geometry import rectangular_electrodes
from solver.grid import AxisymmetricGrid
from solver.interface import straight_cone_interface
from solver.optimization import ConeShapeBounds, OptimizationResult, optimize_cone_shape
from solver.residual import compute_residual


@pytest.fixture
def small_setup():
    """Minimal grid and masks for fast optimizer tests."""
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=25, nz=41))
    masks = rectangular_electrodes(grid, powered="z_max", ground="z_min", far_dirichlet=True)
    physical = PhysicalParams(V0=1000.0, gamma=0.022)
    return grid, masks, physical


def test_optimize_cone_shape_returns_result(small_setup):
    """optimize_cone_shape returns an OptimizationResult with finite fields."""
    grid, masks, physical = small_setup
    result = optimize_cone_shape(grid, masks, physical, n_interface=21)
    assert isinstance(result, OptimizationResult)
    assert np.isfinite(result.half_angle_deg)
    assert np.isfinite(result.rms_residual)
    assert result.n_evals > 0


def test_optimized_angle_within_bounds(small_setup):
    """Optimized half-angle must stay within the box bounds."""
    grid, masks, physical = small_setup
    bounds = ConeShapeBounds(half_angle_deg_min=5.0, half_angle_deg_max=85.0)
    result = optimize_cone_shape(grid, masks, physical, bounds=bounds, n_interface=21)
    assert bounds.half_angle_deg_min <= result.half_angle_deg <= bounds.half_angle_deg_max
    assert bounds.apex_radius_min <= result.apex_radius <= bounds.apex_radius_max


def test_optimizer_converges_to_lower_residual_than_bad_start():
    """Optimizer must find a meaningfully lower residual than a deliberately poor starting angle.

    This verifies the Powell loop is functioning and not stuck, without overclaiming
    the exact angle a rectangular-electrode domain will produce (which is not 49.3° —
    that validation belongs in the example script with a proper conical geometry).
    """
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=25, nz=41))
    masks = rectangular_electrodes(grid, powered="z_max", ground="z_min", far_dirichlet=True)
    physical = PhysicalParams(V0=1000.0, gamma=0.022)

    phi = solve_laplace(grid, masks, physical)
    Er, Ez, _ = compute_electric_field(grid, phi)

    # Evaluate residual at a known poor angle (5°) as baseline
    poor_iface = straight_cone_interface(z_min=0.1, z_max=0.9, apex_z=0.9, half_angle_deg=5.0, n=21)
    diag_poor = compute_residual(grid, poor_iface, Er, Ez, physical)

    result = optimize_cone_shape(
        grid, masks, physical,
        n_interface=21,
        initial_half_angle_deg=5.0,  # start at the poor angle
        powell_options={"maxiter": 300, "ftol": 1e-8},
    )
    assert result.rms_residual < diag_poor.rms_residual, (
        f"Optimizer did not improve over poor starting angle: "
        f"start={diag_poor.rms_residual:.4e} optimized={result.rms_residual:.4e}"
    )
    assert result.n_evals > 1  # optimizer actually ran


def test_coupled_optimizer_differs_from_laplace_only(small_setup):
    """Coupled threshold optimizer must produce a different RMS residual than Laplace-only.

    The threshold Poisson field differs from the pure Laplace field when charge
    activates above E_c, shifting the residual landscape. This confirms the coupling
    is exercised, not silently bypassed.
    """
    grid, masks, physical = small_setup

    # E_c well below the interior Laplace peak so charge activates meaningfully
    sc_params = SpaceChargeParams(
        model="threshold",
        E_c=500.0,
        E_s=300.0,
        rho_max=1e-8,
        relaxation=0.5,
        tolerance=1e-6,
        max_iterations=40,
    )

    result_laplace = optimize_cone_shape(
        grid, masks, physical,
        n_interface=21,
        powell_options={"maxiter": 100, "ftol": 1e-6},
    )
    result_coupled = optimize_cone_shape(
        grid, masks, physical,
        sc_params=sc_params,
        n_interface=21,
        powell_options={"maxiter": 100, "ftol": 1e-6},
    )

    # Laplace-only result must carry None inner-loop fields
    assert result_laplace.sc_converged is None
    assert result_laplace.sc_iterations is None

    # The two runs must produce different residuals (space charge changes the field)
    assert result_coupled.rms_residual != result_laplace.rms_residual, (
        "Coupled and Laplace-only optimizer produced identical residuals — "
        "threshold space charge is not being applied"
    )


def test_optimizer_reduces_residual_vs_initial(small_setup):
    """Optimizer must find a shape with lower RMS residual than the starting point."""
    grid, masks, physical = small_setup
    phi = solve_laplace(grid, masks, physical)
    Er, Ez, _ = compute_electric_field(grid, phi)

    initial_angle = 45.0
    initial_iface = straight_cone_interface(
        z_min=0.1, z_max=0.9, apex_z=0.9,
        half_angle_deg=initial_angle, n=21,
    )
    diag_initial = compute_residual(grid, initial_iface, Er, Ez, physical)

    result = optimize_cone_shape(
        grid, masks, physical,
        n_interface=21,
        initial_half_angle_deg=initial_angle,
    )
    assert result.rms_residual <= diag_initial.rms_residual, (
        f"Optimizer made residual worse: initial={diag_initial.rms_residual:.4e} "
        f"optimized={result.rms_residual:.4e}"
    )


def test_immersed_optimizer_rebuilds_field_and_improves_initial_candidate(small_setup):
    """Immersed mode solves a candidate-dependent boundary, without angle overclaim."""
    grid, masks, physical = small_setup
    result = optimize_cone_shape(
        grid, masks, physical,
        immersed_mode=True,
        apex_z=0.86,
        z_min_interface=0.15,
        z_max_interface=0.85,
        n_interface=25,
        initial_half_angle_deg=35.0,
        initial_apex_radius=0.06,
        bounds=ConeShapeBounds(10.0, 55.0, 0.03, 0.10),
        powell_options={"maxiter": 40, "ftol": 1e-5, "xtol": 1e-3},
    )
    assert result.immersed_mode
    assert result.field_variation is not None and result.field_variation > 0.0
    assert result.initial_rms_residual is not None
    assert result.rms_residual <= result.initial_rms_residual
    assert result.nozzle_radius > result.apex_radius
    assert result.candidate_solve_failures < result.n_evals
