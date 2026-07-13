"""Run the manufactured Poisson verification case.

Usage:
    python examples/00_manufactured_poisson.py
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


from solver.verification import run_manufactured_poisson


if __name__ == "__main__":
    for nr, nz in [(25, 27), (49, 53), (97, 105)]:
        result = run_manufactured_poisson(nr, nz)
        print(
            f"{nr:4d} x {nz:<4d} | "
            f"L2={result.l2_error:.3e} Linf={result.linf_error:.3e} | "
            f"nnz={result.nnz:7d} | solve={result.solve_seconds:.4f}s"
        )
