"""Parameter dataclasses for the Version 1 solver."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EPS0 = 8.8541878128e-12


@dataclass(frozen=True)
class PhysicalParams:
    """Physical parameters for a reduced electrostatic-capillary solve."""

    V0: float = 1.0
    gamma: float = 0.022  # N/m, approximate ethanol-air surface tension near room temp
    eps_g: float = EPS0
    eps_l: float | None = None
    sigma_l: float | None = None
    length_scale: float = 1.0


@dataclass(frozen=True)
class GridParams:
    """Uniform rectangular axisymmetric grid parameters."""

    r_max: float
    z_min: float
    z_max: float
    nr: int
    nz: int

    def __post_init__(self) -> None:
        if self.r_max <= 0:
            raise ValueError("r_max must be positive")
        if self.z_max <= self.z_min:
            raise ValueError("z_max must exceed z_min")
        if self.nr < 3 or self.nz < 3:
            raise ValueError("nr and nz must both be at least 3")


@dataclass(frozen=True)
class SolverParams:
    """Numerical solver controls."""

    linear_solver: Literal["spsolve"] = "spsolve"
    tolerance: float = 1e-10
    max_iterations: int = 100
    use_dimensionless: bool = False


@dataclass(frozen=True)
class SpaceChargeParams:
    """Parameters for Version 1 Gaussian shielding closure."""

    model: Literal["none", "gaussian"] = "none"
    rho0: float | None = None
    ell: float | None = None
    apex_r: float | None = None
    apex_z: float | None = None
    relaxation: float = 0.5
    tolerance: float = 1e-8
    max_iterations: int = 50

    def validate(self) -> None:
        if self.model == "gaussian":
            if self.rho0 is None:
                raise ValueError("Gaussian space charge requires rho0")
            if self.ell is None or self.ell <= 0:
                raise ValueError("Gaussian space charge requires positive ell")
            if self.apex_r is None or self.apex_z is None:
                raise ValueError("Gaussian space charge requires apex_r and apex_z")
        if not (0 < self.relaxation <= 1):
            raise ValueError("relaxation must lie in (0, 1]")
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be positive")
