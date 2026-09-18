"""Concise Node.js installation guidance for the current platform."""

from .environment import Environment
from .node import MIN_NODE_VERSION_TEXT

_NODE_DOWNLOAD = "https://nodejs.org/en/download"
_NVM = "https://github.com/nvm-sh/nvm#installing-and-updating"
_APT_NODE_24 = (
    "   RUN apt-get update && apt-get install -y --no-install-recommends bash ca-certificates curl "
    "&& curl -fsSL https://deb.nodesource.com/setup_24.x -o /tmp/nodesource-setup.sh "
    "&& bash /tmp/nodesource-setup.sh && rm /tmp/nodesource-setup.sh "
    "&& apt-get install -y --no-install-recommends nodejs && rm -rf /var/lib/apt/lists/*"
)
_NODESOURCE = "   NodeSource's apt repository: https://github.com/nodesource/distributions"
_APT_ARCHITECTURES = (
    "The NodeSource apt recipe supports amd64 and arm64. For other CPU architectures, select a supported "
    f"Node.js 24 installation for your target: {_NODE_DOWNLOAD}"
)
_SERVERLESS = {
    "google": (
        "Google Cloud Functions / Cloud Run",
        "Functions deployed from source, including first-generation functions, must move to a Cloud Run service "
        "to deploy a custom image.",
        "https://docs.cloud.google.com/run/docs/building/containers",
    ),
    "azure": (
        "Azure Functions",
        "Consumption and Flex Consumption do not accept custom images. Move to Azure Container Apps "
        "or a Linux Premium/Dedicated plan. Select that hosting environment in the documentation. "
        "On Kubernetes, keep the Azure Functions base image and add Node.",
        "https://learn.microsoft.com/en-us/azure/azure-functions/functions-how-to-custom-container",
    ),
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
    debian_release = {"12": "bookworm", "bookworm": "bookworm", "13": "trixie", "trixie": "trixie"}.get(
        env.linux_distro_version or ""
    )
    if env.linux_distro == "debian" and debian_release:
        return [
            f"CONTAINER: add Node.js 24 to your existing Debian {debian_release.title()} Python image; "
            "this example uses Python 3.12.",
            "Keep FROM set to your existing image, platform, and Python environment:",
            "Run these build steps as root; restore your original USER afterward if needed.",
            _APT_ARCHITECTURES,
            f"   FROM python:3.12-slim-{debian_release}",
            _APT_NODE_24,
            '   ENV PATH="${PATH}:/usr/local/bin"',
            "The default npm global prefix is /usr; the Python image installs scripts in /usr/local/bin.",
            "Keep an existing writable npm prefix only if its bin is separate from Python's scripts directory. "
            "If its bin is missing from PATH, add it before /usr/bin "
            "and after your Python scripts (for example /opt/venv/bin or /usr/local/bin).",
            "If an inherited NPM_CONFIG_PREFIX points to an unwritable directory, change it in the Dockerfile "
            "(for example `ENV NPM_CONFIG_PREFIX=/home/app/.npm-global`). Without that override, a non-root user "
            "can run `npm config set prefix ~/.npm-global`. Add the writable bin to PATH in either case.",
            _NODESOURCE,
        ]
    if env.linux_distro == "ubuntu":
        return [
            "UBUNTU CONTAINER: keep your existing FROM and install Node.js 24 in place as root:",
            _APT_ARCHITECTURES,
            _APT_NODE_24,
            _NODESOURCE,
        ]
    if env.linux_distro == "amzn" and env.linux_distro_version == "2023":
        return [
            "AMAZON LINUX 2023 CONTAINER: keep your existing FROM and install Node.js 24 as root:",
            "   RUN dnf --releasever=latest install -y nodejs24 nodejs24-npm "
            "&& /usr/sbin/alternatives --set node /usr/bin/node-24 && dnf clean all",
            "Node 24 requires repository release 2023.9.20251110 or newer; replace latest with your approved recent "
            "snapshot, or update an older base image before installing.",
            "   https://docs.aws.amazon.com/linux/al2023/ug/nodejs.html",
            "   https://docs.aws.amazon.com/linux/al2023/ug/managing-repos-os-updates.html",
        ]
    if env.linux_distro == "amzn" and env.linux_distro_version == "2":
        return [
            "AMAZON LINUX 2 CONTAINER: move to an Amazon Linux 2023 or another Node.js 24 compatible base image.",
            "Official Node.js 22/24 Linux binaries require newer glibc than Amazon Linux 2 provides.",
            "   https://docs.aws.amazon.com/linux/al2023/ug/nodejs.html",
        ]
    return [
        "CONTAINER: keep your existing base image and install Node.js 24 with npm during the image build.",
        "Use installation instructions compatible with your distribution and CPU architecture:",
        f"   {_NODE_DOWNLOAD}",
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
            "   sudo /usr/sbin/alternatives --set node /usr/bin/node-24",
            "   node --version",
            "   https://docs.aws.amazon.com/linux/al2023/ug/nodejs.html",
            "If your pinned repository is older than 2023.9.20251110, update the base/repository or install from a "
            "newer approved snapshot: sudo dnf --releasever=latest install -y nodejs24 nodejs24-npm",
            f"   Without sudo, install nvm: {_NVM}",
            "   Then run: nvm install 24",
        ]
    if env.linux_distro == "amzn" and env.linux_distro_version == "2":
        return [
            "AMAZON LINUX 2: upgrade to Amazon Linux 2023 or run in a Node.js 24 compatible container.",
            "Official Node.js 22/24 Linux binaries require newer glibc than Amazon Linux 2 provides.",
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
        "Verify with:",
        "   node --version",
        "   npx.cmd --version" if env.os_type == "windows" else "   npx --version",
    ]
    if env.os_type == "windows":
        lines.append("If your Node manager installs npx.exe instead (such as Volta), use: npx.exe --version")

    if env.serverless == "aws":
        lines += [
            "",
            "AWS Lambda: include Node.js and npm in a compatible Lambda layer or a custom Python container.",
            "An existing ZIP function can keep its configuration: attach a layer with Node, npm and npx in /opt/bin.",
            "Include npm's supporting files and target the function's Amazon Linux version and CPU architecture.",
            "   https://docs.aws.amazon.com/lambda/latest/dg/packaging-layers.html",
            "If you choose a container image instead, create a new image-based function "
            "and install Node at build time.",
            "   https://docs.aws.amazon.com/lambda/latest/dg/images-create.html",
        ]
        if env.linux_distro == "amzn" and env.linux_distro_version == "2":
            lines.append(
                "For an Amazon Linux 2 based function, first upgrade to an Amazon Linux 2023 based Python runtime "
                "before packaging the official Node.js 22/24 binaries."
            )
        return "\n".join(lines)
    if env.serverless and env.serverless in _SERVERLESS:
        name, hosting, documentation = _SERVERLESS[env.serverless]
        lines += [
            "",
            f"{name}: build and deploy a custom container that includes both Node.js and Python.",
            hosting,
            "Install both runtimes when building the image; they cannot be installed in the running function.",
            f"   {documentation}",
        ]
        return "\n".join(lines)

    if env.ci_platform == "GitHub Actions":
        lines += ["", "GITHUB ACTIONS: add Node.js to your workflow:", "   - uses: actions/setup-node@v7", "     with:"]
        lines.append("       node-version: '24'")
    elif env.ci_platform:
        lines += ["", f"{env.ci_platform}: use your CI provider's Node.js setup step or an image with Node.js 24."]

    if env.is_docker:
        lines += ["", *_container_instructions(env)]
    if env.is_wsl:
        lines += ["", "WSL: install Node.js inside your Linux distribution, not on the Windows host."]

    if env.os_type == "linux" and (not env.is_docker or env.linux_distro == "alpine"):
        lines += ["", *_linux_instructions(env)]
    elif env.os_type == "darwin":
        lines += ["", "MACOS: install Node.js with Homebrew (`brew install node`) or the installer linked above."]
    elif env.os_type == "windows":
        lines += ["", "WINDOWS: use the installer linked above or run: winget install OpenJS.NodeJS.LTS"]

    lines += ["", "DIRECT USAGE after installing Node.js: npx promptfoo@latest eval"]
    return "\n".join(lines)
