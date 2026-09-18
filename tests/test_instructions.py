import pytest

from promptfoo.environment import Environment
from promptfoo.instructions import get_installation_instructions
from promptfoo.node import MIN_NODE_VERSION_TEXT


@pytest.mark.parametrize("platform", ["linux", "darwin", "windows", "freebsd14"])
def test_every_platform_gets_the_runtime_requirement_and_a_working_fallback(platform: str) -> None:
    output = get_installation_instructions(Environment(os_type=platform))

    assert f"requires Node.js {MIN_NODE_VERSION_TEXT} or newer" in output
    assert "Node.js 24 LTS with npm" in output
    assert "https://nodejs.org/en/download" in output
    npx = "npx.cmd" if platform == "windows" else "npx"
    assert f"   node --version\n   {npx} --version" in output
    assert "node --version &&" not in output
    assert "DIRECT USAGE after installing Node.js: npx promptfoo@latest eval" in output


@pytest.mark.parametrize(
    "platform, hint",
    [("linux", "nvm install 24"), ("darwin", "brew install node"), ("windows", "winget install OpenJS.NodeJS.LTS")],
)
def test_common_platforms_get_one_relevant_installation_hint(platform: str, hint: str) -> None:
    assert hint in get_installation_instructions(Environment(os_type=platform))


def test_alpine_dockerfile_contains_only_the_verified_setup_steps() -> None:
    output = get_installation_instructions(Environment(os_type="linux", linux_distro="alpine", is_docker=True))
    commands = [line.strip() for line in output.splitlines() if line.strip().startswith(("FROM ", "RUN ", "ENV "))]

    assert commands == [
        "FROM node:24-alpine",
        "RUN apk add --no-cache python3 py3-pip",
        "RUN python3 -m venv /opt/venv",
        'ENV PATH="/opt/venv/bin:$PATH"',
    ]
    assert "apk add --no-cache 'nodejs~24' npm" in output
    assert "upgrade Alpine or use the official node:24-alpine container" in output
    assert "apk add --no-cache nodejs npm" not in output


def test_amazon_linux_2023_installs_both_versioned_packages_and_selects_the_active_node() -> None:
    output = get_installation_instructions(
        Environment(os_type="linux", linux_distro="amzn", linux_distro_version="2023")
    )

    assert "sudo dnf install -y nodejs24 nodejs24-npm" in output
    assert "sudo alternatives --set node /usr/bin/node-24" in output
    assert "omit sudo when running as root" in output
    assert "https://docs.aws.amazon.com/linux/al2023/ug/nodejs.html" in output
    assert "Without sudo, install nvm: https://github.com/nvm-sh/nvm#installing-and-updating" in output
    assert "nvm install 24" in output
    assert "dnf install -y nodejs\n" not in output


@pytest.mark.parametrize("version", [None, "2"])
def test_other_amazon_releases_are_not_given_amazon_linux_2023_commands(version: str | None) -> None:
    output = get_installation_instructions(
        Environment(os_type="linux", linux_distro="amzn", linux_distro_version=version)
    )
    assert "nvm install 24" in output
    assert "nodejs24-npm" not in output


def test_ci_container_and_wsl_hints_can_coexist() -> None:
    output = get_installation_instructions(
        Environment(os_type="linux", linux_distro="ubuntu", ci_platform="GitHub Actions", is_docker=True, is_wsl=True)
    )

    assert "- uses: actions/setup-node@v7\n     with:\n       node-version: '24'" in output
    assert "FROM node:24-bookworm-slim AS node" in output
    assert "FROM python:3.12-slim-bookworm" in output
    assert "Keep the second FROM set to your application's Python version" in output
    assert "COPY --from=node /usr/local/bin/node /usr/local/bin/node" in output
    assert "npm/bin/npx-cli.js /usr/local/bin/npx" in output
    assert "RUN python -m venv /opt/venv" in output
    assert 'ENV PATH="/opt/venv/bin:$PATH"' in output
    assert "nvm install" not in output
    assert "https://hub.docker.com/_/node" in output
    assert "install Node.js inside your Linux distribution" in output


def test_other_ci_uses_the_provider_setup_instructions() -> None:
    output = get_installation_instructions(Environment(os_type="linux", ci_platform="GitLab CI"))
    assert "GitLab CI: use your CI provider's Node.js setup step or an image with Node.js 24." in output
    assert "actions/setup-node" not in output


@pytest.mark.parametrize(
    "provider, label, documentation, hosting",
    [
        (
            "aws",
            "AWS Lambda",
            "docs.aws.amazon.com/lambda/latest/dg/images-create.html",
            "create a new image-based function",
        ),
        (
            "google",
            "Google Cloud Functions / Cloud Run",
            "docs.cloud.google.com/run/docs/building/containers",
            "first-generation functions, must move to a Cloud Run service",
        ),
        (
            "azure",
            "Azure Functions",
            "learn.microsoft.com/en-us/azure/azure-functions/functions-how-to-custom-container",
            "Flex Consumption do not accept custom images. Move to Azure Container Apps",
        ),
    ],
)
def test_serverless_links_explain_how_to_build_both_runtimes(
    provider: str, label: str, documentation: str, hosting: str
) -> None:
    output = get_installation_instructions(
        Environment(
            os_type="linux", linux_distro="amzn", linux_distro_version="2023", is_docker=True, serverless=provider
        )
    )

    assert f"{label}: build and deploy a custom container that includes both Node.js and Python" in output
    assert documentation in output
    assert hosting in output
    assert "https://nodejs.org/en/download" in output
    assert "when building the image" in output
    assert "sudo" not in output
    assert "nvm" not in output
    assert "npx promptfoo" not in output
