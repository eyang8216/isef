"""App backend for the Taylor-cone solver Streamlit app.

Exposes a single `run_solver(params) -> SolverResult` entry point.
No `st.*` imports — this module is plain Python, fully testable with pytest.
Plotly figure builders live here and return `plotly.graph_objects.Figure` objects;
`streamlit_app.py` calls `st.plotly_chart()` on them.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Literal

import numpy as np
import plotly.graph_objects as go

from .config import GridParams, PhysicalParams, SolverParams, SpaceChargeParams
from .electrostatics import solve_laplace, solve_poisson
from .fields import compute_electric_field
from .geometry import rectangular_electrodes
from .grid import AxisymmetricGrid
from .interface import straight_cone_interface
from .residual import compute_residual
from .space_charge import (
    solve_gaussian_shielding,
    solve_threshold_shielding,
    shielding_metric,
)


@dataclass(frozen=True)
class RunParams:
    """UI-level parameters for a single solver run.

    All values are plain Python scalars — no numpy, no solver internals.
    """

    # Physical
    V0: float = 1000.0           # applied voltage [V]
    gamma: float = 0.022         # surface tension [N/m]
    # Geometry
    electrode_spacing: float = 1.0   # domain height z_max [m]
    nozzle_radius: float = 0.5       # domain radial extent r_max [m]
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
