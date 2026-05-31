from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_pipeline_to_hero_story(tmp_path: Path) -> Path:
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


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def test_generate_hero_visual_creates_prompt_and_placeholder_png(tmp_path: Path) -> None:
    run_context_path = run_pipeline_to_hero_story(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "generate_hero_visual.py"),
            "--run-context",
            str(run_context_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    output_paths = [Path(line) for line in result.stdout.strip().splitlines()]

    prompt_path = tmp_path / "2026-05-31" / "hero-prompt.md"
    image_path = tmp_path / "2026-05-31" / "hero-image.png"
    assert output_paths == [prompt_path, image_path]

    prompt = prompt_path.read_text(encoding="utf-8")
    assert "[뉴스레터체]" in prompt
    assert "상단 중앙에 강한 헤드라인" in prompt
    assert "ck-daily | 2026.05.31" in prompt
    assert "OpenAI expands enterprise agent controls" in prompt

    assert png_size(image_path) == (1600, 900)
