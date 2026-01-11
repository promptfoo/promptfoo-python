"""
Tests for telemetry module.

This module tests the PostHog telemetry integration including:
- Environment variable opt-out
- User ID generation and persistence
- Event recording
- Error handling (graceful failures)
"""

import os
from pathlib import Path
from unittest import mock

import pytest

from promptfoo.telemetry import (
    _get_config_dir,
    _get_env_bool,
    _get_user_email,
    _get_user_id,
    _is_ci,
    _read_global_config,
    _Telemetry,
    _write_global_config,
    record_wrapper_used,
)


class TestGetEnvBool:
    """Test _get_env_bool helper function."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("1", True),
            ("true", True),
            ("TRUE", True),
            ("True", True),
            ("yes", True),
            ("YES", True),
            ("on", True),
            ("ON", True),
            ("0", False),
            ("false", False),
            ("no", False),
            ("off", False),
            ("", False),
            ("random", False),
        ],
    )
    def test_env_bool_values(self, value: str, expected: bool, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test various environment variable values."""
        monkeypatch.setenv("TEST_VAR", value)
        assert _get_env_bool("TEST_VAR") == expected

    def test_env_bool_unset(self) -> None:
        """Test unset environment variable returns False."""
        with mock.patch.dict(os.environ, {}, clear=True):
            assert _get_env_bool("NONEXISTENT_VAR") is False


class TestCIDetection:
    """Test CI environment detection."""

    @pytest.mark.parametrize(
        "env_var",
        [
            "CI",
            "CONTINUOUS_INTEGRATION",
            "GITHUB_ACTIONS",
            "GITLAB_CI",
            "CIRCLECI",
            "TRAVIS",
            "JENKINS_URL",
            "BUILDKITE",
            "TEAMCITY_VERSION",
            "TF_BUILD",
        ],
    )
    def test_detect_ci_from_env_vars(self, env_var: str, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test CI detection from various environment variables."""
        with mock.patch.dict(os.environ, {}, clear=True):
            monkeypatch.setenv(env_var, "true")
            assert _is_ci() is True

    def test_no_ci_detected(self) -> None:
        """Test no CI detected when environment variables are not set."""
        with mock.patch.dict(os.environ, {}, clear=True):
            assert _is_ci() is False


class TestConfigDir:
    """Test config directory functions."""

    def test_get_config_dir(self) -> None:
        """Test config directory path."""
        config_dir = _get_config_dir()
        assert config_dir == Path.home() / ".promptfoo"


class TestGlobalConfig:
    """Test global config read/write functions."""

    def test_read_config_missing_file(self) -> None:
        """Test reading config when file doesn't exist."""
        with mock.patch("promptfoo.telemetry._get_config_dir") as mock_dir:
            mock_dir.return_value = Path("/nonexistent/path")
            config = _read_global_config()
            assert config == {}

    def test_read_config_valid_yaml(self, tmp_path: Path) -> None:
        """Test reading valid YAML config."""
        config_file = tmp_path / "promptfoo.yaml"
        config_file.write_text("id: test-uuid-123\naccount:\n  email: test@example.com\n")

        with mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path):
            config = _read_global_config()
            assert config["id"] == "test-uuid-123"
            assert config["account"]["email"] == "test@example.com"

    def test_read_config_invalid_yaml(self, tmp_path: Path) -> None:
        """Test reading invalid YAML config returns empty dict."""
        config_file = tmp_path / "promptfoo.yaml"
        config_file.write_text("invalid: yaml: content:")

        with mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path):
            config = _read_global_config()
            # Should return empty dict on parse error
            assert config == {}

    def test_read_config_non_dict_yaml(self, tmp_path: Path) -> None:
        """Test reading YAML that isn't a dict returns empty dict."""
        config_file = tmp_path / "promptfoo.yaml"
        config_file.write_text("- item1\n- item2\n")

        with mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path):
            config = _read_global_config()
            assert config == {}

    def test_write_config(self, tmp_path: Path) -> None:
        """Test writing config to file."""
        with mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path):
            _write_global_config({"id": "test-uuid", "key": "value"})

            config_file = tmp_path / "promptfoo.yaml"
            assert config_file.exists()
            content = config_file.read_text()
            assert "id: test-uuid" in content
            assert "key: value" in content

    def test_write_config_creates_directory(self, tmp_path: Path) -> None:
        """Test writing config creates parent directory."""
        nested_dir = tmp_path / "nested" / ".promptfoo"
        with mock.patch("promptfoo.telemetry._get_config_dir", return_value=nested_dir):
            _write_global_config({"id": "test-uuid"})

            config_file = nested_dir / "promptfoo.yaml"
            assert config_file.exists()


class TestUserId:
    """Test user ID functions."""

    def test_get_user_id_existing(self, tmp_path: Path) -> None:
        """Test getting existing user ID from config."""
        config_file = tmp_path / "promptfoo.yaml"
        config_file.write_text("id: existing-uuid-456\n")

        with mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path):
            user_id = _get_user_id()
            assert user_id == "existing-uuid-456"

    def test_get_user_id_generates_new(self, tmp_path: Path) -> None:
        """Test generating new user ID when none exists."""
        with mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path):
            user_id = _get_user_id()

            # Should generate a UUID
            assert len(user_id) == 36  # UUID format
            assert "-" in user_id

            # Should persist to config
            config_file = tmp_path / "promptfoo.yaml"
            assert config_file.exists()
            content = config_file.read_text()
            assert user_id in content


class TestUserEmail:
    """Test user email functions."""

    def test_get_user_email_exists(self, tmp_path: Path) -> None:
        """Test getting existing user email from config."""
        config_file = tmp_path / "promptfoo.yaml"
        config_file.write_text("account:\n  email: user@example.com\n")

        with mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path):
            email = _get_user_email()
            assert email == "user@example.com"

    def test_get_user_email_missing(self, tmp_path: Path) -> None:
        """Test getting email when not set returns None."""
        config_file = tmp_path / "promptfoo.yaml"
        config_file.write_text("id: test-uuid\n")

        with mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path):
            email = _get_user_email()
            assert email is None

    def test_get_user_email_invalid_account(self, tmp_path: Path) -> None:
        """Test getting email when account is not a dict."""
        config_file = tmp_path / "promptfoo.yaml"
        config_file.write_text("account: invalid\n")

        with mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path):
            email = _get_user_email()
            assert email is None


class TestTelemetryClass:
    """Test _Telemetry class."""

    def test_disabled_by_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test telemetry is disabled by PROMPTFOO_DISABLE_TELEMETRY."""
        monkeypatch.setenv("PROMPTFOO_DISABLE_TELEMETRY", "1")
        telemetry = _Telemetry()
        assert telemetry._disabled is True

    def test_disabled_by_is_testing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test telemetry is disabled by IS_TESTING."""
        monkeypatch.setenv("IS_TESTING", "1")
        telemetry = _Telemetry()
        assert telemetry._disabled is True

    def test_enabled_by_default(self) -> None:
        """Test telemetry is enabled by default."""
        with mock.patch.dict(os.environ, {}, clear=True):
            telemetry = _Telemetry()
            assert telemetry._disabled is False

    def test_record_when_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test record does nothing when disabled."""
        monkeypatch.setenv("PROMPTFOO_DISABLE_TELEMETRY", "1")
        telemetry = _Telemetry()

        # Should not raise or initialize client
        telemetry.record("test_event", {"key": "value"})
        assert telemetry._client is None
        assert telemetry._initialized is False

    def test_record_initializes_client(self, tmp_path: Path) -> None:
        """Test record lazily initializes the client."""
        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path),
            mock.patch("promptfoo.telemetry.Posthog") as mock_posthog,
        ):
            mock_client = mock.Mock()
            mock_posthog.return_value = mock_client

            telemetry = _Telemetry()
            assert telemetry._initialized is False

            telemetry.record("test_event", {"key": "value"})

            assert telemetry._initialized is True
            assert telemetry._client is mock_client
            mock_client.capture.assert_called_once()

    def test_record_enriches_properties(self, tmp_path: Path) -> None:
        """Test record adds enriched properties."""
        config_file = tmp_path / "promptfoo.yaml"
        config_file.write_text("id: test-user-id\n")

        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path),
            mock.patch("promptfoo.telemetry.Posthog") as mock_posthog,
        ):
            mock_client = mock.Mock()
            mock_posthog.return_value = mock_client

            telemetry = _Telemetry()
            telemetry.record("test_event", {"custom": "prop"})

            call_args = mock_client.capture.call_args
            properties = call_args.kwargs["properties"]

            assert properties["custom"] == "prop"
            assert "packageVersion" in properties
            assert "pythonVersion" in properties
            assert "platform" in properties
            assert "isRunningInCi" in properties
            assert properties["source"] == "python-wrapper"

    def test_record_includes_email_when_present(self, tmp_path: Path) -> None:
        """Test record includes $set with email when present."""
        config_file = tmp_path / "promptfoo.yaml"
        config_file.write_text("id: test-user-id\naccount:\n  email: test@example.com\n")

        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path),
            mock.patch("promptfoo.telemetry.Posthog") as mock_posthog,
        ):
            mock_client = mock.Mock()
            mock_posthog.return_value = mock_client

            telemetry = _Telemetry()
            telemetry.record("test_event")

            call_args = mock_client.capture.call_args
            properties = call_args.kwargs["properties"]

            assert properties["$set"] == {"email": "test@example.com"}

    def test_record_omits_set_when_no_email(self, tmp_path: Path) -> None:
        """Test record does not include $set when no email."""
        config_file = tmp_path / "promptfoo.yaml"
        config_file.write_text("id: test-user-id\n")

        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path),
            mock.patch("promptfoo.telemetry.Posthog") as mock_posthog,
        ):
            mock_client = mock.Mock()
            mock_posthog.return_value = mock_client

            telemetry = _Telemetry()
            telemetry.record("test_event")

            call_args = mock_client.capture.call_args
            properties = call_args.kwargs["properties"]

            assert "$set" not in properties

    def test_record_handles_capture_error(self, tmp_path: Path) -> None:
        """Test record handles errors gracefully."""
        config_file = tmp_path / "promptfoo.yaml"
        config_file.write_text("id: test-user-id\n")

        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path),
            mock.patch("promptfoo.telemetry.Posthog") as mock_posthog,
        ):
            mock_client = mock.Mock()
            mock_client.capture.side_effect = Exception("Network error")
            mock_posthog.return_value = mock_client

            telemetry = _Telemetry()

            # Should not raise
            telemetry.record("test_event")

    def test_shutdown_flushes_client(self, tmp_path: Path) -> None:
        """Test shutdown flushes and closes client."""
        config_file = tmp_path / "promptfoo.yaml"
        config_file.write_text("id: test-user-id\n")

        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path),
            mock.patch("promptfoo.telemetry.Posthog") as mock_posthog,
        ):
            mock_client = mock.Mock()
            mock_posthog.return_value = mock_client

            telemetry = _Telemetry()
            telemetry._ensure_initialized()

            telemetry.shutdown()

            mock_client.flush.assert_called_once()
            mock_client.shutdown.assert_called_once()
            assert telemetry._client is None

    def test_shutdown_handles_error(self, tmp_path: Path) -> None:
        """Test shutdown handles errors gracefully."""
        config_file = tmp_path / "promptfoo.yaml"
        config_file.write_text("id: test-user-id\n")

        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path),
            mock.patch("promptfoo.telemetry.Posthog") as mock_posthog,
        ):
            mock_client = mock.Mock()
            mock_client.flush.side_effect = Exception("Flush error")
            mock_posthog.return_value = mock_client

            telemetry = _Telemetry()
            telemetry._ensure_initialized()

            # Should not raise
            telemetry.shutdown()
            assert telemetry._client is None


class TestRecordWrapperUsed:
    """Test record_wrapper_used function."""

    def test_record_wrapper_used_global(self, tmp_path: Path) -> None:
        """Test recording wrapper used with global method."""
        config_file = tmp_path / "promptfoo.yaml"
        config_file.write_text("id: test-user-id\n")

        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path),
            mock.patch("promptfoo.telemetry.Posthog") as mock_posthog,
            mock.patch("promptfoo.telemetry._telemetry", None),
        ):
            mock_client = mock.Mock()
            mock_posthog.return_value = mock_client

            record_wrapper_used("global")

            call_args = mock_client.capture.call_args
            assert call_args.kwargs["event"] == "wrapper_used"
            properties = call_args.kwargs["properties"]
            assert properties["method"] == "global"
            assert properties["wrapperType"] == "python"

    def test_record_wrapper_used_npx(self, tmp_path: Path) -> None:
        """Test recording wrapper used with npx method."""
        config_file = tmp_path / "promptfoo.yaml"
        config_file.write_text("id: test-user-id\n")

        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path),
            mock.patch("promptfoo.telemetry.Posthog") as mock_posthog,
            mock.patch("promptfoo.telemetry._telemetry", None),
        ):
            mock_client = mock.Mock()
            mock_posthog.return_value = mock_client

            record_wrapper_used("npx")

            call_args = mock_client.capture.call_args
            properties = call_args.kwargs["properties"]
            assert properties["method"] == "npx"

    def test_record_wrapper_used_error(self, tmp_path: Path) -> None:
        """Test recording wrapper used with error method."""
        config_file = tmp_path / "promptfoo.yaml"
        config_file.write_text("id: test-user-id\n")

        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch("promptfoo.telemetry._get_config_dir", return_value=tmp_path),
            mock.patch("promptfoo.telemetry.Posthog") as mock_posthog,
            mock.patch("promptfoo.telemetry._telemetry", None),
        ):
            mock_client = mock.Mock()
            mock_posthog.return_value = mock_client

            record_wrapper_used("error")

            call_args = mock_client.capture.call_args
            properties = call_args.kwargs["properties"]
            assert properties["method"] == "error"

    def test_record_wrapper_used_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test record_wrapper_used does nothing when disabled."""
        monkeypatch.setenv("PROMPTFOO_DISABLE_TELEMETRY", "1")

        with mock.patch("promptfoo.telemetry._telemetry", None):
            # Should not raise or make any calls
            record_wrapper_used("global")
