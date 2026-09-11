from solver.verification import taylor_cone_half_angle_deg


def test_classical_taylor_half_angle_from_legendre_root():
    alpha = taylor_cone_half_angle_deg()
    assert abs(alpha - 49.2900892921) < 1e-9
