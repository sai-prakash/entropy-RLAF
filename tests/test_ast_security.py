import asyncio

from entropy_rlaf.plugins.ast_security import ASTSecurityVerifier


def test_ast_security_blocks_unsafe_imports() -> None:
    verifier = ASTSecurityVerifier()
    result = asyncio.run(verifier.verify("import os\nprint('x')"))
    assert not result.passed
    assert result.score == 0.0


def test_ast_security_allows_safe_payload() -> None:
    verifier = ASTSecurityVerifier()
    result = asyncio.run(verifier.verify("print('hello')"))
    assert result.passed
    assert result.score == 1.0
