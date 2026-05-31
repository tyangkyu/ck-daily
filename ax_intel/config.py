from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"
REPORTS_DIR = PROJECT_ROOT / "Reports"


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


def load_config(name: str) -> Dict[str, Any]:
    return load_yaml(CONFIG_DIR / name)

