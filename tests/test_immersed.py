import math

import numpy as np
import pytest
from scipy.sparse.linalg import spsolve
from solver.config import GridParams
from solver.geometry import ImplicitCone
from solver.grid import AxisymmetricGrid
from solver.immersed import _unequal_weights, apply_immersed_dirichlet, normal_field_on_interface
from solver.operators import build_axisymmetric_laplacian


def _grid(nr=7, nz=8):
    return AxisymmetricGrid.from_params(GridParams(r_max=1.2, z_min=-0.4, z_max=1.0, nr=nr, nz=nz))


def test_unequal_weights_exact_polynomials():
    for xb, xo, q in [(-.037,.2,0),(.083,-.2,0),(-.051,.2,2.7),(.119,-.2,2.7)]:
        w=np.asarray(_unequal_weights(xb,xo,q)); x=np.asarray([xb,0,xo])
        for degree in range(3):
            assert w @ x**degree == pytest.approx((2 if degree==2 else 0)+(q if degree==1 else 0))

class _PlanarCut:
    boundary_value=4.25
    def __init__(self,axis,location,conductor_less): self.axis,self.location,self.conductor_less=axis,location,conductor_less
    def conductor_mask(self,g):
        x=g.R if self.axis=='r' else g.Z
        return x < self.location if self.conductor_less else x > self.location
    def boundary_fraction(self,r0,z0,r1,z1):
        x0=r0 if self.axis=='r' else z0; x1=r1 if self.axis=='r' else z1
        return (self.location-x0)/(x1-x0)

def _assert_cut(cut,i,j,side,rhs_value):
    g=_grid(); A0=build_axisymmetric_laplacian(g); b0=np.full(g.size,rhs_value)
    A,b=apply_immersed_dirichlet(A0,b0,g,cut); row=A.getrow(g.idx(i,j)).toarray().ravel(); expected=A0.getrow(g.idx(i,j)).toarray().ravel()
    if cut.axis=='z':
        h=g.dz; other=g.idx(i,j-side); neighbour=g.idx(i,j+side); frac=abs(cut.location-g.z[j])/h; wb,wc,wo=_unequal_weights(side*frac*h,-side*h)
        expected[g.idx(i,j-1)]-=1/h**2; expected[g.idx(i,j)]+=2/h**2; expected[g.idx(i,j+1)]-=1/h**2
    else:
        h=g.dr; other=g.idx(i-side,j); neighbour=g.idx(i+side,j); frac=abs(cut.location-g.r[i])/h; wb,wc,wo=_unequal_weights(side*frac*h,-side*h,1/g.r[i])
        cp=(g.r[i]+h/2)/(g.r[i]*h**2); cm=(g.r[i]-h/2)/(g.r[i]*h**2); expected[g.idx(i-1,j)]-=cm; expected[g.idx(i,j)]+=cm+cp; expected[g.idx(i+1,j)]-=cp
    expected[g.idx(i,j)]+=wc; expected[other]+=wo
    assert row[neighbour] == pytest.approx(0); assert row == pytest.approx(expected); assert b[g.idx(i,j)] == pytest.approx(rhs_value-wb*cut.boundary_value)

def test_axial_cuts_both_sides():
    g=_grid(); j=3
    _assert_cut(_PlanarCut('z',g.z[j]-.31*g.dz,True),3,j,-1,-7)
    _assert_cut(_PlanarCut('z',g.z[j]+.64*g.dz,False),3,j,1,-7)

def test_radial_cuts_both_sides():
    g=_grid(); i=3
    _assert_cut(_PlanarCut('r',g.r[i]-.42*g.dr,True),i,4,-1,2.5)
    _assert_cut(_PlanarCut('r',g.r[i]+.73*g.dr,False),i,4,1,2.5)

def test_conductor_rows_identity_and_input_unchanged():
    g=_grid(); c=_PlanarCut('r',.47,True); A0=build_axisymmetric_laplacian(g); b0=np.arange(g.size,dtype=float); A,b=apply_immersed_dirichlet(A0,b0,g,c)
    assert (A0 != build_axisymmetric_laplacian(g)).nnz==0
    for i,j in np.argwhere(c.conductor_mask(g)):
        row=A.getrow(g.idx(int(i),int(j))); assert row.nnz==1 and row.indices[0]==g.idx(int(i),int(j)) and row.data[0]==1 and b[g.idx(int(i),int(j))]==c.boundary_value

def test_tiny_cut_falls_back_to_dirichlet_row():
    """A cut within min_fraction of the gas node pins that node to the boundary
    value (identity row) instead of forming a near-singular stencil or raising."""
    g = _grid()
    cut = _PlanarCut("r", g.r[3] - 5e-7 * g.dr, True)  # fraction ~5e-7 < min_fraction
    A, b = apply_immersed_dirichlet(
        build_axisymmetric_laplacian(g), np.zeros(g.size), g, cut
    )
    row = A.getrow(g.idx(3, 4)).toarray().ravel()
    assert row[g.idx(3, 4)] == pytest.approx(1.0)
    assert row.sum() == pytest.approx(1.0)  # identity row, no other stencil entries
    assert b[g.idx(3, 4)] == pytest.approx(cut.boundary_value)


def test_degenerate_zero_fraction_rejected():
    """A boundary exactly on the gas node (fraction 0) is an adjacency/geometry
    mismatch, not a small cut, and must still be rejected."""
    g = _grid()
    cut = _PlanarCut("r", g.r[3], True)  # boundary exactly on the node
    with pytest.raises(ValueError, match="pathological"):
        apply_immersed_dirichlet(build_axisymmetric_laplacian(g), np.zeros(g.size), g, cut)

def test_normal_field_one_sided():
    g=AxisymmetricGrid.from_params(GridParams(r_max=2,z_min=-1,z_max=2,nr=31,nz=35)); c=ImplicitCone(1,35,.3,8)
    z=np.asarray([c.join_z-.15,c.join_z-.3]); r=np.asarray(c.surface_radius(z)); a=c.half_angle
    potential=c.boundary_value+2.75*((g.R-c.join_radius)*np.cos(a)+(g.Z-c.join_z)*np.sin(a))
    assert normal_field_on_interface(g,potential,c,r,z,sample_distance=.025)==pytest.approx(np.full(2,-2.75),abs=2e-13)

def test_smooth_immersed_manufactured_solution_second_order_convergence():
    """Formal Richardson order check for the immersed Dirichlet stencil.

    This is the *declared* manufactured test for the immersed operator — a
    smooth curved irregular boundary (a circle), deliberately independent of
    the singular Taylor potential. Gibou et al. (2002) proved that the
    fractional-distance ghost-cell discretization is second-order accurate on
    curved boundaries; the O(h) staircase error it replaces (Shortley & Weller
    1938) was the original motivation for the immersed path. We therefore
    assert an observed L2 order >= 1.8, i.e. an error ratio <= 2**-1.8 ~= 0.29
    per grid doubling (the spec's "0.57 per doubling" figure is inconsistent
    with order >= 1.8 and is treated as superseded by the direct order check).

    Declared norm/region: L2 over gas nodes, excluding the outer Dirichlet
    ring (and, by construction, the conductor interior).
    """

    class Circle:
        boundary_value = 0.0

        def __init__(self):
            self.radius = 0.31
            self.center_z = 1.03

        def signed_function(self, r, z):
            return np.asarray(r) ** 2 + (np.asarray(z) - self.center_z) ** 2 - self.radius**2

        def conductor_mask(self, g):
            return self.signed_function(g.R, g.Z) <= 0

        def boundary_fraction(self, r0, z0, r1, z1):
            dr, dz = r1 - r0, z1 - z0
            y = z0 - self.center_z
            aa = dr * dr + dz * dz
            bb = 2 * (r0 * dr + y * dz)
            cc = r0 * r0 + y * y - self.radius**2
            roots = np.roots((aa, bb, cc))
            return min(
                float(x.real)
                for x in roots
                if abs(x.imag) < 1e-10 and -1e-10 <= x.real <= 1 + 1e-10
            )

    # Grid levels chosen so the spacing halves at each refinement.
    levels = ((25, 33), (49, 65), (97, 129))
    errors: list[float] = []
    spacings: list[float] = []
    for nr, nz in levels:
        g = AxisymmetricGrid.from_params(GridParams(1.5, 0, 2, nr, nz))
        c = Circle()
        y = g.Z - c.center_z
        q = g.R**2 + y**2 - c.radius**2
        exact = q * np.exp(g.Z)
        source = np.exp(g.Z) * (6 + 4 * y + q)
        outer = np.zeros(g.shape, bool)
        outer[-1, :] = True
        outer[:, 0] = True
        outer[:, -1] = True
        from solver.boundary_conditions import apply_dirichlet_values

        A, b = apply_dirichlet_values(
            build_axisymmetric_laplacian(g), g.flatten(source), g, outer, exact
        )
        A, b = apply_immersed_dirichlet(A, b, g, c, fixed_mask=outer)
        sol = g.unflatten(spsolve(A, b))
        gas = ~c.conductor_mask(g) & ~outer
        errors.append(float(np.sqrt(np.mean((sol[gas] - exact[gas]) ** 2))))
        spacings.append(g.dr)
    assert all(h > 0 for h in spacings)
    # Observed order between consecutive levels: p = ln(e_i/e_{i+1}) / ln(h_i/h_{i+1}).
    orders = [
        math.log(errors[i] / errors[i + 1]) / math.log(spacings[i] / spacings[i + 1])
        for i in range(len(errors) - 1)
    ]
    for i, order in enumerate(orders, start=1):
        assert order >= 1.8, (
            f"observed order between levels {i} and {i + 1} is {order:.2f} (< 1.8); "
            f"errors per level: {[f'{e:.3e}' for e in errors]}"
        )
    # Keep a mild monotone-decrease sanity check as a second, weaker guard.
    assert errors[-1] < errors[0] * 0.5
