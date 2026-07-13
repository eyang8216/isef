from solver.verification import run_manufactured_poisson, run_quartic_manufactured_poisson


def test_manufactured_poisson_error_is_small_and_converges():
    coarse = run_manufactured_poisson(25, 27)
    fine = run_manufactured_poisson(49, 53)
    assert coarse.linf_error < 1e-10
    assert fine.linf_error < 1e-10
    assert fine.nnz > coarse.nnz



def test_quartic_manufactured_poisson_converges_under_refinement():
    coarse = run_quartic_manufactured_poisson(25, 27)
    medium = run_quartic_manufactured_poisson(49, 53)
    fine = run_quartic_manufactured_poisson(97, 105)
    assert medium.l2_error < 0.35 * coarse.l2_error
    assert fine.l2_error < 0.35 * medium.l2_error
    assert fine.linf_error < medium.linf_error < coarse.linf_error
