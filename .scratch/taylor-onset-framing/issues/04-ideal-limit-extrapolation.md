# 04 — Ideal-limit extrapolation on the grounded-box problem (P3iii, deferred)

**What to build (later, post-deadline):** Document the angle trend of the
*actual* solver configuration (grounded box, `rectangular_electrodes`) toward
49.29° as the domain grows and the cap shrinks — or document the physical
reason the finite rounded truncated-domain problem cannot reach it.

**Why:** the committed verification is the imposed-Taylor test (ticket 03).
This is the paper's optional "on its own" story: does the grounded-box
free-boundary solve approach 49.29° in the ideal limit? Decision from the
2026-08-09 grilling session: user chose (i) now, (iii) written into the spec
as later work.

**Known difficulty (measured 2026-08-09):** the projected-residual minimum is
non-monotone under domain growth at fixed cap (42° at 1×1 → 52°+ at 2×2, the
latter at the angle-cap edge), so the domain design must be careful — vary
domain size and cap radius jointly, report the full sweep, and prefer a
documented limit over a forced number.

**Blocked by:** tickets 01, 02, 03 (needs the P1+P2 machinery and the P3i
setup as reference)

**Status:** deferred (do not start before the deadline milestone is complete)

- [ ] Domain/cap sweep table for the grounded-box projected objective
- [ ] Documented trend toward 49.29° or a documented reason it differs
- [ ] Recorded in the paper as the ideal-limit discussion, not a headline
