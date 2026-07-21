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


def test_electrostatics_convergence_order():
    """L2 error must halve (≤0.6×) under 2× grid refinement on the quartic manufactured solution.

    This catches regressions in the axisymmetric operator or boundary-condition
    application at the electrostatics level, independent of the higher-level
    manufactured-Poisson test.
    """
    from solver.verification import run_quartic_manufactured_poisson

    coarse = run_quartic_manufactured_poisson(nr=25, nz=25)
    fine = run_quartic_manufactured_poisson(nr=51, nz=51)  # ≈2× refinement
    ratio = fine.l2_error / coarse.l2_error
    assert ratio <= 0.6, (
        f"Expected L2 error to halve under 2× refinement (ratio ≤ 0.6), got {ratio:.4f} "
        f"(coarse={coarse.l2_error:.3e}, fine={fine.l2_error:.3e})"
    )
