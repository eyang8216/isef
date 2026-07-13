# Axisymmetric Electrostatics

Tags: #theory #electrostatics

The computational core solves electrostatics in cylindrical coordinates.

For an axisymmetric potential:

$$
\nabla^2\phi=\frac{1}{r}\frac{\partial}{\partial r}\left(r\frac{\partial\phi}{\partial r}\right)+\frac{\partial^2\phi}{\partial z^2}.
$$

Laplace model:

$$
\nabla^2\phi=0.
$$

Poisson model:

$$
\nabla^2\phi=-\frac{\rho_e}{\varepsilon_0}.
$$

Boundary conditions:

- powered boundary: \(\phi=V_0\),
- ground: \(\phi=0\),
- axis: \(\partial_r\phi=0\),
- far boundary: Dirichlet or Neumann.

Links: [[04_Numerical_Core]], [[06_Space_Charge_Shielding]]
