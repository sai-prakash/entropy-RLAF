import asyncio

from entropy_rlaf.core.models import CandidateAction
from entropy_rlaf.engine.prm import TriangulatedPRMEngine
from entropy_rlaf.orchestrator.search import FastPruner, SearchOrchestrator, SlowExecutor
from entropy_rlaf.plugins.ast_security import ASTSecurityVerifier
from entropy_rlaf.plugins.sqlite_transactional import SQLiteTransactionalVerifier
from entropy_rlaf.verification_mesh.mesh import VerificationMesh


def test_search_prefers_safe_candidate() -> None:
    unsafe = CandidateAction(
        candidate_id="unsafe",
        code="print('oops')",
        sql="DROP TABLE users;",
        critic_score=0.9,
    )
    safe = CandidateAction(
        candidate_id="safe",
        code="print('ok')",
        sql="SELECT * FROM users;",
        critic_score=0.6,
    )
    mesh = VerificationMesh([ASTSecurityVerifier(), SQLiteTransactionalVerifier()])
    orchestrator = SearchOrchestrator(FastPruner(), SlowExecutor(mesh, TriangulatedPRMEngine()))
    result = asyncio.run(orchestrator.run([unsafe, safe], top_n=2))
    assert result.candidate.candidate_id == "safe"
