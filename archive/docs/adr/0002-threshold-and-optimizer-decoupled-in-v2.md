# Threshold closure and shape optimizer: decoupled by default, coupled via `sc_params`

## Decision (V3 update)

The threshold-activated space-charge closure and the shape optimizer are now
optionally coupled. The V2 default (Laplace-only) is preserved: calling
`optimize_cone_shape()` without `sc_params` behaves exactly as before — Laplace
is solved once and the field is fixed for all Powell evaluations.

Passing `sc_params=SpaceChargeParams(model="threshold", ...)` enables coupled
mode: `solve_threshold_shielding()` runs on every optimizer evaluation, so the
field adjusts to the current shape's space-charge distribution. The final
`OptimizationResult` carries `sc_converged` and `sc_iterations` to report the
inner loop's status.

## Rationale for original deferral (V2)

Coupling was deferred in V2 because debugging two nonlinear loops simultaneously
— before either was individually validated — was an unnecessary risk. Both modules
needed their own verification tests first.

## Why coupling is now safe

Both modules are individually validated as of V2:
- `solve_threshold_shielding()` has a shielding sanity test confirming `S_E > 0`
  for physically sensible parameters.
- `optimize_cone_shape()` has tests confirming bounds are respected and residual
  is reduced vs. a poor starting angle.

The coupled path is exercised by `test_coupled_optimizer_differs_from_laplace_only`,
which confirms the inner loop status is reported and the residual landscape
shifts when space charge is active.

## Trade-off

Coupled mode is significantly slower: each Powell function evaluation runs the
full Poisson fixed-point iteration (typically 20–80 iterations). On a 25×41 grid
with 40 inner iterations and ~100 Powell evaluations, coupled mode takes roughly
40× longer than Laplace-only. Use `sc_params.max_iterations` and
`sc_params.tolerance` to control the inner loop cost.
