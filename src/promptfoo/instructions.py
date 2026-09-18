"""Concise Node.js installation guidance for the current platform."""

from .environment import Environment
from .node import MIN_NODE_VERSION_TEXT

_NODE_DOWNLOAD = "https://nodejs.org/en/download"
_NVM = "https://github.com/nvm-sh/nvm#installing-and-updating"
_SERVERLESS = {
    "aws": ("AWS Lambda", "https://docs.aws.amazon.com/lambda/latest/dg/images-create.html"),
    "google": ("Google Cloud Functions", "https://cloud.google.com/run/docs/runtimes/nodejs"),
    "azure": ("Azure Functions", "https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-node"),
}


def _container_instructions(env: Environment) -> list[str]:
    if env.linux_distro == "alpine":
        return [
            "CONTAINER: start from the official Node.js 24 Alpine image and add Python:",
            "   FROM node:24-alpine",
            "   RUN apk add --no-cache python3 py3-pip",
            "   RUN python3 -m venv /opt/venv",
            '   ENV PATH="/opt/venv/bin:$PATH"',
        ]
    return [
        "CONTAINER: include Node.js 24 in your image; keep the Node and Python base distributions compatible.",
        "   Official Node.js images: https://hub.docker.com/_/node",
    ]


def _linux_instructions(env: Environment) -> list[str]:
    if env.linux_distro == "alpine":
        return [
            "ALPINE: on a release whose repositories provide Node.js 24, run as root:",
            "   apk add --no-cache 'nodejs~24' npm",
            "   node --version",
            "If apk cannot find Node.js 24, upgrade Alpine or use the official node:24-alpine container.",
        ]
    if env.linux_distro == "amzn" and env.linux_distro_version == "2023":
        return [
            "AMAZON LINUX 2023: install and select Node.js 24 (omit sudo when running as root):",
            "   sudo dnf install -y nodejs24 nodejs24-npm",
            "   sudo alternatives --set node /usr/bin/node-24",
            "   node --version",
            "   https://docs.aws.amazon.com/linux/al2023/ug/nodejs.html",
        ]
    return [
        "LINUX: use a Node.js version manager or your distribution's instructions for Node.js 24.",
        f"   Install nvm: {_NVM}",
        "   Then run: nvm install 24",
    ]


def get_installation_instructions(env: Environment) -> str:
    """Explain how to install a supported Node.js runtime without guessing package versions."""
    lines = [
        f"ERROR: promptfoo requires Node.js {MIN_NODE_VERSION_TEXT} or newer, but it was not found.",
        f"Install Node.js 24 LTS with npm: {_NODE_DOWNLOAD}",
        "Verify with: node --version && npx --version",
    ]

    if env.serverless and env.serverless in _SERVERLESS:
        name, documentation = _SERVERLESS[env.serverless]
        lines += ["", f"{name}: use a deployment that includes both Node.js and Python.", f"   {documentation}"]

    if env.ci_platform == "GitHub Actions":
        lines += ["", "GITHUB ACTIONS: add Node.js to your workflow:", "   - uses: actions/setup-node@v7", "     with:"]
        lines.append("       node-version: '24'")
    elif env.ci_platform:
        lines += ["", f"{env.ci_platform}: use your CI provider's Node.js setup step or an image with Node.js 24."]

    if env.is_docker:
        lines += ["", *_container_instructions(env)]
    if env.is_wsl:
        lines += ["", "WSL: install Node.js inside your Linux distribution, not on the Windows host."]

    if env.os_type == "linux":
        lines += ["", *_linux_instructions(env)]
    elif env.os_type == "darwin":
        lines += ["", "MACOS: install Node.js with Homebrew (`brew install node`) or the installer linked above."]
    elif env.os_type == "windows":
        lines += ["", "WINDOWS: use the installer linked above or run: winget install OpenJS.NodeJS.LTS"]

    lines += ["", "DIRECT USAGE after installing Node.js: npx promptfoo@latest eval"]
    return "\n".join(lines)
