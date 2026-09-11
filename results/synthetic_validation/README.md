# Synthetic Validation Results

Synthetic validation tests the image processing pipeline on computer-generated
images with known ground truth before applying to real experimental data.

Run synthetic validation:
```bash
python backend/examples/13_experimental_workflow.py
```

Expected outputs:
- `synthetic_clean.png` - Clean synthetic Taylor cone image
- `synthetic_noisy.png` - Image with realistic noise added
- `validation_results.png` - Angle and profile accuracy vs noise level

Acceptance criteria (from paper Section 08):
- Angle error < 1° for SNR ≥ 40 dB
- Profile nRMSE < 2% of cone length
