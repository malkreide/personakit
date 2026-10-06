# Contributing

Thanks for considering a contribution. The project is small and opinionated: the format encodes a method (see [`docs/METHOD.md`](docs/METHOD.md)), so changes to the schema or the lint rules should name the method finding they rest on.

## Setup

```bash
pip install -e ".[dev]"
pip install -r requirements-lint.txt
pytest
ruff check .
ruff format --check .
python scripts/validate_repo.py .
```

## What is welcome

- Lint rules that catch a documented persona anti-pattern (reference the source in the PR)
- Additional renderers (keep them in `render.py`, keep output deterministic)
- Fixes to round-trip behaviour (`model.py`) – every fix needs a test in `tests/`
- Translations of the CLI messages, if kept consistent

## Ground rules

- Example personas must stay synthetic. No real interview data, no personal data, no internal documents of any organisation.
- Schema changes bump the `personakit` format version; add a note to `CHANGELOG.md` under `[Unreleased]`.
- Conventional commits: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
- Open a draft PR early; CI runs lint, format gate, tests and the repository structure check.
