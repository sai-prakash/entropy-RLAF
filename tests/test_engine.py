from entropy_rlaf.engine.prm import TriangulatedPRMEngine


def test_fidelity_and_meta_correction() -> None:
    engine = TriangulatedPRMEngine()
    fidelity = engine.fidelity_score(env_outcome=0.0, critic_opinion=1.0)
    assert fidelity == 0.0
    corrected = engine.apply_meta_correction(fidelity)
    assert corrected
    assert engine.w3 < 0.2
