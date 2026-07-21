"""Shape optimizer for the analytic cone family (Version 2).

Finds the cone-family interface that minimises the Young-Laplace-Maxwell
RMS residual using a gradient-free Powell optimizer. Per ADR-0001, the
shape parameterization is an analytic cone family (cone angle, apex radius)
— spline control points are out of scope. Per ADR-0002, the optimizer
always runs with the Laplace solve; threshold/Gaussian closures are never
called internally.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize

from .config import PhysicalParams, SolverParams
from .electrostatics import solve_laplace
from .fields import compute_electric_field
from .geometry import GeometryMasks
from .grid import AxisymmetricGrid
from .interface import straight_cone_interface
from .residual import compute_residual


@dataclass(frozen=True)
class ConeShapeBounds:
    """Box bounds for the two free shape parameters (half_angle_deg, apex_radius)."""

    half_angle_deg_min: float = 1.0
    half_angle_deg_max: float = 89.0
    apex_radius_min: float = 1e-6    # must stay positive; R(z)>0 is required by GraphInterface
    apex_radius_max: float = 0.1


@dataclass(frozen=True)
class OptimizationResult:
    """Result of a cone-shape optimization run."""

    half_angle_deg: float
    rms_residual: float
    apex_radius: float
    nozzle_radius: float
    n_evals: int
    converged: bool
    message: str


def optimize_cone_shape(
    grid: AxisymmetricGrid,
    masks: GeometryMasks,
    physical: PhysicalParams,
    *,
    apex_z: float | None = None,
    z_min_interface: float | None = None,
    z_max_interface: float | None = None,
    n_interface: int = 41,
    initial_half_angle_deg: float = 45.0,
    initial_apex_radius: float = 1e-4,
    bounds: ConeShapeBounds | None = None,
    solver: SolverParams | None = None,
    powell_options: dict | None = None,
) -> OptimizationResult:
    """Find the cone-family interface minimising the YLM RMS residual.

    Solves the Laplace equation once before optimizing (fixed field), then
    minimises RMS residual over (half_angle_deg, apex_radius) with Powell.
    Δp is always eliminated by mean-subtraction inside compute_residual;
    it is never a free variable.
    """
    bounds = bounds or ConeShapeBounds()
    solver = solver or SolverParams()

    z_margin = 0.1 * (grid.z[-1] - grid.z[0])
    z_min_iface = z_min_interface if z_min_interface is not None else grid.z[0] + z_margin
    z_max_iface = z_max_interface if z_max_interface is not None else grid.z[-1] - z_margin
    apex_z_val = apex_z if apex_z is not None else z_max_iface

    # Tighten the angle upper bound so the widest feasible cone stays inside the grid.
    # Without this, Powell may evaluate angles where R(z_min) > r_max, causing
    # interpolation failures that would be silently penalized rather than properly bounded.
    # Derived from: tan(angle_max) = (r_max_safe - apex_radius_min) / |apex_z - z_min_iface|
    r_max_safe = grid.r[-1] * 0.95
    dz_max = abs(apex_z_val - z_min_iface)
    if dz_max > 0:
        geom_angle_max = float(np.degrees(np.arctan(
            (r_max_safe - bounds.apex_radius_min) / dz_max
        )))
        angle_upper = min(bounds.half_angle_deg_max, geom_angle_max)
    else:
        angle_upper = bounds.half_angle_deg_max
    angle_upper = max(angle_upper, bounds.half_angle_deg_min + 1.0)

    phi = solve_laplace(grid, masks, physical, solver=solver)
    Er, Ez, _ = compute_electric_field(grid, phi)

    n_evals = 0

    def objective(x: np.ndarray) -> float:
        nonlocal n_evals
        n_evals += 1
        half_angle_deg = float(np.clip(x[0], bounds.half_angle_deg_min, angle_upper))
        apex_radius = float(np.clip(x[1], bounds.apex_radius_min, bounds.apex_radius_max))
        try:
            iface = straight_cone_interface(
                z_min=z_min_iface, z_max=z_max_iface, apex_z=apex_z_val,
                half_angle_deg=half_angle_deg, n=n_interface, apex_radius=apex_radius,
            )
            diag = compute_residual(grid, iface, Er, Ez, physical)
            return diag.rms_residual
        except Exception:
            return 1e10  # penalize geometrically degenerate shapes

    x0 = np.array([
        float(np.clip(initial_half_angle_deg, bounds.half_angle_deg_min, angle_upper)),
        float(np.clip(initial_apex_radius, bounds.apex_radius_min, bounds.apex_radius_max)),
    ])
    scipy_bounds = [
        (bounds.half_angle_deg_min, angle_upper),
        (bounds.apex_radius_min, bounds.apex_radius_max),
    ]
    options = {"maxiter": 2000, "ftol": 1e-10, "xtol": 1e-8}
    if powell_options:
        options.update(powell_options)

    result = minimize(objective, x0, method="Powell", bounds=scipy_bounds, options=options)

    opt_angle = float(np.clip(result.x[0], bounds.half_angle_deg_min, angle_upper))
    opt_apex = float(np.clip(result.x[1], bounds.apex_radius_min, bounds.apex_radius_max))

    nozzle_radius = float("nan")
    rms_final = float(result.fun)
    try:
        iface_opt = straight_cone_interface(
            z_min=z_min_iface, z_max=z_max_iface, apex_z=apex_z_val,
            half_angle_deg=opt_angle, n=n_interface, apex_radius=opt_apex,
        )
        diag_opt = compute_residual(grid, iface_opt, Er, Ez, physical)
        rms_final = diag_opt.rms_residual
        nozzle_radius = float(iface_opt.R[-1])
    except Exception:
        pass

    return OptimizationResult(
        half_angle_deg=opt_angle,
        rms_residual=rms_final,
        apex_radius=opt_apex,
        nozzle_radius=nozzle_radius,
        n_evals=n_evals,
        converged=bool(result.success),
        message=str(result.message),
    )
