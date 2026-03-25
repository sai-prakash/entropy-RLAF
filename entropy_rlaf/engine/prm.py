"""Triangulated process reward model engine."""

from __future__ import annotations

from dataclasses import dataclass

from entropy_rlaf.core.interfaces import RewardEngine
from entropy_rlaf.core.models import StepReward


@dataclass
class TriangulatedPRMEngine(RewardEngine):
    """Calculates dense process rewards and critic-fidelity correction."""

    w1: float = 0.4
    w2: float = 0.4
    w3: float = 0.2
    critic_penalty: float = 0.0

    def score_step(
        self,
        step_index: int,
        env_diff: float,
        det_policy: float,
        critic_consensus: float,
    ) -> StepReward:
        value = (self.w1 * env_diff) + (self.w2 * det_policy) + (self.w3 * critic_consensus)
        return StepReward(
            step_index=step_index,
            value=value,
            env_diff=env_diff,
            det_policy=det_policy,
            critic_consensus=critic_consensus,
        )

    def fidelity_score(self, env_outcome: float, critic_opinion: float) -> float:
        return 1.0 - abs(env_outcome - critic_opinion)

    def apply_meta_correction(self, fidelity: float) -> bool:
        """Penalize critic influence when fidelity drops below threshold."""
        if fidelity < 0.5:
            self.critic_penalty += 0.1
            self.w3 = max(0.05, self.w3 - 0.05)
            return True
        return False
