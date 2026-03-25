"""Active inference search with two-phase pruning."""

from __future__ import annotations

import time
from typing import Sequence

from entropy_rlaf.core.models import CandidateAction, SearchOutcome, StepEvaluation
from entropy_rlaf.engine.prm_engine import TriangulatedPRMEngine
from entropy_rlaf.verification_mesh.mesh import VerificationMesh


class FastPruner:
    """Static policy + AST pre-filter.

    Keeps only candidates that pass cheap lexical checks. Intended runtime is <10ms.
    """

    def __init__(self, top_n: int = 2) -> None:
        self.top_n = top_n

    def prune(self, candidates: Sequence[CandidateAction]) -> list[CandidateAction]:
        start = time.perf_counter()
        safe = []
        for candidate in candidates:
            lower = candidate.content.lower()
            blocked = any(token in lower for token in ["drop table", " or 1=1", "exec(", "eval("])
            if not blocked:
                safe.append(candidate)
        sorted_safe = sorted(safe, key=lambda item: item.critic_score, reverse=True)
        elapsed_ms = (time.perf_counter() - start) * 1000
        if elapsed_ms > 10:
            raise RuntimeError(f"FastPruner exceeded latency budget: {elapsed_ms:.3f}ms")
        return sorted_safe[: self.top_n]


class SlowExecutor:
    """Runs surviving branches in the verification mesh and PRM engine."""

    def __init__(self, mesh: VerificationMesh, prm: TriangulatedPRMEngine) -> None:
        self.mesh = mesh
        self.prm = prm

    async def execute(self, candidate: CandidateAction) -> tuple[float, float, str]:
        results = await self.mesh.run(candidate)
        det_score = min(result.score for result in results)
        env_score = 1.0 if all(result.passed for result in results) else 0.0
        step = StepEvaluation(
            env_diff=env_score,
            det_policy=det_score,
            critic_consensus=candidate.critic_score,
        )
        ground_truth = self.prm.process_reward(step)
        fidelity = self.prm.fidelity_score(env_outcome=env_score, critic_opinion=candidate.critic_score)
        self.prm.meta_correct(fidelity)
        rationale = "; ".join(result.rationale for result in results)
        return ground_truth, fidelity, rationale


class SearchOrchestrator:
    """FastPruner -> SlowExecutor orchestration loop."""

    def __init__(self, fast: FastPruner, slow: SlowExecutor) -> None:
        self.fast = fast
        self.slow = slow

    async def run(self, candidates: Sequence[CandidateAction]) -> SearchOutcome:
        survivors = self.fast.prune(candidates)
        if not survivors:
            raise ValueError("No candidates survived fast pruning")

        best: SearchOutcome | None = None
        for candidate in survivors:
            ground_truth, fidelity, rationale = await self.slow.execute(candidate)
            outcome = SearchOutcome(
                selected=candidate,
                ground_truth_score=ground_truth,
                fidelity_score=fidelity,
                rationale=rationale,
            )
            if best is None or outcome.ground_truth_score > best.ground_truth_score:
                best = outcome
            if ground_truth == 1.0 and fidelity == 1.0:
                return outcome

        assert best is not None
        return best
