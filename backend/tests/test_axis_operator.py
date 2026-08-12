import numpy as np

from solver.config import GridParams
from solver.grid import AxisymmetricGrid
from solver.operators import build_axisymmetric_laplacian


def test_axisymmetric_operator_matches_quadratic_interior_and_axis():
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=-0.5, z_max=0.5, nr=21, nz=23))
    A = build_axisymmetric_laplacian(grid)
    phi = grid.flatten(grid.R**2 + grid.Z**2)
    lap = grid.unflatten(A @ phi)

    # Avoid artificial one-sided placeholder rows on outer/far boundaries.
    interior = np.zeros(grid.shape, dtype=bool)
    interior[:, 1:-1] = True
    interior[:-1, :] &= True
    interior[-1, :] = False
    interior[:, 0] = False
    interior[:, -1] = False

    assert np.max(np.abs(lap[interior] - 6.0)) < 1e-10
    # Specifically confirm axis interior rows use the regularized 2*phi_rr limit.
    assert np.max(np.abs(lap[0, 1:-1] - 6.0)) < 1e-10


def test_operator_is_sparse_and_linear_size():
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=30, nz=40))
    A = build_axisymmetric_laplacian(grid)
    assert A.shape == (grid.size, grid.size)
    assert A.nnz < 6 * grid.size



def test_poisson_rhs_sign_matches_equation():
    from solver.config import EPS0
    from solver.operators import poisson_rhs

    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=5, nz=5))
    # If rho_e = -eps0 * 6, Poisson equation gives laplacian(phi) = 6.
    rho = np.full(grid.shape, -EPS0 * 6.0)
    rhs = grid.unflatten(poisson_rhs(grid, rho, EPS0))
    assert np.allclose(rhs, 6.0)
