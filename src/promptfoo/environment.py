"""Detect only the environment details that change the missing-Node help."""

import os
import platform
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Environment:
    """Platform information used by the Node installation instructions."""

    os_type: str
    linux_distro: str | None = None
    linux_distro_version: str | None = None
    is_docker: bool = False
    is_wsl: bool = False
    ci_platform: str | None = None
    serverless: str | None = None


def _read_probe(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return ""


def _linux_release() -> tuple[str | None, str | None]:
    try:
        release = platform.freedesktop_os_release()
    except OSError:
        return None, None

    distro = release.get("ID", "").lower()
    version = release.get("VERSION_ID") or None
    family = [distro, *release.get("ID_LIKE", "").lower().split()]
    if "alpine" in family:
        return "alpine", version
    if distro in ("amzn", "amazon"):
        return "amzn", version
    return distro or None, version


def _in_container() -> bool:
    if os.environ.get("KUBERNETES_SERVICE_HOST") or Path("/.dockerenv").is_file():
        return True
    cgroup = _read_probe("/proc/1/cgroup").lower()
    return any(runtime in cgroup for runtime in ("docker", "containerd", "kubepods", "crio"))


def _ci_platform() -> str | None:
    for variable, name in (
        ("GITHUB_ACTIONS", "GitHub Actions"),
        ("GITLAB_CI", "GitLab CI"),
        ("CIRCLECI", "CircleCI"),
        ("JENKINS_URL", "Jenkins"),
        ("BUILDKITE", "Buildkite"),
        ("TF_BUILD", "Azure Pipelines"),
        ("CI", "CI"),
    ):
        if os.environ.get(variable):
            return name
    return None


def _serverless() -> str | None:
    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return "aws"
    if os.environ.get("FUNCTIONS_WORKER_RUNTIME"):
        return "azure"
    if os.environ.get("FUNCTION_TARGET") or os.environ.get("FUNCTION_NAME"):
        return "google"
    return None


def detect_environment() -> Environment:
    """Return the current platform and the deployment hints relevant to installation."""
    os_type = "linux" if sys.platform.startswith("linux") else {"win32": "windows"}.get(sys.platform, sys.platform)
    distro, version = _linux_release() if os_type == "linux" else (None, None)
    is_wsl = os_type == "linux" and bool(
        os.environ.get("WSL_DISTRO_NAME")
        or os.environ.get("WSL_INTEROP")
        or "microsoft" in _read_probe("/proc/sys/kernel/osrelease").lower()
    )
    return Environment(
        os_type=os_type,
        linux_distro=distro,
        linux_distro_version=version,
        is_docker=os_type == "linux" and _in_container(),
        is_wsl=is_wsl,
        ci_platform=_ci_platform(),
        serverless=_serverless(),
    )
