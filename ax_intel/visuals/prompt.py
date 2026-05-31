from __future__ import annotations

from datetime import date
from typing import List

from ax_intel.models import HeroStory, Signal


def _signal_chips(hero_signal: Signal, all_signals: List[Signal]) -> List[str]:
    chips = [
        f"AX 연관성 {hero_signal.scores.ax_relevance}/5",
        f"{hero_signal.priority}",
        f"총점 {hero_signal.total_score}/30",
    ]
    if len(all_signals) > 1:
        chips.append(f"Top 신호 {len(all_signals)}건")
    return chips[:3]


def build_hero_prompt(hero_story: HeroStory, signals: List[Signal], run_date: date) -> str:
    signal_lookup = {signal.item_id: signal for signal in signals}
    hero_signal = signal_lookup[hero_story.signal_id]
    chips = _signal_chips(hero_signal, signals)
    formatted_date = run_date.strftime("%Y.%m.%d")

    return f"""# 히어로 비주얼 프롬프트

ck-daily용 16:9 경영진 뉴스레터 히어로 이미지를 [뉴스레터체]로 생성한다.

## [뉴스레터체] Style Memory

- 상단 중앙에 강한 헤드라인을 크게 배치한다.
- 컬러풀한 뉴스레터/매거진 썸네일 느낌을 낸다.
- 디테일이 풍부한 애니·일러스트 스타일을 사용한다.
- 밝고 선명한 조명과 고밀도 배치를 적용한다.
- 한 장만 봐도 메시지가 전달되는 장면 연출을 우선한다.
- 우측 하단에 작은 제작 크레딧 형태의 signature를 포함한다.
- 투자, 산업, 트렌드, 사회 이슈를 시각적으로 스토리텔링한다.

## Canvas

- Aspect ratio: 16:9
- Top-center: large Korean headline
- Middle: dense business infographic composition
- Bottom/right: compact signal chips and small credit
- Credit: `ck-daily | {formatted_date}`

## Headline

{hero_story.title}

## Subheadline

{hero_story.selection_reason}

## Visual Narrative

{hero_story.visual_message}

## Signal Chips

1. {chips[0]}
2. {chips[1]}
3. {chips[2]}

## Constraints

- Use a colorful but executive-grade palette.
- Avoid real company logos unless explicitly provided and permitted.
- Avoid unreadable fake Korean text outside the provided headline, subheadline, chips, and credit.
- Avoid a generic robot mascot or childish icon style.
"""
