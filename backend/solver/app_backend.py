"""App backend for the Taylor-cone solver Streamlit app.

Exposes a single `run_solver(params) -> SolverResult` entry point.
No `st.*` imports — this module is plain Python, fully testable with pytest.
Plotly figure builders live here and return `plotly.graph_objects.Figure` objects;
`streamlit_app.py` calls `st.plotly_chart()` on them.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Literal

import numpy as np
import plotly.graph_objects as go
from scipy.special import lpmv
from scipy.sparse.linalg import spsolve

from .boundary_conditions import apply_dirichlet_values
from .config import GridParams, PhysicalParams, SolverParams, SpaceChargeParams
from .electrostatics import solve_laplace, solve_poisson
from .fields import compute_electric_field
from .geometry import ImplicitCone, rectangular_electrodes
from .grid import AxisymmetricGrid
from .immersed import apply_immersed_dirichlet
from .interface import straight_cone_interface
from .operators import build_axisymmetric_laplacian
from .optimization import _immersed_masks, _immersed_projected_stats
from .residual import compute_residual
from .space_charge import (
    solve_gaussian_shielding,
    solve_threshold_shielding,
    shielding_metric,
)
from .taylor_analytical import taylor_potential
from .verification import taylor_cone_half_angle_deg


@dataclass(frozen=True)
class RunParams:
    """UI-level parameters for a single solver run.

    All values are plain Python scalars — no numpy, no solver internals.
    """

    # Physical
    V0: float = 1000.0           # applied voltage [V]
    gamma: float = 0.022         # surface tension [N/m]
    # Geometry
    electrode_spacing: float = 10e-3  # domain height z_max [m] (needle-to-plate gap)
    nozzle_radius: float = 10e-3      # domain radial extent r_max [m] (interface inlet)
    # Grid
    nr: int = 31
    nz: int = 51
    # Space-charge model
    space_charge_model: Literal["none", "gaussian", "threshold"] = "none"
    # Gaussian closure params
    rho0: float | None = None
    ell: float | None = None
    apex_r: float | None = None
    apex_z: float | None = None
    # Threshold closure params
    E_c: float | None = None
    E_s: float | None = None
    rho_max: float | None = None
    # Shared space-charge iteration
    relaxation: float = 0.5
    sc_tolerance: float = 1e-8
    sc_max_iterations: int = 50
    # Interface for residual diagnostics
    interface_half_angle_deg: float = 49.3
    interface_n_points: int = 41


@dataclass(frozen=True)
class SolverResult:
    """All outputs from a single solver run, ready for the app layer to render."""

    # Field arrays
    phi: np.ndarray
    Er: np.ndarray
    Ez: np.ndarray
    E_mag: np.ndarray
    rho_e: np.ndarray
    # Grid coordinates (for plotting)
    grid_r: np.ndarray
    grid_z: np.ndarray
    # Interface geometry
    interface_R: np.ndarray
    interface_z: np.ndarray
    # Residual diagnostics
    residual_profile: np.ndarray
    # Scalar outputs
    half_angle: float
    peak_field: float
    rms_residual: float
    shielding_metric: float | None
    runtime_s: float
    converged: bool
    iterations: int


def run_solver(params: RunParams) -> SolverResult:
    """Run the electrostatic-capillary solver and return a SolverResult.

    Covers Laplace, Poisson with Gaussian closure, and Poisson with threshold
    closure. The shape optimizer is not exposed here (see examples/05_*).
    """
    t0 = time.perf_counter()

    grid = AxisymmetricGrid.from_params(GridParams(
        r_max=params.nozzle_radius,
        z_min=0.0,
        z_max=params.electrode_spacing,
        nr=params.nr,
        nz=params.nz,
    ))
    masks = rectangular_electrodes(grid, powered="z_max", ground="z_min", far_dirichlet=True)
    physical = PhysicalParams(V0=params.V0, gamma=params.gamma)
    solver = SolverParams()

    converged = True
    iterations = 1
    rho_e = np.zeros(grid.shape, dtype=float)
    shielding: float | None = None

    if params.space_charge_model == "none":
        phi = solve_laplace(grid, masks, physical, solver=solver)
        Er, Ez, E_mag = compute_electric_field(grid, phi)

    elif params.space_charge_model == "gaussian":
        sc_params = SpaceChargeParams(
            model="gaussian",
            rho0=params.rho0,
            ell=params.ell,
            apex_r=params.apex_r,
            apex_z=params.apex_z,
            relaxation=params.relaxation,
            tolerance=params.sc_tolerance,
            max_iterations=params.sc_max_iterations,
        )
        result = solve_gaussian_shielding(grid, masks, physical, sc_params, solver=solver)
        phi, Er, Ez, E_mag = result.phi, result.Er, result.Ez, result.E_mag
        rho_e = result.rho_e
        converged = result.converged
        iterations = result.iterations
        shielding = result.shielding_metric

    elif params.space_charge_model == "threshold":
        sc_params = SpaceChargeParams(
            model="threshold",
            E_c=params.E_c,
            E_s=params.E_s,
            rho_max=params.rho_max,
            relaxation=params.relaxation,
            tolerance=params.sc_tolerance,
            max_iterations=params.sc_max_iterations,
        )
        result = solve_threshold_shielding(grid, masks, physical, sc_params, solver=solver)
        phi, Er, Ez, E_mag = result.phi, result.Er, result.Ez, result.E_mag
        rho_e = result.rho_e
        converged = result.converged
        iterations = result.iterations
        shielding = result.shielding_metric

    else:
        raise ValueError(f"Unknown space_charge_model: {params.space_charge_model!r}")

    # Build interface and compute residual diagnostics.
    # Cap the interface angle so the widest cone stays inside r_max.
    z_margin = 0.1 * params.electrode_spacing
    z_min_iface = z_margin
    z_max_iface = params.electrode_spacing - z_margin
    apex_z_iface = z_max_iface
    dz = abs(apex_z_iface - z_min_iface)
    r_max_safe = params.nozzle_radius * 0.95
    max_angle = float(np.degrees(np.arctan(r_max_safe / dz))) if dz > 0 else 89.0
    capped_angle = min(params.interface_half_angle_deg, max_angle)
    iface = straight_cone_interface(
        z_min=z_min_iface,
        z_max=z_max_iface,
        apex_z=apex_z_iface,
        half_angle_deg=capped_angle,
        n=params.interface_n_points,
    )
    diag = compute_residual(grid, iface, Er, Ez, physical)

    runtime_s = time.perf_counter() - t0

    return SolverResult(
        phi=phi,
        Er=Er,
        Ez=Ez,
        E_mag=E_mag,
        rho_e=rho_e,
        grid_r=grid.r,
        grid_z=grid.z,
        interface_R=iface.R,
        interface_z=iface.z,
        residual_profile=diag.residual,
        half_angle=diag.half_angle_deg,
        peak_field=diag.peak_field,
        rms_residual=diag.rms_residual,
        shielding_metric=shielding,
        runtime_s=runtime_s,
        converged=converged,
        iterations=iterations,
    )


# ---------------------------------------------------------------------------
# Plotly figure builders — each takes a SolverResult and returns a Figure.
# ---------------------------------------------------------------------------

def figure_potential(result: SolverResult) -> go.Figure:
    """Filled contour plot of the electric potential φ(r,z)."""
    fig = go.Figure(go.Contour(
        z=result.phi.T,
        x=result.grid_r,
        y=result.grid_z,
        colorscale="RdBu_r",
        contours={"showlabels": True},
        colorbar={"title": "φ [V]"},
    ))
    fig.update_layout(
        title="Electric Potential",
        xaxis_title="r [m]",
        yaxis_title="z [m]",
        yaxis_scaleanchor="x",
    )
    return fig


def figure_field_magnitude(result: SolverResult) -> go.Figure:
    """Heatmap of |E|(r,z)."""
    fig = go.Figure(go.Heatmap(
        z=result.E_mag.T,
        x=result.grid_r,
        y=result.grid_z,
        colorscale="Inferno",
        colorbar={"title": "|E| [V/m]"},
    ))
    fig.update_layout(
        title="Electric Field Magnitude",
        xaxis_title="r [m]",
        yaxis_title="z [m]",
        yaxis_scaleanchor="x",
    )
    return fig


def figure_interface_overlay(result: SolverResult) -> go.Figure:
    """Potential contour with the interface overlaid."""
    fig = figure_potential(result)
    fig.add_trace(go.Scatter(
        x=result.interface_R,
        y=result.interface_z,
        mode="lines",
        line={"color": "lime", "width": 2},
        name="Interface",
    ))
    fig.update_layout(title="Potential with Interface Overlay")
    return fig


def figure_residual_profile(result: SolverResult) -> go.Figure:
    """YLM residual along the interface arc."""
    fig = go.Figure(go.Scatter(
        x=result.interface_z,
        y=result.residual_profile,
        mode="lines+markers",
        line={"color": "firebrick"},
        name="Residual",
    ))
    fig.add_hline(y=0.0, line_dash="dash", line_color="grey")
    fig.update_layout(
        title=f"YLM Residual Profile  (RMS = {result.rms_residual:.3e} Pa)",
        xaxis_title="z [m]",
        yaxis_title="Residual [Pa]",
    )
    return fig


def figure_space_charge(result: SolverResult) -> go.Figure:
    """Heatmap of space-charge density ρ_e(r,z)."""
    fig = go.Figure(go.Heatmap(
        z=result.rho_e.T,
        x=result.grid_r,
        y=result.grid_z,
        colorscale="Viridis",
        colorbar={"title": "ρ_e [C/m³]"},
    ))
    fig.update_layout(
        title="Space-Charge Density",
        xaxis_title="r [m]",
        yaxis_title="z [m]",
        yaxis_scaleanchor="x",
    )
    return fig


# ---------------------------------------------------------------------------
# Immersed free-boundary verification (P2 onset projection + P3i Taylor identity)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ImmersedVerificationParams:
    """UI-level parameters for the immersed free-boundary verification tab.

    All lengths are SI; the defaults are at realistic mm scale.  The
    computational domain is a square of side ``electrode_spacing`` (the
    needle-to-plate gap), with the apex at ``apex_z`` and a spherical cap of
    radius ``apex_radius``.  The flank-sampling windows are fixed fractions of
    ``electrode_spacing``, so rescaling the spacing rescales the whole problem.
    """

    nr: int = 61
    nz: int = 89
    electrode_spacing: float = 10e-3   # domain side [m] (needle-to-plate gap)
    apex_z: float = 8.6e-3             # on-axis apex position [m] (0.86 * spacing)
    apex_radius: float = 0.5e-3        # apex cap radius [m] (5% of spacing)
    bc_type: Literal["grounded", "taylor_farfield"] = "taylor_farfield"
    gamma: float = 0.022
    V0: float = 1000.0


@dataclass(frozen=True)
class ImmersedVerificationResult:
    """Outputs of the immersed verification run, ready for the app layer."""

    # Free-boundary landscape (P2)
    recovered_angle_deg: float
    onset_voltage_V: float | None
    min_rms_Pa: float
    landscape_angles: np.ndarray
    landscape_rms: np.ndarray
    # Imposed-Taylor identity (P3i)
    taylor_angle_deg: float
    identity_ratio: float | None       # V0* / A* at the Taylor angle (1.0 = exact)
    identity_argmin_deg: float | None
    phi_identity: np.ndarray | None    # imposed-Taylor solve at 49.29 deg
    grid_r: np.ndarray | None
    grid_z: np.ndarray | None
    runtime_s: float


def _taylor_amplitude(gamma: float) -> float:
    """Analytic balance amplitude A* = sqrt(2 gamma cos a / (eps0 P^1^2 sin a))."""
    alpha = taylor_cone_half_angle_deg()
    theta0 = np.radians(180.0 - alpha)
    p1 = lpmv(1, 0.5, np.cos(theta0))
    eps0 = 8.8541878128e-12
    return float(np.sqrt(2.0 * gamma * np.cos(np.radians(alpha)) / (eps0 * p1**2 * np.sin(np.radians(alpha)))))


def _solve_imposed_taylor(grid: AxisymmetricGrid, angle_deg: float, cap: float, apex_z: float):
    """Laplace solve with the analytic Taylor potential on the box ring and the
    rounded cone (candidate angle, cap) as the immersed zero equipotential."""
    cone = ImplicitCone(
        apex_z=apex_z + 1e-10 * apex_z,
        half_angle_deg=angle_deg,
        apex_radius=cap,
        boundary_value=0.0,
    )
    phi_outer = taylor_potential(grid.R, grid.Z, apex_z, 1.0)
    outer = np.zeros(grid.shape, bool)
    outer[-1, :] = True
    outer[:, 0] = True
    outer[:, -1] = True
    outer[0, :] = True
    Aop = build_axisymmetric_laplacian(grid)
    Aop, b = apply_dirichlet_values(Aop, np.zeros(grid.size), grid, outer, phi_outer)
    Aop, b = apply_immersed_dirichlet(Aop, b, grid, cone, fixed_mask=outer)
    return cone, grid.unflatten(spsolve(Aop, b))


def run_immersed_verification(params: ImmersedVerificationParams) -> ImmersedVerificationResult:
    """Run the committed immersed verifications for the app tab.

    1. **Free-boundary landscape (P2):** sweep the half-angle with the
       amplitude-projected residual (``_immersed_projected_stats``) and refine
       around the minimum.  With ``bc_type="grounded"`` the outer box is
       grounded (the truncation baseline, recovering ~44 deg and a physical
       onset voltage); with ``bc_type="taylor_farfield"`` the outer boundary is
       set to the analytical Taylor potential (recovering ~49.3 deg).
    2. **Imposed-Taylor identity (P3i):** impose the exact analytic Taylor
       potential on the box ring, cone at 0, and compare the projected onset
       voltage at 49.29 deg with the analytic balance amplitude A* (ratio ~1.01).
    """
    t0 = time.perf_counter()
    physical = PhysicalParams(V0=params.V0, gamma=params.gamma)
    z_max = params.electrode_spacing
    grid = AxisymmetricGrid.from_params(GridParams(z_max, 0.0, z_max, params.nr, params.nz))
    alpha = taylor_cone_half_angle_deg()

    # --- free-boundary landscape (recovered angle + onset voltage) ---
    z_min_w, z_max_w = 0.15 * z_max, 0.85 * z_max
    taylor_z_min, taylor_z_max = 0.30 * z_max, 0.75 * z_max
    external = rectangular_electrodes(grid, powered="z_max", ground="z_min", far_dirichlet=True)
    normal_clearance = 3.0 * max(grid.dr, grid.dz)
    r_max_safe = min(grid.r[-1] * 0.95, grid.r[-1] - normal_clearance)
    dz_max = abs(params.apex_z - z_min_w)
    angle_upper = float(np.degrees(np.arctan(max(0.0, r_max_safe) / dz_max))) if dz_max > 0 else 89.0

    taylor_physical = PhysicalParams(V0=1.0, gamma=params.gamma)

    def projected(angle_deg: float) -> tuple[float, float] | None:
        try:
            if params.bc_type == "taylor_farfield":
                cone, phi = _solve_imposed_taylor(
                    grid, float(angle_deg), params.apex_radius, params.apex_z
                )
                return _immersed_projected_stats(
                    grid, cone, phi, taylor_physical,
                    z_min=taylor_z_min, z_max=taylor_z_max, n_interface=41,
                )
            cone = ImplicitCone(
                apex_z=params.apex_z + 1e-10 * params.apex_z,
                half_angle_deg=float(angle_deg),
                apex_radius=params.apex_radius,
                boundary_value=params.V0,
            )
            masks = _immersed_masks(grid, external, cone)
            phi = solve_laplace(grid, masks, physical, immersed=cone)
            return _immersed_projected_stats(
                grid, cone, phi, physical, z_min=z_min_w, z_max=z_max_w, n_interface=41
            )
        except (ValueError, RuntimeError):
            return None

    rms_map: dict[float, float] = {}
    coarse = np.unique(np.concatenate((np.arange(35.0, angle_upper + 1e-9, 2.5), [alpha])))
    coarse = coarse[coarse <= angle_upper]
    for a in coarse:
        res = projected(float(a))
        if res is not None:
            rms_map[float(a)] = res[0]
    if not rms_map:
        raise RuntimeError("immersed verification: all landscape candidates failed")
    coarse_argmin = min(rms_map, key=rms_map.get)
    refine = np.arange(max(30.0, coarse_argmin - 2.5), min(angle_upper, coarse_argmin + 2.51), 0.5)
    for a in refine:
        res = projected(float(a))
        if res is not None:
            rms_map[float(a)] = res[0]
    argmin = min(rms_map, key=rms_map.get)
    final = projected(argmin)
    rms_min = float(final[0])
    # The projected onset voltage is physical only for the finite grounded box;
    # the analytical Taylor far-field is scale-free and has no onset voltage.
    onset_voltage = final[1] if params.bc_type == "grounded" else None
    land_angles = np.array(sorted(rms_map))
    land_rms = np.array([rms_map[a] for a in land_angles])

    # --- imposed-Taylor identity (P3i) ---
    # The cone is at potential 0 here, so the projection is normalized to the
    # imposed outer amplitude (V0 = A = 1); V0* then equals the best-fit balance
    # amplitude A*.
    identity_ratio: float | None = None
    identity_argmin: float | None = None
    phi_identity: np.ndarray | None = None
    try:
        cap_id = 0.001 * z_max
        cone_id, phi_identity = _solve_imposed_taylor(grid, alpha, cap_id, params.apex_z)
        _, v0_taylor = _immersed_projected_stats(
            grid, cone_id, phi_identity, PhysicalParams(V0=1.0, gamma=params.gamma),
            z_min=taylor_z_min, z_max=taylor_z_max, n_interface=41,
        )
        amp = _taylor_amplitude(params.gamma)
        if v0_taylor is not None and amp > 0:
            identity_ratio = float(v0_taylor / amp)
        id_angles = np.arange(47.0, 52.01, 1.0)
        id_rms: dict[float, float] = {}
        for a in id_angles:
            cone_a, phi_a = _solve_imposed_taylor(grid, float(a), cap_id, params.apex_z)
            id_rms[float(a)] = _immersed_projected_stats(
                grid, cone_a, phi_a, PhysicalParams(V0=1.0, gamma=params.gamma),
                z_min=taylor_z_min, z_max=taylor_z_max, n_interface=41,
            )[0]
        identity_argmin = float(min(id_rms, key=id_rms.get))
    except (ValueError, RuntimeError):
        pass

    return ImmersedVerificationResult(
        recovered_angle_deg=float(argmin),
        onset_voltage_V=onset_voltage,
        min_rms_Pa=rms_min,
        landscape_angles=land_angles,
        landscape_rms=land_rms,
        taylor_angle_deg=alpha,
        identity_ratio=identity_ratio,
        identity_argmin_deg=identity_argmin,
        phi_identity=phi_identity,
        grid_r=grid.r,
        grid_z=grid.z,
        runtime_s=time.perf_counter() - t0,
    )


def figure_verification_landscape(result: ImmersedVerificationResult) -> go.Figure:
    """Free-boundary amplitude-projected residual RMS vs half-angle."""
    fig = go.Figure(go.Scatter(
        x=result.landscape_angles,
        y=result.landscape_rms,
        mode="lines+markers",
        name="Projected residual RMS",
        line={"color": "steelblue"},
    ))
    fig.add_vline(
        x=result.taylor_angle_deg, line_dash="dash", line_color="green",
        annotation_text=f"Taylor {result.taylor_angle_deg:.2f}°",
    )
    fig.add_vline(
        x=result.recovered_angle_deg, line_dash="dash", line_color="firebrick",
        annotation_text=f"argmin {result.recovered_angle_deg:.1f}°",
    )
    fig.update_layout(
        title="Free-boundary amplitude-projected residual vs half-angle",
        xaxis_title="Half-angle [deg]",
        yaxis_title="RMS residual [Pa]",
        yaxis_type="log",
    )
    return fig


def figure_imposed_taylor_field(result: ImmersedVerificationResult) -> go.Figure:
    """Potential of the imposed-Taylor solve at 49.29 deg (cone at 0)."""
    if result.phi_identity is None or result.grid_r is None or result.grid_z is None:
        return go.Figure()
    fig = go.Figure(go.Contour(
        z=result.phi_identity.T,
        x=result.grid_r,
        y=result.grid_z,
        colorscale="RdBu_r",
        colorbar={"title": "φ [V]"},
    ))
    fig.update_layout(
        title=f"Imposed-Taylor potential at {result.taylor_angle_deg:.2f}° (cone at 0)",
        xaxis_title="r [m]",
        yaxis_title="z [m]",
        yaxis_scaleanchor="x",
    )
    return fig


# ---------------------------------------------------------------------------
# JSON serialization of runs — writes the full parameter set plus compact
# output summaries to a file so agents can inspect what the solver computed
# without re-running the app. Pure Python: no streamlit dependency.
# ---------------------------------------------------------------------------

def _array_summary(name: str, a: np.ndarray) -> dict:
    """JSON-safe compact summary of a field array (agents read this instead of
    the raw grids, which can be large)."""
    a = np.asarray(a, dtype=float)
    return {
        "name": name,
        "shape": list(a.shape),
        "size": int(a.size),
        "min": float(np.nanmin(a)),
        "max": float(np.nanmax(a)),
        "mean": float(np.nanmean(a)),
        "std": float(np.nanstd(a)),
        "rms": float(np.sqrt(np.nanmean(a**2))),
        "nan_count": int(np.isnan(a).sum()),
    }


def solver_run_to_dict(params: RunParams, result: SolverResult) -> dict:
    """JSON-serializable snapshot of a classic solver run.

    Includes every input parameter (``asdict(params)``) plus all scalar
    outputs and compact summaries of the field/geometry arrays.
    """
    return {
        "schema": "isef-taylor-cone/classic-run",
        "schema_version": 1,
        "kind": "classic_solver_run",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parameters": asdict(params),
        "outputs": {
            "half_angle_deg": float(result.half_angle),
            "peak_field_V_m": float(result.peak_field),
            "rms_residual_Pa": float(result.rms_residual),
            "shielding_metric_SE": (float(result.shielding_metric)
                                    if result.shielding_metric is not None else None),
            "runtime_s": float(result.runtime_s),
            "converged": bool(result.converged),
            "iterations": int(result.iterations),
        },
        "grid": {
            "nr": int(result.grid_r.size),
            "nz": int(result.grid_z.size),
            "r_min": float(np.min(result.grid_r)),
            "r_max": float(np.max(result.grid_r)),
            "z_min": float(np.min(result.grid_z)),
            "z_max": float(np.max(result.grid_z)),
        },
        "fields": {
            "phi": _array_summary("phi", result.phi),
            "Er": _array_summary("Er", result.Er),
            "Ez": _array_summary("Ez", result.Ez),
            "E_mag": _array_summary("E_mag", result.E_mag),
            "rho_e": _array_summary("rho_e", result.rho_e),
        },
        "interface": {
            "half_angle_deg": float(result.half_angle),
            "n_points": int(result.interface_R.size),
            "R_min": float(np.min(result.interface_R)),
            "R_max": float(np.max(result.interface_R)),
            "z_min": float(np.min(result.interface_z)),
            "z_max": float(np.max(result.interface_z)),
        },
        "residual_profile": {
            "n_points": int(result.residual_profile.size),
            "min_Pa": float(np.min(result.residual_profile)),
            "max_Pa": float(np.max(result.residual_profile)),
            "rms_Pa": float(result.rms_residual),
        },
    }


def verification_run_to_dict(params: ImmersedVerificationParams,
                             result: ImmersedVerificationResult) -> dict:
    """JSON-serializable snapshot of an immersed-verification run.

    Includes every input parameter plus the recovered angle, onset voltage,
    Taylor-identity outputs, and the full residual-landscape curve.
    """
    return {
        "schema": "isef-taylor-cone/verification-run",
        "schema_version": 1,
        "kind": "immersed_verification_run",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parameters": asdict(params),
        "outputs": {
            "recovered_angle_deg": float(result.recovered_angle_deg),
            "onset_voltage_V": (float(result.onset_voltage_V)
                                if result.onset_voltage_V is not None else None),
            "min_rms_Pa": float(result.min_rms_Pa),
            "taylor_angle_deg": float(result.taylor_angle_deg),
            "identity_ratio_V0_over_A": (float(result.identity_ratio)
                                         if result.identity_ratio is not None else None),
            "identity_argmin_deg": (float(result.identity_argmin_deg)
                                    if result.identity_argmin_deg is not None else None),
            "runtime_s": float(result.runtime_s),
        },
        "landscape": {
            "n_points": int(result.landscape_angles.size),
            "angles_deg": [float(x) for x in result.landscape_angles],
            "rms_Pa": [float(x) for x in result.landscape_rms],
        },
        "imposed_taylor_field": (
            _array_summary("phi_identity", result.phi_identity)
            if result.phi_identity is not None else None
        ),
    }


def write_results_json(path: str | os.PathLike, payload: dict) -> str:
    """Atomically write *payload* as pretty JSON to *path* (creates parent
    directories). Returns the path as a string."""
    path = os.fspath(path)
    parent = os.path.dirname(path) or "."
    os.makedirs(parent, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".results-", suffix=".json", dir=parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            # allow_nan=False: refuse to write NaN/Infinity (invalid RFC 8259
            # JSON) instead of producing a file strict parsers cannot read.
            json.dump(payload, fh, indent=2, allow_nan=False)
            fh.write("\n")
        os.replace(tmp, path)
        os.chmod(path, 0o644)  # readable by other users/agents
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return path
