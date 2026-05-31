#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ax_intel.distribution.gmail_draft import build_send_result, create_draft_preview
from ax_intel.distribution.recipients import load_recipients
from ax_intel.io import read_json, write_json
from ax_intel.models import RunContext, RunMode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create Phase 9 Gmail draft skeleton outputs.")
    parser.add_argument("--run-context", type=Path, required=True, help="Path to run-context.json.")
    parser.add_argument("--mode", choices=[mode.value for mode in RunMode], default=RunMode.DRAFT.value)
    parser.add_argument("--approval-token", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = RunContext.model_validate(read_json(args.run_context))
    mode = RunMode(args.mode)
    recipients = load_recipients()
    preview = create_draft_preview(context, recipients)
    send_result = build_send_result(
        context=context,
        recipients=recipients,
        mode=mode,
        draft_id=preview.draft_id,
        approval_token=args.approval_token,
    )

    write_json(context.output_paths["email_draft_preview"], preview.model_dump(mode="json"))
    write_json(context.output_paths["email_send_result"], send_result.model_dump(mode="json"))
    print(context.output_paths["email_draft_preview"])
    print(context.output_paths["email_send_result"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
