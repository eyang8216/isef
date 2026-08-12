"""Boundary-condition row replacement for sparse systems."""

from __future__ import annotations

import numpy as np
from scipy.sparse import lil_matrix, spmatrix

from .config import PhysicalParams
from .geometry import GeometryMasks
from .grid import AxisymmetricGrid


def _set_dirichlet_row(A: lil_matrix, b: np.ndarray, k: int, value: float) -> None:
    A.rows[k] = [k]
    A.data[k] = [1.0]
    b[k] = value


def apply_dirichlet_conditions(
    A: spmatrix,
    b: np.ndarray,
    grid: AxisymmetricGrid,
    masks: GeometryMasks,
    physical: PhysicalParams,
    far_value: float | None = None,
) -> tuple[spmatrix, np.ndarray]:
    """Apply Dirichlet rows for named geometry masks.

    Precedence is:

    1. grounded electrode nodes at 0 V,
    2. optional far-boundary nodes at `far_value` if supplied,
    3. powered/conductor nodes at `physical.V0`.

    Thus a powered corner remains powered even if it also lies on the far
    boundary. The symmetry axis is not Dirichlet unless it intersects an
    electrode mask.
    """
    A_lil = A.tolil(copy=True)
    b = np.asarray(b, dtype=float).copy()
    if b.size != grid.size:
        raise ValueError(f"RHS size {b.size} does not match grid size {grid.size}")

    powered = masks.powered | masks.conductor

    for i, j in zip(*np.nonzero(masks.grounded)):
        _set_dirichlet_row(A_lil, b, grid.idx(int(i), int(j)), 0.0)

    if far_value is not None:
        far_only = masks.far_boundary & ~masks.grounded & ~powered
        for i, j in zip(*np.nonzero(far_only)):
            _set_dirichlet_row(A_lil, b, grid.idx(int(i), int(j)), float(far_value))

    for i, j in zip(*np.nonzero(powered)):
        _set_dirichlet_row(A_lil, b, grid.idx(int(i), int(j)), physical.V0)

    return A_lil.tocsr(), b



def apply_dirichlet_values(
    A: spmatrix,
    b: np.ndarray,
    grid: AxisymmetricGrid,
    mask: np.ndarray,
    values: np.ndarray | float,
) -> tuple[spmatrix, np.ndarray]:
    """Apply arbitrary Dirichlet values on `mask`.

    This is used for manufactured-solution verification where boundary values
    are not simply 0 or V0.
    """
    mask = np.asarray(mask, dtype=bool)
    if mask.shape != grid.shape:
        raise ValueError(f"mask shape {mask.shape} does not match grid shape {grid.shape}")
    if np.isscalar(values):
        value_array = np.full(grid.shape, float(values), dtype=float)
    else:
        value_array = np.asarray(values, dtype=float)
        if value_array.shape != grid.shape:
            raise ValueError(f"values shape {value_array.shape} does not match grid shape {grid.shape}")
    A_lil = A.tolil(copy=True)
    b = np.asarray(b, dtype=float).copy()
    for i, j in zip(*np.nonzero(mask)):
        _set_dirichlet_row(A_lil, b, grid.idx(int(i), int(j)), float(value_array[i, j]))
    return A_lil.tocsr(), b
