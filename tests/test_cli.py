"""Tests for the promptfoo CLI wrapper."""

import platform
import subprocess
import sys
from unittest import mock

import pytest

from promptfoo import cli


class TestCheckNodeInstalled:
    """Tests for check_node_installed function."""

    def test_node_is_installed(self):
        """Test when node is found in PATH."""
        with mock.patch("shutil.which", return_value="/usr/bin/node"):
            assert cli.check_node_installed() is True

    def test_node_is_not_installed(self):
        """Test when node is not found in PATH."""
        with mock.patch("shutil.which", return_value=None):
            assert cli.check_node_installed() is False


class TestCheckNpxInstalled:
    """Tests for check_npx_installed function."""

    def test_npx_is_installed(self):
        """Test when npx is found in PATH."""
        with mock.patch("shutil.which", return_value="/usr/bin/npx"):
            assert cli.check_npx_installed() is True

    def test_npx_is_not_installed(self):
        """Test when npx is not found in PATH."""
        with mock.patch("shutil.which", return_value=None):
            assert cli.check_npx_installed() is False


class TestMain:
    """Tests for the main CLI entry point."""

    def test_exits_when_node_not_installed(self, capsys):
        """Test that main() exits with code 1 when Node.js is not installed."""
        with mock.patch("promptfoo.cli.check_node_installed", return_value=False):
            with pytest.raises(SystemExit) as exc_info:
                cli.main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "ERROR: promptfoo requires Node.js to be installed" in captured.err

    def test_uses_global_promptfoo_when_available_unix(self):
        """Test using globally installed promptfoo on Unix systems."""
        with mock.patch("promptfoo.cli.check_node_installed", return_value=True), mock.patch(
            "platform.system", return_value="Linux"
        ), mock.patch("shutil.which") as mock_which, mock.patch("subprocess.run") as mock_run:
            # Setup: promptfoo is globally installed
            mock_which.side_effect = lambda cmd: "/usr/local/bin/promptfoo" if cmd == "promptfoo" else None
            mock_run.return_value = mock.Mock(returncode=0)

            # Override sys.argv
            with mock.patch.object(sys, "argv", ["promptfoo", "--version"]):
                with pytest.raises(SystemExit) as exc_info:
                    cli.main()

            # Verify correct command was built
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][0] == ["/usr/local/bin/promptfoo", "--version"]
            assert call_args[1]["shell"] is False
            assert exc_info.value.code == 0

    def test_uses_global_promptfoo_when_available_windows(self):
        """Test using globally installed promptfoo on Windows with cmd.exe."""
        with mock.patch("promptfoo.cli.check_node_installed", return_value=True), mock.patch(
            "platform.system", return_value="Windows"
        ), mock.patch("shutil.which") as mock_which, mock.patch("subprocess.run") as mock_run:
            # Setup: promptfoo is globally installed
            mock_which.side_effect = (
                lambda cmd: "C:\\Program Files\\nodejs\\promptfoo.cmd" if cmd == "promptfoo" else None
            )
            mock_run.return_value = mock.Mock(returncode=0)

            # Override sys.argv
            with mock.patch.object(sys, "argv", ["promptfoo", "--version"]):
                with pytest.raises(SystemExit) as exc_info:
                    cli.main()

            # Verify cmd.exe is used on Windows
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][0][:3] == ["cmd", "/c", "C:\\Program Files\\nodejs\\promptfoo.cmd"]
            assert call_args[1]["shell"] is False
            assert exc_info.value.code == 0

    def test_falls_back_to_npx_when_promptfoo_not_installed_unix(self):
        """Test fallback to npx when promptfoo is not globally installed on Unix."""
        with mock.patch("promptfoo.cli.check_node_installed", return_value=True), mock.patch(
            "platform.system", return_value="Linux"
        ), mock.patch("shutil.which") as mock_which, mock.patch("subprocess.run") as mock_run:
            # Setup: promptfoo not installed, but npx is available
            mock_which.side_effect = lambda cmd: "/usr/bin/npx" if cmd == "npx" else None
            mock_run.return_value = mock.Mock(returncode=0)

            # Override sys.argv
            with mock.patch.object(sys, "argv", ["promptfoo", "eval"]):
                with pytest.raises(SystemExit) as exc_info:
                    cli.main()

            # Verify npx is used with @latest
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][0] == ["/usr/bin/npx", "--yes", "promptfoo@latest", "eval"]
            assert call_args[1]["shell"] is False
            assert exc_info.value.code == 0

    def test_falls_back_to_npx_when_promptfoo_not_installed_windows(self):
        """Test fallback to npx with cmd.exe when promptfoo is not installed on Windows."""
        with mock.patch("promptfoo.cli.check_node_installed", return_value=True), mock.patch(
            "platform.system", return_value="Windows"
        ), mock.patch("shutil.which") as mock_which, mock.patch("subprocess.run") as mock_run:
            # Setup: promptfoo not installed, but npx is available
            mock_which.side_effect = lambda cmd: "C:\\Program Files\\nodejs\\npx.cmd" if cmd == "npx" else None
            mock_run.return_value = mock.Mock(returncode=0)

            # Override sys.argv
            with mock.patch.object(sys, "argv", ["promptfoo", "eval"]):
                with pytest.raises(SystemExit) as exc_info:
                    cli.main()

            # Verify cmd.exe is used for npx on Windows
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][0][:4] == ["cmd", "/c", "C:\\Program Files\\nodejs\\npx.cmd", "--yes"]
            assert call_args[1]["shell"] is False
            assert exc_info.value.code == 0

    def test_exits_when_neither_promptfoo_nor_npx_available(self, capsys):
        """Test exit with error when neither promptfoo nor npx is available."""
        with mock.patch("promptfoo.cli.check_node_installed", return_value=True), mock.patch(
            "shutil.which", return_value=None
        ):
            with pytest.raises(SystemExit) as exc_info:
                cli.main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "ERROR: promptfoo is not installed and npx is not available" in captured.err

    def test_handles_keyboard_interrupt(self, capsys):
        """Test graceful handling of KeyboardInterrupt (Ctrl+C)."""
        with mock.patch("promptfoo.cli.check_node_installed", return_value=True), mock.patch(
            "shutil.which", return_value="/usr/bin/npx"
        ), mock.patch("subprocess.run", side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit) as exc_info:
                cli.main()
            assert exc_info.value.code == 130

        captured = capsys.readouterr()
        assert "Interrupted by user" in captured.err

    def test_handles_subprocess_exception(self, capsys):
        """Test handling of unexpected subprocess exceptions."""
        with mock.patch("promptfoo.cli.check_node_installed", return_value=True), mock.patch(
            "shutil.which", return_value="/usr/bin/npx"
        ), mock.patch("subprocess.run", side_effect=Exception("Unexpected error")):
            with pytest.raises(SystemExit) as exc_info:
                cli.main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "ERROR: Failed to execute promptfoo: Unexpected error" in captured.err

    def test_preserves_exit_code_from_promptfoo(self):
        """Test that main() exits with the same code as the promptfoo process."""
        with mock.patch("promptfoo.cli.check_node_installed", return_value=True), mock.patch(
            "shutil.which", return_value="/usr/bin/npx"
        ), mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=42)

            with pytest.raises(SystemExit) as exc_info:
                cli.main()
            assert exc_info.value.code == 42

    def test_passes_environment_variables(self):
        """Test that environment variables are passed through to subprocess."""
        with mock.patch("promptfoo.cli.check_node_installed", return_value=True), mock.patch(
            "shutil.which", return_value="/usr/bin/npx"
        ), mock.patch("subprocess.run") as mock_run, mock.patch("os.environ.copy") as mock_env:
            mock_env.return_value = {"TEST_VAR": "test_value"}
            mock_run.return_value = mock.Mock(returncode=0)

            with pytest.raises(SystemExit):
                cli.main()

            # Verify environment was passed
            call_args = mock_run.call_args
            assert call_args[1]["env"] == {"TEST_VAR": "test_value"}


class TestPrintInstallationHelp:
    """Tests for print_installation_help function."""

    def test_prints_installation_instructions(self, capsys):
        """Test that installation help is printed to stderr."""
        cli.print_installation_help()
        captured = capsys.readouterr()

        # Check that key installation methods are mentioned
        assert "ERROR: promptfoo requires Node.js to be installed" in captured.err
        assert "brew install node" in captured.err
        assert "sudo apt install nodejs npm" in captured.err
        assert "https://nodejs.org/" in captured.err
        assert "nvm" in captured.err
