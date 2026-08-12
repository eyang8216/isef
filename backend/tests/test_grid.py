import numpy as np
import pytest

from solver.config import GridParams
from solver.grid import AxisymmetricGrid


def test_grid_index_roundtrip_and_shape():
    grid = AxisymmetricGrid.from_params(GridParams(r_max=2.0, z_min=-1.0, z_max=3.0, nr=7, nz=9))
    assert grid.shape == (7, 9)
    assert grid.size == 63
    for i in range(grid.nr):
        for j in range(grid.nz):
            k = grid.idx(i, j)
            assert k == i * grid.nz + j
            assert grid.unidx(k) == (i, j)


def test_flatten_unflatten_uses_project_convention():
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=3, nz=4))
    arr = np.arange(grid.size).reshape(grid.shape)
    flat = grid.flatten(arr)
    assert flat.tolist() == list(range(grid.size))
    assert np.array_equal(grid.unflatten(flat), arr)


def test_grid_params_reject_bad_inputs():
    with pytest.raises(ValueError):
        GridParams(r_max=0.0, z_min=0.0, z_max=1.0, nr=3, nz=3)
    with pytest.raises(ValueError):
        GridParams(r_max=1.0, z_min=1.0, z_max=1.0, nr=3, nz=3)
    with pytest.raises(ValueError):
        GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=2, nz=3)
