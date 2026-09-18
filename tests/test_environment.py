from pathlib import Path
from unittest.mock import MagicMock

import pytest

from promptfoo import environment


@pytest.fixture(autouse=True)
def isolated_probes(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "GITHUB_ACTIONS",
        "GITLAB_CI",
        "CIRCLECI",
        "JENKINS_URL",
        "JENKINS_HOME",
        "BUILDKITE",
        "TF_BUILD",
        "TEAMCITY_VERSION",
        "TRAVIS",
        "DRONE",
        "BITBUCKET_BUILD_NUMBER",
        "CONTINUOUS_INTEGRATION",
        "CI",
        "AWS_LAMBDA_FUNCTION_NAME",
        "FUNCTIONS_WORKER_RUNTIME",
        "FUNCTION_TARGET",
        "FUNCTION_NAME",
        "WSL_DISTRO_NAME",
        "WSL_INTEROP",
        "KUBERNETES_SERVICE_HOST",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(environment, "_read_probe", lambda path: "")
    monkeypatch.setattr(Path, "is_file", lambda path: False)


@pytest.mark.parametrize(
    "release, expected",
    [
        ({"ID": "alpine", "VERSION_ID": "3.24"}, ("alpine", "3.24")),
        ({"ID": "derivative", "ID_LIKE": "alpine", "VERSION_ID": "1"}, ("alpine", "1")),
        ({"ID": "amzn", "ID_LIKE": "fedora", "VERSION_ID": "2023"}, ("amzn", "2023")),
        ({"ID": "amzn", "VERSION_ID": "2"}, ("amzn", "2")),
        ({"ID": "ubuntu", "VERSION_ID": "24.04"}, ("ubuntu", "24.04")),
        ({"ID": "unknown"}, ("unknown", None)),
        ({}, (None, None)),
    ],
)
def test_reads_the_standard_linux_release(
    monkeypatch: pytest.MonkeyPatch, release: dict[str, str], expected: tuple[str | None, str | None]
) -> None:
    monkeypatch.setattr(environment.platform, "freedesktop_os_release", lambda: release)
    assert environment._linux_release() == expected


def test_missing_linux_release_does_not_prevent_generic_help(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(environment.platform, "freedesktop_os_release", MagicMock(side_effect=OSError))
    assert environment._linux_release() == (None, None)


@pytest.mark.parametrize("platform, expected", [("win32", "windows"), ("darwin", "darwin"), ("freebsd14", "freebsd14")])
def test_non_linux_platforms_do_not_probe_linux_files(
    monkeypatch: pytest.MonkeyPatch, platform: str, expected: str
) -> None:
    monkeypatch.setattr(environment.sys, "platform", platform)
    probe = MagicMock(side_effect=AssertionError("Linux probe ran on another OS"))
    monkeypatch.setattr(environment, "_linux_release", probe)
    monkeypatch.setattr(environment, "_in_container", probe)
    monkeypatch.setattr(environment, "_read_probe", probe)
    assert environment.detect_environment() == environment.Environment(os_type=expected)


def test_kubernetes_is_used_to_show_container_help(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(environment.sys, "platform", "linux")
    monkeypatch.setattr(environment.platform, "freedesktop_os_release", lambda: {"ID": "alpine"})
    monkeypatch.setattr(environment, "_read_probe", lambda path: "0::/" if path == "/proc/1/cgroup" else "")
    monkeypatch.setenv("KUBERNETES_SERVICE_HOST", "10.0.0.1")

    result = environment.detect_environment()

    assert result.is_docker
    assert result.linux_distro == "alpine"


@pytest.mark.parametrize("runtime", ["docker", "containerd", "kubepods", "crio"])
def test_container_runtime_can_also_be_detected_from_cgroups(monkeypatch: pytest.MonkeyPatch, runtime: str) -> None:
    monkeypatch.setattr(environment, "_read_probe", lambda path: f"0::/{runtime}/container")
    assert environment._in_container()


def test_docker_marker_works_without_cgroup_names(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Path, "is_file", lambda path: str(path).replace("\\", "/").endswith("/.dockerenv"))
    assert environment._in_container()


@pytest.mark.parametrize("use_environment", [True, False])
def test_detects_wsl_only_on_linux(monkeypatch: pytest.MonkeyPatch, use_environment: bool) -> None:
    monkeypatch.setattr(environment.sys, "platform", "linux")
    monkeypatch.setattr(environment.platform, "freedesktop_os_release", lambda: {"ID": "ubuntu"})
    if use_environment:
        monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")
    else:
        monkeypatch.setattr(environment, "_read_probe", lambda path: "6.6-Microsoft-standard-WSL2")
    assert environment.detect_environment().is_wsl


@pytest.mark.parametrize(
    "variable, expected",
    [
        ("GITHUB_ACTIONS", "GitHub Actions"),
        ("GITLAB_CI", "GitLab CI"),
        ("CIRCLECI", "CircleCI"),
        ("JENKINS_HOME", "Jenkins"),
        ("TEAMCITY_VERSION", "TeamCity"),
        ("TRAVIS", "Travis CI"),
        ("DRONE", "Drone CI"),
        ("BITBUCKET_BUILD_NUMBER", "Bitbucket Pipelines"),
        ("CONTINUOUS_INTEGRATION", "CI"),
        ("CI", "CI"),
    ],
)
def test_detects_ci_guidance(monkeypatch: pytest.MonkeyPatch, variable: str, expected: str) -> None:
    monkeypatch.setenv(variable, "1")
    assert environment._ci_platform() == expected


@pytest.mark.parametrize(
    "variable, expected",
    [("AWS_LAMBDA_FUNCTION_NAME", "aws"), ("FUNCTIONS_WORKER_RUNTIME", "azure"), ("FUNCTION_TARGET", "google")],
)
def test_detects_serverless_from_provider_supplied_variables(
    monkeypatch: pytest.MonkeyPatch, variable: str, expected: str
) -> None:
    monkeypatch.setenv(variable, "configured")
    assert environment._serverless() == expected
