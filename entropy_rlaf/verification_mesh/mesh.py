"""Verification Mesh implementation with pluggable backends."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from entropy_rlaf.core.base import Verifier as VerifierProtocol
from entropy_rlaf.core.models import CandidateAction, VerificationResult


class VerificationMesh:
    """Runs multiple verifiers concurrently and aggregates evidence."""

    def __init__(self, verifiers: Sequence[VerifierProtocol]) -> None:
        self._verifiers = list(verifiers)

    async def run(self, action: CandidateAction) -> Sequence[VerificationResult]:
        """Execute all verifiers in parallel for one candidate action."""
        tasks = [verifier.verify(action) for verifier in self._verifiers]
        return await asyncio.gather(*tasks)


class FirecrackerMicroVMVerifier:
    """Stub verifier representing microVM-based isolation backend."""

    name = "firecracker_microvm_stub"

    async def verify(self, action: CandidateAction) -> VerificationResult:
        if "DROP TABLE" in action.content.upper():
            return VerificationResult(
                verifier_name=self.name,
                passed=False,
                score=0.0,
                rationale="MicroVM policy blocked destructive database operation.",
            )
        return VerificationResult(
            verifier_name=self.name,
            passed=True,
            score=1.0,
            rationale="MicroVM execution stub completed successfully.",
        )


class Z3TheoremVerifier:
    """Stub verifier representing formal constraint checks."""

    name = "z3_theorem_stub"

    async def verify(self, action: CandidateAction) -> VerificationResult:
        banned = ("exec(", "eval(")
        unsafe = any(token in action.content for token in banned)
        return VerificationResult(
            verifier_name=self.name,
            passed=not unsafe,
            score=0.0 if unsafe else 0.9,
            rationale="Formal policy disallowed runtime code execution."
            if unsafe
            else "Formal policy constraints satisfied.",
        )


class ASTStaticAnalyzer:
    """Simple static analyzer backend for syntax-level security evidence."""

    name = "ast_static_analyzer"

    async def verify(self, action: CandidateAction) -> VerificationResult:
        payload = action.content.lower()
        suspicious = "--" in payload or " or 1=1" in payload
        return VerificationResult(
            verifier_name=self.name,
            passed=not suspicious,
            score=0.0 if suspicious else 0.95,
            rationale="Detected SQL injection signature."
            if suspicious
            else "No SQL injection signatures detected.",
        )
