"""Generate source-derived nontrivial manufactured Poisson convergence data."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from solver.verification import run_quartic_manufactured_poisson, convergence_order

if __name__ == "__main__":
    cases = [(17, 19), (33, 37), (65, 73), (129, 145)]
    previous = None
    print("nr nz L2 Linf order_L2 order_Linf seconds")
    for nr, nz in cases:
        r = run_quartic_manufactured_poisson(nr, nz)
        if previous is None:
            o2 = oinf = float("nan")
        else:
            h0 = 1.0 / ((previous.nr - 1) * (previous.nz - 1)) ** 0.5
            h1 = 1.0 / ((r.nr - 1) * (r.nz - 1)) ** 0.5
            o2 = convergence_order(h0, h1, previous.l2_error, r.l2_error)
            oinf = convergence_order(h0, h1, previous.linf_error, r.linf_error)
        print(f"{nr} {nz} {r.l2_error:.8e} {r.linf_error:.8e} {o2:.5f} {oinf:.5f} {r.solve_seconds:.6f}")
        previous = r
