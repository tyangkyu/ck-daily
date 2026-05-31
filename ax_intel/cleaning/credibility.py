from __future__ import annotations

from ax_intel.models import SourceTier


TIER_REASONS = {
    SourceTier.A: "Tier A official or highest-credibility source.",
    SourceTier.B: "Tier B credible industry source.",
    SourceTier.C: "Tier C weak signal source; requires corroboration.",
}


def credibility_reason(source_tier: SourceTier) -> str:
    return TIER_REASONS[source_tier]

