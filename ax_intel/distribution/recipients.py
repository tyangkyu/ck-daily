from __future__ import annotations

from typing import Dict, List

from ax_intel.config import load_config
from ax_intel.models import Recipient


def load_recipients() -> List[Recipient]:
    config = load_config("recipients.yaml")
    groups: Dict[str, Dict[str, str]] = config["groups"]
    max_recipients = config["send_policy"]["max_recipients"]
    recipients = [
        Recipient(group=group_key, name=group["name"], email=group["email"])
        for group_key, group in groups.items()
    ]
    if len(recipients) != max_recipients:
        raise ValueError(f"Expected exactly {max_recipients} recipients")
    return recipients


def subject_for_date(run_date, prefix: str = "[ck-daily]") -> str:
    return f"{prefix} {run_date.strftime('%Y.%m.%d')} 데일리 브리프"
