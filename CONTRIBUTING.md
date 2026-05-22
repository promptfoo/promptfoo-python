# Contributing

## Contributing to promptfoo

For contributions to promptfoo itself — new features, providers, bug fixes, and documentation — please go to the main project:

**[github.com/promptfoo/promptfoo](https://github.com/promptfoo/promptfoo)**

## Contributing to this pip wrapper

This repository is only the thin Python shim that lets people install promptfoo via `pip`. Issues here should be about:

- Installation failures via pip
- Node.js detection or environment problems
- Python shim behaviour on Windows/macOS/Linux

### Setup

Requires Python 3.10+, Node.js 20+, and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/promptfoo/promptfoo-python.git
cd promptfoo-python
uv sync --extra dev
uv run pytest -m 'not smoke'   # fast unit tests
uv run pytest                  # all tests (requires Node.js)
```

### Submitting changes

1. Branch from `main`
2. Follow [Conventional Commits](https://www.conventionalcommits.org/) — release-please uses commit messages to version and changelog automatically
3. Run checks before opening a PR:
   ```bash
   uv run ruff check src/ --fix && uv run ruff format src/
   uv run mypy src/promptfoo/ && uv run pyright src/promptfoo/
   uv run pytest -m 'not smoke'
   ```
4. Open a pull request against `main`
