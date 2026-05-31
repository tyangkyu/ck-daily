from __future__ import annotations

from ax_intel.models import SignalPriority


def priority_for_total(total_score: int) -> SignalPriority:
    if total_score >= 25:
        return SignalPriority.CRITICAL
    if total_score >= 20:
        return SignalPriority.HIGH
    if total_score >= 15:
        return SignalPriority.MONITOR
    return SignalPriority.LOW

