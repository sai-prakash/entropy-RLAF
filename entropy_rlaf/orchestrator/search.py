"""Active inference search loop with two-phase pruning."""

from __future__ import annotations

import time

from entropy_rlaf.core.models import CandidateAction, SearchNodeResult
from entropy_rlaf.engine.prm import TriangulatedPRMEngine
from entropy_rlaf.verification_mesh.mesh import VerificationMesh


class FastPruner:
    """Fast deterministic filter that excludes unsafe candidates in <10ms target."""

    def __init__(self, blocked_tokens: tuple[str, ...] = ("DROP TABLE", "exec(", "eval(")) -> None:
        self._blocked_tokens = tuple(token.lower() for token in blocked_tokens)

    def run(self, candidates: list[CandidateAction], top_n: int = 2) -> list[CandidateAction]:
        start = time.perf_counter()
        safe = [
            cand
            for cand in candidates
            if not any(token in (cand.code + " " + (cand.sql or "")).lower() for token in self._blocked_tokens)
        ]
        elapsed_ms = (time.perf_counter() - start) * 1_000
        if elapsed_ms > 10:
            raise RuntimeError(f"FastPruner SLA exceeded: {elapsed_ms:.2f}ms")
        return safe[:top_n]


class SlowExecutor:
    """Executes verifier mesh for candidate branches."""

    def __init__(self, mesh: VerificationMesh, reward_engine: TriangulatedPRMEngine) -> None:
        self._mesh = mesh
        self._reward_engine = reward_engine

    async def evaluate(self, candidate: CandidateAction) -> SearchNodeResult:
        joined_payload = f"{candidate.code}\n{candidate.sql or ''}"
        results = await self._mesh.verify_all(joined_payload)

        deterministic = float(sum(r.score for r in results) / max(len(results), 1))
        env_outcome = deterministic
        fidelity = self._reward_engine.fidelity_score(env_outcome, candidate.critic_score)
        corrected = self._reward_engine.apply_meta_correction(fidelity)
        reward = self._reward_engine.score_step(
            step_index=0,
            env_diff=env_outcome,
            det_policy=deterministic,
            critic_consensus=candidate.critic_score,
        )
        return SearchNodeResult(
            candidate=candidate,
            verifier_results=results,
            ground_truth_score=reward.value,
            env_outcome=env_outcome,
            deterministic_score=deterministic,
            critic_consensus=candidate.critic_score,
            fidelity_score=fidelity,
            was_meta_corrected=corrected,
        )


class SearchOrchestrator:
    """FastPruner -> SlowExecutor orchestration with early perfect-score abort."""

    def __init__(self, fast_pruner: FastPruner, slow_executor: SlowExecutor) -> None:
        self._fast_pruner = fast_pruner
        self._slow_executor = slow_executor

    async def run(self, candidates: list[CandidateAction], top_n: int = 2) -> SearchNodeResult:
        survivors = self._fast_pruner.run(candidates, top_n=top_n)
        if not survivors:
            raise ValueError("No candidate survived fast pruning")

        best: SearchNodeResult | None = None
        for candidate in survivors:
            result = await self._slow_executor.evaluate(candidate)
            if best is None or result.ground_truth_score > best.ground_truth_score:
                best = result
            if result.ground_truth_score >= 0.999:
                return result
        if best is None:
            raise RuntimeError("No candidate result was produced")
        return best
