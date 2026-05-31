from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from ax_intel.cleaning.normalize import canonicalize_url
from ax_intel.io import read_json
from ax_intel.models import CleanItem, RawItem


ROOT = Path(__file__).resolve().parents[1]


def test_canonicalize_url_removes_tracking_and_fragment() -> None:
    canonical = canonicalize_url(
        "HTTPS://OpenAI.com/news/enterprise-agent-controls/?utm_source=x&keep=1#section"
    )

    assert canonical == "https://openai.com/news/enterprise-agent-controls?keep=1"


def test_clean_and_rank_sources_creates_clean_items_json(tmp_path: Path) -> None:
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

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "collect_sources.py"),
            "--run-context",
            str(run_context_path),
        ],
        cwd=ROOT,
        check=True,
    )

    clean_result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "clean_and_rank_sources.py"),
            "--run-context",
            str(run_context_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    clean_items_path = Path(clean_result.stdout.strip())
    raw_payload = read_json(tmp_path / "2026-05-31" / "raw-items.json")
    clean_payload = read_json(clean_items_path)
    raw_items = [RawItem.model_validate(item) for item in raw_payload]
    clean_items = [CleanItem.model_validate(item) for item in clean_payload]

    assert len(raw_items) == 4
    assert len(clean_items) == 3
    assert clean_items_path == tmp_path / "2026-05-31" / "clean-items.json"
    assert all(item.canonical_url for item in clean_items)
    assert all(item.credibility_reason for item in clean_items)
    assert all(item.related_scope == item.scope for item in clean_items)
    assert all(item.duplicate_group_id.startswith("event-") for item in clean_items)
    assert {item.needs_review for item in clean_items} == {False}


def test_clean_item_marks_tier_c_for_review() -> None:
    item = RawItem(
        id="tier-c-001",
        title="Weak signal about AI shopping",
        url="https://example.com/post?utm_campaign=test",
        source_name="Social Signal",
        source_tier="C",
        discovered_at=datetime.now(timezone.utc),
        scope=["Commerce AI"],
    )

    from ax_intel.cleaning.pipeline import raw_to_clean_item

    clean_item = raw_to_clean_item(item)

    assert clean_item.needs_review is True
    assert clean_item.source_tier == "C"
    assert str(clean_item.canonical_url) == "https://example.com/post"

