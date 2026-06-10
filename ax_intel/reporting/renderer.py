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


def _unique_lines(lines: Iterable[str]) -> List[str]:
    seen = set()
    unique = []
    for line in lines:
        if line in seen:
            continue
        seen.add(line)
        unique.append(line)
    return unique


def render_report_markdown(
    *, context: RunContext, signals: List[Signal], insights: List[Insight], hero_story: HeroStory
) -> str:
    hero_insight = next((insight for insight in insights if insight.signal_id == hero_story.signal_id), insights[0])
    signal_lines = "\n".join(_top_signal_lines(signals))
    insight_sections = "\n\n".join(
        [
            (
                f"### {index}. {_signal_lookup(signals)[insight.signal_id].title}\n\n"
                f"{insight.why_it_matters}\n\n"
                f"**근거**: {insight.what_happened}"
            )
            for index, insight in enumerate(insights[:5], start=1)
        ]
    )
    domestic_sections = "\n\n".join(
        [
            (
                f"### {index}. {_signal_lookup(signals)[insight.signal_id].title}\n\n"
                f"{insight.implication_for_korea}\n\n"
                f"**실행 검토**\n{_actions_md(insight)}"
            )
            for index, insight in enumerate(insights[:3], start=1)
        ]
    )
    outlook_lines = "\n".join(f"- {line}" for line in _unique_lines(insight.implication_for_lg for insight in insights[:5]))

    return f"""# ck-daily 데일리 브리프

> 날짜: {context.run_date.isoformat()}
> 실행 모드: {context.mode}

![히어로 비주얼](hero-image.png)

## 1. 핵심 요약

- 오늘의 핵심 신호는 **{hero_story.title}**이다.
- {hero_story.selection_reason}
- {hero_insight.why_it_matters}
- {hero_insight.implication_for_korea}

## 2. 주목해야 할 변화

{hero_insight.what_happened}

### Top 전략 신호

{signal_lines}

## 3. IT 산업 관점 핵심 인사이트

{insight_sections}

## 4. 국내 기업이 고려해야 할 시사점

{domestic_sections}

## 5. 향후 전망

{outlook_lines}

## 검토 질문

- 이 신호가 기존 기술 로드맵의 어떤 가정을 바꾸는가?
- 1~3년 내 사업 지표나 운영 지표로 검증 가능한 적용 영역은 무엇인가?
- 과장된 홍보 문구를 제외했을 때 실제 투자 우선순위로 남는 항목은 무엇인가?
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
    <h3>핵심 요약</h3>
    <p>{escape(hero_insight.why_it_matters)}</p>
    <h3>주목해야 할 변화</h3>
    <p>{escape(hero_insight.what_happened)}</p>
    <h3>Top 전략 신호</h3>
    <ol>{top_items}</ol>
    <h3>국내 기업이 고려해야 할 시사점</h3>
    <p>{escape(hero_insight.implication_for_korea)}</p>
    <h3>실행 검토</h3>
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
    return report + "\n\n---\n\n아카이브 상태: 생성 완료.\n"


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
