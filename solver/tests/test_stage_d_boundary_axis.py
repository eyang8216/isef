import numpy as np

from solver.config import GridParams, PhysicalParams
from solver.grid import AxisymmetricGrid
from solver.operators import build_axisymmetric_laplacian
from solver.boundary_conditions import apply_dirichlet_conditions
from solver.geometry import GeometryMasks, rectangular_electrodes


def test_axisymmetric_laplacian_axis_row_has_regularized_center_coefficient():
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=5, nz=5))
    A = build_axisymmetric_laplacian(grid).toarray()
    row = A[grid.idx(0, 2)]
    assert row[grid.idx(0, 2)] == -4.0 / grid.dr**2 - 2.0 / grid.dz**2
    assert row[grid.idx(1, 2)] == 4.0 / grid.dr**2
    assert row[grid.idx(0, 1)] == 1.0 / grid.dz**2
    assert row[grid.idx(0, 3)] == 1.0 / grid.dz**2


def test_boundary_masks_have_explicit_precedence_for_overlapping_faces():
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=5, nz=5))
    masks = rectangular_electrodes(grid, powered="z_min", ground="z_max", far_dirichlet=True)
    # Deliberately overlap a powered corner with the far-boundary mask.
    # The current API documents powered/conductor precedence over far values.
    A = build_axisymmetric_laplacian(grid)
    A_bc, b = apply_dirichlet_conditions(A, np.zeros(grid.size), grid, masks, PhysicalParams(V0=7.0), far_value=3.0)
    corner = grid.idx(0, 0)
    row = A_bc.getrow(corner).toarray().ravel()
    assert np.count_nonzero(row) == 1
    assert b[corner] == 7.0
