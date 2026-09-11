"""Graph-form liquid interface utilities for Version 1 residual diagnostics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class GraphInterface:
    """Axisymmetric graph interface represented as ``r = R(z)`` samples.

    ``flank_mask`` optionally marks samples belonging to a straight-flank fit
    window (for example, excluding a rounded cap).  Existing two-argument
    construction remains unchanged and treats every sample as eligible.
    """

    z: np.ndarray
    R: np.ndarray
    flank_mask: np.ndarray | None = None

    def __post_init__(self) -> None:
        z = np.asarray(self.z, dtype=float)
        R = np.asarray(self.R, dtype=float)
        if z.ndim != 1 or R.ndim != 1:
            raise ValueError("z and R must be 1D arrays")
        if z.size != R.size:
            raise ValueError("z and R must have matching lengths")
        if z.size < 3:
            raise ValueError("at least 3 interface samples are required")
        if not np.all(np.isfinite(z)) or not np.all(np.isfinite(R)):
            raise ValueError("interface samples must be finite")
        if not np.all(np.diff(z) > 0):
            raise ValueError("z samples must be strictly increasing")
        if np.any(R < 0):
            raise ValueError("graph-interface radius cannot be negative")
        if self.flank_mask is None:
            flank_mask = np.ones(z.shape, dtype=bool)
        else:
            flank_mask = np.asarray(self.flank_mask, dtype=bool)
            if flank_mask.ndim != 1 or flank_mask.shape != z.shape:
                raise ValueError("flank_mask must be a 1D array matching z")
        object.__setattr__(self, "z", z)
        object.__setattr__(self, "R", R)
        object.__setattr__(self, "flank_mask", flank_mask)

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
        """Estimate cone half-angle by fitting ``R = m z + c``.

        Capped interfaces use the stored flank window.  Legacy interfaces,
        whose default mask includes every point, preserve the historical
        smallest-radius selection.
        """
        n = self.z.size
        eligible = np.flatnonzero(self.flank_mask)
        if eligible.size < 2:
            raise ValueError("at least two flank samples are required")

        all_eligible = eligible.size == n
        if n_points is None:
            if all_eligible:
                n_points = min(max(5, n // 5), n)
            else:
                n_points = eligible.size
        n_points = max(2, min(int(n_points), eligible.size))
        if all_eligible:
            order = np.argsort(self.R[eligible])[:n_points]
            selected = eligible[order]
        else:
            # If explicitly limited, retain points farthest from the cap: for
            # liquid toward decreasing z these are the first flank samples.
            selected = eligible[:n_points]
        m, _ = np.polyfit(self.z[selected], self.R[selected], 1)
        return float(np.degrees(np.arctan(abs(m))))


def straight_cone_interface(z_min: float, z_max: float, apex_z: float, half_angle_deg: float, n: int, apex_radius: float = 1e-6) -> GraphInterface:
    """Create a positive-radius straight conical graph for tests/examples."""
    z = np.linspace(z_min, z_max, n)
    R = apex_radius + np.abs(z - apex_z) * np.tan(np.deg2rad(half_angle_deg))
    return GraphInterface(z=z, R=R)
