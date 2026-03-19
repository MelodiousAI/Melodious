"""Compatibility wrapper for graph-building imports.

The staff detector now lives in `staff_detection.py` so graph-building code can
stay separate from image-processing code.
"""

from staff_detection import IMAGE_ROOT, detect_staff_lines, save_staff_debug_image

__all__ = [
    "IMAGE_ROOT",
    "detect_staff_lines",
    "save_staff_debug_image",
]
