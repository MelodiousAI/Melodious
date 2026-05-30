"""Classification metrics used by graph relationship evaluation."""

from __future__ import annotations


def _safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def classification_report(
    y_true: list[int],
    y_pred: list[int],
    label_names: list[str],
    no_relation_label: str = "no_relation",
) -> dict:
    """Compute per-class and positive-class graph metrics.

    The primary graph metric intentionally excludes `no_relation` so a model
    cannot look good by predicting only the dominant negative class.
    """
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length.")

    per_class = {}
    for class_id, label_name in enumerate(label_names):
        tp = sum(1 for truth, pred in zip(y_true, y_pred) if truth == class_id and pred == class_id)
        fp = sum(1 for truth, pred in zip(y_true, y_pred) if truth != class_id and pred == class_id)
        fn = sum(1 for truth, pred in zip(y_true, y_pred) if truth == class_id and pred != class_id)
        support = sum(1 for truth in y_true if truth == class_id)
        precision = _safe_div(tp, tp + fp)
        recall = _safe_div(tp, tp + fn)
        f1 = _safe_div(2 * precision * recall, precision + recall)
        per_class[label_name] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
            "tp": tp,
            "fp": fp,
            "fn": fn,
        }

    positive_f1_values = [
        metrics["f1"]
        for label_name, metrics in per_class.items()
        if label_name != no_relation_label and metrics["support"] > 0
    ]
    no_relation = per_class.get(no_relation_label)
    accuracy = _safe_div(
        sum(1 for truth, pred in zip(y_true, y_pred) if truth == pred),
        len(y_true),
    )

    return {
        "metric_version": "graph_classification_v2.0",
        "primary_metric": "positive_macro_f1",
        "positive_macro_f1": sum(positive_f1_values) / len(positive_f1_values)
        if positive_f1_values
        else 0.0,
        "accuracy": accuracy,
        "no_relation": no_relation,
        "per_class": per_class,
    }

