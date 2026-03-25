"""Entropy-RLAF CLI demo for secure data pipeline generation."""

from __future__ import annotations

import asyncio
from pathlib import Path

from entropy_rlaf.core.models import CandidateAction
from entropy_rlaf.engine.prm import TriangulatedPRMEngine
from entropy_rlaf.orchestrator.search import FastPruner, SlowExecutor, SearchOrchestrator
from entropy_rlaf.plugins.ast_security import ASTSecurityVerifier
from entropy_rlaf.plugins.sqlite_transactional import SQLiteTransactionalVerifier
from entropy_rlaf.refinery.dataset import DPODatasetRefinery
from entropy_rlaf.telemetry.divergence import DivergenceMap
from entropy_rlaf.verification_mesh.mesh import ASTStaticAnalyzer, FirecrackerMicroVMVerifier, VerificationMesh, Z3TheoremVerifier


async def main() -> None:
    unsafe = CandidateAction(
        candidate_id="unsafe-branch",
        code="import os\nprint('unsafe')",
        sql="SELECT * FROM users WHERE name = '' OR 1=1; DROP TABLE users;--",
        critic_score=0.95,
    )
    safe = CandidateAction(
        candidate_id="safe-branch",
        code="print('safe pipeline')",
        sql="SELECT id, name FROM users WHERE id = 1;",
        critic_score=0.65,
    )

    mesh = VerificationMesh(
        verifiers=[
            ASTSecurityVerifier(),
            ASTStaticAnalyzer(),
            SQLiteTransactionalVerifier(),
            FirecrackerMicroVMVerifier(),
            Z3TheoremVerifier(),
        ]
    )
    engine = TriangulatedPRMEngine()
    orchestrator = SearchOrchestrator(FastPruner(), SlowExecutor(mesh, engine))

    winner = await orchestrator.run([unsafe, safe], top_n=2)

    divergence = DivergenceMap()
    divergence.record(winner)

    refinery = DPODatasetRefinery()
    pair = refinery.build_pair(
        prompt="Generate a compliant SQL data pipeline step.",
        chosen=f"{winner.candidate.code}\n{winner.candidate.sql or ''}",
        rejected=f"{unsafe.code}\n{unsafe.sql or ''}",
        chosen_score=winner.ground_truth_score,
        rejected_score=0.0,
        fidelity_score=winner.fidelity_score,
        environmental_rationale="Unsafe branch attempted SQL injection and state-destructive mutation.",
    )
    output = Path("artifacts")
    output.mkdir(exist_ok=True)
    refinery.write_jsonl([pair], str(output / "dpo_pairs.jsonl"))

    print("=== Entropy-RLAF Demo ===")
    print(f"Winner: {winner.candidate.candidate_id}")
    print(f"Ground truth score: {winner.ground_truth_score:.3f}")
    print(f"Fidelity score: {winner.fidelity_score:.3f}")
    print(f"Critic penalized: {winner.was_meta_corrected}")
    print("Divergence map rows:")
    for row in divergence.heatmap_rows():
        print(row)
    print(f"Saved DPO dataset: {output / 'dpo_pairs.jsonl'}")


if __name__ == "__main__":
    asyncio.run(main())
