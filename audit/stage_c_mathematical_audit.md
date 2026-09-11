# Stage C — Mathematical formulation audit
Date: 2026-09-08
Status: completed audit; no solver source changes made.

## Bottom line
The active solver implements the axisymmetric Laplace/Poisson operator and a graph-interface Young–Laplace–Maxwell residual consistently at the component level. However, the paper currently presents a broader physical interpretation than the code closes. The primary pre-lab model must be described as a prescribed-interface/reduced stress-residual calculation unless a complete interface closure is implemented and verified.

## Equation-to-code map
| Mathematical item | Manuscript | Implementation | Stage C finding |
|---|---|---|---|
| Axisymmetric Laplace operator | Sec. 4 | `solver/solver/operators.py::build_axisymmetric_laplacian` | Matches \(phi_rr+r^{-1}phi_r+phi_zz\); axis uses regularized \(2phi_{rr}\) limit. Boundary rows are placeholders until overwritten. |
| Poisson equation | Sec. 4 | `poisson_rhs` | Implements \(nabla^2phi=-rho_e/eps\). Sign is consistent with \(E=-nabla phi\) under the stated convention. |
| Electric field | Sec. 4 | `fields.py::compute_electric_field` | Implements \(E_r=-phi_r,E_z=-phi_z\); NumPy array axes must remain documented as `(r,z)`. |
| Dirichlet conductors | Sec. 4/solver architecture | `boundary_conditions.py` | Grounded=0 and powered/conductor=V0. Far boundary is optional Dirichlet; the paper must not imply a unique finite-electrode setup unless masks/input are specified. |
| Graph interface | Sec. 4 | `interface.py::GraphInterface` | Represents \(r=R(z)\), requires strictly increasing z and nonnegative R. This excludes overhangs and many general free boundaries. |
| Gas-side normal | Sec. 4 | `GraphInterface.normals` | Returns \((1,-R_z)/sqrt(1+R_z^2)\), pointing toward increasing r. This is a valid graph normal but the paper must use the same orientation in pressure jump. |
| Mean-curvature sum | Sec. 4 | `GraphInterface.curvature` | Implements \(1/(R sqrt(1+R_z^2))-R_{zz}/(1+R_z^2)^{3/2}\). It is curvature sum, not half the mean curvature. Apex/axis singularity requires a stated exclusion/regularization. |
| Maxwell normal pressure | Sec. 4 | `residual.py::compute_residual` | Uses \(p_E=eps_g E_n^2/2\), with supplied/interpolated normal field. This assumes the gas-side field and conductor stress simplification. |
| Young–Laplace residual | Sec. 4 | `compute_residual` | Uses \(gamma kappa-Delta p-p_E\). Sign is internally consistent with the documented formula only if `kappa` and `Delta p` use the same orientation. |
| Pressure offset | Sec. 4 | `compute_residual` | If absent, sets Delta p to the mean of \(gamma kappa-p_E\), forcing zero mean residual. This is a projection/diagnostic choice, not an independent pressure closure or proof of equilibrium. |
| Half angle | Sec. 4/experimental | `GraphInterface.half_angle_deg`; experimental module separately | Graph routine fits selected samples and returns `atan(abs(slope))`; absolute value removes orientation information. Experimental sign and coordinate behavior need distinct audit. |
| Space charge | Sec. 4/limitations | `space_charge.py` | Gaussian and threshold closures are explicit phenomenological models, not derived charge transport. Their outputs must be exploratory unless independently justified. |
| Immersed boundary | Sec. 5 | `immersed.py` | Replaces stencil neighbor with interface point using unequal polynomial weights. Local exactness does not establish global convergence of the coupled free-boundary calculation. |

## Critical interpretation findings

1. `compute_residual` can make a candidate look improved by fitting the constant pressure offset from the same samples. The resulting RMS is the residual after removing its mean component, not the RMS under independently prescribed pressure.
2. The paper's phrase “interface determines Taylor-cone onset geometry” should be narrowed. The active graph residual diagnostics evaluate a supplied interface; the optimizer and far-field routines need a separate audit to determine whether they solve for a free boundary or search a restricted family.
3. A projected voltage/balance calculation must state whether electrostatics is linear and charge-free. Threshold space charge is nonlinear and does not inherit simple V² scaling.
4. The graph representation `r=R(z)` cannot represent arbitrary overhanging interfaces. Any free-boundary claim must be limited to single-valued graphs.
5. Curvature diverges as `R` approaches zero. The apex is therefore excluded, rounded or regularized in any quantitative comparison. The paper must state the cutoff and sensitivity.
6. Optional far-boundary Dirichlet values and conductor masks make results boundary-configuration dependent. “Finite grounded box” and “analytical far field” must be separate named cases.
7. The residual's pressure fitting can make the mean residual exactly zero by construction. Mean residual is therefore not a useful independent validation statistic.
8. The operator docstring and code use the axis limit \(2phi_{rr}\); this is correct for an even smooth axisymmetric field because \(phi_{rr}+r^{-1}phi_r\to2phi_{rr}\), but axis convergence needs its own test.

## Required Stage D/C follow-up

Before numerical-accuracy claims are retained, add a direct equation-to-code test for pressure projection, a prescribed-pressure residual, analytic sphere/cylinder/cone curvature cases where nonsingular, axis-limit field cases, and boundary-mask precedence. Audit optimization separately for true unknown interface degrees of freedom, constraints and objective normalization. Add explicit dimensionless definitions and an assumption table to the paper.

## Paper language approved after this audit

“a reduced axisymmetric electrostatic–capillary solver and stress-residual framework for single-valued graph interfaces” is supported as a working description.

“a complete physical predictor of Taylor-cone onset, cone–jet transition or arbitrary finite-nozzle meniscus shape” is not supported by this audit.

## Stage C gate

- [x] Read theory section and active mathematical modules.
- [x] Map core equations to implementation.
- [x] Identify sign, coordinate, closure and interpretation risks.
- [x] Distinguish diagnostic residual from independently closed equilibrium.
- [x] Record required follow-up tests and wording.
- [ ] Implement Stage C repairs/tests (Stage D implementation work).
- [ ] Rewrite paper equations and claims (manuscript stage).
