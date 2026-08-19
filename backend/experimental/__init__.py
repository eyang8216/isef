"""Experimental validation infrastructure for Taylor-cone solver.

This module provides tools for comparing simulation predictions with experimental
measurements of Taylor-cone geometry, onset voltage, and interface profiles.

Submodules:
    image_processing: Edge detection, calibration, contour extraction
    profile_extraction: Coordinate transformation, angle measurement
    comparison: Profile alignment, RMSE computation, statistical validation
    synthetic_validation: Generate and validate pipeline on synthetic images
    preregistration: Freeze predictions before viewing experimental data
    metadata: Trial metadata management and JSON schemas
"""

__all__ = [
    "image_processing",
    "profile_extraction",
    "comparison",
    "synthetic_validation",
    "preregistration",
    "metadata",
]
