# Research Notes: Taylor-Cone FD Boundary Conditions

*Date: 2026-07-30*

---

## 1. Taylor (1964) — Conical Equilibrium and the Half-Angle

**Primary source:** G. I. Taylor, "Disintegration of water drops in an electric field," *Proc. R. Soc. London A*, 280(1382), 383–397, 1964. DOI: 10.1098/rspa.1964.0151

Taylor showed that a conducting liquid surface in equilibrium with an external electric field must be conical. In spherical coordinates (r, θ) with θ measured from the cone axis, the electrostatic potential outside a perfectly conducting cone satisfies Laplace's equation with the cone surface as an equipotential. The separable solution with the correct r-dependence is:

```
φ(r, θ) = A · r^ν · P_ν(cos θ)
```

where P_ν is the Legendre function of the first kind of degree ν. For the conical surface at polar angle θ₀ to be an equipotential (φ = 0 on the cone, taking the cone as grounded relative to the applied field), Taylor required:

```
P_ν(cos θ₀) = 0
```

Balancing the Maxwell electric stress against surface tension (Young-Laplace pressure on a cone) forces ν = 1/2. Thus the equilibrium potential is:

```
φ(r, θ) = A · r^(1/2) · P_{1/2}(cos θ)
```

and the cone half-angle satisfies P_{1/2}(cos θ₀) = 0. Taylor solved this numerically and found **θ₀ ≈ 130.7°** from the axis (equivalently, a half-angle of **49.3°** from the cone apex measured from the symmetry axis to the liquid surface). This is the "Taylor angle." The derivation appears in §3–4 of the 1964 paper; the stress-balance argument is equations (3.1)–(3.5).

---

## 2. Staircase / Grid-Mask Error on Curved Boundaries

**Primary sources:**
- G. H. Shortley and R. Weller, "The numerical solution of Laplace's equation," *J. Appl. Phys.*, 9(5), 334–348, 1938. DOI: 10.1063/1.1710426
- R. J. LeVeque, *Finite Difference Methods for Ordinary and Partial Differential Equations*, SIAM, 2007, §2.12–2.13.
- J. C. Strikwerda, *Finite Difference Schemes and Partial Differential Equations*, 2nd ed., SIAM, 2004, §1.4.

When a smooth curved boundary (here, the 49.3° cone) is represented on a Cartesian grid by flagging the nearest grid nodes as Dirichlet points, the enforced boundary is a staircase of horizontal and vertical segments. For a cone of half-angle α, grid spacing h, and radial distance r from the apex, the staircase boundary sits at a local radial error of order h relative to the true surface. Concretely, the effective polar angle of the discretized boundary oscillates around θ₀ with amplitude O(h/r).

Because the equilibrium condition is P_{1/2}(cos θ₀) = 0, any O(h) shift in the effective cone angle shifts the effective zero of P_{1/2} away from the true root. Near the root, P_{1/2} varies as (dP_{1/2}/dθ)·Δθ, so the enforced Dirichlet value on the staircase boundary is O(h) rather than zero. This introduces a first-order consistency error on the cone surface that does not vanish as h → 0 faster than O(h) — degrading the global solution from O(h²) to O(h) even with a standard second-order interior stencil. Shortley & Weller (1938) identified this class of irregular-boundary truncation error and introduced the asymmetric difference formula to restore accuracy at boundary-adjacent nodes, but that fix addresses off-axis node spacing, not the geometric misplacement of the boundary itself.

---

## 3. Ghost-Cell / Immersed Boundary Dirichlet Correction

**Primary source:** F. Gibou, R. P. Fedkiw, L.-T. Cheng, and M. Kang, "A second-order-accurate symmetric discretization of the Poisson equation on irregular domains," *J. Comput. Phys.*, 176(1), 205–227, 2002. DOI: 10.1006/jcph.2001.6977

**Supporting source:** R. P. Fedkiw, T. Aslam, B. Merriman, and S. Osher, "A non-oscillatory Eulerian approach to interfaces in multimaterial flows (the ghost fluid method)," *J. Comput. Phys.*, 152(2), 457–492, 1999. DOI: 10.1006/jcph.1999.6236

The ghost-cell (or immersed interface) approach avoids staircase error by keeping the Cartesian grid unchanged and instead modifying the finite-difference stencil at cells whose stencil crosses the true boundary. For a grid node x_i that lies inside the domain but has a neighbor x_{i+1} outside, one locates the true boundary crossing point x_b between them, evaluates the prescribed Dirichlet value φ_b there, and replaces the standard centered difference with a one-sided formula weighted by the fractional distance θ = (x_b − x_i)/h:

```
(φ_{i+1} − φ_i)/h  →  (φ_b − φ_i)/(θ·h)   [linear interpolation]
```

Gibou et al. (2002) proved this yields a second-order-accurate symmetric (positive-definite) discretization of the Poisson equation for arbitrary irregular domains, including curved boundaries. Applied to the Taylor cone, the true cone surface at each grid column is located by the analytic formula r·sin(θ) = r·sin(49.3°), and the Dirichlet condition φ = 0 is imposed at that exact sub-cell position — eliminating the O(h) staircase displacement.

---

## 4. Analytical Outer Dirichlet BC (φ = A·r^(1/2)·P_{1/2})

**Sources consulted:**
- O. A. Basaran and L. E. Scriven, "Axisymmetric shapes and stability of charged drops in an external electric field," *J. Colloid Interface Sci.*, 140(1), 10–30, 1990. DOI: 10.1016/0021-9797(90)90316-G
- J. Eggers and E. Villermaux, "Physics of liquid jets," *Rep. Prog. Phys.*, 71(3), 036601, 2008. DOI: 10.1088/0034-4885/71/3/036601

Rather than meshing the cone interior and applying a Dirichlet BC on the cone surface, an alternative formulation imposes φ = A·r^(1/2)·P_{1/2}(cos θ) on the **outer** rectangular boundary of the computational domain and solves Laplace's equation inside, letting the solution naturally produce the conical equipotential. This is the "far-field analytical BC" approach.

Basaran & Scriven (1990) use a boundary-integral / finite-element formulation for axisymmetric drops but do not explicitly adopt this outer-BC strategy; their far-field condition is a uniform applied field. Eggers & Villermaux (2008, §4.2) discuss the Taylor solution as an asymptotic outer field but do not formulate a rectangular-domain FD solver with the Taylor potential as the boundary condition. No paper in the electrospray/EHD literature appears to use the exact formulation of imposing φ = A·r^(1/2)·P_{1/2} on a rectangular outer boundary as the primary computational approach; the closest practice is using the Taylor solution as a far-field matching condition in matched-asymptotic or boundary-integral methods (Fernández de la Mora 2007, *Annu. Rev. Fluid Mech.*; Collins et al. electrospray papers use level-set/VOF methods with applied-field outer BCs, not the Taylor potential directly). This approach therefore appears to be a novel formulation in the present solver.

---

## 5. Half-Integer Legendre Function P_{1/2}

**Primary source:** NIST Digital Library of Mathematical Functions (DLMF), §14 "Legendre and Related Functions," https://dlmf.nist.gov/14, F. W. J. Olver et al. (eds.), 2010–.

P_{1/2}(x) is the Legendre function of the first kind of degree ν = 1/2 and order μ = 0. It is defined for x ∈ (−1, 1) via the hypergeometric function (DLMF 14.3.1):

```
P_{1/2}(x) = ₂F₁(−1/2, 3/2; 1; (1−x)/2)
```

or equivalently via the integral representation (DLMF 14.6.1). For x = cos θ with θ ∈ (0°, 180°), P_{1/2}(cos θ) has exactly one zero in this interval. Numerically, the zero occurs at:

```
θ₀ ≈ 130.7099°   →   cos θ₀ ≈ −0.6529
```

(This matches Taylor 1964 to four significant figures.)

**Numerical evaluation** in Python:

```python
from scipy.special import lpmv
import numpy as np

# lpmv(m, v, x) computes P_v^m(x); for P_{1/2}(cos θ) use m=0, v=0.5
theta = np.deg2rad(130.7099)
val = lpmv(0, 0.5, np.cos(theta))   # should be ≈ 0
```

`scipy.special.lpmv` implements the associated Legendre function for real non-integer degree using the hypergeometric representation; for degree 0.5 and order 0 it reduces to P_{1/2}. The DLMF (§14.2, §14.3) is the authoritative reference for the definition and special values.
