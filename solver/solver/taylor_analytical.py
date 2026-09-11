"""Analytical Taylor-cone potential for far-field and verification use.

The exact exterior solution to the Laplace problem for a semi-infinite
conducting cone is

    phi(r, z) = A * rho^(1/2) * P_{1/2}(cos theta),

where ``rho = sqrt(r^2 + (z - apex_z)^2)`` and ``cos theta = (z - apex_z)/rho``.
The ideal cone surface (half-angle given by ``taylor_cone_half_angle_deg``)
is the zero equipotential: ``P_{1/2}(cos theta_T) = 0``.
"""

from __future__ import annotations

import numpy as np
from scipy.special import lpmv


def taylor_potential(r, z, apex_z: float, amplitude: float = 1.0) -> np.ndarray:
    """Exact exterior Taylor potential about the apex ``(0, apex_z)``.

    Parameters
    ----------
    r : array_like
        Radial coordinate(s) [m].
    z : array_like
        Axial coordinate(s) [m].
    apex_z : float
        On-axis apex position [m].
    amplitude : float
        Potential amplitude ``A`` [V].

    Returns
    -------
    numpy.ndarray
        ``A * rho^(1/2) * P_{1/2}(cos theta)``; the NaN at the apex
        (``rho = 0``) is replaced by its limit value 0.

    Notes
    -----
    Finite for ``theta < 180 deg``. The on-axis ray through the cone interior
    (``theta = 180 deg``, i.e. ``r = 0`` with ``z < apex_z``) is singular:
    ``P_{1/2}(cos theta)`` diverges there. Those nodes are outside the physical
    exterior domain, so the guard pins every non-finite value to the
    cone-surface value 0 instead of leaking ``inf`` (or ``np.nan_to_num``'s
    default ~1.8e308 stand-in) into a boundary condition. Cone-interior nodes
    are overwritten by the immersed Dirichlet stencil anyway.
    """
    r = np.asarray(r)
    z = np.asarray(z)
    rho = np.sqrt(r**2 + (z - apex_z) ** 2)
    with np.errstate(divide="ignore", invalid="ignore"):
        cost = (z - apex_z) / rho
        pot = amplitude * np.sqrt(rho) * lpmv(0, 0.5, cost)
    # P_{1/2}(cos theta) diverges on the singular axis ray (r = 0, z < apex_z,
    # theta = 180 deg, inside the ideal cone): lpmv returns -inf there, and NaN
    # at the apex (rho = 0). np.nan_to_num's default would replace that -inf
    # with ~-1.8e308, which could contaminate a boundary condition if a
    # singular-axis node ever lands on the Dirichlet mask. Pin every non-finite
    # value to the cone-surface value 0 instead.
    return np.where(np.isfinite(pot), pot, 0.0)
