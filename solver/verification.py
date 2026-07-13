"""Scientific/numerical verification helpers for Version 1."""

from __future__ import annotations

from dataclasses import dataclass
import time

import numpy as np

from .boundary_conditions import apply_dirichlet_values
from .config import EPS0, GridParams, PhysicalParams
from .grid import AxisymmetricGrid
from .operators import build_axisymmetric_laplacian
from scipy.sparse.linalg import spsolve
from scipy import optimize, special


def manufactured_phi(grid: AxisymmetricGrid) -> np.ndarray:
    return grid.R ** 2 + grid.Z ** 2


def manufactured_laplacian(grid: AxisymmetricGrid) -> np.ndarray:
    # Axisymmetric laplacian of r^2 + z^2 is 2 + 2 + 2 = 6.
    return np.full(grid.shape, 6.0, dtype=float)


def manufactured_phi_quartic(grid: AxisymmetricGrid) -> np.ndarray:
    """Nontrivial smooth exact solution for convergence tests.

    phi = r^4 + z^4 + r^2 z^2 has regular axis behavior and an exact
    axisymmetric Laplacian 18 r^2 + 16 z^2. Unlike the quadratic case, the
    second-order discretization is not exact, so grid refinement should reduce
    the error.
    """
    return grid.R**4 + grid.Z**4 + (grid.R**2) * (grid.Z**2)


def manufactured_laplacian_quartic(grid: AxisymmetricGrid) -> np.ndarray:
    return 18.0 * grid.R**2 + 16.0 * grid.Z**2


@dataclass(frozen=True)
class ManufacturedResult:
    nr: int
    nz: int
    l2_error: float
    linf_error: float
    solve_seconds: float
    nnz: int


def run_manufactured_poisson(nr: int, nz: int) -> ManufacturedResult:
    """Solve ∇²phi = 6 with exact Dirichlet boundaries for phi=r²+z²."""
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=-0.5, z_max=0.5, nr=nr, nz=nz))
    A = build_axisymmetric_laplacian(grid)
    b = grid.flatten(manufactured_laplacian(grid))
    exact = manufactured_phi(grid)
    boundary = np.zeros(grid.shape, dtype=bool)
    # Dirichlet on physical outer/far boundaries only. Do NOT overwrite the
    # r=0 axis interior rows: those must exercise the special regularity
    # stencil. Axis corner nodes on z_min/z_max remain Dirichlet via j-boundary.
    boundary[-1, :] = True
    boundary[:, 0] = True
    boundary[:, -1] = True
    A, b = apply_dirichlet_values(A, b, grid, boundary, exact)
    t0 = time.perf_counter()
    numerical = grid.unflatten(spsolve(A, b))
    elapsed = time.perf_counter() - t0
    err = numerical - exact
    interior = np.ones(grid.shape, dtype=bool)
    interior[boundary] = False
    l2 = float(np.sqrt(np.mean(err[interior] ** 2)))
    linf = float(np.max(np.abs(err[interior])))
    return ManufacturedResult(nr=nr, nz=nz, l2_error=l2, linf_error=linf, solve_seconds=elapsed, nnz=int(A.nnz))


def run_quartic_manufactured_poisson(nr: int, nz: int) -> ManufacturedResult:
    """Solve a nontrivial manufactured case and report convergence errors.

    Dirichlet values are imposed on z-min, z-max, and r-max. Interior axis rows
    are left to the regularized axis stencil, so this verifies the coupled
    operator/boundary treatment rather than overwriting r=0 with exact values.
    """
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=-0.5, z_max=0.5, nr=nr, nz=nz))
    A = build_axisymmetric_laplacian(grid)
    b = grid.flatten(manufactured_laplacian_quartic(grid))
    exact = manufactured_phi_quartic(grid)
    boundary = np.zeros(grid.shape, dtype=bool)
    boundary[-1, :] = True
    boundary[:, 0] = True
    boundary[:, -1] = True
    A, b = apply_dirichlet_values(A, b, grid, boundary, exact)
    t0 = time.perf_counter()
    numerical = grid.unflatten(spsolve(A, b))
    elapsed = time.perf_counter() - t0
    err = numerical - exact
    interior = np.ones(grid.shape, dtype=bool)
    interior[boundary] = False
    l2 = float(np.sqrt(np.mean(err[interior] ** 2)))
    linf = float(np.max(np.abs(err[interior])))
    return ManufacturedResult(nr=nr, nz=nz, l2_error=l2, linf_error=linf, solve_seconds=elapsed, nnz=int(A.nnz))


def voltage_scaling_ratio(E1: np.ndarray, E2: np.ndarray, expected: float) -> float:
    """Return median ratio of nonzero field magnitudes, useful for tests."""
    mag1 = np.asarray(E1, dtype=float)
    mag2 = np.asarray(E2, dtype=float)
    mask = mag1 > 1e-14 * max(float(np.max(mag1)), 1.0)
    return float(np.median(mag2[mask] / mag1[mask]) / expected)


def taylor_cone_half_angle_deg() -> float:
    """Compute Taylor's classical cone half-angle from P_{1/2}(cos theta)=0.

    Returns the physical semi-vertical angle alpha = 180 deg - theta0.
    This is an analytical benchmark, not a finite-difference free-boundary
    result.
    """
    f = lambda x: special.lpmv(0, 0.5, x)
    root = optimize.brentq(f, -0.9, -0.2)
    theta0 = np.degrees(np.arccos(root))
    return float(180.0 - theta0)
