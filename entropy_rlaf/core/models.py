"""Core domain models shared across Entropy-RLAF modules."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CandidateAction(BaseModel):
    """Represents a candidate branch/action considered in search.

    Attributes:
        action_id: Stable ID for the candidate.
        language: Language for action payload, e.g. ``python`` or ``sql``.
        content: Action body.
        critic_score: Latent safety/quality score from critic ensemble.
    """

    action_id: str
    language: str
    content: str
    critic_score: float = Field(ge=0.0, le=1.0)


class VerificationResult(BaseModel):
    """Result for a verifier backend run."""

    verifier_name: str
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    rationale: str


class StepEvaluation(BaseModel):
    """Dense step-wise evaluation values used by PRM."""

    env_diff: float = Field(ge=0.0, le=1.0)
    det_policy: float = Field(ge=0.0, le=1.0)
    critic_consensus: float = Field(ge=0.0, le=1.0)


class SearchOutcome(BaseModel):
    """Final outcome of the orchestrated search run."""

    selected: CandidateAction
    ground_truth_score: float = Field(ge=0.0, le=1.0)
    fidelity_score: float = Field(ge=0.0, le=1.0)
    rationale: str
