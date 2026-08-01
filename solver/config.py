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
    """Numerical solver controls (reserved for future options).

    Currently spsolve with its defaults is the only supported linear solver,
    so this dataclass intentionally carries no fields yet.
    """


@dataclass(frozen=True)
class SpaceChargeParams:
    """Parameters for space-charge shielding closures (Gaussian or threshold-activated)."""

    model: Literal["none", "gaussian", "threshold"] = "none"
    # Gaussian closure fields
    rho0: float | None = None
    ell: float | None = None
    apex_r: float | None = None
    apex_z: float | None = None
    # Threshold closure fields
    E_c: float | None = None   # critical field [V/m] — charge activates above this
    E_s: float | None = None   # scale field [V/m] — controls activation sharpness
    rho_max: float | None = None  # peak charge density [C/m³]
    # Shared iteration controls
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
        if self.model == "threshold":
            if self.E_c is None or self.E_c < 0:
                raise ValueError("Threshold closure requires non-negative E_c")
            if self.E_s is None or self.E_s <= 0:
                raise ValueError("Threshold closure requires positive E_s")
            if self.rho_max is None or self.rho_max <= 0:
                raise ValueError("Threshold closure requires positive rho_max")
        if not (0 < self.relaxation <= 1):
            raise ValueError("relaxation must lie in (0, 1]")
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be positive")
