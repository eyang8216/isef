"""Image processing pipeline for Taylor-cone experimental validation.

This module implements the computer-vision pipeline described in Section 08 of the paper.
It converts raw experimental images into quantitative interface coordinates.

Functions:
    select_stable_frames: Identify stable frame sequences from video
    calibrate_pixels_to_mm: Convert pixel measurements to physical units
    preprocess_image: Crop, normalize, and denoise raw images
    detect_edges_canny: Canny edge detection with hysteresis thresholding
    detect_edges_otsu: Otsu thresholding + contour extraction
    detect_edges_sobel: Sobel gradient magnitude + non-maximum suppression
    extract_contour: Find interface boundary from edge-detected image
    smooth_contour: Apply low-pass filter to reduce pixel-level noise
"""

from __future__ import annotations

import numpy as np
from typing import Literal, Tuple, Optional
import warnings

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    warnings.warn("OpenCV not available. Install with: pip install opencv-python")

try:
    from scipy.signal import savgol_filter
    from scipy.interpolate import UnivariateSpline
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    warnings.warn("SciPy not available. Install with: pip install scipy")


def select_stable_frames(
    video_frames: np.ndarray,
    timestamps: np.ndarray,
    voltage_segments: list[tuple[float, float]],
    stability_tolerance: float = 0.05,
    n_frames_per_segment: int = 10,
) -> dict[int, list[int]]:
    """Identify stable frame sequences from voltage-ramp video.

    For each voltage segment, compute shape metric time series and find the
    longest contiguous interval where metrics remain within tolerance bands.

    Parameters
    ----------
    video_frames : np.ndarray
        Video frames array, shape (n_frames, height, width) or (n_frames, height, width, channels)
    timestamps : np.ndarray
        Timestamp for each frame in seconds, shape (n_frames,)
    voltage_segments : list of (t_start, t_end) tuples
        Time intervals corresponding to each voltage step
    stability_tolerance : float
        Fractional tolerance for shape metric stability (default 5%)
    n_frames_per_segment : int
        Number of representative frames to select per segment

    Returns
    -------
    dict[int, list[int]]
        Mapping from segment index to list of selected frame indices.
        Empty list if no stable interval found in that segment.

    Notes
    -----
    Shape metric used: centroid z-position (simple proxy for apex stability).
    For production use, could extend to curvature, area, or multiple metrics.
    """
    selected_frames = {}

    for seg_idx, (t_start, t_end) in enumerate(voltage_segments):
        # Find frames in this segment
        mask = (timestamps >= t_start) & (timestamps <= t_end)
        seg_frame_indices = np.where(mask)[0]

        if len(seg_frame_indices) < n_frames_per_segment:
            selected_frames[seg_idx] = []
            continue

        # Compute shape metric: centroid z-position (simple stability proxy)
        seg_frames = video_frames[seg_frame_indices]
        centroids = np.array([_compute_centroid(frame) for frame in seg_frames])

        # Find longest stable interval
        mean_centroid = np.mean(centroids)
        tolerance_band = stability_tolerance * abs(mean_centroid) if mean_centroid != 0 else stability_tolerance

        stable_mask = np.abs(centroids - mean_centroid) <= tolerance_band
        stable_intervals = _find_longest_true_interval(stable_mask)

        if stable_intervals is None or len(stable_intervals) < n_frames_per_segment:
            selected_frames[seg_idx] = []
            continue

        # Select n_frames uniformly from the stable interval
        stable_start, stable_end = stable_intervals
        stable_indices = seg_frame_indices[stable_start:stable_end+1]
        selected = np.linspace(0, len(stable_indices)-1, n_frames_per_segment, dtype=int)
        selected_frames[seg_idx] = stable_indices[selected].tolist()

    return selected_frames


def _compute_centroid(frame: np.ndarray) -> float:
    """Compute vertical centroid of thresholded image (simple shape metric)."""
    if frame.ndim == 3:
        frame = np.mean(frame, axis=2)  # Convert to grayscale

    # Simple Otsu-like threshold at median
    threshold = np.median(frame)
    binary = frame < threshold  # Assume liquid is dark

    if not np.any(binary):
        return 0.0

    y_coords, x_coords = np.where(binary)
    return float(np.mean(y_coords))


def _find_longest_true_interval(mask: np.ndarray) -> Optional[Tuple[int, int]]:
    """Find the longest contiguous True interval in a boolean array."""
    if not np.any(mask):
        return None

    # Find start and end of True runs
    padded = np.concatenate(([False], mask, [False]))
    diff = np.diff(padded.astype(int))
    starts = np.where(diff == 1)[0]
    ends = np.where(diff == -1)[0] - 1

    lengths = ends - starts + 1
    longest_idx = np.argmax(lengths)

    return (int(starts[longest_idx]), int(ends[longest_idx]))


def calibrate_pixels_to_mm(
    image: np.ndarray,
    method: Literal["target", "needle_diameter"],
    known_distance_mm: Optional[float] = None,
    needle_diameter_mm: Optional[float] = None,
) -> float:
    """Convert pixel measurements to millimeters.

    Parameters
    ----------
    image : np.ndarray
        Calibration image containing reference feature
    method : {"target", "needle_diameter"}
        Calibration method to use
    known_distance_mm : float, optional
        Known physical distance on calibration target (mm), required if method="target"
    needle_diameter_mm : float, optional
        Known needle outer diameter (mm), required if method="needle_diameter"

    Returns
    -------
    float
        Calibration scale in mm/pixel

    Raises
    ------
    ValueError
        If required parameter not provided for selected method
    NotImplementedError
        If OpenCV not available

    Notes
    -----
    Method "target" uses edge detection on a precision scale.
    Method "needle_diameter" fits parallel lines to needle sidewalls.
    """
    if not HAS_OPENCV:
        raise NotImplementedError("OpenCV required for calibration. Install opencv-python.")

    if method == "target":
        if known_distance_mm is None:
            raise ValueError("known_distance_mm required for target method")
        # Simplified: detect two prominent edges, measure pixel distance
        # Production would use checkerboard corners or scale markers
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        edges = cv2.Canny(gray, 50, 150)

        # Find two strongest horizontal edge runs (simplified heuristic)
        edge_rows = np.sum(edges, axis=1)
        peaks = np.argsort(edge_rows)[-2:]
        distance_pixels = float(np.abs(peaks[1] - peaks[0]))

        return known_distance_mm / distance_pixels

    elif method == "needle_diameter":
        if needle_diameter_mm is None:
            raise ValueError("needle_diameter_mm required for needle_diameter method")

        # Fit parallel lines to needle sidewalls
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        edges = cv2.Canny(gray, 50, 150)

        # Find two strongest vertical edge columns (simplified)
        edge_cols = np.sum(edges, axis=0)
        peaks = np.argsort(edge_cols)[-2:]
        distance_pixels = float(np.abs(peaks[1] - peaks[0]))

        return needle_diameter_mm / distance_pixels

    else:
        raise ValueError(f"Unknown calibration method: {method}")


def preprocess_image(
    image: np.ndarray,
    roi: Optional[Tuple[int, int, int, int]] = None,
    normalize: bool = True,
    gaussian_sigma: float = 0.0,
) -> np.ndarray:
    """Preprocess raw image for edge detection.

    Parameters
    ----------
    image : np.ndarray
        Raw grayscale or color image
    roi : tuple of (x, y, width, height), optional
        Region of interest to crop. If None, use full image.
    normalize : bool
        Apply histogram equalization to maximize dynamic range
    gaussian_sigma : float
        Gaussian blur sigma in pixels. If 0, no blur applied.

    Returns
    -------
    np.ndarray
        Preprocessed grayscale image, dtype uint8
    """
    if not HAS_OPENCV:
        raise NotImplementedError("OpenCV required for preprocessing. Install opencv-python.")

    # Convert to grayscale if needed
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Crop ROI
    if roi is not None:
        x, y, w, h = roi
        gray = gray[y:y+h, x:x+w]

    # Normalize intensity
    if normalize:
        gray = cv2.equalizeHist(gray)

    # Gaussian blur
    if gaussian_sigma > 0:
        ksize = int(2 * np.ceil(3 * gaussian_sigma) + 1)  # Cover 3σ on each side
        gray = cv2.GaussianBlur(gray, (ksize, ksize), gaussian_sigma)

    return gray


def detect_edges_canny(
    image: np.ndarray,
    low_threshold: int = 50,
    high_threshold: int = 150,
) -> np.ndarray:
    """Canny edge detection with hysteresis thresholding.

    Parameters
    ----------
    image : np.ndarray
        Preprocessed grayscale image (uint8)
    low_threshold : int
        Lower hysteresis threshold (default 50)
    high_threshold : int
        Upper hysteresis threshold (default 150)

    Returns
    -------
    np.ndarray
        Binary edge map, dtype uint8 (0 or 255)
    """
    if not HAS_OPENCV:
        raise NotImplementedError("OpenCV required. Install opencv-python.")

    return cv2.Canny(image, low_threshold, high_threshold)


def detect_edges_otsu(image: np.ndarray) -> np.ndarray:
    """Otsu thresholding followed by contour extraction.

    Parameters
    ----------
    image : np.ndarray
        Preprocessed grayscale image (uint8)

    Returns
    -------
    np.ndarray
        Binary edge map, dtype uint8 (0 or 255)
    """
    if not HAS_OPENCV:
        raise NotImplementedError("OpenCV required. Install opencv-python.")

    # Otsu automatic threshold
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Extract contours and draw as edges
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    edge_map = np.zeros_like(image)
    cv2.drawContours(edge_map, contours, -1, 255, 1)

    return edge_map


def detect_edges_sobel(
    image: np.ndarray,
    threshold: int = 50,
) -> np.ndarray:
    """Sobel gradient magnitude with thresholding.

    Parameters
    ----------
    image : np.ndarray
        Preprocessed grayscale image (uint8)
    threshold : int
        Gradient magnitude threshold

    Returns
    -------
    np.ndarray
        Binary edge map, dtype uint8 (0 or 255)
    """
    if not HAS_OPENCV:
        raise NotImplementedError("OpenCV required. Install opencv-python.")

    # Sobel gradients
    grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)

    # Magnitude
    magnitude = np.sqrt(grad_x**2 + grad_y**2)
    magnitude = np.uint8(255 * magnitude / np.max(magnitude))

    # Threshold
    _, edges = cv2.threshold(magnitude, threshold, 255, cv2.THRESH_BINARY)

    return edges


def extract_contour(
    edge_map: np.ndarray,
    needle_tip_approx: Optional[Tuple[int, int]] = None,
    min_length: int = 50,
) -> np.ndarray:
    """Extract the Taylor-cone interface contour from edge-detected image.

    Parameters
    ----------
    edge_map : np.ndarray
        Binary edge map from edge detection
    needle_tip_approx : tuple of (x, y), optional
        Approximate needle tip location in pixels. If provided, selects
        contour originating near this point.
    min_length : int
        Minimum contour length (number of points) to consider

    Returns
    -------
    np.ndarray
        Contour coordinates, shape (n_points, 2) where each row is (x, y) in pixels

    Notes
    -----
    Selects the longest contour that originates near the needle tip,
    extends into the gap region, and has monotonic axial coordinate.
    """
    if not HAS_OPENCV:
        raise NotImplementedError("OpenCV required. Install opencv-python.")

    contours, _ = cv2.findContours(edge_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if len(contours) == 0:
        raise ValueError("No contours found in edge map")

    # Filter by length
    contours = [c for c in contours if len(c) >= min_length]

    if len(contours) == 0:
        raise ValueError(f"No contours with length >= {min_length}")

    # If needle tip provided, select contour closest to it
    if needle_tip_approx is not None:
        tip_x, tip_y = needle_tip_approx
        distances = [np.min(np.linalg.norm(c.reshape(-1, 2) - [tip_x, tip_y], axis=1)) for c in contours]
        selected = contours[np.argmin(distances)]
    else:
        # Select longest contour
        selected = max(contours, key=len)

    # Reshape from (n, 1, 2) to (n, 2)
    return selected.reshape(-1, 2)


def smooth_contour(
    contour: np.ndarray,
    method: Literal["savgol", "spline", "none"] = "savgol",
    window_length: int = 11,
    polyorder: int = 3,
    spline_smooth: float = 0.5,
) -> np.ndarray:
    """Apply low-pass filter to reduce pixel-level noise in contour.

    Parameters
    ----------
    contour : np.ndarray
        Raw contour coordinates, shape (n_points, 2)
    method : {"savgol", "spline", "none"}
        Smoothing method
    window_length : int
        Savitzky-Golay filter window length (must be odd)
    polyorder : int
        Savitzky-Golay polynomial order
    spline_smooth : float
        Spline smoothing parameter (0 = interpolation, >0 = smoothing)

    Returns
    -------
    np.ndarray
        Smoothed contour, same shape as input

    Notes
    -----
    Savitzky-Golay preserves local shape features better than simple moving average.
    Spline smoothing is more flexible but adds a tuning parameter.
    """
    if method == "none":
        return contour

    if not HAS_SCIPY:
        raise NotImplementedError("SciPy required for smoothing. Install scipy.")

    if method == "savgol":
        if window_length % 2 == 0:
            window_length += 1  # Must be odd

        x_smooth = savgol_filter(contour[:, 0], window_length, polyorder)
        y_smooth = savgol_filter(contour[:, 1], window_length, polyorder)

        return np.column_stack([x_smooth, y_smooth])

    elif method == "spline":
        # Parametric spline along arclength
        t = np.arange(len(contour))

        spline_x = UnivariateSpline(t, contour[:, 0], s=spline_smooth * len(contour))
        spline_y = UnivariateSpline(t, contour[:, 1], s=spline_smooth * len(contour))

        x_smooth = spline_x(t)
        y_smooth = spline_y(t)

        return np.column_stack([x_smooth, y_smooth])

    else:
        raise ValueError(f"Unknown smoothing method: {method}")
