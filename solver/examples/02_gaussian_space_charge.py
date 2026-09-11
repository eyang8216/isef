"""Run a small Gaussian Poisson shielding case.

The sign of rho0 controls whether the prescribed charge distribution shields or
enhances the local field for a particular geometry. This example prints the
solver's shielding metric rather than assuming every sign convention shields.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


from solver.config import GridParams, PhysicalParams, SpaceChargeParams
from solver.geometry import rectangular_electrodes
from solver.grid import AxisymmetricGrid
from solver.space_charge import solve_gaussian_shielding


if __name__ == "__main__":
    grid = AxisymmetricGrid.from_params(GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=51, nz=51))
    masks = rectangular_electrodes(grid, powered="z_max", ground="z_min", far_dirichlet=True)
    physical = PhysicalParams(V0=1000.0)
    params = SpaceChargeParams(
        model="gaussian",
        rho0=-1e-8,
        ell=0.12,
        apex_r=0.0,
        apex_z=0.5,
        relaxation=0.7,
        tolerance=1e-7,
        max_iterations=40,
    )
    result = solve_gaussian_shielding(grid, masks, physical, params)
    print(f"converged: {result.converged} in {result.iterations} iterations")
    print(f"peak |E|: {result.E_mag.max():.6g} V/m")
    print(f"shielding metric S_E: {result.shielding_metric:.6g}")
    print("last iteration:", result.history[-1])
