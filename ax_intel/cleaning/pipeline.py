from __future__ import annotations

from typing import Iterable, List

from ax_intel.cleaning.credibility import credibility_reason
from ax_intel.cleaning.dedupe import dedupe_items, duplicate_group_id
from ax_intel.cleaning.normalize import canonicalize_url
from ax_intel.models import CleanItem, RawItem, SourceTier


def raw_to_clean_item(item: RawItem) -> CleanItem:
    source_tier = SourceTier(item.source_tier)
    return CleanItem(
        **item.model_dump(mode="python"),
        canonical_url=canonicalize_url(str(item.url)),
        credibility_reason=credibility_reason(source_tier),
        related_scope=item.scope,
        duplicate_group_id=duplicate_group_id(item),
        needs_review=source_tier == SourceTier.C,
    )


def clean_items(items: Iterable[RawItem]) -> List[CleanItem]:
    return [raw_to_clean_item(item) for item in dedupe_items(items)]

