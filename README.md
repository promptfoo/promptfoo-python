# Promptfoo: LLM evals & red teaming

<p align="center">
  <a href="https://pypi.org/project/promptfoo/"><img src="https://badge.fury.io/py/promptfoo.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/promptfoo/"><img src="https://img.shields.io/pypi/pyversions/promptfoo.svg" alt="Python versions"></a>
  <a href="https://npmjs.com/package/promptfoo"><img src="https://img.shields.io/npm/dm/promptfoo" alt="npm downloads"></a>
  <a href="https://github.com/promptfoo/promptfoo/blob/main/LICENSE"><img src="https://img.shields.io/github/license/promptfoo/promptfoo" alt="MIT license"></a>
  <a href="https://discord.gg/promptfoo"><img src="https://github.com/user-attachments/assets/2092591a-ccc5-42a7-aeb6-24a2808950fd" alt="Discord"></a>
</p>

---

> **📦 About this Python package**
>
> This is a lightweight wrapper that installs promptfoo via `pip`. It requires **Node.js 20+** and executes `npx promptfoo@latest` under the hood.
>
> **💡 If you have Node.js installed**, we recommend using `npx promptfoo@latest` directly for better performance:
>
> ```bash
> npx promptfoo@latest init
> npx promptfoo@latest eval
> ```
>
> See the [main project](https://github.com/promptfoo/promptfoo) for the official npm package.
>
> **🐍 Use this pip wrapper when you:**
>
> - Need to install via `pip` for Python-only CI/CD environments
> - Want to manage promptfoo with poetry/pipenv/pip alongside Python dependencies
> - Work in environments where pip packages are easier to approve than npm

---

<p align="center">
  <code>promptfoo</code> is a developer-friendly local tool for testing LLM applications. Stop the trial-and-error approach - start shipping secure, reliable AI apps.
</p>

<p align="center">
  <a href="https://www.promptfoo.dev">Website</a> ·
  <a href="https://www.promptfoo.dev/docs/getting-started/">Getting Started</a> ·
  <a href="https://www.promptfoo.dev/docs/red-team/">Red Teaming</a> ·
  <a href="https://www.promptfoo.dev/docs/">Documentation</a> ·
  <a href="https://discord.gg/promptfoo">Discord</a>
</p>

## Installation

### Requirements

- **Python 3.9+** (for this wrapper)
- **Node.js 20+** (required to run promptfoo)

### Install from PyPI

```bash
pip install promptfoo
```

### Alternative: Use npx (Recommended)

If you have Node.js installed, you can skip the wrapper and use npx directly:

```bash
npx promptfoo@latest init
npx promptfoo@latest eval
```

This is faster and gives you direct access to the latest version.

## Quick Start

```bash
# Install
pip install promptfoo

# Initialize project
promptfoo init

# Run your first evaluation
promptfoo eval
```

See [Getting Started](https://www.promptfoo.dev/docs/getting-started/) (evals) or [Red Teaming](https://www.promptfoo.dev/docs/red-team/) (vulnerability scanning) for more.

## What can you do with Promptfoo?

- **Test your prompts and models** with [automated evaluations](https://www.promptfoo.dev/docs/getting-started/)
- **Secure your LLM apps** with [red teaming](https://www.promptfoo.dev/docs/red-team/) and vulnerability scanning
- **Compare models** side-by-side (OpenAI, Anthropic, Azure, Bedrock, Ollama, and [more](https://www.promptfoo.dev/docs/providers/))
- **Automate checks** in [CI/CD](https://www.promptfoo.dev/docs/integrations/ci-cd/)
- **Review pull requests** for LLM-related security and compliance issues with [code scanning](https://www.promptfoo.dev/docs/code-scanning/)
- **Share results** with your team

Here's what it looks like in action:

![prompt evaluation matrix - web viewer](https://www.promptfoo.dev/img/claude-vs-gpt-example@2x.png)

It works on the command line too:

![prompt evaluation matrix - command line](https://github.com/promptfoo/promptfoo/assets/310310/480e1114-d049-40b9-bd5f-f81c15060284)

It also can generate [security vulnerability reports](https://www.promptfoo.dev/docs/red-team/):

![gen ai red team](https://www.promptfoo.dev/img/riskreport-1@2x.png)

## Why Promptfoo?

- 🚀 **Developer-first**: Fast, with features like live reload and caching
- 🔒 **Private**: LLM evals run 100% locally - your prompts never leave your machine
- 🔧 **Flexible**: Works with any LLM API or programming language
- 💪 **Battle-tested**: Powers LLM apps serving 10M+ users in production
- 📊 **Data-driven**: Make decisions based on metrics, not gut feel
- 🤝 **Open source**: MIT licensed, with an active community

## How This Wrapper Works

This Python package is a thin wrapper that:

1. Checks if Node.js is installed
2. Executes `npx promptfoo@latest <your-args>` (or uses globally installed promptfoo if available)
3. Passes through all arguments and environment variables
4. Returns the same exit code

The actual promptfoo logic runs via the official TypeScript package from npm. All features and commands work identically.

## Python-Specific Usage

### With pip

```bash
pip install promptfoo
promptfoo eval
```

### With poetry

```bash
poetry add --group dev promptfoo
poetry run promptfoo eval
```

### With requirements.txt

```bash
echo "promptfoo>=0.2.0" >> requirements.txt
pip install -r requirements.txt
promptfoo eval
```

### In CI/CD (GitHub Actions example)

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: "20"

- name: Install promptfoo
  run: pip install promptfoo

- name: Run red team tests
  run: promptfoo redteam run
```

## Learn More

- 📚 [Full Documentation](https://www.promptfoo.dev/docs/intro/)
- 🔐 [Red Teaming Guide](https://www.promptfoo.dev/docs/red-team/)
- 🎯 [Getting Started](https://www.promptfoo.dev/docs/getting-started/)
- 💻 [CLI Usage](https://www.promptfoo.dev/docs/usage/command-line/)
- 📦 [Main Project (npm)](https://github.com/promptfoo/promptfoo)
- 🤖 [Supported Models](https://www.promptfoo.dev/docs/providers/)
- 🔬 [Code Scanning Guide](https://www.promptfoo.dev/docs/code-scanning/)

## Troubleshooting

### "ERROR: promptfoo requires Node.js"

The wrapper needs Node.js to run. Install it:

- **macOS**: `brew install node`
- **Ubuntu/Debian**: `sudo apt install nodejs npm`
- **Windows**: Download from https://nodejs.org/
- **Any OS**: Use [nvm](https://github.com/nvm-sh/nvm)

### Slow First Run

The first time you run `promptfoo`, npx downloads the latest version from npm (typically ~50MB). Subsequent runs use the cached version and are fast.

To speed this up, install promptfoo globally:

```bash
npm install -g promptfoo
```

The Python wrapper will automatically use the global installation when available.

### Version Pinning

By default, this wrapper uses `npx promptfoo@latest`. To pin a specific version:

```bash
export PROMPTFOO_VERSION=0.95.0
promptfoo --version
```

Or install a specific version globally:

```bash
npm install -g promptfoo@0.95.0
```

## Contributing

We welcome contributions! Check out our [contributing guide](https://www.promptfoo.dev/docs/contributing/) to get started.

Join our [Discord community](https://discord.gg/promptfoo) for help and discussion.

**For wrapper-specific issues**: Report them in this repository
**For promptfoo features/bugs**: Report in the [main project](https://github.com/promptfoo/promptfoo)

<a href="https://github.com/promptfoo/promptfoo/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=promptfoo/promptfoo" />
</a>

## License

MIT License - Same as promptfoo
