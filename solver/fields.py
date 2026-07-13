"""Electric-field reconstruction and bilinear interpolation utilities."""

from __future__ import annotations

import numpy as np

from .grid import AxisymmetricGrid


def compute_electric_field(grid: AxisymmetricGrid, phi: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute `Er=-dphi/dr`, `Ez=-dphi/dz`, and `|E|` on the grid.

    Uses second-order central differences in the interior and first-order
    one-sided differences at boundaries via `numpy.gradient`.
    """
    phi = np.asarray(phi, dtype=float)
    if phi.shape != grid.shape:
        raise ValueError(f"phi shape {phi.shape} does not match grid shape {grid.shape}")
    dphi_dr, dphi_dz = np.gradient(phi, grid.dr, grid.dz, edge_order=1)
    Er = -dphi_dr
    Ez = -dphi_dz
    E_mag = np.sqrt(Er * Er + Ez * Ez)
    return Er, Ez, E_mag


def bilinear_interpolate(grid: AxisymmetricGrid, values: np.ndarray, r_points: np.ndarray, z_points: np.ndarray) -> np.ndarray:
    """Bilinearly interpolate a grid-shaped array to arbitrary `(r,z)` points."""
    values = np.asarray(values, dtype=float)
    if values.shape != grid.shape:
        raise ValueError(f"values shape {values.shape} does not match grid shape {grid.shape}")
    r_points = np.asarray(r_points, dtype=float)
    z_points = np.asarray(z_points, dtype=float)
    if r_points.shape != z_points.shape:
        raise ValueError("r_points and z_points must have matching shapes")
    if np.any(r_points < grid.r[0]) or np.any(r_points > grid.r[-1]):
        raise ValueError("interpolation r point outside grid")
    if np.any(z_points < grid.z[0]) or np.any(z_points > grid.z[-1]):
        raise ValueError("interpolation z point outside grid")

    # Cell lower-left indices.
    i = np.searchsorted(grid.r, r_points, side="right") - 1
    j = np.searchsorted(grid.z, z_points, side="right") - 1
    i = np.clip(i, 0, grid.nr - 2)
    j = np.clip(j, 0, grid.nz - 2)

    r0 = grid.r[i]
    r1 = grid.r[i + 1]
    z0 = grid.z[j]
    z1 = grid.z[j + 1]
    tr = (r_points - r0) / (r1 - r0)
    tz = (z_points - z0) / (z1 - z0)

    v00 = values[i, j]
    v10 = values[i + 1, j]
    v01 = values[i, j + 1]
    v11 = values[i + 1, j + 1]
    return (1 - tr) * (1 - tz) * v00 + tr * (1 - tz) * v10 + (1 - tr) * tz * v01 + tr * tz * v11


def interpolate_field_to_points(
    grid: AxisymmetricGrid,
    Er: np.ndarray,
    Ez: np.ndarray,
    r_points: np.ndarray,
    z_points: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Interpolate electric-field components to interface/sample points."""
    return (
        bilinear_interpolate(grid, Er, r_points, z_points),
        bilinear_interpolate(grid, Ez, r_points, z_points),
    )
