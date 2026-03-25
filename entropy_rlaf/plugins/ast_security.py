"""AST security verifier plugin.

Performs strict AST-level sanitization before payload reaches a critic or runtime.
"""

from __future__ import annotations

import ast

from entropy_rlaf.core.models import VerificationResult


class ASTSecurityVerifier:
    """Reject dangerous Python patterns and obvious SQL injection strings."""

    name = "ast_security"
    _blocked_imports = {"os", "subprocess", "sys"}
    _blocked_calls = {"eval", "exec", "compile", "__import__"}

    async def verify(self, payload: str) -> VerificationResult:
        findings: list[str] = []
        try:
            tree = ast.parse(payload)
        except SyntaxError as exc:
            return VerificationResult(
                verifier_name=self.name,
                passed=False,
                score=0.0,
                rationale=f"Syntax error blocks execution: {exc.msg}",
            )

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split(".")[0]
                    if root_mod in self._blocked_imports:
                        findings.append(f"blocked import: {root_mod}")
            if isinstance(node, ast.ImportFrom) and node.module:
                root_mod = node.module.split(".")[0]
                if root_mod in self._blocked_imports:
                    findings.append(f"blocked import-from: {root_mod}")
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in self._blocked_calls:
                    findings.append(f"blocked call: {node.func.id}")

        lowered = payload.lower()
        sql_injection_markers = ("drop table", " or 1=1", "--", ";--")
        if any(marker in lowered for marker in sql_injection_markers):
            findings.append("possible SQL injection pattern")

        passed = not findings
        return VerificationResult(
            verifier_name=self.name,
            passed=passed,
            score=1.0 if passed else 0.0,
            rationale="AST security policy passed" if passed else "; ".join(findings),
        )
