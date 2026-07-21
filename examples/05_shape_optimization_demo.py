"""Example 05 — Shape optimization demo in the Laplace limit.

Runs the Powell optimizer over a cone-family parameterization to find the
interface that minimises the Young-Laplace-Maxwell RMS residual. Uses a
conical conductor geometry (powered electrode at the Taylor angle) to
produce a field that resembles the classical Taylor-cone setup.

Primary validation: the recovered half-angle should be near 49.3°. The
grid-mask conical conductor introduces geometry errors (see IMPLEMENTATION_STATUS.md),
so exact recovery is not expected — but the optimizer should converge toward
the right neighborhood.

Usage:
    python examples/05_shape_optimization_demo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from solver.config import GridParams, PhysicalParams
from solver.geometry import conical_conductor
from solver.grid import AxisymmetricGrid
from solver.optimization import ConeShapeBounds, optimize_cone_shape
from solver.verification import taylor_cone_half_angle_deg


def main() -> None:
    theoretical = taylor_cone_half_angle_deg()
    print(f"Theoretical Taylor half-angle: {theoretical:.4f}°")

    # Conical conductor at the theoretical Taylor angle as the powered electrode.
    # Ground outer boundary. Apex at z=3.5 pointing downward.
    grid = AxisymmetricGrid.from_params(
        GridParams(r_max=3.0, z_min=0.0, z_max=4.0, nr=31, nz=51)
    )
    apex_z = 3.5
    masks = conical_conductor(
        grid,
        apex_r=0.0,
        apex_z=apex_z,
        half_angle_deg=theoretical,
        z_direction="negative",
        ground_outer=True,
    )
    physical = PhysicalParams(V0=1000.0, gamma=0.022)

    print(f"Grid: {grid.nr}×{grid.nz}  ({grid.size} unknowns)")
    print("Running Powell optimizer over cone-family shape parameters...")

    result = optimize_cone_shape(
        grid, masks, physical,
        n_interface=41,
        initial_half_angle_deg=45.0,
        initial_apex_radius=1e-4,
        apex_z=apex_z,
        z_min_interface=0.5,
        z_max_interface=apex_z - 0.05,
        bounds=ConeShapeBounds(
            half_angle_deg_min=5.0,
            half_angle_deg_max=89.0,
            apex_radius_min=1e-6,
            apex_radius_max=0.1,
        ),
        powell_options={"maxiter": 800, "ftol": 1e-10, "xtol": 1e-8},
    )

    print(f"\nOptimized half-angle: {result.half_angle_deg:.4f}°")
    print(f"RMS residual:         {result.rms_residual:.4e} Pa")
    print(f"Apex radius:          {result.apex_radius:.2e} m")
    print(f"Function evaluations: {result.n_evals}")
    print(f"Converged:            {result.converged}")

    deviation = abs(result.half_angle_deg - theoretical)
    print(f"\nDeviation from Taylor limit: {deviation:.2f}°")
    if deviation < 15.0:
        print("✓ Recovered angle is within 15° of the Taylor limit.")
        print("  Residual deviation is expected: the conical-conductor geometry")
        print("  uses a grid mask (not a sharp immersed boundary), which shifts")
        print("  the optimal angle away from 49.3°.")
    else:
        print(f"✗ Deviation {deviation:.1f}° exceeds 15° — check optimizer or geometry.")


if __name__ == "__main__":
    main()
