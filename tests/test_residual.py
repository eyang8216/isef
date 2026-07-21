import numpy as np

from solver.config import GridParams, PhysicalParams
from solver.electrostatics import solve_laplace
from solver.fields import compute_electric_field
from solver.geometry import rectangular_electrodes
from solver.grid import AxisymmetricGrid
from solver.interface import GraphInterface, straight_cone_interface
from solver.residual import compute_residual


def test_residual_mean_subtraction_zeroes_constant_capillary_pressure_without_field():
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=21, nz=21))
    Er = np.zeros(grid.shape)
    Ez = np.zeros(grid.shape)
    z = np.linspace(0.2, 0.8, 21)
    interface = GraphInterface(z=z, R=np.full_like(z, 0.25))
    diag = compute_residual(grid, interface, Er, Ez, PhysicalParams(gamma=0.022))
    assert abs(diag.delta_p - 0.022 * 4.0) < 1e-12
    assert diag.rms_residual < 1e-14
    assert diag.max_abs_residual < 1e-14


def test_maxwell_pressure_scales_quadratically_with_field():
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=21, nz=21))
    z = np.linspace(0.2, 0.8, 21)
    interface = GraphInterface(z=z, R=np.full_like(z, 0.25))
    Er = np.ones(grid.shape) * 3.0
    Ez = np.zeros(grid.shape)
    diag1 = compute_residual(grid, interface, Er, Ez, PhysicalParams(gamma=0.022))
    diag2 = compute_residual(grid, interface, 2.0 * Er, Ez, PhysicalParams(gamma=0.022))
    ratio = diag2.peak_maxwell_pressure / diag1.peak_maxwell_pressure
    assert abs(ratio - 4.0) < 1e-12


def test_residual_decreases_toward_better_shaped_interface():
    """A cone interface closer to the equilibrium half-angle must produce a lower RMS residual.

    This confirms the optimizer has a meaningful monotone signal to follow.
    Uses a real Laplace solve so the field and curvature are physically consistent.
    """
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=31, nz=51))
    masks = rectangular_electrodes(grid, powered="z_max", ground="z_min", far_dirichlet=True)
    physical = PhysicalParams(V0=1000.0, gamma=0.022)

    phi = solve_laplace(grid, masks, physical)
    Er, Ez, _ = compute_electric_field(grid, phi)

    # Shared cone geometry — only half_angle_deg varies between the two interfaces
    cone_kwargs = dict(z_min=0.1, z_max=0.9, apex_z=0.9, n=41)
    # Taylor equilibrium is ~49.3°; a cone at 49° is "better" than one at 20°
    interface_good = straight_cone_interface(half_angle_deg=49.0, **cone_kwargs)
    interface_bad = straight_cone_interface(half_angle_deg=20.0, **cone_kwargs)

    diag_good = compute_residual(grid, interface_good, Er, Ez, physical)
    diag_bad = compute_residual(grid, interface_bad, Er, Ez, physical)

    assert diag_good.rms_residual < diag_bad.rms_residual, (
        f"Expected RMS residual to decrease toward equilibrium angle: "
        f"good={diag_good.rms_residual:.4e} bad={diag_bad.rms_residual:.4e}"
    )
