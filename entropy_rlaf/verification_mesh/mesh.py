"""Verification mesh with pluggable backends.

The mesh aggregates deterministic and environmental checks under an isolated
execution contract to prevent state bleed between branches.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from entropy_rlaf.core.interfaces import Verifier
from entropy_rlaf.core.models import VerificationResult


@dataclass
class VerificationMesh:
    """Runs a list of verifiers concurrently and returns all results."""

    verifiers: list[Verifier]

    async def verify_all(self, payload: str) -> list[VerificationResult]:
        """Execute every verifier asynchronously for the same payload."""
        tasks = [verifier.verify(payload) for verifier in self.verifiers]
        return await asyncio.gather(*tasks)


class FirecrackerMicroVMVerifier:
    """Stub microVM verifier for future hardened runtime integration."""

    name = "firecracker_microvm_stub"

    async def verify(self, payload: str) -> VerificationResult:
        return VerificationResult(
            verifier_name=self.name,
            passed=True,
            score=1.0,
            rationale="Stubbed: assumes isolated microVM execution succeeded.",
        )


class Z3TheoremVerifier:
    """Stub formal verifier for future SMT constraints."""

    name = "z3_theorem_stub"

    async def verify(self, payload: str) -> VerificationResult:
        return VerificationResult(
            verifier_name=self.name,
            passed=True,
            score=0.9,
            rationale="Stubbed: formal constraints likely satisfied.",
        )


class ASTStaticAnalyzer:
    """Simple AST static analyzer used as deterministic mesh member."""

    name = "ast_static_analyzer"

    async def verify(self, payload: str) -> VerificationResult:
        unsafe_tokens = ("exec(", "eval(", "os.system", "subprocess")
        matched = [token for token in unsafe_tokens if token in payload]
        passed = not matched
        return VerificationResult(
            verifier_name=self.name,
            passed=passed,
            score=1.0 if passed else 0.0,
            rationale="No unsafe static patterns found." if passed else f"Unsafe token(s): {matched}",
        )
