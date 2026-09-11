"""Axisymmetric `(r, z)` grid utilities.

Flattening convention is fixed project-wide:

    k = i * nz + j

where `i` is the radial index and `j` is the axial index.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import GridParams


@dataclass(frozen=True)
class AxisymmetricGrid:
    r: np.ndarray
    z: np.ndarray

    @classmethod
    def from_params(cls, params: GridParams) -> "AxisymmetricGrid":
        r = np.linspace(0.0, params.r_max, params.nr, dtype=float)
        z = np.linspace(params.z_min, params.z_max, params.nz, dtype=float)
        return cls(r=r, z=z)

    @property
    def nr(self) -> int:
        return int(self.r.size)

    @property
    def nz(self) -> int:
        return int(self.z.size)

    @property
    def shape(self) -> tuple[int, int]:
        return (self.nr, self.nz)

    @property
    def size(self) -> int:
        return self.nr * self.nz

    @property
    def dr(self) -> float:
        return float(self.r[1] - self.r[0])

    @property
    def dz(self) -> float:
        return float(self.z[1] - self.z[0])

    @property
    def R(self) -> np.ndarray:
        return np.meshgrid(self.r, self.z, indexing="ij")[0]

    @property
    def Z(self) -> np.ndarray:
        return np.meshgrid(self.r, self.z, indexing="ij")[1]

    def idx(self, i: int, j: int) -> int:
        if not (0 <= i < self.nr and 0 <= j < self.nz):
            raise IndexError(f"grid index out of range: {(i, j)}")
        return i * self.nz + j

    def unidx(self, k: int) -> tuple[int, int]:
        if not (0 <= k < self.size):
            raise IndexError(f"flat index out of range: {k}")
        return divmod(k, self.nz)

    def flatten(self, a: np.ndarray) -> np.ndarray:
        if a.shape != self.shape:
            raise ValueError(f"expected array shape {self.shape}, got {a.shape}")
        return np.asarray(a, dtype=float).reshape(self.size)

    def unflatten(self, a: np.ndarray) -> np.ndarray:
        if np.asarray(a).size != self.size:
            raise ValueError(f"expected flat array size {self.size}, got {np.asarray(a).size}")
        return np.asarray(a, dtype=float).reshape(self.shape)
