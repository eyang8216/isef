import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "solver"))
from solver.app_backend import ImmersedVerificationParams, run_immersed_verification

# (label, nr, nz, electrode_spacing_m, apex_radius_m)
C = [
 ("41x59   0.5% cap", 41, 59, 10e-3, 0.05e-3),
 ("61x89   0.5% cap", 61, 89, 10e-3, 0.05e-3),
 ("121x177 0.5% cap", 121, 177, 10e-3, 0.05e-3),
 ("241x353 0.5% cap", 241, 353, 10e-3, 0.05e-3),
 ("121x177 0.25% cap", 121, 177, 10e-3, 0.025e-3),
 ("121x177 1.0% cap", 121, 177, 10e-3, 0.10e-3),
 ("121x177 1.25x dom", 121, 177, 12.5e-3, 0.05e-3),
 ("121x177 1.50x dom", 121, 177, 15.0e-3, 0.05e-3),
]
print(f"{'case':<20} {'recovered':>10} {'crossing':>10} {'method':>18}")
lo, hi = 1e9, -1e9
for lab, nr, nz, sp, cap in C:
    p = ImmersedVerificationParams(nr=nr, nz=nz, electrode_spacing=sp,
                                   apex_z=8.6e-3, apex_radius=cap,
                                   bc_type="taylor_farfield", gamma=0.022, V0=1000.0)
    r = run_immersed_verification(p)
    c = r.identity_exponent_crossing_deg
    print(f"{lab:<20} {r.recovered_angle_deg:>10.4f} {c:>10.4f} {r.recovered_angle_method:>18}")
    lo, hi = min(lo, c), max(hi, c)
print(f"\nreproduced crossing band: {lo:.3f} -- {hi:.3f} deg")
print(f"paper 06_numerical_results.tex:30 claims: 49.067 -- 49.176 deg")
