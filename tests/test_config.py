from __future__ import annotations

from ax_intel.config import load_config


def test_required_config_files_are_loadable() -> None:
    companies = load_config("companies.yaml")
    sources = load_config("sources.yaml")
    scoring = load_config("scoring-rubric.yaml")
    recipients = load_config("recipients.yaml")

    assert "global_ai_leaders" in companies["tiers"]
    assert sources["policy"]["tier_c_can_be_critical_alone"] is False
    assert scoring["score_range"] == {"min": 1, "max": 5}
    assert recipients["send_policy"]["default_mode"] == "draft"
    assert len(recipients["groups"]) == 5

