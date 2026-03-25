# Contributing

Thanks for contributing to Entropy-RLAF.

## Development setup

```bash
pip install -e .[dev]
pre-commit install
pytest
```

## Plugin extension guidelines

1. Implement the `Verifier` interface (`async verify(payload: str) -> VerificationResult`).
2. Ensure branch isolation (transaction rollback or copy-on-write environment semantics).
3. Return explicit rationale for every failure mode.
4. Add targeted unit tests for adversarial cases.
5. Register verifier in `VerificationMesh` usage sites.

## Quality bar

- Type checks should pass with strict mypy.
- Format with black and lint with ruff.
- Keep functions small and explicit.
