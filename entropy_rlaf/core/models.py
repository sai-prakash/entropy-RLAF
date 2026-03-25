"""Shared typed models used across Entropy-RLAF.

Uses Pydantic v2 when available, with a dataclass fallback for offline/minimal
execution environments.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

try:
    from pydantic import BaseModel, Field
except ModuleNotFoundError:  # pragma: no cover - fallback for constrained runtime
    BaseModel = object  # type: ignore[assignment,misc]

    def Field(*, default: Any = None, default_factory: Any = None, **_: Any) -> Any:
        if default_factory is not None:
            return default_factory()
        return default


if BaseModel is object:

    @dataclass
    class CandidateAction:
        candidate_id: str
        code: str
        sql: str | None = None
        critic_score: float = 0.0

    @dataclass
    class VerificationResult:
        verifier_name: str
        passed: bool
        score: float
        rationale: str
        metadata: dict[str, str] = field(default_factory=dict)

    @dataclass
    class StepReward:
        step_index: int
        value: float
        env_diff: float
        det_policy: float
        critic_consensus: float

    @dataclass
    class SearchNodeResult:
        candidate: CandidateAction
        verifier_results: list[VerificationResult]
        ground_truth_score: float
        env_outcome: float
        deterministic_score: float
        critic_consensus: float
        fidelity_score: float
        was_meta_corrected: bool = False

    @dataclass
    class PreferencePair:
        prompt: str
        chosen: str
        rejected: str
        chosen_score: float
        rejected_score: float
        fidelity_score: float
        environmental_rationale: str

        def model_dump(self) -> dict[str, Any]:
            return asdict(self)

else:

    class CandidateAction(BaseModel):
        candidate_id: str
        code: str
        sql: str | None = None
        critic_score: float = Field(ge=0.0, le=1.0)

    class VerificationResult(BaseModel):
        verifier_name: str
        passed: bool
        score: float = Field(ge=0.0, le=1.0)
        rationale: str
        metadata: dict[str, str] = Field(default_factory=dict)

    class StepReward(BaseModel):
        step_index: int
        value: float
        env_diff: float
        det_policy: float
        critic_consensus: float

    class SearchNodeResult(BaseModel):
        candidate: CandidateAction
        verifier_results: list[VerificationResult]
        ground_truth_score: float
        env_outcome: float
        deterministic_score: float
        critic_consensus: float
        fidelity_score: float
        was_meta_corrected: bool = False

    class PreferencePair(BaseModel):
        prompt: str
        chosen: str
        rejected: str
        chosen_score: float
        rejected_score: float
        fidelity_score: float
        environmental_rationale: str
