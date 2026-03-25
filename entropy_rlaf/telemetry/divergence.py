"""Divergence map telemetry helpers."""

from __future__ import annotations

from dataclasses import dataclass

try:
    from opentelemetry import trace
except ModuleNotFoundError:  # pragma: no cover
    class _DummySpan:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return None
        def set_attribute(self, key, value):
            return None

    class _DummyTracer:
        def start_as_current_span(self, name):
            return _DummySpan()

    class _DummyTrace:
        @staticmethod
        def get_tracer(_name):
            return _DummyTracer()

    trace = _DummyTrace()

from entropy_rlaf.core.models import SearchNodeResult


@dataclass
class DivergencePoint:
    """Captures latent-vs-literal disagreement for one node."""

    candidate_id: str
    critic_score: float
    deterministic_score: float


class DivergenceMap:
    """Collects divergence events and exports lightweight summaries."""

    def __init__(self) -> None:
        self._points: list[DivergencePoint] = []
        self._tracer = trace.get_tracer("entropy_rlaf.telemetry")

    def record(self, result: SearchNodeResult) -> None:
        """Record one result and emit OpenTelemetry span data."""
        with self._tracer.start_as_current_span("search_node") as span:
            span.set_attribute("candidate.id", result.candidate.candidate_id)
            span.set_attribute("critic.score", result.critic_consensus)
            span.set_attribute("deterministic.score", result.deterministic_score)
            self._points.append(
                DivergencePoint(
                    candidate_id=result.candidate.candidate_id,
                    critic_score=result.critic_consensus,
                    deterministic_score=result.deterministic_score,
                )
            )

    def heatmap_rows(self) -> list[dict[str, float | str]]:
        """Return rows that external tools can convert to heatmaps."""
        return [
            {
                "candidate_id": p.candidate_id,
                "critic_score": p.critic_score,
                "deterministic_score": p.deterministic_score,
                "divergence": abs(p.critic_score - p.deterministic_score),
            }
            for p in self._points
        ]
