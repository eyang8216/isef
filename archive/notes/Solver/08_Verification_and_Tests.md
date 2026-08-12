# Verification and Tests

Tags: #verification #testing #numerics

Before any experiment, the solver must pass internal mathematical tests.

## Test 1 — Taylor angle benchmark

Recover:

$$
\alpha_T\approx49.3^\circ.
$$

This validates the classical limit.

## Test 2 — manufactured Poisson solution

Choose an exact function, e.g.

$$
\phi_{\rm exact}(r,z)=r^2+z^2.
$$

Compute the axisymmetric Laplacian analytically and set the source accordingly. Verify convergence.

## Test 3 — grid refinement

Run the same case at increasing resolutions:

- \(50\times50\),
- \(100\times100\),
- \(200\times200\),
- \(400\times400\), if feasible.

Track convergence of:

- potential,
- field magnitude,
- RMS residual,
- predicted angle,
- runtime.

## Test 4 — boundary conditions

Check:

- powered conductor is fixed at \(V_0\),
- grounded electrode is fixed at zero,
- axis satisfies \(\partial_r\phi=0\),
- far boundary does not dominate the cone region.

## Test 5 — stress scaling

Electric pressure should scale like:

$$
p_E\propto V_0^2.
$$

The dimensionless electric Bond number is:

$$
\mathrm{Bo}_E=\frac{\varepsilon_0V_0^2}{\gamma L}.
$$

## Test 6 — shielding sanity check

Positive shielding model should reduce peak field relative to Laplace in the intended sign convention:

$$
E_{\max}^{\rm shielded}<E_{\max}^{\rm Laplace}.
$$

## Test 7 — runtime and memory

Record:

- grid size,
- operator nonzeros,
- solve time,
- total runtime,
- memory estimate.

Links: [[04_Numerical_Core]], [[06_Space_Charge_Shielding]]
