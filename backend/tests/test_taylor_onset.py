"""Imposed-Taylor free-boundary verification (ticket taylor-onset-framing/03).

Imposes the exact analytic Taylor potential ``phi = A rho^1/2 P_1/2(cos theta)``
on the box boundary with the rounded ``ImplicitCone`` as the immersed zero
equipotential, then checks three things:

1. **Amplitude identity**: the amplitude-projected onset voltage at the Taylor
   angle matches the analytic balance amplitude
   ``A* = sqrt(2 gamma cos(alpha) / (eps0 P^1_1/2(cos(pi-alpha))^2 sin(alpha)))``
   to within 3% (the cone is at potential 0 here, so the projection is
   normalized to the imposed outer amplitude, ``V0 = A``).

2. **Flank exponent crossing**: the flank field ``E_n^2 ~ rho^p`` crosses
   ``p = -1`` (the scale-consistency condition of the Young-Laplace-Maxwell
   balance, since capillary ``gamma kappa ~ cot(alpha)/rho`` on the flank)
   within ~0.1 deg of the ideal 49.29 deg.  This is the committed half-angle
   observable: the projected-residual argmin is flat to within its
   discretization floor near the minimum and wanders with grid/cap/window
   (measured 2026-08-16: 47.6-52 deg), while the exponent is monotone in the
   half-angle and grid-convergent.

3. **Floor improves with refinement**: the residual floor at the minimum
   shrinks as the grid refines.

Measured 2026-08-16 (cap=0.001, window [0.30, 0.60]): identity ratio
1.0005-1.0032; exponent crossing 49.18 (61x89), 49.21 (121x177), 49.26
(241x353) — within 0.03-0.11 deg of the ideal 49.29 deg.  The free-boundary
recovery (app backend, cap=0.5% of spacing) measures 49.13 (61x89) and
49.20 (121x177).
"""

from __future__ import annotations

import numpy as np
from scipy.special import lpmv
from scipy.sparse.linalg import spsolve

from solver.config import GridParams, PhysicalParams
from solver.geometry import ImplicitCone
from solver.grid import AxisymmetricGrid
from solver.operators import build_axisymmetric_laplacian
from solver.boundary_conditions import apply_dirichlet_values
from solver.immersed import apply_immersed_dirichlet
from solver.optimization import _immersed_projected_stats, flank_field_exponent
from solver.taylor_analytical import taylor_potential
from solver.verification import taylor_cone_half_angle_deg

ALPHA = taylor_cone_half_angle_deg()  # 49.290089 deg
THETA0 = np.radians(180.0 - ALPHA)  # cone polar angle; P_1/2(cos THETA0) = 0
APEX_Z = 0.86
GAMMA = 0.022
EPS0 = 8.8541878128e-12
P1 = lpmv(1, 0.5, np.cos(THETA0))
# Analytic balance amplitude for the imposed Taylor field: p_E = 1/2 eps0 E_n^2
# with E_n = A rho^-1/2 |P^1| equals the code's capillary term
# p_gamma = gamma * kappa with kappa = cos(alpha)/R (the code's SUM-curvature
# convention, R = rho sin(alpha) on the flank) -> A*^2 = 2 gamma cos(alpha) /
# (eps0 (P^1)^2 sin(alpha)). The factor 2 comes from the 1/2 eps0 and the sum
# (not mean) curvature.
ANALYTIC_AMPLITUDE = np.sqrt(2.0 * GAMMA * np.cos(np.radians(ALPHA)) / (EPS0 * P1**2 * np.sin(np.radians(ALPHA))))
# Flank sampling window: [0.30, 0.60] of the domain keeps well below the apex
# (cap and sub-grid singularity) and clear of the base walls; [0.30, 0.75]
# adds near-apex samples whose E_n reconstruction error dominates the
# projected residual (measured 2026-08-16).
ZWIN = (0.30, 0.60)


def _solve_imposed_taylor(grid: AxisymmetricGrid, angle_deg: float, cap: float) -> tuple[ImplicitCone, np.ndarray]:
    """Solve Laplace with the analytic Taylor potential on the box ring and the
    rounded cone (candidate angle, cap) as the immersed zero equipotential."""
    cone = ImplicitCone(
        apex_z=APEX_Z + 1e-10 * APEX_Z,
        half_angle_deg=angle_deg,
        apex_radius=cap,
        boundary_value=0.0,
    )
    phi_outer = taylor_potential(grid.R, grid.Z, APEX_Z, 1.0)
    # Dirichlet ring on all four box sides. The bottom row (z=0) is almost
    # entirely inside the cone (the flank reaches r ~ 1.0 there) and is
    # overridden to 0 by the immersed pass; only the gas sliver keeps the
    # analytic value, which is harmless.
    outer = np.zeros(grid.shape, bool)
    outer[-1, :] = True
    outer[:, 0] = True
    outer[:, -1] = True
    outer[0, :] = True
    Aop = build_axisymmetric_laplacian(grid)
    Aop, b = apply_dirichlet_values(Aop, np.zeros(grid.size), grid, outer, phi_outer)
    Aop, b = apply_immersed_dirichlet(Aop, b, grid, cone, fixed_mask=outer)
    return cone, grid.unflatten(spsolve(Aop, b))


def _projected(grid: AxisymmetricGrid, angle_deg: float, cap: float) -> tuple[float, float]:
    """(rms, onset_voltage) of the amplitude-projected residual.  The cone is at
    potential 0 here, so the projection is normalized to the imposed outer
    amplitude (V0 = A = 1); V0* then equals the best-fit balance amplitude."""
    cone, phi = _solve_imposed_taylor(grid, angle_deg, cap)
    # The flank window stays well below the apex (join_z >= 0.859 at cap<=0.001)
    # and clear of the bottom boundary.
    return _immersed_projected_stats(
        grid, cone, phi, PhysicalParams(V0=1.0, gamma=GAMMA),
        z_min=ZWIN[0], z_max=ZWIN[1], n_interface=41,
    )


def _exponent(grid: AxisymmetricGrid, angle_deg: float, cap: float) -> float:
    """Flank power-law exponent p of E_n^2 ~ rho^p for one candidate angle."""
    cone, phi = _solve_imposed_taylor(grid, angle_deg, cap)
    return flank_field_exponent(
        grid, cone, phi, z_min=ZWIN[0], z_max=ZWIN[1], n_interface=41,
    )


def _exponent_crossing(grid: AxisymmetricGrid, cap: float) -> float:
    """Half-angle where p(alpha) + 1 changes sign over the sweep [47, 52]."""
    angles = np.arange(47.0, 52.01, 1.0)
    ps = np.array([_exponent(grid, float(a), cap) for a in angles])
    for i in range(len(angles) - 1):
        lo, hi = ps[i] + 1.0, ps[i + 1] + 1.0
        if lo * hi <= 0.0:
            t = lo / (lo - hi)
            return float(angles[i] + t * (angles[i + 1] - angles[i]))
    raise AssertionError(f"exponent p+1 never crosses zero: {ps}")


def test_imposed_taylor_amplitude_identity():
    """The projected onset voltage at the Taylor angle matches the analytic
    balance amplitude (within 3%) at the smallest cap."""
    grid = AxisymmetricGrid.from_params(GridParams(1.0, 0.0, 1.0, 121, 177))
    rms, v0 = _projected(grid, ALPHA, 0.001)
    assert np.isfinite(rms)
    ratio = v0 / ANALYTIC_AMPLITUDE
    assert 0.98 <= ratio <= 1.03, (
        f"amplitude identity ratio {ratio:.4f} outside [0.98, 1.03] "
        f"(V0*={v0:.4e}, A*={ANALYTIC_AMPLITUDE:.4e})"
    )


def test_imposed_taylor_exponent_crossing_near_ideal():
    """The flank exponent crossing (p = -1) recovers the ideal angle within
    ~0.1 deg at 121x177 and improves with refinement.

    Measured 2026-08-16: 49.18 (61x89), 49.21 (121x177), 49.26 (241x353).
    """
    for nr, nz, tol in ((61, 89, 0.2), (121, 177, 0.15), (241, 353, 0.1)):
        grid = AxisymmetricGrid.from_params(GridParams(1.0, 0.0, 1.0, nr, nz))
        cross = _exponent_crossing(grid, 0.001)
        assert abs(cross - ALPHA) <= tol, (
            f"exponent crossing {cross:.3f} deg at {nr}x{nz} deviates from "
            f"ideal {ALPHA:.3f} deg by {abs(cross - ALPHA):.3f} deg (> {tol})"
        )


def test_imposed_taylor_floor_improves_with_refinement():
    """The residual floor at the minimum shrinks as the grid refines."""
    floors = []
    for nr, nz in ((61, 89), (121, 177)):
        grid = AxisymmetricGrid.from_params(GridParams(1.0, 0.0, 1.0, nr, nz))
        angles = np.arange(48.0, 52.01, 1.0)
        rms = {a: _projected(grid, a, 0.001)[0] for a in angles}
        floors.append(min(rms.values()))
    assert floors[1] < floors[0], f"residual floor did not improve with refinement ({floors})"


def test_free_boundary_recovers_taylor_angle():
    """The app-backend free-boundary verification recovers the Taylor half-angle
    within 0.2 deg via the flank exponent crossing (Taylor far field, default
    0.5% apex cap).

    Measured 2026-08-16: 49.13 deg at 61x89 and 49.20 deg at 121x177
    (ideal 49.290089 deg).  This is the regression that guards the committed
    fix for the previous ~1.3 deg residual-argmin bias (48.0 deg).
    """
    from solver.app_backend import ImmersedVerificationParams, run_immersed_verification

    for nr, nz, tol in ((61, 89, 0.25), (121, 177, 0.2)):
        result = run_immersed_verification(ImmersedVerificationParams(nr=nr, nz=nz))
        assert result.recovered_angle_method == "exponent_crossing"
        assert abs(result.recovered_angle_deg - ALPHA) <= tol, (
            f"free-boundary recovered angle {result.recovered_angle_deg:.3f} deg "
            f"at {nr}x{nz} deviates from ideal {ALPHA:.3f} deg by "
            f"{abs(result.recovered_angle_deg - ALPHA):.3f} deg (> {tol})"
        )
        assert result.identity_ratio is not None and 0.98 <= result.identity_ratio <= 1.03
