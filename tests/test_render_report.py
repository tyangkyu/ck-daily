from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

from ax_intel.io import read_json
from ax_intel.models import ReportManifest


ROOT = Path(__file__).resolve().parents[1]


def run_pipeline_to_visual(tmp_path: Path) -> Path:
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


def test_render_report_creates_markdown_html_archive_and_manifest(tmp_path: Path) -> None:
    run_context_path = run_pipeline_to_visual(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "render_report.py"),
            "--run-context",
            str(run_context_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    output_paths = [Path(line) for line in result.stdout.strip().splitlines()]

    report_path = tmp_path / "2026-05-31" / "report.md"
    docx_path = tmp_path / "2026-05-31" / "report.docx"
    pdf_path = tmp_path / "2026-05-31" / "report.pdf"
    email_path = tmp_path / "2026-05-31" / "email.html"
    archive_path = tmp_path / "2026-05-31" / "archive.md"
    manifest_path = tmp_path / "2026-05-31" / "report-manifest.json"
    assert output_paths == [report_path, docx_path, pdf_path, email_path, archive_path, manifest_path]

    report = report_path.read_text(encoding="utf-8")
    email = email_path.read_text(encoding="utf-8")
    archive = archive_path.read_text(encoding="utf-8")
    manifest = ReportManifest.model_validate(read_json(manifest_path))

    assert "1페이지: 히어로 스토리" in report
    assert "2페이지: Top 전략 신호" in report
    assert "5페이지: 실행 과제" in report
    assert "OpenAI expands enterprise agent controls" in report
    assert "<h3>Top 전략 신호</h3>" in email
    assert "핵심 권고" in email
    assert "아카이브 상태: Phase 8 skeleton에서 생성됨." in archive
    assert zipfile.is_zipfile(docx_path)
    with zipfile.ZipFile(docx_path) as archive_file:
        assert "word/document.xml" in archive_file.namelist()
        document_xml = archive_file.read("word/document.xml").decode("utf-8")
        assert "ck-daily 데일리 브리프" in document_xml
    assert pdf_path.read_bytes().startswith(b"%PDF-1.4")
    assert manifest.markdown_path == report_path
    assert manifest.docx_path == docx_path
    assert manifest.pdf_path == pdf_path
    assert manifest.html_email_path == email_path
    assert manifest.archive_path == archive_path
