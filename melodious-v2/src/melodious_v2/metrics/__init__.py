"""Metric implementations for Melodious V2."""

from melodious_v2.metrics.classification import classification_report
from melodious_v2.metrics.detection import evaluate_detection_dataset

__all__ = ["classification_report", "evaluate_detection_dataset"]

