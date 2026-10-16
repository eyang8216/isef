"""Generate Figure 5 (multistart optimizer study) with the in-repository solver.

Five Powell restarts of the immersed free-boundary objective are run on the
31x45 grid from the start pairs plotted in the paper.  Each restart minimises
the amplitude-projected Young-Laplace-Maxwell residual over the analytic cone
family (half-angle, apex radius); the endpoints and their final residuals are
written to ``paper/paper_submission/data/multistart_results.txt`` and drawn in
``paper/paper_submission/figures/05_optimizer_multistart.png``.

Units: one model length unit corresponds to 10 mm for this case (the model
domain is ``z_max = 1.0`` against a nominal 10 mm axial extent), so apex radii
are reported in millimetres.  The optimizer works in model units, where the
prescribed box is ``apex_radius in [0.025, 0.10]``, i.e. 0.25 mm to 1.00 mm.

Usage::

    PYTHONPATH=solver python experiments/methodology/generate_multistart_figure.py

Pass ``--rerun`` to re-run the five optimizations even when a previous result
table is present; by default the table is reused so that only the figure is
redrawn.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "solver"))

from solver.config import GridParams, PhysicalParams  # noqa: E402
from solver.geometry import rectangular_electrodes  # noqa: E402
from solver.grid import AxisymmetricGrid  # noqa: E402
from solver.optimization import ConeShapeBounds, optimize_cone_shape  # noqa: E402

# --------------------------------------------------------------------------
# Case definition (identical to solver/examples/08_immersed_refinement_study.py
# Part C, evaluated on the coarse production grid used for the study).
# --------------------------------------------------------------------------
NR, NZ = 31, 45
R_MAX = 1.0
Z_MAX = 1.0
APEX_Z = 0.86
Z_MIN_IFACE = 0.15
Z_MAX_IFACE = 0.85
N_INTERFACE = 41
PHYSICAL = PhysicalParams(V0=1000.0, gamma=0.022)
BOUNDS = ConeShapeBounds(10.0, 60.0, 0.025, 0.10)
POWELL_OPTIONS = {"maxiter": 60, "ftol": 1e-7, "xtol": 1e-5}

MODEL_UNIT_MM = 10.0

# (half_angle_deg, apex_radius) starting pairs plotted in the paper.
STARTS = (
    (15.0, 0.030),
    (25.0, 0.085),
    (35.0, 0.060),
    (45.0, 0.035),
    (55.0, 0.090),
)

FIGURE_PATH = REPO_ROOT / "paper" / "paper_submission" / "figures" / "05_optimizer_multistart.png"
DATA_PATH = REPO_ROOT / "paper" / "paper_submission" / "data" / "multistart_results.txt"

START_COLOR = "#1f77b4"
ENDPOINT_COLOR = "#b8720d"


def build_case() -> tuple[AxisymmetricGrid, object]:
    grid = AxisymmetricGrid.from_params(
        GridParams(r_max=R_MAX, z_min=0.0, z_max=Z_MAX, nr=NR, nz=NZ)
    )
    external = rectangular_electrodes(grid, powered="z_max", ground="z_min", far_dirichlet=True)
    return grid, external


def run_starts() -> list[dict]:
    """Run every prescribed restart and collect its endpoint and residual."""
    grid, external = build_case()
    rows = []
    for index, (angle0, radius0) in enumerate(STARTS, start=1):
        result = optimize_cone_shape(
            grid,
            external,
            PHYSICAL,
            immersed_mode=True,
            apex_z=APEX_Z,
            z_min_interface=Z_MIN_IFACE,
            z_max_interface=Z_MAX_IFACE,
            n_interface=N_INTERFACE,
            initial_half_angle_deg=angle0,
            initial_apex_radius=radius0,
            bounds=BOUNDS,
            powell_options=POWELL_OPTIONS,
        )
        rows.append(
            {
                "index": index,
                "angle_start_deg": angle0,
                "radius_start": radius0,
                "angle_deg": result.half_angle_deg,
                "radius": result.apex_radius,
                "rms_residual_Pa": result.rms_residual,
                "n_evals": result.n_evals,
                "candidate_solve_failures": result.candidate_solve_failures,
                "converged": bool(result.converged),
            }
        )
        print(
            f"start {index}: ({angle0:.1f} deg, {radius0:.4f}) -> "
            f"({result.half_angle_deg:.3f} deg, {result.apex_radius:.4f}, "
            f"{result.rms_residual:.5f} Pa, {result.n_evals} evals, "
            f"converged={bool(result.converged)})"
        )
    return rows


def write_data_file(rows: list[dict]) -> None:
    lines = [
        "# Multistart Powell optimization, immersed free-boundary objective",
        f"# Grid: {NR}x{NZ} (r_max={R_MAX}, z_max={Z_MAX}), n_interface={N_INTERFACE}, "
        f"apex_z={APEX_Z}, interface window {Z_MIN_IFACE}-{Z_MAX_IFACE}",
        f"# Bounds: half_angle in [{BOUNDS.half_angle_deg_min}, {BOUNDS.half_angle_deg_max}] deg, "
        f"apex_radius in [{BOUNDS.apex_radius_min}, {BOUNDS.apex_radius_max}] model units",
        f"# One model length unit = {MODEL_UNIT_MM:g} mm; apex radii below are model units unless noted",
        f"# Powell options: maxiter={POWELL_OPTIONS['maxiter']}, ftol={POWELL_OPTIONS['ftol']}, "
        f"xtol={POWELL_OPTIONS['xtol']}",
        "Start_index,Angle_start_deg,Radius_start,Angle_final_deg,Radius_final,"
        "Radius_final_mm,RMS_residual_Pa,N_evals,Candidate_solve_failures,Converged",
    ]
    for row in rows:
        lines.append(
            f"{row['index']},{row['angle_start_deg']:.3f},{row['radius_start']:.4f},"
            f"{row['angle_deg']:.4f},{row['radius']:.4f},"
            f"{row['radius'] * MODEL_UNIT_MM:.4f},{row['rms_residual_Pa']:.6f},"
            f"{row['n_evals']},{row['candidate_solve_failures']},{row['converged']}"
        )
    angles = [row["angle_deg"] for row in rows]
    radii = [row["radius"] for row in rows]
    rms = [row["rms_residual_Pa"] for row in rows]
    lines.append(
        f"# Summary: angle {min(angles):.3f}-{max(angles):.3f} deg, "
        f"radius {min(radii) * MODEL_UNIT_MM:.4f}-{max(radii) * MODEL_UNIT_MM:.4f} mm, "
        f"RMS residual {min(rms):.5f}-{max(rms):.5f} Pa"
    )
    DATA_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {DATA_PATH}")


def load_data_file() -> list[dict]:
    """Read a previously written result table."""
    rows = []
    for line in DATA_PATH.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        fields = line.split(",")
        if not fields[0].strip().isdigit():
            continue  # column header
        rows.append(
            {
                "index": int(fields[0]),
                "angle_start_deg": float(fields[1]),
                "radius_start": float(fields[2]),
                "angle_deg": float(fields[3]),
                "radius": float(fields[4]),
                "rms_residual_Pa": float(fields[6]),
                "n_evals": int(fields[7]),
                "candidate_solve_failures": int(fields[8]),
                "converged": fields[9].strip().lower() == "true",
            }
        )
    return rows


def create_figure(rows: list[dict]) -> None:
    figure, (ax_start, ax_residual) = plt.subplots(1, 2, figsize=(12.4, 5.0))

    start_angle = [row["angle_start_deg"] for row in rows]
    start_radius = [row["radius_start"] * MODEL_UNIT_MM for row in rows]
    final_angle = [row["angle_deg"] for row in rows]
    final_radius = [row["radius"] * MODEL_UNIT_MM for row in rows]

    for angle0, radius0, angle1, radius1 in zip(
        start_angle, start_radius, final_angle, final_radius
    ):
        ax_start.plot([angle0, angle1], [radius0, radius1], color="0.65", linewidth=1.2, zorder=1)
    ax_start.scatter(
        start_angle,
        start_radius,
        s=110,
        marker="o",
        color=START_COLOR,
        edgecolor="white",
        linewidth=1.0,
        zorder=3,
        label="Specified start",
    )
    ax_start.scatter(
        final_angle,
        final_radius,
        s=110,
        marker="s",
        color=ENDPOINT_COLOR,
        edgecolor="white",
        linewidth=1.0,
        zorder=3,
        label="Endpoint",
    )
    for row in rows:
        ax_start.annotate(
            str(row["index"]),
            (row["angle_deg"], row["radius"] * MODEL_UNIT_MM),
            textcoords="offset points",
            xytext=(7, 5),
            fontsize=11,
            color=ENDPOINT_COLOR,
        )
    ax_start.set_xlabel(r"Half-angle [$^\circ$]")
    ax_start.set_ylabel("Apex radius [mm]")
    ax_start.set_title("(a) Starts and endpoints")
    ax_start.set_xticks(np.arange(15, 60, 5))
    ax_start.grid(True, color="0.88", linewidth=0.8)
    ax_start.set_axisbelow(True)
    ax_start.legend(loc="upper left", framealpha=0.95)
    residual = [row["rms_residual_Pa"] for row in rows]
    ax_residual.bar(
        [row["index"] for row in rows],
        residual,
        width=0.7,
        color=ENDPOINT_COLOR,
        edgecolor="white",
        linewidth=0.8,
    )
    ax_residual.set_xlabel("Start index")
    ax_residual.set_ylabel("Final projected RMS [Pa]")
    ax_residual.set_title("(b) Final residual")
    ax_residual.set_xticks([row["index"] for row in rows])
    ax_residual.set_ylim(0.0, 1.05 * max(residual))
    ax_residual.grid(True, axis="y", color="0.88", linewidth=0.8)
    ax_residual.set_axisbelow(True)

    for axis in (ax_start, ax_residual):
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)

    figure.tight_layout()
    figure.savefig(FIGURE_PATH, dpi=250, bbox_inches="tight")
    plt.close(figure)
    print(f"wrote {FIGURE_PATH}")


def main() -> None:
    if DATA_PATH.exists() and "--rerun" not in sys.argv:
        rows = load_data_file()
        print(f"reusing {DATA_PATH} (pass --rerun to repeat the optimizations)")
    else:
        rows = run_starts()
        write_data_file(rows)
    create_figure(rows)

    failures = sum(row["candidate_solve_failures"] for row in rows)
    converged = sum(1 for row in rows if row["converged"])
    print(f"{converged}/{len(rows)} restarts converged; {failures} candidate solve failures")


if __name__ == "__main__":
    main()
