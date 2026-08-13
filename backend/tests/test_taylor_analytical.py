"""Tests for the shared analytical Taylor-cone potential."""

from __future__ import annotations

import numpy as np

from solver.taylor_analytical import taylor_potential
from solver.verification import taylor_cone_half_angle_deg


def test_taylor_potential_is_zero_on_ideal_cone_surface():
    """The ideal half-angle cone surface is the zero equipotential of the
    analytical exterior solution (P_{1/2}(cos theta_T) = 0 defines theta_T)."""
    alpha = np.radians(taylor_cone_half_angle_deg())
    apex_z = 0.86
    dz = np.linspace(0.001, 0.01, 20)  # distance below the apex along the flank
    z = apex_z - dz
    r = dz * np.tan(alpha)
    phi = taylor_potential(r, z, apex_z, 1.0)
    assert np.max(np.abs(phi)) < 1e-8, (
        f"potential should vanish on the ideal cone surface (got max |phi| = {np.max(np.abs(phi)):.3e})"
    )


def test_taylor_potential_scales_with_amplitude_and_handles_apex():
    """Amplitude is a linear prefactor, and the apex (rho=0) limit is 0."""
    apex_z = 0.86
    # cos(theta) = 0 (theta = 90 deg), a regular gas-region point where
    # P_{1/2}(0) is finite and nonzero — avoids the singular axis at theta=180 deg.
    r = np.array([0.5])
    z = np.array([apex_z])
    a1 = taylor_potential(r, z, apex_z, 1.0)
    a3 = taylor_potential(r, z, apex_z, 3.0)
    np.testing.assert_allclose(a3, 3.0 * a1)
    assert abs(float(a1[0])) > 0.0  # nonzero off the cone surface
    with np.errstate(divide="ignore", invalid="ignore"):
        apex_value = float(taylor_potential(0.0, apex_z, apex_z, 2.5))
    assert apex_value == 0.0
