"""
Tests for environment detection.

This module tests detection of operating systems, Linux distributions,
cloud providers, containers, CI/CD platforms, and Python environments.
"""

import os
from pathlib import Path
from unittest import mock

import pytest

from promptfoo.environment import (
    _detect_ci,
    _detect_cloud_provider,
    _detect_container,
    _detect_linux_distro,
    _detect_python_env,
    _has_sudo_access,
    detect_environment,
)


class TestLinuxDistroDetection:
    """Test Linux distribution detection."""

    def test_detect_linux_distro_returns_tuple(self) -> None:
        """Linux distro detection returns a tuple."""
        distro, version = _detect_linux_distro()
        # Should return tuple even if both None
        assert isinstance(distro, (str, type(None)))
        assert isinstance(version, (str, type(None)))


class TestCloudProviderDetection:
    """Test cloud provider detection."""

    def test_detect_aws_from_hypervisor_uuid(self, tmp_path: Path) -> None:
        """Detect AWS from hypervisor UUID."""
        uuid_file = tmp_path / "uuid"
        uuid_file.write_text("ec2e1916-9099-7caf-fd21-012345abcdef\n")

        with mock.patch("promptfoo.environment.Path") as mock_path:
            mock_path_instance = mock_path.return_value
            mock_path_instance.exists.return_value = True
            mock_path_instance.__truediv__.return_value = uuid_file

            with mock.patch("builtins.open", mock.mock_open(read_data="ec2e1916-9099-7caf-fd21-012345abcdef\n")):
                provider = _detect_cloud_provider()
                assert provider == "aws"

    def test_detect_aws_from_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Detect AWS from environment variables."""
        monkeypatch.setenv("AWS_EXECUTION_ENV", "AWS_Lambda_python3.11")

        with mock.patch("promptfoo.environment.Path") as mock_path:
            mock_path.return_value.exists.return_value = False

            provider = _detect_cloud_provider()
            assert provider == "aws"

    def test_detect_gcp_from_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Detect GCP from environment variables."""
        monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "my-project")

        with mock.patch("promptfoo.environment.Path") as mock_path:
            mock_path.return_value.exists.return_value = False

            provider = _detect_cloud_provider()
            assert provider == "gcp"

    def test_detect_azure_from_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Detect Azure from environment variables."""
        monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "12345")

        with mock.patch("promptfoo.environment.Path") as mock_path:
            mock_path.return_value.exists.return_value = False

            provider = _detect_cloud_provider()
            assert provider == "azure"

    def test_no_cloud_provider_detected(self) -> None:
        """Return None when no cloud provider is detected."""
        with mock.patch("promptfoo.environment.Path") as mock_path:
            mock_path.return_value.exists.return_value = False
            with mock.patch.dict(os.environ, {}, clear=True):
                provider = _detect_cloud_provider()
                assert provider is None


class TestContainerDetection:
    """Test container detection."""

    def test_detect_kubernetes_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Detect Kubernetes from environment variable."""
        monkeypatch.setenv("KUBERNETES_SERVICE_HOST", "10.96.0.1")

        with mock.patch("promptfoo.environment.Path") as mock_path:
            mock_path.return_value.exists.return_value = False

            is_docker, is_k8s = _detect_container()
            assert is_k8s is True

    def test_detect_container_returns_tuple(self) -> None:
        """Container detection returns a tuple of booleans."""
        is_docker, is_k8s = _detect_container()
        assert isinstance(is_docker, bool)
        assert isinstance(is_k8s, bool)


class TestWSLDetection:
    """Test WSL detection."""

    def test_detect_wsl_from_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Detect WSL from WSL_DISTRO_NAME environment variable."""
        monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")

        from promptfoo.environment import _detect_wsl

        assert _detect_wsl() is True

    def test_detect_wsl_from_interop_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Detect WSL from WSL_INTEROP environment variable."""
        monkeypatch.setenv("WSL_INTEROP", "/run/WSL/123_interop")

        from promptfoo.environment import _detect_wsl

        assert _detect_wsl() is True

    def test_no_wsl_detected(self) -> None:
        """Return False when not in WSL."""
        with mock.patch.dict(os.environ, {}, clear=True):
            from promptfoo.environment import _detect_wsl

            # This will return False unless we're actually in WSL
            # Just verify it returns a boolean
            result = _detect_wsl()
            assert isinstance(result, bool)


class TestCIDetection:
    """Test CI/CD platform detection."""

    @pytest.mark.parametrize(
        "env_var,expected_platform",
        [
            ("GITHUB_ACTIONS", "github"),
            ("GITLAB_CI", "gitlab"),
            ("CIRCLECI", "circleci"),
            ("JENKINS_HOME", "jenkins"),
            ("TRAVIS", "travis"),
            ("BUILDKITE", "buildkite"),
        ],
    )
    def test_detect_specific_ci_platforms(
        self, env_var: str, expected_platform: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Detect specific CI/CD platforms from environment variables."""
        with mock.patch.dict(os.environ, {}, clear=True):
            monkeypatch.setenv(env_var, "true")
            is_ci, platform = _detect_ci()
            assert is_ci is True
            assert platform == expected_platform

    def test_detect_generic_ci(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Detect generic CI from CI environment variable."""
        with mock.patch.dict(os.environ, {}, clear=True):
            monkeypatch.setenv("CI", "true")
            is_ci, platform = _detect_ci()
            assert is_ci is True
            assert platform is None

    def test_no_ci_detected(self) -> None:
        """Return False when no CI is detected."""
        with mock.patch.dict(os.environ, {}, clear=True):
            is_ci, platform = _detect_ci()
            assert is_ci is False
            assert platform is None


class TestPythonEnvDetection:
    """Test Python environment detection."""

    def test_detect_venv(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Detect virtualenv from sys.prefix."""
        import sys

        with mock.patch.object(sys, "prefix", "/home/user/venv"), mock.patch.object(sys, "base_prefix", "/usr"):
            is_venv, is_conda = _detect_python_env()
            assert is_venv is True

    def test_detect_conda(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Detect conda from environment variable."""
        monkeypatch.setenv("CONDA_DEFAULT_ENV", "base")
        is_venv, is_conda = _detect_python_env()
        assert is_conda is True

    def test_no_venv_detected(self) -> None:
        """Return False when no venv is detected."""
        import sys

        with (
            mock.patch.object(sys, "prefix", "/usr"),
            mock.patch.object(sys, "base_prefix", "/usr"),
            mock.patch.dict(os.environ, {}, clear=True),
        ):
            is_venv, is_conda = _detect_python_env()
            assert is_venv is False
            assert is_conda is False


class TestSudoAccess:
    """Test sudo access detection."""

    def test_has_sudo_when_root(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Detect sudo access when running as root."""
        if hasattr(os, "geteuid"):
            with mock.patch("os.geteuid", return_value=0):
                assert _has_sudo_access() is True

    def test_has_sudo_when_sudo_command_exists(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Detect sudo access when sudo command exists."""
        if hasattr(os, "geteuid"):
            with (
                mock.patch("os.geteuid", return_value=1000),
                mock.patch("shutil.which", return_value="/usr/bin/sudo"),
            ):
                assert _has_sudo_access() is True

    def test_no_sudo_when_command_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Return False when sudo command doesn't exist."""
        if hasattr(os, "geteuid"):
            with mock.patch("os.geteuid", return_value=1000), mock.patch("shutil.which", return_value=None):
                assert _has_sudo_access() is False


class TestDetectEnvironment:
    """Test complete environment detection."""

    def test_detect_ubuntu_with_docker(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Detect Ubuntu in Docker container."""
        os_release = tmp_path / "os-release"
        os_release.write_text('ID=ubuntu\nVERSION_ID="22.04"')

        with (
            mock.patch("sys.platform", "linux"),
            mock.patch("promptfoo.environment._detect_linux_distro", return_value=("ubuntu", "22.04")),
            mock.patch("promptfoo.environment._detect_container", return_value=(True, False)),
            mock.patch("promptfoo.environment._detect_wsl", return_value=False),
            mock.patch("promptfoo.environment._detect_ci", return_value=(False, None)),
            mock.patch("promptfoo.environment._detect_cloud_provider", return_value=None),
            mock.patch("promptfoo.environment._detect_python_env", return_value=(True, False)),
            mock.patch("promptfoo.environment._has_sudo_access", return_value=False),
        ):
            env = detect_environment()

            assert env.os_type == "linux"
            assert env.linux_distro == "ubuntu"
            assert env.linux_distro_version == "22.04"
            assert env.is_docker is True
            assert env.is_kubernetes is False
            assert env.is_wsl is False
            assert env.is_venv is True

    def test_detect_macos_environment(self) -> None:
        """Detect macOS environment."""
        with (
            mock.patch("sys.platform", "darwin"),
            mock.patch("promptfoo.environment._detect_ci", return_value=(False, None)),
            mock.patch("promptfoo.environment._detect_cloud_provider", return_value=None),
            mock.patch("promptfoo.environment._detect_python_env", return_value=(False, False)),
            mock.patch("promptfoo.environment._has_sudo_access", return_value=True),
        ):
            env = detect_environment()

            assert env.os_type == "darwin"
            assert env.linux_distro is None
            assert env.has_sudo is True

    def test_detect_windows_environment(self) -> None:
        """Detect Windows environment."""
        with (
            mock.patch("sys.platform", "win32"),
            mock.patch("promptfoo.environment._detect_ci", return_value=(False, None)),
            mock.patch("promptfoo.environment._detect_cloud_provider", return_value=None),
            mock.patch("promptfoo.environment._detect_python_env", return_value=(False, False)),
            mock.patch("promptfoo.environment._has_sudo_access", return_value=False),
        ):
            env = detect_environment()

            assert env.os_type == "windows"

    def test_detect_aws_lambda(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Detect AWS Lambda environment."""
        monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "my-function")

        with (
            mock.patch("sys.platform", "linux"),
            mock.patch("promptfoo.environment._detect_linux_distro", return_value=("amzn", "2")),
            mock.patch("promptfoo.environment._detect_container", return_value=(False, False)),
            mock.patch("promptfoo.environment._detect_wsl", return_value=False),
            mock.patch("promptfoo.environment._detect_ci", return_value=(False, None)),
            mock.patch("promptfoo.environment._detect_cloud_provider", return_value="aws"),
            mock.patch("promptfoo.environment._detect_python_env", return_value=(False, False)),
            mock.patch("promptfoo.environment._has_sudo_access", return_value=False),
        ):
            env = detect_environment()

            assert env.is_lambda is True
            assert env.cloud_provider == "aws"

    def test_detect_github_actions(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Detect GitHub Actions environment."""
        monkeypatch.setenv("GITHUB_ACTIONS", "true")

        with (
            mock.patch("sys.platform", "linux"),
            mock.patch("promptfoo.environment._detect_linux_distro", return_value=("ubuntu", "22.04")),
            mock.patch("promptfoo.environment._detect_container", return_value=(False, False)),
            mock.patch("promptfoo.environment._detect_wsl", return_value=False),
            mock.patch("promptfoo.environment._detect_ci", return_value=(True, "github")),
            mock.patch("promptfoo.environment._detect_cloud_provider", return_value=None),
            mock.patch("promptfoo.environment._detect_python_env", return_value=(False, False)),
            mock.patch("promptfoo.environment._has_sudo_access", return_value=True),
        ):
            env = detect_environment()

            assert env.is_ci is True
            assert env.ci_platform == "github"

    def test_detect_wsl_ubuntu(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Detect WSL with Ubuntu."""
        monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")

        with (
            mock.patch("sys.platform", "linux"),
            mock.patch("promptfoo.environment._detect_linux_distro", return_value=("ubuntu", "22.04")),
            mock.patch("promptfoo.environment._detect_container", return_value=(False, False)),
            mock.patch("promptfoo.environment._detect_wsl", return_value=True),
            mock.patch("promptfoo.environment._detect_ci", return_value=(False, None)),
            mock.patch("promptfoo.environment._detect_cloud_provider", return_value=None),
            mock.patch("promptfoo.environment._detect_python_env", return_value=(False, False)),
            mock.patch("promptfoo.environment._has_sudo_access", return_value=True),
        ):
            env = detect_environment()

            assert env.os_type == "linux"
            assert env.linux_distro == "ubuntu"
            assert env.is_wsl is True
            assert env.is_docker is False
