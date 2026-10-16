import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "solver"))
import numpy as np
from solver.app_backend import ImmersedVerificationParams, run_immersed_verification

variants = [
    ("41x59", dict(nr=41, nz=59)),
    ("61x89", dict(nr=61, nz=89)),
    ("121x177", dict(nr=121, nz=177)),
    ("241x353", dict(nr=241, nz=353)),
    ("121x177 0.25% cap", dict(nr=121, nz=177, apex_radius=0.025e-3)),
    ("121x177 1.00% cap", dict(nr=121, nz=177, apex_radius=0.10e-3)),
]
base = dict(electrode_spacing=10e-3, apex_z=8.6e-3, apex_radius=0.05e-3,
            bc_type="taylor_farfield", gamma=0.022, V0=1000.0)
res = []
for name, over in variants:
    p = ImmersedVerificationParams(**{**base, **over})
    r = run_immersed_verification(p)
    a = np.asarray(r.landscape_angles); m = np.asarray(r.landscape_rms)
    amin = float(a[int(np.argmin(m))])
    res.append(amin)
    print(f"{name:22s} argmin_angle={amin:7.2f}  recovered={r.recovered_angle_deg:7.3f} ({r.recovered_angle_method})  min_rms={r.min_rms_Pa:.5f}")
print(f"argmin span = {min(res):.2f} to {max(res):.2f} deg  (half-width {0.5*(max(res)-min(res)):.2f})")
