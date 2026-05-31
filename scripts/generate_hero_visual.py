#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ax_intel.io import read_json
from ax_intel.models import HeroStory, RunContext, Signal
from ax_intel.visuals.placeholder_png import write_solid_png
from ax_intel.visuals.prompt import build_hero_prompt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Phase 7 hero visual prompt and placeholder image.")
    parser.add_argument("--run-context", type=Path, required=True, help="Path to run-context.json.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = RunContext.model_validate(read_json(args.run_context))
    hero_story = HeroStory.model_validate(read_json(context.output_paths["hero_story"]))
    signals = [
        Signal.model_validate(signal)
        for signal in read_json(context.output_paths["signals"])
    ]

    prompt = build_hero_prompt(hero_story, signals, context.run_date)
    prompt_path = context.output_paths["hero_prompt"]
    image_path = context.output_paths["hero_image"]

    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")
    write_solid_png(image_path, size=(1600, 900))

    print(prompt_path)
    print(image_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

