from __future__ import annotations

from typing import Iterable, List

from ax_intel.models import CleanItem, ScoreSet, Signal, SourceTier
from ax_intel.scoring.rubric import priority_for_total


AX_KEYWORDS = {"ax", "agentic ai", "enterprise adoption", "multimodal ai"}
COMMERCE_KEYWORDS = {"commerce ai", "personalization", "recommendation", "ai shopping assistant"}
REVENUE_KEYWORDS = {"commerce", "shopping", "retail", "personalized", "membership"}
THREAT_KEYWORDS = {"amazon", "shopify", "openai", "agent", "platform"}


def _contains_any(text: str, keywords: Iterable[str]) -> bool:
    folded = text.casefold()
    return any(keyword in folded for keyword in keywords)


def _score(base: int, *signals: bool) -> int:
    return min(5, base + sum(1 for signal in signals if signal))


def score_clean_item(item: CleanItem) -> Signal:
    source_tier = SourceTier(item.source_tier)
    joined_scope = " ".join(item.scope + item.related_scope).casefold()
    text = f"{item.title} {item.summary_raw} {' '.join(item.companies)}".casefold()

    tier_boost = source_tier == SourceTier.A
    commerce_signal = _contains_any(joined_scope + " " + text, COMMERCE_KEYWORDS)
    ax_signal = _contains_any(joined_scope + " " + text, AX_KEYWORDS)
    revenue_signal = _contains_any(text, REVENUE_KEYWORDS)
    threat_signal = _contains_any(text, THREAT_KEYWORDS)
    enterprise_signal = "enterprise" in text or "workflow" in text

    scores = ScoreSet(
        strategic_impact=_score(2, tier_boost, enterprise_signal, ax_signal),
        market_disruption=_score(2, tier_boost, commerce_signal, ax_signal),
        revenue_impact=_score(1, commerce_signal, revenue_signal, enterprise_signal),
        competitive_threat=_score(1, threat_signal, commerce_signal, tier_boost),
        ax_relevance=_score(2, ax_signal, "agent" in text, "multimodal" in text),
        executive_urgency=_score(1, tier_boost, enterprise_signal, commerce_signal),
    )
    total = scores.total
    priority = priority_for_total(total)

    return Signal(
        item_id=item.id,
        title=item.title,
        source_tier=source_tier,
        scores=scores,
        total_score=total,
        priority=priority,
        rationale=(
            f"{item.source_tier} source with scope {', '.join(item.related_scope or item.scope)} "
            f"produced a {total}/30 strategic signal."
        ),
    )


def score_items(items: Iterable[CleanItem]) -> List[Signal]:
    return sorted(
        (score_clean_item(item) for item in items),
        key=lambda signal: signal.total_score,
        reverse=True,
    )

