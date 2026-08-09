"""Shape optimizer for the analytic cone family (V2+).

Finds the cone-family interface that minimises the Young-Laplace-Maxwell
RMS residual using a gradient-free Powell optimizer. Per ADR-0001, the
shape parameterization is an analytic cone family (cone angle, apex radius)
— spline control points are out of scope.

V2: optimizer runs with the Laplace solve (ADR-0002 default).
V3: pass `sc_params` to couple the threshold-activated closure — the
    inner Poisson fixed-point loop runs on every optimizer evaluation.
V4: optional immersed mode makes every candidate cone the powered boundary
    of its own electrostatic solve.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize

from .config import PhysicalParams, SolverParams, SpaceChargeParams
from .electrostatics import solve_laplace
from .fields import compute_electric_field
from .geometry import GeometryMasks, ImplicitCone
from .grid import AxisymmetricGrid
from .immersed import normal_field_on_interface
from .interface import straight_cone_interface
from .residual import compute_residual
from .space_charge import solve_threshold_shielding


@dataclass(frozen=True)
class ConeShapeBounds:
    """Box bounds for the two free shape parameters (half_angle_deg, apex_radius)."""

    half_angle_deg_min: float = 1.0
    half_angle_deg_max: float = 89.0
    apex_radius_min: float = 1e-6
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
    sc_converged: bool | None = None
    sc_iterations: int | None = None
    immersed_mode: bool = False
    initial_rms_residual: float | None = None
    candidate_solve_failures: int = 0
    field_variation: float | None = None


def _immersed_masks(grid: AxisymmetricGrid, external: GeometryMasks, cone: ImplicitCone) -> GeometryMasks:
    """Make the cone powered while retaining external grounding safely."""
    cone_masks = cone.masks(grid, ground_outer=True)
    conductor = cone_masks.conductor
    powered = conductor.copy()
    # Existing powered boundaries belong to the legacy electrode and must not
    # remain powered. Existing grounds, plus the cone geometry's outer ground,
    # remain external Dirichlet boundaries unless covered by liquid.
    grounded = (cone_masks.grounded | external.grounded) & ~conductor
    gas = ~(conductor | grounded)
    return GeometryMasks(
        powered=powered,
        grounded=grounded,
        axis=external.axis | cone_masks.axis,
        far_boundary=external.far_boundary | cone_masks.far_boundary,
        conductor=conductor,
        gas=gas,
    )


def _immersed_rms(
    grid: AxisymmetricGrid,
    cone: ImplicitCone,
    potential: np.ndarray,
    physical: PhysicalParams,
    *,
    z_min: float,
    z_max: float,
    n_interface: int,
) -> float:
    """Evaluate the mean-eliminated YLM residual on flank-only cone samples."""
    interface = cone.sample_graph(z_min, z_max, n_interface)
    flank = np.asarray(interface.flank_mask, dtype=bool)
    if np.count_nonzero(flank) < 3:
        raise ValueError("immersed residual requires at least three flank samples")

    r = interface.r[flank]
    z = interface.z[flank]
    E_n = np.asarray(normal_field_on_interface(grid, potential, cone, r, z), dtype=float)
    curvature = interface.curvature()[flank]
    weights = interface.arclength_weights()[flank]
    if not (np.all(np.isfinite(E_n)) and np.all(np.isfinite(curvature))):
        raise ValueError("non-finite immersed interface diagnostics")

    p_E = 0.5 * physical.eps_g * E_n * E_n
    p_gamma = physical.gamma * curvature
    delta_p = float(np.average(p_gamma - p_E, weights=weights))
    residual = p_gamma - delta_p - p_E
    return float(np.sqrt(np.average(residual * residual, weights=weights)))


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
    sc_params: SpaceChargeParams | None = None,
    immersed_mode: bool = False,
    immersed: bool | None = None,
) -> OptimizationResult:
    """Find the cone-family interface minimising the YLM RMS residual.

    The default is the legacy path: Laplace electrostatics is solved once and
    reused, unless ``sc_params`` requests the historical coupled threshold
    solve. With ``immersed_mode=True`` (or the alias ``immersed=True``), each
    objective evaluation constructs an :class:`ImplicitCone`, solves a new
    candidate-dependent Laplace problem, reconstructs its boundary-normal
    field, and evaluates only straight-flank samples. Immersed space-charge
    coupling is intentionally not enabled by this Laplace milestone.
    """
    if immersed is not None:
        if immersed_mode and not immersed:
            raise ValueError("conflicting immersed and immersed_mode values")
        immersed_mode = bool(immersed)
    if immersed_mode and sc_params is not None:
        raise ValueError("immersed optimization currently supports Laplace mode only")

    bounds = bounds or ConeShapeBounds()
    solver = solver or SolverParams()

    z_margin = 0.1 * (grid.z[-1] - grid.z[0])
    z_min_iface = z_min_interface if z_min_interface is not None else grid.z[0] + z_margin
    z_max_iface = z_max_interface if z_max_interface is not None else grid.z[-1] - z_margin
    apex_z_val = apex_z if apex_z is not None else z_max_iface
    # The implicit cap evaluates the exact apex through a square root.  A tiny
    # upward offset keeps a grid node at the nominal apex unambiguously on the
    # liquid side instead of turning roundoff into a zero-length cut stencil.
    immersed_apex_z = apex_z_val + (1.0e-10 * max(1.0, abs(apex_z_val))) if immersed_mode else apex_z_val

    # Leave radial room for the three gas-normal samples used by the immersed
    # field reconstruction (up to 3*max(dr,dz) along the normal). Legacy mode
    # retains its historical 95% margin.
    normal_clearance = 3.0 * max(grid.dr, grid.dz) if immersed_mode else 0.0
    r_max_safe = min(grid.r[-1] * 0.95, grid.r[-1] - normal_clearance)
    dz_max = abs(apex_z_val - z_min_iface)
    if dz_max > 0:
        geom_angle_max = float(np.degrees(np.arctan(
            max(0.0, r_max_safe - bounds.apex_radius_min) / dz_max
        )))
        # The immersed E_n reconstruction samples up to 3*max(dr,dz) along the
        # gas normal; its vertical reach (3d*sin(angle) above z_max_iface) must
        # also stay inside the grid top, or candidates on coarse grids would be
        # silently penalized as out-of-domain sample failures.
        z_reach = normal_clearance
        z_headroom = grid.z[-1] - z_max_iface
        if z_headroom > 0.0 and z_reach > z_headroom:
            geom_angle_max = min(
                geom_angle_max,
                float(np.degrees(np.arcsin(z_headroom / z_reach))),
            )
        angle_upper = min(bounds.half_angle_deg_max, geom_angle_max)
    else:
        angle_upper = bounds.half_angle_deg_max
    angle_upper = max(angle_upper, bounds.half_angle_deg_min + 1.0)

    coupled = sc_params is not None
    if not immersed_mode and not coupled:
        phi_base = solve_laplace(grid, masks, physical, solver=solver)
        Er_base, Ez_base, _ = compute_electric_field(grid, phi_base)

    def _legacy_fields() -> tuple[np.ndarray, np.ndarray, bool | None, int | None]:
        if coupled:
            sc = solve_threshold_shielding(grid, masks, physical, sc_params, solver=solver)
            return sc.Er, sc.Ez, sc.converged, sc.iterations
        return Er_base, Ez_base, None, None

    n_evals = 0
    solve_failures = 0
    failure_messages: list[str] = []
    reference_phi: np.ndarray | None = None
    max_field_variation = 0.0

    def objective(x: np.ndarray) -> float:
        nonlocal n_evals, solve_failures, reference_phi, max_field_variation
        n_evals += 1
        half_angle_deg = float(np.clip(x[0], bounds.half_angle_deg_min, angle_upper))
        apex_radius = float(np.clip(x[1], bounds.apex_radius_min, bounds.apex_radius_max))
        try:
            if immersed_mode:
                cone = ImplicitCone(
                    apex_z=immersed_apex_z,
                    half_angle_deg=half_angle_deg,
                    apex_radius=apex_radius,
                    boundary_value=physical.V0,
                )
                candidate_masks = _immersed_masks(grid, masks, cone)
                phi = solve_laplace(
                    grid, candidate_masks, physical, solver=solver, immersed=cone
                )
                if reference_phi is None:
                    reference_phi = phi.copy()
                else:
                    max_field_variation = max(
                        max_field_variation, float(np.max(np.abs(phi - reference_phi)))
                    )
                return _immersed_rms(
                    grid, cone, phi, physical,
                    z_min=z_min_iface, z_max=z_max_iface, n_interface=n_interface,
                )

            iface = straight_cone_interface(
                z_min=z_min_iface, z_max=z_max_iface, apex_z=apex_z_val,
                half_angle_deg=half_angle_deg, n=n_interface, apex_radius=apex_radius,
            )
            Er, Ez, _, _ = _legacy_fields()
            return compute_residual(grid, iface, Er, Ez, physical).rms_residual
        except (ValueError, RuntimeError, np.linalg.LinAlgError) as exc:
            solve_failures += 1
            if len(failure_messages) < 3:
                failure_messages.append(f"{type(exc).__name__}: {exc}")
            return 1e10

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

    initial_rms = objective(x0)
    result = minimize(objective, x0, method="Powell", bounds=scipy_bounds, options=options)

    # Do not report a Powell endpoint worse than its own explicitly evaluated
    # starting candidate (possible after penalties on a discontinuous mask change).
    if not np.isfinite(result.fun) or float(result.fun) > initial_rms:
        opt_x = x0
    else:
        opt_x = result.x
    opt_angle = float(np.clip(opt_x[0], bounds.half_angle_deg_min, angle_upper))
    opt_apex = float(np.clip(opt_x[1], bounds.apex_radius_min, bounds.apex_radius_max))

    nozzle_radius = float("nan")
    rms_final = float(min(float(result.fun), initial_rms))
    sc_converged_final: bool | None = None
    sc_iters_final: int | None = None
    try:
        if immersed_mode:
            cone_opt = ImplicitCone(immersed_apex_z, opt_angle, opt_apex, physical.V0)
            candidate_masks = _immersed_masks(grid, masks, cone_opt)
            phi_final = solve_laplace(
                grid, candidate_masks, physical, solver=solver, immersed=cone_opt
            )
            rms_final = _immersed_rms(
                grid, cone_opt, phi_final, physical,
                z_min=z_min_iface, z_max=z_max_iface, n_interface=n_interface,
            )
            # Liquid extends toward decreasing z: z_min is the wide base/nozzle,
            # while the physical tip at apex_z has zero graph radius.
            nozzle_radius = float(cone_opt.surface_radius(z_min_iface))
        else:
            iface_opt = straight_cone_interface(
                z_min=z_min_iface, z_max=z_max_iface, apex_z=apex_z_val,
                half_angle_deg=opt_angle, n=n_interface, apex_radius=opt_apex,
            )
            Er_final, Ez_final, sc_converged_final, sc_iters_final = _legacy_fields()
            rms_final = compute_residual(grid, iface_opt, Er_final, Ez_final, physical).rms_residual
            nozzle_radius = float(iface_opt.R[0])
    except (ValueError, RuntimeError, np.linalg.LinAlgError) as exc:
        solve_failures += 1
        if len(failure_messages) < 3:
            failure_messages.append(f"final {type(exc).__name__}: {exc}")

    message = str(result.message)
    if failure_messages:
        message += "; candidate failures: " + " | ".join(failure_messages)

    return OptimizationResult(
        half_angle_deg=opt_angle,
        rms_residual=rms_final,
        apex_radius=opt_apex,
        nozzle_radius=nozzle_radius,
        n_evals=n_evals,
        converged=bool(result.success and np.isfinite(rms_final) and rms_final < 1e10),
        message=message,
        sc_converged=sc_converged_final,
        sc_iterations=sc_iters_final,
        immersed_mode=immersed_mode,
        initial_rms_residual=float(initial_rms),
        candidate_solve_failures=solve_failures,
        field_variation=max_field_variation if immersed_mode else None,
    )
