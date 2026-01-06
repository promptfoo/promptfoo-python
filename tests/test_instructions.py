"""
Tests for platform-specific installation instructions.

This module tests that appropriate instructions are generated for
different platforms and environments.
"""

from promptfoo.environment import Environment
from promptfoo.instructions import get_installation_instructions


class TestLambdaInstructions:
    """Test instructions for AWS Lambda."""

    def test_lambda_instructions(self) -> None:
        """Generate Lambda-specific instructions."""
        env = Environment(
            os_type="linux",
            linux_distro="rhel",
            cloud_provider="aws",
            is_lambda=True,
        )

        instructions = get_installation_instructions(env)

        assert "AWS Lambda" in instructions
        assert "Lambda Layer" in instructions
        assert "Node.js runtime" in instructions


class TestCloudFunctionInstructions:
    """Test instructions for Cloud Functions."""

    def test_gcp_cloud_function_instructions(self) -> None:
        """Generate GCP Cloud Functions instructions."""
        env = Environment(
            os_type="linux",
            cloud_provider="gcp",
            is_cloud_function=True,
        )

        instructions = get_installation_instructions(env)

        assert "Google Cloud Functions" in instructions or "GCP" in instructions

    def test_azure_function_instructions(self) -> None:
        """Generate Azure Functions instructions."""
        env = Environment(
            os_type="linux",
            cloud_provider="azure",
            is_cloud_function=True,
        )

        instructions = get_installation_instructions(env)

        assert "Azure Functions" in instructions


class TestCIInstructions:
    """Test instructions for CI/CD environments."""

    def test_github_actions_instructions(self) -> None:
        """Generate GitHub Actions-specific instructions."""
        env = Environment(
            os_type="linux",
            linux_distro="ubuntu",
            is_ci=True,
            ci_platform="github",
        )

        instructions = get_installation_instructions(env)

        assert "actions/setup-node" in instructions
        assert "GITHUB" in instructions.upper()

    def test_gitlab_ci_instructions(self) -> None:
        """Generate GitLab CI instructions."""
        env = Environment(
            os_type="linux",
            is_ci=True,
            ci_platform="gitlab",
        )

        instructions = get_installation_instructions(env)

        assert "gitlab" in instructions.lower() or "GITLAB" in instructions
        assert "image:" in instructions or "before_script" in instructions

    def test_circleci_instructions(self) -> None:
        """Generate CircleCI instructions."""
        env = Environment(
            os_type="linux",
            is_ci=True,
            ci_platform="circleci",
        )

        instructions = get_installation_instructions(env)

        assert "circleci" in instructions.lower() or "CIRCLECI" in instructions


class TestDockerInstructions:
    """Test instructions for Docker containers."""

    def test_docker_alpine_instructions(self) -> None:
        """Generate Docker instructions for Alpine."""
        env = Environment(
            os_type="linux",
            linux_distro="alpine",
            is_docker=True,
        )

        instructions = get_installation_instructions(env)

        assert "apk add" in instructions
        assert "Dockerfile" in instructions

    def test_docker_ubuntu_instructions(self) -> None:
        """Generate Docker instructions for Ubuntu."""
        env = Environment(
            os_type="linux",
            linux_distro="ubuntu",
            is_docker=True,
        )

        instructions = get_installation_instructions(env)

        assert "apt-get" in instructions
        assert "Dockerfile" in instructions


class TestWSLInstructions:
    """Test instructions for WSL (Windows Subsystem for Linux)."""

    def test_wsl_instructions(self) -> None:
        """Generate WSL-specific instructions."""
        env = Environment(
            os_type="linux",
            linux_distro="ubuntu",
            is_wsl=True,
        )

        instructions = get_installation_instructions(env)

        assert "WSL" in instructions or "Windows Subsystem for Linux" in instructions
        assert "nvm" in instructions
        assert "/mnt/c" in instructions  # Should mention Windows filesystem
        assert "performance" in instructions.lower()

    def test_wsl_with_ubuntu_shows_both(self) -> None:
        """WSL instructions should show both WSL tips and Ubuntu instructions."""
        env = Environment(
            os_type="linux",
            linux_distro="ubuntu",
            is_wsl=True,
            has_sudo=True,
        )

        instructions = get_installation_instructions(env)

        # Should have WSL-specific guidance
        assert "WSL" in instructions
        # Should also have Ubuntu/Debian instructions
        assert "UBUNTU" in instructions or "DEBIAN" in instructions


class TestLinuxInstructions:
    """Test instructions for various Linux distributions."""

    def test_ubuntu_instructions_with_sudo(self) -> None:
        """Generate Ubuntu instructions with sudo access."""
        env = Environment(
            os_type="linux",
            linux_distro="ubuntu",
            has_sudo=True,
        )

        instructions = get_installation_instructions(env)

        assert "UBUNTU/DEBIAN" in instructions
        assert "sudo apt" in instructions
        assert "NodeSource" in instructions

    def test_ubuntu_instructions_without_sudo(self) -> None:
        """Generate Ubuntu instructions without sudo access."""
        env = Environment(
            os_type="linux",
            linux_distro="ubuntu",
            has_sudo=False,
        )

        instructions = get_installation_instructions(env)

        assert "nvm" in instructions
        # Should NOT suggest sudo apt commands when user doesn't have sudo
        assert "sudo apt" not in instructions
        assert "sudo snap" not in instructions

    def test_debian_instructions(self) -> None:
        """Generate Debian instructions."""
        env = Environment(
            os_type="linux",
            linux_distro="debian",
            has_sudo=True,
        )

        instructions = get_installation_instructions(env)

        assert "UBUNTU/DEBIAN" in instructions
        assert "apt" in instructions

    def test_rhel_instructions_with_sudo(self) -> None:
        """Generate RHEL instructions with sudo."""
        env = Environment(
            os_type="linux",
            linux_distro="rhel",
            has_sudo=True,
        )

        instructions = get_installation_instructions(env)

        assert "RHEL" in instructions or "CENTOS" in instructions or "FEDORA" in instructions
        assert "dnf" in instructions or "yum" in instructions

    def test_amazon_linux_instructions(self) -> None:
        """Generate Amazon Linux instructions."""
        env = Environment(
            os_type="linux",
            linux_distro="rhel",
            linux_distro_version="2023",
            has_sudo=True,
        )

        instructions = get_installation_instructions(env)

        assert "AMAZON LINUX" in instructions
        assert "dnf" in instructions or "yum" in instructions

    def test_alpine_instructions(self) -> None:
        """Generate Alpine Linux instructions."""
        env = Environment(
            os_type="linux",
            linux_distro="alpine",
        )

        instructions = get_installation_instructions(env)

        assert "ALPINE" in instructions
        assert "apk add" in instructions

    def test_arch_instructions(self) -> None:
        """Generate Arch Linux instructions."""
        env = Environment(
            os_type="linux",
            linux_distro="arch",
        )

        instructions = get_installation_instructions(env)

        assert "ARCH" in instructions
        assert "pacman" in instructions

    def test_suse_instructions(self) -> None:
        """Generate SUSE instructions."""
        env = Environment(
            os_type="linux",
            linux_distro="suse",
        )

        instructions = get_installation_instructions(env)

        assert "SUSE" in instructions or "OPENSUSE" in instructions
        assert "zypper" in instructions

    def test_generic_linux_instructions(self) -> None:
        """Generate generic Linux instructions for unknown distro."""
        env = Environment(
            os_type="linux",
            linux_distro="unknown",
        )

        instructions = get_installation_instructions(env)

        assert "nvm" in instructions


class TestMacOSInstructions:
    """Test instructions for macOS."""

    def test_macos_instructions(self) -> None:
        """Generate macOS instructions."""
        env = Environment(os_type="darwin")

        instructions = get_installation_instructions(env)

        assert "MACOS" in instructions
        assert "brew install node" in instructions
        assert "Official installer" in instructions
        assert "nvm" in instructions
        assert "nodejs.org" in instructions


class TestWindowsInstructions:
    """Test instructions for Windows."""

    def test_windows_instructions(self) -> None:
        """Generate Windows instructions."""
        env = Environment(os_type="windows")

        instructions = get_installation_instructions(env)

        assert "WINDOWS" in instructions
        assert "winget" in instructions
        assert "Chocolatey" in instructions or "choco" in instructions
        assert "Scoop" in instructions


class TestVenvInstructions:
    """Test virtual environment instructions."""

    def test_venv_instructions_included(self) -> None:
        """Include venv instructions when in virtualenv."""
        env = Environment(
            os_type="linux",
            linux_distro="ubuntu",
            is_venv=True,
        )

        instructions = get_installation_instructions(env)

        assert "nodeenv" in instructions
        assert "virtualenv" in instructions.lower()

    def test_conda_instructions_included(self) -> None:
        """Include venv instructions when in conda."""
        env = Environment(
            os_type="linux",
            linux_distro="ubuntu",
            is_conda=True,
        )

        instructions = get_installation_instructions(env)

        assert "nodeenv" in instructions


class TestNpxInstructions:
    """Test npx direct usage instructions."""

    def test_npx_instructions_always_included(self) -> None:
        """NPX instructions should always be included."""
        env = Environment(os_type="linux", linux_distro="ubuntu")

        instructions = get_installation_instructions(env)

        assert "npx promptfoo@latest" in instructions
        assert "DIRECT USAGE" in instructions


class TestErrorMessageFormat:
    """Test error message formatting."""

    def test_error_message_has_clear_header(self) -> None:
        """Error message should have a clear header."""
        env = Environment(os_type="linux", linux_distro="ubuntu")

        instructions = get_installation_instructions(env)

        assert "ERROR: promptfoo requires Node.js" in instructions
        assert "=" * 70 in instructions

    def test_multiline_output(self) -> None:
        """Instructions should be multi-line."""
        env = Environment(os_type="linux", linux_distro="ubuntu")

        instructions = get_installation_instructions(env)

        lines = instructions.split("\n")
        assert len(lines) > 5  # Should have multiple lines


class TestComplexEnvironments:
    """Test instructions for complex, combined environments."""

    def test_docker_github_actions_ubuntu(self) -> None:
        """Generate instructions for Docker in GitHub Actions on Ubuntu."""
        env = Environment(
            os_type="linux",
            linux_distro="ubuntu",
            is_docker=True,
            is_ci=True,
            ci_platform="github",
        )

        instructions = get_installation_instructions(env)

        # Should include both CI and Docker instructions
        assert "GITHUB" in instructions.upper()
        assert "DOCKER" in instructions.upper()

    def test_aws_ec2_rhel_with_venv(self) -> None:
        """Generate instructions for AWS EC2 RHEL with virtualenv."""
        env = Environment(
            os_type="linux",
            linux_distro="rhel",
            cloud_provider="aws",
            is_venv=True,
            has_sudo=True,
        )

        instructions = get_installation_instructions(env)

        # Should include RHEL and venv instructions
        assert "RHEL" in instructions or "CENTOS" in instructions or "FEDORA" in instructions
        assert "nodeenv" in instructions
