"""Space-charge shielding closures: Gaussian (Version 1) and threshold-activated (Version 2)."""

from __future__ import annotations

from collections.abc import Callable
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


def _apex_local_mask(
    grid: AxisymmetricGrid,
    masks: GeometryMasks,
    apex_r: float,
    apex_z: float,
    radius: float,
) -> np.ndarray:
    """Boolean mask of gas nodes within ``radius`` of ``(apex_r, apex_z)``.

    Restricts the shielding metric to the localized region where a Gaussian
    cloud actually acts, excluding Dirichlet boundary nodes whose field is
    pinned by the electrodes and would otherwise dominate the global max.
    """
    gas = np.asarray(masks.gas, dtype=bool)
    dist = np.hypot(grid.R - apex_r, grid.Z - apex_z)
    return gas & (dist <= radius)


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


def _relative_norm(delta: np.ndarray, ref: np.ndarray) -> float:
    return float(np.linalg.norm(delta.ravel()) / max(np.linalg.norm(ref.ravel()), 1e-300))


def _solve_state(
    grid: AxisymmetricGrid,
    masks: GeometryMasks,
    physical: PhysicalParams,
    rho: np.ndarray,
    solver: SolverParams,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    phi = solve_poisson(grid, masks, physical, rho, solver=solver)
    Er, Ez, E_mag = compute_electric_field(grid, phi)
    return phi, Er, Ez, E_mag


def _fixed_point_iterate(
    grid: AxisymmetricGrid,
    masks: GeometryMasks,
    physical: PhysicalParams,
    params: SpaceChargeParams,
    solver: SolverParams,
    charge_update: Callable[[np.ndarray, np.ndarray], np.ndarray],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, bool, list[dict[str, float]]]:
    """Run the shared under-relaxed Poisson fixed-point iteration.

    Each iteration solves Poisson for the current charge, reconstructs the
    field, and asks ``charge_update(rho, E_mag)`` for the next charge state;
    the closure decides how that state depends on the field (a fixed
    prescribed cloud for the Gaussian closure, a nonlinear function of |E|
    for the threshold closure). ``params`` supplies the relaxation weight,
    tolerance, and iteration budget.

    Returns ``(phi, rho, Er, Ez, E_mag, iterations, converged, history)``.
    """
    rho = np.zeros(grid.shape, dtype=float)
    phi_prev = None
    peak_prev = None
    history: list[dict[str, float]] = []
    converged = False

    for it in range(1, params.max_iterations + 1):
        phi, Er, Ez, E_mag = _solve_state(grid, masks, physical, rho, solver)
        rho_next = np.where(masks.gas, charge_update(rho, E_mag), 0.0)
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

    # Re-solve with the accepted charge state so returned fields and rho_e are
    # a self-consistent Poisson state rather than one iteration out of sync.
    phi, Er, Ez, E_mag = _solve_state(grid, masks, physical, rho, solver)
    return phi, rho, Er, Ez, E_mag, it, converged, history


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

    The returned ``shielding_metric`` is evaluated over an apex-local region
    of interest (gas nodes within ``3 * ell`` of the cloud centre), so it is
    positive when the cloud reduces the near-apex field — a global max would
    instead sit on the Dirichlet-fixed electrodes and read ~0.
    """
    params.validate()
    solver = solver or SolverParams()
    rho_target = gaussian_charge_density(grid, params)

    def charge_update(rho: np.ndarray, E_mag: np.ndarray) -> np.ndarray:
        # Relax toward the fixed prescribed cloud; the current field is unused.
        return (1.0 - params.relaxation) * rho + params.relaxation * rho_target

    phi, rho, Er, Ez, E_mag, it, converged, history = _fixed_point_iterate(
        grid, masks, physical, params, solver, charge_update
    )
    phi_laplace = solve_laplace(grid, masks, physical, solver=solver)
    _, _, E_laplace = compute_electric_field(grid, phi_laplace)
    mask = _apex_local_mask(grid, masks, params.apex_r, params.apex_z, 3.0 * params.ell)
    metric = shielding_metric(E_mag, E_laplace, mask=mask) if mask.any() else None
    return SpaceChargeResult(phi=phi, rho_e=rho, Er=Er, Ez=Ez, E_mag=E_mag, iterations=it, converged=converged, history=history, shielding_metric=metric)


def threshold_charge_density(E_mag: np.ndarray, params: SpaceChargeParams) -> np.ndarray:
    """Return threshold-activated charge density for the current field magnitude.

    Nodes where |E| < E_c produce exactly zero charge density.
    """
    params.validate()
    if params.model != "threshold":
        return np.zeros_like(E_mag)
    above = E_mag > params.E_c
    rho = np.zeros_like(E_mag)
    rho[above] = params.rho_max * (1.0 - np.exp(-(E_mag[above] - params.E_c) / params.E_s))
    return rho


def solve_threshold_shielding(
    grid: AxisymmetricGrid,
    masks: GeometryMasks,
    physical: PhysicalParams,
    params: SpaceChargeParams,
    solver: SolverParams | None = None,
) -> SpaceChargeResult:
    """Solve the nonlinear threshold-activated Poisson shielding case.

    Shares the fixed-point under-relaxation machinery with the Gaussian
    closure via `_fixed_point_iterate`; only the charge update differs — here
    rho_e is a nonlinear function of the current |E|, not a prescribed cloud.

    The returned ``shielding_metric`` is evaluated over the gas (interior)
    nodes, excluding the Dirichlet-fixed electrodes, so it is positive when
    the threshold charge reduces the interior field.
    """
    params.validate()
    solver = solver or SolverParams()

    def charge_update(rho: np.ndarray, E_mag: np.ndarray) -> np.ndarray:
        candidate = threshold_charge_density(E_mag, params)
        return (1.0 - params.relaxation) * rho + params.relaxation * candidate

    phi, rho, Er, Ez, E_mag, it, converged, history = _fixed_point_iterate(
        grid, masks, physical, params, solver, charge_update
    )
    phi_laplace = solve_laplace(grid, masks, physical, solver=solver)
    _, _, E_laplace = compute_electric_field(grid, phi_laplace)
    metric = shielding_metric(E_mag, E_laplace, mask=masks.gas) if masks.gas.any() else None
    return SpaceChargeResult(
        phi=phi, rho_e=rho, Er=Er, Ez=Ez, E_mag=E_mag,
        iterations=it, converged=converged, history=history,
        shielding_metric=metric,
    )
