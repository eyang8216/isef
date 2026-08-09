"""Example 09 — ideal-limit study: grounded-box angle vs domain and cap.

Ticket ``taylor-onset-framing/04`` (P3iii).  Question: does the *actual*
solver configuration (grounded box, ``rectangular_electrodes``) recover
Taylor's 49.29 deg half-angle as the domain grows and the cap shrinks?

**Measured answer (2026-08-09): no — and this is a model property, not a
solver bug.**  Three reproducible facts:

1. The amplitude-projected residual minimum (P2) moves to *larger* angles as
   the box grows: 45 deg (1x1) -> 52.5 (1.5x1.5) -> 60 (2x2) -> 75+ (3x3),
   with the residual still decreasing at the 75 deg sweep edge.
2. The field near the flank is not the ideal conical field: E_n*sqrt(rho)
   (constant for E ~ rho^-1/2) varies by ~45%+ along the flank and the
   deviation *grows* with the box (1x1: 3199->2283; 3x3: 1648->917).  The
   rounded cap regularizes the apex (E finite there), and the finite box
   distorts the mid-flank field.
3. In a large box the flattest cones balance best: at large half-angle the
   flank curvature cos(a)/R and the field profile both become nearly uniform,
   so their shapes match better — the projected residual is a shape-matching
   measure and prefers flat cones there.

**Why the machinery is still correct:** the imposed-Taylor verification
(ticket 03, ``tests/test_taylor_onset.py``) imposes the exact analytic Taylor
field and reproduces the analytic balance amplitude to ratio 1.009 — the
solver's field + residual + projection chain is verified.  The grounded-box
angle is the answer of *that* problem (a truncated perfect cone in a finite
grounded box, no nozzle pinning, no extractor field structure), not Taylor's
meniscus limit.  Taylor's 49.29 deg is a local asymptotic property of the
meniscus near the apex in the conical field; the correct verification is the
imposed-Taylor test, not this grounded-box sweep.
"""

from __future__ import annotations

import numpy as np

from solver.config import GridParams, PhysicalParams
from solver.electrostatics import solve_laplace
from solver.geometry import ImplicitCone, rectangular_electrodes
from solver.grid import AxisymmetricGrid
from solver.immersed import normal_field_on_interface
from solver.optimization import _immersed_masks, _immersed_projected_stats
from solver.verification import taylor_cone_half_angle_deg

ALPHA = taylor_cone_half_angle_deg()  # 49.290089 deg
APEX_Z = 0.86
PHYSICAL = PhysicalParams(V0=1000.0, gamma=0.022)
GRID_SCALE = 60  # cells per unit length


def _projected(grid: AxisymmetricGrid, angle_deg: float, cap: float) -> float:
    cone = ImplicitCone(
        apex_z=APEX_Z + 1e-10 * APEX_Z,
        half_angle_deg=angle_deg,
        apex_radius=cap,
        boundary_value=PHYSICAL.V0,
    )
    external = rectangular_electrodes(grid, powered="z_max", ground="z_min", far_dirichlet=True)
    phi = solve_laplace(grid, _immersed_masks(grid, external, cone), PHYSICAL, immersed=cone)
    return _immersed_projected_stats(
        grid, cone, phi, PHYSICAL, z_min=0.15, z_max=0.85, n_interface=41
    )[0]


def _argmin(rmax: float, zmax: float, cap: float) -> tuple[float | None, dict[float, float]]:
    nr = int(rmax * GRID_SCALE) + 1
    nz = int(zmax * GRID_SCALE) + 1
    grid = AxisymmetricGrid.from_params(GridParams(rmax, 0.0, zmax, nr, nz))
    angles = [35, 40, 45, 47.5, 49.29, 50, 52.5, 55, 57.5, 60, 62.5, 65, 67.5, 70, 72.5, 75]
    if zmax < 1.5:
        angles = [a for a in angles if a <= 52.5]
    rms: dict[float, float] = {}
    for a in angles:
        try:
            rms[a] = _projected(grid, a, cap)
        except (ValueError, RuntimeError):
            continue
    return (min(rms, key=rms.get) if rms else None), rms


def _field_structure(rmax: float, zmax: float) -> None:
    """E_n*sqrt(rho) along the flank at 49.29 deg: constant would mean the
    ideal conical E ~ rho^-1/2 field."""
    grid = AxisymmetricGrid.from_params(
        GridParams(rmax, 0.0, zmax, int(rmax * GRID_SCALE) + 1, int(zmax * GRID_SCALE) + 1)
    )
    cone = ImplicitCone(
        apex_z=APEX_Z + 1e-10 * APEX_Z,
        half_angle_deg=ALPHA,
        apex_radius=0.05,
        boundary_value=PHYSICAL.V0,
    )
    external = rectangular_electrodes(grid, powered="z_max", ground="z_min", far_dirichlet=True)
    phi = solve_laplace(grid, _immersed_masks(grid, external, cone), PHYSICAL, immersed=cone)
    zs = np.linspace(0.30, 0.81, 6)
    rp = np.asarray(cone.surface_radius(zs), float)
    en = np.abs(np.asarray(normal_field_on_interface(grid, phi, cone, rp, zs), dtype=float))
    rho = np.sqrt(rp**2 + (zs - APEX_Z) ** 2)
    print(f"  E_n*sqrt(rho) along the flank ({rmax:.0f}x{zmax:.0f} box, 49.29 deg):")
    print("    " + " ".join(f"rho={ro:.2f}:{e:.0f}" for ro, e in zip(rho, en * np.sqrt(rho))))
    spread = float(np.ptp(en * np.sqrt(rho)) / np.mean(en * np.sqrt(rho)))
    print(f"    spread = {spread:.0%} (0% would be the ideal conical field)")


def main() -> None:
    print(f"Taylor ideal half-angle: {ALPHA:.3f} deg\n")
    print("Part A — grounded-box projected-residual argmin vs domain/cap")
    print(f"{'domain':>7} {'cap':>6} {'argmin':>7}  {'residual at argmin':>19}")
    for rmax, zmax in ((1.0, 1.0), (1.5, 1.5), (2.0, 2.0), (3.0, 3.0)):
        for cap in (0.05, 0.02, 0.01):
            am, rms = _argmin(rmax, zmax, cap)
            r49 = rms.get(49.29)
            if am is None:
                print(f"{rmax:.1f}x{zmax:.1f} {cap:6.3f}   all candidates failed")
                continue
            print(
                f"{rmax:.1f}x{zmax:.1f} {cap:6.3f} {am:6.1f} deg  "
                f"{rms[am]:.4e} Pa   (rms@49.29 = {r49:.3e})"
            )
    print("\n  The argmin moves to larger angles as the box grows — it does NOT")
    print("  approach 49.29 deg. See the docstring for the physical reason.\n")

    print("Part B — is the grounded-box field conical? (E_n*sqrt(rho) should be constant)")
    _field_structure(1.0, 1.0)
    _field_structure(3.0, 3.0)

    print("\nPart C — interpretation")
    print("  The solver machinery is verified by the imposed-Taylor test")
    print("  (tests/test_taylor_onset.py: balance amplitude identity ratio ~1.009).")
    print("  The grounded-box angle is the answer of the truncated-perfect-cone-in-a-box")
    print("  problem, which is not Taylor's meniscus limit; 49.29 deg is a local")
    print("  asymptotic property verified via the imposed field, not via this sweep.")


if __name__ == "__main__":
    main()
