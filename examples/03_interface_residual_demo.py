
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""Evaluate Young-Laplace-Maxwell residual on a prescribed conical interface."""

import numpy as np

from solver.config import GridParams, PhysicalParams
from solver.electrostatics import solve_laplace
from solver.fields import compute_electric_field
from solver.geometry import rectangular_electrodes
from solver.grid import AxisymmetricGrid
from solver.interface import GraphInterface
from solver.residual import compute_residual


if __name__ == "__main__":
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=81, nz=81))
    physical = PhysicalParams(V0=1000.0, gamma=0.022)
    masks = rectangular_electrodes(grid, powered="z_max", ground="z_min", far_dirichlet=False)
    phi = solve_laplace(grid, masks, physical)
    Er, Ez, _ = compute_electric_field(grid, phi)

    z = np.linspace(0.15, 0.85, 80)
    alpha = 49.3
    R = 0.08 + (z - z.min()) * np.tan(np.deg2rad(alpha)) * 0.2
    interface = GraphInterface(z=z, R=R)
    diag = compute_residual(grid, interface, Er, Ez, physical)
    print(f"half angle estimate: {diag.half_angle_deg:.6g} deg")
    print(f"Delta_p mean-subtracted: {diag.delta_p:.6e} Pa")
    print(f"RMS residual: {diag.rms_residual:.6e} Pa")
    print(f"max |residual|: {diag.max_abs_residual:.6e} Pa")
