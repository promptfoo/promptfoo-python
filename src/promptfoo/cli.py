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

from .telemetry import record_wrapper_used

_WRAPPER_ENV = "PROMPTFOO_PY_WRAPPER"
_WINDOWS_SHELL_EXTENSIONS = (".bat", ".cmd")


def check_node_installed() -> bool:
    """Check if Node.js is installed and available."""
    return shutil.which("node") is not None


def check_npx_installed() -> bool:
    """Check if npx is installed and available."""
    return shutil.which("npx") is not None


def print_installation_help() -> None:
    """Print contextual installation instructions for Node.js based on the environment."""
    from .environment import detect_environment
    from .instructions import get_installation_instructions

    env = detect_environment()
    instructions = get_installation_instructions(env)
    print(instructions, file=sys.stderr)


def _normalize_path(path: str) -> str:
    """Normalize a path for safe comparison."""
    return os.path.normcase(os.path.abspath(path))


def _strip_quotes(path: str) -> str:
    """Strip surrounding quotes from a path string."""
    if len(path) >= 2 and path[0] == path[-1] and path[0] in ('"', "'"):
        return path[1:-1]
    return path


def _split_path(path_value: str) -> list[str]:
    """Split a PATH string into a list of directories."""
    entries = []
    for entry in path_value.split(os.pathsep):
        entry = _strip_quotes(entry.strip())
        if entry:
            entries.append(entry)
    return entries


def _resolve_argv0() -> Optional[str]:
    """Resolve the absolute path of the current script (argv[0])."""
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
    """
    Search for promptfoo in standard Windows installation locations.
    Useful when not in PATH.
    """
    search_dirs = []

    # Check npm config env vars
    for key in ("NPM_CONFIG_PREFIX", "npm_config_prefix"):
        if prefix := os.environ.get(key):
            search_dirs.append(prefix)

    # Check standard npm folders
    if appdata := os.environ.get("APPDATA"):
        search_dirs.append(os.path.join(appdata, "npm"))
    if localappdata := os.environ.get("LOCALAPPDATA"):
        search_dirs.append(os.path.join(localappdata, "npm"))

    # Check Program Files
    for env_key in ("ProgramFiles", "ProgramFiles(x86)"):
        if program_files := os.environ.get(env_key):
            search_dirs.append(os.path.join(program_files, "nodejs"))

    for base_dir in search_dirs:
        for name in ("promptfoo.cmd", "promptfoo.exe"):
            candidate = os.path.join(base_dir, name)
            if os.path.isfile(candidate):
                return candidate
    return None


def _is_executing_wrapper(found_path: str) -> bool:
    """
    Detect if the found executable is actually this wrapper script.

    This handles cases where the wrapper is installed in the same bin/ directory
    as the target or if we are inside a virtual environment.
    """
    argv0_path = _resolve_argv0()
    found_norm = _normalize_path(found_path)

    # direct argv0 match
    if argv0_path and found_norm == argv0_path:
        return True

    # venv detection (shim check)
    return sys.prefix != sys.base_prefix and os.path.dirname(found_norm) == os.path.dirname(
        _normalize_path(sys.executable)
    )


def _search_path_excluding(exclude_dir: str) -> Optional[str]:
    """Search PATH for promptfoo, excluding the specified directory."""
    path_entries = [entry for entry in _split_path(os.environ.get("PATH", "")) if _normalize_path(entry) != exclude_dir]
    if not path_entries:
        return None
    return shutil.which("promptfoo", path=os.pathsep.join(path_entries))


def _find_external_promptfoo() -> Optional[str]:
    """Find the external promptfoo executable, avoiding the wrapper itself."""
    # 1. First naive search
    candidate = shutil.which("promptfoo")

    # 2. If not found, try explicit Windows paths
    if not candidate:
        if os.name == "nt":
            return _find_windows_promptfoo()
        return None

    # 3. If found, check if it's us (the wrapper)
    if _is_executing_wrapper(candidate):
        wrapper_dir = _normalize_path(os.path.dirname(candidate))
        # Search again excluding our directory
        candidate = _search_path_excluding(wrapper_dir)

        # If still not found, try Windows fallback
        if not candidate and os.name == "nt":
            return _find_windows_promptfoo()

    return candidate


def _requires_shell(executable: str) -> bool:
    """Check if the executable requires a shell to run (Windows only)."""
    if os.name != "nt":
        return False
    _, ext = os.path.splitext(executable)
    return ext.lower() in _WINDOWS_SHELL_EXTENSIONS


def _run_command(cmd: list[str], env: Optional[dict[str, str]] = None) -> subprocess.CompletedProcess[bytes]:
    """Execute a command, handling shell requirements on Windows."""
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
        record_wrapper_used("global")
        cmd = [promptfoo_path] + sys.argv[1:]
        env = os.environ.copy()
        env[_WRAPPER_ENV] = "1"
        result = _run_command(cmd, env=env)
    else:
        npx_path = shutil.which("npx")
        if npx_path:
            record_wrapper_used("npx")
            cmd = [npx_path, "-y", "promptfoo@latest"] + sys.argv[1:]
            result = _run_command(cmd)
        else:
            record_wrapper_used("error")
            print("ERROR: Neither promptfoo nor npx is available.", file=sys.stderr)
            print("Please install promptfoo: npm install -g promptfoo", file=sys.stderr)
            print("Or ensure Node.js is properly installed.", file=sys.stderr)
            sys.exit(1)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
