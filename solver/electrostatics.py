"""High-level Laplace/Poisson solve entry points."""

from __future__ import annotations

import numpy as np
from scipy.sparse.linalg import spsolve

from .boundary_conditions import apply_dirichlet_conditions
from .config import PhysicalParams, SolverParams
from .geometry import GeometryMasks
from .grid import AxisymmetricGrid
from .operators import build_axisymmetric_laplacian, poisson_rhs


def solve_electrostatics(
    grid: AxisymmetricGrid,
    masks: GeometryMasks,
    physical: PhysicalParams,
    solver: SolverParams | None = None,
    rho_e: np.ndarray | None = None,
    far_value: float | None = None,
) -> np.ndarray:
    """Solve axisymmetric Laplace/Poisson equation and return `phi[nr,nz]`."""
    solver = solver or SolverParams()
    if solver.linear_solver != "spsolve":
        raise NotImplementedError("Version 1 supports only scipy.sparse.linalg.spsolve")
    A = build_axisymmetric_laplacian(grid)
    b = poisson_rhs(grid, rho_e, physical.eps_g)
    A, b = apply_dirichlet_conditions(A, b, grid, masks, physical, far_value=far_value)
    phi = spsolve(A, b)
    return grid.unflatten(phi)


def solve_laplace(
    grid: AxisymmetricGrid,
    masks: GeometryMasks,
    physical: PhysicalParams,
    solver: SolverParams | None = None,
    far_value: float | None = None,
) -> np.ndarray:
    return solve_electrostatics(grid, masks, physical, solver, rho_e=None, far_value=far_value)


def solve_poisson(
    grid: AxisymmetricGrid,
    masks: GeometryMasks,
    physical: PhysicalParams,
    rho_e: np.ndarray,
    solver: SolverParams | None = None,
    far_value: float | None = None,
) -> np.ndarray:
    return solve_electrostatics(grid, masks, physical, solver, rho_e=rho_e, far_value=far_value)
