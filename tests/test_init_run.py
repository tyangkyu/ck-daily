from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ax_intel.io import read_json
from ax_intel.models import RunContext


ROOT = Path(__file__).resolve().parents[1]


def test_init_run_creates_run_context(tmp_path: Path) -> None:
    result = subprocess.run(
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

    output_path = Path(result.stdout.strip())
    assert output_path == tmp_path / "2026-05-31" / "run-context.json"
    payload = read_json(output_path)
    context = RunContext.model_validate(payload)

    assert context.run_date.isoformat() == "2026-05-31"
    assert context.timezone == "Asia/Seoul"
    assert context.dry_run is True
    assert context.collection_window_hours == 72
    assert "OpenAI" in context.companies
    assert "LG전자" in context.companies
    assert context.output_paths["raw_items"].name == "raw-items.json"

