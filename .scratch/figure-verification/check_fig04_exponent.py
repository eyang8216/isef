"""Partial reproduction of figure 04(b): flank field exponent p(alpha) vs half-angle.

The campaign script (validation_campaign.py) is absent, so this only checks that
the exponent machinery in solver/solver/optimization.py:152 produces a p = -1
crossing in the neighbourhood of the angle the paper reports (49.067-49.176 deg,
06_numerical_results.tex:30).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "solver"))

import numpy as np

from solver.config import GridParams, PhysicalParams
from solver.electrostatics import solve_laplace
from solver.geometry import ImplicitCone, rectangular_electrodes
from solver.grid import AxisymmetricGrid
from solver.optimization import _immersed_masks, flank_field_exponent

PHYSICAL = PhysicalParams(V0=1000.0, gamma=0.022)
APEX_Z = 0.86
APEX_RADIUS = 0.005  # "0.5% cap"
Z_IFACE = (0.30, 0.60)
N_IFACE = 41

for nr, nz in ((61, 89), (81, 117), (41, 59)):
    g = AxisymmetricGrid.from_params(
        GridParams(r_max=1.25, z_min=0.0, z_max=1.0, nr=nr, nz=nz)
    )
    ext = rectangular_electrodes(g, powered="z_max", ground="z_min", far_dirichlet=True)
    alphas, ps = [], []
    for alpha in np.arange(46.0, 52.01, 0.25):
        cone = ImplicitCone(
            apex_z=APEX_Z + 1.0e-10 * APEX_Z,
            half_angle_deg=float(alpha),
            apex_radius=APEX_RADIUS,
            boundary_value=PHYSICAL.V0,
        )
        phi = solve_laplace(g, _immersed_masks(g, ext, cone), PHYSICAL, immersed=cone)
        p = flank_field_exponent(
            g, cone, phi, z_min=Z_IFACE[0], z_max=Z_IFACE[1], n_interface=N_IFACE
        )
        alphas.append(float(alpha))
        ps.append(p)
    alphas_a = np.array(alphas)
    ps_a = np.array(ps)
    crossing = np.nan
    sign = np.sign(ps_a + 1.0)
    idx = np.nonzero(np.diff(sign) != 0)[0]
    if idx.size:
        i = idx[-1]
        crossing = float(
            alphas_a[i] + (alphas_a[i + 1] - alphas_a[i]) * (0.0 - ps_a[i] - 1.0) / (ps_a[i + 1] - ps_a[i])
        )
    print(f"{nr}x{nz:<4} p(46)={ps_a[0]:+.4f}  p(49.29)={np.interp(49.29, alphas_a, ps_a):+.4f}  "
          f"p(52)={ps_a[-1]:+.4f}  p=-1 crossing at {crossing:.3f} deg")
