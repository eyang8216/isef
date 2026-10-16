import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "solver"))
import numpy as np
from solver.config import GridParams, PhysicalParams
from solver.geometry import ImplicitCone
from solver.grid import AxisymmetricGrid
from solver.app_backend import _solve_imposed_taylor, _exponent_crossing_deg
from solver.optimization import flank_field_exponent

def exponent_taylor(nr, nz, angle_deg, cap=0.005):
    g = AxisymmetricGrid.from_params(GridParams(r_max=1.25, z_min=0.0, z_max=1.0, nr=nr, nz=nz))
    cone, phi = _solve_imposed_taylor(g, angle_deg, cap, 0.86)


    return flank_field_exponent(g, cone, phi, z_min=0.30, z_max=0.60, n_interface=41)

for nr, nz in ((61,89),(121,177),(241,353)):
    vals = [(a, exponent_taylor(nr,nz,a)) for a in (46,47,48,49,50,51,52)]
    mono = all(vals[i][1] > vals[i+1][1] for i in range(len(vals)-1))
    cross = _exponent_crossing_deg({a: p for a, p in vals})
    print(f"{nr}x{nz} monotone-decreasing-with-angle={mono}  crossing={cross if cross is None else round(cross,4)}")
    print("   " + "  ".join(f"{a}:{p:+.4f}" for a, p in vals))
