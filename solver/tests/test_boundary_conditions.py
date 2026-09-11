import numpy as np

from solver.boundary_conditions import apply_dirichlet_values
from solver.config import GridParams
from solver.grid import AxisymmetricGrid
from solver.operators import build_axisymmetric_laplacian


def test_arbitrary_dirichlet_rows_are_identity_and_rhs_value():
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=5, nz=6))
    A = build_axisymmetric_laplacian(grid)
    b = np.zeros(grid.size)
    mask = np.zeros(grid.shape, dtype=bool)
    mask[2, 3] = True
    values = np.zeros(grid.shape)
    values[2, 3] = 12.5

    A_bc, b_bc = apply_dirichlet_values(A, b, grid, mask, values)
    row = A_bc.getrow(grid.idx(2, 3))
    assert row.nnz == 1
    assert row.indices[0] == grid.idx(2, 3)
    assert row.data[0] == 1.0
    assert b_bc[grid.idx(2, 3)] == 12.5



def test_far_value_applies_without_overriding_powered_boundary():
    from solver.boundary_conditions import apply_dirichlet_conditions
    from solver.config import PhysicalParams
    from solver.geometry import rectangular_electrodes

    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=5, nz=6))
    masks = rectangular_electrodes(grid, powered="z_max", ground="z_min", far_dirichlet=False)
    A = build_axisymmetric_laplacian(grid)
    b = np.zeros(grid.size)
    A_bc, b_bc = apply_dirichlet_conditions(A, b, grid, masks, PhysicalParams(V0=10.0), far_value=3.0)
    assert b_bc[grid.idx(4, 2)] == 3.0  # r_max far boundary
    assert b_bc[grid.idx(4, 5)] == 10.0  # powered corner wins
    assert b_bc[grid.idx(4, 0)] == 0.0  # grounded corner wins over far value
    for i, j, val in [(4, 2, 3.0), (4, 5, 10.0), (4, 0, 0.0)]:
        row = A_bc.getrow(grid.idx(i, j))
        assert row.nnz == 1
        assert row.indices[0] == grid.idx(i, j)
        assert row.data[0] == 1.0
