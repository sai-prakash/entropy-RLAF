"""Abstract interfaces for core components.

The framework intentionally separates deterministic checks, environmental execution,
and dataset creation so that each policy and runtime backend can evolve independently.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from entropy_rlaf.core.models import CandidateAction, StepEvaluation, VerificationResult


class Verifier(ABC):
    """Base verifier interface for deterministic and environmental checks."""

    name: str

    @abstractmethod
    async def verify(self, action: CandidateAction) -> VerificationResult:
        """Verify a candidate action asynchronously in an isolated context."""


class RollbackManager(ABC):
    """State rollback interface for stateful verifiers."""

    @abstractmethod
    def begin(self) -> None:
        """Begin a transactional checkpoint."""

    @abstractmethod
    def rollback(self) -> None:
        """Rollback to checkpoint."""


class RewardEngine(ABC):
    """Computes process rewards and fidelity from step evaluations."""

    @abstractmethod
    def process_reward(self, step: StepEvaluation) -> float:
        """Compute dense process reward for an intermediate step."""

    @abstractmethod
    def fidelity_score(self, env_outcome: float, critic_opinion: float) -> float:
        """Compute latent-vs-literal agreement."""


class DatasetFactory(ABC):
    """Creates preference records from validated trajectories."""

    @abstractmethod
    def build_record(
        self,
        prompt: str,
        chosen: CandidateAction,
        rejected: CandidateAction,
        rationale: str,
    ) -> dict[str, str]:
        """Return a serializable preference record."""


class VerificationMesh(ABC):
    """Composable asynchronous verification layer."""

    @abstractmethod
    async def run(self, action: CandidateAction) -> Sequence[VerificationResult]:
        """Run all backends and return verification evidence."""
