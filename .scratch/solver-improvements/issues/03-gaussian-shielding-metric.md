# 03 — Make the Gaussian shielding metric positive

**What to build:** The Gaussian-closure shielding metric `S_E` is currently computed over the whole field, so the global maximum lands on fixed Dirichlet boundary nodes and the reported value is negative (≈ −0.7%), implying "anti-shielding". Evaluate `S_E` over an apex-local region of interest instead — exactly as the domain glossary already defines it, and as the threshold closure already does — so a Gaussian run reports a positive, physically sensible few-percent value and the paper's "shielding" claim is grounded.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Gaussian closure reports `S_E` over an apex-local region of interest, consistent with the glossary definition and the threshold closure's existing behaviour.
- [ ] Default Gaussian run reports `S_E > 0` with a magnitude in the few-percent range (not ≈ −0.7%).
- [ ] A regression test asserts `S_E > 0` and a physically reasonable magnitude for the Gaussian closure.
- [ ] The abstract's "shielding" wording matches the corrected positive metric.
