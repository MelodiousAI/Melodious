"""Shared detector-contract mappings reused across export paths."""

from __future__ import annotations


MUSCIMA_TO_SHARED_DETECTION_CLASS = {
    "noteheadFull": (0, "notehead-full"),
    "noteheadHalf": (1, "notehead-half"),
    "noteheadWhole": (2, "notehead-whole"),
    "gClef": (3, "clefG"),
    "fClef": (4, "clefF"),
    "cClef": (5, "clefC"),
    "rest8th": (6, "rest-8th"),
    "restQuarter": (7, "rest-quarter"),
    "restHalf": (8, "rest-half"),
    "restWhole": (9, "rest-whole"),
    "accidentalSharp": (10, "accidentalSharp"),
    "accidentalFlat": (11, "accidentalFlat"),
    "accidentalNatural": (12, "accidentalNatural"),
    "beam": (13, "beam"),
    "stem": (14, "stem"),
}

SHARED_DETECTION_CLASS_NAMES = {
    detector_class_name for _, detector_class_name in MUSCIMA_TO_SHARED_DETECTION_CLASS.values()
}
