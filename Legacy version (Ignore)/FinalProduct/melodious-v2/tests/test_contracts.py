import unittest

from pydantic import ValidationError

from melodious_v2.contracts import (
    DetectionV2,
    DetectorPayloadV2,
    ImageSize,
    NormalizedBBox,
)
from melodious_v2.taxonomies import DEEPSCORES_136_CLASS_NAMES, validate_taxonomies


class ContractTests(unittest.TestCase):
    def test_taxonomy_has_136_classes(self):
        validate_taxonomies()
        self.assertEqual(len(DEEPSCORES_136_CLASS_NAMES), 136)

    def test_payload_accepts_valid_full_taxonomy_detection(self):
        detection = DetectionV2(
            class_id=24,
            class_name="noteheadBlackOnLine",
            confidence=0.92,
            bbox=NormalizedBBox(x_center=0.5, y_center=0.5, width=0.1, height=0.1),
        )
        payload = DetectorPayloadV2(
            run_id="run_001",
            model_id="unit-test",
            taxonomy_id="deepscores_136",
            image_size=ImageSize(width=1000, height=800),
            detections=[detection],
        )
        self.assertEqual(payload.schema_version, "2.0")
        self.assertEqual(payload.detections[0].semantic_group, "notehead")

    def test_payload_rejects_wrong_class_id(self):
        with self.assertRaises(ValidationError):
            DetectionV2(
                class_id=0,
                class_name="noteheadBlackOnLine",
                confidence=0.92,
                bbox=NormalizedBBox(x_center=0.5, y_center=0.5, width=0.1, height=0.1),
            )


if __name__ == "__main__":
    unittest.main()

