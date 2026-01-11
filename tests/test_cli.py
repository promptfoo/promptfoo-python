"""
Tests for the promptfoo CLI wrapper.

This module tests all functionality of the CLI wrapper including:
- Dependency detection (Node.js, npx)
- External promptfoo detection and recursion prevention
- Command execution with proper shell handling
- Error handling and exit codes
- Platform-specific behavior (Windows vs Unix)
"""

import os
import subprocess
import sys
from typing import Optional
from unittest.mock import MagicMock

import pytest

from promptfoo.cli import (
    _WINDOWS_SHELL_EXTENSIONS,
    _WRAPPER_ENV,
    _find_external_promptfoo,
    _find_windows_promptfoo,
    _normalize_path,
    _requires_shell,
    _resolve_argv0,
    _run_command,
    _split_path,
    _strip_quotes,
    check_node_installed,
    check_npx_installed,
    main,
    print_installation_help,
)

# =============================================================================
# Unit Tests for Helper Functions
# =============================================================================


class TestNodeDetection:
    """Test Node.js and npx detection functions."""

    def test_check_node_installed_when_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Node.js detection returns True when node is in PATH."""
        monkeypatch.setattr("shutil.which", lambda cmd: "/usr/bin/node" if cmd == "node" else None)
        assert check_node_installed() is True

    def test_check_node_installed_when_not_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Node.js detection returns False when node is not in PATH."""
        monkeypatch.setattr("shutil.which", lambda cmd: None)
        assert check_node_installed() is False

    def test_check_npx_installed_when_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """npx detection returns True when npx is in PATH."""
        monkeypatch.setattr("shutil.which", lambda cmd: "/usr/bin/npx" if cmd == "npx" else None)
        assert check_npx_installed() is True

    def test_check_npx_installed_when_not_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """npx detection returns False when npx is not in PATH."""
        monkeypatch.setattr("shutil.which", lambda cmd: None)
        assert check_npx_installed() is False


class TestInstallationHelp:
    """Test installation help message output."""

    def test_print_installation_help_outputs_to_stderr(self, capsys: pytest.CaptureFixture) -> None:
        """Installation help is printed to stderr with platform-specific content."""
        print_installation_help()
        captured = capsys.readouterr()
        assert captured.out == ""  # Nothing to stdout
        assert "ERROR: promptfoo requires Node.js" in captured.err
        # Platform-specific instructions will vary by environment
        # Just verify that some installation instructions are present
        assert "nodejs.org" in captured.err or "install node" in captured.err.lower()
        assert "DIRECT USAGE" in captured.err  # npx instructions always included
        assert "npx promptfoo@latest" in captured.err


class TestPathUtilities:
    """Test path normalization and manipulation functions."""

    def test_normalize_path(self) -> None:
        """Path normalization converts to absolute normalized case."""
        result = _normalize_path(".")
        assert os.path.isabs(result)
        assert result == os.path.normcase(os.path.abspath("."))

    @pytest.mark.parametrize(
        "input_path,expected",
        [
            ('"/usr/bin"', "/usr/bin"),
            ("'/usr/bin'", "/usr/bin"),
            ("/usr/bin", "/usr/bin"),
            ('""', ""),
            ("''", ""),
            ('"incomplete', '"incomplete'),
            ("'incomplete", "'incomplete"),
        ],
    )
    def test_strip_quotes(self, input_path: str, expected: str) -> None:
        """Quote stripping handles various quote patterns correctly."""
        assert _strip_quotes(input_path) == expected

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-style PATH separator test")
    @pytest.mark.parametrize(
        "path_value,expected",
        [
            ("/usr/bin:/usr/local/bin", ["/usr/bin", "/usr/local/bin"]),
            ('"/usr/bin":/usr/local/bin', ["/usr/bin", "/usr/local/bin"]),
            ("/usr/bin::/usr/local/bin", ["/usr/bin", "/usr/local/bin"]),  # Empty entry removed
            ("  /usr/bin  :  /usr/local/bin  ", ["/usr/bin", "/usr/local/bin"]),  # Whitespace
            ("", []),
            (":::", []),  # Only separators
        ],
    )
    def test_split_path_unix(self, path_value: str, expected: list[str]) -> None:
        """PATH splitting handles quotes, empty entries, and whitespace on Unix."""
        assert _split_path(path_value) == expected

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-style PATH separator test")
    @pytest.mark.parametrize(
        "path_value,expected",
        [
            ("C:\\bin;C:\\tools", ["C:\\bin", "C:\\tools"]),
            ('"C:\\bin";C:\\tools', ["C:\\bin", "C:\\tools"]),
            ("C:\\bin;;C:\\tools", ["C:\\bin", "C:\\tools"]),  # Empty entry removed
            ("  C:\\bin  ;  C:\\tools  ", ["C:\\bin", "C:\\tools"]),  # Whitespace
            ("", []),
            (";;;", []),  # Only separators
        ],
    )
    def test_split_path_windows(self, path_value: str, expected: list[str]) -> None:
        """PATH splitting handles quotes, empty entries, and whitespace on Windows."""
        assert _split_path(path_value) == expected


class TestArgvResolution:
    """Test sys.argv[0] resolution logic."""

    def test_resolve_argv0_with_empty_argv(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Returns None when sys.argv is empty."""
        monkeypatch.setattr(sys, "argv", [])
        assert _resolve_argv0() is None

    def test_resolve_argv0_with_empty_string(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Returns None when argv[0] is empty string."""
        monkeypatch.setattr(sys, "argv", [""])
        assert _resolve_argv0() is None

    def test_resolve_argv0_with_absolute_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Returns normalized path when argv[0] contains path separator."""
        test_path = "/usr/bin/promptfoo"
        monkeypatch.setattr(sys, "argv", [test_path])
        result = _resolve_argv0()
        assert result == _normalize_path(test_path)

    def test_resolve_argv0_with_command_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Resolves command name via which() when no path separator."""
        monkeypatch.setattr(sys, "argv", ["promptfoo"])
        monkeypatch.setattr("shutil.which", lambda cmd: "/usr/bin/promptfoo" if cmd == "promptfoo" else None)
        result = _resolve_argv0()
        assert result == _normalize_path("/usr/bin/promptfoo")

    def test_resolve_argv0_with_unresolvable_command(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Returns None when command cannot be resolved via which()."""
        monkeypatch.setattr(sys, "argv", ["promptfoo"])
        monkeypatch.setattr("shutil.which", lambda cmd: None)
        assert _resolve_argv0() is None


class TestWindowsPromptfooDiscovery:
    """Test Windows-specific promptfoo discovery."""

    def test_find_windows_promptfoo_in_npm_prefix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Finds promptfoo.cmd in npm prefix directory."""
        monkeypatch.setenv("NPM_CONFIG_PREFIX", "C:\\npm")

        def mock_isfile(p: str) -> bool:
            return p == os.path.join("C:\\npm", "promptfoo.cmd")

        monkeypatch.setattr(os.path, "isfile", mock_isfile)

        # Only test on Windows or mock the function call
        if os.name == "nt":
            result = _find_windows_promptfoo()
            assert result == os.path.join("C:\\npm", "promptfoo.cmd")
        else:
            # On non-Windows, test the logic by directly calling with mocked env
            # This is testing the Windows code path even on Unix
            pytest.skip("Windows-specific test, skipping on non-Windows platform")

    def test_find_windows_promptfoo_in_appdata(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Finds promptfoo.cmd in APPDATA npm directory."""
        monkeypatch.setenv("APPDATA", "C:\\Users\\test\\AppData\\Roaming")

        expected_path = os.path.join("C:\\Users\\test\\AppData\\Roaming", "npm", "promptfoo.cmd")

        def mock_isfile(p: str) -> bool:
            return p == expected_path

        monkeypatch.setattr(os.path, "isfile", mock_isfile)

        # Only test on Windows
        if os.name == "nt":
            result = _find_windows_promptfoo()
            assert result == expected_path
        else:
            pytest.skip("Windows-specific test, skipping on non-Windows platform")

    def test_find_windows_promptfoo_not_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Returns None when no promptfoo found in Windows locations."""
        monkeypatch.setattr(os.path, "isfile", lambda p: False)

        # Only test on Windows
        if os.name == "nt":
            assert _find_windows_promptfoo() is None
        else:
            pytest.skip("Windows-specific test, skipping on non-Windows platform")


class TestExternalPromptfooDiscovery:
    """Test external promptfoo detection and recursion prevention."""

    def test_find_external_promptfoo_when_not_in_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Returns None when no promptfoo in PATH."""
        monkeypatch.setattr("shutil.which", lambda cmd, path=None: None)
        monkeypatch.setattr(os, "name", "posix")
        assert _find_external_promptfoo() is None

    def test_find_external_promptfoo_when_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Returns path when promptfoo found and not this wrapper."""
        promptfoo_path = "/usr/local/bin/promptfoo"
        monkeypatch.setattr("shutil.which", lambda cmd, path=None: promptfoo_path if cmd == "promptfoo" else None)
        monkeypatch.setattr(sys, "argv", ["different-script"])
        result = _find_external_promptfoo()
        assert result == promptfoo_path

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific recursion test")
    def test_find_external_promptfoo_prevents_recursion_unix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Filters out wrapper directory from PATH to prevent recursion on Unix."""
        wrapper_path = "/home/user/.local/bin/promptfoo"
        real_promptfoo = "/usr/local/bin/promptfoo"

        monkeypatch.setattr(sys, "argv", [wrapper_path])
        monkeypatch.setenv("PATH", "/home/user/.local/bin:/usr/local/bin")

        def mock_which(cmd: str, path: Optional[str] = None) -> Optional[str]:
            if cmd != "promptfoo":
                return None
            if path is None:
                return wrapper_path
            # When called with filtered PATH, return the real one
            if "/home/user/.local/bin" not in path:
                return real_promptfoo
            return None

        monkeypatch.setattr("shutil.which", mock_which)
        result = _find_external_promptfoo()
        assert result == real_promptfoo

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific recursion test")
    def test_find_external_promptfoo_prevents_recursion_windows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Filters out wrapper directory from PATH to prevent recursion on Windows."""
        wrapper_path = "C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python312\\Scripts\\promptfoo.exe"
        real_promptfoo = "C:\\npm\\prefix\\promptfoo.cmd"

        monkeypatch.setattr(sys, "argv", [wrapper_path])
        test_path = "C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python312\\Scripts;C:\\npm\\prefix"
        monkeypatch.setenv("PATH", test_path)

        def mock_which(cmd: str, path: Optional[str] = None) -> Optional[str]:
            if cmd != "promptfoo":
                return None
            if path is None:
                return wrapper_path
            # When called with filtered PATH, return the real one
            if "Python312\\Scripts" not in path:
                return real_promptfoo
            return None

        monkeypatch.setattr("shutil.which", mock_which)
        result = _find_external_promptfoo()
        assert result == real_promptfoo


class TestShellRequirement:
    """Test Windows shell requirement detection for .bat/.cmd files."""

    def test_requires_shell_on_windows_with_bat(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Returns True for .bat files on Windows."""
        monkeypatch.setattr(os, "name", "nt")
        assert _requires_shell("promptfoo.bat") is True

    def test_requires_shell_on_windows_with_cmd(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Returns True for .cmd files on Windows."""
        monkeypatch.setattr(os, "name", "nt")
        assert _requires_shell("promptfoo.cmd") is True

    def test_requires_shell_on_windows_with_exe(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Returns False for .exe files on Windows."""
        monkeypatch.setattr(os, "name", "nt")
        assert _requires_shell("promptfoo.exe") is False

    def test_requires_shell_on_unix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Returns False for all files on Unix."""
        monkeypatch.setattr(os, "name", "posix")
        assert _requires_shell("promptfoo.bat") is False
        assert _requires_shell("promptfoo.cmd") is False
        assert _requires_shell("promptfoo") is False


class TestCommandExecution:
    """Test command execution with proper shell handling."""

    def test_run_command_with_shell_for_bat_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Uses shell=True for .bat files on Windows."""
        monkeypatch.setattr(os, "name", "nt")
        mock_run = MagicMock(return_value=subprocess.CompletedProcess([], 0))
        monkeypatch.setattr(subprocess, "run", mock_run)

        cmd = ["promptfoo.bat", "eval"]
        _run_command(cmd)

        # Should be called with shell=True
        assert mock_run.call_count == 1
        call_args = mock_run.call_args
        assert call_args.kwargs.get("shell") is True

    def test_run_command_without_shell_for_regular_executable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Uses shell=False for regular executables."""
        monkeypatch.setattr(os, "name", "posix")
        mock_run = MagicMock(return_value=subprocess.CompletedProcess([], 0))
        monkeypatch.setattr(subprocess, "run", mock_run)

        cmd = ["/usr/bin/promptfoo", "eval"]
        _run_command(cmd)

        # Should be called with the list directly, no shell
        assert mock_run.call_count == 1
        call_args = mock_run.call_args
        assert call_args.args[0] == cmd
        assert call_args.kwargs.get("shell") is not True

    def test_run_command_passes_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Passes environment variables to subprocess."""
        monkeypatch.setattr(os, "name", "posix")
        mock_run = MagicMock(return_value=subprocess.CompletedProcess([], 0))
        monkeypatch.setattr(subprocess, "run", mock_run)

        cmd = ["promptfoo", "eval"]
        env = {"TEST": "value"}
        _run_command(cmd, env=env)

        call_args = mock_run.call_args
        assert call_args.kwargs.get("env") == env


# =============================================================================
# Integration Tests for main()
# =============================================================================


class TestMainFunction:
    """Test the main CLI entry point with various scenarios."""

    def test_main_exits_when_node_not_installed(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        """Exits with code 1 and prints help when Node.js not found."""
        monkeypatch.setattr("shutil.which", lambda cmd: None)

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "ERROR: promptfoo requires Node.js" in captured.err

    def test_main_uses_external_promptfoo_when_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Uses external promptfoo when found and sets wrapper env var."""
        monkeypatch.setattr(sys, "argv", ["promptfoo", "eval"])
        monkeypatch.setattr(
            "shutil.which",
            lambda cmd, path=None: {"node": "/usr/bin/node", "promptfoo": "/usr/local/bin/promptfoo"}.get(cmd),
        )
        # Mock telemetry to avoid PostHog calls during test
        monkeypatch.setattr("promptfoo.cli.record_wrapper_used", lambda mode: None)

        mock_result = subprocess.CompletedProcess([], 0)
        mock_run = MagicMock(return_value=mock_result)
        monkeypatch.setattr(subprocess, "run", mock_run)

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        assert mock_run.call_count == 1

        # Check command and environment
        call_args = mock_run.call_args
        if call_args.kwargs.get("shell"):
            # Shell mode - check environment
            assert call_args.kwargs["env"][_WRAPPER_ENV] == "1"
        else:
            # Non-shell mode
            cmd = call_args.args[0]
            assert cmd[0] == "/usr/local/bin/promptfoo"
            assert cmd[1] == "eval"
            assert call_args.kwargs["env"][_WRAPPER_ENV] == "1"

    def test_main_skips_external_when_wrapper_env_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Skips external promptfoo search when wrapper env var is set."""
        monkeypatch.setattr(sys, "argv", ["promptfoo", "eval"])
        monkeypatch.setenv(_WRAPPER_ENV, "1")
        monkeypatch.setattr(
            "shutil.which",
            lambda cmd, path=None: {
                "node": "/usr/bin/node",
                "npx": "/usr/bin/npx",
                "promptfoo": "/usr/local/bin/promptfoo",
            }.get(cmd),
        )
        # Mock telemetry to avoid PostHog calls during test
        monkeypatch.setattr("promptfoo.cli.record_wrapper_used", lambda mode: None)

        mock_result = subprocess.CompletedProcess([], 0)
        mock_run = MagicMock(return_value=mock_result)
        monkeypatch.setattr(subprocess, "run", mock_run)

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

        # Should use npx, not external promptfoo
        call_args = mock_run.call_args
        if not call_args.kwargs.get("shell"):
            cmd = call_args.args[0]
            assert "npx" in cmd[0]
            assert "promptfoo@latest" in cmd

    def test_main_falls_back_to_npx(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Falls back to npx when no external promptfoo found."""
        monkeypatch.setattr(sys, "argv", ["promptfoo", "eval"])
        monkeypatch.setattr(
            "shutil.which", lambda cmd, path=None: {"node": "/usr/bin/node", "npx": "/usr/bin/npx"}.get(cmd)
        )
        # Mock telemetry to avoid PostHog calls during test
        monkeypatch.setattr("promptfoo.cli.record_wrapper_used", lambda mode: None)

        mock_result = subprocess.CompletedProcess([], 0)
        mock_run = MagicMock(return_value=mock_result)
        monkeypatch.setattr(subprocess, "run", mock_run)

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        assert mock_run.call_count == 1

        # Check that npx was used
        call_args = mock_run.call_args
        if not call_args.kwargs.get("shell"):
            cmd = call_args.args[0]
            assert cmd[0] == "/usr/bin/npx"
            assert "-y" in cmd
            assert "promptfoo@latest" in cmd
            assert "eval" in cmd

    def test_main_exits_when_neither_external_nor_npx_available(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        """Exits with error when neither external promptfoo nor npx found."""
        # Use platform-appropriate path for node
        node_path = "C:\\Program Files\\nodejs\\node.exe" if sys.platform == "win32" else "/usr/bin/node"

        monkeypatch.setattr(sys, "argv", ["promptfoo", "eval"])
        monkeypatch.setattr("shutil.which", lambda cmd, path=None: {"node": node_path}.get(cmd))
        # Also mock os.path.isfile to prevent _find_windows_promptfoo() from finding
        # a real promptfoo installation on Windows CI runners
        monkeypatch.setattr(os.path, "isfile", lambda p: False)

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "ERROR: Neither promptfoo nor npx is available" in captured.err

    def test_main_passes_arguments_correctly(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Passes command-line arguments to the subprocess."""
        monkeypatch.setattr(sys, "argv", ["promptfoo", "redteam", "run", "--config", "test.yaml"])
        monkeypatch.setattr(
            "shutil.which", lambda cmd, path=None: {"node": "/usr/bin/node", "npx": "/usr/bin/npx"}.get(cmd)
        )
        # Mock telemetry to avoid PostHog calls during test
        monkeypatch.setattr("promptfoo.cli.record_wrapper_used", lambda mode: None)

        mock_result = subprocess.CompletedProcess([], 0)
        mock_run = MagicMock(return_value=mock_result)
        monkeypatch.setattr(subprocess, "run", mock_run)

        with pytest.raises(SystemExit):
            main()

        call_args = mock_run.call_args
        if not call_args.kwargs.get("shell"):
            cmd = call_args.args[0]
            assert "redteam" in cmd
            assert "run" in cmd
            assert "--config" in cmd
            assert "test.yaml" in cmd

    def test_main_returns_subprocess_exit_code(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Returns the exit code from the subprocess."""
        monkeypatch.setattr(sys, "argv", ["promptfoo", "eval"])
        monkeypatch.setattr(
            "shutil.which", lambda cmd, path=None: {"node": "/usr/bin/node", "npx": "/usr/bin/npx"}.get(cmd)
        )
        # Mock telemetry to avoid PostHog calls during test
        monkeypatch.setattr("promptfoo.cli.record_wrapper_used", lambda mode: None)

        # Test non-zero exit code
        mock_result = subprocess.CompletedProcess([], 42)
        mock_run = MagicMock(return_value=mock_result)
        monkeypatch.setattr(subprocess, "run", mock_run)

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 42


# =============================================================================
# Platform-Specific Tests
# =============================================================================


class TestPlatformSpecificBehavior:
    """Test platform-specific code paths."""

    def test_windows_shell_extensions_constant(self) -> None:
        """Windows shell extensions constant contains expected values."""
        assert ".bat" in _WINDOWS_SHELL_EXTENSIONS
        assert ".cmd" in _WINDOWS_SHELL_EXTENSIONS

    def test_wrapper_env_constant(self) -> None:
        """Wrapper environment variable constant has expected value."""
        assert _WRAPPER_ENV == "PROMPTFOO_PY_WRAPPER"
