# Literature Evidence for the Taylor-Cone Solver

This file records concrete references supporting the theory used in the
reduced-order solver. It is not yet a full paper bibliography, but it gives the
main evidence chain and the caveats judges may ask about.

## Classical Taylor cone and 49.3° angle

1. **G. I. Taylor (1964), "Disintegration of water drops in an electric field," Proceedings of the Royal Society A.**
   DOI: `10.1098/rspa.1964.0151`

   Relevance: foundational derivation of the conical equilibrium of conducting
   drops in an electric field. This is the source of the classical Taylor cone
   angle used by our `taylor_cone_half_angle_deg()` benchmark.

2. **J. Fernández de la Mora (2007), "The Fluid Dynamics of Taylor Cones," Annual Review of Fluid Mechanics.**
   DOI: `10.1146/annurev.fluid.39.050905.110159`

   Relevance: review of Taylor cones, cone-jets, and electrospray fluid
   dynamics. Supports our framing that the full cone-jet is richer than the
   static Taylor angle and that our solver is a reduced onset-level model.

## Maxwell stress, interfacial EHD, and leaky dielectrics

3. **J. R. Melcher and G. I. Taylor (1969), "Electrohydrodynamics: A Review of the Role of Interfacial Shear Stresses," Annual Review of Fluid Mechanics.**
   DOI: `10.1146/annurev.fl.01.010169.000551`

   Relevance: foundational review of EHD interfacial stresses and the physical
   setting behind Maxwell stress balances. Supports the use of Maxwell stress
   at fluid interfaces.

4. **D. A. Saville (1997), "Electrohydrodynamics: The Taylor-Melcher Leaky Dielectric Model," Annual Review of Fluid Mechanics.**
   DOI: `10.1146/annurev.fluid.29.1.27`

   Relevance: authoritative review of the Taylor-Melcher leaky dielectric
   model. Supports our document's distinction between a perfect-conductor
   limit and a more complete leaky-dielectric model. Also warns that our first
   solver is not yet a full leaky-dielectric simulation.

## Cone-jet/electrospray scaling and current/onset physics

5. **A. M. Gañán-Calvo (1997), "Cone-Jet Analytical Extension of Taylor's Electrostatic Solution and the Asymptotic Universal Scaling Laws in Electrospraying," Physical Review Letters.**
   DOI: `10.1103/PhysRevLett.79.217`

   Relevance: extends Taylor-type electrostatic cone ideas toward cone-jet
   electrospraying and scaling laws. Supports the idea that Taylor's ideal
   solution is a starting point, not the final physics.

6. **J. Fernández de la Mora and I. G. Loscertales (1994), "The current emitted by highly conducting Taylor cones," Journal of Fluid Mechanics.**
   DOI: `10.1017/S0022112094003472`

   Relevance: connects Taylor cones to emitted current and conducting-liquid
   electrospray behavior. Useful later when we move beyond prescribed charge
   clouds toward current-constrained validation.

7. **R. P. A. Hartman et al. (1999), "Electrohydrodynamic atomization in the cone-jet mode: physical modeling of the liquid cone and jet," Journal of Aerosol Science.**
   DOI: `10.1016/S0021-8502(99)00033-6`

   Relevance: physical modeling of cone-jet electrospray. Supports the need to
   distinguish the liquid cone, jet, and downstream breakup as separate modeling
   levels.

## Important caveats for our solver wording

- The current solver's Gaussian `rho_e` model is a controlled Poisson-source
  experiment. It is **not** a full emission-current or ion-transport model.
- A global peak-field shielding metric can be dominated by electrode corners or
  far-boundary artifacts. Use an apex-local region-of-interest metric for serious
  shielding claims.
- The current interface residual is diagnostic. It does not yet solve the true
  moving-boundary/free-boundary problem.
- The perfect-conductor Taylor benchmark is correct as a limit, but real doped
  ethanol/electrospray operation may require conductivity, surface charge, flow,
  and current measurements for quantitative prediction.
- The 2D axisymmetric assumption is valid only for onset-level axisymmetric
  geometries before non-axisymmetric instabilities dominate.
