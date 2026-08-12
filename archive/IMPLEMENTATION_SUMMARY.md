# Implementation Summary - What Remains from Specs

## Overview

All three spec files have been analyzed:
- ✅ V1 Spec (`.scratch/taylor-cone-solver-v1/spec.md`): **COMPLETE**
- ✅ V2 Spec (`.scratch/taylor-cone-solver-v2/spec.md`): **COMPLETE**
- ⚠️ V3 Spec (`.scratch/taylor-cone-fd-bcs/spec.md`): **70% IMPLEMENTED**

## What's Already Done (V3)

### ✅ Core Implementation Complete
- `ImplicitCone` geometry with rounded cap
- `solver/immersed.py` with fractional-distance stencils
- One-sided normal field reconstruction
- Candidate-dependent optimizer mode
- `examples/07_immersed_free_boundary.py`
- Tests: `test_immersed.py`, `test_implicit_cone.py`
- 51 tests passing (up from 34)

### ✅ Files Modified
- `solver/geometry.py` - Added ImplicitCone
- `solver/electrostatics.py` - Added immersed mode
- `solver/optimization.py` - Added immersed_mode flag
- `solver/residual.py` - Added flank-only sampling
- `solver/space_charge.py` - Gas-only charge, final solve
- `solver/interface.py` - Flank-aware angle extraction

## What Remains from V3 Spec

### 1. Convergence Verification (HIGH PRIORITY)

**User Story 9**: "I want a manufactured-solution test using the exact Taylor potential φ = A·ρ^½·P_{1/2}(cosθ) as the outer Dirichlet condition with the sharp cone as the equipotential, asserting observed convergence order ≥ 1.8 under refinement"

**Status**: DONE (2026-08-09, commit `ebea0b8`) - `test_smooth_immersed_manufactured_solution_second_order_convergence` runs three refinement levels of the smooth circular manufactured test, computes observed order via Richardson, and asserts each level ≥ 1.8 (measured ≈ 2.0). Note: per the spec's 2026-08-06 note, the formal order test uses the smooth irregular boundary, not the Taylor potential + sharp cone.

**Implementation**:
```python
# In tests/test_immersed.py, enhance the convergence test:
def test_smooth_immersed_manufactured_solution_convergence_order():
    """Verify second-order convergence with Richardson extrapolation."""
    # Compute on 3+ grid levels
    # Calculate observed order: log(e1/e2) / log(h1/h2)
    # Assert order ≥ 1.8
```

### 2. Taylor Angle Recovery (HIGH PRIORITY)

**User Story 10**: "I want the optimizer demo to recover a half-angle within ±0.5° of 49.29° at the finest testable grid with a documented refinement trend"

**Status**: Currently recovers ~47.5° on example grid, needs:
- [ ] Refinement study showing trend toward 49.29°
- [ ] Documentation of grid/domain/cap-radius extrapolation
- [ ] Either achieve ±0.5° OR document why finite rounded case differs

**Implementation**:
```python
# Add to examples/07_immersed_free_boundary.py:
# Run on multiple grids (coarse → fine)
# Print refinement table
# Document extrapolation to ideal limit
```

### 3. Small-Cut Conditioning (MEDIUM PRIORITY)

**Status**: DONE (2026-08-09, commit `8e2a2c8`) - tiny positive cuts (0, min_fraction] are pinned to the boundary value via the identity-row fallback instead of raising; example 07 now runs with 0 candidate failures. Degenerate zero/non-crossing fractions still raise. See `test_tiny_cut_falls_back_to_dirichlet_row`.

**Remaining**: the optimizer's well-posedness (flat-in-angle, monotone-in-radius objective) - see `docs/plans/2026-08-09-next-steps.md` S1 and `examples/08_immersed_refinement_study.py`.

**Implementation**: Enhance `solver/immersed.py` to handle edge cases more robustly.

### 4. Interface Convergence Study (MEDIUM PRIORITY)

**From IMPLEMENTATION_STATUS.md**: "Convergence of interface-normal field, Maxwell pressure, residual, or angle" not yet proven

**Needed**:
- [ ] Grid convergence study for E_n at interface
- [ ] Grid convergence study for residual
- [ ] Grid convergence study for recovered angle

### 5. Physical Free-Boundary Constraints (LOWER PRIORITY - Future Work)

**From spec**: "A unique physical free-boundary solution with volume/contact-line constraints"

This is more research than implementation - deferrable to V4.

## Recommended Implementation Order

1. **Fix git lock issue** (prevents commits)
   ```bash
   # You may need to manually run:
   cd /Users/a3015110/Desktop/isef
   rm -f .git/index.lock .git/objects/maintenance.lock
   ```

2. **Enhance convergence test** (test_immersed.py)
   - Add Richardson extrapolation
   - Calculate observed order
   - Assert ≥ 1.8

3. **Refinement study** (examples/07_immersed_free_boundary.py)
   - Run on [coarse, medium, fine, finest] grids
   - Print table: h, angle, |angle - 49.29°|
   - Document trend

4. **Small-cut robustness** (solver/immersed.py)
   - Better handling of pathological cases
   - Document limits

5. **Update docs** (IMPLEMENTATION_STATUS.md, ADR-0003)
   - Mark verified items as complete
   - Update status from "partially implemented"

## Files That Need Changes

### To Complete V3 Spec Verification:

1. **tests/test_immersed.py** - Enhance convergence test
2. **examples/07_immersed_free_boundary.py** - Add refinement study
3. **solver/immersed.py** - Improve small-cut handling (optional)
4. **IMPLEMENTATION_STATUS.md** - Update status
5. **docs/adr/0003-merged-free-boundary-immersed-cone.md** - Update status

## Current Git Status

Branch: `feat/immersed-free-boundary`

Modified files (uncommitted):
- .scratch/taylor-cone-fd-bcs/spec.md
- IMPLEMENTATION_STATUS.md
- docs/adr/0003-merged-free-boundary-immersed-cone.md
- solver/*.py (multiple)
- tests/*.py (multiple)

New files (untracked):
- docs/plans/
- examples/07_immersed_free_boundary.py
- solver/immersed.py
- tests/test_immersed.py
- tests/test_implicit_cone.py

**Issue**: Git lock files preventing operations
- .git/index.lock
- .git/objects/maintenance.lock

## Next Steps

1. Fix git locks manually
2. Commit current work
3. Pull from main (has app improvements from 2 days ago)
4. Implement remaining verification items
5. Push everything

## Estimated Effort

- Convergence verification: 2-3 hours
- Refinement study: 1-2 hours
- Documentation updates: 1 hour
- Small-cut improvements: 2-4 hours (optional)

**Total**: ~6 hours core work, ~10 hours with optional improvements
