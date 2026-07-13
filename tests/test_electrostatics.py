import numpy as np

from solver.config import GridParams, PhysicalParams
from solver.electrostatics import solve_laplace
from solver.fields import compute_electric_field
from solver.geometry import rectangular_electrodes
from solver.grid import AxisymmetricGrid


def test_voltage_scaling_for_parallel_plate_laplace_case():
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=25, nz=25))
    masks = rectangular_electrodes(grid, powered="z_max", ground="z_min", far_dirichlet=False)
    phi1 = solve_laplace(grid, masks, PhysicalParams(V0=1.0))
    phi2 = solve_laplace(grid, masks, PhysicalParams(V0=2.0))
    _, _, E1 = compute_electric_field(grid, phi1)
    _, _, E2 = compute_electric_field(grid, phi2)
    interior = E1[1:-1, 1:-1]
    ratio = E2[1:-1, 1:-1] / interior
    assert np.max(np.abs(ratio - 2.0)) < 1e-10
