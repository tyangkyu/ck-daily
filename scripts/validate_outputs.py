#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ax_intel.io import read_json, write_json
from ax_intel.models import RunContext
from ax_intel.validation.engine import run_validation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated ck-daily outputs.")
    parser.add_argument("--run-context", type=Path, required=True, help="Path to run-context.json.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = RunContext.model_validate(read_json(args.run_context))
    result = run_validation(context)
    output_path = context.output_paths.get("validation_result", context.report_dir / "validation-result.json")
    write_json(output_path, result.model_dump(mode="json"))
    print(output_path)
    print("passed" if result.passed else "failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
