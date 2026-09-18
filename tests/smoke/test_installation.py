import re
import shutil
import subprocess
import sys

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
