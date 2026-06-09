import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_prep.class_mapping import (
    build_class_mapping_payload,
    get_class_id,
    get_class_name,
    load_muscima_nodes,
)


class TestClassMapping(unittest.TestCase):
    def test_mapping_payload_is_deterministic_and_round_trips(self):
        nodes = load_muscima_nodes()
        payload = build_class_mapping_payload(nodes)

        self.assertEqual(payload["class_count"], len(payload["class_name_to_id"]))
        self.assertEqual(payload["class_count"], len(payload["class_id_to_name"]))
        self.assertEqual(payload["class_count"], 115)

        notehead_id = get_class_id("noteheadFull", payload)
        self.assertEqual(get_class_name(notehead_id, payload), "noteheadFull")

    def test_mapping_ids_follow_alphabetical_order(self):
        nodes = load_muscima_nodes()
        payload = build_class_mapping_payload(nodes)

        sorted_names = sorted(payload["class_name_to_id"].keys())
        rebuilt_names = [payload["class_id_to_name"][str(index)] for index in range(len(sorted_names))]

        self.assertEqual(rebuilt_names, sorted_names)


if __name__ == "__main__":
    unittest.main()
