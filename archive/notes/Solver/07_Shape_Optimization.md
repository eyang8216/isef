# Shape Optimization

Tags: #optimization #free_boundary #solver

The free-boundary problem is too hard to solve first with arbitrary moving meshes. We begin with low-dimensional shape optimization.

## Shape family

Represent the interface as:

$$
R(z;\mathbf a)=R_{\rm base}(z)+\sum_{k=1}^{N}a_kB_k(z).
$$

Possible bases:

- rounded cone,
- spherical cap plus conical tail,
- spline through controlled anchor points.

## Objective function

$$
J(\mathbf a,\Delta p)=\int_\Gamma \left[\gamma\kappa-\Delta p-\frac{\varepsilon_0}{2}E_n^2\right]^2 ds+\lambda\mathcal S[\Gamma].
$$

## Constraints

- \(R(z)>0\) except possibly at a rounded apex,
- fixed nozzle radius at inlet,
- smoothness,
- no self-intersection,
- bounded curvature,
- apex radius not below grid resolution.

## Optimization sequence

1. Start with fixed prescribed interfaces.
2. Optimize only \(\Delta p\).
3. Optimize one or two geometric parameters.
4. Add spline coefficients gradually.
5. Compare optimized half-angle with Taylor limit.

## Angle extraction

Near the apex, fit a line to interface points:

$$
\tan\alpha=\left|\frac{dR}{dz}\right|.
$$

Target in ideal limit:

$$
\alpha\to49.3^\circ.
$$

Links: [[05_Interface_and_Residual]], [[01_Model_Hierarchy]]
