"""Reproduce figure 04 via the in-repo immersed verification workflow.

`solver/solver/app_backend.py:run_immersed_verification` implements exactly the
sweep figure 04 shows: projected residual RMS vs candidate half-angle plus the
flank field exponent p(alpha), on a grid/cap/window sweep, with either a Taylor
far field or a grounded box.  Defaults: 121x177 grid, 10 mm electrode spacing,
apex z = 8.6 mm, apex radius = 0.05 mm (0.5% cap).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "solver"))

from solver.app_backend import ImmersedVerificationParams, run_immersed_verification

print(f"{'bc':>16} {'grid':>10} {'recovered':>10} {'method':>20} {'min_rms_Pa':>11} {'identity':>9}")
for bc in ("taylor_farfield", "grounded"):
    for nr, nz in ((41, 59), (61, 89), (121, 177), (241, 353)):
        res = run_immersed_verification(
            ImmersedVerificationParams(nr=nr, nz=nz, bc_type=bc)
        )
        ident = res.identity_ratio if res.identity_ratio is not None else float("nan")
        print(
            f"{bc:>16} {nr:>4}x{nz:<5} {res.recovered_angle_deg:>10.4f} "
            f"{res.recovered_angle_method:>20} {res.min_rms_Pa:>11.5f} {ident:>9.4f}"
        )
