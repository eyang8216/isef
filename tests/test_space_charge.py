import numpy as np

from solver.config import GridParams, SpaceChargeParams
from solver.grid import AxisymmetricGrid
from solver.space_charge import gaussian_charge_density, shielding_metric


def test_gaussian_charge_peak_and_decay():
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=-1.0, z_max=1.0, nr=51, nz=51))
    params = SpaceChargeParams(model="gaussian", rho0=2.0, ell=0.2, apex_r=0.0, apex_z=0.0)
    rho = gaussian_charge_density(grid, params)
    assert rho.shape == grid.shape
    assert np.isclose(rho[0, 25], 2.0)
    assert rho[-1, 0] < 1e-5



def test_gaussian_relaxed_solver_converges_to_prescribed_cloud():
    from solver.config import PhysicalParams
    from solver.geometry import rectangular_electrodes
    from solver.space_charge import solve_gaussian_shielding

    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=17, nz=17))
    masks = rectangular_electrodes(grid, powered="z_max", ground="z_min", far_dirichlet=True)
    params = SpaceChargeParams(
        model="gaussian",
        rho0=1e-10,
        ell=0.2,
        apex_r=0.0,
        apex_z=0.5,
        relaxation=0.8,
        tolerance=1e-7,
        max_iterations=50,
    )
    result = solve_gaussian_shielding(grid, masks, PhysicalParams(V0=10.0), params)
    target = gaussian_charge_density(grid, params)
    assert result.converged
    assert result.iterations < params.max_iterations
    assert np.linalg.norm((result.rho_e - target).ravel()) / np.linalg.norm(target.ravel()) < 1e-6



def test_shielding_metric_can_use_apex_local_mask():
    ref = np.array([[10.0, 2.0], [3.0, 100.0]])
    shielded = np.array([[5.0, 1.0], [2.0, 100.0]])
    mask = np.array([[True, True], [False, False]])
    assert shielding_metric(shielded, ref) == 0.0  # global max unchanged
    assert shielding_metric(shielded, ref, mask=mask) == 0.5


def test_threshold_shielding_reduces_apex_field():
    """Threshold closure with sensible params must produce S_E > 0 (field reduced) in the interior.

    The global peak is always at the Dirichlet-enforced electrode boundary, so the
    shielding metric must be evaluated over an interior mask to measure the physical
    effect of the space charge on the interior field.
    """
    from solver.config import PhysicalParams
    from solver.geometry import rectangular_electrodes
    from solver.electrostatics import solve_laplace
    from solver.fields import compute_electric_field
    from solver.space_charge import solve_threshold_shielding

    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=21, nz=21))
    masks = rectangular_electrodes(grid, powered="z_max", ground="z_min", far_dirichlet=True)
    physical = PhysicalParams(V0=1000.0)

    # rho_max=1e-8 C/m³: perturbation ~1 V on 1000 V domain — physically gentle, measurable
    # E_c=500 V/m is below the interior Laplace peak (~9883 V/m) so charge activates
    params = SpaceChargeParams(
        model="threshold",
        E_c=500.0,
        E_s=300.0,
        rho_max=1e-8,
        relaxation=0.5,
        tolerance=1e-7,
        max_iterations=80,
    )
    result = solve_threshold_shielding(grid, masks, physical, params)
    assert result.converged

    # Reference Laplace field for the interior metric
    phi_laplace = solve_laplace(grid, masks, physical)
    _, _, E_laplace = compute_electric_field(grid, phi_laplace)

    # Evaluate shielding over interior nodes only — boundary values are Dirichlet-fixed
    interior = np.zeros(grid.shape, dtype=bool)
    interior[1:-1, 1:-1] = True
    s_interior = shielding_metric(result.E_mag, E_laplace, mask=interior)

    assert s_interior > 0, (
        f"Expected interior S_E > 0 (field reduced vs Laplace), got {s_interior:.6f}"
    )
