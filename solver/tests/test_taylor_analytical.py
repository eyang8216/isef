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


def test_taylor_potential_is_finite_on_singular_axis_ray():
    """The cone-interior axis ray (r = 0, z < apex_z) is singular for
    P_{1/2}(cos theta). The guard must pin those nodes (and the apex) to the
    cone-surface value 0 instead of leaking -inf or ~-1.8e308 into a boundary
    condition."""
    apex_z = 0.86
    z = np.array([0.1, 0.4, apex_z - 1e-6, apex_z])  # last entry is the apex (rho = 0)
    phi = taylor_potential(np.zeros_like(z), z, apex_z, 1.0)
    assert np.all(np.isfinite(phi)), f"non-finite values on singular ray: {phi}"
    assert np.all(phi == 0.0), f"singular-ray nodes should be pinned to 0, got {phi}"


def test_taylor_potential_full_grid_call_has_no_huge_values():
    """The full-grid call used for the Taylor far-field BC must be finite
    everywhere, with no ~1.8e308 values leaking from the singular axis nodes
    below the apex. Points on the exterior axis (r = 0, z > apex_z) stay
    physical and nonzero."""
    apex_z = 0.86
    R, Z = np.meshgrid(np.linspace(0.0, 0.1, 21), np.linspace(0.0, 1.0, 51), indexing="ij")
    phi = taylor_potential(R, Z, apex_z, 1.0)
    assert np.all(np.isfinite(phi))
    assert np.max(np.abs(phi)) < 1e6, f"huge values leaked from the singular ray: {np.max(np.abs(phi)):.3e}"
    assert float(phi[0, -1]) > 0.0  # exterior axis above the apex remains physical
