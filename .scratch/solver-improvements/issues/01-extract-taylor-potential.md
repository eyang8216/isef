# 01 — Extract and test the analytical Taylor potential

**What to build:** A single, importable `taylor_potential(r, z, …)` function in the solver package that returns the analytical Taylor-cone potential (`φ ∝ R^½ · P_½(cos θ)`), replacing the two current in-place copies (one in the verification backend, one in its test). This is a pure prefactor: no numerical behaviour changes, it just makes the far-field boundary condition in ticket 04 a small wiring change.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] One importable `taylor_potential` function lives in the solver package, parameterized by reference length and amplitude.
- [ ] Both prior call sites (verification backend and its test) import it; no duplication remains.
- [ ] A unit test asserts the potential is constant on the ideal 49.3° half-angle cone surface (relative std < 1%).
- [ ] Full test suite stays green — the extraction introduces no numerical behaviour change.
