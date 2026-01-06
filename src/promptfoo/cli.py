"""
CLI wrapper for promptfoo

This module provides a thin wrapper around the promptfoo Node.js CLI tool.
It executes a global promptfoo binary when available, falling back to npx.
"""

import os
import shutil
import subprocess
import sys
from typing import NoReturn, Optional

_WRAPPER_ENV = "PROMPTFOO_PY_WRAPPER"
_WINDOWS_SHELL_EXTENSIONS = (".bat", ".cmd")


def check_node_installed() -> bool:
    """Check if Node.js is installed and available."""
    return shutil.which("node") is not None


def check_npx_installed() -> bool:
    """Check if npx is installed and available."""
    return shutil.which("npx") is not None


def print_installation_help() -> None:
    """Print helpful installation instructions for Node.js."""
    print("ERROR: promptfoo requires Node.js to be installed.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Please install Node.js:", file=sys.stderr)
    print("  - macOS: brew install node", file=sys.stderr)
    print("  - Ubuntu/Debian: sudo apt install nodejs npm", file=sys.stderr)
    print("  - Windows: Download from https://nodejs.org/", file=sys.stderr)
    print("", file=sys.stderr)
    print("Or use nvm (Node Version Manager):", file=sys.stderr)
    print("  https://github.com/nvm-sh/nvm", file=sys.stderr)


def _normalize_path(path: str) -> str:
    return os.path.normcase(os.path.abspath(path))


def _strip_quotes(path: str) -> str:
    if len(path) >= 2 and path[0] == path[-1] and path[0] in ('"', "'"):
        return path[1:-1]
    return path


def _split_path(path_value: str) -> list[str]:
    entries = []
    for entry in path_value.split(os.pathsep):
        entry = _strip_quotes(entry.strip())
        if entry:
            entries.append(entry)
    return entries


def _resolve_argv0() -> Optional[str]:
    if not sys.argv:
        return None
    argv0 = sys.argv[0]
    if not argv0:
        return None
    if os.path.sep in argv0 or (os.path.altsep and os.path.altsep in argv0):
        return _normalize_path(argv0)
    resolved = shutil.which(argv0)
    if resolved:
        return _normalize_path(resolved)
    return None


def _find_windows_promptfoo() -> Optional[str]:
    candidates = []
    for key in ("NPM_CONFIG_PREFIX", "npm_config_prefix"):
        prefix = os.environ.get(key)
        if prefix:
            candidates.append(prefix)
    appdata = os.environ.get("APPDATA")
    if appdata:
        candidates.append(os.path.join(appdata, "npm"))
    localappdata = os.environ.get("LOCALAPPDATA")
    if localappdata:
        candidates.append(os.path.join(localappdata, "npm"))
    for env_key in ("ProgramFiles", "ProgramFiles(x86)"):
        program_files = os.environ.get(env_key)
        if program_files:
            candidates.append(os.path.join(program_files, "nodejs"))
    for base in candidates:
        for name in ("promptfoo.cmd", "promptfoo.exe"):
            candidate = os.path.join(base, name)
            if os.path.isfile(candidate):
                return candidate
    return None


def _find_external_promptfoo() -> Optional[str]:
    promptfoo_path = shutil.which("promptfoo")
    if not promptfoo_path:
        if os.name == "nt":
            return _find_windows_promptfoo()
        return None

    argv0_path = _resolve_argv0()
    promptfoo_path_norm = _normalize_path(promptfoo_path)
    is_self = False

    if argv0_path and promptfoo_path_norm == argv0_path:
        is_self = True
    elif (
        sys.prefix != sys.base_prefix
        and os.path.dirname(promptfoo_path_norm) == os.path.dirname(_normalize_path(sys.executable))
    ):
        # Running in a virtual environment. Check if the found executable is in the same
        # directory as the Python interpreter. This detects shims (e.g. Windows .exe, uv)
        # where argv0 points to the script but shutil.which finds the shim.
        is_self = True

    if is_self:
        wrapper_dir = _normalize_path(os.path.dirname(promptfoo_path))
        path_entries = [
            entry for entry in _split_path(os.environ.get("PATH", "")) if _normalize_path(entry) != wrapper_dir
        ]
        if path_entries:
            candidate = shutil.which("promptfoo", path=os.pathsep.join(path_entries))
            if candidate:
                return candidate
        if os.name == "nt":
            return _find_windows_promptfoo()
        return None
    return promptfoo_path


def _requires_shell(executable: str) -> bool:
    if os.name != "nt":
        return False
    _, ext = os.path.splitext(executable)
    return ext.lower() in _WINDOWS_SHELL_EXTENSIONS


def _run_command(cmd: list[str], env: Optional[dict[str, str]] = None) -> subprocess.CompletedProcess:
    if _requires_shell(cmd[0]):
        return subprocess.run(subprocess.list2cmdline(cmd), shell=True, env=env)
    return subprocess.run(cmd, env=env)


def main() -> NoReturn:
    """
    Main entry point for the promptfoo CLI wrapper.

    Executes promptfoo using subprocess.run() with minimal configuration.
    """
    # Check for Node.js installation
    if not check_node_installed():
        print_installation_help()
        sys.exit(1)

    # Build command: try external promptfoo first, fall back to npx
    promptfoo_path = None if os.environ.get(_WRAPPER_ENV) else _find_external_promptfoo()
    if promptfoo_path:
        cmd = [promptfoo_path] + sys.argv[1:]
        env = os.environ.copy()
        env[_WRAPPER_ENV] = "1"
        result = _run_command(cmd, env=env)
    else:
        npx_path = shutil.which("npx")
        if npx_path:
            cmd = [npx_path, "-y", "promptfoo@latest"] + sys.argv[1:]
            result = _run_command(cmd)
        else:
            print("ERROR: Neither promptfoo nor npx is available.", file=sys.stderr)
            print("Please install promptfoo: npm install -g promptfoo", file=sys.stderr)
            print("Or ensure Node.js is properly installed.", file=sys.stderr)
            sys.exit(1)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
