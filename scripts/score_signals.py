#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ax_intel.io import read_json, write_json
from ax_intel.models import CleanItem, RunContext
from ax_intel.scoring.ranker import score_items


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score Phase 5 strategic signals.")
    parser.add_argument("--run-context", type=Path, required=True, help="Path to run-context.json.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = RunContext.model_validate(read_json(args.run_context))
    clean_payload = read_json(context.output_paths["clean_items"])
    clean_items = [CleanItem.model_validate(item) for item in clean_payload]
    signals = score_items(clean_items)
    output_path = context.output_paths["signals"]
    write_json(output_path, [signal.model_dump(mode="json") for signal in signals])
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

