# Agent Documentation for promptfoo-python

This document provides comprehensive guidance for AI agents and developers working on the promptfoo-python repository.

## Repository Overview

**promptfoo-python** is a lightweight Python wrapper that installs promptfoo via pip. It provides a convenience layer for Python users who want to install promptfoo through pip rather than npm.

- **Primary Purpose**: Enable pip-based installation of promptfoo for Python-centric environments
- **Implementation**: Thin wrapper that delegates to the official TypeScript promptfoo package
- **Requirements**: Python 3.10+ and Node.js 20+

### How It Works

1. User installs via `pip install promptfoo`
2. User runs `promptfoo eval` (or any promptfoo command)
3. The Python wrapper (`src/promptfoo/cli.py`):
   - Checks if Node.js/npx is available
   - Detects if promptfoo is globally installed
   - Falls back to `npx promptfoo@latest` if needed
   - Prevents recursive wrapper calls
   - Passes through all arguments and exit codes

### Key Architecture Components

- **Wrapper Shim**: `src/promptfoo/cli.py` - Main entry point that detects and delegates to promptfoo
- **Recursive Detection**: Uses `PROMPTFOO_PY_WRAPPER` env var to prevent wrapper loops
- **Platform Support**: Cross-platform with special handling for Windows `.cmd` and `.bat` wrappers

## Development Policies

### 1. Never Commit Directly to Main

**CRITICAL**: Always create a pull request. Never commit directly to the `main` branch.

```bash
# ✅ CORRECT
git checkout -b feat/my-feature
# make changes
git commit -m "feat: add new feature"
git push -u origin feat/my-feature
gh pr create

# ❌ WRONG
git checkout main
git commit -m "feat: add new feature"
git push  # This bypasses PR review!
```

### 2. Use Conventional Commits

All commits must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New feature (bumps minor version pre-1.0.0)
- `fix:` - Bug fix (bumps patch version)
- `docs:` - Documentation changes
- `chore:` - Maintenance tasks
- `ci:` - CI/CD changes
- `test:` - Test additions/modifications
- `refactor:` - Code refactoring
- `style:` - Code style changes (formatting, etc.)

**Why?** Release-please uses commit messages to automatically determine version bumps and generate changelogs.

```bash
# ✅ CORRECT
git commit -m "fix: correct wrapper shim detection on Windows"
git commit -m "feat: add support for custom npx registry"
git commit -m "docs: update installation instructions"

# ❌ WRONG
git commit -m "fixed a bug"
git commit -m "updates"
git commit -m "WIP"
```

### 3. PR Review Process

- All PRs require approval from `@promptfoo/engineering` (see `.github/CODEOWNERS`)
- PRs must pass all CI checks before merging
- CI includes: linting, type checking, tests on multiple Python versions and OSes

## Release Process

This repository uses **release-please** for automated releases.

### How Releases Work

1. **Push commits to `main`** (via merged PRs with conventional commits)
2. **Release-please analyzes commits** and creates/updates a release PR
3. **Review the release PR** - It will contain:
   - Updated `CHANGELOG.md`
   - Version bump in `pyproject.toml` and `.release-please-manifest.json`
   - Generated release notes
4. **Merge the release PR** - This triggers:
   - GitHub release creation with tag
   - Build workflow
   - Automatic PyPI publish via OIDC

### Version Bumping Strategy

We're currently pre-1.0.0, which uses special semver rules:

- `fix:` commits → **minor** version bump (0.2.0 → 0.3.0)
- `feat:` commits → **minor** version bump (0.2.0 → 0.3.0)
- `BREAKING CHANGE:` → **major** version bump (0.2.0 → 1.0.0)

This is configured via `bump-patch-for-minor-pre-major: true` in `release-please-config.json`.

### Release Configuration Files

- **`release-please-config.json`**: Main configuration for release-please
  - Defines release type (python)
  - Specifies extra files to update (pyproject.toml)
  - Sets versioning behavior
- **`.release-please-manifest.json`**: Tracks the last released version
  - Format: `{ ".": "0.2.0" }`
  - Updated automatically by release-please

### Manual Release Steps (If Needed)

If you need to manually trigger a release or fix release-please:

1. Ensure `.release-please-manifest.json` has the correct last version
2. Push to `main` to trigger release-please workflow
3. Check Actions tab for release-please PR creation
4. If issues occur, check workflow logs in `.github/workflows/release-please.yml`

## CI/CD Pipelines

### Test Workflow (`.github/workflows/test.yml`)

Runs on every PR and push to main:

- **Lint**: Ruff linting (`uv run ruff check src/`)
- **Format Check**: Ruff formatting (`uv run ruff format --check src/`)
- **Type Check**: Both mypy and pyright in strict mode (run in parallel via matrix)
  - `uv run mypy src/promptfoo/` - Standard Python type checker
  - `uv run pyright src/promptfoo/` - Microsoft's type checker for additional coverage
- **Unit Tests**: Fast tests with mocked dependencies (`uv run pytest -m 'not smoke'`)
- **Smoke Tests**: Integration tests against real CLI (`uv run pytest tests/smoke/`)
- **Build**: Package build validation

Tests run on multiple Python versions (3.10, 3.13) and OSes (Ubuntu, Windows).

### Release Workflow (`.github/workflows/release-please.yml`)

Triggered on push to main:

1. **release-please job**: Creates/updates release PR
2. **build job**: (on release PR merge)
   - Builds Python package with `uv build`
   - Verifies package version matches release
   - Uploads build artifacts
3. **publish-pypi job**: (on release PR merge)
   - Downloads build artifacts
   - Publishes to PyPI using OIDC (no tokens!)

### OIDC Publishing to PyPI

We use **OpenID Connect (OIDC)** for secure, credential-free PyPI publishing:

- **No API tokens stored** in GitHub secrets
- **Environment**: `pypi` (configured in workflow)
- **Permissions**: `id-token: write` and `contents: read`
- **PyPI Trusted Publisher**: Configured at https://pypi.org/manage/project/promptfoo/settings/publishing/

**Configuration**:
- Repository: `promptfoo/promptfoo-python`
- Workflow: `release-please.yml`
- Environment: `pypi`

## Code Standards

### Python Version Support

- **Minimum**: Python 3.10
- **Tested**: Python 3.10 and 3.13
- **Target**: `py310` for Ruff and mypy

### Code Quality Tools

- **Linter**: Ruff with extended rule sets (isort, pycodestyle, flake8-bugbear, etc.)
- **Formatter**: Ruff (replaces Black)
- **Type Checkers**: Both **mypy** and **pyright** in strict mode for comprehensive coverage
  - **mypy**: The standard Python type checker with strict mode and additional error codes
  - **pyright**: Microsoft's fast type checker that catches different issues than mypy
- **Package Manager**: uv (Astral's fast Python package manager)

### Running Checks Locally

```bash
# Install dependencies
uv sync --extra dev

# Run linter
uv run ruff check src/

# Auto-fix linting issues
uv run ruff check src/ --fix

# Format code
uv run ruff format src/

# Type check with mypy (strict mode)
uv run mypy src/promptfoo/

# Type check with pyright (strict mode)
uv run pyright src/promptfoo/

# Run both type checkers (recommended before PR)
uv run mypy src/promptfoo/ && uv run pyright src/promptfoo/

# Run tests
uv run pytest
```

### Code Style Guidelines

- **Line length**: 120 characters
- **Quote style**: Double quotes
- **Imports**: Sorted with isort rules
- **Type hints**: Required for all function signatures
- **Docstrings**: Required for public functions and modules

## Testing Strategy

### Test Structure

Tests are organized in the `tests/` directory:

```
tests/
├── __init__.py
├── test_cli.py              # Unit tests for CLI wrapper logic
├── test_environment.py      # Unit tests for environment detection
├── test_instructions.py     # Unit tests for installation instructions
└── smoke/
    ├── __init__.py
    ├── README.md            # Smoke test documentation
    ├── test_smoke.py        # Integration tests against real CLI
    └── fixtures/
        └── configs/         # YAML configs for smoke tests
            ├── basic.yaml
            ├── assertions.yaml
            └── failing-assertion.yaml
```

### Test Types

**Unit Tests** (`tests/test_*.py`):
- Fast, isolated tests for individual functions
- Mock external dependencies
- Run on every PR

**Smoke Tests** (`tests/smoke/`):
- Integration tests that run the actual CLI via subprocess
- Use the `echo` provider (no external API dependencies)
- Test the full Python → Node.js integration
- Slower but verify end-to-end functionality
- Marked with `@pytest.mark.smoke`

### Test Matrix

CI tests across:
- **Operating Systems**: Ubuntu, Windows (macOS temporarily excluded due to runner constraints)
- **Python Versions**: 3.10 (min), 3.13 (max)
- **Scenarios**: Global promptfoo install vs. npx fallback

### Running Tests

```bash
# Install dependencies with dev extras
uv sync --extra dev

# Run all tests (unit + smoke)
uv run pytest

# Run only unit tests (fast)
uv run pytest -m 'not smoke'

# Run only smoke tests (slow, requires Node.js)
uv run pytest tests/smoke/

# Run with coverage
uv run pytest --cov=src/promptfoo

# Run specific test class
uv run pytest tests/test_cli.py::TestMainFunction

# Run specific test
uv run pytest tests/smoke/test_smoke.py::TestEvalCommand::test_basic_eval
```

### Smoke Test Details

Smoke tests verify critical CLI functionality:
- **Basic CLI**: `--version`, `--help`, unknown commands, missing files
- **Eval Command**: Output formats (JSON, YAML, CSV), flags (`--repeat`, `--verbose`)
- **Exit Codes**: 0 for success, 100 for assertion failures, 1 for errors
- **Echo Provider**: Variable substitution, multiple variables
- **Assertions**: `contains`, `icontains`, failing assertions

The smoke tests use a 120-second timeout to accommodate the first `npx` call which downloads promptfoo.

## Security Practices

### 1. No Credentials in Repository

- **Never** commit API tokens, passwords, or secrets
- PyPI publishing uses OIDC (no tokens needed)
- GitHub Actions secrets are NOT required for publishing

### 2. Dependency Management

- Dependencies are minimal (only dev dependencies)
- Regular updates via Renovate bot
- Pin Python and Node.js versions in CI

### 3. Supply Chain Security

- OIDC publishing prevents token compromise
- Workflow permissions are minimal (`contents: read`, `id-token: write` only when needed)
- Artifacts are verified before publishing

## Common Development Tasks

### Adding a New Feature

```bash
# 1. Create branch from main
git checkout main
git pull
git checkout -b feat/my-feature-name

# 2. Make changes
# ... edit code ...

# 3. Run quality checks
uv run ruff check src/ --fix
uv run ruff format src/
uv run mypy src/promptfoo/
uv run pyright src/promptfoo/
uv run pytest

# 4. Commit with conventional commit message
git add .
git commit -m "feat: add support for custom promptfoo version"

# 5. Push and create PR
git push -u origin feat/my-feature-name
gh pr create --title "feat: add support for custom promptfoo version" --body "Description of changes"
```

### Fixing a Bug

```bash
# 1. Create branch from main
git checkout main
git pull
git checkout -b fix/bug-description

# 2. Make changes and add test
# ... edit code ...
# ... add test case ...

# 3. Run quality checks
uv run ruff check src/ --fix
uv run ruff format src/
uv run mypy src/promptfoo/
uv run pyright src/promptfoo/
uv run pytest

# 4. Commit with conventional commit message
git add .
git commit -m "fix: correct wrapper shim detection on Windows venv"

# 5. Push and create PR
git push -u origin fix/bug-description
gh pr create --title "fix: correct wrapper shim detection on Windows venv" --body "Fixes #123"
```

### Updating Dependencies

Dependencies are managed by Renovate bot, which automatically creates PRs for updates.

To manually update:

```bash
# Update all dependencies
uv sync --upgrade

# Update specific dependency
uv add --dev ruff@latest

# Commit changes
git add pyproject.toml uv.lock  # or equivalent lock file
git commit -m "chore(deps): update ruff to vX.Y.Z"
```

### Creating a Release (Automated)

Releases are fully automated via release-please:

1. Merge PRs with conventional commits to `main`
2. Release-please creates a release PR
3. Review the release PR (check CHANGELOG, version bump)
4. Merge the release PR
5. GitHub release is created automatically
6. Package is published to PyPI automatically

### Troubleshooting Release Issues

If release-please fails:

1. Check workflow logs: https://github.com/promptfoo/promptfoo-python/actions
2. Verify `release-please-config.json` is valid JSON
3. Verify `.release-please-manifest.json` has correct version
4. Ensure commits follow conventional commit format
5. Check PyPI trusted publisher configuration

## Project Structure

```
promptfoo-python/
├── .github/
│   ├── CODEOWNERS              # Code review assignments
│   └── workflows/
│       ├── release-please.yml  # Release automation
│       └── test.yml            # CI tests
├── src/
│   └── promptfoo/
│       ├── __init__.py         # Package exports
│       ├── cli.py              # Main wrapper implementation
│       ├── environment.py      # Environment detection
│       └── instructions.py     # Node.js installation instructions
├── tests/
│   ├── test_cli.py             # Unit tests for CLI
│   ├── test_environment.py     # Unit tests for environment detection
│   ├── test_instructions.py    # Unit tests for instructions
│   └── smoke/
│       ├── test_smoke.py       # Integration smoke tests
│       └── fixtures/configs/   # Test configuration files
├── AGENTS.md                   # This file (agent documentation)
├── CHANGELOG.md                # Auto-generated by release-please
├── CLAUDE.md                   # Points to AGENTS.md
├── LICENSE                     # MIT License
├── README.md                   # User-facing documentation
├── pyproject.toml              # Package configuration
├── release-please-config.json  # Release-please configuration
└── .release-please-manifest.json # Release version tracking
```

## Key Contacts

- **Code Owners**: `@promptfoo/engineering`
- **Main Repository**: https://github.com/promptfoo/promptfoo (TypeScript)
- **PyPI Package**: https://pypi.org/project/promptfoo/

## Additional Resources

- [promptfoo Documentation](https://www.promptfoo.dev/docs)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Release Please Documentation](https://github.com/googleapis/release-please)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [uv Documentation](https://github.com/astral-sh/uv)

## FAQ

### Q: Why can't I commit directly to main?

**A**: All changes must go through PR review to ensure:
- Code quality standards are met
- Tests pass on all platforms
- Changes are reviewed by maintainers
- Conventional commits are enforced
- CI/CD pipelines validate changes

### Q: My commit message doesn't follow conventional commits. Can I fix it?

**A**: Yes, before pushing:

```bash
# Amend the last commit message
git commit --amend -m "fix: correct commit message"

# Force push to your branch (only if not yet merged!)
git push --force
```

### Q: How do I test my changes on Windows if I'm on macOS?

**A**: Push to your PR branch and let GitHub Actions run the Windows tests. You can also use:
- WSL (Windows Subsystem for Linux)
- A Windows VM
- GitHub Codespaces with Windows

### Q: The release-please PR shows the wrong version. How do I fix it?

**A**: The version bump is determined by commit messages:
- Check all commits since the last release
- Ensure they follow conventional commits
- `fix:` commits bump minor version (pre-1.0.0)
- `feat:` commits bump minor version (pre-1.0.0)
- If the version is still wrong, you may need to manually adjust `.release-please-manifest.json` in a new PR

### Q: How do I manually publish to PyPI?

**A**: You shouldn't need to! The OIDC workflow handles this automatically. If you absolutely must:

1. Build the package: `uv build`
2. Contact a maintainer with PyPI access
3. They can manually upload via `twine` (but this defeats the purpose of OIDC)

### Q: Can AI agents merge their own PRs?

**A**: No. All PRs require human review and approval from `@promptfoo/engineering` before merging.

---

**Last Updated**: 2026-01-11
**Maintained By**: @promptfoo/engineering
