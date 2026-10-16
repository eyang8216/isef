import sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "solver"))
sys.path.insert(0, str(ROOT / "experiments" / "methodology"))
from generate_synthetic_validation import generate_cone_profile, TEST_ANGLES, NOISE_CONFIGS
from experimental.synthetic_validation import validate_pipeline_accuracy

np.random.seed(20260922)
for a in TEST_ANGLES:
    r, z = generate_cone_profile(a)
    res = validate_pipeline_accuracy(r, z, a, needle_radius_mm=0.4, mm_per_pixel=0.02,
                                     noise_levels=[s for _, s in NOISE_CONFIGS])
    print(f"alpha={a}")
    for (lab, s), e, m in zip(NOISE_CONFIGS, res["angle_errors_deg"], res["profile_rmse_mm"]):
        print(f"   {lab:>5} (sigma={s:5.1f})  angle_err={e if not np.isnan(e) else float('nan'):8.4f}  rmse_mm={m:7.4f}")
    print("   acceptance:", res["acceptance_criteria_met"], res["failure_messages"])
