# Contributing

Thanks for improving Entropy-RLAF.

## Development setup

```bash
pip install -e .[dev]
pre-commit install
pytest
```

## Plugin extension guidelines

1. Implement `verify(action)` with deterministic, fail-closed behavior.
2. For stateful plugins, use a `RollbackManager` implementation.
3. Return explicit rationale strings for auditability.
4. Add tests for both safe and unsafe trajectories.

## Coding standards

- Python 3.11+, strict typing.
- Keep functions small and explicit.
- Never trust model output without sanitization.
