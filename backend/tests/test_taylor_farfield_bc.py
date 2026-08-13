"""Tests for ticket 04 — analytical Taylor far-field boundary condition."""

from __future__ import annotations

from solver.app_backend import ImmersedVerificationParams, run_immersed_verification


def test_taylor_farfield_recovers_near_ideal_half_angle():
    """The Taylor far-field BC removes the finite-box truncation artifact: the
    recovered half-angle lands near 49.3 deg (vs ~44 deg for the grounded box),
    the residual is small, and the amplitude identity holds."""
    result = run_immersed_verification(ImmersedVerificationParams(bc_type="taylor_farfield"))
    assert 46.0 <= result.recovered_angle_deg <= 52.0, (
        f"Taylor far-field recovered {result.recovered_angle_deg:.2f} deg, expected near 49.3"
    )
    # The ideal Taylor cone is scale-free, so there is no physical onset voltage.
    assert result.onset_voltage_V is None
    assert result.min_rms_Pa < 0.1, f"residual {result.min_rms_Pa:.3e} Pa >= 0.1 Pa"
    assert result.identity_ratio is not None and 0.98 <= result.identity_ratio <= 1.03


def test_grounded_box_remains_available_with_physical_onset():
    """The grounded-box BC is still selectable and reports the truncation
    artifact angle (~44 deg) plus a physical onset voltage in the kV range."""
    result = run_immersed_verification(ImmersedVerificationParams(bc_type="grounded"))
    assert 40.0 <= result.recovered_angle_deg <= 48.0, (
        f"grounded-box recovered {result.recovered_angle_deg:.2f} deg, expected ~44"
    )
    assert result.onset_voltage_V is not None and 1e3 < result.onset_voltage_V < 1e4
