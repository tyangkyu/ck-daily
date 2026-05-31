from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from ax_intel.models import (
    CleanItem,
    RawItem,
    Recipient,
    ScoreSet,
    SendResult,
    Signal,
)


def test_raw_item_contract_accepts_required_source_fields() -> None:
    item = RawItem(
        id="openai-001",
        title="OpenAI launches enterprise agent update",
        url="https://openai.com/news/example",
        source_name="OpenAI Newsroom",
        source_tier="A",
        discovered_at=datetime.now(timezone.utc),
        companies=["OpenAI"],
        scope=["Agentic AI", "Enterprise Adoption"],
        summary_raw="Official release note excerpt.",
    )

    assert item.source_tier == "A"
    assert str(item.url).startswith("https://openai.com")


def test_clean_item_requires_credibility_reason() -> None:
    with pytest.raises(ValidationError):
        CleanItem(
            id="openai-001",
            title="OpenAI launches enterprise agent update",
            url="https://openai.com/news/example",
            canonical_url="https://openai.com/news/example",
            source_name="OpenAI Newsroom",
            source_tier="A",
            discovered_at=datetime.now(timezone.utc),
            duplicate_group_id="event-openai-001",
            credibility_reason="",
        )


def test_signal_total_score_must_match_score_set() -> None:
    scores = ScoreSet(
        strategic_impact=5,
        market_disruption=4,
        revenue_impact=4,
        competitive_threat=4,
        ax_relevance=5,
        executive_urgency=4,
    )

    signal = Signal(
        item_id="openai-001",
        title="OpenAI launches enterprise agent update",
        source_tier="A",
        scores=scores,
        total_score=26,
        priority="Critical Signal",
        rationale="Strong enterprise AX implications for commerce operations.",
    )
    assert signal.total_score == scores.total

    with pytest.raises(ValidationError):
        Signal(
            item_id="openai-001",
            title="OpenAI launches enterprise agent update",
            source_tier="A",
            scores=scores,
            total_score=20,
            priority="High Priority",
            rationale="This total is intentionally inconsistent.",
        )


def test_send_result_rejects_more_than_five_recipients() -> None:
    recipients = [
        Recipient(group=f"group_{index}", name=f"Person {index}", email=f"p{index}@example.com")
        for index in range(6)
    ]

    with pytest.raises(ValidationError):
        SendResult(
            run_date="2026-05-31",
            mode="draft",
            recipients=recipients,
            status="draft_created",
        )

