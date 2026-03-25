# Security Policy

## Supported Versions

Entropy-RLAF is pre-1.0; only latest main branch is supported.

## Reporting a Vulnerability

Please report vulnerabilities privately to project maintainers and include:

- Reproduction steps,
- Impact assessment,
- Suggested mitigation if available.

Do not publicly disclose zero-days before maintainers have time to patch.

## Design-level mitigations

- AST sanitization prior to evaluator ingestion,
- Ensemble-style verification evidence,
- Transactional rollback for state isolation,
- Fidelity gating to prevent low-trust preference pairs.
