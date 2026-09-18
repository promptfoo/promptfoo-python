import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from promptfoo.environment import Environment
from promptfoo.instructions import get_installation_instructions


def windows_verification_commands(launcher: str | None = None) -> list[str]:
    instructions = get_installation_instructions(Environment(os_type="windows")).splitlines()
    start = instructions.index("Verify with:") + 1
    if launcher is None:
        launcher = next((name for name in ("npx.cmd", "npx.exe") if shutil.which(name)), None)
    assert launcher, "Neither npx.cmd nor npx.exe is available"
    npx = instructions[start + 1].strip()
    if launcher == "npx.exe":
        npx = next(line.partition("use: ")[2] for line in instructions if "use: npx.exe" in line)
    return [instructions[start].strip(), npx]


def git_bash() -> Path | None:
    roots = []
    if git := shutil.which("git"):
        location = Path(git).resolve()
        roots += [location.parent, location.parent.parent]
    for variable, suffix in (("PROGRAMFILES", "Git"), ("LOCALAPPDATA", "Programs/Git")):
        if directory := os.environ.get(variable):
            roots.append(Path(directory) / suffix)
    return next(
        (
            candidate
            for root in roots
            for candidate in (root / "bin/bash.exe", root / "usr/bin/bash.exe")
            if candidate.is_file()
        ),
        None,
    )


@pytest.mark.smoke
@pytest.mark.skipif(sys.platform != "win32", reason="Tests native Windows PowerShell's restricted execution policy")
def test_windows_verification_commands_run_with_powershell_scripts_disabled() -> None:
    powershell = shutil.which("powershell")
    assert powershell
    commands = windows_verification_commands()
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
    if not (bash := git_bash()):
        pytest.skip("Git for Windows is not installed")
    commands = windows_verification_commands()

    result = subprocess.run(
        [str(bash), "--noprofile", "--norc", "-c", "set -e; " + "; ".join(commands)],
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stderr
    assert len([line for line in result.stdout.splitlines() if re.fullmatch(r"v?\d+\.\d+\.\d+", line)]) == 2


@pytest.mark.smoke
@pytest.mark.skipif(sys.platform != "win32", reason="Tests native Windows executable lookup")
@pytest.mark.parametrize("shell", ["powershell", "git-bash"])
def test_windows_npx_executable_alternative_works_in_each_shell(tmp_path: Path, shell: str) -> None:
    launcher = shutil.which("node")
    assert launcher
    node = subprocess.run([launcher, "-p", "process.execPath"], capture_output=True, text=True, check=True, timeout=20)
    shutil.copy2(node.stdout.strip(), tmp_path / "npx.exe")
    command = windows_verification_commands("npx.exe")[1]
    if shell == "powershell":
        powershell = shutil.which("powershell")
        assert powershell
        prefix = [powershell, "-NoProfile", "-ExecutionPolicy", "Restricted", "-Command"]
    elif bash := git_bash():
        prefix = [str(bash), "--noprofile", "--norc", "-c"]
    else:
        pytest.skip("Git for Windows is not installed")

    result = subprocess.run(
        [*prefix, command],
        env=os.environ | {"PATH": str(tmp_path) + os.pathsep + os.environ["PATH"]},
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stderr
    assert re.fullmatch(r"v\d+\.\d+\.\d+", result.stdout.strip())
