"""Immersed Dirichlet stencils for an implicit conducting cone.

The correction in this module is deliberately separate from the ordinary
boundary-condition machinery.  It replaces only a coordinate-direction
stencil whose immediate neighbour is in the conductor.  The conductor node
is replaced by the exact interface point and the resulting unequal, three
point polynomial stencil is used at the gas node.
"""

from __future__ import annotations

import numpy as np
from scipy.sparse import issparse

from .fields import bilinear_interpolate
from .geometry import ImplicitCone
from .grid import AxisymmetricGrid


def _unequal_weights(x_boundary: float, x_other: float, first_derivative: float = 0.0) -> tuple[float, float, float]:
    """Weights at zero on the nodes ``(x_boundary, 0, x_other)``.

    The returned weights approximate ``f''(0) + first_derivative*f'(0)`` and
    are ordered as boundary, centre, other.  Both distances are signed.
    """
    xb, xo = float(x_boundary), float(x_other)
    if xb == 0.0 or xo == 0.0 or xb == xo:
        raise ValueError("immersed stencil points must be distinct")

    # Derivatives of the three quadratic Lagrange basis polynomials at zero.
    d2_b = 2.0 / (xb * (xb - xo))
    d2_o = 2.0 / (xo * (xo - xb))
    d2_c = 2.0 / (xb * xo)
    d1_b = -xo / (xb * (xb - xo))
    d1_o = -xb / (xo * (xo - xb))
    d1_c = -(d1_b + d1_o)
    q = float(first_derivative)
    return d2_b + q * d1_b, d2_c + q * d1_c, d2_o + q * d1_o


def apply_immersed_dirichlet(
    matrix,
    rhs: np.ndarray,
    grid: AxisymmetricGrid,
    cone: ImplicitCone,
    *,
    min_fraction: float = 1.0e-6,
    fixed_mask: np.ndarray | None = None,
):
    """Apply exact-distance immersed Dirichlet corrections.

    Parameters
    ----------
    matrix, rhs
        Existing matrix and right hand side for the axisymmetric operator
        ``d2/dr2 + (1/r)d/dr + d2/dz2``.  They are copied and are not modified
        in place.  The matrix is expected to have the stencil produced by
        :func:`solver.operators.build_axisymmetric_laplacian`.
    grid, cone
        The uniform axisymmetric grid and implicit conducting cone.
    min_fraction
        Tiny-cut band threshold: a boundary crossing at or below
        ``min_fraction * 4`` of one grid step from a gas node pins that node
        to ``cone.boundary_value`` (identity Dirichlet row) instead of forming
        a near-singular polynomial stencil.  Larger cuts use the exact
        fractional-distance weights.

    Returns
    -------
    (matrix, rhs)
        A CSR matrix and one-dimensional RHS.  Gas-node Poisson values are
        retained, apart from the analytically eliminated boundary term.
        Every conductor row is identity with ``cone.boundary_value`` on the
        RHS.

    Notes
    -----
    If the crossing is on either side of a gas node, the third interpolation
    point is the grid node on the opposite side.  In ``z`` the quadratic
    weights approximate ``d2/dz2``.  In ``r`` they approximate
    ``d2/dr2 + (1/r)d/dr`` at the gas-node radius.
    """
    if not issparse(matrix):
        raise TypeError("matrix must be a scipy sparse matrix")
    if matrix.shape != (grid.size, grid.size):
        raise ValueError(f"matrix shape {matrix.shape} does not match grid size {grid.size}")
    b = np.asarray(rhs, dtype=float)
    if b.ndim != 1 or b.size != grid.size:
        raise ValueError(f"rhs must be one-dimensional with size {grid.size}")
    if not np.isfinite(min_fraction) or not 0.0 < min_fraction < 1.0:
        raise ValueError("min_fraction must lie strictly between zero and one")
    if fixed_mask is not None:
        fixed_mask = np.asarray(fixed_mask, dtype=bool)
        if fixed_mask.shape != grid.shape:
            raise ValueError("fixed_mask must match grid shape")

    b = b.copy()
    A = matrix.astype(float).tolil(copy=True)
    conductor = cone.conductor_mask(grid)
    gas = ~conductor
    if fixed_mask is not None:
        gas &= ~fixed_mask

    def crossing_fraction(i: int, j: int, ni: int, nj: int) -> float:
        fraction = float(
            cone.boundary_fraction(
                float(grid.r[i]), float(grid.z[j]),
                float(grid.r[ni]), float(grid.z[nj]),
            )
        )
        # A crossing at the conductor endpoint (fraction == 1) is regular and
        # simply recovers the ordinary centred stencil.  A tiny positive cut
        # (0 < fraction <= min_fraction*4) is legitimate geometry handled by
        # the identity-row fallback below; only non-crossings (fraction <= 0)
        # or out-of-segment values indicate an adjacency/geometry mismatch and
        # are rejected.
        if not np.isfinite(fraction) or fraction <= 0.0 or fraction > 1.0 + 1.0e-12:
            raise ValueError(
                f"pathological immersed-boundary fraction {fraction!r} at gas node {(i, j)}"
            )
        return min(fraction, 1.0)

    for i in range(grid.nr):
        for j in range(grid.nz):
            if not gas[i, j]:
                continue
            row = grid.idx(i, j)

            # Axial direction.  A cut on either side uses the uncut node on
            # the other side, at its signed coordinate relative to the centre.
            z_cuts = []
            if j > 0 and conductor[i, j - 1]:
                z_cuts.append(-1)
            if j + 1 < grid.nz and conductor[i, j + 1]:
                z_cuts.append(+1)
            if len(z_cuts) > 1:
                raise ValueError(f"gas node {(i, j)} is cut on both axial sides")
            if z_cuts:
                side = z_cuts[0]
                other_j = j - side
                if not (0 <= other_j < grid.nz) or conductor[i, other_j]:
                    raise ValueError(f"no gas-side third point for axial cut at {(i, j)}")
                neighbour_j = j + side
                frac = crossing_fraction(i, j, i, neighbour_j)
                if frac <= min_fraction * 4.0:
                    A.rows[row] = [row]
                    A.data[row] = [1.0]
                    b[row] = cone.boundary_value
                    continue
                h = grid.dz
                w_boundary, w_centre, w_other = _unequal_weights(side * frac * h, -side * h)

                # Remove the original centred z stencil, then insert the two
                # unknown coefficients.  The boundary coefficient is known.
                A[row, grid.idx(i, j - 1)] += -1.0 / h**2
                A[row, row] += 2.0 / h**2
                A[row, grid.idx(i, j + 1)] += -1.0 / h**2
                A[row, row] += w_centre
                A[row, grid.idx(i, other_j)] += w_other
                b[row] -= w_boundary * cone.boundary_value

            # Radial direction.  A conductor-adjacent gas node cannot be on
            # the symmetry axis; the regular interior radial stencil is the
            # finite-volume form, algebraically equal to centred f''+f'/r.
            r_cuts = []
            if i > 0 and conductor[i - 1, j]:
                r_cuts.append(-1)
            if i + 1 < grid.nr and conductor[i + 1, j]:
                r_cuts.append(+1)
            if len(r_cuts) > 1:
                raise ValueError(f"gas node {(i, j)} is cut on both radial sides")
            if r_cuts:
                side = r_cuts[0]
                other_i = i - side
                if i == 0 or i == grid.nr - 1 or not (0 <= other_i < grid.nr) or conductor[other_i, j]:
                    raise ValueError(f"no gas-side third point for radial cut at {(i, j)}")
                neighbour_i = i + side
                frac = crossing_fraction(i, j, neighbour_i, j)
                if frac <= min_fraction * 4.0:
                    A.rows[row] = [row]
                    A.data[row] = [1.0]
                    b[row] = cone.boundary_value
                    continue
                h = grid.dr
                r_i = float(grid.r[i])
                w_boundary, w_centre, w_other = _unequal_weights(
                    side * frac * h, -side * h, first_derivative=1.0 / r_i
                )

                c_plus = (r_i + 0.5 * h) / (r_i * h**2)
                c_minus = (r_i - 0.5 * h) / (r_i * h**2)
                A[row, grid.idx(i - 1, j)] += -c_minus
                A[row, row] += c_minus + c_plus
                A[row, grid.idx(i + 1, j)] += -c_plus
                A[row, row] += w_centre
                A[row, grid.idx(other_i, j)] += w_other
                b[row] -= w_boundary * cone.boundary_value

    # Rows inside/on the liquid are prescribed independently of whatever rows
    # the input operator or earlier boundary-condition pass contained.
    for i, j in np.argwhere(conductor):
        row = grid.idx(int(i), int(j))
        A.rows[row] = [row]
        A.data[row] = [1.0]
        b[row] = cone.boundary_value

    result = A.tocsr()
    result.eliminate_zeros()
    return result, b


# Descriptive aliases for callers that regard this as a matrix correction pass.
correct_immersed_dirichlet = apply_immersed_dirichlet
apply_immersed_boundary = apply_immersed_dirichlet


def normal_field_on_interface(
    grid: AxisymmetricGrid,
    potential: np.ndarray,
    cone: ImplicitCone,
    r_points: np.ndarray | float,
    z_points: np.ndarray | float,
    *,
    sample_distance: float | None = None,
) -> np.ndarray | float:
    """Return the gas-side normal electric field ``E_n`` on the interface.

    The potential is sampled at distances ``d``, ``2d`` and ``3d`` along the
    cone's unit gas normal using bilinear interpolation.  Together with the
    exact Dirichlet value at distance zero these four samples give the
    one-sided cubic-exact derivative

    ``E_n = -(-11*V_b + 18*V(d) - 9*V(2d) + 2*V(3d)) / (6*d)``.

    ``sample_distance`` defaults to one grid cell (``max(dr, dz)``).  Two
    design choices, measured 2026-08-09 (ticket ``taylor-onset-framing/01``):

    - **Full-cell sample distances**: samples at or beyond one cell sit in
      cells fully inside the gas, so bilinear interpolation is not
      contaminated by the cut cell that straddles the conductor surface.  The
      previous half-cell default produced E_n errors of up to ~50% on solved
      potentials that *grew* with refinement.
    - **Cubic-exact stencil**: four samples cancel the quadratic and cubic
      profile terms, keeping the surface derivative accurate on strongly
      curved normal profiles (the analytic Taylor field and the manufactured
      circle both fail the old three-point quadratic by ~10-30% at practical
      grids).

    Interface points and all gas-side samples must be inside the
    interpolation domain.  Scalar inputs produce a float; broadcast array
    inputs produce an array.
    """
    values = np.asarray(potential, dtype=float)
    if values.shape != grid.shape:
        raise ValueError(f"potential shape {values.shape} does not match grid shape {grid.shape}")
    if not np.all(np.isfinite(values)):
        raise ValueError("potential must contain only finite values")

    rp, zp = np.broadcast_arrays(np.asarray(r_points, dtype=float), np.asarray(z_points, dtype=float))
    if not np.all(np.isfinite(rp)) or not np.all(np.isfinite(zp)):
        raise ValueError("interface points must be finite")
    d = max(grid.dr, grid.dz) if sample_distance is None else float(sample_distance)
    if not np.isfinite(d) or d <= 0.0:
        raise ValueError("sample_distance must be finite and positive")

    nr, nz = cone.normal(rp, zp)
    nr = np.asarray(nr, dtype=float)
    nz = np.asarray(nz, dtype=float)
    r1, z1 = rp + d * nr, zp + d * nz
    r2, z2 = rp + 2.0 * d * nr, zp + 2.0 * d * nz
    r3, z3 = rp + 3.0 * d * nr, zp + 3.0 * d * nz

    # bilinear_interpolate performs strict domain checks.  Also check that the
    # selected orientation really is the gas side, which catches accidental
    # use of interface points far from the represented zero contour.
    if np.any(np.asarray(cone.signed_function(r1, z1)) <= 0.0):
        raise ValueError("one-sided normal samples must lie in the gas")
    v1 = bilinear_interpolate(grid, values, r1, z1)
    v2 = bilinear_interpolate(grid, values, r2, z2)
    v3 = bilinear_interpolate(grid, values, r3, z3)
    en = -(-11.0 * cone.boundary_value + 18.0 * v1 - 9.0 * v2 + 2.0 * v3) / (6.0 * d)
    return float(en) if en.ndim == 0 else en
