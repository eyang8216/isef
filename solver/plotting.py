"""Minimal matplotlib plotting helpers for examples and reports."""

from __future__ import annotations

import numpy as np

from .grid import AxisymmetricGrid
from .interface import GraphInterface


def plot_scalar_field(grid: AxisymmetricGrid, values: np.ndarray, title: str = "field", ax=None):
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots()
    c = ax.contourf(grid.Z, grid.R, values, levels=40)
    ax.set_xlabel("z")
    ax.set_ylabel("r")
    ax.set_title(title)
    return ax, c


def plot_interface(interface: GraphInterface, ax=None, **kwargs):
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots()
    defaults = {"color": "white", "linewidth": 2}
    defaults.update(kwargs)
    ax.plot(interface.z, interface.R, **defaults)
    return ax
