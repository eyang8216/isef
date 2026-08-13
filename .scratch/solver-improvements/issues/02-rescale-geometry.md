# 02 — Rescale geometry to realistic experimental dimensions

**What to build:** The app accepts experimental geometry in physical engineering units — nozzle inner/outer diameter in mm, electrode spacing in mm, apex radius in μm, surface tension in mN/m — and converts them to SI internally. The computational domain sizes itself from the electrode spacing instead of a hardcoded ~1 m box, so the default ethanol run predicts an onset voltage in the 2–5 kV literature range (today it predicts ~27 kV at metre scale) and the apex stays adequately resolved.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] App inputs use mm/μm/mN/m with realistic defaults, converted to SI (m, N/m) before the solve.
- [ ] Domain size derives from electrode spacing, not a hardcoded ~1 m box.
- [ ] Default ethanol run reports onset voltage in the 2–5 kV range (vs the current ~27 kV).
- [ ] Apex is resolved with more than 3 cells per apex radius at the default grid resolution.
- [ ] Both solver modes (classic and immersed verification) run without errors at the new scale.
- [ ] Onset-voltage sanity check against the √(γL/ε₀) scale passes.
