from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Dict, Iterable, List

from ax_intel.models import HeroStory, Insight, ReportManifest, RunContext, Signal


def _signal_lookup(signals: Iterable[Signal]) -> Dict[str, Signal]:
    return {signal.item_id: signal for signal in signals}


def _top_signal_lines(signals: List[Signal]) -> List[str]:
    return [
        f"- **{signal.title}** - {signal.priority}, {signal.total_score}/30점"
        for signal in signals[:5]
    ]


def _actions_md(insight: Insight) -> str:
    immediate = "\n".join(f"  - {item}" for item in insight.recommended_actions.immediate)
    thirty = "\n".join(f"  - {item}" for item in insight.recommended_actions.thirty_days)
    ninety = "\n".join(f"  - {item}" for item in insight.recommended_actions.ninety_days)
    return (
        "- 즉시 실행\n"
        f"{immediate}\n"
        "- 30일 계획\n"
        f"{thirty}\n"
        "- 90일 계획\n"
        f"{ninety}"
    )


def render_report_markdown(
    *, context: RunContext, signals: List[Signal], insights: List[Insight], hero_story: HeroStory
) -> str:
    hero_insight = next((insight for insight in insights if insight.signal_id == hero_story.signal_id), insights[0])
    signal_lines = "\n".join(_top_signal_lines(signals))
    insight_sections = "\n\n".join(
        [
            (
                f"### {index}. {insight.what_happened}\n\n"
                f"**왜 중요한가**: {insight.why_it_matters}\n\n"
                f"**한국 시장 시사점**: {insight.implication_for_korea}\n\n"
                f"**LG / 엔터프라이즈 커머스 시사점**: {insight.implication_for_lg}\n\n"
                f"**권고 액션**\n{_actions_md(insight)}"
            )
            for index, insight in enumerate(insights[:5], start=1)
        ]
    )

    return f"""# ck-daily 데일리 브리프

> 날짜: {context.run_date.isoformat()}
> Mode: {context.mode}

## 1페이지: 히어로 스토리

![히어로 비주얼](hero-image.png)

**{hero_story.title}**

{hero_story.selection_reason}

{hero_story.visual_message}

## 요약

- 히어로 신호: {hero_story.title}
- 우선순위: {_signal_lookup(signals)[hero_story.signal_id].priority}
- Top 신호 수: {len(signals[:5])}
- 핵심 시사점: {hero_insight.implication_for_lg}

## 2페이지: Top 전략 신호

{signal_lines}

## 3페이지: 커머스 인텔리전스

{insight_sections}

## 4페이지: AX 전환 인사이트

- 리소스 투입 전에 AX 연관성과 경영진 긴급도를 함께 검토한다.
- 우선순위가 높은 신호는 측정 가능한 PoC 가설로 전환한다.
- 약한 커머스 신호는 Tier A 공식 출처의 보강 여부를 계속 추적한다.

## 5페이지: 실행 과제

{_actions_md(hero_insight)}

## 경영진 질문

- 어떤 신호에 즉시 경영진 스폰서십이 필요한가?
- 어떤 커머스 업무 흐름이 AI 에이전트 PoC에 가장 적합한가?
- 90일 내 확산 판단을 위해 어떤 근거가 필요한가?
"""


def render_email_html(
    *, context: RunContext, signals: List[Signal], insights: List[Insight], hero_story: HeroStory
) -> str:
    hero_insight = next((insight for insight in insights if insight.signal_id == hero_story.signal_id), insights[0])
    top_items = "".join(
        f"<li><strong>{escape(signal.title)}</strong> — {escape(signal.priority)}, {signal.total_score}/30</li>"
        for signal in signals[:5]
    )
    actions = "".join(f"<li>{escape(action)}</li>" for action in hero_insight.recommended_actions.immediate)
    return f"""<!doctype html>
<html>
  <body style="font-family: Arial, sans-serif; color: #111827; line-height: 1.5;">
    <h1 style="margin-bottom: 4px;">ck-daily</h1>
    <p style="margin-top: 0; color: #6b7280;">{context.run_date.isoformat()} 데일리 브리프</p>
    <img src="hero-image.png" alt="Hero visual" style="width: 100%; max-width: 720px; border-radius: 8px;" />
    <h2>{escape(hero_story.title)}</h2>
    <p>{escape(hero_story.selection_reason)}</p>
    <h3>요약</h3>
    <p>{escape(hero_insight.why_it_matters)}</p>
    <h3>Top 전략 신호</h3>
    <ol>{top_items}</ol>
    <h3>핵심 권고</h3>
    <ul>{actions}</ul>
    <p style="color: #6b7280;">PDF 첨부는 현재 report.pdf 산출물로 생성된다.</p>
  </body>
</html>
"""


def render_archive_markdown(
    *, context: RunContext, signals: List[Signal], insights: List[Insight], hero_story: HeroStory
) -> str:
    report = render_report_markdown(
        context=context,
        signals=signals,
        insights=insights,
        hero_story=hero_story,
    )
    return report + "\n\n---\n\n아카이브 상태: Phase 8 skeleton에서 생성됨.\n"


def build_manifest(context: RunContext) -> ReportManifest:
    return ReportManifest(
        run_date=context.run_date,
        report_dir=context.report_dir,
        markdown_path=context.output_paths["report_markdown"],
        docx_path=context.output_paths["report_docx"],
        pdf_path=context.output_paths["report_pdf"],
        html_email_path=context.output_paths["email_html"],
        archive_path=context.output_paths["archive_markdown"],
    )
