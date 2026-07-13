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
) -> ResidualDiagnostics:
    """Compute Maxwell/capillary pressures and residual on a graph interface."""
    Er_i, Ez_i = interpolate_field_to_points(grid, Er, Ez, interface.r, interface.z)
    n_r, n_z = interface.normals()
    E_n = Er_i * n_r + Ez_i * n_z
    p_E = 0.5 * physical.eps_g * E_n * E_n
    p_gamma = physical.gamma * interface.curvature()
    if delta_p is None:
        delta_p = float(np.average(p_gamma - p_E, weights=interface.arclength_weights()))
    residual = p_gamma - delta_p - p_E
    weights = interface.arclength_weights()
    rms = float(np.sqrt(np.average(residual * residual, weights=weights)))
    return ResidualDiagnostics(
        E_n=E_n,
        maxwell_pressure=p_E,
        capillary_pressure=p_gamma,
        delta_p=float(delta_p),
        residual=residual,
        rms_residual=rms,
        max_abs_residual=float(np.max(np.abs(residual))),
        mean_residual=float(np.average(residual, weights=weights)),
        half_angle_deg=interface.half_angle_deg(),
        peak_field=float(np.max(np.sqrt(Er_i * Er_i + Ez_i * Ez_i))),
        peak_maxwell_pressure=float(np.max(p_E)),
    )
