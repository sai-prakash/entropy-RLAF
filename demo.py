"""CLI demonstration for Entropy-RLAF Phase 1 MVP."""

from __future__ import annotations

import asyncio
from pathlib import Path

from entropy_rlaf.core.models import CandidateAction
from entropy_rlaf.engine.prm_engine import TriangulatedPRMEngine
from entropy_rlaf.orchestrator.search import FastPruner, SearchOrchestrator, SlowExecutor
from entropy_rlaf.plugins.ast_security import ASTSecurityVerifier
from entropy_rlaf.plugins.sqlite_transactional import SQLiteTransactionalVerifier
from entropy_rlaf.refinery.dpo_refinery import DPODatasetRefinery
from entropy_rlaf.telemetry.divergence import DivergenceMap, DivergencePoint
from entropy_rlaf.verification_mesh.mesh import ASTStaticAnalyzer, FirecrackerMicroVMVerifier, VerificationMesh, Z3TheoremVerifier


async def main() -> None:
    prompt = "Generate a secure SQL query to read a user by ID."

    unsafe = CandidateAction(
        action_id="unsafe_sqli",
        language="sql",
        content="SELECT * FROM users WHERE id = 1 OR 1=1 --",
        critic_score=0.98,
    )
    safe = CandidateAction(
        action_id="safe_sql",
        language="sql",
        content="SELECT * FROM users WHERE id = 1",
        critic_score=0.65,
    )

    mesh = VerificationMesh(
        [
            ASTSecurityVerifier(),
            SQLiteTransactionalVerifier(),
            FirecrackerMicroVMVerifier(),
            Z3TheoremVerifier(),
            ASTStaticAnalyzer(),
        ]
    )
    prm = TriangulatedPRMEngine()
    orchestrator = SearchOrchestrator(FastPruner(top_n=2), SlowExecutor(mesh, prm))

    outcome = await orchestrator.run([unsafe, safe])

    rejected = unsafe if outcome.selected.action_id == safe.action_id else safe
    refinery = DPODatasetRefinery(min_fidelity=0.5)
    record = refinery.build_record(
        prompt=prompt,
        chosen=outcome.selected,
        rejected=rejected,
        rationale=outcome.rationale,
        fidelity=outcome.fidelity_score,
    )
    if record:
        output = Path("data/dpo_pairs.jsonl")
        refinery.write_jsonl(output, [record])
        print(f"Saved DPO pair to {output}")

    divergence = DivergenceMap().summarize(
        [
            DivergencePoint(node_id="unsafe", critic_score=unsafe.critic_score, deterministic_score=0.0),
            DivergencePoint(node_id="safe", critic_score=safe.critic_score, deterministic_score=1.0),
        ]
    )

    print(f"Selected branch: {outcome.selected.action_id}")
    print(f"Ground-truth score: {outcome.ground_truth_score:.2f}")
    print(f"Fidelity score: {outcome.fidelity_score:.2f}")
    print(f"Critic penalty after meta-correction: {prm.critic_penalty:.2f}")
    print(f"Divergence summary: {divergence}")


if __name__ == "__main__":
    asyncio.run(main())
