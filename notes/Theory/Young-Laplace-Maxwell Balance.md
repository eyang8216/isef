# Young-Laplace-Maxwell Balance

Tags: #theory #stress_balance

The physical interface condition balances capillary pressure and electric pressure.

For a conducting liquid:

$$
p_E=\frac{\varepsilon_0}{2}E_n^2.
$$

For interface curvature \(\kappa\):

$$
\gamma\kappa=\Delta p+\frac{\varepsilon_0}{2}E_n^2.
$$

Residual form:

$$
\mathcal R=\gamma\kappa-\Delta p-\frac{\varepsilon_0}{2}E_n^2.
$$

The solver minimizes or evaluates \(\mathcal R\) along the interface.

Links: [[05_Interface_and_Residual]], [[07_Shape_Optimization]]
