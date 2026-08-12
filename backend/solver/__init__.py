"""Lightweight axisymmetric electrostatic-capillary Taylor-cone solver.

Version 1 focuses on sparse 2D axisymmetric Laplace/Poisson electrostatics,
field reconstruction, interface residual diagnostics, and Gaussian space-charge
shielding. It is a reduced-order research solver, not a full CFD/EHD package.
"""

from .config import PhysicalParams, GridParams, SolverParams, SpaceChargeParams
from .grid import AxisymmetricGrid

__all__ = [
    "PhysicalParams",
    "GridParams",
    "SolverParams",
    "SpaceChargeParams",
    "AxisymmetricGrid",
]
