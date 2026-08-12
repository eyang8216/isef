import numpy as np

from solver.interface import GraphInterface


def test_cylinder_curvature_is_one_over_radius():
    z = np.linspace(-1.0, 1.0, 101)
    R = np.full_like(z, 0.25)
    interface = GraphInterface(z=z, R=R)
    assert np.max(np.abs(interface.curvature() - 4.0)) < 1e-12


def test_half_angle_for_straight_cone():
    z = np.linspace(0.0, 1.0, 101)
    alpha = 49.3
    R = 0.01 + z * np.tan(np.deg2rad(alpha))
    interface = GraphInterface(z=z, R=R)
    assert abs(interface.half_angle_deg(n_points=50) - alpha) < 1e-10
