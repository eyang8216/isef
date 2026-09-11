# Stage B reproducibility baseline
Date: 2026-09-08

## Environment
Python 3.10.12 was available. The project declares Python >=3.11. Initial environment lacked pytest and scipy; after installation, test collection lacked plotly. After installing plotly, the explicit command below completed successfully.

## Command and outcome
```bash
PYTHONPATH=solver python3 -m pytest solver/tests -q
```
Outcome: 74 tests passed (`........................................................................ [ 97%] .. [100%]`).

This is a local successful run under Python 3.10.12 after installing missing dependencies; it is not yet a clean Python >=3.11 environment reproduction.

## Configuration issue
`pyproject.toml` declares `package-dir = {"": "backend"}`, `packages = ["solver"]`, `testpaths = ["backend/tests"]`, and `pythonpath = ["backend"]`, but active package/tests are under `solver/`. The test command above works by explicitly setting `PYTHONPATH=solver`, bypassing the declared project configuration. This configuration must be repaired in Stage B before calling the project reproducible.

The dependency declaration also omits direct runtime requirements used by active modules/tests, notably Plotly for `solver/app_backend.py` and Pillow/OpenCV/SciPy for experimental imaging modules. Optional dependency groups are not sufficient if tests import those modules under the advertised default test command.

## Failure classification
1. Setup failure: missing pytest/scipy in the starting environment.
2. Collection/setup failure: missing plotly after installing only pytest/scipy.
3. Configuration defect: package/test paths point to `backend` while active code is under `solver`.
4. No test failures were observed after adding the missing runtime dependency and using explicit `PYTHONPATH`.

## Interpretation
The result supports: “74 tests pass in the current environment under the explicit solver path after required dependencies are installed.” It does not support: “the declared package configuration works,” “a clean Python >=3.11 install passes,” or “the numerical model is experimentally validated.”
