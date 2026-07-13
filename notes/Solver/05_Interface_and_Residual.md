# Interface and Residual

Tags: #interface #maxwell_stress #curvature

This module turns an electrostatic field into a physical stress-balance diagnostic.

## Interface representation

Initial implementation should support graph form:

$$
r=R(z).
$$

Later implementation can support parametric form:

$$
s\mapsto (r(s),z(s)).
$$

## Normal vector

For gas toward increasing \(r\):

$$
\mathbf n=\frac{(1,-R_z)}{\sqrt{1+R_z^2}}.
$$

Important: sign convention must remain consistent across curvature and Maxwell pressure.

## Axisymmetric curvature

$$
\kappa=rac{1}{R\sqrt{1+R_z^2}}-\frac{R_{zz}}{(1+R_z^2)^{3/2}}.
$$

Numerical caution: curvature is differentiation-heavy and will amplify interface noise.

## Maxwell pressure

For a conducting liquid:

$$
p_E=\frac{\varepsilon_0}{2}E_n^2,
\qquad
E_n=\mathbf E\cdot\mathbf n.
$$

## Young–Laplace–Maxwell residual

$$
\mathcal R(s)=\gamma\kappa(s)-\Delta p-\frac{\varepsilon_0}{2}E_n(s)^2.
$$

Diagnostics:

$$
\mathcal R_{\rm RMS}=\sqrt{\frac{1}{L_\Gamma}\int_\Gamma \mathcal R^2\,ds}.
$$

## Implementation plan

1. Sample interface points.
2. Compute \(R_z,R_{zz}\) using smooth basis derivatives or high-order finite difference.
3. Compute normals.
4. Interpolate grid field to interface points.
5. Compute \(E_n\).
6. Compute \(p_E\), \(\gamma\kappa\), and residual.
7. Report RMS residual, max residual, and residual profile.

Links: [[Young-Laplace-Maxwell Balance]], [[07_Shape_Optimization]]
