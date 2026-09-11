# Taylor-Cone Electrospray Solver

Reduced-order axisymmetric electrostatic-capillary solver for studying Taylor-cone onset and space-charge shielding effects. Not a full CFD or EHD simulator.

## Language

### Electrostatics

**Residual**:
The pointwise Young–Laplace–Maxwell pressure mismatch along the interface: `γκ - Δp - ½ε₀Eₙ²`. A scalar field on the interface, not an iteration error.
_Avoid_: error, mismatch, imbalance

**Shielding metric**:
`S_E = 1 - Emax_shielded / Emax_reference`, computed over an apex-local region of interest. Positive means field was reduced; negative indicates a sign/model problem.
_Avoid_: shielding factor, attenuation

**Half-angle**:
The cone half-angle α, estimated as `arctan(|dR/dz|)` fitted near the apex on the current interface. Always the absolute value of slope — never signed. Target in the ideal Laplace limit: 49.3°.
_Avoid_: cone angle, Taylor angle, apex angle

### Interface and geometry

**Interface**:
The candidate liquid surface, represented as a graph `R(z)` with sampled points. Does not refer to the liquid bulk or the gas domain.
_Avoid_: surface, meniscus, boundary (when meaning the liquid surface)

**Apex**:
The tip of the interface where `R` is smallest. The region of interest for shielding metrics and optimizer angle extraction.
_Avoid_: tip, cone point

**Nozzle radius**:
The fixed outer radius of the interface at its inlet (top of domain). A geometric constraint, not a free parameter.
_Avoid_: emitter radius, base radius

### Space charge

**Closure**:
The constitutive relation that maps the electric field magnitude to the space-charge density `ρ_e`. Version 1 uses a prescribed Gaussian closure; Version 2 adds a threshold-activated closure. The word "closure" refers specifically to this mapping, not to the iteration scheme.
_Avoid_: model (when meaning closure), charge model

**Fixed-point iteration**:
The outer loop that alternates between solving the Poisson equation for `φ` and updating `ρ_e` from the closure, with under-relaxation. Distinct from the shape optimizer's inner loop.
_Avoid_: Poisson iteration, charge iteration

### Optimization

**Shape parameters**:
The scalar degrees of freedom in the analytic cone family (e.g. cone angle, apex radius). Not spline control points.
_Avoid_: design variables, coefficients (when meaning shape parameters)
