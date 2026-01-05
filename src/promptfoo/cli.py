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


def _find_external_promptfoo() -> Optional[str]:
    promptfoo_path = shutil.which("promptfoo")
    if not promptfoo_path:
        return None
    argv0_path = _resolve_argv0()
    if argv0_path and _normalize_path(promptfoo_path) == argv0_path:
        wrapper_dir = _normalize_path(os.path.dirname(promptfoo_path))
        path_entries = [
            entry
            for entry in os.environ.get("PATH", "").split(os.pathsep)
            if entry and _normalize_path(entry) != wrapper_dir
        ]
        if not path_entries:
            return None
        return shutil.which("promptfoo", path=os.pathsep.join(path_entries))
    return promptfoo_path


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
        result = subprocess.run(cmd, env=env)
    elif shutil.which("npx"):
        cmd = ["npx", "-y", "promptfoo@latest"] + sys.argv[1:]
        result = subprocess.run(cmd)
    else:
        print("ERROR: Neither promptfoo nor npx is available.", file=sys.stderr)
        print("Please install promptfoo: npm install -g promptfoo", file=sys.stderr)
        print("Or ensure Node.js is properly installed.", file=sys.stderr)
        sys.exit(1)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
