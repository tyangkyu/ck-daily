from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from ax_intel.config import load_config
from ax_intel.models import EmailDraftPreview, Recipient, RunContext, RunMode, SendResult
from ax_intel.distribution.recipients import subject_for_date


REQUIRED_EMAIL_BLOCKS = [
    "ck-daily",
    "요약",
    "Top 전략 신호",
    "핵심 권고",
]


def validate_artifacts(context: RunContext) -> None:
    html_path = context.output_paths["email_html"]
    pdf_path = context.output_paths["report_pdf"]
    if not html_path.exists():
        raise FileNotFoundError(f"Missing email HTML: {html_path}")
    if not pdf_path.exists():
        raise FileNotFoundError(f"Missing PDF attachment: {pdf_path}")
    html = html_path.read_text(encoding="utf-8")
    missing = [block for block in REQUIRED_EMAIL_BLOCKS if block not in html]
    if missing:
        raise ValueError(f"Email HTML missing required blocks: {', '.join(missing)}")


def build_draft_id(context: RunContext, recipients: List[Recipient]) -> str:
    digest = hashlib.sha256(
        f"{context.run_date.isoformat()}|{','.join(str(r.email) for r in recipients)}".encode("utf-8")
    ).hexdigest()
    return f"draft-{digest[:16]}"


def create_draft_preview(context: RunContext, recipients: List[Recipient]) -> EmailDraftPreview:
    validate_artifacts(context)
    config = load_config("recipients.yaml")
    subject = subject_for_date(context.run_date, config["send_policy"]["subject_prefix"])
    return EmailDraftPreview(
        run_date=context.run_date,
        subject=subject,
        recipients=recipients,
        html_path=context.output_paths["email_html"],
        pdf_path=context.output_paths["report_pdf"],
        draft_id=build_draft_id(context, recipients),
        status="draft_created",
        created_at=datetime.now(timezone.utc),
    )


def build_send_result(
    *,
    context: RunContext,
    recipients: List[Recipient],
    mode: RunMode,
    draft_id: str,
    approval_token: Optional[str],
) -> SendResult:
    if mode == RunMode.SEND and not approval_token:
        raise ValueError("--approval-token is required for send mode")
    if mode == RunMode.SEND_AFTER_APPROVAL and not approval_token:
        return SendResult(
            run_date=context.run_date,
            mode=mode,
            recipients=recipients,
            status="approval_pending",
            draft_id=draft_id,
        )
    if mode == RunMode.SEND:
        return SendResult(
            run_date=context.run_date,
            mode=mode,
            recipients=recipients,
            status="send_stubbed",
            draft_id=draft_id,
            message_id=f"message-{draft_id.removeprefix('draft-')}",
            sent_at=datetime.now(timezone.utc),
        )
    return SendResult(
        run_date=context.run_date,
        mode=mode,
        recipients=recipients,
        status="draft_created",
        draft_id=draft_id,
    )
