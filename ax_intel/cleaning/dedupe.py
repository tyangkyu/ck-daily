from __future__ import annotations

import hashlib
import re
from typing import Iterable, List

from ax_intel.cleaning.normalize import canonicalize_url
from ax_intel.models import RawItem


WORD_RE = re.compile(r"[a-z0-9가-힣]+")


def normalized_title(title: str) -> str:
    return " ".join(WORD_RE.findall(title.casefold()))


def duplicate_group_id(item: RawItem) -> str:
    canonical_url = canonicalize_url(str(item.url))
    title_key = normalized_title(item.title)
    company_key = ",".join(sorted(item.companies))
    digest = hashlib.sha256(f"{canonical_url}|{title_key}|{company_key}".encode("utf-8")).hexdigest()
    return f"event-{digest[:16]}"


def dedupe_items(items: Iterable[RawItem]) -> List[RawItem]:
    seen = set()
    unique: List[RawItem] = []
    for item in items:
        key = duplicate_group_id(item)
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique

