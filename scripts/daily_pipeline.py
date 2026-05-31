#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ax_intel.config import REPORTS_DIR
from ax_intel.models import RunMode
from ax_intel.pipeline.orchestrator import run_pipeline
from scripts.init_run import build_run_context


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the ck-daily pipeline.")
    parser.add_argument("--date", dest="run_date", required=True, help="Run date in YYYY-MM-DD format.")
    parser.add_argument("--mode", choices=[mode.value for mode in RunMode], default=RunMode.DRAFT.value)
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--reports-dir", type=Path, default=REPORTS_DIR)
    parser.add_argument("--approval-token", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mode = RunMode(args.mode)
    context = build_run_context(
        run_date=date.fromisoformat(args.run_date),
        mode=mode,
        dry_run=args.dry_run,
        reports_dir=args.reports_dir,
    )
    run_log = run_pipeline(
        context=context,
        mode=mode,
        approval_token=args.approval_token,
    )
    print(context.output_paths["run_log"])
    print(run_log.status)
    return 0 if run_log.status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
