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


@dataclass(frozen=True)
class ImplicitCone:
    """Rounded axisymmetric cone whose conducting liquid extends toward ``-z``.

    ``apex_z`` is the physical, on-axis tip and ``apex_radius`` is the
    radius of its spherical cap.  The cap is joined tangentially to a straight
    flank of half-angle ``half_angle_deg``.  The implicit value is negative in
    liquid, positive in gas, and its gradient points to the gas.

    The function is the exact signed distance to either the spherical cap or
    the straight flank in their respective tangent-coordinate regions.  The
    two formulae have the same value and gradient on the region boundary, so
    the representation is C1 wherever that boundary is relevant to the
    surface (including the cap/flank join).
    """

    apex_z: float
    half_angle_deg: float
    apex_radius: float
    boundary_value: float = 1.0

    def __post_init__(self) -> None:
        values = (self.apex_z, self.half_angle_deg, self.apex_radius, self.boundary_value)
        if not np.all(np.isfinite(values)):
            raise ValueError("cone parameters must be finite")
        if not 0.0 < self.half_angle_deg < 90.0:
            raise ValueError("half_angle_deg must lie strictly between 0 and 90")
        if self.apex_radius <= 0.0:
            raise ValueError("apex_radius must be positive")

    @property
    def half_angle(self) -> float:
        """Half-angle in radians."""
        return float(np.deg2rad(self.half_angle_deg))

    @property
    def cap_center_z(self) -> float:
        return self.apex_z - self.apex_radius

    @property
    def cap_join_z(self) -> float:
        """Alias for :attr:`join_z` for descriptive external callers."""
        return self.join_z

    @property
    def cap_join_r(self) -> float:
        """Alias for :attr:`join_radius`."""
        return self.join_radius

    @property
    def join_z(self) -> float:
        """Axial coordinate of the cap/flank tangent circle."""
        return self.cap_center_z + self.apex_radius * np.sin(self.half_angle)

    @property
    def join_radius(self) -> float:
        return self.apex_radius * np.cos(self.half_angle)

    @property
    def virtual_apex_z(self) -> float:
        """Apex of the extrapolated straight flanks (not the rounded tip)."""
        return self.join_z + self.join_radius / np.tan(self.half_angle)

    def _arrays(self, r: np.ndarray | float, z: np.ndarray | float) -> tuple[np.ndarray, np.ndarray]:
        r_arr, z_arr = np.broadcast_arrays(np.asarray(r, dtype=float), np.asarray(z, dtype=float))
        return r_arr, z_arr

    def _cap_region(self, r: np.ndarray, z: np.ndarray) -> np.ndarray:
        # Positive tangent coordinate points from the join around the cap.
        a = self.half_angle
        return (-(r - self.join_radius) * np.sin(a) + (z - self.join_z) * np.cos(a)) >= 0.0

    def signed_function(self, r: np.ndarray | float, z: np.ndarray | float) -> np.ndarray | float:
        """Return the implicit value: ``<= 0`` liquid and ``> 0`` gas."""
        r_arr, z_arr = self._arrays(r, z)
        a = self.half_angle
        cap = np.hypot(r_arr, z_arr - self.cap_center_z) - self.apex_radius
        flank = ((r_arr - self.join_radius) * np.cos(a)
                 + (z_arr - self.join_z) * np.sin(a))
        result = np.where(self._cap_region(r_arr, z_arr), cap, flank)
        return float(result) if result.ndim == 0 else result

    # Common level-set spellings retained as concise conveniences.
    phi = signed_function
    signed_distance = signed_function

    def normal(self, r: np.ndarray | float, z: np.ndarray | float) -> tuple[np.ndarray | float, np.ndarray | float]:
        """Return unit gas-side normal components ``(n_r, n_z)``.

        Normals are principally intended on the zero contour.  At the cap
        sphere's center, where a spherical normal is undefined, ``(1, 0)`` is
        returned deterministically.
        """
        r_arr, z_arr = self._arrays(r, z)
        a = self.half_angle
        cap_region = self._cap_region(r_arr, z_arr)
        d = np.hypot(r_arr, z_arr - self.cap_center_z)
        safe_d = np.where(d > 0.0, d, 1.0)
        cap_nr = np.where(d > 0.0, r_arr / safe_d, 1.0)
        cap_nz = np.where(d > 0.0, (z_arr - self.cap_center_z) / safe_d, 0.0)
        nr = np.where(cap_region, cap_nr, np.cos(a))
        nz = np.where(cap_region, cap_nz, np.sin(a))
        if nr.ndim == 0:
            return float(nr), float(nz)
        return nr, nz

    def surface_radius(self, z: np.ndarray | float) -> np.ndarray | float:
        """Radius of the zero contour as a graph ``r=R(z)``.

        The surface exists for all ``z <= apex_z``.  Values above the physical
        apex are returned as NaN rather than inventing a second sphere branch.
        """
        z_arr = np.asarray(z, dtype=float)
        flank = self.join_radius + (self.join_z - z_arr) * np.tan(self.half_angle)
        radicand = self.apex_radius**2 - (z_arr - self.cap_center_z) ** 2
        cap = np.sqrt(np.maximum(radicand, 0.0))
        cap = np.where(np.isclose(z_arr, self.apex_z, rtol=0.0, atol=1e-14), 0.0, cap)
        result = np.where(z_arr <= self.join_z, flank, cap)
        result = np.where(z_arr <= self.apex_z, result, np.nan)
        return float(result) if result.ndim == 0 else result

    radius = surface_radius

    def is_flank(self, r: np.ndarray | float, z: np.ndarray | float, *, margin: float = 0.0) -> np.ndarray | bool:
        """Identify the straight-flank region, optionally excluding a margin.

        ``margin`` is physical distance measured along the surface away from
        the tangent join.  It is useful as a residual/fit window.
        """
        if not np.isfinite(margin) or margin < 0.0:
            raise ValueError("margin must be a finite non-negative distance")
        r_arr, z_arr = self._arrays(r, z)
        a = self.half_angle
        tangent_coordinate = (r_arr - self.join_radius) * np.sin(a) - (z_arr - self.join_z) * np.cos(a)
        result = tangent_coordinate >= margin
        return bool(result) if result.ndim == 0 else result

    def flank_mask(self, z: np.ndarray | float, *, margin: float = 0.0) -> np.ndarray | bool:
        """Return a flank-only window for samples on ``r=R(z)``."""
        z_arr = np.asarray(z, dtype=float)
        r_arr = self.surface_radius(z_arr)
        return self.is_flank(r_arr, z_arr, margin=margin)

    def flank_window(
        self,
        z: np.ndarray | float,
        *,
        margin: float = 0.0,
        z_min: float | None = None,
        z_max: float | None = None,
    ) -> np.ndarray | bool:
        """Return a flank mask additionally restricted to an axial window."""
        if z_min is not None and not np.isfinite(z_min):
            raise ValueError("z_min must be finite when provided")
        if z_max is not None and not np.isfinite(z_max):
            raise ValueError("z_max must be finite when provided")
        if z_min is not None and z_max is not None and z_min > z_max:
            raise ValueError("z_min cannot exceed z_max")
        z_arr = np.asarray(z, dtype=float)
        result = np.asarray(self.flank_mask(z_arr, margin=margin), dtype=bool)
        if z_min is not None:
            result &= z_arr >= z_min
        if z_max is not None:
            result &= z_arr <= z_max
        return bool(result) if result.ndim == 0 else result

    def conductor_mask(self, grid: AxisymmetricGrid) -> np.ndarray:
        return np.asarray(self.signed_function(grid.R, grid.Z) <= 0.0, dtype=bool)

    def gas_mask(self, grid: AxisymmetricGrid) -> np.ndarray:
        return np.asarray(self.signed_function(grid.R, grid.Z) > 0.0, dtype=bool)

    def masks(self, grid: AxisymmetricGrid, ground_outer: bool = True) -> GeometryMasks:
        """Build solver masks with the liquid as the powered conductor."""
        conductor = self.conductor_mask(grid)
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
        gas = ~(conductor | grounded)
        return GeometryMasks(powered, grounded, axis, far, conductor, gas)

    def segment_boundary_fraction(
        self, r0: float, z0: float, r1: float, z1: float, *, tolerance: float = 1e-12
    ) -> float:
        """Return the exact zero-contour crossing fraction on a segment.

        Endpoints must lie on opposite sides (an endpoint on the boundary is
        allowed).  Analytic line/circle intersections are used and checked
        against the cap/flank region split; bisection provides a roundoff-safe
        fallback for a valid sign-changing segment.
        """
        points = np.asarray((r0, z0, r1, z1), dtype=float)
        if not np.all(np.isfinite(points)):
            raise ValueError("segment endpoints must be finite")
        if tolerance <= 0.0 or not np.isfinite(tolerance):
            raise ValueError("tolerance must be finite and positive")
        f0 = float(self.signed_function(r0, z0))
        f1 = float(self.signed_function(r1, z1))
        scale = max(1.0, self.apex_radius, np.hypot(r1 - r0, z1 - z0))
        ftol = tolerance * scale
        if f0 == 0.0:
            return 0.0
        if f1 == 0.0:
            return 1.0
        if np.signbit(f0) == np.signbit(f1):
            raise ValueError("segment endpoints must bracket the liquid/gas boundary")

        dr, dz = r1 - r0, z1 - z0
        if dr == 0.0 and dz == 0.0:
            raise ValueError("segment must have nonzero length")
        a = self.half_angle
        candidates: list[tuple[str, float]] = []

        # Straight-flank intersection.
        denominator = dr * np.cos(a) + dz * np.sin(a)
        if abs(denominator) > np.finfo(float).eps * np.hypot(dr, dz):
            numerator = ((r0 - self.join_radius) * np.cos(a)
                         + (z0 - self.join_z) * np.sin(a))
            candidates.append(("flank", -numerator / denominator))

        # Spherical-cap intersections, using a cancellation-resistant quadratic.
        y0 = z0 - self.cap_center_z
        qa = dr * dr + dz * dz
        qb = 2.0 * (r0 * dr + y0 * dz)
        qc = r0 * r0 + y0 * y0 - self.apex_radius**2
        discriminant = qb * qb - 4.0 * qa * qc
        disc_tol = 32.0 * np.finfo(float).eps * (qb * qb + abs(4.0 * qa * qc) + 1.0)
        if discriminant >= -disc_tol:
            root_disc = np.sqrt(max(0.0, discriminant))
            q = -0.5 * (qb + np.copysign(root_disc, qb))
            if q != 0.0:
                candidates.extend((("cap", q / qa), ("cap", qc / q)))
            else:
                candidates.append(("cap", -qb / (2.0 * qa)))

        valid: list[float] = []
        theta_tol = tolerance * 8.0
        for branch, theta in candidates:
            if -theta_tol <= theta <= 1.0 + theta_tol:
                theta = min(1.0, max(0.0, float(theta)))
                rr, zz = r0 + theta * dr, z0 + theta * dz
                cap_region = bool(self._cap_region(np.asarray(rr), np.asarray(zz)))
                cap_value = np.hypot(rr, zz - self.cap_center_z) - self.apex_radius
                flank_value = ((rr - self.join_radius) * np.cos(a)
                               + (zz - self.join_z) * np.sin(a))
                # Require the candidate to belong to the branch that generated
                # it, avoiding acceptance merely because the inactive branch
                # happens to vanish elsewhere on the segment.
                generated_by_flank = branch == "flank"
                branch_valid = (not cap_region) if generated_by_flank else cap_region
                branch_value = flank_value if generated_by_flank else cap_value
                if branch_valid and abs(float(branch_value)) <= 64.0 * ftol:
                    valid.append(theta)
        if valid:
            # A bracketing segment normally has one root.  In the uncommon
            # multi-root case, choose the first actual sign transition.
            for theta in sorted(set(valid)):
                eps = min(1e-7, 0.25 * min(theta, 1.0 - theta))
                if eps == 0.0:
                    return theta
                left = float(self.signed_function(r0 + (theta - eps) * dr, z0 + (theta - eps) * dz))
                right = float(self.signed_function(r0 + (theta + eps) * dr, z0 + (theta + eps) * dz))
                if np.signbit(left) != np.signbit(right):
                    return theta
            return min(valid)

        # The opposite endpoint signs guarantee convergence even if an
        # analytical candidate was lost to extreme floating-point scaling.
        lo, hi, flo = 0.0, 1.0, f0
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            fm = float(self.signed_function(r0 + mid * dr, z0 + mid * dz))
            if abs(fm) <= ftol or hi - lo <= tolerance:
                return mid
            if np.signbit(fm) == np.signbit(flo):
                lo, flo = mid, fm
            else:
                hi = mid
        return 0.5 * (lo + hi)

    # Short name expected by immersed-stencil callers.
    boundary_fraction = segment_boundary_fraction

    def segment_boundary_point(self, r0: float, z0: float, r1: float, z1: float) -> tuple[float, float]:
        theta = self.segment_boundary_fraction(r0, z0, r1, z1)
        return r0 + theta * (r1 - r0), z0 + theta * (z1 - z0)

    def sample_graph(
        self, z_min: float, z_max: float, n: int, *, flank_margin: float = 0.0
    ):  # return annotation is postponed to avoid a geometry/interface import cycle
        """Sample this same zero contour as a :class:`GraphInterface`."""
        from .interface import GraphInterface

        if not np.isfinite(z_min) or not np.isfinite(z_max) or not z_min < z_max:
            raise ValueError("finite z_min < z_max is required")
        if z_max > self.apex_z:
            raise ValueError("z_max cannot exceed the physical apex")
        if isinstance(n, bool) or int(n) != n or n < 3:
            raise ValueError("n must be an integer of at least 3")
        z = np.linspace(z_min, z_max, int(n), dtype=float)
        radius = np.asarray(self.surface_radius(z))
        flank = np.asarray(self.flank_mask(z, margin=flank_margin), dtype=bool)
        return GraphInterface(z=z, R=radius, flank_mask=flank)

    graph_interface = sample_graph


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
