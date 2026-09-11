#!/usr/bin/env python3
"""Generate grid convergence plot for paper Section 6.

Creates a log-log plot showing second-order convergence of the Poisson solver.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Data from Table 1 in the paper (manufactured Poisson convergence)
# Grid sizes and corresponding L2 errors
grids = [
    (25, 27),
    (49, 53),
    (97, 105),
]

# L2 and Linf errors from the paper
l2_errors = [8.104e-4, 1.992e-4, 4.936e-5]
linf_errors = [1.353e-3, 3.389e-4, 8.479e-5]

# Compute effective grid spacing (geometric mean of dr and dz)
# Domain is roughly 1x1, so spacing ≈ 1/N
grid_spacings = [1.0 / np.sqrt(nr * nz) for nr, nz in grids]

# Compute convergence order between successive refinements
def compute_order(h1, h2, e1, e2):
    """Compute convergence order p where e ~ h^p"""
    return np.log(e1 / e2) / np.log(h1 / h2)

orders_l2 = []
for i in range(len(grids) - 1):
    order = compute_order(grid_spacings[i], grid_spacings[i+1],
                         l2_errors[i], l2_errors[i+1])
    orders_l2.append(order)

mean_order = np.mean(orders_l2)
std_order = np.std(orders_l2)

print(f"Convergence orders (L2): {orders_l2}")
print(f"Mean order: {mean_order:.3f} ± {std_order:.3f}")

# Create figure
fig, ax = plt.subplots(figsize=(7, 5))

# Plot L2 and Linf errors
ax.loglog(grid_spacings, l2_errors, 'o-', linewidth=2, markersize=8,
          label='L² error', color='#2E86AB')
ax.loglog(grid_spacings, linf_errors, 's-', linewidth=2, markersize=8,
          label='L∞ error', color='#A23B72')

# Plot reference slopes
h_ref = np.array([grid_spacings[0], grid_spacings[-1]])

# First-order reference
e_ref_1 = l2_errors[0] * (h_ref / grid_spacings[0])**1
ax.loglog(h_ref, e_ref_1, '--', linewidth=1.5, color='gray', alpha=0.6,
          label='First order (slope = 1)')

# Second-order reference
e_ref_2 = l2_errors[0] * (h_ref / grid_spacings[0])**2
ax.loglog(h_ref, e_ref_2, '--', linewidth=1.5, color='black', alpha=0.8,
          label='Second order (slope = 2)')

# Labels and formatting
ax.set_xlabel('Grid spacing Δh', fontsize=12)
ax.set_ylabel('Error', fontsize=12)
ax.set_title('Manufactured Poisson Solution Convergence', fontsize=13, fontweight='bold')
ax.grid(True, which='both', alpha=0.3, linestyle=':')
ax.legend(loc='upper left', fontsize=10)

# Add convergence order annotation
textstr = f'Measured order:\n$p = {mean_order:.2f} \\pm {std_order:.2f}$'
ax.text(0.65, 0.25, textstr, transform=ax.transAxes, fontsize=11,
        verticalalignment='top', bbox=dict(boxstyle='round',
        facecolor='wheat', alpha=0.5))

# Add grid size labels
for i, (h, e) in enumerate(zip(grid_spacings, l2_errors)):
    nr, nz = grids[i]
    ax.annotate(f'{nr}×{nz}', (h, e), textcoords="offset points",
                xytext=(10, -5), ha='left', fontsize=9, color='#2E86AB')

plt.tight_layout()

# Save figure
output_dir = Path(__file__).parent / 'paper_submission' / 'figures'
output_dir.mkdir(exist_ok=True)
output_file = output_dir / 'poisson_convergence.pdf'

plt.savefig(output_file, bbox_inches='tight', dpi=300)
print(f"\nFigure saved to: {output_file}")

# Also save as PNG for preview
output_file_png = output_dir / 'poisson_convergence.png'
plt.savefig(output_file_png, bbox_inches='tight', dpi=150)
print(f"PNG preview saved to: {output_file_png}")

plt.show()

# Print LaTeX figure code
print("\n" + "="*60)
print("LATEX FIGURE CODE FOR PAPER")
print("="*60)
print()
print(r"\begin{figure}[H]")
print(r"\centering")
print(r"\includegraphics[width=0.7\textwidth]{figures/poisson_convergence.pdf}")
print(r"\caption{Grid convergence of the immersed boundary Poisson solver on a manufactured solution $\phi = r^4 + z^4 + r^2z^2$. The measured convergence order is $p = %.2f \pm %.2f$, confirming second-order accuracy of the cubic-exact boundary stencil.}" % (mean_order, std_order))
print(r"\label{fig:poisson-convergence}")
print(r"\end{figure}")
