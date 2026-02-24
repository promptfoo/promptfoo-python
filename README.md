# promptfoo Python wrapper

<p align="center">
  <a href="https://pypi.org/project/promptfoo/"><img src="https://badge.fury.io/py/promptfoo.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/promptfoo/"><img src="https://img.shields.io/pypi/pyversions/promptfoo.svg" alt="Python versions"></a>
  <a href="https://npmjs.com/package/promptfoo"><img src="https://img.shields.io/npm/dm/promptfoo" alt="npm downloads"></a>
  <a href="https://github.com/promptfoo/promptfoo/blob/main/LICENSE"><img src="https://img.shields.io/github/license/promptfoo/promptfoo" alt="MIT license"></a>
  <a href="https://discord.gg/promptfoo"><img src="https://github.com/user-attachments/assets/2092591a-ccc5-42a7-aeb6-24a2808950fd" alt="Discord"></a>
</p>

> **This is a thin pip wrapper for [promptfoo](https://github.com/promptfoo/promptfoo).**
> It exists solely to let Python-centric environments install promptfoo via `pip`.
> All features, documentation, and issues belong to the [main project](https://github.com/promptfoo/promptfoo).

---

## What is promptfoo?

[promptfoo](https://github.com/promptfoo/promptfoo) is a developer-friendly tool for testing and evaluating LLM applications — prompt evals, red teaming, and vulnerability scanning.

- **Test your prompts and models** with [automated evaluations](https://www.promptfoo.dev/docs/getting-started/)
- **Secure your LLM apps** with [red teaming](https://www.promptfoo.dev/docs/red-team/) and vulnerability scanning
- **Compare models** side-by-side (OpenAI, Anthropic, Azure, Bedrock, Ollama, and [more](https://www.promptfoo.dev/docs/providers/))
- **Automate checks** in [CI/CD](https://www.promptfoo.dev/docs/integrations/ci-cd/)

For full documentation, see **[promptfoo.dev/docs](https://www.promptfoo.dev/docs/)** or the **[main repository](https://github.com/promptfoo/promptfoo)**.

## Why use this pip package?

promptfoo is a Node.js tool. Most users should install it directly:

```bash
npm install -g promptfoo
# or
npx promptfoo@latest init
```

Use this pip wrapper when you:

- Need to install via `pip` for Python-only CI/CD environments
- Want to manage promptfoo alongside Python dependencies (poetry, pip, pipenv)
- Work in environments where pip packages are easier to approve than npm

> **Note:** Node.js 20+ is still required regardless of how you install promptfoo. This wrapper installs the Python shim; the actual promptfoo logic runs via Node.js.

## Installation

### Requirements

- **Python 3.9+**
- **Node.js 20+**

### Install

```bash
pip install promptfoo
```

## Quick Start

```bash
# Initialize a project
promptfoo init

# Run your first evaluation
promptfoo eval
```

See [Getting Started](https://www.promptfoo.dev/docs/getting-started/) (evals) or [Red Teaming](https://www.promptfoo.dev/docs/red-team/) (vulnerability scanning) for detailed usage.

## Python-Specific Usage

### With poetry

```bash
poetry add --group dev promptfoo
poetry run promptfoo eval
```

### With requirements.txt

```bash
echo "promptfoo" >> requirements.txt
pip install -r requirements.txt
promptfoo eval
```

### In CI/CD (GitHub Actions)

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: "20"

- name: Install promptfoo
  run: pip install promptfoo

- name: Run evals
  run: promptfoo eval
```

## How This Wrapper Works

1. Checks if Node.js is installed (prints instructions if not)
2. Looks for a globally installed `promptfoo` binary and uses it if found
3. Falls back to `npx promptfoo@latest` if no global install is found
4. Passes through all arguments, environment variables, and exit codes

The actual promptfoo logic runs via the [official npm package](https://www.npmjs.com/package/promptfoo).

## Configuration

### Version Pinning

By default, the wrapper runs `npx promptfoo@latest`. To pin a specific version:

```bash
export PROMPTFOO_VERSION=0.95.0
promptfoo --version
```

Or install a specific version globally (fastest option — skips npx entirely):

```bash
npm install -g promptfoo@0.95.0
```

### Telemetry

This wrapper collects anonymous usage telemetry (which execution path was used: global install vs. npx fallback) to help improve the package. This mirrors the telemetry in the main promptfoo project.

**What is collected:**
- A random anonymous user ID (stored in `~/.promptfoo/promptfoo.yaml`)
- Wrapper version and Python version
- Whether you're running in CI
- Your email address **only if** you have previously logged into promptfoo and it is stored in `~/.promptfoo/promptfoo.yaml`

**To disable telemetry:**

```bash
export PROMPTFOO_DISABLE_TELEMETRY=1
```

Telemetry data is sent to PostHog. The PostHog API key in this project is a write-only client-side key and does not grant any administrative access.

## Troubleshooting

### "ERROR: promptfoo requires Node.js"

Install Node.js:

- **macOS**: `brew install node`
- **Ubuntu/Debian**: `sudo apt install nodejs npm`
- **Windows**: Download from [nodejs.org](https://nodejs.org/)
- **Any OS**: Use [nvm](https://github.com/nvm-sh/nvm)

### Slow First Run

The first time you run `promptfoo`, npx downloads the latest version from npm (~50MB). Subsequent runs use the cached version. To skip the download entirely, install globally:

```bash
npm install -g promptfoo
```

## Documentation & Support

All feature docs, tutorials, and provider references live in the **main project**:

- [Full Documentation](https://www.promptfoo.dev/docs/)
- [Getting Started](https://www.promptfoo.dev/docs/getting-started/)
- [Red Teaming Guide](https://www.promptfoo.dev/docs/red-team/)
- [CLI Reference](https://www.promptfoo.dev/docs/usage/command-line/)
- [Supported Models](https://www.promptfoo.dev/docs/providers/)
- [Main GitHub Repository](https://github.com/promptfoo/promptfoo)

For help, join the [Discord community](https://discord.gg/promptfoo).

## Contributing

**For promptfoo features, bugs, and documentation:** open issues and PRs in [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo).

**For pip wrapper issues** (installation problems, Python shim bugs): open issues here. See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.

## License

MIT — same as [promptfoo](https://github.com/promptfoo/promptfoo/blob/main/LICENSE).
