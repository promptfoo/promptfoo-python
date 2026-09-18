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
    assert "node --version && npx --version" in output
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
    assert "keep the Node and Python base distributions compatible" in output
    assert "https://hub.docker.com/_/node" in output
    assert "install Node.js inside your Linux distribution" in output


def test_other_ci_uses_the_provider_setup_instructions() -> None:
    output = get_installation_instructions(Environment(os_type="linux", ci_platform="GitLab CI"))
    assert "GitLab CI: use your CI provider's Node.js setup step or an image with Node.js 24." in output
    assert "actions/setup-node" not in output


@pytest.mark.parametrize(
    "provider, label, host",
    [
        ("aws", "AWS Lambda", "docs.aws.amazon.com"),
        ("google", "Google Cloud Functions", "cloud.google.com"),
        ("azure", "Azure Functions", "learn.microsoft.com"),
    ],
)
def test_serverless_links_explain_the_need_for_both_runtimes(provider: str, label: str, host: str) -> None:
    output = get_installation_instructions(Environment(os_type="linux", serverless=provider))

    assert f"{label}: use a deployment that includes both Node.js and Python" in output
    assert host in output
    assert "https://nodejs.org/en/download" in output
