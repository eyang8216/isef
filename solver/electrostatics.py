"""High-level Laplace/Poisson solve entry points."""

from __future__ import annotations

import numpy as np
from scipy.sparse.linalg import spsolve

from .boundary_conditions import apply_dirichlet_conditions
from .config import PhysicalParams, SolverParams
from .geometry import GeometryMasks, ImplicitCone
from .grid import AxisymmetricGrid
from .immersed import apply_immersed_dirichlet
from .operators import build_axisymmetric_laplacian, poisson_rhs


def solve_electrostatics(
    grid: AxisymmetricGrid,
    masks: GeometryMasks,
    physical: PhysicalParams,
    solver: SolverParams | None = None,
    rho_e: np.ndarray | None = None,
    far_value: float | None = None,
    immersed: ImplicitCone | None = None,
) -> np.ndarray:
    """Solve axisymmetric Laplace/Poisson equation and return `phi[nr,nz]`."""
    solver = solver or SolverParams()
    A = build_axisymmetric_laplacian(grid)
    b = poisson_rhs(grid, rho_e, physical.eps_g)
    if immersed is None:
        A, b = apply_dirichlet_conditions(A, b, grid, masks, physical, far_value=far_value)
    else:
        if masks.conductor.shape != grid.shape:
            raise ValueError("immersed masks must match grid")
        # Apply ordinary external boundary values first; the immersed pass then
        # owns the candidate-conductor rows and cut-cell gas rows.
        A, b = apply_dirichlet_conditions(A, b, grid, masks, physical, far_value=far_value)
        A, b = apply_immersed_dirichlet(A, b, grid, immersed, fixed_mask=masks.grounded | masks.powered)
    phi = spsolve(A, b)
    if not np.all(np.isfinite(phi)):
        raise RuntimeError("electrostatic solve returned non-finite potential")
    return grid.unflatten(phi)


def solve_laplace(
    grid: AxisymmetricGrid,
    masks: GeometryMasks,
    physical: PhysicalParams,
    solver: SolverParams | None = None,
    far_value: float | None = None,
    immersed: ImplicitCone | None = None,
) -> np.ndarray:
    return solve_electrostatics(
        grid, masks, physical, solver, rho_e=None, far_value=far_value, immersed=immersed
    )


def solve_poisson(
    grid: AxisymmetricGrid,
    masks: GeometryMasks,
    physical: PhysicalParams,
    rho_e: np.ndarray,
    solver: SolverParams | None = None,
    far_value: float | None = None,
    immersed: ImplicitCone | None = None,
) -> np.ndarray:
    return solve_electrostatics(
        grid, masks, physical, solver, rho_e=rho_e, far_value=far_value, immersed=immersed
    )
