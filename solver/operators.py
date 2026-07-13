"""Sparse finite-difference/finite-volume axisymmetric operators."""

from __future__ import annotations

import numpy as np
from scipy.sparse import csr_matrix, lil_matrix

from .grid import AxisymmetricGrid


def build_axisymmetric_laplacian(grid: AxisymmetricGrid) -> csr_matrix:
    """Build sparse matrix for `phi_rr + (1/r) phi_r + phi_zz`.

    Boundary rows initially receive the same local stencil where possible; final
    physical boundary conditions are imposed later by `boundary_conditions.py`.
    The symmetry axis `r=0` uses the regularized limit
    `2 phi_rr ≈ 4*(phi[1,j] - phi[0,j]) / dr^2`.
    """
    nr, nz = grid.nr, grid.nz
    dr2 = grid.dr ** 2
    dz2 = grid.dz ** 2
    A = lil_matrix((grid.size, grid.size), dtype=float)

    for i in range(nr):
        r_i = grid.r[i]
        for j in range(nz):
            k = grid.idx(i, j)

            # Radial operator.
            if i == 0:
                A[k, grid.idx(0, j)] += -4.0 / dr2
                A[k, grid.idx(1, j)] += 4.0 / dr2
            elif i == nr - 1:
                # Placeholder one-sided Neumann-like radial second derivative;
                # normally overwritten by far-boundary Dirichlet/Neumann rows.
                A[k, grid.idx(i, j)] += -2.0 / dr2
                A[k, grid.idx(i - 1, j)] += 2.0 / dr2
            else:
                rp = r_i + 0.5 * grid.dr
                rm = r_i - 0.5 * grid.dr
                c_p = rp / (r_i * dr2)
                c_m = rm / (r_i * dr2)
                A[k, grid.idx(i + 1, j)] += c_p
                A[k, grid.idx(i, j)] += -(c_p + c_m)
                A[k, grid.idx(i - 1, j)] += c_m

            # Axial operator.
            if j == 0:
                A[k, grid.idx(i, j)] += -2.0 / dz2
                A[k, grid.idx(i, j + 1)] += 2.0 / dz2
            elif j == nz - 1:
                A[k, grid.idx(i, j)] += -2.0 / dz2
                A[k, grid.idx(i, j - 1)] += 2.0 / dz2
            else:
                A[k, grid.idx(i, j + 1)] += 1.0 / dz2
                A[k, grid.idx(i, j)] += -2.0 / dz2
                A[k, grid.idx(i, j - 1)] += 1.0 / dz2

    return A.tocsr()


def poisson_rhs(grid: AxisymmetricGrid, rho_e: np.ndarray | None, eps: float) -> np.ndarray:
    """Return flattened RHS for `laplacian(phi) = -rho_e/eps`."""
    if rho_e is None:
        return np.zeros(grid.size, dtype=float)
    rho_e = np.asarray(rho_e, dtype=float)
    if rho_e.shape != grid.shape:
        raise ValueError(f"rho_e shape {rho_e.shape} does not match grid shape {grid.shape}")
    return grid.flatten(-rho_e / eps)
