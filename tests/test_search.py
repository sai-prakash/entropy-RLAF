import asyncio

from entropy_rlaf.core.models import CandidateAction
from entropy_rlaf.engine.prm_engine import TriangulatedPRMEngine
from entropy_rlaf.orchestrator.search import FastPruner, SearchOrchestrator, SlowExecutor
from entropy_rlaf.plugins.ast_security import ASTSecurityVerifier
from entropy_rlaf.plugins.sqlite_transactional import SQLiteTransactionalVerifier
from entropy_rlaf.verification_mesh.mesh import ASTStaticAnalyzer, FirecrackerMicroVMVerifier, VerificationMesh, Z3TheoremVerifier


def test_orchestrator_selects_safe_candidate() -> None:
    candidates = [
        CandidateAction(
            action_id="unsafe",
            language="sql",
            content="SELECT * FROM users WHERE id = 1 OR 1=1 --",
            critic_score=0.95,
        ),
        CandidateAction(
            action_id="safe",
            language="sql",
            content="SELECT * FROM users WHERE id = 1",
            critic_score=0.65,
        ),
    ]
    mesh = VerificationMesh(
        [
            ASTSecurityVerifier(),
            SQLiteTransactionalVerifier(),
            FirecrackerMicroVMVerifier(),
            Z3TheoremVerifier(),
            ASTStaticAnalyzer(),
        ]
    )
    orchestrator = SearchOrchestrator(FastPruner(top_n=2), SlowExecutor(mesh, TriangulatedPRMEngine()))
    outcome = asyncio.run(orchestrator.run(candidates))
    assert outcome.selected.action_id == "safe"
