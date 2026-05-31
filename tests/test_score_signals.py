from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ax_intel.io import read_json
from ax_intel.models import Signal
from ax_intel.scoring.rubric import priority_for_total


ROOT = Path(__file__).resolve().parents[1]


def test_priority_for_total_thresholds() -> None:
    assert priority_for_total(25) == "Critical Signal"
    assert priority_for_total(20) == "High Priority"
    assert priority_for_total(15) == "Monitor"
    assert priority_for_total(14) == "Low Priority"


def test_score_signals_creates_sorted_signals_json(tmp_path: Path) -> None:
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
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "clean_and_rank_sources.py"),
            "--run-context",
            str(run_context_path),
        ],
        cwd=ROOT,
        check=True,
    )

    score_result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "score_signals.py"),
            "--run-context",
            str(run_context_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    signals_path = Path(score_result.stdout.strip())
    payload = read_json(signals_path)
    signals = [Signal.model_validate(item) for item in payload]
    totals = [signal.total_score for signal in signals]

    assert signals_path == tmp_path / "2026-05-31" / "signals.json"
    assert len(signals) == 3
    assert totals == sorted(totals, reverse=True)
    assert all(signal.total_score == signal.scores.total for signal in signals)
    assert all(signal.rationale for signal in signals)
    assert {signal.priority for signal in signals}.issubset(
        {"Critical Signal", "High Priority", "Monitor", "Low Priority"}
    )

