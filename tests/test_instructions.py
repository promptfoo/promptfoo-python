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
    if platform == "windows":
        assert "use: npx.exe --version" in output
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
    assert "sudo /usr/sbin/alternatives --set node /usr/bin/node-24" in output
    assert "omit sudo when running as root" in output
    assert "https://docs.aws.amazon.com/linux/al2023/ug/nodejs.html" in output
    assert "2023.9.20251110" in output
    assert "dnf --releasever=latest install" in output
    assert "Without sudo, install nvm: https://github.com/nvm-sh/nvm#installing-and-updating" in output
    assert "nvm install 24" in output
    assert "dnf install -y nodejs\n" not in output


def test_unknown_amazon_release_is_not_given_amazon_linux_2023_commands() -> None:
    output = get_installation_instructions(Environment(os_type="linux", linux_distro="amzn"))
    assert "nvm install 24" in output
    assert "nodejs24-npm" not in output


@pytest.mark.parametrize("container", [False, True])
def test_amazon_linux_2_recommends_a_compatible_os(container: bool) -> None:
    output = get_installation_instructions(
        Environment(os_type="linux", linux_distro="amzn", linux_distro_version="2", is_docker=container)
    )
    assert "Amazon Linux 2023" in output
    assert "require newer glibc" in output
    assert "nvm install 24" not in output
    if container:
        assert "compatible base image" in output
        assert "keep your existing base image" not in output


def test_ci_container_and_wsl_hints_can_coexist() -> None:
    output = get_installation_instructions(
        Environment(
            os_type="linux",
            linux_distro="debian",
            linux_distro_version="12",
            ci_platform="GitHub Actions",
            is_docker=True,
            is_wsl=True,
        )
    )

    assert "- uses: actions/setup-node@v7\n     with:\n       node-version: '24'" in output
    assert "FROM node:24-bookworm-slim AS node" in output
    assert "FROM python:3.12-slim-bookworm" in output
    assert "Keep the second FROM set to your existing image and Python environment" in output
    assert "COPY --from=node /usr/local/bin/node /usr/local/bin/node" in output
    assert "npm/bin/npx-cli.js /usr/local/bin/npx" in output
    assert "/usr/local/bin/node /usr/bin/node" in output
    assert "/usr/local/bin/npm /usr/bin/npm" in output
    assert "/usr/local/bin/npx /usr/bin/npx" in output
    assert "venv" not in output
    assert 'ENV NPM_CONFIG_PREFIX="/opt/npm-global"' in output
    assert 'ENV PATH="${PATH}:/usr/local/bin:/opt/npm-global/bin"' in output
    assert "nvm install" not in output
    assert "https://hub.docker.com/_/node" in output
    assert "install Node.js inside your Linux distribution" in output


@pytest.mark.parametrize(
    ("distribution", "version", "command"),
    [
        ("ubuntu", "24.04", "https://deb.nodesource.com/setup_24.x"),
        ("amzn", "2023", "dnf --releasever=latest install -y nodejs24 nodejs24-npm"),
    ],
)
def test_non_bookworm_containers_keep_their_original_base(distribution: str, version: str, command: str) -> None:
    output = get_installation_instructions(
        Environment(os_type="linux", linux_distro=distribution, linux_distro_version=version, is_docker=True)
    )
    assert "keep your existing FROM" in output
    assert command in output
    assert "FROM python:" not in output
    assert "bookworm" not in output
    if distribution == "amzn":
        assert "/usr/sbin/alternatives --set node" in output
        assert "2023.9.20251110" in output
    if distribution == "ubuntu":
        commands = [line for line in output.splitlines() if line.strip().startswith("RUN ")]
        assert len(commands) == 1
        assert "apt-get update" in commands[0]
        assert "rm -rf /var/lib/apt/lists/*" in commands[0]


def test_trixie_container_uses_matching_supported_node_and_python_images() -> None:
    output = get_installation_instructions(
        Environment(os_type="linux", linux_distro="debian", linux_distro_version="13", is_docker=True)
    )
    assert "Debian Trixie" in output
    assert "FROM node:24-trixie-slim AS node" in output
    assert "FROM python:3.12-slim-trixie" in output
    assert "/usr/local/bin/node /usr/bin/node" in output
    assert 'ENV NPM_CONFIG_PREFIX="/opt/npm-global"' in output
    assert 'ENV PATH="${PATH}:/usr/local/bin:/opt/npm-global/bin"' in output
    assert "bookworm" not in output


def test_unknown_container_does_not_claim_to_be_bookworm() -> None:
    output = get_installation_instructions(
        Environment(os_type="linux", linux_distro="debian", linux_distro_version="14", is_docker=True)
    )
    assert "keep your existing base image" in output
    assert "distribution and CPU architecture" in output
    assert "FROM python:" not in output


def test_other_ci_uses_the_provider_setup_instructions() -> None:
    output = get_installation_instructions(Environment(os_type="linux", ci_platform="GitLab CI"))
    assert "GitLab CI: use your CI provider's Node.js setup step or an image with Node.js 24." in output
    assert "actions/setup-node" not in output


@pytest.mark.parametrize(
    "provider, label, documentation, hosting",
    [
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
    if provider == "azure":
        assert "Select that hosting environment in the documentation" in output
        assert "?pivots=" not in output


def test_lambda_zip_can_use_a_layer_or_choose_to_create_an_image_based_function() -> None:
    output = get_installation_instructions(
        Environment(os_type="linux", linux_distro="amzn", linux_distro_version="2023", is_docker=True, serverless="aws")
    )
    assert "existing ZIP function can keep its configuration" in output
    assert "Node, npm and npx in /opt/bin" in output
    assert "supporting files" in output
    assert "https://docs.aws.amazon.com/lambda/latest/dg/packaging-layers.html" in output
    assert "If you choose a container image instead, create a new image-based function" in output
    assert "https://docs.aws.amazon.com/lambda/latest/dg/images-create.html" in output
    assert "sudo" not in output


def test_lambda_on_amazon_linux_2_requires_a_compatible_runtime_before_packaging() -> None:
    output = get_installation_instructions(
        Environment(os_type="linux", linux_distro="amzn", linux_distro_version="2", is_docker=True, serverless="aws")
    )
    assert "first upgrade to an Amazon Linux 2023 based Python runtime" in output
