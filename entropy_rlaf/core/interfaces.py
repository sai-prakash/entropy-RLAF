"""Core abstract interfaces for Entropy-RLAF components."""

from __future__ import annotations

from abc import ABC, abstractmethod

from entropy_rlaf.core.models import PreferencePair, StepReward, VerificationResult


class Verifier(ABC):
    """Abstract deterministic or environmental verifier."""

    name: str

    @abstractmethod
    async def verify(self, payload: str) -> VerificationResult:
        """Run verification against payload in isolated context."""


class RollbackManager(ABC):
    """Interface for state rollback primitives."""

    @abstractmethod
    async def begin(self) -> None:
        """Begin isolated transactional scope."""

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback state to pristine point."""


class RewardEngine(ABC):
    """Dense process reward and fidelity scorer."""

    @abstractmethod
    def score_step(self, step_index: int, env_diff: float, det_policy: float, critic_consensus: float) -> StepReward:
        """Calculate one dense process reward value."""

    @abstractmethod
    def fidelity_score(self, env_outcome: float, critic_opinion: float) -> float:
        """Compute latent-vs-literal alignment fidelity."""


class DatasetFactory(ABC):
    """Builds and persists preference datasets."""

    @abstractmethod
    def build_pair(self, prompt: str, chosen: str, rejected: str, chosen_score: float, rejected_score: float, fidelity_score: float, environmental_rationale: str) -> PreferencePair:
        """Create a preference pair object."""

    @abstractmethod
    def write_jsonl(self, pairs: list[PreferencePair], output_path: str) -> None:
        """Persist pairs in JSONL format."""
