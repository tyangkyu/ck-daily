from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ax_intel.io import read_json
from ax_intel.models import HeroStory, Insight


ROOT = Path(__file__).resolve().parents[1]


def run_pipeline_to_signals(tmp_path: Path) -> Path:
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


def test_generate_insights_creates_insights_and_hero_story(tmp_path: Path) -> None:
    run_context_path = run_pipeline_to_signals(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "generate_insights.py"),
            "--run-context",
            str(run_context_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    output_paths = [Path(line) for line in result.stdout.strip().splitlines()]

    insights_path = tmp_path / "2026-05-31" / "insights.json"
    hero_story_path = tmp_path / "2026-05-31" / "hero-story.json"
    assert output_paths == [insights_path, hero_story_path]

    insights = [Insight.model_validate(item) for item in read_json(insights_path)]
    hero_story = HeroStory.model_validate(read_json(hero_story_path))

    assert len(insights) == 3
    assert hero_story.signal_id in {insight.signal_id for insight in insights}
    assert hero_story.title
    assert hero_story.selection_reason
    assert hero_story.visual_message

    for insight in insights:
        assert insight.what_happened
        assert insight.why_it_matters
        assert insight.implication_for_korea
        assert insight.implication_for_lg
        assert insight.recommended_actions.immediate
        assert insight.recommended_actions.thirty_days
        assert insight.recommended_actions.ninety_days

