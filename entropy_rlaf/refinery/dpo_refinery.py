"""DPO dataset refinery for HuggingFace TRL-compatible JSONL output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from entropy_rlaf.core.models import CandidateAction


class DPODatasetRefinery:
    """Transforms verified trajectories into preference pairs.

    Low-fidelity samples are discarded to reduce model-collapse risk.
    """

    def __init__(self, min_fidelity: float = 0.5) -> None:
        self.min_fidelity = min_fidelity

    def build_record(
        self,
        prompt: str,
        chosen: CandidateAction,
        rejected: CandidateAction,
        rationale: str,
        fidelity: float,
    ) -> dict[str, str] | None:
        if fidelity < self.min_fidelity:
            return None
        return {
            "prompt": prompt,
            "chosen": chosen.content,
            "rejected": f"{rejected.content}\n\n[environment_rationale] {rationale}",
        }

    def write_jsonl(self, path: Path, records: Iterable[dict[str, str]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record) + "\n")
