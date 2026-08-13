"""Tests for ticket 02 — rescale geometry to realistic mm-scale dimensions."""

from __future__ import annotations

import math

import numpy as np
import pytest

from solver.app_backend import (
    ImmersedVerificationParams,
    RunParams,
    run_immersed_verification,
    run_solver,
)


def _verification_params(spacing: float, nr: int = 31, nz: int = 45) -> ImmersedVerificationParams:
    """Self-similar verification geometry at a given electrode spacing."""
    return ImmersedVerificationParams(
        nr=nr,
        nz=nz,
        electrode_spacing=spacing,
        apex_z=0.86 * spacing,
        apex_radius=0.05 * spacing,
    )


def test_default_verification_geometry_is_mm_scale():
    """The default verification geometry is ~10 mm, not the old ~1 m box."""
    params = ImmersedVerificationParams()
    assert params.electrode_spacing == pytest.approx(10e-3)
    assert params.apex_z == pytest.approx(8.6e-3)
    assert params.apex_radius == pytest.approx(0.5e-3)


def test_onset_voltage_scales_as_sqrt_of_spacing():
    """The predicted onset voltage follows V* ~ sqrt(gamma L / eps0): doubling
    the electrode spacing must raise the onset voltage by ~sqrt(2)."""
    base = run_immersed_verification(_verification_params(10e-3))
    wide = run_immersed_verification(_verification_params(20e-3))
    assert base.onset_voltage_V is not None and wide.onset_voltage_V is not None
    ratio = wide.onset_voltage_V / base.onset_voltage_V
    assert abs(ratio - math.sqrt(2.0)) < 0.2, (
        f"onset ratio {ratio:.3f} does not follow sqrt(spacing) ≈ {math.sqrt(2.0):.3f}"
    )


def test_classic_domain_scales_with_electrode_spacing():
    """run_solver's domain follows electrode_spacing/nozzle_radius (no hardcoded 1 m)."""
    spacing = 20e-3
    result = run_solver(RunParams(
        V0=2500.0, gamma=0.022, electrode_spacing=spacing, nozzle_radius=spacing,
        nr=13, nz=17, space_charge_model="none",
    ))
    assert result.grid_r[-1] == pytest.approx(spacing)
    assert result.grid_z[-1] == pytest.approx(spacing)
    assert np.isfinite(result.peak_field)
