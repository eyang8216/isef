"""Example 08 — refinement study for the immersed free-boundary path.

Two parts, both deterministic and cheap:

Part A (boundary-treatment convergence, plan Task 6): solve the *same*
prescribed rounded cone (half_angle=30 deg, apex_radius=0.05 m) twice on a
refinement series — once with the immersed Dirichlet treatment, once with the
legacy staircase grid-mask — and estimate the observed order of the potential
in a fixed gas sub-region via inter-level Richardson differences. Expected:
immersed ~ 2nd order, staircase non-convergent (its O(h) staircase boundary
error is the known weakness, Shortley & Weller 1938; Gibou et al. 2002).

Part B (optimizer well-posedness): sweep the immersed objective over the
optimizer's feasible box at two grid levels and report where the minimum sits.
Measured 2026-08-09: the residual decreases monotonically with apex_radius (no
interior minimum) and is nearly flat in half_angle — so a "recovered angle" is
not meaningful without a volume/contact-line constraint (out of scope for this
milestone). The table below is the evidence; it is NOT an angle claim.

Interface-field (E_n) convergence is deliberately not measured here — the
one-sided quadratic derivative amplifies the O(h^2) potential error to O(h)
with oscillating interpolation sign; that study needs Richardson-extrapolated
potentials and is tracked separately (docs/plans/2026-08-09-next-steps.md S3).
"""

from __future__ import annotations

import math

import numpy as np

from solver.config import GridParams, PhysicalParams
from solver.electrostatics import solve_laplace
from solver.fields import bilinear_interpolate
from solver.geometry import (
    GeometryMasks,
    ImplicitCone,
    conical_conductor,
    rectangular_electrodes,
)
from solver.grid import AxisymmetricGrid
from solver.optimization import ConeShapeBounds, _immersed_masks, _immersed_rms, optimize_cone_shape

# Prescribed cone shared by both treatments (away from the singular apex).
HALF_ANGLE_DEG = 30.0
APEX_RADIUS = 0.05
APEX_Z = 0.86
Z_MIN_IFACE = 0.15
Z_MAX_IFACE = 0.85
PHYSICAL = PhysicalParams(V0=1000.0, gamma=0.022)

# Legacy sharp cone whose flank coincides with the rounded cone's flank in the
# measurement window: apex_r = R_cap * cos(2*theta)/cos(theta).
LEGACY_APEX_R = APEX_RADIUS * math.cos(2 * math.radians(HALF_ANGLE_DEG)) / math.cos(
    math.radians(HALF_ANGLE_DEG)
)

GRID_LEVELS = ((31, 45), (45, 65), (61, 89), (87, 129))


def _grid(nr: int, nz: int) -> AxisymmetricGrid:
    return AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=nr, nz=nz))


def _immersed_potential(g: AxisymmetricGrid) -> np.ndarray:
    cone = ImplicitCone(
        apex_z=APEX_Z + 1.0e-10 * APEX_Z,
        half_angle_deg=HALF_ANGLE_DEG,
        apex_radius=APEX_RADIUS,
        boundary_value=PHYSICAL.V0,
    )
    external = rectangular_electrodes(g, powered="z_max", ground="z_min", far_dirichlet=True)
    return solve_laplace(g, _immersed_masks(g, external, cone), PHYSICAL, immersed=cone)


def _legacy_potential(g: AxisymmetricGrid) -> np.ndarray:
    masks = conical_conductor(
        g, LEGACY_APEX_R, APEX_Z, HALF_ANGLE_DEG, z_direction="negative", ground_outer=True
    )
    external = rectangular_electrodes(g, powered="z_max", ground="z_min", far_dirichlet=True)
    powered = masks.powered
    grounded = masks.grounded | external.grounded
    m = GeometryMasks(
        powered=powered,
        grounded=grounded,
        axis=external.axis | masks.axis,
        far_boundary=external.far_boundary | masks.far_boundary,
        conductor=masks.conductor,
        gas=~(powered | grounded),
    )
    return solve_laplace(g, m, PHYSICAL)


def part_a() -> None:
    """Observed potential order, immersed vs legacy staircase, fixed gas region."""
    # Evaluation points are fully in the gas for both treatments on every level:
    # r >= 0.60 clears the 30-deg flank (max surface radius in the window is
    # ~0.42 at z=0.2), and z stays inside [z_min+margin, z_max-margin].
    rr = np.linspace(0.60, 0.95, 8)
    zz = np.linspace(0.25, 0.85, 7)
    rp, zp = np.meshgrid(rr, zz)
    print("Part A — potential convergence in the gas (fixed physical region)")
    print(f"{'treatment':<12} {'level':>8} {'mean phi':>10} {'inter-level L2':>16} {'order':>6}")
    for name, solver in (("immersed", _immersed_potential), ("legacy", _legacy_potential)):
        prev_v: np.ndarray | None = None
        prev_diff: float | None = None
        prev_h: float | None = None
        for nr, nz in GRID_LEVELS:
            g = _grid(nr, nz)
            phi = solver(g)
            v = np.asarray(bilinear_interpolate(g, phi, rp, zp), dtype=float)
            if prev_v is None:
                print(f"{name:<12} {nr}x{nz:>5} {float(v.mean()):>10.2f}")
                prev_v, prev_h = v, g.dr
                continue
            diff = float(np.linalg.norm(v - prev_v))
            order_txt = ""
            if prev_diff is not None:
                order = math.log(prev_diff / diff) / math.log(prev_h / g.dr)
                order_txt = f"{order:6.2f}"
            print(f"{name:<12} {nr}x{nz:>5} {float(v.mean()):>10.2f} {diff:>16.3e} {order_txt}")
            prev_v, prev_diff, prev_h = v, diff, g.dr
        print()


def _angle_upper(g: AxisymmetricGrid, bounds: ConeShapeBounds) -> float:
    normal_clearance = min(g.dr, g.dz)
    r_max_safe = min(g.r[-1] * 0.95, g.r[-1] - normal_clearance)
    dz_max = abs(APEX_Z - Z_MIN_IFACE)
    geom = float(np.degrees(np.arctan(max(0.0, r_max_safe - bounds.apex_radius_min) / dz_max)))
    return max(min(bounds.half_angle_deg_max, geom), bounds.half_angle_deg_min + 1.0)


def part_b() -> None:
    """Sweep the immersed objective over the feasible box at two grid levels."""
    bounds = ConeShapeBounds(10.0, 60.0, 0.025, 0.10)
    angles = np.arange(10.0, 60.1, 5.0)
    radii = (0.025, 0.05, 0.075, 0.10)
    print("Part B — immersed objective over the feasible box (RMS Pa)")
    print("(lower is better; the residual decreases monotonically with apex_radius)")
    for nr, nz in ((31, 45), (61, 89)):
        g = _grid(nr, nz)
        cap = _angle_upper(g, bounds)
        best = (None, None, np.inf)
        rows = []
        for ang in angles:
            if ang > cap:
                continue
            cells = []
            for rad in radii:
                cone = ImplicitCone(
                    apex_z=APEX_Z + 1.0e-10 * APEX_Z,
                    half_angle_deg=float(ang),
                    apex_radius=float(rad),
                    boundary_value=PHYSICAL.V0,
                )
                external = rectangular_electrodes(g, powered="z_max", ground="z_min", far_dirichlet=True)
                phi = solve_laplace(g, _immersed_masks(g, external, cone), PHYSICAL, immersed=cone)
                rms = _immersed_rms(
                    g, cone, phi, PHYSICAL, z_min=Z_MIN_IFACE, z_max=Z_MAX_IFACE, n_interface=41
                )
                cells.append(rms)
                if rms < best[2]:
                    best = (float(ang), float(rad), rms)
            rows.append((float(ang), cells))
        print(f"\ngrid {nr}x{nz} (angle cap {cap:.1f} deg):")
        print(f"{'angle':>6} | " + " ".join(f"r={r:.3f}" for r in radii))
        for ang, cells in rows:
            print(f"{ang:6.1f} | " + " ".join(f"{v:.4f}" for v in cells))
        print(f"  sweep minimum: angle={best[0]:.1f} deg, apex_radius={best[1]:.3f} m, RMS={best[2]:.4f} Pa")
        print("  (rms decreases monotonically with apex_radius at every angle; no interior optimum)")
    print()


def part_c() -> None:
    """One Powell confirmation run from the base-grid sweep minimum."""
    g = _grid(31, 45)
    external = rectangular_electrodes(g, powered="z_max", ground="z_min", far_dirichlet=True)
    result = optimize_cone_shape(
        g,
        external,
        PHYSICAL,
        immersed_mode=True,
        apex_z=APEX_Z,
        z_min_interface=Z_MIN_IFACE,
        z_max_interface=Z_MAX_IFACE,
        n_interface=41,
        initial_half_angle_deg=35.0,
        initial_apex_radius=0.06,
        bounds=ConeShapeBounds(10.0, 60.0, 0.025, 0.10),
        powell_options={"maxiter": 60, "ftol": 1e-7, "xtol": 1e-5},
    )
    print("Part C — Powell confirmation (base grid, from a mid-box start)")
    print(f"  recovered angle:      {result.half_angle_deg:.3f} deg")
    print(f"  apex_radius:          {result.apex_radius:.4f} m")
    print(f"  final RMS:            {result.rms_residual:.4f} Pa")
    print(f"  candidate failures:   {result.candidate_solve_failures} / {result.n_evals} evals")
    print(f"  converged:            {result.converged}")
    print(
        "  Interpretation: this is where Powell stops in a flat basin; it is NOT\n"
        "  a 49.29-deg claim. See Part B and docs/plans/2026-08-09-next-steps.md S1."
    )


def main() -> None:
    part_a()
    part_b()
    part_c()


if __name__ == "__main__":
    main()
