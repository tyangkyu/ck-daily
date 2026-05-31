from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from ax_intel.models import CleanItem, HeroStory, Insight, RecommendedActions, Signal


def _item_lookup(clean_items: Iterable[CleanItem]) -> Dict[str, CleanItem]:
    return {item.id: item for item in clean_items}


def _scope_text(item: CleanItem) -> str:
    scope = item.related_scope or item.scope
    return ", ".join(scope) if scope else "AX/Commerce"


def _company_phrase(item: CleanItem) -> str:
    if not item.companies:
        return "모니터링 대상 시장"
    return ", ".join(item.companies)


def _summary_sentence(item: CleanItem) -> str:
    summary = item.summary_raw.strip()
    if not summary:
        return "세부 요약은 아직 수집되지 않았으며, 후속 크롤링에서 보강이 필요하다."
    return summary


def _strategic_angle(item: CleanItem) -> str:
    scope = set(item.related_scope or item.scope)
    if "Agentic AI" in scope:
        return "AI 에이전트를 실제 업무 흐름에 투입할 때 필요한 통제, 권한, 감사 체계가 경쟁 포인트로 이동하고 있음을 보여준다."
    if "Multimodal AI" in scope:
        return "텍스트 중심 자동화를 넘어 이미지, 문서, 운영 데이터를 함께 해석하는 업무 재설계 압력이 커지고 있음을 의미한다."
    if "AI Shopping Assistant" in scope:
        return "검색과 추천이 대화형 구매 지원으로 확장되며 커머스 접점의 전환율 경쟁이 다시 열릴 가능성이 있다."
    if "Commerce AI" in scope:
        return "커머스 운영의 차별화 축이 가격·상품 구색에서 AI 기반 개인화와 운영 자동화로 이동하고 있음을 시사한다."
    return "AI 전환이 개별 기능 개선을 넘어 경영진이 추적해야 할 플랫폼 전략 이슈로 올라오고 있음을 시사한다."


def build_insight(signal: Signal, item: CleanItem) -> Insight:
    scope = _scope_text(item)
    companies = _company_phrase(item)
    source = f"{item.source_name} ({item.source_tier})"
    summary = _summary_sentence(item)
    strategic_angle = _strategic_angle(item)

    return Insight(
        signal_id=signal.item_id,
        what_happened=f"{source}에서 '{signal.title}' 신호가 포착됐다. 핵심 내용은 {summary}",
        why_it_matters=(
            f"이 신호는 {signal.total_score}/30점으로 '{signal.priority}' 등급이며, "
            f"{scope} 영역과 직접 연결된다. {strategic_angle}"
        ),
        implication_for_korea=(
            f"국내 커머스·플랫폼 기업은 {companies}의 움직임이 고객 경험, 운영 효율, "
            "플랫폼 경쟁력으로 전환되는 방식을 추적해야 한다. 특히 한국 시장에서는 빠른 배송, 멤버십, "
            "검색·추천 품질이 이미 경쟁의 기본값이 되었기 때문에 AI가 실제 구매 여정의 시간을 줄이는지 확인해야 한다."
        ),
        implication_for_lg=(
            "LG 및 엔터프라이즈 커머스 관점에서는 검색, 추천, 풀필먼트, "
            "AI 에이전트 기반 운영 자동화의 적용 후보로 검토할 필요가 있다. 단순 챗봇이 아니라 "
            "상품 탐색, 고객 응대, 재고·물류 예외 처리, 임직원 업무 지원 중 어디에서 매출 또는 비용 효과가 나는지 가설화해야 한다."
        ),
        recommended_actions=RecommendedActions(
            immediate=[
                "출처 신뢰도를 확인하고 기존 AX 커머스 과제와 비교한다.",
                "유사한 내부 PoC 또는 파일럿이 이미 있는지 확인한다.",
            ],
            thirty_days=[
                "커머스 성과와 연결되는 측정 가능한 PoC 가설을 1개 정의한다.",
                "필요 데이터, 업무 오너, 시스템 연계 제약을 정리한다.",
            ],
            ninety_days=[
                "PoC 근거를 바탕으로 확산, 제휴, 모니터링 중 하나를 결정한다.",
                "리스크, 비용, 경쟁 영향이 포함된 경영진 보고안을 준비한다.",
            ],
        ),
    )


def generate_insights(signals: Iterable[Signal], clean_items: Iterable[CleanItem]) -> List[Insight]:
    lookup = _item_lookup(clean_items)
    insights: List[Insight] = []
    for signal in signals:
        item = lookup.get(signal.item_id)
        if item is None:
            continue
        insights.append(build_insight(signal, item))
    return insights


def select_hero_story(signals: List[Signal]) -> HeroStory:
    if not signals:
        raise ValueError("Cannot select hero story without signals")

    hero = max(
        signals,
        key=lambda signal: (
            signal.total_score,
            signal.scores.executive_urgency,
            signal.scores.ax_relevance,
            signal.scores.market_disruption,
        ),
    )
    alternatives = [signal.item_id for signal in signals if signal.item_id != hero.item_id][:2]

    return HeroStory(
        signal_id=hero.item_id,
        title=hero.title,
        selection_reason=(
            f"총점 {hero.total_score}/30점, AX 연관성 {hero.scores.ax_relevance}/5점, "
            f"경영진 긴급도 {hero.scores.executive_urgency}/5점으로 오늘의 핵심 스토리로 선정했다."
        ),
        alternative_signal_ids=alternatives,
        visual_message=(
            "AI 기반 커머스 운영이 단순 리포팅에서 에이전트 기반 실행 체계로 "
            "전환되는 모습을 고밀도 경영진 뉴스레터 장면으로 표현한다."
        ),
    )


def generate_phase6_outputs(
    signals: List[Signal], clean_items: List[CleanItem]
) -> Tuple[List[Insight], HeroStory]:
    insights = generate_insights(signals, clean_items)
    hero_story = select_hero_story(signals)
    return insights, hero_story
