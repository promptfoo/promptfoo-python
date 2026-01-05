# promptfoo - Python wrapper

[![PyPI version](https://badge.fury.io/py/promptfoo.svg)](https://pypi.org/project/promptfoo/)
[![Python versions](https://img.shields.io/pypi/pyversions/promptfoo.svg)](https://pypi.org/project/promptfoo/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python wrapper for [promptfoo](https://www.promptfoo.dev) - the LLM testing, red teaming, and security evaluation framework.

## What is promptfoo?

Promptfoo is a TypeScript/Node.js tool for:

- **LLM Testing & Evaluation** - Compare prompts, models, and RAG systems
- **Red Teaming** - Automated vulnerability testing and adversarial attacks
- **Security Scanning** - Detect prompt injection, jailbreaks, and data leaks
- **CI/CD Integration** - Add automated AI security checks to your pipeline

## Installation

### Requirements

- **Python 3.9+** (for this wrapper)
- **Node.js 18+** (to run the actual promptfoo CLI)

### Install from PyPI

```bash
pip install promptfoo
```

This Python package is a lightweight wrapper that calls the official promptfoo CLI via `npx`.

### Verify Installation

```bash
# Check that Node.js is installed
node --version

# Run promptfoo
promptfoo --version
```

## Quick Start

```bash
# Initialize a new project
promptfoo init

# Run an evaluation
promptfoo eval

# Start red teaming
promptfoo redteam run

# View results in the web UI
promptfoo view
```

## Usage

The `promptfoo` command behaves identically to the official Node.js CLI. All arguments are passed through:

```bash
# Get help
promptfoo --help

# Run tests
promptfoo eval

# Generate red team attacks
promptfoo redteam generate

# Run vulnerability scans
promptfoo redteam run

# View results
promptfoo view

# Export results
promptfoo export --format json --output results.json
```

## How It Works

This Python package is a thin wrapper that:

1. Checks if Node.js and npx are installed
2. Executes `npx promptfoo@latest <your-args>`
3. Passes through all arguments and environment variables
4. Returns the same exit code

The actual promptfoo logic runs via the TypeScript package from npm.

## Why a Python Wrapper?

Many Python developers prefer `pip install` over `npm install` for tools in their workflow. This wrapper allows you to:

- Install promptfoo alongside your Python dependencies
- Use it in Python-based CI/CD pipelines
- Manage it with standard Python tooling (pip, poetry, pipenv, etc.)

## Documentation

- **Website**: https://www.promptfoo.dev
- **Docs**: https://www.promptfoo.dev/docs
- **GitHub**: https://github.com/promptfoo/promptfoo
- **Discord**: https://discord.gg/promptfoo

## Troubleshooting

### "ERROR: promptfoo requires Node.js"

The wrapper needs Node.js to run. Install it:

- **macOS**: `brew install node`
- **Ubuntu/Debian**: `sudo apt install nodejs npm`
- **Windows**: Download from https://nodejs.org/
- **Any OS**: Use [nvm](https://github.com/nvm-sh/nvm)

### Slow First Run

The first time you run `promptfoo`, npx will download the latest version from npm. Subsequent runs are fast.

### Version Pinning

By default, this wrapper uses `npx promptfoo@latest`. To pin a specific version, set the `PROMPTFOO_VERSION` environment variable:

```bash
export PROMPTFOO_VERSION=0.95.0
promptfoo --version
```

## Development

This is a minimal wrapper - the actual promptfoo source code lives in the main TypeScript repository.

## License

MIT License - Same as promptfoo
