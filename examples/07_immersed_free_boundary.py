"""Example 07 — candidate-dependent immersed free-boundary demonstration.

This is a numerical coupling demonstration, not a claim that the finite rounded
model must recover the singular ideal Taylor angle. It reports the analytical
angle only as a reference and verifies that optimization improves its own
initial immersed residual.
"""

from solver.config import GridParams, PhysicalParams
from solver.geometry import rectangular_electrodes
from solver.grid import AxisymmetricGrid
from solver.optimization import ConeShapeBounds, optimize_cone_shape
from solver.verification import taylor_cone_half_angle_deg


def main() -> None:
    grid = AxisymmetricGrid.from_params(
        GridParams(r_max=1.0, z_min=0.0, z_max=1.0, nr=31, nz=45)
    )
    external = rectangular_electrodes(
        grid, powered="z_max", ground="z_min", far_dirichlet=True
    )
    physical = PhysicalParams(V0=1000.0, gamma=0.022)
    result = optimize_cone_shape(
        grid,
        external,
        physical,
        immersed_mode=True,
        apex_z=0.86,
        z_min_interface=0.15,
        z_max_interface=0.85,
        n_interface=41,
        initial_half_angle_deg=35.0,
        initial_apex_radius=0.06,
        bounds=ConeShapeBounds(
            half_angle_deg_min=10.0,
            half_angle_deg_max=60.0,
            apex_radius_min=0.025,
            apex_radius_max=0.10,
        ),
        powell_options={"maxiter": 100, "ftol": 1e-7, "xtol": 1e-5},
    )

    print(f"Analytical sharp Taylor reference: {taylor_cone_half_angle_deg():.6f} deg")
    print(f"Immersed rounded-cone result:      {result.half_angle_deg:.6f} deg")
    print(f"Cap curvature radius:              {result.apex_radius:.6e}")
    print(f"Base/nozzle radius:                {result.nozzle_radius:.6e}")
    print(f"Initial RMS residual:              {result.initial_rms_residual:.6e} Pa")
    print(f"Final RMS residual:                {result.rms_residual:.6e} Pa")
    print(f"Candidate-dependent field change:  {result.field_variation:.6e} V")
    print(f"Candidate solve failures:          {result.candidate_solve_failures}")
    print(f"Optimizer converged:               {result.converged}")
    print("Interpretation: this demonstrates shape -> boundary -> field coupling.")
    print("It is not yet an onset-voltage prediction or an ideal-limit validation.")


if __name__ == "__main__":
    main()
