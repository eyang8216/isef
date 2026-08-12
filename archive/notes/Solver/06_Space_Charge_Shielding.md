# Space Charge Shielding

Tags: #space_charge #poisson #shielding

The space-charge module upgrades the gas-domain electrostatics from Laplace to Poisson:

$$
\nabla^2\phi=-\frac{\rho_e}{\varepsilon_0}.
$$

## Goal

Regularize/reduce the unphysical apex field singularity in the ideal Taylor cone model.

## Closure A — prescribed Gaussian cloud

$$
\rho_e(r,z)=\rho_0\exp\left[-\frac{(r-r_a)^2+(z-z_a)^2}{2\ell^2}\right].
$$

Purpose:

- test Poisson solver,
- study sensitivity to shielding strength,
- demonstrate field reduction near apex.

## Closure B — threshold-activated charge

$$
\rho_e=\rho_{\max}\left[1-\exp\left(-\frac{|\mathbf E|-E_c}{E_s}\right)\right]_+.
$$

This is nonlinear because \(\rho_e\) depends on \(\phi\).

## Fixed-point iteration

```mermaid
flowchart TD
    A[Initialize rho_e] --> B[Solve Poisson]
    B --> C[Compute E]
    C --> D[Update rho_e = F(|E|)]
    D --> E[Under-relax rho_e]
    E --> F{Converged?}
    F -- no --> B
    F -- yes --> G[Return shielded solution]
```

Under-relaxation:

$$
\rho_e^{k+1}=(1-\omega)\rho_e^k+\omega\widetilde\rho_e^{k+1}.
$$

## Shielding metric

$$
S_E=1-\frac{E_{\max}^{\rm shielded}}{E_{\max}^{\rm Laplace}}.
$$

Interpretation:

- \(S_E=0\): no shielding,
- \(S_E>0\): peak field reduced,
- \(S_E<0\): sign convention or model issue to investigate.

## Risks

- wrong sign for \(\rho_e\),
- artificial charge accumulation at boundaries,
- fixed-point oscillation,
- nonphysical parameter choices,
- false stability caused by excessive smoothing.

Links: [[Space Charge Theory]], [[04_Numerical_Core]], [[08_Verification_and_Tests]]
