# Model Hierarchy

Tags: #theory #model_hierarchy #solver

The solver must not begin as an overcomplicated full electrospray simulator. It should be built in physics levels.

## Level 0 — Classical Taylor cone

Goal: reproduce the analytical result

$$
\alpha_T \approx 49.3^\circ.
$$

Key equation:

$$
P_{1/2}(\cos\vartheta_0)=0.
$$

Purpose: benchmark the theory and provide a judge-understandable analytical anchor.

Links: [[Taylor Cone Theory]]

## Level 1 — Axisymmetric Laplace electrostatics

Solve charge-free electrostatics in the gas domain:

$$
\frac{1}{r}\frac{\partial}{\partial r}\left(r\frac{\partial \phi}{\partial r}\right)+\frac{\partial^2\phi}{\partial z^2}=0.
$$

Links: [[Axisymmetric Electrostatics]], [[04_Numerical_Core]]

## Level 2 — Young–Laplace–Maxwell residual

For a candidate interface, evaluate:

$$
\mathcal{R}=\gamma\kappa-\Delta p-\frac{\varepsilon_0}{2}E_n^2.
$$

Links: [[Young-Laplace-Maxwell Balance]], [[05_Interface_and_Residual]]

## Level 3 — Free-boundary shape optimization

Represent the interface by a low-dimensional parameter vector:

$$
R(z;\mathbf a)=R_{\rm base}(z)+\sum_k a_k B_k(z).
$$

Minimize:

$$
J(\mathbf a,\Delta p)=\int_\Gamma \mathcal R^2\,ds+\lambda\mathcal S[\Gamma].
$$

Links: [[07_Shape_Optimization]]

## Level 4 — Poisson space-charge shielding

Replace Laplace with:

$$
\nabla^2\phi=-\frac{\rho_e}{\varepsilon_0}.
$$

First closures:

- prescribed Gaussian cloud,
- threshold-activated effective charge.

Links: [[Space Charge Theory]], [[06_Space_Charge_Shielding]]

## Level 5 — Later leaky-dielectric/transport modules

Not the first core claim. Possible later additions:

- liquid potential solve,
- surface charge conservation,
- drift-diffusion-Poisson gas charge transport,
- current-constrained shielding.

This level is useful for future sophistication but should not block the first solver.
