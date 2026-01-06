"""
Platform-specific Node.js installation instructions.

Generates tailored installation instructions based on the detected environment.
"""

from .environment import Environment


def get_installation_instructions(env: Environment) -> str:
    """
    Generate Node.js installation instructions for the detected environment.

    Args:
        env: Detected environment information

    Returns:
        Formatted installation instructions as a multi-line string
    """
    lines = []
    lines.append("=" * 70)
    lines.append("ERROR: promptfoo requires Node.js but it's not installed")
    lines.append("=" * 70)
    lines.append("")

    # Special cases first (Lambda, Cloud Functions, etc.)
    if env.is_lambda:
        lines.extend(_get_lambda_instructions())
        return "\n".join(lines)

    if env.is_cloud_function:
        lines.extend(_get_cloud_function_instructions(env))
        return "\n".join(lines)

    # CI/CD environment
    if env.is_ci:
        lines.extend(_get_ci_instructions(env))
        lines.append("")

    # Container environment
    if env.is_docker:
        lines.extend(_get_docker_instructions(env))
        lines.append("")

    # WSL environment
    if env.is_wsl:
        lines.extend(_get_wsl_instructions())
        lines.append("")

    # Platform-specific instructions
    if env.os_type == "linux":
        lines.extend(_get_linux_instructions(env))
    elif env.os_type == "darwin":
        lines.extend(_get_macos_instructions())
    elif env.os_type == "windows":
        lines.extend(_get_windows_instructions())

    # Virtual environment alternative
    if env.is_venv or env.is_conda:
        lines.append("")
        lines.extend(_get_venv_instructions())

    # Direct npx usage
    lines.append("")
    lines.extend(_get_npx_instructions())

    return "\n".join(lines)


def _get_lambda_instructions() -> list[str]:
    """Instructions for AWS Lambda environment."""
    return [
        "You are running in AWS Lambda with a Python runtime.",
        "",
        "AWS Lambda Python runtimes do not include Node.js. You have options:",
        "",
        "1. Use a Lambda Layer with Node.js:",
        "   https://docs.aws.amazon.com/lambda/latest/dg/chapter-layers.html",
        "",
        "2. Switch to Node.js runtime:",
        "   https://docs.aws.amazon.com/lambda/latest/dg/lambda-nodejs.html",
        "",
        "3. Use Lambda container images with both Python and Node.js:",
        "   https://docs.aws.amazon.com/lambda/latest/dg/images-create.html",
        "",
        "Note: promptfoo is primarily designed for local development and CI/CD,",
        "not for Lambda runtime execution.",
    ]


def _get_cloud_function_instructions(env: Environment) -> list[str]:
    """Instructions for Cloud Functions (GCP/Azure)."""
    if env.cloud_provider == "gcp":
        return [
            "You are running in Google Cloud Functions with a Python runtime.",
            "",
            "GCP Cloud Functions Python runtimes do not include Node.js.",
            "Consider using Node.js runtime instead:",
            "   https://cloud.google.com/functions/docs/concepts/nodejs-runtime",
        ]
    else:  # Azure or unknown
        return [
            "You are running in Azure Functions with a Python runtime.",
            "",
            "Azure Functions Python runtimes do not include Node.js.",
            "Consider using Node.js runtime instead:",
            "   https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-node",
        ]


def _get_ci_instructions(env: Environment) -> list[str]:
    """Instructions for CI/CD environments."""
    lines = ["RUNNING IN CI/CD: " + (env.ci_platform or "detected").upper(), ""]

    if env.ci_platform == "github":
        lines.extend(
            [
                "Add Node.js to your workflow:",
                "   - uses: actions/setup-node@v4",
                "     with:",
                "       node-version: '20'",
            ]
        )
    elif env.ci_platform == "gitlab":
        lines.extend(
            [
                "Use a Docker image with Node.js:",
                "   image: node:20",
                "Or install Node.js in before_script:",
                "   before_script:",
                "     - apt-get update && apt-get install -y nodejs npm",
            ]
        )
    elif env.ci_platform == "circleci":
        lines.extend(
            [
                "Use a CircleCI image with Node.js:",
                "   docker:",
                "     - image: cimg/python:3.11-node",
            ]
        )
    else:
        lines.extend(
            [
                "Install Node.js in your CI configuration.",
                "Most CI platforms provide Node.js images or setup actions.",
            ]
        )

    return lines


def _get_docker_instructions(env: Environment) -> list[str]:
    """Instructions for Docker environments."""
    lines = ["RUNNING IN DOCKER CONTAINER:", ""]

    if env.linux_distro == "alpine":
        lines.extend(
            [
                "Add to your Dockerfile (Alpine):",
                "   RUN apk add --no-cache nodejs npm",
            ]
        )
    elif env.linux_distro in ("ubuntu", "debian"):
        lines.extend(
            [
                "Add to your Dockerfile (Debian/Ubuntu):",
                "   RUN apt-get update && \\",
                "       apt-get install -y nodejs npm && \\",
                "       rm -rf /var/lib/apt/lists/*",
                "",
                "Or use NodeSource for newer version:",
                "   RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \\",
                "       apt-get install -y nodejs && \\",
                "       rm -rf /var/lib/apt/lists/*",
            ]
        )
    else:
        lines.extend(
            [
                "Add Node.js to your Dockerfile:",
                "   FROM python:3.11",
                "   RUN apt-get update && apt-get install -y nodejs npm",
            ]
        )

    return lines


def _get_wsl_instructions() -> list[str]:
    """Instructions for Windows Subsystem for Linux (WSL)."""
    return [
        "WINDOWS SUBSYSTEM FOR LINUX (WSL) DETECTED:",
        "",
        "IMPORTANT: Install Node.js within WSL, not from Windows.",
        "Using Windows Node.js from WSL can cause path and performance issues.",
        "",
        "Recommended approach:",
        "   1. Use your Linux distribution's package manager (see below)",
        "   2. Or use nvm for version management:",
        "      curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash",
        "      source ~/.bashrc",
        "      nvm install 20",
        "",
        "Tips for WSL:",
        "   - Store project files in the WSL filesystem (~/), not /mnt/c/",
        "   - This improves file I/O performance significantly",
        "   - Use 'wsl --shutdown' to restart WSL if needed",
    ]


def _get_linux_instructions(env: Environment) -> list[str]:
    """Instructions for Linux systems."""
    lines = []
    distro = env.linux_distro

    if distro in ("ubuntu", "debian"):
        lines.extend(_get_debian_instructions(env))
    elif distro == "rhel":
        lines.extend(_get_rhel_instructions(env))
    elif distro == "alpine":
        lines.extend(_get_alpine_instructions())
    elif distro == "arch":
        lines.extend(_get_arch_instructions())
    elif distro == "suse":
        lines.extend(_get_suse_instructions())
    else:
        # Generic Linux instructions
        lines.extend(_get_generic_linux_instructions())

    return lines


def _get_debian_instructions(env: Environment) -> list[str]:
    """Instructions for Debian/Ubuntu systems."""
    lines = ["UBUNTU/DEBIAN INSTALLATION:", ""]

    if env.has_sudo:
        lines.extend(
            [
                "Option 1 - Install from NodeSource (recommended for production):",
                "   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -",
                "   sudo apt install -y nodejs",
                "",
                "Option 2 - Install from default repository (may be outdated):",
                "   sudo apt update",
                "   sudo apt install -y nodejs npm",
                "",
                "Option 3 - Install using snap (not recommended for production):",
                "   sudo snap install node --classic",
                "   # Note: Snap auto-updates can cause unexpected behavior",
            ]
        )
    else:
        lines.extend(
            [
                "You don't have sudo access. Use nvm (Node Version Manager):",
                "   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash",
                "   source ~/.bashrc",
                "   nvm install 20",
            ]
        )

    return lines


def _get_rhel_instructions(env: Environment) -> list[str]:
    """Instructions for RHEL/CentOS/Fedora/Amazon Linux."""
    lines = []

    # Detect Amazon Linux vs RHEL/CentOS/Fedora
    is_amazon_linux = (
        env.linux_distro == "rhel" and env.linux_distro_version and env.linux_distro_version.startswith("202")
    )

    if is_amazon_linux:
        lines.extend(["AMAZON LINUX INSTALLATION:", ""])
        if env.has_sudo:
            lines.extend(
                [
                    "Amazon Linux 2023:",
                    "   sudo dnf install -y nodejs",
                    "",
                    "Amazon Linux 2:",
                    "   curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -",
                    "   sudo yum install -y nodejs",
                ]
            )
        else:
            lines.extend(
                [
                    "Use nvm (Node Version Manager) - no sudo needed:",
                    "   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash",
                    "   source ~/.bashrc",
                    "   nvm install 20",
                ]
            )
    else:
        lines.extend(["RHEL/CENTOS/FEDORA INSTALLATION:", ""])
        if env.has_sudo:
            lines.extend(
                [
                    "Using dnf (RHEL 8+/Fedora):",
                    "   sudo dnf install -y nodejs npm",
                    "",
                    "Using yum (RHEL 7):",
                    "   sudo yum install -y nodejs npm",
                    "",
                    "Or use NodeSource for newer version:",
                    "   curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -",
                    "   sudo yum install -y nodejs",
                ]
            )
        else:
            lines.extend(
                [
                    "Use nvm (Node Version Manager) - no sudo needed:",
                    "   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash",
                    "   source ~/.bashrc",
                    "   nvm install 20",
                ]
            )

    return lines


def _get_alpine_instructions() -> list[str]:
    """Instructions for Alpine Linux."""
    return [
        "ALPINE LINUX INSTALLATION:",
        "",
        "   apk add --update nodejs npm",
        "",
        "In Dockerfile:",
        "   RUN apk add --no-cache nodejs npm",
    ]


def _get_arch_instructions() -> list[str]:
    """Instructions for Arch Linux."""
    return [
        "ARCH LINUX INSTALLATION:",
        "",
        "   sudo pacman -S nodejs npm",
    ]


def _get_suse_instructions() -> list[str]:
    """Instructions for SUSE/openSUSE."""
    return [
        "SUSE/OPENSUSE INSTALLATION:",
        "",
        "   sudo zypper install nodejs npm",
    ]


def _get_generic_linux_instructions() -> list[str]:
    """Fallback instructions for unknown Linux distributions."""
    return [
        "LINUX INSTALLATION:",
        "",
        "Use your package manager to install Node.js, or use nvm:",
        "",
        "Option 1 - nvm (Node Version Manager, works on any Linux):",
        "   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash",
        "   source ~/.bashrc",
        "   nvm install 20",
        "",
        "Option 2 - Download binary from https://nodejs.org/",
    ]


def _get_macos_instructions() -> list[str]:
    """Instructions for macOS."""
    return [
        "MACOS INSTALLATION:",
        "",
        "Option 1 - Homebrew (recommended):",
        "   brew install node",
        "",
        "Option 2 - nvm (Node Version Manager, for version management):",
        "   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash",
        "   source ~/.zshrc  # or ~/.bashrc",
        "   nvm install 20",
        "",
        "Option 3 - Official installer:",
        "   Download from https://nodejs.org/",
    ]


def _get_windows_instructions() -> list[str]:
    """Instructions for Windows."""
    return [
        "WINDOWS INSTALLATION:",
        "",
        "Option 1 - Official installer (recommended):",
        "   Download from https://nodejs.org/",
        "",
        "Option 2 - winget (Windows 10/11, built-in):",
        "   winget install OpenJS.NodeJS.LTS  # For LTS version",
        "   # or: winget install OpenJS.NodeJS  # For current version",
        "",
        "Option 3 - Chocolatey:",
        "   choco install nodejs-lts  # For LTS version",
        "   # or: choco install nodejs  # For current version",
        "",
        "Option 4 - Scoop:",
        "   scoop install nodejs-lts  # For LTS version",
        "   # or: scoop install nodejs  # For current version",
    ]


def _get_venv_instructions() -> list[str]:
    """Instructions for virtual environment users."""
    return [
        "ALTERNATIVE: Install Node.js in your Python virtualenv (no sudo):",
        "   pip install nodeenv",
        "   nodeenv -p  # Installs Node.js in current virtualenv",
        "   # Then run promptfoo again",
    ]


def _get_npx_instructions() -> list[str]:
    """Instructions for direct npx usage."""
    return [
        "DIRECT USAGE (bypasses Python wrapper):",
        "   npx promptfoo@latest eval",
        "   # This is often faster and always uses the latest version",
    ]
