import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "solver"))
import numpy as np
from solver.app_backend import ImmersedVerificationParams, run_immersed_verification

r = run_immersed_verification(ImmersedVerificationParams(bc_type="taylor_farfield"))
a = np.asarray(r.landscape_angles); m = np.asarray(r.landscape_rms)
order = np.argsort(a); a, m = a[order], m[order]
mmin = m.min()
print("angles:", np.array2string(a, precision=2))
print("rms   :", np.array2string(m, precision=5))
print(f"\nmin rms = {mmin:.5f} Pa at {a[int(np.argmin(m))]:.2f} deg")
for frac in (1.02, 1.05, 1.10, 1.25, 1.50):
    sel = a[m <= frac * mmin]
    print(f"within {100*(frac-1):4.0f}% of min: {sel.min():6.2f} -- {sel.max():6.2f} deg  (width {sel.max()-sel.min():.2f})")
