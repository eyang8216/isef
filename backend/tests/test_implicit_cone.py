"""Tests for the shared rounded implicit-cone geometry."""

import numpy as np
import pytest

from solver.config import GridParams
from solver.geometry import ImplicitCone
from solver.grid import AxisymmetricGrid


def cone() -> ImplicitCone:
    return ImplicitCone(apex_z=1.0, half_angle_deg=40.0, apex_radius=0.2, boundary_value=700.0)


def test_tangent_cap_join_is_explicit_and_c1():
    c = cone()
    a = np.deg2rad(c.half_angle_deg)

    assert c.cap_center_z == pytest.approx(c.apex_z - c.apex_radius)
    assert c.join_radius == pytest.approx(c.apex_radius * np.cos(a))
    assert c.join_z == pytest.approx(c.apex_z - c.apex_radius + c.apex_radius * np.sin(a))
    assert c.surface_radius(c.join_z) == pytest.approx(c.join_radius)
    assert c.signed_function(c.join_radius, c.join_z) == pytest.approx(0.0, abs=1e-14)

    # Both formula gradients equal the outward sphere normal at tangency.
    expected = np.array([np.cos(a), np.sin(a)])
    assert np.array(c.normal(c.join_radius, c.join_z)) == pytest.approx(expected)

    eps = 1e-7
    slope_left = (c.surface_radius(c.join_z) - c.surface_radius(c.join_z - eps)) / eps
    slope_right = (c.surface_radius(c.join_z + eps) - c.surface_radius(c.join_z)) / eps
    assert slope_left == pytest.approx(-np.tan(a), abs=2e-6)
    assert slope_right == pytest.approx(-np.tan(a), abs=2e-6)


def test_physical_apex_and_liquid_sign_convention():
    c = cone()
    assert c.surface_radius(c.apex_z) == pytest.approx(0.0)
    assert c.signed_function(0.0, c.apex_z) == pytest.approx(0.0)

    # Behind/below the interface and inside its radius is conducting liquid.
    z = c.join_z - 0.3
    rb = c.surface_radius(z)
    assert c.signed_function(0.5 * rb, z) < 0.0
    assert c.signed_function(rb + 0.05, z) > 0.0
    # In front of the rounded physical tip is gas.
    assert c.signed_function(0.0, c.apex_z + 0.01) > 0.0


def test_gas_side_normals_are_unit_and_match_level_set_gradient():
    c = cone()
    z_values = np.array([c.join_z - 0.25, c.join_z + 0.03, c.apex_z - 0.02])
    r_values = c.surface_radius(z_values)
    nr, nz = c.normal(r_values, z_values)
    assert np.hypot(nr, nz) == pytest.approx(np.ones(3), abs=1e-14)

    h = 1e-7
    for r, z, normal in zip(r_values, z_values, zip(nr, nz)):
        # Moving along the reported normal must move from liquid into gas.
        assert c.signed_function(r + h * normal[0], z + h * normal[1]) > 0.0
        assert c.signed_function(r - h * normal[0], z - h * normal[1]) < 0.0
        grad = np.array([
            (c.signed_function(r + h, z) - c.signed_function(r - h, z)) / (2 * h),
            (c.signed_function(r, z + h) - c.signed_function(r, z - h)) / (2 * h),
        ])
        assert grad == pytest.approx(normal, abs=2e-8)


def test_graph_samples_are_exact_zero_contour_and_mark_only_flank_window():
    c = cone()
    interface = c.sample_graph(0.25, c.apex_z, 301, flank_margin=0.04)
    assert np.max(np.abs(c.signed_function(interface.R, interface.z))) < 2e-14
    assert interface.R[-1] == pytest.approx(0.0)
    assert np.any(interface.flank_mask)
    assert np.any(~interface.flank_mask)
    assert np.all(interface.z[interface.flank_mask] < c.join_z)
    assert interface.half_angle_deg() == pytest.approx(c.half_angle_deg, abs=1e-12)

    # The margin is arclength, not merely an axial offset.
    first_flank = np.flatnonzero(interface.flank_mask)[-1]
    tangent_distance = (c.join_z - interface.z[first_flank]) / np.cos(c.half_angle)
    assert tangent_distance >= 0.04 - (interface.z[1] - interface.z[0]) / np.cos(c.half_angle)


def test_masks_partition_nodes_and_match_signed_function():
    c = cone()
    grid = AxisymmetricGrid.from_params(
        GridParams(r_max=0.8, z_min=0.0, z_max=1.3, nr=17, nz=27)
    )
    conductor = c.conductor_mask(grid)
    gas = c.gas_mask(grid)
    assert np.array_equal(conductor, c.signed_function(grid.R, grid.Z) <= 0.0)
    assert np.array_equal(gas, ~conductor)
    assert not np.any(conductor & gas)
    assert np.all(conductor | gas)

    masks = c.masks(grid, ground_outer=True)
    assert np.array_equal(masks.conductor, conductor)
    assert np.array_equal(masks.powered, conductor)
    assert not np.any(masks.gas & masks.dirichlet)
    assert not np.any(masks.grounded & masks.powered)


def test_exact_segment_fraction_on_flank_cap_and_endpoint():
    c = cone()
    surface_points = [
        (c.surface_radius(c.join_z - 0.2), c.join_z - 0.2),
        (c.surface_radius(c.join_z + 0.04), c.join_z + 0.04),
    ]
    for rb, zb in surface_points:
        nr, nz = c.normal(rb, zb)
        inside_distance, outside_distance = 0.037, 0.083
        p0 = (rb - inside_distance * nr, zb - inside_distance * nz)
        p1 = (rb + outside_distance * nr, zb + outside_distance * nz)
        theta = c.segment_boundary_fraction(*p0, *p1)
        expected = inside_distance / (inside_distance + outside_distance)
        assert theta == pytest.approx(expected, abs=2e-13)
        crossing = c.segment_boundary_point(*p0, *p1)
        assert crossing == pytest.approx((rb, zb), abs=2e-13)
        assert abs(c.signed_function(*crossing)) < 2e-13

    rb, zb = surface_points[0]
    assert c.boundary_fraction(rb, zb, rb + 0.1, zb) == 0.0
    assert c.boundary_fraction(rb + 0.1, zb, rb, zb) == 1.0


def test_segment_fraction_rejects_non_bracketing_segment():
    c = cone()
    z = c.join_z - 0.2
    rb = c.surface_radius(z)
    with pytest.raises(ValueError, match="bracket"):
        c.segment_boundary_fraction(rb + 0.1, z, rb + 0.2, z)


def test_parameter_and_graph_validation():
    with pytest.raises(ValueError):
        ImplicitCone(apex_z=1.0, half_angle_deg=0.0, apex_radius=0.1)
    with pytest.raises(ValueError):
        ImplicitCone(apex_z=1.0, half_angle_deg=40.0, apex_radius=0.0)
    c = cone()
    with pytest.raises(ValueError, match="apex"):
        c.sample_graph(0.0, c.apex_z + 0.1, 20)
    with pytest.raises(ValueError, match="margin"):
        c.flank_mask(np.array([0.5]), margin=-1.0)
