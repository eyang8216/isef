# ISEF Physics Solver Vault

This vault maps the theory-to-code architecture for the Taylor-cone / electrospray onset solver.

## Start here

- [[00_Solver_Architecture_Map]] — main solver architecture
- [[01_Model_Hierarchy]] — what physics we implement first vs later
- [[02_Data_Flow]] — how data moves through the solver
- [[03_Module_Map]] — planned Python modules/classes/functions
- [[04_Numerical_Core]] — axisymmetric Laplace/Poisson discretization
- [[05_Interface_and_Residual]] — Maxwell stress, curvature, residual
- [[06_Space_Charge_Shielding]] — Poisson space-charge closures
- [[07_Shape_Optimization]] — free-boundary optimization strategy
- [[08_Verification_and_Tests]] — pre-experiment verification plan
- [[09_Online_App_Interface]] — future web/Streamlit interface

## Theory source

- [[Taylor Cone Theory]]
- [[Axisymmetric Electrostatics]]
- [[Young-Laplace-Maxwell Balance]]
- [[Space Charge Theory]]

The formal LaTeX theory file is also in the project root:

- `theory.tex`
- `theory.pdf`

## Current project rule

> Until school resumes and approvals are in place, this project remains theory + computation only. No physical high-voltage or chemical experimentation.

#isef #physics #solver #obsidian
