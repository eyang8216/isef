"""Young-Laplace-Maxwell residual diagnostics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import PhysicalParams
from .fields import interpolate_field_to_points
from .grid import AxisymmetricGrid
from .interface import GraphInterface


@dataclass(frozen=True)
class ResidualDiagnostics:
    E_n: np.ndarray
    maxwell_pressure: np.ndarray
    capillary_pressure: np.ndarray
    delta_p: float
    residual: np.ndarray
    rms_residual: float
    max_abs_residual: float
    mean_residual: float
    half_angle_deg: float
    peak_field: float
    peak_maxwell_pressure: float


def compute_residual(
    grid: AxisymmetricGrid,
    interface: GraphInterface,
    Er: np.ndarray,
    Ez: np.ndarray,
    physical: PhysicalParams,
    delta_p: float | None = None,
    E_n_override: np.ndarray | None = None,
    sample_mask: np.ndarray | None = None,
) -> ResidualDiagnostics:
    """Compute Maxwell/capillary pressures and residual on a graph interface.

    ``E_n_override`` supplies a one-sided gas field evaluated directly on an
    immersed conductor. ``sample_mask`` excludes unresolved cap/end regions
    from pressure fitting and scalar diagnostics while preserving full arrays.
    """
    Er_i, Ez_i = interpolate_field_to_points(grid, Er, Ez, interface.r, interface.z)
    n_r, n_z = interface.normals()
    if E_n_override is None:
        E_n = Er_i * n_r + Ez_i * n_z
    else:
        E_n = np.asarray(E_n_override, dtype=float)
        if E_n.shape != interface.z.shape or not np.all(np.isfinite(E_n)):
            raise ValueError("E_n_override must be finite and match the interface")
    if sample_mask is None:
        use = np.ones(interface.z.shape, dtype=bool)
    else:
        use = np.asarray(sample_mask, dtype=bool)
        if use.shape != interface.z.shape or np.count_nonzero(use) < 2:
            raise ValueError("sample_mask must match the interface and select at least two points")
    p_E = 0.5 * physical.eps_g * E_n * E_n
    p_gamma = physical.gamma * interface.curvature()
    weights = interface.arclength_weights()
    if delta_p is None:
        delta_p = float(np.average((p_gamma - p_E)[use], weights=weights[use]))
    residual = p_gamma - delta_p - p_E
    rms = float(np.sqrt(np.average(residual[use] * residual[use], weights=weights[use])))
    return ResidualDiagnostics(
        E_n=E_n,
        maxwell_pressure=p_E,
        capillary_pressure=p_gamma,
        delta_p=float(delta_p),
        residual=residual,
        rms_residual=rms,
        max_abs_residual=float(np.max(np.abs(residual[use]))),
        mean_residual=float(np.average(residual[use], weights=weights[use])),
        half_angle_deg=interface.half_angle_deg(),
        peak_field=float(np.max(np.sqrt(Er_i[use] * Er_i[use] + Ez_i[use] * Ez_i[use]))) if E_n_override is None else float(np.max(np.abs(E_n[use]))),
        peak_maxwell_pressure=float(np.max(p_E[use])),
    )
