"""Graph-form liquid interface utilities for Version 1 residual diagnostics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class GraphInterface:
    """Axisymmetric graph interface represented as `r = R(z)` samples."""

    z: np.ndarray
    R: np.ndarray

    def __post_init__(self) -> None:
        z = np.asarray(self.z, dtype=float)
        R = np.asarray(self.R, dtype=float)
        if z.ndim != 1 or R.ndim != 1:
            raise ValueError("z and R must be 1D arrays")
        if z.size != R.size:
            raise ValueError("z and R must have matching lengths")
        if z.size < 3:
            raise ValueError("at least 3 interface samples are required")
        if not np.all(np.diff(z) > 0):
            raise ValueError("z samples must be strictly increasing")
        if np.any(R <= 0):
            raise ValueError("Version 1 graph interface requires positive R samples")
        object.__setattr__(self, "z", z)
        object.__setattr__(self, "R", R)

    @property
    def r(self) -> np.ndarray:
        return self.R

    def derivatives(self) -> tuple[np.ndarray, np.ndarray]:
        R_z = np.gradient(self.R, self.z, edge_order=2)
        R_zz = np.gradient(R_z, self.z, edge_order=2)
        return R_z, R_zz

    def normals(self) -> tuple[np.ndarray, np.ndarray]:
        """Return gas-side normals `(n_r,n_z)` for gas toward increasing r."""
        R_z, _ = self.derivatives()
        denom = np.sqrt(1.0 + R_z * R_z)
        return 1.0 / denom, -R_z / denom

    def curvature(self) -> np.ndarray:
        """Axisymmetric graph curvature for gas toward increasing radius.

        kappa = 1/(R sqrt(1+R_z^2)) - R_zz/(1+R_z^2)^(3/2)
        """
        R_z, R_zz = self.derivatives()
        denom = 1.0 + R_z * R_z
        return 1.0 / (self.R * np.sqrt(denom)) - R_zz / (denom ** 1.5)

    def arclength_weights(self) -> np.ndarray:
        R_z, _ = self.derivatives()
        ds_dz = np.sqrt(1.0 + R_z * R_z)
        # Trapezoidal-like point weights in physical arclength.
        z = self.z
        dz_w = np.empty_like(z)
        dz_w[1:-1] = 0.5 * (z[2:] - z[:-2])
        dz_w[0] = 0.5 * (z[1] - z[0])
        dz_w[-1] = 0.5 * (z[-1] - z[-2])
        return ds_dz * dz_w

    def half_angle_deg(self, n_points: int | None = None) -> float:
        """Estimate cone half-angle by fitting `R = m z + c` near the apex.

        The apex is approximated by the smallest-radius samples. The reported
        angle is `atan(abs(m))`, independent of z-axis orientation.
        """
        n = self.z.size
        if n_points is None:
            n_points = min(max(5, n // 5), n)
        n_points = max(2, min(n_points, n))
        order = np.argsort(self.R)[:n_points]
        z_fit = self.z[order]
        R_fit = self.R[order]
        m, _ = np.polyfit(z_fit, R_fit, 1)
        return float(np.degrees(np.arctan(abs(m))))


def straight_cone_interface(z_min: float, z_max: float, apex_z: float, half_angle_deg: float, n: int, apex_radius: float = 1e-6) -> GraphInterface:
    """Create a positive-radius straight conical graph for tests/examples."""
    z = np.linspace(z_min, z_max, n)
    R = apex_radius + np.abs(z - apex_z) * np.tan(np.deg2rad(half_angle_deg))
    return GraphInterface(z=z, R=R)
