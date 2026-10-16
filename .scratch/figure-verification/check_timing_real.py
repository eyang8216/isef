"""Real wall-clock timing for the immersed Laplace solve.

Replaces the synthetic table in paper/paper_submission/data/timing_results.txt,
whose generator (experiments/methodology/generate_timing_data.py) cannot import
the solver and therefore emits base_time * (N/675)**2.3 * noise.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "solver"))

import numpy as np

from solver.config import GridParams, PhysicalParams
from solver.electrostatics import solve_laplace
from solver.geometry import ImplicitCone, rectangular_electrodes
from solver.grid import AxisymmetricGrid
from solver.optimization import _immersed_masks

PHYSICAL = PhysicalParams(V0=1000.0, gamma=0.022)
GRIDS = ((25, 27), (49, 53), (61, 89), (97, 105), (121, 177), (181, 265), (241, 353))

print(f"{'nr':>4} {'nz':>4} {'N':>7} {'nnz':>8} {'time_s':>10}")
rows = []
for nr, nz in GRIDS:
    g = AxisymmetricGrid.from_params(
        GridParams(r_max=1.25, z_min=0.0, z_max=1.0, nr=nr, nz=nz)
    )
    cone = ImplicitCone(
        apex_z=0.86 + 1e-11, half_angle_deg=49.29, apex_radius=0.005,
        boundary_value=PHYSICAL.V0,
    )
    ext = rectangular_electrodes(g, powered="z_max", ground="z_min", far_dirichlet=True)
    masks = _immersed_masks(g, ext, cone)

    t0 = time.perf_counter()
    solve_laplace(g, masks, PHYSICAL, immersed=cone)
    dt = time.perf_counter() - t0

    rows.append((nr, nz, g.size, nr * nz, dt))
    print(f"{nr:>4} {nz:>4} {g.size:>7} {nr * nz:>8} {dt:>10.4f}")

N = np.array([r[2] for r in rows], dtype=float)
T = np.array([r[4] for r in rows], dtype=float)
slope, intercept = np.polyfit(np.log(N), np.log(T), 1)
print(f"\nfitted scaling exponent: N^{slope:.3f}   (recorded table claims N^2.3)")
print(f"recorded synthetic 121x177 time: 13.383901 s")
print(f"measured  121x177 time: {dict(((r[0], r[1]), r[4]) for r in rows)[(121, 177)]:.4f} s")
