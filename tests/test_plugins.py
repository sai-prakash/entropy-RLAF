import asyncio

from entropy_rlaf.core.models import CandidateAction
from entropy_rlaf.plugins.ast_security import ASTSecurityVerifier
from entropy_rlaf.plugins.sqlite_transactional import SQLiteTransactionalVerifier


def test_ast_verifier_blocks_exec() -> None:
    verifier = ASTSecurityVerifier()
    action = CandidateAction(action_id="p1", language="python", content="exec('boom')", critic_score=0.1)
    result = asyncio.run(verifier.verify(action))
    assert not result.passed


def test_sqlite_verifier_executes_safe_query() -> None:
    verifier = SQLiteTransactionalVerifier()
    action = CandidateAction(
        action_id="s1",
        language="sql",
        content="SELECT * FROM users WHERE id = 1",
        critic_score=0.7,
    )
    result = asyncio.run(verifier.verify(action))
    assert result.passed
