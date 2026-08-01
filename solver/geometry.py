"""Simple named geometries and boolean boundary masks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from .grid import AxisymmetricGrid


@dataclass(frozen=True)
class GeometryMasks:
    powered: np.ndarray
    grounded: np.ndarray
    axis: np.ndarray
    far_boundary: np.ndarray
    conductor: np.ndarray
    gas: np.ndarray

    def __post_init__(self) -> None:
        shapes = {arr.shape for arr in (self.powered, self.grounded, self.axis, self.far_boundary, self.conductor, self.gas)}
        if len(shapes) != 1:
            raise ValueError(f"all masks must have the same shape, got {shapes}")

    @property
    def dirichlet(self) -> np.ndarray:
        return self.powered | self.grounded | self.conductor


def rectangular_electrodes(
    grid: AxisymmetricGrid,
    powered: Literal["z_min", "z_max"] = "z_max",
    ground: Literal["z_min", "z_max", "r_max"] = "z_min",
    far_dirichlet: bool = True,
) -> GeometryMasks:
    """Flat-electrode rectangular test geometry.

    `powered` and `ground` mark domain boundaries. The axis is always Neumann,
    not Dirichlet. If `far_dirichlet` is true, the outer radial boundary is
    marked grounded unless already used by another boundary.
    """
    shape = grid.shape
    powered_mask = np.zeros(shape, dtype=bool)
    grounded_mask = np.zeros(shape, dtype=bool)
    axis = np.zeros(shape, dtype=bool)
    axis[0, :] = True
    far = np.zeros(shape, dtype=bool)
    far[-1, :] = True
    far[:, 0] = True
    far[:, -1] = True

    if powered == "z_min":
        powered_mask[:, 0] = True
    elif powered == "z_max":
        powered_mask[:, -1] = True
    else:  # pragma: no cover
        raise ValueError(powered)

    if ground == "z_min":
        grounded_mask[:, 0] = True
    elif ground == "z_max":
        grounded_mask[:, -1] = True
    elif ground == "r_max":
        grounded_mask[-1, :] = True
    else:  # pragma: no cover
        raise ValueError(ground)

    if far_dirichlet:
        grounded_mask[-1, :] = True

    # Axis points that are also z-boundary electrodes retain electrode value.
    conductor = np.zeros(shape, dtype=bool)
    gas = ~(powered_mask | grounded_mask | conductor)
    return GeometryMasks(powered_mask, grounded_mask, axis, far, conductor, gas)


def conical_conductor(
    grid: AxisymmetricGrid,
    apex_r: float,
    apex_z: float,
    half_angle_deg: float,
    z_direction: Literal["positive", "negative"] = "negative",
    ground_outer: bool = True,
) -> GeometryMasks:
    """Crude grid-mask conical conductor for field visualization tests.

    This is intentionally simple: all nodes inside/behind the cone are marked as
    a powered conductor. It is not a moving-boundary discretization.
    """
    R, Z = grid.R, grid.Z
    alpha = np.deg2rad(half_angle_deg)
    dz = Z - apex_z
    axial = -dz if z_direction == "negative" else dz
    cone_radius = apex_r + np.maximum(axial, 0.0) * np.tan(alpha)
    conductor = (axial >= 0.0) & (R <= cone_radius)

    powered = conductor.copy()
    grounded = np.zeros(grid.shape, dtype=bool)
    if ground_outer:
        grounded[-1, :] = True
        grounded[:, 0] = True
        grounded[:, -1] = True
        grounded &= ~powered

    axis = np.zeros(grid.shape, dtype=bool)
    axis[0, :] = True
    far = np.zeros(grid.shape, dtype=bool)
    far[-1, :] = True
    far[:, 0] = True
    far[:, -1] = True
    gas = ~(powered | grounded)
    return GeometryMasks(powered, grounded, axis, far, conductor, gas)
