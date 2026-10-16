import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "solver"))
import numpy as np
from solver.app_backend import ImmersedVerificationParams, run_immersed_verification

# Domain variants scaled consistently: apex_z and apex_radius track electrode_spacing
print("=== consistently scaled domain variants (apex_z = 0.86*spacing) ===")
for scale in (1.0, 1.25, 1.50, 2.0):
    sp = 10e-3 * scale
    p = ImmersedVerificationParams(nr=121, nz=177, electrode_spacing=sp,
                                   apex_z=0.86 * sp, apex_radius=0.005 * sp,
                                   bc_type="taylor_farfield", gamma=0.022, V0=1000.0)
    try:
        r = run_immersed_verification(p)
        a = np.asarray(r.landscape_angles); m = np.asarray(r.landscape_rms)
        amin = float(a[int(np.argmin(m))])
        print(f"{scale:4.2f}x  argmin={amin:6.2f}  recovered={r.recovered_angle_deg:7.3f} ({r.recovered_angle_method})  min_rms={r.min_rms_Pa:.5f}")
    except Exception as exc:
        print(f"{scale:4.2f}x  FAILED: {type(exc).__name__}: {exc}")

print("\n=== unscaled (apex fixed at 8.6 mm), as used in my earlier runs ===")
for scale in (1.0, 1.25, 1.50):
    sp = 10e-3 * scale
    p = ImmersedVerificationParams(nr=121, nz=177, electrode_spacing=sp,
                                   apex_z=8.6e-3, apex_radius=0.05e-3,
                                   bc_type="taylor_farfield", gamma=0.022, V0=1000.0)
    try:
        r = run_immersed_verification(p)
        a = np.asarray(r.landscape_angles); m = np.asarray(r.landscape_rms)
        amin = float(a[int(np.argmin(m))])
        print(f"{scale:4.2f}x  argmin={amin:6.2f}  recovered={r.recovered_angle_deg:7.3f} ({r.recovered_angle_method})  min_rms={r.min_rms_Pa:.5f}")
    except Exception as exc:
        print(f"{scale:4.2f}x  FAILED: {type(exc).__name__}: {exc}")
