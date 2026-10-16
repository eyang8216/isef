#!/usr/bin/env python3
"""Collect real wall-clock timing data for the immersed Laplace solve.

Measures the actual solver across a range of grid resolutions and writes the
results to ``paper/paper_submission/data/timing_results.txt``.

History (2026-10-16): the previous version of this script inserted a stale
``backend/`` path, imported three modules that do not exist
(``solver.poisson``, ``solver.geometry.generate_axisymmetric_grid``,
``solver.boundaries``), swallowed the resulting ``ImportError``, and fell back
to a *synthetic* model of its own cost: ``0.005 * (N / 675) ** 2.3`` times a
random factor. The paper then quoted that model back as a measurement, which
is why the old table claimed 13.4 s for the 121x177 grid (the real figure is
under 0.5 s) and an ``O(N^2.3)`` scaling that was an input to the generator
rather than a result. That fallback is gone: this script now imports the real
solver and fails loudly if anything is wrong.
"""

from __future__ import annotations

import platform
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "solver"))

import numpy as np  # noqa: E402

from solver.config import GridParams, PhysicalParams  # noqa: E402
from solver.electrostatics import solve_laplace  # noqa: E402
from solver.geometry import ImplicitCone, rectangular_electrodes  # noqa: E402
from solver.grid import AxisymmetricGrid  # noqa: E402
from solver.optimization import _immersed_masks  # noqa: E402

# Same physical scenario as the Section 6 numerical studies: a 49.29 deg
# rounded cone at 1000 V between a powered top electrode and a grounded base,
# with the model unit equal to 10 mm.
PHYSICAL = PhysicalParams(V0=1000.0, gamma=0.022)
GRIDS = (
    (25, 27),
    (49, 53),
    (61, 89),
    (97, 105),
    (121, 177),
    (181, 265),
    (241, 353),
)
REPEATS = 3
OUTPUT_FILE = REPO_ROOT / "paper" / "paper_submission" / "data" / "timing_results.txt"


def build_case(nr: int, nz: int):
    """Return (grid, masks, cone) for the reference immersed-cone problem."""
    grid = AxisymmetricGrid.from_params(
        GridParams(r_max=1.25, z_min=0.0, z_max=1.0, nr=nr, nz=nz)
    )
    cone = ImplicitCone(
        apex_z=0.86 + 1e-11,
        half_angle_deg=49.29,
        apex_radius=0.005,
        boundary_value=PHYSICAL.V0,
    )
    external = rectangular_electrodes(
        grid, powered="z_max", ground="z_min", far_dirichlet=True
    )
    return grid, _immersed_masks(grid, external, cone), cone


def time_solve(grid, masks, cone) -> float:
    """Wall-clock time in seconds for one full immersed Laplace solve."""
    t0 = time.perf_counter()
    potential = solve_laplace(grid, masks, PHYSICAL, immersed=cone)
    elapsed = time.perf_counter() - t0
    if potential is None or not np.all(np.isfinite(potential)):
        raise RuntimeError("solver returned a non-finite potential")
    return elapsed


def collect_timing_data():
    print("=" * 68)
    print("SOLVER PERFORMANCE TIMING (real measured solves)")
    print("=" * 68)
    print(f"{platform.platform()}")
    print(f"{platform.processor() or 'unknown processor'}")
    print()

    results = []
    for nr, nz in GRIDS:
        grid, masks, cone = build_case(nr, nz)
        times = [time_solve(grid, masks, cone) for _ in range(REPEATS)]
        t_median = float(np.median(times))
        results.append({"nr": nr, "nz": nz, "N": nr * nz, "time": t_median})
        print(
            f"{nr:>4}x{nz:<4} N={nr * nz:>7}  "
            f"median {t_median:>8.4f} s   (runs: "
            + ", ".join(f"{t:.4f}" for t in times)
            + ")"
        )

    N = np.array([r["N"] for r in results], dtype=float)
    T = np.array([r["time"] for r in results], dtype=float)
    exponent = float(np.polyfit(np.log(N), np.log(T), 1)[0])
    production = next(r for r in results if (r["nr"], r["nz"]) == (121, 177))

    print()
    print("=" * 68)
    print(f"Scaling analysis: Time ~ N^{exponent:.2f}")
    print(f"Production grid (121x177): {production['time']:.4f} s")
    print("=" * 68)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write("# Solver Performance Timing Results\n")
        f.write("# Measured wall-clock time for one immersed Laplace solve.\n")
        f.write(f"# Generator: experiments/methodology/generate_timing_data.py\n")
        f.write(f"# Host: {platform.platform()} | {platform.processor() or 'unknown'}\n")
        f.write(f"# Scenario: 49.29 deg rounded cone, V0=1000 V, r_max=1.25, model unit 10 mm\n")
        f.write(f"# Repeats per grid: {REPEATS} (median reported)\n")
        f.write(f"# Fitted scaling exponent: N^{exponent:.3f}\n")
        f.write("#\n")
        f.write("nr,nz,N,time_s\n")
        for r in results:
            f.write(f"{r['nr']},{r['nz']},{r['N']},{r['time']:.6f}\n")

    print(f"\nResults saved to: {OUTPUT_FILE}")
    print(
        "\nSuggested LaTeX line for Section 5 (state the actual host):\n"
        r"\paragraph{Computational Performance.} Over the grid range measured here "
        rf"($N={int(N.min())}$ to ${int(N.max())}$ points) the wall-clock time of a "
        rf"single-threaded immersed Laplace solve is fitted by $\mathcal{{O}}(N^{{{exponent:.1f}}})$. "
        rf"A production-quality $121\times177$ grid (21,417 points) solves in approximately "
        rf"{production['time']:.2f}~s on the recorded test host. Sparse direct factorization is "
        r"asymptotically superlinear in two dimensions, so this exponent describes the tested "
        r"range rather than a bound."
    )
    return results


if __name__ == "__main__":
    collect_timing_data()
