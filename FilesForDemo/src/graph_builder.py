"""Compatibility wrapper for old graph-building imports.

Newer code lives under `src.data_prep` and `src.graph`. This module is kept so
older imports of `src.graph_builder` still resolve.
"""

from src.data_prep.staff_detection import IMAGE_ROOT, detect_staff_lines, save_staff_debug_image

__all__ = [
    "IMAGE_ROOT",
    "detect_staff_lines",
    "save_staff_debug_image",
]
