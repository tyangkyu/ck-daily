from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from ax_intel.models import CleanItem, HeroStory, Insight, RecommendedActions, Signal


def _item_lookup(clean_items: Iterable[CleanItem]) -> Dict[str, CleanItem]:
    return {item.id: item for item in clean_items}


def _scope_text(item: CleanItem) -> str:
    scope = item.related_scope or item.scope
    return ", ".join(scope) if scope else "디지털 전환"


def _title_or_source_contains(item: CleanItem, *keywords: str) -> bool:
    text = f"{item.title} {item.summary_raw} {item.source_name} {' '.join(item.scope)} {' '.join(item.related_scope)}"
    folded = text.casefold()
    return any(keyword.casefold() in folded for keyword in keywords)


def _primary_theme(item: CleanItem) -> str:
    if _title_or_source_contains(item, "multimodal", "image", "document"):
        return "멀티모달 업무 재설계"
    if _title_or_source_contains(item, "agent", "agentic", "workflow", "codex"):
        return "업무 실행형 에이전트"
    if _title_or_source_contains(item, "bedrock", "cloud", "aws", "inference"):
        return "클라우드 기반 AI 플랫폼"
    if _title_or_source_contains(item, "data", "foundation model", "transaction"):
        return "데이터 기반 산업 특화 모델"
    if _title_or_source_contains(item, "security", "cognito", "safeguard", "governance"):
        return "보안과 거버넌스"
    if _title_or_source_contains(item, "commerce", "shopping", "retail", "customer"):
        return "디지털 커머스"
    if _title_or_source_contains(item, "software", "developer", "engineering"):
        return "소프트웨어 엔지니어링"
    return "AI 플랫폼 전략"


def _evidence_phrase(item: CleanItem) -> str:
    theme = _primary_theme(item)
    if theme == "업무 실행형 에이전트":
        return "원문은 에이전트 도입에서 통제, 권한, 안전한 업무 적용 방식이 중요해지고 있음을 다룬다."
    if theme == "멀티모달 업무 재설계":
        return "원문은 텍스트뿐 아니라 이미지, 문서, 운영 데이터를 함께 다루는 업무 흐름의 변화를 다룬다."
    if theme == "클라우드 기반 AI 플랫폼":
        return "원문은 AI 모델을 기업의 기존 클라우드 운영 환경 안에서 더 쉽게 배포하고 관리하는 흐름을 다룬다."
    if theme == "데이터 기반 산업 특화 모델":
        return "원문은 산업 데이터의 구조를 반영한 모델과 분석 기반이 경쟁 자산이 되는 흐름을 다룬다."
    if theme == "보안과 거버넌스":
        return "원문은 AI와 디지털 서비스 확산에 필요한 보안, 복원성, 통제 체계의 강화를 다룬다."
    if theme == "디지털 커머스":
        return "원문은 검색, 추천, 상담, 구매 여정에서 AI가 고객 접점과 운영 방식을 바꾸는 흐름을 다룬다."
    if theme == "소프트웨어 엔지니어링":
        return "원문은 개발 방식과 소프트웨어 전달 체계가 AI를 중심으로 재편되는 흐름을 다룬다."
    return "원문은 AI가 단일 기능이 아니라 플랫폼과 조직 운영 전반의 전략 변수로 이동하는 흐름을 다룬다."


def _change_observed(item: CleanItem) -> str:
    theme = _primary_theme(item)
    return (
        f"{item.source_name}의 신호는 '{item.title}'을 통해 {theme} 경쟁이 기능 출시보다 "
        f"운영 체계와 도입 경로 설계로 이동하고 있음을 보여준다. {_evidence_phrase(item)}"
    )


def _industry_insight(signal: Signal, item: CleanItem) -> str:
    theme = _primary_theme(item)
    if theme == "업무 실행형 에이전트":
        angle = (
            "AI 도입의 초점이 답변 생성에서 권한 위임, 결과 검증, 예외 처리까지 포함한 "
            "업무 운영 모델로 옮겨가고 있다."
        )
    elif theme == "멀티모달 업무 재설계":
        angle = (
            "AI 활용은 단일 문서나 대화 처리에서 벗어나 여러 형태의 데이터를 함께 해석하는 "
            "업무 재설계 과제로 확장되고 있다."
        )
    elif theme == "클라우드 기반 AI 플랫폼":
        angle = (
            "모델 성능 자체보다 배포 경로, 과금 방식, 보안 통제, 기존 클라우드 운영 도구와의 "
            "결합력이 플랫폼 선택 기준으로 부상하고 있다."
        )
    elif theme == "데이터 기반 산업 특화 모델":
        angle = (
            "범용 LLM을 그대로 쓰는 단계에서 벗어나 거래, 고객, 운영 데이터의 구조를 반영한 "
            "산업별 모델과 데이터 상품화가 경쟁 축이 되고 있다."
        )
    elif theme == "보안과 거버넌스":
        angle = (
            "AI 활용 범위가 넓어질수록 인증, 접근 제어, 감사 추적, 지역별 복원성 같은 "
            "기반 통제가 서비스 품질의 일부로 평가된다."
        )
    elif theme == "디지털 커머스":
        angle = (
            "커머스 경쟁은 화면 단위 개인화에서 재고, 가격, 상담, 검색을 함께 조율하는 "
            "운영 플랫폼 경쟁으로 확장되고 있다."
        )
    elif theme == "소프트웨어 엔지니어링":
        angle = (
            "개발 생산성 향상은 코드 작성 자동화만으로는 부족하며, 요구사항 관리, 테스트, 배포, "
            "운영 피드백을 연결하는 방식으로 재설계되고 있다."
        )
    else:
        angle = (
            "AI는 개별 기능 개선 항목이 아니라 데이터, 클라우드, 보안, 조직 운영을 함께 바꾸는 "
            "플랫폼 전략 이슈로 다뤄져야 한다."
        )
    return f"{signal.total_score}/30점의 {signal.priority} 신호다. {angle}"


def _domestic_implication(item: CleanItem) -> str:
    theme = _primary_theme(item)
    if theme == "업무 실행형 에이전트":
        return (
            "국내 기업은 에이전트 PoC를 챗봇 확장으로 설계하기보다, 승인 권한, 로그, 장애 시 "
            "사람 개입 기준을 먼저 정해야 한다. 업무 자동화율보다 재작업 감소와 처리 리드타임을 "
            "우선 지표로 삼는 편이 현실적이다."
        )
    if theme == "멀티모달 업무 재설계":
        return (
            "국내 기업은 멀티모달 AI를 단순 문서 요약 도구로 보기보다, 이미지 검사, 상담 이력, "
            "상품 정보, 현장 문서를 함께 연결하는 업무 단위에서 검토해야 한다. 데이터 접근 권한과 "
            "검수 기준을 먼저 정하지 않으면 현업 확산이 어렵다."
        )
    if theme == "클라우드 기반 AI 플랫폼":
        return (
            "국내 IT 조직은 모델별 성능 비교만으로 의사결정하기 어렵다. 기존 클라우드 계약, "
            "데이터 반출 제한, 보안 심사, 운영 모니터링 체계까지 포함해 플랫폼 전환 비용을 "
            "함께 계산해야 한다."
        )
    if theme == "데이터 기반 산업 특화 모델":
        return (
            "국내 기업은 자체 데이터가 모델 차별화로 이어지는 영역과 외부 플랫폼을 쓰는 편이 "
            "나은 영역을 구분해야 한다. 거래 데이터와 운영 로그의 품질 관리가 향후 1~3년 "
            "투자 우선순위가 될 가능성이 높다."
        )
    if theme == "보안과 거버넌스":
        return (
            "국내 기업은 AI 서비스 도입 전에 개인정보, 접근 권한, 감사 로그, 지역별 장애 대응 "
            "요건을 표준 체크리스트로 만들어야 한다. 보안 심사를 사후 절차로 두면 확산 속도가 "
            "크게 떨어진다."
        )
    if theme == "디지털 커머스":
        return (
            "국내 커머스 기업은 추천 정확도보다 구매 전환, 상담 처리, 재고 예외 대응처럼 "
            "손익계산서와 연결되는 운영 지표를 기준으로 AI 적용 영역을 고르는 것이 유효하다."
        )
    return (
        "국내 IT 기업은 기술 도입 여부보다 어떤 업무 단위에서 비용, 속도, 품질이 동시에 "
        "개선되는지 검증해야 한다. 1~3년 관점에서는 작은 자동화 과제를 넓게 흩뿌리기보다 "
        "플랫폼화 가능한 공통 역량에 투자하는 편이 낫다."
    )


def _future_outlook(item: CleanItem) -> str:
    theme = _primary_theme(item)
    if theme == "업무 실행형 에이전트":
        return "향후 1~3년 동안 에이전트는 단독 앱보다 업무 시스템 안의 실행 계층으로 흡수될 가능성이 높다."
    if theme == "멀티모달 업무 재설계":
        return "멀티모달 AI는 문서 처리 자동화에서 시작해 품질 관리, 고객 응대, 현장 운영 지원으로 확장될 가능성이 높다."
    if theme == "클라우드 기반 AI 플랫폼":
        return "AI 플랫폼 경쟁은 모델 라인업보다 운영 안정성, 규제 대응, 비용 예측 가능성 중심으로 재편될 가능성이 크다."
    if theme == "데이터 기반 산업 특화 모델":
        return "산업별 데이터 모델은 금융, 커머스, 제조처럼 반복 거래 데이터가 많은 영역에서 먼저 상용화될 가능성이 높다."
    if theme == "보안과 거버넌스":
        return "AI 확산 속도는 모델 성능보다 조직이 신뢰할 수 있는 통제 체계를 얼마나 빨리 마련하느냐에 좌우될 것이다."
    if theme == "디지털 커머스":
        return "커머스 AI는 고객 접점 기능보다 가격, 재고, 상담, 물류를 연결하는 운영 최적화 영역에서 실질 효과가 커질 것이다."
    return "AI 투자는 실험성 예산에서 핵심 플랫폼 예산으로 이동하되, 성과 측정이 어려운 과제는 빠르게 정리될 가능성이 높다."


def _actions_for(item: CleanItem) -> RecommendedActions:
    theme = _primary_theme(item)
    immediate = [
        f"{theme} 관점에서 이번 신호가 기존 기술 로드맵의 어떤 가정과 충돌하는지 확인한다.",
        "관련 원문과 경쟁사 움직임을 대조해 과장된 홍보성 표현과 실제 적용 가능한 변화를 분리한다.",
    ]
    thirty_days = [
        "사업 지표나 운영 지표와 직접 연결되는 적용 후보를 1~2개로 좁힌다.",
        "필요 데이터, 보안 제약, 운영 책임자를 함께 정의해 PoC 범위를 작게 고정한다.",
    ]
    ninety_days = [
        "PoC 결과를 비용, 리드타임, 품질 지표로 평가해 확대 또는 중단을 결정한다.",
        "반복 적용 가능성이 확인된 역량은 개별 프로젝트가 아니라 공통 플랫폼 과제로 전환한다.",
    ]
    return RecommendedActions(immediate=immediate, thirty_days=thirty_days, ninety_days=ninety_days)


def build_insight(signal: Signal, item: CleanItem) -> Insight:
    return Insight(
        signal_id=signal.item_id,
        what_happened=_change_observed(item),
        why_it_matters=f"{_industry_insight(signal, item)} 관련 범위: {_scope_text(item)}.",
        implication_for_korea=_domestic_implication(item),
        implication_for_lg=_future_outlook(item),
        recommended_actions=_actions_for(item),
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
            f"총점 {hero.total_score}/30점, 시장 변화 {hero.scores.market_disruption}/5점, "
            f"전략 영향 {hero.scores.strategic_impact}/5점으로 오늘 가장 우선 검토할 신호로 선정했다."
        ),
        alternative_signal_ids=alternatives,
        visual_message=(
            "기술 발표를 단순 기능 출시가 아니라 산업 구조와 조직 운영 변화로 해석하는 "
            "경영진 브리프 장면으로 표현한다."
        ),
    )


def generate_phase6_outputs(
    signals: List[Signal], clean_items: List[CleanItem]
) -> Tuple[List[Insight], HeroStory]:
    insights = generate_insights(signals, clean_items)
    hero_story = select_hero_story(signals)
    return insights, hero_story
