import numpy as np

from solver.config import GridParams, PhysicalParams
from solver.grid import AxisymmetricGrid
from solver.interface import GraphInterface
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
