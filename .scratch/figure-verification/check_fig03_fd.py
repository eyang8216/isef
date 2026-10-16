"""Reproduce the immersed-FD side of figure 03 (fixed rounded cone, FD vs P1 FEM).

Setup transcribed from paper/paper_submission/sections/06_numerical_results.tex:24
"domain radius 12.5 mm, axial extent 10 mm, half-angle 49.29 deg, apex z = 8.6 mm,
cap radius 50 um, 1000 V on the cone, outer boundary grounded, 41 interface
points over z = 3-6 mm".

Model length unit = 10 mm (matching solver/examples/08_immersed_refinement_study.py,
where r_max=1.0, z in [0,1], apex_z=0.86).
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
from solver.immersed import normal_field_on_interface
from solver.optimization import _immersed_masks

HALF_ANGLE_DEG = 49.29
APEX_RADIUS = 0.005  # 50 um in 10 mm units
APEX_Z = 0.86  # 8.6 mm
R_MAX = 1.25  # 12.5 mm
PHYSICAL = PhysicalParams(V0=1000.0, gamma=0.022)
LEVELS = ((65, 97), (129, 193), (257, 385))
Z_IFACE = (0.30, 0.60)  # 3-6 mm
N_IFACE = 41

print(f"{'grid':>10} {'phi_rng':>10}  E_n at z=3,4,5,6 mm  (V/mm)")
for nr, nz in LEVELS:
    g = AxisymmetricGrid.from_params(
        GridParams(r_max=R_MAX, z_min=0.0, z_max=1.0, nr=nr, nz=nz)
    )
    cone = ImplicitCone(
        apex_z=APEX_Z + 1.0e-10 * APEX_Z,
        half_angle_deg=HALF_ANGLE_DEG,
        apex_radius=APEX_RADIUS,
        boundary_value=PHYSICAL.V0,
    )
    ext = rectangular_electrodes(g, powered="z_max", ground="z_min", far_dirichlet=True)
    phi = solve_laplace(g, _immersed_masks(g, ext, cone), PHYSICAL, immersed=cone)

    iface = cone.sample_graph(Z_IFACE[0], Z_IFACE[1], N_IFACE)
    En = np.asarray(normal_field_on_interface(g, phi, cone, iface.r, iface.z), dtype=float)

    # model units -> mm: E_n [V/unit] * (1 unit / 10 mm) = V/mm
    En_v_mm = np.abs(En) / 10.0
    z_mm = iface.z * 10.0

    probes = []
    for zt in (3.0, 4.0, 5.0, 6.0):
        probes.append(float(np.interp(zt, z_mm, En_v_mm)))

    # Maxwell pressure eps0/2 * En^2 in Pa at 1000 V
    pmax = 0.5 * PHYSICAL.eps_g * En**2
    print(
        f"{nr:>4}x{nz:<5} {phi.min():>8.2f}  "
        + "  ".join(f"{p:8.2f}" for p in probes)
        + f"   | p_Max @3..6mm: {np.interp(3.0, z_mm, pmax):.3f} {np.interp(6.0, z_mm, pmax):.3f} Pa"
    )
