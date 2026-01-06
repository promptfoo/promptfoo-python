"""
Smoke tests for the promptfoo CLI.

These tests verify the core evaluation pipeline works correctly
using the echo provider (no external API dependencies).

These tests run against the installed promptfoo package via npx,
testing the Python wrapper integration.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import pytest

# Mark all tests in this module as smoke tests
pytestmark = pytest.mark.smoke

# Directories
SMOKE_DIR = Path(__file__).parent
FIXTURES_DIR = SMOKE_DIR / "fixtures"
CONFIGS_DIR = FIXTURES_DIR / "configs"
OUTPUT_DIR = SMOKE_DIR / ".temp-output"


def run_promptfoo(
    args: list[str],
    cwd: Optional[Path] = None,
    expect_error: bool = False,
    env: Optional[dict[str, str]] = None,
) -> tuple[str, str, int]:
    """
    Run promptfoo CLI and capture output.

    Args:
        args: CLI arguments to pass to promptfoo
        cwd: Working directory for the command
        expect_error: If True, don't raise on non-zero exit
        env: Environment variables to set

    Returns:
        Tuple of (stdout, stderr, exit_code)
    """
    cmd = ["promptfoo"] + args

    full_env = os.environ.copy()
    full_env["NO_COLOR"] = "1"  # Disable color output for easier parsing
    if env:
        full_env.update(env)

    result = subprocess.run(
        cmd,
        cwd=cwd or Path.cwd(),
        capture_output=True,
        text=True,
        env=full_env,
        timeout=120,  # Increased timeout for npx fallback (first npx call downloads promptfoo)
    )

    stdout = result.stdout
    stderr = result.stderr
    exit_code = result.returncode

    if not expect_error and exit_code != 0:
        # For debugging failed tests
        print(f"Command failed: {' '.join(cmd)}")
        print(f"Exit code: {exit_code}")
        print(f"STDOUT:\n{stdout}")
        print(f"STDERR:\n{stderr}")

    return stdout, stderr, exit_code


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    """Create and cleanup output directory for smoke tests."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    yield
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)


class TestBasicCLI:
    """Basic CLI operations smoke tests."""

    def test_version_flag(self):
        """Test --version flag outputs version."""
        stdout, stderr, exit_code = run_promptfoo(["--version"])

        assert exit_code == 0
        # Should output a version number (semver format)
        assert stdout.strip(), "Version output should not be empty"

    def test_help_flag(self):
        """Test --help flag outputs help."""
        stdout, stderr, exit_code = run_promptfoo(["--help"])

        assert exit_code == 0
        assert "promptfoo" in stdout.lower()
        assert "eval" in stdout.lower()

    def test_eval_help(self):
        """Test 'eval --help' outputs eval command help."""
        stdout, stderr, exit_code = run_promptfoo(["eval", "--help"])

        assert exit_code == 0
        assert "--config" in stdout or "-c" in stdout
        assert "--output" in stdout or "-o" in stdout

    def test_unknown_command(self):
        """Test unknown command returns error."""
        stdout, stderr, exit_code = run_promptfoo(
            ["unknowncommand123"],
            expect_error=True,
        )

        assert exit_code != 0
        output = stdout + stderr
        assert "unknown" in output.lower() or "not found" in output.lower()

    def test_missing_config_file(self):
        """Test missing config file returns error."""
        stdout, stderr, exit_code = run_promptfoo(
            ["eval", "-c", "nonexistent-config-file.yaml"],
            expect_error=True,
        )

        assert exit_code != 0
        output = stdout + stderr
        # Should indicate the file wasn't found
        assert any(
            phrase in output.lower()
            for phrase in [
                "not found",
                "no such file",
                "does not exist",
                "cannot find",
                "no configuration file",
            ]
        )


class TestEvalCommand:
    """Eval command smoke tests."""

    def test_basic_eval(self):
        """Test basic eval with echo provider."""
        config_path = CONFIGS_DIR / "basic.yaml"
        stdout, stderr, exit_code = run_promptfoo(
            ["eval", "-c", str(config_path), "--no-cache"]
        )

        assert exit_code == 0, f"Eval failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}"
        # Should show evaluation results
        assert "pass" in stdout.lower() or "✓" in stdout or "success" in stdout.lower()

    def test_json_output(self):
        """Test eval outputs valid JSON."""
        config_path = CONFIGS_DIR / "basic.yaml"
        output_path = OUTPUT_DIR / "output.json"

        stdout, stderr, exit_code = run_promptfoo(
            ["eval", "-c", str(config_path), "-o", str(output_path), "--no-cache"]
        )

        assert exit_code == 0, f"Eval failed:\nSTDOUT: {stdout}\nSTDERR: {stderr}"
        assert output_path.exists(), "Output file was not created"

        # Verify it's valid JSON with expected structure
        with open(output_path) as f:
            data = json.load(f)

        assert "results" in data
        assert "results" in data["results"]
        assert isinstance(data["results"]["results"], list)
        assert len(data["results"]["results"]) > 0

        # Verify echo provider returns the prompt
        first_result = data["results"]["results"][0]
        assert "response" in first_result
        assert "output" in first_result["response"]
        output_text = first_result["response"]["output"]
        assert "Hello" in output_text
        assert "World" in output_text

    def test_yaml_output(self):
        """Test eval outputs YAML format."""
        config_path = CONFIGS_DIR / "basic.yaml"
        output_path = OUTPUT_DIR / "output.yaml"

        stdout, stderr, exit_code = run_promptfoo(
            ["eval", "-c", str(config_path), "-o", str(output_path), "--no-cache"]
        )

        assert exit_code == 0
        assert output_path.exists()

        # Verify it contains YAML-like content
        with open(output_path) as f:
            content = f.read()

        assert "results:" in content

    def test_csv_output(self):
        """Test eval outputs CSV format."""
        config_path = CONFIGS_DIR / "basic.yaml"
        output_path = OUTPUT_DIR / "output.csv"

        stdout, stderr, exit_code = run_promptfoo(
            ["eval", "-c", str(config_path), "-o", str(output_path), "--no-cache"]
        )

        assert exit_code == 0
        assert output_path.exists()

        # Verify it's CSV format (has header row with columns)
        with open(output_path) as f:
            content = f.read()

        lines = content.strip().split("\n")
        assert len(lines) > 0
        # CSV should have comma-separated values
        assert "," in lines[0]

    def test_max_concurrency_flag(self):
        """Test --max-concurrency flag."""
        config_path = CONFIGS_DIR / "basic.yaml"

        stdout, stderr, exit_code = run_promptfoo(
            ["eval", "-c", str(config_path), "--max-concurrency", "1", "--no-cache"]
        )

        assert exit_code == 0

    def test_repeat_flag(self):
        """Test --repeat flag runs tests multiple times."""
        config_path = CONFIGS_DIR / "basic.yaml"
        output_path = OUTPUT_DIR / "repeat-output.json"

        stdout, stderr, exit_code = run_promptfoo(
            [
                "eval",
                "-c",
                str(config_path),
                "--repeat",
                "2",
                "-o",
                str(output_path),
                "--no-cache",
            ]
        )

        assert exit_code == 0

        # Verify we got repeated results
        with open(output_path) as f:
            data = json.load(f)

        # With repeat=2 and 1 test case, we should have 2 results
        assert len(data["results"]["results"]) == 2

    def test_verbose_flag(self):
        """Test --verbose flag."""
        config_path = CONFIGS_DIR / "basic.yaml"

        stdout, stderr, exit_code = run_promptfoo(
            ["eval", "-c", str(config_path), "--verbose", "--no-cache"]
        )

        assert exit_code == 0
        # Verbose mode should produce output
        assert len(stdout) > 0 or len(stderr) > 0


class TestExitCodes:
    """Exit code smoke tests."""

    def test_success_exit_code(self):
        """Test exit code 0 when all assertions pass."""
        config_path = CONFIGS_DIR / "basic.yaml"

        stdout, stderr, exit_code = run_promptfoo(
            ["eval", "-c", str(config_path), "--no-cache"]
        )

        assert exit_code == 0

    def test_failure_exit_code(self):
        """Test exit code 100 when assertions fail."""
        config_path = CONFIGS_DIR / "failing-assertion.yaml"

        stdout, stderr, exit_code = run_promptfoo(
            ["eval", "-c", str(config_path), "--no-cache"],
            expect_error=True,
        )

        # Exit code 100 indicates test failures
        assert exit_code == 100, f"Expected exit code 100, got {exit_code}"

    def test_config_error_exit_code(self):
        """Test exit code 1 for config errors."""
        stdout, stderr, exit_code = run_promptfoo(
            ["eval", "-c", "nonexistent-file.yaml", "--no-cache"],
            expect_error=True,
        )

        assert exit_code == 1


class TestEchoProvider:
    """Echo provider smoke tests."""

    def test_echo_provider_basic(self):
        """Test echo provider returns the prompt."""
        config_path = CONFIGS_DIR / "basic.yaml"
        output_path = OUTPUT_DIR / "echo-test.json"

        stdout, stderr, exit_code = run_promptfoo(
            ["eval", "-c", str(config_path), "-o", str(output_path), "--no-cache"]
        )

        assert exit_code == 0

        # Verify echo provider returns the prompt
        with open(output_path) as f:
            data = json.load(f)

        first_result = data["results"]["results"][0]

        # Echo provider should return the prompt in the response
        output = first_result["response"]["output"]
        assert "Hello" in output
        assert "World" in output

    def test_echo_provider_with_multiple_vars(self):
        """Test echo provider with multiple variables."""
        config_path = CONFIGS_DIR / "assertions.yaml"
        output_path = OUTPUT_DIR / "echo-multi-var.json"

        stdout, stderr, exit_code = run_promptfoo(
            ["eval", "-c", str(config_path), "-o", str(output_path), "--no-cache"]
        )

        assert exit_code == 0

        with open(output_path) as f:
            data = json.load(f)

        first_result = data["results"]["results"][0]
        output = first_result["response"]["output"]

        # Should contain all variable values
        assert "Alice" in output
        assert "Wonderland" in output


class TestAssertions:
    """Assertion smoke tests."""

    def test_contains_assertion(self):
        """Test contains assertion."""
        config_path = CONFIGS_DIR / "basic.yaml"

        stdout, stderr, exit_code = run_promptfoo(
            ["eval", "-c", str(config_path), "--no-cache"]
        )

        assert exit_code == 0
        # All assertions should pass
        assert "pass" in stdout.lower() or "✓" in stdout or "success" in stdout.lower()

    def test_multiple_assertions(self):
        """Test multiple assertions in single test."""
        config_path = CONFIGS_DIR / "assertions.yaml"

        stdout, stderr, exit_code = run_promptfoo(
            ["eval", "-c", str(config_path), "--no-cache"]
        )

        assert exit_code == 0

    def test_failing_assertion(self):
        """Test failing assertion."""
        config_path = CONFIGS_DIR / "failing-assertion.yaml"

        stdout, stderr, exit_code = run_promptfoo(
            ["eval", "-c", str(config_path), "--no-cache"],
            expect_error=True,
        )

        # Should fail with exit code 100
        assert exit_code == 100
        output = stdout + stderr
        # Should indicate failure
        assert "fail" in output.lower() or "✗" in output or "error" in output.lower()
