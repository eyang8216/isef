"""Gaussian space-charge shielding for Version 1."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .config import PhysicalParams, SolverParams, SpaceChargeParams
from .electrostatics import solve_laplace, solve_poisson
from .fields import compute_electric_field
from .geometry import GeometryMasks
from .grid import AxisymmetricGrid


def gaussian_charge_density(grid: AxisymmetricGrid, params: SpaceChargeParams) -> np.ndarray:
    """Return prescribed Gaussian `rho_e(r,z)` on the grid."""
    params.validate()
    if params.model != "gaussian":
        return np.zeros(grid.shape, dtype=float)
    R, Z = grid.R, grid.Z
    return params.rho0 * np.exp(-((R - params.apex_r) ** 2 + (Z - params.apex_z) ** 2) / (2.0 * params.ell ** 2))


def shielding_metric(E_shielded: np.ndarray, E_reference: np.ndarray, mask: np.ndarray | None = None) -> float:
    """Return `1 - max(E_shielded)/max(E_reference)` over an optional ROI.

    A global maximum can be dominated by electrode corners or artificial far
    boundaries. Passing an apex-local `mask` makes the metric more physically
    meaningful for shielding studies.
    """
    E_shielded = np.asarray(E_shielded, dtype=float)
    E_reference = np.asarray(E_reference, dtype=float)
    if E_shielded.shape != E_reference.shape:
        raise ValueError("E_shielded and E_reference must have matching shapes")
    if mask is not None:
        mask = np.asarray(mask, dtype=bool)
        if mask.shape != E_reference.shape:
            raise ValueError("mask must match field shape")
        if not np.any(mask):
            raise ValueError("mask must include at least one node")
        E_s = E_shielded[mask]
        E_r = E_reference[mask]
    else:
        E_s = E_shielded
        E_r = E_reference
    ref = float(np.max(E_r))
    if ref == 0.0:
        return float("nan")
    return 1.0 - float(np.max(E_s)) / ref


@dataclass(frozen=True)
class SpaceChargeResult:
    phi: np.ndarray
    rho_e: np.ndarray
    Er: np.ndarray
    Ez: np.ndarray
    E_mag: np.ndarray
    iterations: int
    converged: bool
    history: list[dict[str, float]] = field(default_factory=list)
    shielding_metric: float | None = None


def solve_gaussian_shielding(
    grid: AxisymmetricGrid,
    masks: GeometryMasks,
    physical: PhysicalParams,
    params: SpaceChargeParams,
    solver: SolverParams | None = None,
) -> SpaceChargeResult:
    """Solve a prescribed/relaxed Gaussian Poisson shielding case.

    The Gaussian closure is prescribed by position/scale, but we still use the
    fixed-point/under-relaxation structure specified for Version 1 so later
    nonlinear closures can share the same convergence machinery.
    """
    params.validate()
    solver = solver or SolverParams()
    rho_target = gaussian_charge_density(grid, params)
    rho = np.zeros_like(rho_target)
    phi_prev = None
    peak_prev = None
    history: list[dict[str, float]] = []
    converged = False

    for it in range(1, params.max_iterations + 1):
        rho_next = (1.0 - params.relaxation) * rho + params.relaxation * rho_target
        phi = solve_poisson(grid, masks, physical, rho_next, solver=solver)
        Er, Ez, E_mag = compute_electric_field(grid, phi)
        peak = float(np.max(E_mag))
        rho_rel = _relative_norm(rho_next - rho, rho_next)
        phi_rel = np.inf if phi_prev is None else _relative_norm(phi - phi_prev, phi)
        peak_rel = np.inf if peak_prev is None else abs(peak - peak_prev) / max(abs(peak), 1e-300)
        history.append({"iteration": float(it), "rho_rel": rho_rel, "phi_rel": phi_rel, "peak_rel": peak_rel, "peak_E": peak})
        rho = rho_next
        phi_prev = phi
        peak_prev = peak
        if it > 1 and rho_rel < params.tolerance and phi_rel < params.tolerance and peak_rel < params.tolerance:
            converged = True
            break

    phi_laplace = solve_laplace(grid, masks, physical, solver=solver)
    _, _, E_laplace = compute_electric_field(grid, phi_laplace)
    metric = shielding_metric(E_mag, E_laplace)
    return SpaceChargeResult(phi=phi, rho_e=rho, Er=Er, Ez=Ez, E_mag=E_mag, iterations=it, converged=converged, history=history, shielding_metric=metric)


def _relative_norm(delta: np.ndarray, ref: np.ndarray) -> float:
    return float(np.linalg.norm(delta.ravel()) / max(np.linalg.norm(ref.ravel()), 1e-300))
