import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "solver"))
import numpy as np
from solver.app_backend import ImmersedVerificationParams, run_immersed_verification

base = dict(electrode_spacing=10e-3, apex_z=8.6e-3, apex_radius=0.05e-3,
            bc_type="taylor_farfield", gamma=0.022, V0=1000.0)
variants = [
    ("41x59", dict(nr=41, nz=59)),
    ("61x89", dict(nr=61, nz=89)),
    ("81x117", dict(nr=81, nz=117)),
    ("121x177", dict(nr=121, nz=177)),
    ("241x353", dict(nr=241, nz=353)),
    ("1.25x domain", dict(nr=121, nz=177, electrode_spacing=12.5e-3)),
    ("1.50x domain", dict(nr=121, nz=177, electrode_spacing=15.0e-3)),
    ("0.25% cap", dict(nr=121, nz=177, apex_radius=0.025e-3)),
    ("1.00% cap", dict(nr=121, nz=177, apex_radius=0.10e-3)),
    ("grounded outer", dict(nr=121, nz=177, bc_type="grounded")),
]
argmins = []
for name, over in variants:
    try:
        r = run_immersed_verification(ImmersedVerificationParams(**{**base, **over}))
    except Exception as exc:
        print(f"{name:16s} FAILED: {type(exc).__name__}: {exc}")
        continue
    a = np.asarray(r.landscape_angles); m = np.asarray(r.landscape_rms)
    amin = float(a[int(np.argmin(m))])
    if "grounded" not in name:
        argmins.append(amin)
    print(f"{name:16s} argmin={amin:6.2f}  recovered={r.recovered_angle_deg:7.3f} ({r.recovered_angle_method})  min_rms={r.min_rms_Pa:.5f}")
print(f"\nTaylor-farfield argmin span: {min(argmins):.2f} -- {max(argmins):.2f} deg")
print("paper 06_numerical_results.tex:24 claims: 48.0 -- 50.0 deg")
