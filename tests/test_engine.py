from entropy_rlaf.core.models import StepEvaluation
from entropy_rlaf.engine.prm_engine import TriangulatedPRMEngine


def test_prm_reward_and_meta_correction() -> None:
    engine = TriangulatedPRMEngine()
    reward = engine.process_reward(StepEvaluation(env_diff=1.0, det_policy=1.0, critic_consensus=0.5))
    assert 0.0 <= reward <= 1.0

    fidelity = engine.fidelity_score(env_outcome=0.0, critic_opinion=1.0)
    assert fidelity == 0.0

    penalty = engine.meta_correct(fidelity)
    assert penalty > 0.0
