"""Solve a simple axisymmetric parallel-plate Laplace case.

This is a sanity-check geometry: phi should vary approximately linearly in z
when the far radial boundary is not forced to ground.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


import numpy as np

from solver.config import GridParams, PhysicalParams
from solver.electrostatics import solve_laplace
from solver.fields import compute_electric_field
from solver.geometry import rectangular_electrodes
from solver.grid import AxisymmetricGrid


if __name__ == "__main__":
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=61, nz=61))
    masks = rectangular_electrodes(grid, powered="z_max", ground="z_min", far_dirichlet=False)
    phi = solve_laplace(grid, masks, PhysicalParams(V0=1000.0))
    Er, Ez, E = compute_electric_field(grid, phi)
    print(f"phi range: {phi.min():.6g} to {phi.max():.6g} V")
    print(f"max |Er| interior: {np.max(np.abs(Er[1:-1,1:-1])):.6g} V/m")
    print(f"median Ez interior: {np.median(Ez[1:-1,1:-1]):.6g} V/m")
    print(f"max |E|: {np.max(E):.6g} V/m")
