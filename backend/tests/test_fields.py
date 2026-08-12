import numpy as np

from solver.config import GridParams
from solver.fields import compute_electric_field, bilinear_interpolate
from solver.grid import AxisymmetricGrid


def test_field_derivative_signs_for_linear_potential():
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=-1.0, z_max=1.0, nr=21, nz=25))
    phi = 3.0 * grid.R - 2.0 * grid.Z
    Er, Ez, E = compute_electric_field(grid, phi)
    assert np.max(np.abs(Er + 3.0)) < 1e-12
    assert np.max(np.abs(Ez - 2.0)) < 1e-12
    assert np.max(np.abs(E - np.sqrt(13.0))) < 1e-12


def test_bilinear_interpolation_exact_for_linear_field():
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=11, nz=11))
    values = 2.0 * grid.R + 5.0 * grid.Z
    rp = np.array([0.15, 0.33, 0.81])
    zp = np.array([0.22, 0.44, 0.91])
    interp = bilinear_interpolate(grid, values, rp, zp)
    assert np.max(np.abs(interp - (2.0 * rp + 5.0 * zp))) < 1e-12
