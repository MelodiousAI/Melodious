"""Write the V2 detector payload JSON Schema."""

from __future__ import annotations

import argparse

from melodious_v2.contracts import write_detector_payload_schema


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="docs/detector_payload_v2.schema.json")
    args = parser.parse_args()
    write_detector_payload_schema(args.output)
    print(args.output)


if __name__ == "__main__":
    main()

