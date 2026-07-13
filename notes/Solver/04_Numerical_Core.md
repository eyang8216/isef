# Numerical Core

Tags: #numerics #poisson #laplace #solver

The numerical core is the sparse axisymmetric Laplace/Poisson solver.

## Governing operator

For axisymmetric \(\phi(r,z)\):

$$
\nabla^2\phi=rac{1}{r}\frac{\partial}{\partial r}\left(r\frac{\partial\phi}{\partial r}\right)+\frac{\partial^2\phi}{\partial z^2}.
$$

Laplace:

$$
\nabla^2\phi=0.
$$

Poisson:

$$
\nabla^2\phi=-\frac{\rho_e}{\varepsilon_0}.
$$

## Discretization choice

Use finite-volume style radial discretization:

$$
\frac{1}{r_i\Delta r}\left[
r_{i+1/2}\frac{\phi_{i+1,j}-\phi_{i,j}}{\Delta r}
-
r_{i-1/2}\frac{\phi_{i,j}-\phi_{i-1,j}}{\Delta r}
\right].
$$

Axial discretization:

$$
\frac{\phi_{i,j+1}-2\phi_{i,j}+\phi_{i,j-1}}{\Delta z^2}.
$$

## Axis treatment

At \(r=0\), regularity requires:

$$
\partial_r\phi=0.
$$

Use the limit:

$$
\lim_{r\to0}\left(\phi_{rr}+\frac{1}{r}\phi_r\right)=2\phi_{rr}(0,z).
$$

Discrete axis radial part:

$$
2\phi_{rr}(0,z_j)\approx \frac{4(\phi_{1,j}-\phi_{0,j})}{\Delta r^2}.
$$

## Matrix form

The solve is:

$$
A\boldsymbol\phi=\mathbf b.
$$

Required design decision:

- use one flattened index \(k=iN_z+j\), or
- use \(k=jN_r+i\).

Choose one and never mix.

## Boundary conditions

Dirichlet rows become identity rows:

$$
A_{kk}=1,\qquad b_k=\phi_{bc}.
$$

Boundary types:

- powered conductor/liquid surface: \(\phi=V_0\),
- grounded extractor: \(\phi=0\),
- axis: \(\partial_r\phi=0\),
- far boundary: Dirichlet or Neumann depending on test.

## Numerical risks

- wrong sign in Poisson source,
- singularity at \(r=0\),
- artificial far-boundary effects,
- field noise from differentiating \(\phi\),
- incorrectly masking conductor boundaries,
- dense matrix memory explosion.

Links: [[Axisymmetric Electrostatics]], [[03_Module_Map]], [[08_Verification_and_Tests]]
