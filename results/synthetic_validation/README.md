# Synthetic Validation Results

Synthetic validation tests the image-processing and extraction pipeline on
computer-generated silhouettes with known ground truth.

Run it:
```bash
PYTHONPATH=solver python solver/examples/13_experimental_workflow.py
```

Outputs written here:
- `synthetic_clean.png` — clean synthetic Taylor-cone image
- `synthetic_noisy.png` — the same image with realistic noise added
- `validation_results.png` — angle and profile accuracy versus noise level

Acceptance criteria, asserted over the two lowest noise levels (nominal
SNR ≥ 30 dB) and defined in `solver/experimental/synthetic_validation.py`:
- half-angle error < 1°
- profile nRMSE < 2% of cone length

The paper's synthetic round trip (Section 6.5) is a separate run of the same
pipeline via `experiments/methodology/generate_synthetic_validation.py`, which
writes `paper/paper_submission/data/synthetic_validation_results.txt`.
