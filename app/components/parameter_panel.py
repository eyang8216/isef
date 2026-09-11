"""Reusable parameter input components with validation and presets."""

import json
from pathlib import Path
from typing import Dict, Any, Optional

import streamlit as st


def load_preset(preset_name: str) -> Optional[Dict[str, Any]]:
    """Load a parameter preset from JSON file.

    Args:
        preset_name: Name of preset (without .json extension)

    Returns:
        Dictionary of preset parameters or None if not found
    """
    preset_path = Path(__file__).parent.parent / "assets" / "presets" / f"{preset_name}.json"
    if preset_path.exists():
        with open(preset_path, "r") as f:
            return json.load(f)
    return None


def preset_selector() -> Optional[Dict[str, Any]]:
    """Display preset selector and return selected preset parameters.

    Returns:
        Selected preset parameters or None if custom
    """
    presets = {
        "Custom": None,
        "Ethanol (standard)": "ethanol_standard",
        "Water (standard)": "water_standard",
        "Formamide (standard)": "formamide_standard",
    }

    selected = st.selectbox(
        "Configuration preset",
        options=list(presets.keys()),
        help="Load validated parameter sets from literature or create a custom configuration."
    )

    if selected == "Custom":
        return None

    preset_data = load_preset(presets[selected])
    if preset_data:
        with st.expander("ℹ️ Preset details", expanded=False):
            st.caption(preset_data.get("description", ""))
            if "reference" in preset_data:
                st.caption(f"**Reference:** {preset_data['reference']}")

    return preset_data


def geometry_parameters(preset: Optional[Dict] = None) -> Dict[str, float]:
    """Display geometry parameter inputs.

    Args:
        preset: Optional preset to use for default values

    Returns:
        Dictionary of geometry parameters
    """
    st.subheader("Geometry")

    defaults = preset["parameters"] if preset else {}

    electrode_spacing = st.number_input(
        "Electrode spacing [mm]",
        min_value=0.5,
        max_value=50.0,
        value=defaults.get("electrode_spacing", 0.010) * 1e3,
        step=1.0,
        format="%.1f",
        help="Distance from emitter tip to grounded counter-electrode. Sets the domain "
             "height (z_max). Typical experimental values: 10–50 mm for benchtop "
             "electrospray, 1–5 mm for microdevices."
    ) * 1e-3

    nozzle_radius = st.number_input(
        "Nozzle / domain radius [mm]",
        min_value=0.5,
        max_value=50.0,
        value=defaults.get("nozzle_radius", 0.010) * 1e3,
        step=1.0,
        format="%.1f",
        help="Radial extent of the computational domain (r_max) and initial nozzle outer "
             "radius. Should be large enough to minimize radial boundary effects. For a "
             "square domain, set equal to the electrode spacing."
    ) * 1e-3

    # Validation
    if electrode_spacing < 2 * nozzle_radius:
        st.warning(
            "⚠️ Electrode spacing should typically exceed 2× the nozzle radius for "
            "accurate far-field behavior.",
            icon="⚠️"
        )

    return {
        "electrode_spacing": electrode_spacing,
        "nozzle_radius": nozzle_radius,
    }


def material_parameters(preset: Optional[Dict] = None) -> Dict[str, float]:
    """Display material parameter inputs.

    Args:
        preset: Optional preset to use for default values

    Returns:
        Dictionary of material parameters
    """
    st.subheader("Materials")

    defaults = preset["parameters"] if preset else {}

    gamma = st.number_input(
        "Surface tension γ [mN/m]",
        min_value=15.0,
        max_value=72.0,
        value=defaults.get("gamma", 0.022) * 1e3,
        step=1.0,
        format="%.1f",
        help="Surface tension of the working fluid. Determines the capillary pressure "
             "scale γκ. Common values: Ethanol ≈ 22 mN/m, Water ≈ 72 mN/m, "
             "Formamide ≈ 58 mN/m."
    ) * 1e-3

    st.caption("📖 [Material properties reference →](#)")

    return {"gamma": gamma}


def grid_parameters(preset: Optional[Dict] = None, key_prefix: str = "") -> Dict[str, int]:
    """Display grid resolution parameters.

    Args:
        preset: Optional preset to use for default values
        key_prefix: Prefix for widget keys to avoid conflicts

    Returns:
        Dictionary with nr, nz grid dimensions
    """
    st.subheader("Mesh resolution")

    grid_res = st.select_slider(
        "Grid resolution (nr × nz)",
        options=["Coarse (21×31)", "Medium (31×51)", "Fine (41×71)", "Very Fine (61×91)"],
        value="Medium (31×51)",
        help="Finite-difference grid resolution (radial × axial). Higher resolution "
             "improves accuracy but increases computation time. Coarse: quick tests, "
             "Medium: routine work, Fine: publication quality.",
        key=f"{key_prefix}_grid"
    )

    grid_map = {
        "Coarse (21×31)": (21, 31),
        "Medium (31×51)": (31, 51),
        "Fine (41×71)": (41, 71),
        "Very Fine (61×91)": (61, 91),
    }

    nr, nz = grid_map[grid_res]

    # Computational cost estimate
    n_cells = nr * nz
    if n_cells > 3000:
        st.info(f"ℹ️ Grid has {n_cells:,} cells. Expect 1-5 seconds per solve.", icon="ℹ️")

    return {"nr": nr, "nz": nz}
