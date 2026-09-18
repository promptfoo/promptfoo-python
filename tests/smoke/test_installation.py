import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from promptfoo.environment import Environment
from promptfoo.instructions import get_installation_instructions


@pytest.mark.smoke
@pytest.mark.skipif(sys.platform != "win32", reason="Tests native Windows PowerShell's restricted execution policy")
def test_windows_verification_commands_run_with_powershell_scripts_disabled() -> None:
    powershell = shutil.which("powershell")
    assert powershell
    instructions = get_installation_instructions(Environment(os_type="windows")).splitlines()
    start = instructions.index("Verify with:") + 1
    commands = [line.strip() for line in instructions[start : start + 2]]
    script = "; ".join(["$ErrorActionPreference = 'Stop'", *commands, "if ($LASTEXITCODE) { exit $LASTEXITCODE }"])

    result = subprocess.run(
        [powershell, "-NoProfile", "-ExecutionPolicy", "Restricted", "-Command", script],
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stderr
    assert len([line for line in result.stdout.splitlines() if re.fullmatch(r"v?\d+\.\d+\.\d+", line)]) == 2


@pytest.mark.smoke
@pytest.mark.skipif(sys.platform != "win32", reason="Tests native Windows Git Bash")
def test_windows_verification_commands_run_in_git_bash() -> None:
    bash = Path(os.environ["PROGRAMFILES"]) / "Git" / "bin" / "bash.exe"
    if not bash.is_file():
        pytest.skip("Git for Windows is not installed")
    instructions = get_installation_instructions(Environment(os_type="windows")).splitlines()
    start = instructions.index("Verify with:") + 1
    commands = [line.strip() for line in instructions[start : start + 2]]

    result = subprocess.run(
        [str(bash), "--noprofile", "--norc", "-c", "set -e; " + "; ".join(commands)],
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stderr
    assert len([line for line in result.stdout.splitlines() if re.fullmatch(r"v?\d+\.\d+\.\d+", line)]) == 2
