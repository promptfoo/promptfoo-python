"""
Environment detection for providing contextual Node.js installation instructions.

This module detects the operating system, Linux distribution, cloud provider,
container environment, CI/CD platform, and Python environment to provide
tailored installation instructions for Node.js.
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Environment:
    """Information about the current execution environment."""

    os_type: str  # "linux", "darwin", "windows"
    linux_distro: Optional[str] = None  # "ubuntu", "debian", "rhel", "fedora", "alpine", "arch", etc.
    linux_distro_version: Optional[str] = None  # e.g., "22.04", "11", "9"
    cloud_provider: Optional[str] = None  # "aws", "gcp", "azure"
    is_lambda: bool = False  # AWS Lambda
    is_cloud_function: bool = False  # GCP Cloud Functions or Azure Functions
    is_docker: bool = False
    is_kubernetes: bool = False
    is_wsl: bool = False  # Windows Subsystem for Linux
    is_ci: bool = False
    ci_platform: Optional[str] = None  # "github", "gitlab", "circleci", "jenkins", etc.
    is_venv: bool = False
    is_conda: bool = False
    has_sudo: bool = False  # Best guess if user has sudo access


def _detect_linux_distro() -> tuple[Optional[str], Optional[str]]:
    """
    Detect Linux distribution and version.

    Returns:
        Tuple of (distro_id, version) where distro_id is normalized
        (e.g., "ubuntu", "debian", "rhel", "alpine", "arch")
    """
    # Define known distros for normalization
    known_base_distros = {"ubuntu", "debian", "alpine", "arch", "fedora"}
    rhel_family = {"rhel", "centos", "rocky", "almalinux", "ol", "amzn"}
    suse_family = {"opensuse", "opensuse-leap", "opensuse-tumbleweed", "sles"}

    # Try /etc/os-release first, then /usr/lib/os-release (per freedesktop spec)
    for os_release_path in [Path("/etc/os-release"), Path("/usr/lib/os-release")]:
        if os_release_path.exists():
            try:
                with open(os_release_path) as f:
                    os_release = {}
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            key, _, value = line.partition("=")
                            # Remove quotes
                            value = value.strip('"').strip("'")
                            os_release[key] = value

                    distro_id = os_release.get("ID", "").lower()
                    version = os_release.get("VERSION_ID", "")
                    id_like = os_release.get("ID_LIKE", "").lower().split()

                    # Normalize distro IDs
                    if distro_id in known_base_distros:
                        return distro_id, version
                    elif distro_id in rhel_family:
                        # Oracle Linux (ol), Amazon Linux (amzn)
                        return "rhel", version
                    elif distro_id in suse_family:
                        return "suse", version

                    # Check ID_LIKE for derivative distributions (e.g., Pop!_OS, Raspbian, Mint)
                    if id_like:
                        for parent in id_like:
                            if parent in known_base_distros:
                                return parent, version
                            elif parent in rhel_family:
                                return "rhel", version
                            elif parent in suse_family:
                                return "suse", version

                    # Return the raw distro_id if we couldn't normalize it
                    return distro_id, version
            except OSError:
                pass

    # Fallback: check for specific files
    if Path("/etc/debian_version").exists():
        return "debian", None
    elif Path("/etc/redhat-release").exists():
        return "rhel", None
    elif Path("/etc/alpine-release").exists():
        return "alpine", None
    elif Path("/etc/arch-release").exists():
        return "arch", None

    return None, None


def _detect_cloud_provider() -> Optional[str]:
    """
    Detect if running on a cloud provider.

    Returns:
        One of "aws", "gcp", "azure", or None
    """
    # AWS detection
    # Check for EC2 metadata
    if Path("/sys/hypervisor/uuid").exists():
        try:
            with open("/sys/hypervisor/uuid") as f:
                uuid = f.read().strip()
                if uuid.startswith("ec2") or uuid.startswith("EC2"):
                    return "aws"
        except OSError:
            pass

    # Check AWS environment variables
    if os.getenv("AWS_EXECUTION_ENV") or os.getenv("AWS_REGION"):
        return "aws"

    # GCP detection
    # Check for GCP metadata
    if Path("/sys/class/dmi/id/product_name").exists():
        try:
            with open("/sys/class/dmi/id/product_name") as f:
                product = f.read().strip()
                if "Google" in product or "GCE" in product:
                    return "gcp"
        except OSError:
            pass

    # Check GCP environment variables
    if os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT"):
        return "gcp"

    # Azure detection
    if Path("/sys/class/dmi/id/sys_vendor").exists():
        try:
            with open("/sys/class/dmi/id/sys_vendor") as f:
                vendor = f.read().strip()
                # Could be Azure or Hyper-V, check for Azure-specific
                if "Microsoft Corporation" in vendor and Path("/var/lib/waagent").exists():
                    return "azure"
        except OSError:
            pass

    # Check Azure environment variables
    if os.getenv("AZURE_SUBSCRIPTION_ID") or os.getenv("WEBSITE_INSTANCE_ID"):
        return "azure"

    return None


def _detect_container() -> tuple[bool, bool]:
    """
    Detect if running in a container.

    Returns:
        Tuple of (is_docker, is_kubernetes)
    """
    is_docker = False
    is_kubernetes = False

    # Docker detection
    if Path("/.dockerenv").exists():
        is_docker = True

    # Also check cgroup
    if Path("/proc/1/cgroup").exists():
        try:
            with open("/proc/1/cgroup") as f:
                cgroup_content = f.read()
                if "docker" in cgroup_content or "containerd" in cgroup_content:
                    is_docker = True
        except OSError:
            pass

    # Kubernetes detection
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        is_kubernetes = True

    return is_docker, is_kubernetes


def _detect_wsl() -> bool:
    """
    Detect if running in Windows Subsystem for Linux (WSL).

    Returns:
        True if running in WSL, False otherwise
    """
    # Check for WSL environment variable
    if os.getenv("WSL_DISTRO_NAME") or os.getenv("WSL_INTEROP"):
        return True

    # Check /proc/version for Microsoft/WSL signatures
    if Path("/proc/version").exists():
        try:
            with open("/proc/version") as f:
                version_info = f.read().lower()
                if "microsoft" in version_info or "wsl" in version_info:
                    return True
        except OSError:
            pass

    # Check for Windows filesystem mounts (WSL mounts Windows drives at /mnt/)
    # This is less reliable but can catch WSL 1
    return Path("/mnt/c").exists() and Path("/proc/version").exists()


def _detect_ci() -> tuple[bool, Optional[str]]:
    """
    Detect if running in a CI/CD environment.

    Returns:
        Tuple of (is_ci, ci_platform)
    """
    ci_env_vars = {
        "GITHUB_ACTIONS": "github",
        "GITLAB_CI": "gitlab",
        "CIRCLECI": "circleci",
        "JENKINS_HOME": "jenkins",
        "TRAVIS": "travis",
        "BUILDKITE": "buildkite",
        "DRONE": "drone",
        "BITBUCKET_BUILD_NUMBER": "bitbucket",
        "TEAMCITY_VERSION": "teamcity",
        "TF_BUILD": "azure-devops",
    }

    for env_var, platform in ci_env_vars.items():
        if os.getenv(env_var):
            return True, platform

    # Generic CI detection
    if os.getenv("CI"):
        return True, None

    return False, None


def _detect_python_env() -> tuple[bool, bool]:
    """
    Detect Python virtual environment.

    Returns:
        Tuple of (is_venv, is_conda)
    """
    # venv/virtualenv detection
    is_venv = hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)

    # Conda detection
    is_conda = "CONDA_DEFAULT_ENV" in os.environ or "CONDA_PREFIX" in os.environ

    return is_venv, is_conda


def _has_sudo_access() -> bool:
    """
    Best-effort check if user likely has sudo access.

    Returns:
        True if user is root or likely has sudo, False otherwise
    """
    # Unix-like systems
    if hasattr(os, "geteuid"):
        # Root user
        if os.geteuid() == 0:
            return True

        # Check if sudo command exists
        import shutil

        return shutil.which("sudo") is not None

    # Windows - check if admin (requires elevation detection)
    if sys.platform == "win32":
        try:
            import ctypes

            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    return False


def detect_environment() -> Environment:
    """
    Detect the current execution environment.

    Returns:
        Environment object with detected platform information
    """
    os_type = sys.platform
    if os_type.startswith("linux"):
        os_type = "linux"
    elif os_type == "darwin":
        os_type = "darwin"
    elif os_type == "win32":
        os_type = "windows"

    # Linux-specific detection
    linux_distro = None
    linux_distro_version = None
    if os_type == "linux":
        linux_distro, linux_distro_version = _detect_linux_distro()

    # Cloud provider detection
    cloud_provider = _detect_cloud_provider()

    # Lambda and Cloud Functions detection
    is_lambda = os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None
    is_cloud_function = (
        os.getenv("FUNCTION_NAME") is not None  # GCP Cloud Functions
        or os.getenv("FUNCTIONS_WORKER_RUNTIME") is not None  # Azure Functions
    )

    # Container detection
    is_docker, is_kubernetes = False, False
    if os_type == "linux":
        is_docker, is_kubernetes = _detect_container()

    # WSL detection
    is_wsl = False
    if os_type == "linux":
        is_wsl = _detect_wsl()

    # CI detection
    is_ci, ci_platform = _detect_ci()

    # Python environment detection
    is_venv, is_conda = _detect_python_env()

    # Sudo detection
    has_sudo = _has_sudo_access()

    return Environment(
        os_type=os_type,
        linux_distro=linux_distro,
        linux_distro_version=linux_distro_version,
        cloud_provider=cloud_provider,
        is_lambda=is_lambda,
        is_cloud_function=is_cloud_function,
        is_docker=is_docker,
        is_kubernetes=is_kubernetes,
        is_wsl=is_wsl,
        is_ci=is_ci,
        ci_platform=ci_platform,
        is_venv=is_venv,
        is_conda=is_conda,
        has_sudo=has_sudo,
    )
