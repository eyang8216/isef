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
    ``P_{1/2}(cos theta)`` diverges there, so the returned values are not
    meaningful on that ray.
    """
    r = np.asarray(r)
    z = np.asarray(z)
    rho = np.sqrt(r**2 + (z - apex_z) ** 2)
    cost = (z - apex_z) / rho
    return np.nan_to_num(amplitude * np.sqrt(rho) * lpmv(0, 0.5, cost))
