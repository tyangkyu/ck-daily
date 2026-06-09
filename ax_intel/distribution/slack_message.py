from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from ax_intel.models import CleanItem, HeroStory, Insight, ReportManifest, RunContext, Signal


def _signal_lookup(signals: Iterable[Signal]) -> Dict[str, Signal]:
    return {signal.item_id: signal for signal in signals}


def _item_lookup(clean_items: Iterable[CleanItem]) -> Dict[str, CleanItem]:
    return {item.id: item for item in clean_items}


def _hero_insight(insights: List[Insight], hero_story: HeroStory) -> Insight:
    return next((insight for insight in insights if insight.signal_id == hero_story.signal_id), insights[0])


def _clip(text: str, limit: int = 220) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def _priority_label(priority: str) -> str:
    normalized = priority.lower()
    if "high" in normalized:
        return "High"
    if "monitor" in normalized or "medium" in normalized:
        return "Medium"
    return "Low"


def render_slack_message(
    *,
    context: RunContext,
    signals: List[Signal],
    insights: List[Insight],
    hero_story: HeroStory,
    manifest: ReportManifest,
    clean_items: List[CleanItem],
    canvas_url: Optional[str] = None,
) -> str:
    signals_by_id = _signal_lookup(signals)
    items_by_id = _item_lookup(clean_items)
    hero_signal = signals_by_id[hero_story.signal_id]
    hero_item = items_by_id[hero_story.signal_id]
    insight = _hero_insight(insights, hero_story)
    top_signals = "\n".join(
        f"{index}. [{_priority_label(signal.priority)}] *{signal.title}* ({signal.total_score}/30)"
        for index, signal in enumerate(signals[:3], start=1)
    )
    immediate_actions = "\n".join(f"- {action}" for action in insight.recommended_actions.immediate[:2])
    canvas_line = f"- Slack Canvas: {canvas_url}\n" if canvas_url else ""

    return f"""*ck-daily | {context.run_date.isoformat()} Executive Dashboard*

*Executive Summary*
- 핵심 신호: *{hero_story.title}* ({_priority_label(hero_signal.priority)}, {hero_signal.total_score}/30)
- 출처: {hero_item.source_name} / Tier {hero_item.source_tier}
- 한줄 판단: {_clip(insight.why_it_matters, 180)}

*Impact*
- Korea: {_clip(insight.implication_for_korea, 160)}
- LG/Enterprise: {_clip(insight.implication_for_lg, 180)}

*Top 전략 신호*
{top_signals}

*핵심 권고*
{immediate_actions}

*상세*
{canvas_line}- PDF: {manifest.pdf_path.name if manifest.pdf_path else "report.pdf"}
- 원문: {hero_item.url}
"""
