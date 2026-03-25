"""Triangulated Process Reward Model (PRM) engine."""

from __future__ import annotations

import logging

from entropy_rlaf.core.models import StepEvaluation

logger = logging.getLogger(__name__)


class TriangulatedPRMEngine:
    """Combines environment, deterministic, and critic signals.

    Args:
        w1: Weight for environment diff.
        w2: Weight for deterministic policy compliance.
        w3: Weight for critic consensus.
    """

    def __init__(self, w1: float = 0.5, w2: float = 0.3, w3: float = 0.2) -> None:
        total = w1 + w2 + w3
        if abs(total - 1.0) > 1e-9:
            raise ValueError("w1 + w2 + w3 must equal 1.0")
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        self.critic_penalty = 0.0

    def process_reward(self, step: StepEvaluation) -> float:
        """Compute dense step reward.

        Formula: R_step = w1*Env_diff + w2*Det_policy + w3*Critic_consensus.
        """
        reward = (self.w1 * step.env_diff) + (self.w2 * step.det_policy) + (
            self.w3 * step.critic_consensus
        )
        return max(0.0, min(1.0, reward))

    def fidelity_score(self, env_outcome: float, critic_opinion: float) -> float:
        """Compute fidelity between environmental reality and critic opinion."""
        return max(0.0, min(1.0, 1.0 - abs(env_outcome - critic_opinion)))

    def meta_correct(self, fidelity: float) -> float:
        """Penalize critic trust when fidelity is too low.

        Returns:
            Updated critic penalty in [0.0, 1.0].
        """
        if fidelity < 0.5:
            self.critic_penalty = min(1.0, self.critic_penalty + (0.5 - fidelity))
            logger.warning(
                "Critic fidelity below threshold; applying meta-correction",
                extra={"fidelity": fidelity, "critic_penalty": self.critic_penalty},
            )
        return self.critic_penalty
