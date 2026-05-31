from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ax_intel.io import read_json
from ax_intel.models import EmailDraftPreview, SendResult


ROOT = Path(__file__).resolve().parents[1]


def run_pipeline_to_report(tmp_path: Path) -> Path:
    init_result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "init_run.py"),
            "--date",
            "2026-05-31",
            "--dry-run",
            "--reports-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    run_context_path = Path(init_result.stdout.strip())

    for script_name in [
        "collect_sources.py",
        "clean_and_rank_sources.py",
        "score_signals.py",
        "generate_insights.py",
        "generate_hero_visual.py",
        "render_report.py",
    ]:
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / script_name),
                "--run-context",
                str(run_context_path),
            ],
            cwd=ROOT,
            check=True,
        )

    return run_context_path


def test_send_gmail_creates_draft_preview_and_send_result(tmp_path: Path) -> None:
    run_context_path = run_pipeline_to_report(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "send_gmail.py"),
            "--run-context",
            str(run_context_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    output_paths = [Path(line) for line in result.stdout.strip().splitlines()]

    preview_path = tmp_path / "2026-05-31" / "email-draft-preview.json"
    send_result_path = tmp_path / "2026-05-31" / "email-send-result.json"
    assert output_paths == [preview_path, send_result_path]

    preview = EmailDraftPreview.model_validate(read_json(preview_path))
    send_result = SendResult.model_validate(read_json(send_result_path))

    assert preview.subject == "[ck-daily] 2026.05.31 데일리 브리프"
    assert preview.status == "draft_created"
    assert preview.draft_id.startswith("draft-")
    assert len(preview.recipients) == 5
    assert preview.html_path.name == "email.html"
    assert preview.pdf_path.name == "report.pdf"
    assert send_result.status == "draft_created"
    assert send_result.draft_id == preview.draft_id
    assert send_result.message_id is None


def test_send_mode_requires_approval_token(tmp_path: Path) -> None:
    run_context_path = run_pipeline_to_report(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "send_gmail.py"),
            "--run-context",
            str(run_context_path),
            "--mode",
            "send",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "--approval-token is required for send mode" in result.stderr
