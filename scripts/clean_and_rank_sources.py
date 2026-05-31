#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ax_intel.cleaning.pipeline import clean_items
from ax_intel.io import read_json, write_json
from ax_intel.models import RawItem, RunContext


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean Phase 4 raw source items.")
    parser.add_argument("--run-context", type=Path, required=True, help="Path to run-context.json.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = RunContext.model_validate(read_json(args.run_context))
    raw_payload = read_json(context.output_paths["raw_items"])
    raw_items = [RawItem.model_validate(item) for item in raw_payload]
    cleaned = clean_items(raw_items)
    output_path = context.output_paths["clean_items"]
    write_json(output_path, [item.model_dump(mode="json") for item in cleaned])
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

