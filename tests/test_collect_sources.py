from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ax_intel.io import read_json
from ax_intel.models import RawItem
from ax_intel.source_clients.rss import stable_item_id


ROOT = Path(__file__).resolve().parents[1]


def test_stable_item_id_is_deterministic() -> None:
    first = stable_item_id("OpenAI Newsroom", "Title", "https://example.com/a")
    second = stable_item_id("OpenAI Newsroom", "Title", "https://example.com/a")

    assert first == second
    assert len(first) == 16


def test_collect_sources_creates_raw_items_json(tmp_path: Path) -> None:
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

    collect_result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "collect_sources.py"),
            "--run-context",
            str(run_context_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    raw_items_path = Path(collect_result.stdout.strip())
    payload = read_json(raw_items_path)
    items = [RawItem.model_validate(item) for item in payload]

    assert raw_items_path == tmp_path / "2026-05-31" / "raw-items.json"
    assert len(items) == 4
    assert {item.source_tier for item in items} == {"A", "B"}
    assert any(item.source_name == "OpenAI Newsroom Sample" for item in items)
    assert all(str(item.url).startswith("https://") for item in items)
    assert all(item.discovered_at is not None for item in items)
