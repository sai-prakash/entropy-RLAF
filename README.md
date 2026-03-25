# Entropy-RLAF

Entropy-RLAF is an **environment-grounded alignment framework** for agentic LLM systems.
It triangulates:

1. Latent critic opinions,
2. Deterministic policy/static checks,
3. Empirical sandbox outcomes.

It will not emit preference pairs unless a chosen trajectory succeeds in isolated execution with dense process rewards.

## Why this matters

LLM-on-LLM evaluation can be poisoned, jailbroken, or simply wrong. Entropy-RLAF adds deterministic and empirical reality checks so training data is anchored to verifiable outcomes.

## Phase 1 MVP Scope

- Secure Python/SQL pipeline branch selection.
- Two-phase search (`FastPruner -> SlowExecutor`).
- Verification Mesh with pluggable verifiers.
- Triangulated PRM engine with fidelity-aware meta-correction.
- DPO dataset refinery producing TRL-compatible JSONL.
- Divergence telemetry summaries.

## Architecture

```mermaid
flowchart LR
  A[Candidate Branches] --> B[FastPruner\n(AST + static checks)]
  B --> C[SlowExecutor]
  C --> D[Verification Mesh\n(AST, SQLite tx, MicroVM stub, Z3 stub)]
  D --> E[Triangulated PRM Engine]
  E --> F[DPO Refinery]
  E --> G[Divergence Map + OTel]
```

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python demo.py
```

## Repository Layout

- `entropy_rlaf/core`: contracts + shared models
- `entropy_rlaf/plugins`: security and transactional plugins
- `entropy_rlaf/orchestrator`: fast/slow search orchestration
- `entropy_rlaf/verification_mesh`: mesh + verifier stubs
- `entropy_rlaf/engine`: process reward/fidelity logic
- `entropy_rlaf/refinery`: DPO JSONL generation
- `entropy_rlaf/telemetry`: divergence analytics
- `tests`: unit coverage for core flows

## Security stance

- Fail-closed static checks before expensive execution.
- Transaction rollback for stateful SQL verification.
- Multi-backend evidence for Byzantine tolerance.
- Fidelity-gated dataset export to reduce poisoned preferences.
