import numpy as np
import pytest

from solver.app_backend import RunParams, SolverResult, run_solver


def test_run_solver_laplace_returns_complete_result():
    """run_solver with no space charge returns a SolverResult with all fields populated."""
    params = RunParams(V0=1000.0, gamma=0.022, nr=15, nz=21, space_charge_model="none")
    result = run_solver(params)

    assert isinstance(result, SolverResult)
    # Field arrays must have the right shape
    assert result.phi.shape == (params.nr, params.nz)
    assert result.Er.shape == (params.nr, params.nz)
    assert result.Ez.shape == (params.nr, params.nz)
    assert result.E_mag.shape == (params.nr, params.nz)
    assert result.rho_e.shape == (params.nr, params.nz)
    # Interface and residual arrays must be 1D and non-empty
    assert result.interface_R.ndim == 1 and result.interface_R.size > 0
    assert result.interface_z.ndim == 1 and result.interface_z.size == result.interface_R.size
    assert result.residual_profile.ndim == 1
    # Grid coords
    assert result.grid_r.shape == (params.nr,)
    assert result.grid_z.shape == (params.nz,)
    # Scalar fields must be finite
    assert np.isfinite(result.half_angle)
    assert np.isfinite(result.peak_field)
    assert np.isfinite(result.rms_residual)
    assert np.isfinite(result.runtime_s)
    assert result.runtime_s > 0
    assert result.converged is True
    assert result.iterations >= 1


def test_run_solver_half_angle_in_physical_range():
    """half_angle must be finite and in (0°, 90°) for a basic Laplace case."""
    params = RunParams(V0=1000.0, gamma=0.022, nr=15, nz=21, space_charge_model="none")
    result = run_solver(params)
    assert 0.0 < result.half_angle < 90.0, (
        f"half_angle={result.half_angle:.2f}° is outside physical range (0°, 90°)"
    )


def test_run_solver_laplace_rho_e_is_zero():
    """Space-charge density must be identically zero for a Laplace run."""
    params = RunParams(V0=500.0, nr=13, nz=17, space_charge_model="none")
    result = run_solver(params)
    assert np.all(result.rho_e == 0.0)


def test_run_solver_laplace_shielding_metric_is_none():
    """shielding_metric must be None for a Laplace (no space-charge) run."""
    params = RunParams(V0=1000.0, nr=13, nz=17, space_charge_model="none")
    result = run_solver(params)
    assert result.shielding_metric is None
    """app_backend must not import streamlit — it must be testable without a Streamlit session."""
    import importlib
    import sys
    # Ensure streamlit is not in the module's imports by checking the module source
    import solver.app_backend as mod
    import inspect
    src = inspect.getsource(mod)
    assert "import streamlit" not in src, "app_backend.py must not import streamlit"
    assert "from streamlit" not in src, "app_backend.py must not import from streamlit"


def test_figure_builders_return_plotly_figures():
    """All five Plotly figure builders must return plotly Figure objects."""
    import plotly.graph_objects as go
    from solver.app_backend import (
        figure_field_magnitude,
        figure_interface_overlay,
        figure_potential,
        figure_residual_profile,
        figure_space_charge,
    )

    params = RunParams(V0=1000.0, nr=13, nz=17, space_charge_model="none")
    result = run_solver(params)

    for builder in (
        figure_potential,
        figure_field_magnitude,
        figure_interface_overlay,
        figure_residual_profile,
        figure_space_charge,
    ):
        fig = builder(result)
        assert isinstance(fig, go.Figure), f"{builder.__name__} did not return a Figure"


def test_immersed_verification_runs_and_reports_sane_values():
    """The immersed verification tab's backend must run and report physically
    sensible values: an interior recovered angle, a finite onset voltage in the
    kilovolt range, and an imposed-Taylor amplitude identity near 1.0."""
    from solver.app_backend import ImmersedVerificationParams, run_immersed_verification

    result = run_immersed_verification(ImmersedVerificationParams(nr=31, nz=45))
    assert 30.0 <= result.recovered_angle_deg <= 55.0
    assert result.onset_voltage_V is not None and 1e3 < result.onset_voltage_V < 1e6
    assert np.isfinite(result.min_rms_Pa) and result.min_rms_Pa > 0.0
    assert len(result.landscape_angles) >= 10
    assert result.landscape_rms.size == result.landscape_angles.size
    assert result.identity_ratio is not None and 0.95 <= result.identity_ratio <= 1.06
    assert result.phi_identity is not None
    assert result.runtime_s > 0.0
