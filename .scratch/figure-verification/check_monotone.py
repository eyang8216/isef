import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "solver"))
import numpy as np
from solver.config import GridParams, PhysicalParams
from solver.geometry import ImplicitCone, rectangular_electrodes
from solver.grid import AxisymmetricGrid
from solver.electrostatics import solve_laplace
from solver.optimization import _immersed_masks, flank_field_exponent

PHYS = PhysicalParams(V0=1000.0, gamma=0.022)

def exponent(nr, nz, angle_deg, cap=0.005):
    g = AxisymmetricGrid.from_params(GridParams(r_max=1.25, z_min=0.0, z_max=1.0, nr=nr, nz=nz))
    cone = ImplicitCone(apex_z=0.86 + 1e-11, half_angle_deg=angle_deg, apex_radius=cap,
                        boundary_value=PHYS.V0)
    ext = rectangular_electrodes(g, powered="z_max", ground="z_min", far_dirichlet=True)
    phi = solve_laplace(g, _immersed_masks(g, ext, cone), PHYS, immersed=cone)
    return flank_field_exponent(g, cone, phi, z_min=0.30, z_max=0.60, n_interface=41)

print("monotonicity in angle at 121x177, cap 0.5%:")
for a in (46.0, 47.0, 48.0, 49.0, 50.0, 51.0, 52.0):
    print(f"  alpha={a:6.2f}  p={exponent(121,177,a):+.5f}")

print("grid convergence of the p=-1 crossing (bisection):")
def crossing(nr, nz, cap):
    f = lambda a: exponent(nr, nz, a, cap) + 1.0
    lo, hi = 46.0, 52.0
    flo = f(lo)
    for _ in range(30):
        mid = 0.5*(lo+hi)
        fm = f(mid)
        if (flo > 0) == (fm > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return 0.5*(lo+hi)

for nr, nz in ((61,89),(121,177),(241,353)):
    print(f"  {nr}x{nz}  crossing = {crossing(nr,nz,0.005):.4f} deg")
