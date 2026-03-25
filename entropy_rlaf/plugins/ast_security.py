"""AST security verifier plugin.

This plugin fails closed for dangerous imports/calls and common SQL injection patterns.
"""

from __future__ import annotations

import ast

from entropy_rlaf.core.models import CandidateAction, VerificationResult

_DANGEROUS_IMPORTS = {"os", "subprocess", "socket", "sys"}
_DANGEROUS_CALLS = {"eval", "exec", "compile", "__import__"}


class ASTSecurityVerifier:
    """Deterministic verifier for malicious Python payload patterns."""

    name = "ast_security"

    async def verify(self, action: CandidateAction) -> VerificationResult:
        if action.language.lower() != "python":
            return VerificationResult(
                verifier_name=self.name,
                passed=True,
                score=1.0,
                rationale="Language not Python; AST security checks skipped.",
            )

        try:
            tree = ast.parse(action.content)
        except SyntaxError as error:
            return VerificationResult(
                verifier_name=self.name,
                passed=False,
                score=0.0,
                rationale=f"SyntaxError during AST parse: {error.msg}",
            )

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = {alias.name.split(".")[0] for alias in node.names}
                risky = names.intersection(_DANGEROUS_IMPORTS)
                if risky:
                    return VerificationResult(
                        verifier_name=self.name,
                        passed=False,
                        score=0.0,
                        rationale=f"Dangerous import blocked: {sorted(risky)[0]}",
                    )
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in _DANGEROUS_CALLS:
                    return VerificationResult(
                        verifier_name=self.name,
                        passed=False,
                        score=0.0,
                        rationale=f"Dangerous call blocked: {node.func.id}()",
                    )

        if "or 1=1" in action.content.lower() or "--" in action.content:
            return VerificationResult(
                verifier_name=self.name,
                passed=False,
                score=0.0,
                rationale="Static SQL injection signature detected.",
            )

        return VerificationResult(
            verifier_name=self.name,
            passed=True,
            score=1.0,
            rationale="AST policy checks passed.",
        )
