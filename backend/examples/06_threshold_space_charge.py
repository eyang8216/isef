"""Example 06 — Threshold-activated space-charge shielding.

Demonstrates solve_threshold_shielding() on a simple rectangular domain.
Prints the apex-local (interior) shielding metric S_E > 0 confirming field
reduction relative to the Laplace baseline.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from solver.config import GridParams, PhysicalParams, SpaceChargeParams
from solver.electrostatics import solve_laplace
from solver.fields import compute_electric_field
from solver.geometry import rectangular_electrodes
from solver.grid import AxisymmetricGrid
from solver.space_charge import shielding_metric, solve_threshold_shielding
import numpy as np


def main() -> None:
    grid = AxisymmetricGrid.from_params(
        GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=41, nz=41)
    )
    masks = rectangular_electrodes(grid, powered="z_max", ground="z_min", far_dirichlet=True)
    physical = PhysicalParams(V0=1000.0)

    params = SpaceChargeParams(
        model="threshold",
        E_c=500.0,    # V/m — charge activates above this field
        E_s=300.0,    # V/m — activation sharpness scale
        rho_max=1e-8, # C/m³ — peak charge density (~1 V perturbation on 1000 V domain)
        relaxation=0.5,
        tolerance=1e-7,
        max_iterations=80,
    )

    print(f"Grid: {grid.nr}×{grid.nz}  ({grid.size} unknowns)")
    print(f"Threshold closure: E_c={params.E_c:.0f} V/m  E_s={params.E_s:.0f} V/m  rho_max={params.rho_max:.0e} C/m³")

    result = solve_threshold_shielding(grid, masks, physical, params)

    print(f"\nConverged: {result.converged}  ({result.iterations} iterations)")
    print(f"Peak |E| (shielded): {np.max(result.E_mag):.2f} V/m")
    print(f"Max rho_e activated: {np.max(result.rho_e):.3e} C/m³")

    # Reference Laplace field
    phi_laplace = solve_laplace(grid, masks, physical)
    _, _, E_laplace = compute_electric_field(grid, phi_laplace)
    print(f"Peak |E| (Laplace):  {np.max(E_laplace):.2f} V/m")

    # Interior shielding metric — excludes Dirichlet boundary nodes where the field
    # is fixed regardless of charge. In a rectangular test domain without a cone
    # interface, the interior is the correct proxy for the apex-local region.
    interior = np.zeros(grid.shape, dtype=bool)
    interior[1:-1, 1:-1] = True
    s_interior = shielding_metric(result.E_mag, E_laplace, mask=interior)
    print(f"\nInterior shielding metric S_E = {s_interior:.6f}  (>0 means field reduced)")

    if s_interior > 0:
        print("✓ Threshold closure produces positive shielding in the interior.")
    else:
        print("✗ Shielding metric is non-positive — check parameters.")


if __name__ == "__main__":
    main()
