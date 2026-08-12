"""Compute the classical Taylor cone half-angle from the Legendre root."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from solver.verification import taylor_cone_half_angle_deg


if __name__ == "__main__":
    print(f"Taylor cone half-angle: {taylor_cone_half_angle_deg():.10f} degrees")
