from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ax_intel.config import PROJECT_ROOT
from ax_intel.models import RunContext, RunMode, SlackSendResult

_ENV_LOADED = False


def _load_env_file() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    _ENV_LOADED = True
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def _env(key: str) -> Optional[str]:
    _load_env_file()
    return os.environ.get(key)


def _file_message_ts(response: object, channel_id: str) -> Optional[str]:
    if not isinstance(response, dict):
        return None
    file_payload = response.get("file")
    if not isinstance(file_payload, dict):
        return None
    shares = file_payload.get("shares")
    if not isinstance(shares, dict):
        return None
    for bucket in ("public", "private"):
        by_channel = shares.get(bucket)
        if not isinstance(by_channel, dict):
            continue
        entries = by_channel.get(channel_id)
        if isinstance(entries, list) and entries:
            ts = entries[0].get("ts")
            if isinstance(ts, str):
                return ts
    return None


def upload_slack(context: RunContext) -> SlackSendResult:
    """Post the daily brief to Slack with report.pdf as the primary attachment."""
    channel_id = _env("SLACK_CHANNEL_ID") or "C0B7AUS6J0H"
    run_date = context.run_date

    if context.dry_run or not _env("SLACK_BOT_TOKEN"):
        status = "dry_run" if context.dry_run else "blocked_missing_slack_token"
        return SlackSendResult(
            run_date=run_date,
            channel_id=channel_id,
            channel_name="dry-run" if context.dry_run else channel_id,
            status=status,
            sent_at=datetime.now(timezone.utc),
        )

    from slack_sdk import WebClient

    client = WebClient(token=_env("SLACK_BOT_TOKEN"))
    subject = f"ck-daily {run_date.isoformat()} 데일리 브리프"

    hero_image_ts: Optional[str] = None
    pdf_ts: Optional[str] = None
    message_ts: Optional[str] = None

    # 0. Ensure bot is in the channel (works for public channels)
    try:
        client.conversations_join(channel=channel_id)
    except Exception:
        pass  # Private channel — must be manually invited

    pdf_path: Path = context.output_paths["report_pdf"]
    if not pdf_path.exists():
        raise FileNotFoundError(f"Missing report PDF for Slack upload: {pdf_path}")

    # 1. Upload report.pdf with the message as the primary channel post.
    slack_message_path: Path = context.output_paths["slack_message"]
    text = slack_message_path.read_text(encoding="utf-8") if slack_message_path.exists() else subject
    resp = client.files_upload_v2(
        channel=channel_id,
        file=str(pdf_path),
        filename=f"ck-daily-{run_date.isoformat()}.pdf",
        title=f"{subject} PDF",
        initial_comment=text,
    )
    pdf_ts = resp.get("file", {}).get("id")
    message_ts = _file_message_ts(resp, channel_id)
    if not pdf_ts:
        raise RuntimeError("Slack PDF upload did not return a file id")

    # 2. Upload hero image as reply (best-effort)
    hero_path: Path = context.output_paths["hero_image"]
    if hero_path.exists() and message_ts:
        try:
            resp = client.files_upload_v2(
                channel=channel_id,
                file=str(hero_path),
                filename=hero_path.name,
                title=f"Hero Visual — {subject}",
                thread_ts=message_ts,
            )
            hero_image_ts = resp.get("file", {}).get("id")
        except Exception as exc:
            print(f"[WARN] Hero image upload skipped: {exc}", file=sys.stderr)

    return SlackSendResult(
        run_date=run_date,
        channel_id=channel_id,
        channel_name=channel_id,
        message_ts=message_ts,
        hero_image_ts=hero_image_ts,
        pdf_ts=pdf_ts,
        status="sent",
        sent_at=datetime.now(timezone.utc),
    )
