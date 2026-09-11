import numpy as np
import pytest

from solver.config import GridParams, PhysicalParams
from solver.grid import AxisymmetricGrid
from solver.interface import GraphInterface
from solver.residual import compute_residual


def _grid():
    return AxisymmetricGrid.from_params(
        GridParams(r_max=2.0, z_min=0.0, z_max=2.0, nr=41, nz=41)
    )


def test_graph_interface_curvature_for_cylinder():
    z = np.linspace(0.3, 1.7, 101)
    radius = 0.7
    interface = GraphInterface(z=z, R=np.full_like(z, radius))
    curvature = interface.curvature()
    assert np.allclose(curvature[2:-2], 1.0 / radius, atol=1e-10)


def test_graph_interface_curvature_for_linear_flank():
    z = np.linspace(0.3, 1.7, 101)
    slope = 0.8
    intercept = 0.4
    interface = GraphInterface(z=z, R=intercept + slope * z)
    expected = 1.0 / (interface.R * np.sqrt(1.0 + slope**2))
    assert np.allclose(interface.curvature()[2:-2], expected[2:-2], rtol=1e-10, atol=1e-10)


def test_residual_prescribed_pressure_is_not_mean_projected():
    grid = _grid()
    z = np.linspace(0.4, 1.6, 31)
    interface = GraphInterface(z=z, R=np.full_like(z, 0.5))
    er = np.zeros(grid.shape)
    ez = np.zeros(grid.shape)
    physical = PhysicalParams(gamma=0.022)
    diag = compute_residual(grid, interface, er, ez, physical, delta_p=0.0)
    assert diag.delta_p == 0.0
    assert diag.mean_residual > 0.0
    assert diag.rms_residual > 0.0


def test_residual_pressure_projection_zeroes_weighted_mean():
    grid = _grid()
    z = np.linspace(0.4, 1.6, 31)
    interface = GraphInterface(z=z, R=np.full_like(z, 0.5))
    er = np.zeros(grid.shape)
    ez = np.zeros(grid.shape)
    diag = compute_residual(grid, interface, er, ez, PhysicalParams(gamma=0.022))
    assert abs(diag.mean_residual) < 1e-12


def test_pressure_projection_sample_mask_only_uses_selected_points():
    grid = _grid()
    z = np.linspace(0.4, 1.6, 31)
    interface = GraphInterface(z=z, R=0.5 + 0.1 * (z - z.mean())**2)
    er = np.zeros(grid.shape)
    ez = np.zeros(grid.shape)
    mask = np.zeros(z.shape, dtype=bool)
    mask[8:-8] = True
    diag = compute_residual(grid, interface, er, ez, PhysicalParams(gamma=0.022), sample_mask=mask)
    assert abs(np.average(diag.residual[mask], weights=interface.arclength_weights()[mask])) < 1e-12
    assert np.all(np.isfinite(diag.residual))


def test_graph_interface_rejects_nonmonotone_z_and_negative_radius():
    with pytest.raises(ValueError):
        GraphInterface(z=np.array([0.0, 0.5, 0.4]), R=np.ones(3))
    with pytest.raises(ValueError):
        GraphInterface(z=np.array([0.0, 0.5, 1.0]), R=np.array([0.2, -0.1, 0.2]))
