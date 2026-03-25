"""Divergence map telemetry utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from opentelemetry import trace

tracer = trace.get_tracer("entropy_rlaf.telemetry")


@dataclass(frozen=True)
class DivergencePoint:
    """One latent-vs-literal comparison data point."""

    node_id: str
    critic_score: float
    deterministic_score: float


class DivergenceMap:
    """Computes and summarizes latent/literal disagreements."""

    def summarize(self, points: Iterable[DivergencePoint]) -> dict[str, int]:
        severe = 0
        mild = 0
        total = 0
        with tracer.start_as_current_span("divergence_map.summarize"):
            for point in points:
                total += 1
                if point.critic_score > 0.9 and point.deterministic_score == 0.0:
                    severe += 1
                elif abs(point.critic_score - point.deterministic_score) > 0.4:
                    mild += 1
        return {"total": total, "severe": severe, "mild": mild}
