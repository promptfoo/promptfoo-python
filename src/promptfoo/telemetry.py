"""
Telemetry module for the promptfoo Python wrapper.

Sends anonymous usage analytics to PostHog to help improve promptfoo.
Telemetry can be disabled by setting PROMPTFOO_DISABLE_TELEMETRY=1.
"""

import atexit
import os
import platform
import sys
import uuid
from pathlib import Path
from typing import Any, Optional

import yaml
from posthog import Posthog

from . import __version__

# PostHog configuration - same as the main promptfoo TypeScript project.
# NOTE: This is an intentionally public PostHog project API key:
# - Safe to commit to source control (client-side telemetry key)
# - Only allows sending anonymous usage events to the promptfoo PostHog project
# - Does not grant administrative access to the PostHog account
# - Abuse is mitigated by PostHog's built-in rate limiting
# - Telemetry can be disabled via PROMPTFOO_DISABLE_TELEMETRY=1
_POSTHOG_HOST = "https://a.promptfoo.app"
_POSTHOG_KEY = "phc_E5n5uHnDo2eREJL1uqX1cIlbkoRby4yFWt3V94HqRRg"


def _get_env_bool(name: str) -> bool:
    """Check if an environment variable is set to a truthy value."""
    value = os.environ.get(name, "").lower()
    return value in ("1", "true", "yes", "on")


def _is_ci() -> bool:
    """Detect if running in a CI environment."""
    ci_env_vars = [
        "CI",
        "CONTINUOUS_INTEGRATION",
        "GITHUB_ACTIONS",
        "GITLAB_CI",
        "CIRCLECI",
        "TRAVIS",
        "JENKINS_URL",
        "BUILDKITE",
        "TEAMCITY_VERSION",
        "TF_BUILD",  # Azure Pipelines
    ]
    return any(os.environ.get(var) for var in ci_env_vars)


def _get_config_dir() -> Path:
    """Get the promptfoo config directory path."""
    return Path.home() / ".promptfoo"


def _read_global_config() -> dict[str, Any]:
    """Read the global promptfoo config from ~/.promptfoo/promptfoo.yaml."""
    config_file = _get_config_dir() / "promptfoo.yaml"
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)
                return config if isinstance(config, dict) else {}
        except Exception:
            return {}
    return {}


def _write_global_config(config: dict[str, Any]) -> None:
    """Write the global promptfoo config to ~/.promptfoo/promptfoo.yaml."""
    config_dir = _get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "promptfoo.yaml"
    try:
        with open(config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
    except Exception:
        pass  # Silently fail - telemetry should never break the CLI


def _get_user_id() -> str:
    """Get or create a unique user ID stored in the global config."""
    config = _read_global_config()
    user_id = config.get("id")

    if not user_id:
        user_id = str(uuid.uuid4())
        config["id"] = user_id
        _write_global_config(config)

    return user_id


def _get_user_email() -> Optional[str]:
    """Get the user email from the global config if set."""
    config = _read_global_config()
    account = config.get("account", {})
    return account.get("email") if isinstance(account, dict) else None


class _Telemetry:
    """Internal telemetry client for the promptfoo Python wrapper."""

    def __init__(self) -> None:
        self._client: Optional[Posthog] = None
        self._user_id: Optional[str] = None
        self._email: Optional[str] = None
        self._initialized = False

    @property
    def _disabled(self) -> bool:
        """Check if telemetry is disabled."""
        return _get_env_bool("PROMPTFOO_DISABLE_TELEMETRY") or _get_env_bool("IS_TESTING")

    def _ensure_initialized(self) -> None:
        """Lazily initialize the telemetry client."""
        if self._initialized:
            return

        self._initialized = True

        if self._disabled:
            return

        try:
            self._user_id = _get_user_id()
            self._email = _get_user_email()
            self._client = Posthog(
                project_api_key=_POSTHOG_KEY,
                host=_POSTHOG_HOST,
            )
        except Exception:
            self._client = None  # Silently fail

    def record(self, event_name: str, properties: Optional[dict[str, Any]] = None) -> None:
        """Record a telemetry event."""
        if self._disabled:
            return

        self._ensure_initialized()

        if not self._client or not self._user_id:
            return

        try:
            enriched_properties: dict[str, Any] = {
                **(properties or {}),
                "packageVersion": __version__,
                "pythonVersion": platform.python_version(),
                "platform": sys.platform,
                "isRunningInCi": _is_ci(),
                "source": "python-wrapper",
            }

            # Only set email if present
            if self._email:
                enriched_properties["$set"] = {"email": self._email}

            self._client.capture(
                event=event_name,
                distinct_id=self._user_id,
                properties=enriched_properties,
            )
        except Exception:
            pass  # Silently fail - telemetry should never break the CLI

    def shutdown(self) -> None:
        """Shutdown the telemetry client and flush any pending events."""
        if self._client:
            try:
                self._client.flush()  # type: ignore[no-untyped-call]
                self._client.shutdown()  # type: ignore[no-untyped-call]
            except Exception:
                pass  # Silently fail
            finally:
                self._client = None


# Global singleton instance
_telemetry: Optional[_Telemetry] = None


def _get_telemetry() -> _Telemetry:
    """Get the global telemetry instance."""
    global _telemetry
    if _telemetry is None:
        _telemetry = _Telemetry()
        atexit.register(_telemetry.shutdown)
    return _telemetry


def record_wrapper_used(method: str) -> None:
    """
    Record that the Python wrapper was used.

    Args:
        method: The execution method used - "global" for global promptfoo install,
                "npx" for npx fallback, or "error" if execution failed.
    """
    _get_telemetry().record("wrapper_used", {"method": method, "wrapperType": "python"})
