"""DPO dataset refinery producing HuggingFace TRL-compatible JSONL."""

from __future__ import annotations

import json
from dataclasses import dataclass

from entropy_rlaf.core.interfaces import DatasetFactory
from entropy_rlaf.core.models import PreferencePair


@dataclass
class DPODatasetRefinery(DatasetFactory):
    """Filters and serializes high-fidelity preference pairs."""

    fidelity_threshold: float = 0.6

    def build_pair(
        self,
        prompt: str,
        chosen: str,
        rejected: str,
        chosen_score: float,
        rejected_score: float,
        fidelity_score: float,
        environmental_rationale: str,
    ) -> PreferencePair:
        rejected_with_rationale = f"{rejected}\n\n[Environmental Rationale]\n{environmental_rationale}"
        return PreferencePair(
            prompt=prompt,
            chosen=chosen,
            rejected=rejected_with_rationale,
            chosen_score=chosen_score,
            rejected_score=rejected_score,
            fidelity_score=fidelity_score,
            environmental_rationale=environmental_rationale,
        )

    def filter_pairs(self, pairs: list[PreferencePair]) -> list[PreferencePair]:
        """Drop low-fidelity data to avoid preference poisoning."""
        return [pair for pair in pairs if pair.fidelity_score >= self.fidelity_threshold]

    def write_jsonl(self, pairs: list[PreferencePair], output_path: str) -> None:
        rows = self.filter_pairs(pairs)
        with open(output_path, "w", encoding="utf-8") as file:
            for pair in rows:
                file.write(json.dumps(pair.model_dump()) + "\n")
