# Taylor-Cone Solver Streamlit Application

Professional academic interface for the Taylor-cone electrostatic-capillary solver.

## Overview

This application provides an interactive, publication-quality interface for:
- Electrostatic field computation (Laplace/Poisson)
- Young-Laplace-Maxwell residual analysis
- Onset voltage prediction
- Immersed boundary verification
- Space-charge shielding models

## Quick Start

### Run the Application

```bash
streamlit run backend/app/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

### Legacy Application

The previous single-file app is preserved as `streamlit_app_legacy.py` and can be run with:

```bash
streamlit run backend/app/streamlit_app_legacy.py
```

## Application Structure

```
backend/app/
├── streamlit_app.py              # Main entry point with navigation
├── streamlit_app_legacy.py       # Original single-file app (preserved)
├── app_pages/                    # Multi-page application
│   ├── 01_overview.py           # Landing page with theory
│   ├── 02_solver.py             # Main solver interface
│   ├── 03_verification.py       # Immersed boundary verification
│   └── 07_documentation.py      # Theory and methods reference
├── components/                   # Reusable UI components
│   ├── parameter_panel.py       # Parameter input widgets with presets
│   ├── plot_styling.py          # Academic plot styling
│   └── theory_boxes.py          # Mathematical theory boxes
├── .streamlit/
│   └── config.toml              # Theme configuration (academic style)
├── assets/
│   └── presets/                 # JSON parameter presets
│       ├── ethanol_standard.json
│       ├── water_standard.json
│       └── formamide_standard.json
└── docs/
    └── SCIENTIST_USER_GUIDE.md  # Detailed guide for scientists and creators
```

## Features

### Professional Design
- Academic color scheme (serif fonts, blue accents)
- Generous spacing for plots (550-600px height)
- Publication-quality figure styling
- Material Symbols icons throughout
- Institutional branding

### Parameter Management
- **Presets:** Load validated configurations from literature
- **Hierarchical organization:** Geometry, Materials, Physics, Mesh, Solver Settings
- **Validation:** Real-time parameter checking with warnings
- **Documentation:** Inline tooltips and theory boxes

### Visualization
- Enhanced spacing for all plots (side-by-side with spacers)
- Academic styling (white background, professional colormaps)
- Interactive Plotly charts with zoom, pan, hover
- Export-ready figures

### Results Management
- Run history tracking in session state
- Results exported to `backend/results/`
- JSON export for programmatic analysis
- Copyable parameter summaries

### Verification Suite
- Taylor angle recovery (→ 49.29°)
- Taylor identity test (V₀*/A* ≈ 1.000)
- Grid convergence visualization
- Flank field exponent landscape

## Usage Workflows

### 1. Basic Solver Run

1. Navigate to **Solver** tab
2. Select a preset (e.g., "Ethanol (standard)")
3. Click **▶️ Run Solver**
4. Examine scalar diagnostics and field plots
5. Export results if needed

### 2. Onset Voltage Prediction

1. Set your fluid's surface tension and geometry
2. Start with Taylor angle (49.3°)
3. Run solver at guessed voltage
4. Examine RMS residual:
   - Residual ≈ 0 → voltage is near onset
   - Residual large → adjust voltage and rerun

### 3. Verification

1. Navigate to **Verification** tab
2. Select Fine or Very Fine grid
3. Click **▶️ Run Verification**
4. Check recovered angle (should be ≈49.2°)
5. Check identity ratio (should be ≈1.000)

## Parameter Reference

### Quick Defaults (Ethanol, Standard)

```python
gamma = 22 mN/m              # Surface tension
electrode_spacing = 10 mm    # Domain height
nozzle_radius = 10 mm       # Domain width
V0 = 2.5 kV                 # Applied voltage
space_charge_model = none   # Vacuum electrostatics
interface_angle = 49.3°     # Taylor angle
grid = 31 × 51              # Medium resolution
```

### Expected Runtime

- **Coarse grid (21×31):** < 0.5 seconds
- **Medium grid (31×51):** ~0.5–1 seconds
- **Fine grid (41×71):** ~1–2 seconds
- **Verification (Fine 121×177):** ~10–30 seconds

## Developer Guide

### Adding a New Preset

1. Create JSON file in `assets/presets/`:

```json
{
  "name": "My Fluid",
  "description": "Description of the configuration",
  "parameters": {
    "gamma": 0.035,
    "electrode_spacing": 0.015,
    "nozzle_radius": 0.015,
    "V0": 3000.0,
    "space_charge_model": "none",
    "interface_half_angle_deg": 49.3
  },
  "grid": {
    "nr": 31,
    "nz": 51
  },
  "reference": "Citation or source for these parameters"
}
```

2. Add to preset selector in `components/parameter_panel.py`:

```python
presets = {
    # ... existing presets ...
    "My Fluid (standard)": "my_fluid_standard",
}
```

### Adding a New Page

1. Create `app_pages/0X_pagename.py`
2. Import necessary components
3. Follow the structure of existing pages (title, sidebar params, results display)
4. Add to navigation in `streamlit_app.py`:

```python
new_page = st.Page("app_pages/0X_pagename.py", title="Page Name", icon="🔬")
pg = st.navigation([overview_page, solver_page, new_page, ...])
```

### Styling Guidelines

- Use `st.columns([10, 1, 10])` for side-by-side plots with spacing
- Apply `apply_academic_style(fig, height=550)` to all Plotly figures
- Use `st.metric(..., border=True)` for scalar diagnostics
- Add help text to all parameters
- Include theory boxes for mathematical concepts

## Scientific Documentation

See `docs/SCIENTIST_USER_GUIDE.md` for:
- What inputs scientists provide and why
- What outputs scientists look for
- Interpretation of diagnostics
- Scientific workflows
- Validation checklist for creators

## Troubleshooting

### App doesn't start
- Check that you're running from the repository root
- Verify all dependencies installed: `pip install -e .`
- Try legacy app to isolate issue: `streamlit run backend/app/streamlit_app_legacy.py`

### Import errors
- The app pages add parent directories to `sys.path` for imports
- Verify `solver/` package is in `backend/`
- Check that `app_backend.py` exists in `solver/`

### Plots not displaying
- Check that solver runs complete without exceptions
- Verify Plotly installed: `pip install plotly`
- Try clearing cache with **🗑️ Clear Cache** button

### Solver doesn't converge
- Reduce under-relaxation ω (try 0.3 or 0.2)
- Increase max iterations
- Check space-charge parameters are physical
- Use coarser grid for initial exploration

### Verification angle far from 49.29°
- Use Fine or Very Fine grid (coarse grids have ~1° error)
- Verify Taylor far-field BC is being used
- Check that domain is square (electrode_spacing ≈ nozzle_radius)

## Design Philosophy

This application follows COMSOL-inspired design principles:

1. **Professional appearance** with academic color schemes and typography
2. **Clear hierarchy** from problem setup → solve → analysis → export
3. **Self-documenting** with integrated theory and parameter tooltips
4. **Research-ready** outputs suitable for papers and presentations
5. **Educational** with guided workflows and explanatory text

## Version History

- **v2.0** (2026-08-23): Multi-page restructure with academic styling
  - Professional theme and layout
  - Enhanced plot spacing (550-600px)
  - Component-based architecture
  - Preset management
  - Comprehensive documentation

- **v1.0** (2026-08-18): Original single-page app
  - Preserved as `streamlit_app_legacy.py`
  - Basic two-tab interface (Solver, Verification)
  - Functional but minimal styling

## Citation

If you use this application in your research, please cite:

```bibtex
@article{yang2026taylor,
  title={A Lightweight Axisymmetric Electrostatic-Capillary Solver for
         Taylor-Cone Onset with Planned Experimental Validation},
  author={Yang, Ethan and Dong, Elliot and Lau, Curtis},
  journal={ISEF 2026},
  year={2026},
  institution={Independent Schools Foundation Academy, Hong Kong SAR}
}
```

## License

See repository root for license information.

## Contact

For questions about the application:
- Open an issue on GitHub
- See paper for author contact information
